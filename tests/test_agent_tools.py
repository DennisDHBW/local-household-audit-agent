"""Calculator, tool schemas, argument cleaning and the five tools without Ollama."""

import pytest
from pydantic import ValidationError

from audit_agent.agent import CalculationError, EvidenceBook, ToolBox, ToolError, calculate
from audit_agent.agent.calculator import format_result, normalize_expression
from audit_agent.agent.tools import (
    CalculateArguments,
    FilterArguments,
    SearchArguments,
    clean_arguments,
    describe_filter,
    matches_year,
    tool_parameters,
)
from audit_agent.config import AgentSettings, Settings
from audit_agent.corpus import DocType, UtilityType
from audit_agent.ingestion import (
    ChunkMetadata,
    ChunkType,
    DocumentChunk,
    ParsedDocument,
    chunks_path,
)
from audit_agent.retrieval import MetadataFilter
from audit_agent.retrieval.evidence import shorten
from tests.agent_fakes import (
    BILL_FILE,
    CONTRACT_FILE,
    GAS_FILE,
    NOTICE_FILE,
    FakeBackend,
    make_catalog,
    make_hit,
)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("3100 * (0.395 - 0.382)", "40.3"),
        ("3250 * 0.348 + 12 * 11.50 - 80", "1189"),
        ("7320 * 78 / 312", "1830"),
        ("2 ** 3", "8"),
        ("-5 + 2", "-3"),
        ("0.1 + 0.2", "0.3"),
        ("3,5 * 2 €", "7"),
        ("100 EUR / 4", "25"),
    ],
)
def test_calculate_is_exact_and_liberal(expression, expected):
    # Arrange / Act
    result = format_result(calculate(expression))

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('ls')",
        "open('x')",
        "abs(-1)",
        "x + 1",
        "(1).real",
        "[1, 2]",
        "1 if True else 2",
        "True + 1",
        "5 % 2",
        "2 ** 11",
        "2 ** 0.5",
        "1 / 0",
        "",
        "1 +",
        "1 + " * 80 + "1",
        "9" * 250,
    ],
)
def test_calculate_rejects_everything_but_arithmetic(expression):
    with pytest.raises(CalculationError):
        calculate(expression)


def test_normalize_expression_changes_only_decimal_commas_and_currency():
    assert normalize_expression("1,5 + 2,25 EUR") == "1.5 + 2.25"
    assert normalize_expression("f(1, 2)") == "f(1, 2)"


def test_tool_parameters_are_flat_json_schema():
    # Act
    schema = tool_parameters(SearchArguments)
    list_schema = tool_parameters(FilterArguments)

    # Assert
    text = str(schema) + str(list_schema)
    assert "$ref" not in text and "$defs" not in text and "'title'" not in text
    assert schema["required"] == ["query"]
    assert schema["properties"]["utility_type"]["type"] == "string"
    assert schema["properties"]["include_counterpart"]["type"] == "boolean"
    assert list_schema["properties"]["doc_type"]["enum"] == [d.value for d in DocType]
    assert list_schema["properties"]["year"]["type"] == "integer"


def test_clean_arguments_drops_empty_values_and_flattens_filter():
    # Act
    cleaned = clean_arguments(
        {"query": "Preis", "doc_type": "null", "year": "", "filter": {"utility_type": "gas"}}
    )

    # Assert
    assert cleaned == {"query": "Preis", "utility_type": "gas"}


def test_arguments_are_validated_and_liberal():
    assert FilterArguments.model_validate({"year": "2024", "x": 1}).year == 2024
    # filters the search no longer offers are ignored, not rejected (ADR-0014)
    ignored = SearchArguments.model_validate({"query": "Preis", "doc_type": "bill", "year": 2024})
    assert not hasattr(ignored, "doc_type") and not hasattr(ignored, "year")
    with pytest.raises(ValidationError):
        SearchArguments.model_validate({"doc_type": "bill"})


def _toolbox(tmp_path, backend=None, **agent_options):
    settings = Settings(project_root=tmp_path, agent=AgentSettings(**agent_options))
    backend = backend or FakeBackend(lambda query, options: [make_hit()])
    return ToolBox(settings, backend, make_catalog()), backend, settings


