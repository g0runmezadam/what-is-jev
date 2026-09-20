"""Shared fixtures for the test suite. No network, no real repo data."""

import json
import os
import sys
import tempfile
import unittest

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def jsonl(rows):
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)


def legacy_row(repo, **kw):
    row = {
        "repo": repo,
        "url": "https://github.com/" + repo,
        "kategori": "diger",
        "ne_yapiyor": "Bir sey yapiyor",
        "jev_gercek_mi": "belirsiz",
        "soru_tipleri": [],
        "P1_jev_derinligi": 1,
        "P2_bize_uygunluk": 1,
        "P3_fikir_yeniligi": 1,
        "P4_olgunluk": 1,
        "P5_kanit": 1,
        "toplam": 5,
        "sinif": "C",
        "alinacak_fikir": "yok",
        "risk": "gorulmedi",
        "kanit_url": "readme/" + repo.replace("/", "@") + ".md",
    }
    row.update(kw)
    return row


# A deliberately broken JSON line: invalid \P escape, and it carries a local
# path. Like the one real broken line, x/broken is sound in another file, so
# skipping this one loses nothing.
BROKEN_LINE = (
    '{"repo":"x/broken","url":"https://github.com/x/broken","kategori":"diger",'
    '"alinacak_fikir":"C:\\Projects notlarina bak","toplam":0}\n'
)

# A broken line whose repository appears nowhere else: skipping it would drop
# the repository silently, so the build must stop instead.
LOST_LINE = (
    '{"repo":"z/lost","url":"https://github.com/z/lost","kategori":"diger",'
    '"alinacak_fikir":"C:\\Projects","toplam":0}\n'
)


def make_legacy(root):
    """Build a small but representative repo-analizi/ tree under *root*."""
    ra = os.path.join(root, "repo-analizi")

    write(
        os.path.join(ra, "sonuc-00.jsonl"),
        jsonl([
            legacy_row(
                "a/one",
                kategori="ajan-kapisi",
                jev_gercek_mi="evet",
                soru_tipleri=["choice", "noul"],
                P1_jev_derinligi=3, P2_bize_uygunluk=3, P3_fikir_yeniligi=2,
                P4_olgunluk=2, P5_kanit=1, toplam=11, sinif="A",
                alinacak_fikir="Esik + belirsiz bandi",
            ),
            legacy_row(
                "b/two",
                kategori="kod-inceleme-hook",
                jev_gercek_mi="hayir",
                kanit_url="../ham/readme/b@two.md (jev gecmiyor)",
            ),
        ]) + BROKEN_LINE,
    )
    write(
        os.path.join(ra, "sonuc-01.jsonl"),
        jsonl([
            # same repo as in sonuc-00: the LAST file must win
            legacy_row(
                "a/one",
                kategori="ajan-kapisi",
                jev_gercek_mi="evet",
                soru_tipleri=["choice"],
                P1_jev_derinligi=2, P2_bize_uygunluk=2, P3_fikir_yeniligi=2,
                P4_olgunluk=2, P5_kanit=1, toplam=9, sinif="B",
                alinacak_fikir="Esik + belirsiz bandi",
            ),
            legacy_row("c/three", kategori="cli", kanit_url="eksik.txt"),
            # the same repo as the broken line in sonuc-00, written soundly here
            legacy_row("x/broken", kategori="diger"),
            legacy_row(
                "d/four",
                kategori="degerlendirme-benchmark",
                jev_gercek_mi="evet",
                kanit_url="https://github.com/d/four (docs/BENCH.md)",
            ),
        ]),
    )

    write(
        os.path.join(ra, "meta.jsonl"),
        jsonl([
            {"repo": "a/one", "desc": "Gate", "stars": 12, "forks": 3, "lang": "Python",
             "license": "MIT", "created": "2026-01-01T00:00:00Z",
             "pushed": "2026-09-01T00:00:00Z", "archived": False, "fork": False,
             "topics": ["jev"]},
            {"repo": "c/three", "desc": "CLI", "stars": 1, "forks": 0, "lang": "Go",
             "license": None, "created": "2026-02-02T00:00:00Z",
             "pushed": "2026-08-08T00:00:00Z", "archived": True, "fork": False,
             "topics": []},
        ]),
    )
    write(os.path.join(ra, "repos.txt"), "a/one\nb/two\n")
    write(os.path.join(ra, "yeni-repolar.tsv"),
          "c/three\thttps://github.com/c/three\n")
    return ra


