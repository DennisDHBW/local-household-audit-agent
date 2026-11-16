"""Tests of the test module (M6a): metrics, variants B0/P1/P2, answer store and scoring CLI."""

from __future__ import annotations

import json
import shutil
from datetime import date
from decimal import Decimal

import httpx
import pytest

from audit_agent.agent import AgentLoop, ToolBox
from audit_agent.agent.loop import estimate_tokens
from audit_agent.agent.models import ModelCallStep
from audit_agent.config import PROJECT_ROOT, AgentSettings, EvaluationSettings, Settings
from audit_agent.corpus import (
    CorpusError,
    DocType,
    DocumentCatalog,
    DocumentMeta,
    ExpectedFact,
    Question,
    QuestionCategory,
    SourceRef,
    UtilityType,
    load_ground_truth,
)
from audit_agent.evaluation import (
    EvaluationError,
    ShownSource,
    ToolUse,
    VariantAnswer,
    score_answer,
    select_questions,
    summarize,
)
from audit_agent.evaluation import __main__ as cli
from audit_agent.evaluation.__main__ import _score
from audit_agent.evaluation.metrics import (
    answer_verdict,
    cited_numbers,
    expected_verdict,
    filter_excludes,
    is_fact_in_answer,
    strip_citations,
)
from audit_agent.evaluation.prompts import evidence_prompt
from audit_agent.evaluation.store import (
    answers_path,
    append_answer,
    check_same_model,
    load_answers,
    load_run,
)
from audit_agent.evaluation.variants import (
    PIPELINE_CHUNK_TYPES,
    AgentVariant,
    FullTextVariant,
    PipelineVariant,
    build_full_text_context,
    full_text_budget,
    unloads_after_each_question,
)
from audit_agent.ingestion import (
    ChunkMetadata,
    ChunkType,
    DocumentChunk,
    ParsedDocument,
    chunks_path,
)
from tests.agent_fakes import (
    BILL_FILE,
    CONTRACT_FILE,
    NOTICE_FILE,
    FakeBackend,
    ScriptedChat,
    answer_reply,
    make_catalog,
    make_hit,
    tool_reply,
)

NOISE_FILE = "05_telecom_z/22_Internet_Vertrag_2024.pdf"


def _catalog_with_noise() -> DocumentCatalog:
    noise = DocumentMeta(
        file=NOISE_FILE,
        utility_type=UtilityType.TELECOM,
        doc_type=DocType.CONTRACT,
        provider="Netz AG",
        document_date=date(2024, 1, 1),
        is_noise_document=True,
    )
    return DocumentCatalog(documents=(*make_catalog().documents, noise))


def _audit_question(**overrides) -> Question:
    values = {
        "id": "G1",
        "category": QuestionCategory.EDGE_CASE,
        "question": "Wurde der neue Arbeitspreis angewendet?",
        "expected_answer": "Nein. Angekündigt 38,20, abgerechnet 39,50 ct/kWh.",
        "facts": (ExpectedFact(label="Abgerechnet", value=Decimal("39.50"), unit="ct/kWh"),),
        "sources": (SourceRef(file=NOTICE_FILE, page=1), SourceRef(file=BILL_FILE, page=1)),
        "expected_tools": ("search", "calculate"),
        "tests": "Fehlererkennung",
    }
    return Question(**{**values, **overrides})


def _negative_question() -> Question:
    return Question(
        id="N1",
        category=QuestionCategory.NEGATIVE,
        question="Stromrechnung 2023?",
        expected_answer="Liegt nicht vor.",
        is_answerable=False,
        tests="keine erfundene Zahl",
    )


def _model_step(prompt_tokens: int = 100) -> ModelCallStep:
    return ModelCallStep(
        index=0,
        offered_tools=False,
        message_count=2,
        prompt_tokens=prompt_tokens,
        prefill_seconds=5.0,
        generated_tokens=20,
        decode_seconds=4.0,
        seconds=9.0,
        content="x",
        tool_calls=(),
    )


def _answer(text: str, variant="p1", question_id="G1", model="m", **overrides) -> VariantAnswer:
    values = {
        "variant": variant,
        "question_id": question_id,
        "model": model,
        "answer": text,
        "stop_reason": "answer",
        "seconds": 10.0,
        "sources": (
            ShownSource(number=1, filename=BILL_FILE, page_number=1),
            ShownSource(number=2, filename=NOISE_FILE, page_number=1),
            ShownSource(number=3, filename=NOTICE_FILE, page_number=2),
        ),
        "model_calls": (_model_step(),),
    }
    return VariantAnswer(**{**values, **overrides})