def test_toolbox_offers_the_five_tools_with_specs(tmp_path):
    # Act
    tools = _toolbox(tmp_path)[0].tools()

    # Assert
    assert list(tools) == [
        "list_documents",
        "search",
        "search_images",
        "get_document_outline",
        "calculate",
    ]
    spec = tools["search"].spec()
    assert spec["type"] == "function"
    assert spec["function"]["name"] == "search"
    assert spec["function"]["parameters"]["required"] == ["query"]


@pytest.mark.parametrize(
    ("tool", "expected_types"),
    [
        ("search", {ChunkType.TEXT, ChunkType.TABLE_ROW}),
        ("search_images", {ChunkType.IMAGE}),
    ],
)
def test_search_tools_restrict_the_chunk_types(tmp_path, tool, expected_types):
    # Arrange
    toolbox, backend, _ = _toolbox(tmp_path)

    # Act
    toolbox.tools()[tool].run(SearchArguments(query="Arbeitspreis"), EvidenceBook())

    # Assert
    assert backend.calls[0][1].chunk_types == frozenset(expected_types)


def test_table_summaries_reach_the_model_only_when_switched_on(tmp_path):
    # Arrange
    toolbox, backend, _ = _toolbox(tmp_path, include_table_summaries=True)

    # Act
    toolbox.tools()["search"].run(SearchArguments(query="Preis"), EvidenceBook())

    # Assert
    assert backend.calls[0][1].chunk_types == {
        ChunkType.TEXT,
        ChunkType.TABLE_ROW,
        ChunkType.TABLE_SUMMARY,
    }


def test_usage_shows_the_call_shape_with_required_arguments(tmp_path):
    # Act
    tools = _toolbox(tmp_path)[0].tools()

    # Assert
    assert tools["calculate"].usage() == "calculate(expression*)"
    assert tools["search"].usage() == "search(query*, utility_type, include_counterpart)"


def test_search_result_text_numbers_hits_and_registers_them(tmp_path):
    # Arrange
    toolbox, _, _ = _toolbox(tmp_path)
    tool, book = toolbox.tools()["search"], EvidenceBook()

    # Act
    first = tool.run(SearchArguments(query="Arbeitspreis"), book)
    second = tool.run(SearchArguments(query="Preis"), book)

    # Assert
    assert first.hit_numbers == (1,) and second.hit_numbers == (1,)
    assert "[1] 04_Strom_Jahresabrechnung_2024.pdf, S. 1, Tabellenzeile" in first.text
    assert "Kapitel: Jahresrechnung" in first.text
    assert "34,80 ct/kWh" in first.text
    assert len(book.numbered_hits) == 1


def test_model_generated_hits_are_labelled_as_no_evidence(tmp_path):
    # Arrange
    summary = make_hit("s1", ChunkType.TABLE_SUMMARY, content="Die Tabelle zeigt Preise.")
    toolbox, _, _ = _toolbox(tmp_path, FakeBackend(lambda q, o: [summary]))

    # Act
    result = toolbox.tools()["search"].run(SearchArguments(query="Preise"), EvidenceBook())

    # Assert
    assert "KI-Zusammenfassung, kein Beleg" in result.text


def test_long_hits_are_shortened_for_the_model_but_not_in_the_book(tmp_path):
    # Arrange
    long_hit = make_hit(content="Kündigung " * 200)
    toolbox, _, _ = _toolbox(tmp_path, FakeBackend(lambda q, o: [long_hit]), max_hit_chars=300)
    book = EvidenceBook()

    # Act
    result = toolbox.tools()["search"].run(SearchArguments(query="Kündigung"), book)

    # Assert
    content_line = result.text.splitlines()[-1]
    assert len(content_line) == 300 and content_line.endswith("…")
    assert book.numbered_hits[0].hit.content == long_hit.content


def test_search_offers_the_sparte_filter_but_neither_document_type_nor_year():
    # Act
    fields = set(SearchArguments.model_fields)

    # Assert
    assert fields == {"query", "utility_type", "include_counterpart"}