def add_audit(root):
    write(
        os.path.join(root, "repo-analizi", "A-denetim.jsonl"),
        jsonl([
            {"repo": "a/one",
             "eski": {"P1": 2, "P2": 2, "P3": 2, "P4": 2, "P5": 1, "toplam": 9, "sinif": "B"},
             "yeni": {"P1": 1, "P2": 1, "P3": 1, "P4": 1, "P5": 1, "toplam": 5, "sinif": "C"},
             "degisti": True, "readme_acildi": True, "gerekce": "Sisirilmis P2",
             "mukerrer_of": None},
            {"repo": "b/two",
             "eski": {"P1": 1, "P2": 1, "P3": 1, "P4": 1, "P5": 1, "toplam": 5, "sinif": "C"},
             "yeni": {"P1": 1, "P2": 1, "P3": 1, "P4": 1, "P5": 1, "toplam": 5, "sinif": "C"},
             "degisti": False, "readme_acildi": False, "gerekce": "Ayni",
             "mukerrer_of": "a/one"},
        ]),
    )


def add_audit_notes(root, rows=None):
    """The bilingual audit notes, written for the public pages."""
    write(
        os.path.join(root, "repo-analizi", "denetim-notlari.jsonl"),
        jsonl(rows if rows is not None else [
            {"repo": "a/one", "audit_note_tr": "Sisirilmis uygunluk puani",
             "audit_note_en": "Inflated relevance score", "hardware_penalty": False},
            {"repo": "b/two", "audit_note_tr": "Ayni is", "audit_note_en": "Same work",
             "hardware_penalty": False},
        ]),
    )


def add_translations(root):
    ra = os.path.join(root, "repo-analizi")
    write(os.path.join(ra, "ceviri-0.jsonl"), jsonl([
        {"repo": "a/one", "summary_en": "Agent gate", "takeaway_en": "Threshold band",
         "risk_en": "none seen"},
    ]))
    # translator INPUT files must never be mistaken for translator output
    write(os.path.join(ra, "ceviri-girdi-0.jsonl"), jsonl([
        {"repo": "a/one", "ne_yapiyor": "Bir sey", "alinacak_fikir": "yok",
         "risk": "gorulmedi"},
    ]))


def add_notr(root, rows_tr=None, rows_en=None):
    """The neutralisation pass: rewritten rows that overwrite the imported text."""
    ra = os.path.join(root, "repo-analizi")
    write(os.path.join(ra, "notr-tr.jsonl"), jsonl(rows_tr if rows_tr is not None else [
        {"repo": "a/one", "summary_tr": "Notr ozet", "takeaway_tr": "Notr fikir",
         "risk_tr": "Notr risk"},
    ]))
    write(os.path.join(ra, "notr-en.jsonl"), jsonl(rows_en if rows_en is not None else [
        {"repo": "a/one", "summary_en": "Neutral summary",
         "takeaway_en": "Neutral takeaway", "risk_en": "Neutral risk"},
    ]))


def break_last_line(path):
    """Cut the last line of a jsonl file in half, the way a killed agent does."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    write(path, text + '{"repo":"a/one","yeni":{"P1":1,')


SOURCES = [
    {"id": "docs-llms", "type": "official-docs", "title": "TypeSafe docs",
     "url": "https://docs.typesafe.ai/llms.txt", "author": "TypeSafe",
     "date": "2026-09-01", "lang": "en", "trust": 5,
     "note_en": "Primary API reference.", "note_tr": "Birincil API belgesi.",
     "status": "read"},
    {"id": "own-calls", "type": "own-measurement", "title": "Our own calls",
     "url": "https://api.typesafe.ai/v1/systemone", "author": "us",
     "date": "2026-09-10", "lang": "en", "trust": 5,
     "note_en": "Latency and confidence behaviour.", "note_tr": "Gecikme ve guven.",
     "status": "read"},
]


class BaseCase(unittest.TestCase):
    def tmproot(self):
        d = tempfile.mkdtemp(prefix="jev-test-")
        self.addCleanup(self._rm, d)
        return d

    @staticmethod
    def _rm(d):
        import shutil
        shutil.rmtree(d, ignore_errors=True)