# --- metrics -------------------------------------------------------------------------------


def test_citations_are_found_and_removed():
    answer = "Preis 39,50 ct [1], laut Schreiben [2, 3] und [4;5]."
    assert cited_numbers(answer) == {1, 2, 3, 4, 5}
    assert "[" not in strip_citations(answer)


def test_a_citation_number_is_not_a_found_fact():
    fact = ExpectedFact(label="Anteil", value=Decimal(25), unit="%", tolerance=Decimal(0))
    assert is_fact_in_answer(fact, "Der Anteil beträgt 30 % [25].") is False
    assert is_fact_in_answer(fact, "Der Anteil beträgt 25 % [2].") is True


def test_text_facts_match_whole_words_only():
    fact = ExpectedFact(label="korrekt", value="ja")
    assert is_fact_in_answer(fact, "Die Jahresabrechnung 2024 …") is False
    assert is_fact_in_answer(fact, "Ja, sie stimmt.") is True


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("Nein, abgerechnet wurden 39,50 ct/kWh [2].", "nein"),
        ("Ja. Der Betrag von 1.189,00 EUR stimmt [1].", "ja"),
        ("Die Abrechnung stimmt nicht mit dem Preisschreiben überein.", "nein"),
        ("Die Abrechnung stimmt mit dem Vertrag überein. Nicht berechnet: nichts.", "ja"),
        ("Es gibt keine Abweichung zwischen Vertrag und Rechnung.", "ja"),
        ("Es wurden 40,30 EUR zu viel berechnet.", "nein"),
        ("Der Arbeitspreis beträgt 34,80 ct/kWh [1].", None),
        ("Abgerechnet wurden 39,50 ct/kWh [1]. Der neue Preis wurde nicht angewendet.", "nein"),
    ],
)
def test_answer_verdict_heuristic(answer, expected):
    assert answer_verdict(answer) == expected


def test_expected_verdict_only_for_leading_yes_or_no():
    assert expected_verdict(_audit_question()) == "nein"
    assert expected_verdict(_audit_question(expected_answer="Ja, 1.830 EUR.")) == "ja"
    assert expected_verdict(_negative_question()) is None


def test_filter_excludes_follows_the_tool_rules():
    bill, contract = (make_catalog().by_file(f) for f in (BILL_FILE, CONTRACT_FILE))
    assert filter_excludes({"query": "x", "doc_type": "bill"}, contract) is True
    assert filter_excludes({"query": "x", "utility_type": "gas"}, bill) is True
    assert filter_excludes({"query": "x", "doc_type": "bill", "year": 2025}, bill) is True
    assert filter_excludes({"query": "x", "doc_type": "bill", "year": 2024}, bill) is False
    # a year without a suitable document type is ignored by the tools (ISS-025)
    assert filter_excludes({"query": "x", "year": 2025}, contract) is False
    assert filter_excludes({"query": "x", "utility_type": "Strom"}, bill) is False


def test_score_of_an_agent_answer():
    # Arrange
    answer = _answer(
        "Nein, abgerechnet 39,50 statt 38,20 ct/kWh [1][2][9].",
        variant="p2",
        tool_uses=(
            ToolUse(
                name="search",
                arguments={"query": "a", "doc_type": "contract"},
                is_valid=True,
            ),
            ToolUse(name="search", arguments={"query": "b"}, is_valid=True),
            ToolUse(name="calculate", arguments={"expression": "1"}, is_valid=False),
        ),
    )

    # Act
    score = score_answer(_audit_question(), answer, _catalog_with_noise())

    # Assert
    assert score.missing_facts == ()
    assert (score.cited_count, score.invalid_citations) == (2, 1)
    assert (score.cited_expected, score.expected_cited, score.expected_count) == (1, 1, 2)
    assert (score.cited_distractors, score.shown_distractors, score.shown_count) == (1, 1, 3)
    assert score.called_tools == ("search", "search")
    assert score.are_tools_ok is False  # calculate was invalid
    assert (score.filtered_searches, score.filter_misses) == (1, 1)
    assert score.answer_verdict == "nein"
    assert score.is_correct is True