def test_search_filters_by_utility_type_only(tmp_path):
    # Arrange
    toolbox, backend, _ = _toolbox(tmp_path)

    # Act
    toolbox.tools()["search"].run(
        SearchArguments(query="Preis", utility_type=UtilityType.GAS), EvidenceBook()
    )

    # Assert
    assert backend.calls[0][1].metadata_filter == MetadataFilter(utility_type=UtilityType.GAS)


def test_empty_filtered_search_is_not_repeated_and_names_the_inventory(tmp_path):
    # Arrange
    toolbox, backend, _ = _toolbox(tmp_path, FakeBackend(lambda q, o: []))

    # Act
    result = toolbox.tools()["search"].run(
        SearchArguments(query="Grundpreis", utility_type=UtilityType.DISTRICT_HEATING),
        EvidenceBook(),
    )

    # Assert
    assert len(backend.calls) == 1
    assert "Keine Treffer" in result.text
    assert "Vorhanden sind Unterlagen zu: electricity" in result.text
    assert "gas" in result.text and result.hit_numbers == ()


def _by_doc_type(options):
    """Bill hits for a bill search, contract hits for a contract search, else a bill hit."""
    if options.metadata_filter.doc_type is DocType.CONTRACT:
        return [make_hit("k1", filename=CONTRACT_FILE)]
    return [make_hit("b1", filename=BILL_FILE)]


def test_counterpart_search_adds_the_contract_to_a_bill_hit(tmp_path):
    # Arrange
    toolbox, backend, _ = _toolbox(tmp_path, FakeBackend(lambda q, o: _by_doc_type(o)))

    # Act
    result = toolbox.tools()["search"].run(
        SearchArguments(query="Arbeitspreis", include_counterpart=True), EvidenceBook()
    )

    # Assert
    doc_types = [call[1].metadata_filter.doc_type for call in backend.calls]
    assert doc_types[0] is None and DocType.CONTRACT in doc_types
    assert DocType.BILL not in doc_types
    assert result.hit_numbers == (1, 2)
    assert "Gegenstück" in result.text


def test_counterpart_search_uses_the_quantity_query(tmp_path):
    # Arrange
    toolbox, backend, _ = _toolbox(tmp_path, FakeBackend(lambda q, o: _by_doc_type(o)))

    # Act
    toolbox.tools()["search"].run(
        SearchArguments(query="neuer Arbeitspreis 2025", include_counterpart=True), EvidenceBook()
    )

    # Assert
    queries = [call[0] for call in backend.calls]
    assert queries[0] == "neuer Arbeitspreis 2025"
    assert queries[1:] and set(queries[1:]) == {"Arbeitspreis"}


def test_quantity_search_adds_only_new_hits_after_the_main_hits(tmp_path):
    # Arrange
    def hits(query, options):
        if query == "Arbeitspreis":
            return [make_hit("c1"), make_hit("row", content="Arbeitspreis | 38,20 ct")]
        return [make_hit("c1", content="Zwischenablesung"), make_hit("c2")]

    toolbox, backend, _ = _toolbox(tmp_path, FakeBackend(hits))

    # Act
    result = toolbox.tools()["search"].run(
        SearchArguments(query="neuer Arbeitspreis 2025"), EvidenceBook()
    )

    # Assert
    assert [call[0] for call in backend.calls] == ["neuer Arbeitspreis 2025", "Arbeitspreis"]
    assert result.hit_numbers == (1, 2, 3)
    assert result.text.index("Zwischenablesung") < result.text.index("38,20 ct")
    assert 'Weitere Treffer stammen aus einer Suche nur nach "Arbeitspreis"' in result.text


def test_quantity_search_is_skipped_for_a_short_query_and_when_switched_off(tmp_path):
    # Arrange
    short, short_backend, _ = _toolbox(tmp_path, FakeBackend(lambda q, o: [make_hit()]))
    off, off_backend, _ = _toolbox(
        tmp_path, FakeBackend(lambda q, o: [make_hit()]), quantity_hits=0
    )

    # Act
    short.tools()["search"].run(SearchArguments(query="Arbeitspreis"), EvidenceBook())
    off.tools()["search"].run(SearchArguments(query="neuer Arbeitspreis 2025"), EvidenceBook())

    # Assert
    assert len(short_backend.calls) == 1 and len(off_backend.calls) == 1


