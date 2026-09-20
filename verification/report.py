"""Turn the summaries into pages: one report per job, one index in two languages.

The reports are generated, not written by hand, for the same reason the rest of
this repository generates its pages: a hand-edited number drifts away from the
file it came from, and then nobody can tell which one is true. Everything here
comes from ``results/<job>/summary.json`` and the job file beside it.

``python -X utf8 verification/report.py``
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

BANNER = "<!-- GENERATED — do not edit; run verification/report.py -->"

BADGE = {
    "reproduced": "reproduced",
    "partially reproduced": "partially reproduced",
    "not reproduced": "not reproduced",
    "not run": "not run",
}

BADGE_TR = {
    "reproduced": "yeniden üretildi",
    "partially reproduced": "kısmen üretildi",
    "not reproduced": "üretilemedi",
    "not run": "koşulmadı",
}

KIND_TR = {
    "reproducibility-check": "tekrar üretilebilirlik testi",
    "independent-check": "bağımsız doğrulama",
}


def number(value, places=4):
    if value is None:
        return "n/a"
    if isinstance(value, (int,)) and not isinstance(value, bool):
        return str(value)
    return ("%." + str(places) + "f") % value


def interval(criterion):
    span = criterion.get("ci95")
    if not span:
        return "—"
    return "%s – %s" % (number(span[0], 3), number(span[1], 3))


def load(root):
    """Every job that has a summary, paired with its job file, id order."""
    out = []
    results = os.path.join(root, "results")
    if not os.path.isdir(results):
        return out
    for name in sorted(os.listdir(results)):
        path = os.path.join(results, name, "summary.json")
        job_path = os.path.join(root, "jobs", name + ".json")
        if not (os.path.exists(path) and os.path.exists(job_path)):
            continue
        with open(path, encoding="utf-8") as handle:
            summary = json.load(handle)
        with open(job_path, encoding="utf-8") as handle:
            job = json.load(handle)
        out.append((job, summary))
    return out


def report(job, summary):
    source = summary["source"]
    lines = [
        BANNER,
        "",
        "# %s" % summary.get("title", summary["id"]),
        "",
        "**Verdict: %s.** %s of %s items answered on %s, against %s."
        % (BADGE[summary["verdict"]], summary["answered"],
           summary["items_offered"], summary["run_at"],
           ", ".join(summary["model_versions"]) or "an unreported model version"),
        "",
        "This is a **%s**. %s" % (job.get("kind", "reproducibility-check"),
                                  job.get("kind_note", "")),
        "",
        "## What was run",
        "",
        "| | |",
        "| --- | --- |",
        "| source | [%s](%s) |" % (source["repo"], source["url"]),
        "| commit | `%s` |" % source["commit"],
        "| source's own run | %s |" % source.get("reported_run", "not stated"),
        "| licence | %s |" % source.get("license", "not stated"),
        "| corpus | %s |" % job.get("dataset", {}).get("name", "the source's own"),
        "| language of the test | %s |" % job.get("lang"),
        "| items | %s |" % job.get("sample", {}).get("rule", ""),
        "| live calls | %s |" % summary["calls"],
        "| failed calls | %s |" % summary["failed"],
        "",
        "The questions were copied character for character from the source at "
        "that commit; the file and line range are in "
        "[`jobs/%s.json`](../../jobs/%s.json), together with the digest of every "
        "file downloaded. Nothing was translated." % (summary["id"], summary["id"]),
        "",
        "## Reported against measured",
        "",
        "| metric | reported | measured | our 95% interval | verdict |",
        "| --- | --- | --- | --- | --- |",
    ]
    for criterion in summary["criteria"]:
        lines.append("| %s | %s | %s | %s | %s |" % (
            criterion["metric"], number(criterion["reported"]),
            number(criterion.get("observed")), interval(criterion),
            BADGE[criterion["verdict"]]))
    lines += [
        "",
        "The rule each row was judged by was committed before the first call of "
        "this job; the git history of the job file is the proof.",
        "",
        "## Deviations",
        "",
    ]
    for note in job.get("deviations_known_before_the_run", []):
        lines.append("- %s" % note)
    for note in summary.get("deviations_found", []):
        lines.append("- %s" % note)
    if summary["failed"]:
        lines.append("- %d call(s) came back without an answer and are counted "
                     "as spent, not as measurements." % summary["failed"])
    if summary.get("stopped"):
        lines.append("- The run stopped early: %s." % summary["stopped"])
    lines += [
        "",
        "## Limits",
        "",
        "- One run, no repeats. A single run cannot separate a real difference "
        "from ordinary variation between runs.",
        "- The verdict is about the number, not about the claim behind it. A "
        "reproduced accuracy on a corpus with noisy labels is still an accuracy "
        "on a corpus with noisy labels.",
        "- The raw answers are in `raw.jsonl` beside this file: one line per "
        "item, carrying the item's id and the digests of its text and its "
        "request, and no third-party text.",
        "",
    ]
    return "\n".join(lines)


def index(rows, lang):
    badge = BADGE if lang == "en" else BADGE_TR
    if lang == "en":
        head = [BANNER, "",
                "English | [Türkçe](../tr/verification/RESULTS.md)", "",
                "# Re-run results", "",
                "Every textual test we have re-run with our own key, in the "
                "test's original language and with its original inputs. The "
                "method is in [README.md](README.md); what each verdict was "
                "judged against is in the job file linked from each report.", "",
                "| test | source | kind | n | calls | verdict | report |",
                "| --- | --- | --- | --- | --- | --- | --- |"]
    else:
        head = [BANNER, "",
                "[English](../../verification/RESULTS.md) | Türkçe", "",
                "# Yeniden koşum sonuçları", "",
                "Kendi anahtarımızla, testin orijinal dilinde ve orijinal "
                "girdileriyle yeniden koştuğumuz metinsel testler. Yöntem: "
                "[README.md](README.md). Her hükmün neye göre verildiği, "
                "rapordan bağlanan iş tanımı dosyasında yazılı. Testlerin "
                "kendisi İngilizce koşuldu ve çevrilmedi.", "",
                "| test | kaynak | tür | n | çağrı | hüküm | rapor |",
                "| --- | --- | --- | --- | --- | --- | --- |"]
    prefix = "" if lang == "en" else "../../verification/"
    for job, summary in rows:
        kind = job.get("kind", "reproducibility-check")
        head.append("| %s | [%s](%s) | %s | %s | %s | %s | [%s](%sresults/%s/REPORT.md) |" % (
            summary.get("title", summary["id"]), summary["source"]["repo"],
            summary["source"]["url"],
            kind if lang == "en" else KIND_TR.get(kind, kind),
            summary["answered"], summary["calls"],
            badge[summary["verdict"]],
            "REPORT.md" if lang == "en" else "rapor", prefix, summary["id"]))
    head.append("")
    return "\n".join(head)


def main(root=None):
    root = root or HERE
    rows = load(root)
    for job, summary in rows:
        path = os.path.join(root, "results", summary["id"], "REPORT.md")
        write(path, report(job, summary))
    write(os.path.join(root, "RESULTS.md"), index(rows, "en"))
    write(os.path.join(os.path.dirname(root), "tr", "verification",
                       "RESULTS.md"), index(rows, "tr"))
    return len(rows)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text if text.endswith("\n") else text + "\n")


if __name__ == "__main__":
    print("%d report(s)" % main())