def test_score_of_a_pipeline_answer_has_no_tool_metrics():
    score = score_answer(_audit_question(), _answer("Ja, alles korrekt [1]."), make_catalog())
    assert score.called_tools is None and score.are_tools_ok is None
    assert score.missing_facts == ("Abgerechnet",)
    assert score.is_verdict_ok is False and score.is_correct is False


def test_negative_question_is_correct_only_with_an_honest_gap():
    question = _negative_question()
    honest = score_answer(question, _answer("Dazu liegen keine Angaben vor."), make_catalog())
    polite = score_answer(question, _answer("Ich habe keine Informationen dazu."), make_catalog())
    invented = score_answer(question, _answer("Sie betrug 980 EUR [1]."), make_catalog())
    assert honest.is_correct is True and polite.is_correct is True
    assert invented.is_correct is False


def test_summary_counts_per_variant_in_fixed_order():
    # Arrange
    catalog = _catalog_with_noise()
    audit_ok = _audit_question(id="G2", expected_answer="Ja, 1.830 EUR.")
    scores = [
        score_answer(_audit_question(), _answer("Nein, 39,50 ct [1].", variant="p2"), catalog),
        score_answer(
            audit_ok, _answer("Nein, zu hoch [1].", variant="p2", question_id="G2"), catalog
        ),
        score_answer(_negative_question(), _answer("Keine Angaben.", variant="b0"), catalog),
    ]

    # Act
    b0, p2 = summarize(scores)

    # Assert
    assert (b0.variant, p2.variant) == ("b0", "p2")
    assert (b0.negatives_detected, b0.negative_count, b0.tools_ok_count) == (1, 1, None)
    assert (p2.errors_detected, p2.error_count) == (1, 1)
    assert (p2.false_alarms, p2.correct_bill_count) == (1, 1)
    assert p2.seconds_mean == 10.0


# --- test set and store --------------------------------------------------------------------


def test_select_questions_keeps_order_and_rejects_unknown_ids():
    truth = load_ground_truth(PROJECT_ROOT / "dataset" / "ground_truth.yaml")
    assert [q.id for q in select_questions(truth, ["N1", "S2", "N1"])] == ["N1", "S2"]
    assert len(select_questions(truth)) == 14
    with pytest.raises(CorpusError, match="X9"):
        select_questions(truth, ["X9"])


def test_answers_are_appended_and_read_back(tmp_path):
    path = answers_path(tmp_path, "p1")
    append_answer(path, _answer("a", question_id="S1"))
    append_answer(path, _answer("b", question_id="S2"))
    assert [a.answer for a in load_answers(path)] == ["a", "b"]
    assert load_answers(answers_path(tmp_path, "b0")) == []


def test_a_run_never_mixes_models(tmp_path):
    with pytest.raises(EvaluationError, match="new --run-id"):
        check_same_model([_answer("a", model="llama3.1:8b")], "qwen2.5:7b")
    with pytest.raises(EvaluationError, match="no answers"):
        load_run(tmp_path)


# --- variants ------------------------------------------------------------------------------


def _chunk(meta: DocumentMeta, i: int, page: int, content: str, kind=ChunkType.TEXT):
    extra = {"image_path": "images/x.png"} if kind is ChunkType.IMAGE else {}
    metadata = ChunkMetadata.from_document(meta).model_copy(update=extra)
    return DocumentChunk(
        chunk_id=f"{meta.file}-{i}",
        chunk_type=kind,
        content=content,
        page_number=page,
        metadata=metadata,
    )


def _write_processed(settings: Settings, meta: DocumentMeta, chunks) -> None:
    path = chunks_path(settings.processed_dir, meta.file)
    path.parent.mkdir(parents=True, exist_ok=True)
    document = ParsedDocument(file=meta.file, page_count=2, chunks=tuple(chunks))
    path.write_text(document.model_dump_json(), encoding="utf-8")