def test_counterpart_search_is_off_by_default(tmp_path):
    # Arrange
    toolbox, backend, _ = _toolbox(tmp_path, FakeBackend(lambda q, o: _by_doc_type(o)))

    # Act
    toolbox.tools()["search"].run(SearchArguments(query="Arbeitspreis"), EvidenceBook())

    # Assert
    assert len(backend.calls) == 1


def test_list_documents_filters_by_type_and_year(tmp_path):
    # Arrange
    tool = _toolbox(tmp_path)[0].tools()["list_documents"]

    # Act
    gas = tool.run(FilterArguments(utility_type=UtilityType.GAS), EvidenceBook()).text
    year_2025 = tool.run(FilterArguments(year=2025), EvidenceBook()).text
    everything = tool.run(FilterArguments(), EvidenceBook()).text

    # Assert
    assert gas.splitlines()[0].startswith("1 Dokumente")
    assert (
        "10_Gas_Jahresabrechnung_2025.pdf | gas / bill | G-9 | Zeitraum 2025-01-01..2025-12-31"
        in gas
    )
    assert "03_Strom_Preisanpassung_2025.pdf" in year_2025  # valid from 2025
    assert "04_Strom_Jahresabrechnung_2024.pdf" not in year_2025
    assert everything.splitlines()[0].startswith("4 Dokumente")
    assert "gültig ab 2024-01-01" in everything


def test_list_documents_says_so_when_nothing_exists(tmp_path):
    # Act
    text = (
        _toolbox(tmp_path)[0]
        .tools()["list_documents"]
        .run(FilterArguments(utility_type=UtilityType.ELECTRICITY, year=2023), EvidenceBook())
        .text
    )

    # Assert
    assert text.startswith("Keine Dokumente") and "liegen nicht vor" in text


def test_list_documents_limits_the_rows(tmp_path):
    # Act
    text = (
        _toolbox(tmp_path, max_list_rows=2)[0]
        .tools()["list_documents"]
        .run(FilterArguments(), EvidenceBook())
        .text
    )

    # Assert
    assert len(text.splitlines()) == 4 and "2 weitere" in text


def _write_outline(settings, file, headings):
    meta = make_catalog().by_file(file)
    chunks = tuple(
        DocumentChunk(
            chunk_id=f"{i}",
            chunk_type=ChunkType.HEADING,
            content=stack[-1],
            heading_stack=stack,
            page_number=page,
            metadata=ChunkMetadata.from_document(meta),
        )
        for i, (stack, page) in enumerate(headings)
    )
    path = chunks_path(settings.processed_dir, file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        ParsedDocument(file=file, page_count=2, chunks=chunks).model_dump_json(), encoding="utf-8"
    )


def test_outline_lists_headings_with_page_and_indent(tmp_path):
    # Arrange
    toolbox, _, settings = _toolbox(tmp_path)
    _write_outline(settings, CONTRACT_FILE, [(("Vertrag",), 1), (("Vertrag", "Kündigung"), 2)])
    from audit_agent.agent.tools import OutlineArguments

    # Act
    result = toolbox.tools()["get_document_outline"].run(
        OutlineArguments(filename="strom_vertrag"), EvidenceBook()
    )

    # Assert
    assert result.text.splitlines() == [
        "Gliederung von 01_Strom_Vertrag_2024.pdf:",
        "S. 1 Vertrag",
        "S. 2   Kündigung",
    ]


def test_outline_errors_are_tool_errors(tmp_path):
    # Arrange
    from audit_agent.agent.tools import OutlineArguments

    tool = _toolbox(tmp_path)[0].tools()["get_document_outline"]

    # Act / Assert
    with pytest.raises(ToolError, match="Kein Dokument"):
        tool.run(OutlineArguments(filename="Wasser"), EvidenceBook())
    with pytest.raises(ToolError, match="2 Dokumente"):
        tool.run(OutlineArguments(filename="Jahresabrechnung"), EvidenceBook())
    with pytest.raises(ToolError, match="noch nicht verarbeitet"):
        tool.run(OutlineArguments(filename="Preisanpassung"), EvidenceBook())


