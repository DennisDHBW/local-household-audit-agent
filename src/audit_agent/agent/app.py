"""Streamlit UI: question -> live evidence -> answer.

Start: ``uv run streamlit run src/audit_agent/agent/app.py``.

The page is a thin shell around ``AgentLoop``: it shows the evidence as soon as a search tool
returns, then the answer, then the step log. Everything testable lives in ``evidence_view``.
"""

from __future__ import annotations

import streamlit as st
from ollama import Client

from audit_agent.agent.evidence_view import evidence_sections
from audit_agent.agent.factory import create_agent
from audit_agent.agent.models import AgentStep, EvidenceBook, NudgeStep, ToolCallStep
from audit_agent.config import Settings
from audit_agent.corpus import CorpusError
from audit_agent.preflight import MissingModelError, ensure_models_available
from audit_agent.retrieval import RetrievalError


def _step_line(step: AgentStep) -> str:
    if isinstance(step, ToolCallStep):
        return f"- Werkzeug `{step.tool}` {step.arguments} → {step.state} ({step.seconds} s)"
    if isinstance(step, NudgeStep):
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
            with st.expander(title, expanded=True):
                st.markdown(body)


def main() -> None:
    st.set_page_config(page_title="Energie- & Nebenkosten-Auditor", layout="wide")
    st.title("Energie- & Nebenkosten-Auditor")
    settings = Settings.from_env()
    model = st.sidebar.text_input("Agent-Modell", settings.models.agent)
    st.sidebar.caption("Eine Frage dauert auf der CPU mehrere Minuten.")
    question = st.text_area("Frage zu deinen Unterlagen")
    if not st.button("Prüfen", disabled=not question.strip()):
        return

    client = Client(host=settings.ollama_host, timeout=settings.ollama_timeout_s)
    try:
        installed = [entry.model for entry in client.list().models]
        ensure_models_available(installed, [model, settings.models.embedding])
        agent = create_agent(settings, client)
    except (RetrievalError, MissingModelError, CorpusError) as error:
        st.error(str(error))
        return
    except Exception as error:  # Ollama not reachable: show it instead of a stack trace
        st.error(f"Ollama nicht erreichbar unter {settings.ollama_host}: {error}")
        return

    evidence_slot = st.empty()
    answer_slot = st.empty()
    log_slot = st.empty()
    lines: list[str] = []

    def on_step(step: AgentStep, book: EvidenceBook) -> None:
        lines.append(_step_line(step))
        log_slot.markdown("**Schritte**\n" + "\n".join(lines))
        _show_evidence(evidence_slot, book)

    _show_evidence(evidence_slot, EvidenceBook())
    with st.spinner("Der Agent sucht und rechnet …"):
        run = agent.run(question, model=model, on_step=on_step)
    with answer_slot.container():
        st.subheader("Antwort")
        st.markdown(run.answer or "_Keine Antwort erhalten._")
        st.caption(f"{run.stop_reason}, {run.tool_call_count} Werkzeugaufrufe, {run.seconds} s")


main()