def test_full_text_context_fills_the_budget_in_catalog_order(tmp_path):
    # Arrange: contract (1 page), notice (2 pages), bill; the budget ends inside the notice
    catalog = make_catalog()
    contract, notice, bill, gas = catalog.documents
    blocks = [
        "[1] 01_Strom_Vertrag_2024.pdf, S. 1\nVertrag Arbeitspreis 34,80",
        "[2] 03_Strom_Preisanpassung_2025.pdf, S. 1\n" + "Preis neu 38,20 " * 20,
        "[3] 03_Strom_Preisanpassung_2025.pdf, S. 2\n" + "Seite zwei " * 40,
    ]
    costs = [estimate_tokens(block) + 1 for block in blocks]
    probe = Settings(
        project_root=tmp_path, evaluation=EvaluationSettings(full_text_reserve_tokens=0)
    )
    fixed = probe.num_ctx - full_text_budget(probe)
    settings = probe.model_copy(update={"num_ctx": fixed + costs[0] + costs[1] + costs[2] - 1})
    _write_processed(
        settings,
        contract,
        [
            _chunk(contract, 0, 1, "Vertrag Arbeitspreis 34,80"),
            _chunk(contract, 1, 1, "KI-Beschreibung", ChunkType.IMAGE),
        ],
    )
    _write_processed(
        settings,
        notice,
        [_chunk(notice, 0, 1, "Preis neu 38,20 " * 20), _chunk(notice, 1, 2, "Seite zwei " * 40)],
    )

    # Act
    context = build_full_text_context(settings, catalog)

    # Assert
    assert context.text == "\n\n".join(blocks[:2])
    assert context.blocks == tuple(blocks[:2])
    assert "KI-Beschreibung" not in context.text
    assert [s.number for s in context.sources] == [1, 2]
    assert context.complete_files == (contract.file,)
    assert context.partial_file == notice.file
    assert context.missing_files == (bill.file, gas.file)
    assert context.estimated_tokens == costs[0] + costs[1] <= context.budget_tokens


def test_full_text_context_fails_fast_without_ingestion(tmp_path):
    with pytest.raises(EvaluationError, match="ingestion"):
        build_full_text_context(Settings(project_root=tmp_path), make_catalog())


def test_full_text_variant_sends_the_context_as_system_prompt(tmp_path):
    # Arrange
    settings = Settings(project_root=tmp_path)
    contract = make_catalog().documents[0]
    _write_processed(settings, contract, [_chunk(contract, 0, 1, "Arbeitspreis 34,80 ct/kWh")])
    context = build_full_text_context(settings, DocumentCatalog(documents=(contract,)))
    chat = ScriptedChat([answer_reply("34,80 ct/kWh [1].", prompt_tokens=900)])

    # Act
    answer = FullTextVariant(settings, chat, context).answer(_audit_question(id="S2"), "m")

    # Assert
    request = chat.requests[0]
    assert request["messages"][0]["content"] == evidence_prompt(context.text)
    assert request["messages"][1]["content"] == _audit_question().question
    assert request["options"]["num_ctx"] == settings.num_ctx
    assert "tools" not in request
    assert (answer.variant, answer.question_id, answer.prompt_tokens) == ("b0", "S2", 900)
    assert answer.sources == context.sources
    assert answer.contexts == context.blocks


def test_pipeline_variant_searches_once_without_filter_and_numbers_the_hits(tmp_path):
    # Arrange
    hits = [make_hit("a"), make_hit("b", ChunkType.TEXT, filename=NOTICE_FILE, page_number=2)]
    backend = FakeBackend(lambda query, options: hits)
    chat = ScriptedChat([answer_reply("Nein [1][2].")])
    settings = Settings(project_root=tmp_path, agent=AgentSettings(max_hit_chars=100))

    # Act
    answer = PipelineVariant(settings, chat, backend).answer(_audit_question(), "m")

    # Assert
    query, options = backend.calls[0]
    assert query == _audit_question().question
    assert options.chunk_types == PIPELINE_CHUNK_TYPES
    assert options.metadata_filter.utility_type is None
    system = chat.requests[0]["messages"][0]["content"]
    assert "[1] 04_Strom_Jahresabrechnung_2024.pdf, S. 1, Tabellenzeile" in system
    assert "[2] 03_Strom_Preisanpassung_2025.pdf, S. 2, Text" in system
    assert [(s.number, s.filename) for s in answer.sources] == [(1, BILL_FILE), (2, NOTICE_FILE)]
    assert answer.variant == "p1" and answer.answer == "Nein [1][2]."
    assert len(answer.contexts) == 2
    assert answer.contexts[1].startswith("[2] 03_Strom_Preisanpassung_2025.pdf, S. 2, Text")
    assert all(block in system for block in answer.contexts)


def test_pipeline_variant_without_hits_still_asks_the_model(tmp_path):
    chat = ScriptedChat([answer_reply("Dazu liegen keine Angaben vor.")])
    backend = FakeBackend(lambda query, options: [])
    answer = PipelineVariant(Settings(project_root=tmp_path), chat, backend).answer(
        _negative_question(), "m"
    )
    assert "(keine Treffer)" in chat.requests[0]["messages"][0]["content"]
    assert answer.sources == ()