def test_calculate_tool_returns_expression_and_result_or_error(tmp_path):
    # Arrange
    tool = _toolbox(tmp_path)[0].tools()["calculate"]

    # Act
    result = tool.run(CalculateArguments(expression="3100 * (0.395 - 0.382)"), EvidenceBook())

    # Assert
    assert result.text == "3100 * (0.395 - 0.382) = 40.3"
    with pytest.raises(ToolError, match="Rechnung nicht möglich"):
        tool.run(CalculateArguments(expression="abs(1)"), EvidenceBook())


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1.963,28 - 1.920,00", "43.28"),
        ("12.345.678,5 + 0,5", "12345679"),
        ("1.963 + 1", "2.963"),
        ("1,5 + 2.250,25 EUR", "2251.75"),
    ],
)
def test_calculate_reads_german_thousands_separators_only_before_a_decimal_comma(
    expression, expected
):
    # Arrange / Act
    result = format_result(calculate(expression))

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    ("arguments", "expression"),
    [
        ({"a": "1.963,28", "b": "1.920,00", "operator": "-"}, "1.963,28 - 1.920,00"),
        ({"a": 3250, "b": 0.348, "op": "mal"}, "3250 * 0.348"),
        ({"x": "10", "y": "4", "operation": "Minus"}, "10 - 4"),
        ({"left": "7", "right": "2", "operator": "/"}, "7 / 2"),
        ({"a": "5", "b": "-3", "operator": "+"}, "5 + (-3)"),
        ({"expression": "2*3", "a": "1", "b": "2", "operator": "+"}, "2*3"),
    ],
)
def test_calculate_arguments_build_the_expression_from_operands(arguments, expression):
    # Arrange / Act
    parsed = CalculateArguments.model_validate(arguments)

    # Assert
    assert parsed.expression == expression


def test_calculate_operands_without_an_operator_are_not_guessed():
    # Arrange: G4 of RUN-013 sent two numbers and no operator
    arguments = {"a": "1.963,28", "b": "-1.920,00"}

    # Act
    with pytest.raises(ValidationError) as error:
        CalculateArguments.model_validate(arguments)

    # Assert: the message names the argument and shows the shape with the model's own numbers
    assert "expression" in str(error.value)
    assert 'expression="1.963,28 - -1.920,00"' in str(error.value)


def test_calculate_without_operands_still_reports_the_missing_expression():
    with pytest.raises(ValidationError, match="expression"):
        CalculateArguments.model_validate({"foo": "1"})
    with pytest.raises(ValidationError, match="expression"):
        CalculateArguments.model_validate({"a": "1"})


def test_operands_are_not_part_of_the_schema_shown_to_the_model(tmp_path):
    # Arrange
    tool = _toolbox(tmp_path)[0].tools()["calculate"]

    # Act
    properties = tool.spec()["function"]["parameters"]["properties"]

    # Assert
    assert list(properties) == ["expression"]


def test_helpers_describe_filter_shorten_and_match_year():
    catalog = make_catalog()
    assert describe_filter(MetadataFilter()) == "keine"
    assert (
        describe_filter(MetadataFilter.for_year(2024, UtilityType.GAS, DocType.BILL))
        == "Sparte=gas, Art=bill, Jahr=2024"
    )
    assert shorten("a  b\nc", 10) == "a b c"
    assert shorten("abcdef", 4) == "abc…"
    assert matches_year(catalog.by_file(BILL_FILE), 2024)
    assert not matches_year(catalog.by_file(BILL_FILE), 2025)
    assert matches_year(catalog.by_file(NOTICE_FILE), 2025)
    assert matches_year(catalog.by_file(CONTRACT_FILE), 2024)  # valid from
    assert not matches_year(catalog.by_file(CONTRACT_FILE), 2023)  # only written in 2023
    assert not matches_year(catalog.by_file(GAS_FILE), 2026)
