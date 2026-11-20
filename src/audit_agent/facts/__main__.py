"""CLI: ``python -m audit_agent.facts build|audit`` (no Ollama needed)."""

from __future__ import annotations

import argparse
from collections import Counter

from audit_agent.config import Settings
from audit_agent.corpus import DocType, load_document_catalog
from audit_agent.facts import STATUS_LABELS, build_fact_store, check_bill, facts_path, fmt
from audit_agent.facts.views import TRACKED_UTILITIES


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m audit_agent.facts")
    parser.add_argument("command", choices=("build", "audit"))
    args = parser.parse_args()
    settings = Settings.from_env()
    store = build_fact_store(settings)
    store.save(facts_path(settings))
    counts = Counter(f.kind.value for f in store.facts)
    print(f"{len(store.facts)} Fakten nach {facts_path(settings)}: {dict(sorted(counts.items()))}")
    if args.command == "audit":
        catalog = load_document_catalog(settings.documents_file)
        for meta in catalog.documents:
            if meta.doc_type is not DocType.BILL or meta.utility_type not in TRACKED_UTILITIES:
                continue
            report = check_bill(store, meta)
            print(
                f"\n{meta.file}: {len(report.deviations)} Abweichung(en), "
                f"Auswirkung {fmt(report.total_impact, 'EUR', 2)}"
            )
            for check in report.checks:
                print(
                    f"  {STATUS_LABELS[check.status]:13} {check.name}: Soll {check.expected} | "
                    f"Ist {check.actual}"
                )


if __name__ == "__main__":
    main()
