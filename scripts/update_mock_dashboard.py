"""Refresh the Markdown progress dashboard from the criterion report."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATEGORIES={
    "V01":"Requirements and traceability","V02":"Workflow and deliverables",
    "V03":"Academic correctness","V04":"Source fidelity",
    "V05":"Print and visual quality","V06":"Historical regression",
    "V07":"Operations and repeatability","ARCH":"Architecture and isolation",
}


def main():
    report=json.loads((ROOT/"outputs/verification-report.json").read_text(encoding="utf-8-sig"))
    mandatory=[row for row in report["criteria"] if row["mandatory"]]
    passed=sum(row["status"]=="PASS" for row in mandatory)
    lines=[
        "# Mock Assessment dashboard","",
        f"**{passed} / {len(mandatory)} mandatory criteria verified ({100*passed/len(mandatory):.1f}%)**",
        f'**Status {report["status"]}** · Iteration {report["iteration"]}',"",
        "Percentages count criteria with recorded revision-bound evidence. Quality checks still pending remain unverified.","",
        "| Category | Verified | Percentage |","|---|---:|---:|",
    ]
    for prefix,label in CATEGORIES.items():
        rows=[row for row in mandatory if row["id"].startswith(prefix+".")]
        count=sum(row["status"]=="PASS" for row in rows)
        lines.append(f"| {label} | {count} / {len(rows)} | {100*count/len(rows):.1f}% |")
    lines+=["","## Current outcomes",""]
    lines+=["- "+line for line in report.get("current_outcomes",[])]
    lines+=["","## Next actions",""]
    lines += [f"{number}. {step}" for number,step in enumerate(report.get("next",[]),1)]
    lines+=["","**Your action** None required for implementation.","",
            "[Verification report](verification-report.md) · [Machine-readable criteria](verification-report.json)",
            "",f'Code revision reviewed: {report["revision"]}. Later code changes require dependent checks to be repeated.']
    (ROOT/"outputs/dashboard.md").write_bytes(("\n".join(lines)+"\n").encode("utf-8"))


if __name__=="__main__":
    main()