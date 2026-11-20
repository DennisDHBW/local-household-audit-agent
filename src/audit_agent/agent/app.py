"""Streamlit UI: chat with the agent -> live plan, evidence and steps -> answer with tables and
charts (ADR-0019).

Start: ``uv run streamlit run src/audit_agent/agent/app.py``.

The page is a thin shell around ``AgentLoop``. Earlier questions and answers of the chat go to
the agent as history, so a follow-up such as "und jetzt als Grafik?" works. Everything testable
lives in ``evidence_view`` and the loop.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from ollama import Client

from audit_agent.agent.evidence_view import evidence_sections
from audit_agent.agent.factory import create_agent
from audit_agent.agent.models import (
    AgentRun,
    AgentStep,
    Artifact,
    AuditFlowStep,
    EvidenceBook,
    NudgeStep,
    ToolCallStep,
)
from audit_agent.config import Settings
from audit_agent.corpus import CorpusError
from audit_agent.preflight import MissingModelError, ensure_models_available
from audit_agent.retrieval import RetrievalError

EXAMPLES = (
    "Ist die Heizstromabrechnung 2025 korrekt?",
    "Gib mir eine Übersicht über alle Kosten 2025.",
    "Erstelle eine Grafik zum Stromverbrauch 2024 und 2025, getrennt nach Licht- und Heizstrom.",
)


def _step_line(step: AgentStep) -> str:
    if isinstance(step, ToolCallStep):
        if step.tool == "plan" and step.is_valid:
            steps = "; ".join(str(s) for s in step.arguments.get("steps", []) or [])
            return f"- **Plan:** {steps}"
        return f"- Werkzeug `{step.tool}` {step.arguments} → {step.state} ({step.seconds} s)"
    if isinstance(step, NudgeStep | AuditFlowStep):
        return f"- {step.label}"
    calls = ", ".join(call.name for call in step.tool_calls) or "Antwort"
    return f"- Modell ({step.seconds} s, {step.prompt_tokens} Prompt-Token) → {calls}"


def _show_evidence(slot, book: EvidenceBook) -> None:
    sections = evidence_sections(book.numbered_hits)
    with slot.container():
        st.subheader("Belege")
        if not sections:
            st.caption("Noch keine Treffer.")
        for title, body in sections:
            with st.expander(title, expanded=False):
                st.markdown(body)


def _show_artifact(artifact: Artifact) -> None:
    st.markdown(f"**{artifact.title}**")
    if artifact.image_path and Path(artifact.image_path).is_file():
        st.image(artifact.image_path)
        with st.expander("Daten der Grafik"):
            st.markdown(artifact.markdown)
    else:
        st.markdown(artifact.markdown)


def _show_answer(run: AgentRun) -> None:
    st.markdown(run.answer or "_Keine Antwort erhalten._")
    for artifact in run.artifacts:
        _show_artifact(artifact)
    st.caption(f"{run.stop_reason}, {run.tool_call_count} Werkzeugaufrufe, {run.seconds} s")


def _agent(settings: Settings, model: str):
    client = Client(host=settings.ollama_host, timeout=settings.ollama_timeout_s)
    installed = [entry.model for entry in client.list().models]
    ensure_models_available(installed, [model, settings.models.embedding])
    return create_agent(settings, client)


def main() -> None:
    st.set_page_config(page_title="Energie- & Nebenkosten-Auditor", layout="wide")
    st.title("Energie- & Nebenkosten-Auditor")
    settings = Settings.from_env()
    model = st.sidebar.text_input("Agent-Modell", settings.models.agent)
    st.sidebar.caption("Eine Frage dauert auf der CPU mehrere Minuten.")
    st.sidebar.markdown("**Beispiele**\n" + "\n".join(f"- {e}" for e in EXAMPLES))
    if st.sidebar.button("Neuer Chat"):
        st.session_state["turns"] = []
    turns: list[AgentRun] = st.session_state.setdefault("turns", [])

    for run in turns:
        with st.chat_message("user"):
            st.markdown(run.question)
        with st.chat_message("assistant"):
            _show_answer(run)

    question = st.chat_input("Frage zu deinen Unterlagen")
    if not question:
        return
    with st.chat_message("user"):
        st.markdown(question)
    try:
        agent = _agent(settings, model)
    except (RetrievalError, MissingModelError, CorpusError) as error:
        st.error(str(error))
        return
    except Exception as error:  # Ollama not reachable: show it instead of a stack trace
        st.error(f"Ollama nicht erreichbar unter {settings.ollama_host}: {error}")
        return

    with st.chat_message("assistant"):
        left, right = st.columns([3, 2])
        log_slot = left.empty()
        evidence_slot = right.empty()
        lines: list[str] = []

        def on_step(step: AgentStep, book: EvidenceBook) -> None:
            lines.append(_step_line(step))
            log_slot.markdown("**Schritte**\n" + "\n".join(lines))
            _show_evidence(evidence_slot, book)

        history = [(run.question, run.answer) for run in turns]
        with st.spinner("Der Agent plant, sucht, prüft und rechnet …"):
            run = agent.run(question, model=model, on_step=on_step, history=history)
        _show_answer(run)
    turns.append(run)


main()