def test_agent_variant_translates_the_run_and_logs_every_step(tmp_path):
    # Arrange
    settings = Settings(project_root=tmp_path)
    backend = FakeBackend(lambda query, options: [make_hit()])
    chat = ScriptedChat(
        [tool_reply(("search", {"query": "Arbeitspreis"})), answer_reply("34,80 [1].")]
    )
    loop = AgentLoop(settings, chat, ToolBox(settings, backend, make_catalog()).tools())

    # Act
    question = _audit_question(id="S2", question="Welcher Arbeitspreis gilt?")
    answer = AgentVariant(loop, log_dir=tmp_path).answer(question, "m")

    # Assert
    assert answer.variant == "p2" and answer.answer == "34,80 [1]."
    assert answer.tool_uses == (
        ToolUse(name="search", arguments={"query": "Arbeitspreis"}, is_valid=True),
    )
    assert [s.filename for s in answer.sources] == [BILL_FILE]
    assert len(answer.model_calls) == 2
    assert len(answer.contexts) == 1
    assert answer.contexts[0].startswith('Treffer für "Arbeitspreis"')
    log_lines = (tmp_path / "p2-S2.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(log_lines[-1])["kind"] == "run"


# --- scoring CLI ---------------------------------------------------------------------------


def test_score_writes_scores_and_report_without_ollama(tmp_path):
    # Arrange: a project root with the real catalog and ground truth
    shutil.copytree(
        PROJECT_ROOT / "dataset", tmp_path / "dataset", ignore=shutil.ignore_patterns("*.pdf")
    )
    settings = Settings(project_root=tmp_path)
    run_dir = settings.eval_dir / "r1"
    source = ShownSource(
        number=1,
        filename="01_electricity_suedvolt/01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf",
        page_number=1,
    )
    common = {"sources": (source,), "question_id": "S2"}
    append_answer(
        answers_path(run_dir, "b0"), _answer("34,80 ct/kWh und 11,50 EUR [1].", "b0", **common)
    )
    append_answer(answers_path(run_dir, "p1"), _answer("Keine Angaben.", "p1", **common))
    (run_dir / "manifest.json").write_text(
        json.dumps({"b0_context": {"complete_files": ["a"], "missing_files": ["b", "c"]}}),
        encoding="utf-8",
    )

    # Act
    code = _score(settings, "r1")

    # Assert
    assert code == 0
    payload = json.loads((run_dir / "scores.json").read_text(encoding="utf-8"))
    assert [s["variant"] for s in payload["summaries"]] == ["b0", "p1"]
    assert payload["summaries"][0]["correct_count"] == 1
    report = (run_dir / "report.md").read_text(encoding="utf-8")
    assert "| Metrik | B0 Volltext | P1 Pipeline |" in report
    assert "| S2 | ✓ 2/2 | ✗ 0/2 |" in report
    assert "B0-Kontext: 1 Dateien vollständig" in report
    assert "[1] 01_Strom_Vertragsbestaetigung_SuedVolt_2024.pdf S. 1" in report


def test_token_estimate_uses_the_measured_ratio():
    # 2.4 characters per token (RUN-007, ISS-041); higher than the old estimate of 3
    assert estimate_tokens("x" * 2400) == 1001


def test_only_b0_keeps_its_model_between_questions():
    # B0 lives on the prompt cache of its shared prefix; P1/P2 unload against OOM (ISS-043)
    assert not unloads_after_each_question("b0")
    assert unloads_after_each_question("p1") and unloads_after_each_question("p2")


def test_a_server_dying_mid_request_ends_with_the_resume_hint(monkeypatch, capsys):
    # Arrange: Ollama is killed while answering (RUN-010, ISS-049)
    def dies(*_args):
        raise httpx.RemoteProtocolError("Server disconnected without sending a response.")

    monkeypatch.setattr(cli, "_generate", dies)
    monkeypatch.setattr(cli, "_unload", lambda *_args: None)
    monkeypatch.setattr("sys.argv", ["evaluation", "generate", "--run-id", "r"])

    # Act
    code = cli.main()

    # Assert
    assert code == 1
    assert "setzt derselbe Befehl den Lauf fort" in capsys.readouterr().err
