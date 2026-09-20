#!/usr/bin/env python3
"""Build the generated pages of the "What is Jev?" repository.

One source of truth (``data/repos.jsonl`` + ``data/sources.jsonl``), two
languages (root = English, ``tr/`` = Turkish), byte-for-byte deterministic
output: the same input always produces the same bytes, LF endings, UTF-8.

    python tools/build.py [--import-legacy] [--strict] [--check] [--root DIR]

``--import-legacy``  rebuild data/repos.jsonl from the 2026-09-19 working
                     files under repo-analizi/ (never written to, only read).
                     Not part of the normal flow: data/repos.jsonl is the one
                     source of truth and repo-analizi/ is on its way out of
                     the repository. A build without the flag never looks at
                     that directory; with the flag and no directory, it fails.
``--strict``         turn "missing translation" warnings into a failure
``--check``          write nothing; exit 1 if the generated files on disk are
                     not byte for byte the set the data asks for
``--root``           build another tree (used by the cross-process test)

Standard library only. No network. Nothing under ham/ is ever copied into a
generated page - only links.
"""

import argparse
import collections
import datetime
import glob
import hashlib
import json
import os
import re
import sys
import urllib.parse

# --------------------------------------------------------------------------
# constants

BANNER = "<!-- GENERATED — do not edit; run tools/build.py -->"

#: The date the legacy working files were produced. Used as first_seen /
#: scored_at on import so that a rebuild never depends on the wall clock.
IMPORT_DATE = "2026-09-19"
RUBRIC_VERSION = 1

CATEGORY_MAP = {
    "ajan-kapisi": "agent-gate",
    "kod-inceleme-hook": "code-review-hook",
    "yonlendirici-router": "model-router",
    "compaction-hafiza": "compaction-memory",
    "siniflandirma-triyaj": "classification-triage",
    "arama-rerank": "search-rerank",
    "guvenlik-injection": "security-injection",
    "tarayici-bilgisayar": "browser-computer-use",
    "oyun-demo": "game-demo",
    "sdk-istemci": "sdk-client",
    "cli": "cli",
    "mcp-skill-plugin": "mcp-skill-plugin",
    "degerlendirme-benchmark": "eval-benchmark",
    "liste-dizin": "list-directory",
    "metin-uretimi-deney": "text-generation-experiment",
    "diger": "other",
}

CATEGORY_TITLES = {
    "agent-gate": ("Agent gates", "Ajan kapıları"),
    "code-review-hook": ("Code review hooks", "Kod inceleme hook'ları"),
    "model-router": ("Model routers", "Model yönlendiriciler"),
    "compaction-memory": ("Compaction and memory", "Compaction ve hafıza"),
    "classification-triage": ("Classification and triage", "Sınıflandırma ve triyaj"),
    "search-rerank": ("Search and rerank", "Arama ve yeniden sıralama"),
    "security-injection": ("Security and prompt injection", "Güvenlik ve injection"),
    "browser-computer-use": ("Browser and computer use", "Tarayıcı ve bilgisayar kullanımı"),
    "game-demo": ("Games and demos", "Oyunlar ve demolar"),
    "sdk-client": ("SDKs and clients", "SDK'lar ve istemciler"),
    "cli": ("Command line tools", "Komut satırı araçları"),
    "mcp-skill-plugin": ("MCP servers, skills, plugins", "MCP, skill ve eklentiler"),
    "eval-benchmark": ("Evaluation and benchmarks", "Değerlendirme ve benchmark"),
    "list-directory": ("Lists and directories", "Listeler ve dizinler"),
    "text-generation-experiment": ("Text generation experiments", "Metin üretimi denemeleri"),
    "other": ("Other", "Diğer"),
}

CALLS_MAP = {"evet": "yes", "hayir": "no", "hayır": "no",
             "belirsiz": "unclear", "bilinmiyor": "unclear"}

SCORE_KEYS = [
    ("depth", "P1_jev_derinligi", "P1"),
    ("relevance", "P2_bize_uygunluk", "P2"),
    ("novelty", "P3_fikir_yeniligi", "P3"),
    ("maturity", "P4_olgunluk", "P4"),
    ("evidence", "P5_kanit", "P5"),
]

META_KEYS = [
    ("description", "desc"), ("stars", "stars"), ("forks", "forks"),
    ("language", "lang"), ("license", "license"), ("created_at", "created"),
    ("pushed_at", "pushed"), ("archived", "archived"), ("fork", "fork"),
    ("topics", "topics"),
]

SOURCE_TYPES = ["official-docs", "own-measurement", "independent-test", "article",
                "video", "community-list", "tool", "community-message"]
SOURCE_STATUS = ["read", "irrelevant", "unavailable"]
SOURCE_TYPE_TITLES = {
    "official-docs": ("Official documentation", "Resmî belgeler"),
    "own-measurement": ("Our own measurements", "Kendi ölçümlerimiz"),
    "independent-test": ("Independent tests", "Bağımsız testler"),
    "article": ("Articles", "Yazılar"),
    "video": ("Videos", "Videolar"),
    "community-list": ("Community lists", "Topluluk listeleri"),
    "tool": ("Tools", "Araçlar"),
    "community-message": ("Community messages", "Topluluk mesajları"),
}

QUESTION_TYPES = ["choice", "score", "noul"]
CLASSES = ["A", "B", "C"]

#: Every version of data/rubric.md that has ever scored a row. A row scored
#: with something else cannot be compared with the rest, so it is refused
#: rather than quietly mixed in.
RUBRIC_VERSIONS = (1,)

#: The shape of ``meta``: exactly these fields, each of these types. ``None``
#: means "we have not asked GitHub yet", which is not the same as zero.
NONE = type(None)
META_FIELD_TYPES = {
    "description": (str, NONE),
    "stars": (int, NONE),
    "forks": (int, NONE),
    "language": (str, NONE),
    "license": (str, NONE),
    "created_at": (str, NONE),
    "pushed_at": (str, NONE),
    "archived": (bool, NONE),
    "fork": (bool, NONE),
    "topics": (list,),
}

#: Everything that must never reach a public page, a public data file or a
#: handwritten document: a path on somebody's machine, an address on somebody's
#: private network, an e-mail address. The exception list starts empty on
#: purpose - ``noreply@`` addresses are addresses too.
PRIVACY_PATTERNS = [
    # C:\Projects, D:/Users/... - a drive letter, but never the "s:" of https://
    ("Windows sürücü yolu", re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]")),
    ("/mnt/ yolu", re.compile(r"/mnt/")),
    ("/home/ yolu", re.compile(r"/home/")),
    # ham/readme/x@y.md, ../ham/readme/... - a path INTO ham/, not the word
    ("ham/ yolu", re.compile(r"""(?:^|[\s("'])\.{0,2}[\\/]?ham[\\/][A-Za-z0-9._-]""")),
    ("özel IP", re.compile(
        r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
        r"|192\.168\.\d{1,3}\.\d{1,3})\b")),
    ("e-posta adresi", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
]

#: Deliberately empty. An address only gets in here by an operator decision.
EMAIL_ALLOWED = ()

#: Handwritten documents the privacy scan reads from disk.
HANDWRITTEN_GLOBS = ("*.md", "llms.txt", "tr/*.md", "tr/**/*.md", "data/*.md")

STATS_START = "<!-- STATS:START -->"
STATS_END = "<!-- STATS:END -->"


def privacy_hits(text):
    """Every private-looking thing in *text*, as (label, match) pairs."""
    hits = []
    for label, pattern in PRIVACY_PATTERNS:
        for match in pattern.finditer(text or ""):
            if label == "e-posta adresi" and match.group(0) in EMAIL_ALLOWED:
                continue
            hits.append((label, match.group(0)))
    return hits


# --------------------------------------------------------------------------
# small io helpers

#: Enough of a broken line to tell which repository it was about.
REPO_HINT = re.compile(r'"repo"\s*:\s*"([^"]{1,200})"')


def scan_jsonl(path):
    """Every non-empty line as (number, raw, object or None, error or None)."""
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for number, line in enumerate(fh, 1):
            raw = line.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except ValueError as exc:
                out.append((number, raw, None, "bozuk JSON (%s)" % exc))
                continue
            if not isinstance(obj, dict):
                out.append((number, raw, None, "JSON nesnesi değil"))
                continue
            out.append((number, raw, obj, None))
    return out


def read_jsonl(path):
    """Return (records, errors). A malformed line is skipped and reported."""
    records, errors = [], []
    for number, _raw, obj, error in scan_jsonl(path):
        if error:
            errors.append("%s:%d %s" % (os.path.basename(path), number, error))
        else:
            records.append(obj)
    return records, errors


def read_jsonl_strict(path):
    """Return (records, fatal). Here a malformed line is never just skipped.

    An agent that was killed mid-write leaves a half line behind. Skipping it
    silently drops a score, an audit or a translation and the build still says
    it passed - so these files fail instead.
    """
    records, fatal = [], []
    for number, _raw, obj, error in scan_jsonl(path):
        if error:
            fatal.append("%s:%d %s - yarım/bozuk satır atlanmaz"
                         % (os.path.basename(path), number, error))
        else:
            records.append(obj)
    return records, fatal


def write_text(path, text):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write_tmp(path, text):
    """Write ``path + ".tmp"`` and flush it all the way to the disk."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    return tmp


def write_text_atomic(path, text):
    """Write *text* so that no reader ever sees the file half written.

    The one source of truth is rewritten while other work may still fail; a
    torn ``data/repos.jsonl`` would be worse than no change at all. Write a
    neighbouring temporary file, flush it to the disk, then rename over the
    target - a rename within one directory either happened or did not.
    """
    os.replace(write_tmp(path, text), path)


def sha256_of(path):
    """The content hash of a file, as 64 hex characters."""
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def read_text(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read().replace("\r\n", "\n")


def read_bytes(path):
    """The file exactly as it is on disk. A CRLF is a difference."""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return fh.read()


def dump_jsonl(records):
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                   for r in records)


def read_lines(path):
    text = read_text(path)
    if text is None:
        return []
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


# --------------------------------------------------------------------------
# legacy import

def normalize_evidence_url(raw, url, report=None):
    """Turn the working files' ``kanit_url`` into a public https link.

    A local README path (``readme/x@y.md``, ``../ham/readme/x@y.md``, with or
    without a trailing note) becomes ``<repo url>#readme``; anything that is
    not an http(s) link falls back to the repository URL. Nothing under
    ``ham/`` is ever published - only this link.
    """
    raw = (raw or "").strip()
    if not raw:
        return url
    if raw.lower().startswith(("http://", "https://")):
        # drop trailing notes: "https://… (docs/X.md)" / "https://…; other"
        cleaned = re.split(r"[\s;]+", raw, 1)[0]
        if _is_http(cleaned):
            return cleaned
        # a tail we cannot clean away (a markdown escape, a stray bracket):
        # the row falls back to the repository and says so.
        if report is not None:
            report["warnings"].append(
                "kanit_url temizlenemedi -> repo URL'si kullanıldı (%r)" % raw)
        return url
    if re.match(r"^(\.\.[\\/])?(ham[\\/])?readme[\\/]", raw, re.IGNORECASE) and url:
        return url + "#readme"
    # eksik.txt, meta.jsonl, discord dökümü … : nothing public to point at,
    # so the row falls back to the repository itself. It never stays linkless.
    return url


def _meta_from(raw):
    meta = {}
    for name, legacy in META_KEYS:
        value = raw.get(legacy) if raw else None
        if name == "topics":
            value = list(value) if isinstance(value, list) else []
        meta[name] = value
    return meta


def _audit_scores(block):
    """Read the auditor's score block, which may use P1.. or P1_... names."""
    scores = {}
    for name, legacy, short in SCORE_KEYS:
        for key in (legacy, short, name):
            if key in block:
                scores[name] = int(block[key])
                break
        else:
            return None
    return scores


def import_legacy(root):
    """Build records from the repo-analizi/ working files. Read only."""
    area = os.path.join(root, "repo-analizi")
    report = {"lines": 0, "skipped": 0, "skipped_detail": [], "overridden": 0,
              "audited": 0, "audit_notes": 0, "missing_translation": 0,
              "meta_missing": 0, "neutralised": 0, "hardware_reverted": 0,
              "warnings": [], "fatal": []}

    if not os.path.isdir(area):
        report["fatal"].append(
            "repo-analizi/ yok - --import-legacy okuyacak bir şey bulamadı")
        return [], report

    discord = set(read_lines(os.path.join(area, "repos.txt")))
    topic = set()
    for line in read_lines(os.path.join(area, "yeni-repolar.tsv")):
        topic.add(line.split("\t")[0].strip())

    meta_rows, meta_errors = read_jsonl(os.path.join(area, "meta.jsonl"))
    report["skipped_detail"].extend(meta_errors)
    meta_by_repo = {}
    for row in meta_rows:
        if row.get("repo"):
            meta_by_repo[row["repo"].lower()] = row

    # sonuc-*.jsonl, sorted by name; when a repo appears twice the LAST file wins
    by_repo = {}
    broken = []
    for path in sorted(glob.glob(os.path.join(area, "sonuc-*.jsonl"))):
        rows = []
        for number, raw, obj, error in scan_jsonl(path):
            report["lines"] += 1
            if error:
                hint = REPO_HINT.search(raw)
                broken.append((os.path.basename(path), number, error,
                               hint.group(1).strip() if hint else None))
                continue
            rows.append(obj)
        for row in rows:
            repo = (row.get("repo") or "").strip()
            if not repo:
                report["skipped"] += 1
                report["skipped_detail"].append(
                    "%s: repo alanı boş satır atlandı" % os.path.basename(path))
                continue
            key = repo.lower()
            if key in by_repo:
                report["overridden"] += 1
            by_repo[key] = (repo, row, os.path.basename(path))

    # A broken legacy line is forgiven only when the repository it was about
    # is sound in another file - then nothing is lost. Otherwise the build
    # stops rather than quietly shipping a shorter list.
    for name, number, error, hint in broken:
        if hint and hint.lower() in by_repo:
            report["skipped"] += 1
            report["skipped_detail"].append(
                "%s:%d %s - %s başka dosyada sağlam" % (name, number, error, hint))
        else:
            report["fatal"].append(
                "%s:%d %s - repo kurtarılamadı (%s)"
                % (name, number, error, hint or "repo adı okunamadı"))

    records = []
    for key in sorted(by_repo):
        repo, row, _source_file = by_repo[key]
        url = (row.get("url") or "").strip() or "https://github.com/" + repo

        legacy_category = (row.get("kategori") or "diger").strip()
        category = CATEGORY_MAP.get(legacy_category)
        if category is None:
            category = "other"
            report["warnings"].append(
                "%s: bilinmeyen kategori %r -> other" % (repo, legacy_category))

        legacy_calls = (row.get("jev_gercek_mi") or "").strip().lower()
        calls = CALLS_MAP.get(legacy_calls)
        if calls is None:
            calls = "unclear"
            if legacy_calls:
                report["warnings"].append(
                    "%s: bilinmeyen jev_gercek_mi %r -> unclear" % (repo, legacy_calls))

        scores = {}
        for name, legacy, _short in SCORE_KEYS:
            try:
                scores[name] = int(row.get(legacy, 0))
            except (TypeError, ValueError):
                scores[name] = 0
                report["warnings"].append("%s: %s sayı değil -> 0" % (repo, legacy))
        total = sum(scores.values())
        if row.get("toplam") != total:
            report["warnings"].append(
                "%s: toplam %r puan toplamıyla (%d) uyuşmuyor -> hesaplanan kullanıldı"
                % (repo, row.get("toplam"), total))

        klass = (row.get("sinif") or "").strip().upper()
        if klass not in CLASSES:
            klass = expected_class(total, scores["relevance"], scores["novelty"])
            report["warnings"].append("%s: sınıf okunamadı -> %s" % (repo, klass))

        raw_meta = meta_by_repo.get(key)
        if raw_meta is None:
            report["meta_missing"] += 1

        question_types = [q for q in (row.get("soru_tipleri") or [])
                          if q in QUESTION_TYPES]

        if repo in discord:
            source_set = "discord"
        elif repo in topic:
            source_set = "topic"
        else:
            source_set = "manual"

        records.append({
            "repo": repo,
            "url": url,
            "source_set": source_set,
            "first_seen": IMPORT_DATE,
            "scored_at": IMPORT_DATE,
            "rubric_version": RUBRIC_VERSION,
            "meta": _meta_from(raw_meta),
            "category": category,
            "calls_jev": calls,
            "question_types": question_types,
            "scores": scores,
            "total": total,
            "class": klass,
            "summary_en": "",
            "summary_tr": (row.get("ne_yapiyor") or "").strip(),
            "takeaway_en": "",
            "takeaway_tr": (row.get("alinacak_fikir") or "").strip(),
            "risk_en": "",
            "risk_tr": (row.get("risk") or "").strip(),
            "evidence_url": normalize_evidence_url(row.get("kanit_url"), url, report),
            "audited": False,
            "audit_note_en": "",
            "audit_note_tr": "",
            "duplicate_of": None,
            "status": "active",
        })

    index = {r["repo"].lower(): r for r in records}
    notes = _audit_notes(area, report)
    _apply_audit(area, index, report, notes)
    _apply_audit_notes(index, report, notes)
    _apply_translations(area, index, report)
    _apply_notr(area, index, report)

    for rec in records:
        if not rec["summary_en"]:
            report["missing_translation"] += 1

    return records, report


def _audit_notes(area, report):
    """``denetim-notlari.jsonl``: the note written FOR the public pages.

    The auditor's own ``gerekce`` in ``A-denetim.jsonl`` is an internal note in
    one language, written for us; it never reaches the data file. This file is
    the public one, and it carries both languages plus the hardware flag.
    """
    path = os.path.join(area, "denetim-notlari.jsonl")
    if not os.path.exists(path):
        report["warnings"].append(
            "repo-analizi/denetim-notlari.jsonl yok - denetim notları boş kalıyor")
        return {}
    rows, fatal = read_jsonl_strict(path)
    report["fatal"].extend(fatal)
    notes = {}
    for row in rows:
        repo = (row.get("repo") or "").strip().lower()
        if repo:
            notes[repo] = row
    return notes


def _apply_audit_notes(index, report, notes):
    for repo, row in sorted(notes.items()):
        rec = index.get(repo)
        if rec is None:
            report["warnings"].append(
                "denetim-notlari: %s data'da yok - atlandı" % row.get("repo"))
            continue
        rec["audit_note_en"] = str(row.get("audit_note_en") or "").strip()
        rec["audit_note_tr"] = str(row.get("audit_note_tr") or "").strip()
        report["audit_notes"] += 1


def _revert_hardware_penalty(row, scores, note, repo, report):
    """Undo a relevance cut that only made sense on the auditor's own machine.

    A few rows lost relevance because the project needs hardware the auditor
    did not have. At the scale this repository is published at that is not a
    property of the project, so ``relevance`` goes back to what it was before
    the audit. The other four axes, and the note, are the auditor's and stay.
    Mutates *scores* in place; returns whether anything changed.
    """
    if not (note or {}).get("hardware_penalty"):
        return False
    old = _audit_scores(row.get("eski") or {})
    if old is None:
        report["warnings"].append(
            "%s: donanım cezası geri alınamadı - eski puanlar okunamadı" % repo)
        return False
    if old["relevance"] == scores["relevance"]:
        return False
    scores["relevance"] = old["relevance"]
    report["hardware_reverted"] += 1
    return True


def _apply_audit(area, index, report, notes=None):
    notes = notes or {}
    path = os.path.join(area, "A-denetim.jsonl")
    if not os.path.exists(path):
        report["warnings"].append(
            "repo-analizi/A-denetim.jsonl yok - denetim uygulanmadı")
        return
    rows, fatal = read_jsonl_strict(path)
    report["fatal"].extend(fatal)
    for row in rows:
        repo = (row.get("repo") or "").strip().lower()
        rec = index.get(repo)
        if rec is None:
            report["warnings"].append(
                "A-denetim: %s data'da yok - atlandı" % row.get("repo"))
            continue
        new = row.get("yeni") or {}
        scores = _audit_scores(new)
        if scores is not None:
            reverted = _revert_hardware_penalty(
                row, scores, notes.get(repo), rec["repo"], report)
            rec["scores"] = scores
            rec["total"] = sum(scores.values())
            klass = str(new.get("sinif") or "").strip().upper()
            # a reverted relevance changes the total, so the auditor's own
            # class label no longer describes the row: recompute it.
            rec["class"] = expected_class(
                rec["total"], scores["relevance"], scores["novelty"]) \
                if reverted or klass not in CLASSES else klass
        rec["audited"] = True
        duplicate = row.get("mukerrer_of") or None
        rec["duplicate_of"] = duplicate.strip() if isinstance(duplicate, str) else None
        report["audited"] += 1


def _translation_files(area):
    """``ceviri-*.jsonl`` minus the translator's own INPUT files."""
    out = []
    for path in sorted(glob.glob(os.path.join(area, "ceviri-*.jsonl"))):
        if os.path.basename(path).startswith("ceviri-girdi"):
            continue
        out.append(path)
    return out


def _apply_translations(area, index, report):
    files = _translation_files(area)
    if not files:
        report["warnings"].append(
            "repo-analizi/ceviri-*.jsonl yok - İngilizce alanlar boş kalıyor")
        return
    aliases = {
        "summary_en": ("summary_en", "ne_yapiyor_en"),
        "takeaway_en": ("takeaway_en", "alinacak_fikir_en"),
        "risk_en": ("risk_en",),
    }
    for path in files:
        rows, fatal = read_jsonl_strict(path)
        report["fatal"].extend(fatal)
        for row in rows:
            rec = index.get((row.get("repo") or "").strip().lower())
            if rec is None:
                continue
            for field, keys in aliases.items():
                for key in keys:
                    value = row.get(key)
                    if isinstance(value, str) and value.strip():
                        rec[field] = value.strip()
                        break


#: The neutralisation pass: rows rewritten by hand (or by an agent) to take a
#: local path or a private detail out of the text. It runs last, so it wins.
NOTR_FILES = [
    ("notr-tr.jsonl", ("summary_tr", "takeaway_tr", "risk_tr")),
    ("notr-en.jsonl", ("summary_en", "takeaway_en", "risk_en")),
]


def _apply_notr(area, index, report):
    for name, fields in NOTR_FILES:
        path = os.path.join(area, name)
        if not os.path.exists(path):
            report["warnings"].append(
                "repo-analizi/%s yok - nötrleştirme uygulanmadı" % name)
            continue
        rows, fatal = read_jsonl_strict(path)
        report["fatal"].extend(fatal)
        for row in rows:
            rec = index.get((row.get("repo") or "").strip().lower())
            if rec is None:
                report["warnings"].append(
                    "%s: %s data'da yok - atlandı" % (name, row.get("repo")))
                continue
            applied = False
            for field in fields:
                value = row.get(field)
                if isinstance(value, str) and value.strip():
                    rec[field] = value.strip()
                    applied = True
            if applied:
                report["neutralised"] += 1


# --------------------------------------------------------------------------
# validation

def expected_class(total, relevance, novelty):
    if total >= 11 or (relevance == 3 and novelty >= 2):
        return "A"
    if total >= 7:
        return "B"
    return "C"


#: A url we are willing to print. No space, no control character, and none of
#: the characters that would let it break out of ``[label](target)``.
URL_FORBIDDEN = set(')]<>"\'`')
URL_SCHEME = re.compile(r"^https?://[^/\s]", re.IGNORECASE)

#: ``url`` is the repository itself and nothing else. \Z, not $: a trailing
#: newline must not slip through.
REPO_URL = re.compile(
    r"\Ahttps://github\.com/[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+\Z")
REPO_NAME = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+\Z")

#: Text that must never appear in a text field: it would survive as markup on
#: somebody's machine even if our own renderer escapes it.
TEXT_FORBIDDEN = [
    ("HTML etiketi", re.compile(r"<\s*/?\s*[A-Za-z!][^>]*>")),
    ("markdown bağlantısı ](", re.compile(r"\]\(")),
    ("javascript: şeması", re.compile(r"javascript\s*:", re.IGNORECASE)),
    ("data: şeması", re.compile(r"data\s*:", re.IGNORECASE)),
]

TEXT_FIELDS = ["summary_en", "summary_tr", "takeaway_en", "takeaway_tr",
               "risk_en", "risk_tr", "audit_note_en", "audit_note_tr"]


def _is_http(value):
    """A strict url: http(s), no whitespace, no bracket, no quote."""
    if not isinstance(value, str) or not URL_SCHEME.match(value):
        return False
    for ch in value:
        if ch.isspace() or ord(ch) < 0x21 or ord(ch) == 0x7F or ch in URL_FORBIDDEN:
            return False
    return True


def _text_problems(where, field, value):
    if not isinstance(value, str):
        return []
    out = []
    for label, pattern in TEXT_FORBIDDEN:
        match = pattern.search(value)
        if match:
            out.append("%s: %s içinde %s var (%r)"
                       % (where, field, label, match.group(0)))
    return out


#: A date, not a timestamp: the pages must not move when the clock does.
DATE_RE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")


def is_date(value):
    """``YYYY-MM-DD`` and a day that exists. 2026-02-30 is neither."""
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _meta_problems(where, meta):
    """``meta`` is exactly the ten GitHub fields, each of its own type."""
    if not isinstance(meta, dict):
        return ["%s: meta nesne değil (%r)" % (where, meta)]
    out = []
    missing = sorted(set(META_FIELD_TYPES) - set(meta))
    extra = sorted(set(meta) - set(META_FIELD_TYPES))
    if missing:
        out.append("%s: meta eksik alan: %s" % (where, ", ".join(missing)))
    if extra:
        out.append("%s: meta şemada olmayan alan: %s" % (where, ", ".join(extra)))
    for field, types in META_FIELD_TYPES.items():
        if field not in meta:
            continue
        value = meta[field]
        # bool is an int in Python; a star count of ``True`` is not a count.
        ok = isinstance(value, types) and not (
            bool not in types and isinstance(value, bool))
        if not ok:
            out.append("%s: meta.%s türü yanlış (%r)" % (where, field, value))
        elif field == "topics" and not all(isinstance(t, str) for t in value):
            out.append("%s: meta.topics yalnız metin içerebilir (%r)"
                       % (where, value))
    return out


def validate(records, sources=None, strict=False):
    """Return (errors, warnings). Errors make the build fail.

    This is the one validation there is: ``data/repos.jsonl`` and an incoming
    batch line are held to the same rules, because a batch line becomes a
    ``data/repos.jsonl`` line the moment it is applied.
    """
    errors, warnings = [], []
    seen = {}
    for rec in records:
        repo = rec.get("repo")
        where = repo or "<repo alanı yok>"
        if not repo:
            errors.append("repo alanı yok: %r" % (rec,))
        elif not (isinstance(repo, str) and REPO_NAME.match(repo)):
            errors.append("%s: repo owner/name değil (%r)" % (where, repo))
        else:
            key = repo.lower()
            if key in seen:
                errors.append("%s: repo tekil değil (%s ile çakışıyor)" % (repo, seen[key]))
            seen[key] = repo

        if not _is_http(rec.get("url")):
            errors.append("%s: url http(s) değil (%r)" % (where, rec.get("url")))
        elif not REPO_URL.match(rec["url"]):
            errors.append("%s: url tam olarak https://github.com/<owner>/<name> "
                          "değil (%r)" % (where, rec["url"]))
        if not _is_http(rec.get("evidence_url")):
            errors.append("%s: evidence_url http(s) değil (%r)"
                          % (where, rec.get("evidence_url")))

        duplicate = rec.get("duplicate_of")
        if duplicate is not None and not (isinstance(duplicate, str)
                                          and REPO_NAME.match(duplicate)):
            errors.append("%s: duplicate_of owner/name değil (%r)" % (where, duplicate))

        for field in TEXT_FIELDS:
            if field in rec and not isinstance(rec[field], str):
                errors.append("%s: %s metin değil (%r)" % (where, field, rec[field]))
            errors.extend(_text_problems(where, field, rec.get(field)))
        errors.extend(_text_problems(
            where, "meta.description", (rec.get("meta") or {}).get("description")))

        for field in ("first_seen", "scored_at"):
            if not is_date(rec.get(field)):
                errors.append("%s: %s YYYY-MM-DD bir takvim günü değil (%r)"
                              % (where, field, rec.get(field)))
        if rec.get("rubric_version") not in RUBRIC_VERSIONS:
            errors.append("%s: rubric_version bilinen sürümlerden biri değil "
                          "(%r, bilinen: %s)"
                          % (where, rec.get("rubric_version"),
                             ", ".join(str(v) for v in RUBRIC_VERSIONS)))
        errors.extend(_meta_problems(where, rec.get("meta")))
        if not isinstance(rec.get("audited"), bool):
            errors.append("%s: audited doğru/yanlış değil (%r)"
                          % (where, rec.get("audited")))

        if rec.get("category") not in CATEGORY_TITLES:
            errors.append("%s: category geçersiz (%r)" % (where, rec.get("category")))
        if rec.get("calls_jev") not in ("yes", "no", "unclear"):
            errors.append("%s: calls_jev geçersiz (%r)" % (where, rec.get("calls_jev")))
        if rec.get("class") not in CLASSES:
            errors.append("%s: class geçersiz (%r)" % (where, rec.get("class")))
        if rec.get("status") not in ("active", "gone"):
            errors.append("%s: status geçersiz (%r)" % (where, rec.get("status")))
        if rec.get("source_set") not in ("discord", "topic", "manual"):
            errors.append("%s: source_set geçersiz (%r)" % (where, rec.get("source_set")))
        questions = rec.get("question_types")
        if not isinstance(questions, list):
            errors.append("%s: question_types liste değil (%r)" % (where, questions))
        else:
            if len(set(map(repr, questions))) != len(questions):
                errors.append("%s: question_types tekrar içeriyor (%r)"
                              % (where, questions))
            for question in questions:
                if question not in QUESTION_TYPES:
                    errors.append("%s: question_types geçersiz (%r)"
                                  % (where, question))

        scores = rec.get("scores") or {}
        names = [name for name, _l, _s in SCORE_KEYS]
        if sorted(scores) != sorted(names):
            errors.append("%s: scores alanları eksik/fazla (%r)" % (where, sorted(scores)))
        else:
            for name in names:
                value = scores[name]
                if not isinstance(value, int) or not 0 <= value <= 3:
                    errors.append("%s: scores.%s 0-3 aralığında değil (%r)"
                                  % (where, name, value))
            if isinstance(rec.get("total"), int) and rec["total"] != sum(scores.values()):
                errors.append("%s: total (%r) puan toplamı (%d) değil"
                              % (where, rec.get("total"), sum(scores.values())))
            elif not isinstance(rec.get("total"), int):
                errors.append("%s: total sayı değil (%r)" % (where, rec.get("total")))
            else:
                wanted = expected_class(rec["total"], scores["relevance"], scores["novelty"])
                # An audited row carries a human judgement and may differ. An
                # unaudited one is nothing but the rubric applied to the scores,
                # so a class the rubric does not produce is simply wrong.
                if wanted != rec.get("class") and not rec.get("audited"):
                    errors.append("%s: class %s, denetlenmemiş satırda ölçek %s "
                                  "diyor" % (where, rec.get("class"), wanted))

        if not str(rec.get("summary_tr") or "").strip():
            warnings.append("%s: summary_tr boş" % where)
        if strict and not str(rec.get("summary_en") or "").strip():
            errors.append("%s: summary_en boş (--strict)" % where)

    errors.extend(_validate_sources(sources or []))
    return errors, warnings


def _validate_sources(sources):
    errors = []
    seen = set()
    for src in sources:
        where = src.get("id") or src.get("title") or "<kaynak>"
        if not src.get("id"):
            errors.append("kaynak: id yok (%r)" % (src.get("title"),))
        elif src["id"] in seen:
            errors.append("kaynak: id tekil değil (%s)" % src["id"])
        seen.add(src.get("id"))
        if not _is_http(src.get("url")):
            errors.append("%s: kaynak url http(s) değil (%r)" % (where, src.get("url")))
        if src.get("type") not in SOURCE_TYPES:
            errors.append("%s: kaynak type geçersiz (%r)" % (where, src.get("type")))
        if src.get("status") not in SOURCE_STATUS:
            errors.append("%s: kaynak status geçersiz (%r)" % (where, src.get("status")))
        trust = src.get("trust")
        if not isinstance(trust, int) or not 1 <= trust <= 5:
            errors.append("%s: kaynak trust 1-5 değil (%r)" % (where, trust))
        for field in ("title", "author", "note_en", "note_tr"):
            errors.extend(_text_problems(where, "kaynak " + field, src.get(field)))
    return errors


def _scan_record(rec, problems):
    where = rec.get("repo") or "<repo alanı yok>"
    for field in TEXT_FIELDS + ["url", "evidence_url"]:
        for label, found in privacy_hits(rec.get(field)):
            problems.append("data/repos.jsonl %s alan %s: %s (%r)"
                            % (where, field, label, found))
    for label, found in privacy_hits((rec.get("meta") or {}).get("description")):
        problems.append("data/repos.jsonl %s alan meta.description: %s (%r)"
                        % (where, label, found))


def scan_privacy(root, records, pages):
    """Look for private data everywhere it could still be hiding.

    The data file, every page we are about to write, every other ``data/*.jsonl``
    and every handwritten document. A handwritten document is reported, never
    repaired - the operator owns that text.
    """
    problems = []
    for rec in records:
        _scan_record(rec, problems)

    for path in sorted(glob.glob(os.path.join(root, "data", "*.jsonl"))):
        if os.path.basename(path) == "repos.jsonl":
            continue
        rel = "data/" + os.path.basename(path)
        for number, line in enumerate((read_text(path) or "").splitlines(), 1):
            for label, found in privacy_hits(line):
                problems.append("%s:%d: %s (%r)" % (rel, number, label, found))

    for name in sorted(pages):
        for number, line in enumerate(pages[name].splitlines(), 1):
            for label, found in privacy_hits(line):
                problems.append("%s:%d: %s (%r)" % (name, number, label, found))

    for rel in _handwritten(root, set(pages)):
        for number, line in enumerate((read_text(os.path.join(root, rel)) or
                                       "").splitlines(), 1):
            for label, found in privacy_hits(line):
                problems.append("%s:%d: %s (%r) [elle yazılmış - düzeltilmedi]"
                                % (rel, number, label, found))
    return problems


def _handwritten(root, generated):
    """Handwritten documents: the markdown we did not generate, plus llms.txt."""
    names = set()
    for pattern in HANDWRITTEN_GLOBS:
        for path in glob.glob(os.path.join(root, *pattern.split("/")),
                              recursive=True):
            if not os.path.isfile(path):
                continue
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if rel in generated:
                continue
            text = read_text(path) or ""
            if text.startswith(BANNER):
                continue
            names.add(rel)
    return sorted(names)


#: The pages this script owns, wherever they are: the three fixed ones and
#: whatever sits under categories/. A file only counts as ours when it starts
#: with the GENERATED banner - a handwritten note in the same folder is safe.
GENERATED_NAMES = ("SOURCES.md", "REPOS.md", "TOP.md")


def discover_generated(root):
    """Every generated page actually on disk, as page names."""
    names = set()
    candidates = []
    for prefix in ("", "tr/"):
        candidates.extend(prefix + name for name in GENERATED_NAMES)
        for path in glob.glob(os.path.join(root, *(prefix + "categories/*.md")
                                           .split("/"))):
            candidates.append(os.path.relpath(path, root).replace(os.sep, "/"))
    marker = BANNER.encode("utf-8")
    for name in candidates:
        blob = read_bytes(os.path.join(root, *name.split("/")))
        if blob is not None and blob.startswith(marker):
            names.add(name)
    return names


def check_language_parity(pages):
    """Every root page must have a tr/ twin and the other way round."""
    problems = []
    root_pages = {name for name in pages if not name.startswith("tr/")}
    tr_pages = {name[3:] for name in pages if name.startswith("tr/")}
    for name in sorted(root_pages - tr_pages):
        problems.append("tr/%s eksik" % name)
    for name in sorted(tr_pages - root_pages):
        problems.append("%s eksik (tr/ karşılığı var)" % name)
    return problems


# --------------------------------------------------------------------------
# statistics

def counted(records):
    """Rows that count: duplicates are listed but never counted."""
    return [r for r in records if not r.get("duplicate_of")]


def stats(records, sources):
    rows = counted(records)
    calls = {key: 0 for key in ("yes", "no", "unclear")}
    classes = {key: 0 for key in CLASSES}
    categories = collections.Counter()
    for rec in rows:
        calls[rec["calls_jev"]] = calls.get(rec["calls_jev"], 0) + 1
        classes[rec["class"]] = classes.get(rec["class"], 0) + 1
        categories[rec["category"]] += 1
    source_types = collections.Counter(s.get("type") for s in sources)
    scored = sorted(r.get("scored_at") or "" for r in records)
    return {
        "total": len(rows),
        "duplicates": len(records) - len(rows),
        "calls_jev": calls,
        "classes": classes,
        # not most_common(): ties there keep the order the rows arrived in,
        # so the same data in a different order gave a different page
        "categories": sorted(categories.items(), key=lambda kv: (-kv[1], kv[0])),
        "sources": len(sources),
        "source_types": sorted(source_types.items()),
        "audited": sum(1 for r in rows if r.get("audited")),
        "missing_translation": sum(1 for r in rows if not r.get("summary_en")),
        "generated_at": scored[-1] if scored else IMPORT_DATE,
    }


def _top_categories(st, limit=8):
    return st["categories"][:limit]


def stats_block(st, lang):
    english = lang == "en"
    lines = []
    lines.append("| %s | %s |" % (("Number", "Value") if english else ("Sayı", "Değer")))
    lines.append("|---|---|")
    label = "Repositories" if english else "Repo"
    lines.append("| %s | %d |" % (label, st["total"]))
    lines.append("| %s | yes %d · no %d · unclear %d |" % (
        "Calls Jev" if english else "Jev çağırıyor",
        st["calls_jev"]["yes"], st["calls_jev"]["no"], st["calls_jev"]["unclear"]))
    lines.append("| %s | A %d · B %d · C %d |" % (
        "Classes" if english else "Sınıflar",
        st["classes"]["A"], st["classes"]["B"], st["classes"]["C"]))
    lines.append("| %s | %d |" % ("Audited" if english else "Denetlenmiş", st["audited"]))
    lines.append("| %s | %d |" % ("Sources" if english else "Kaynak", st["sources"]))
    # a count of zero is not news: the row only appears when there is work left
    if st["missing_translation"]:
        lines.append("| %s | %d |" % (
            "Rows still untranslated" if english else "Çevirisi eksik satır",
            st["missing_translation"]))
    lines.append("| %s | %s |" % ("Data as of" if english else "Veri tarihi",
                                  st["generated_at"]))
    lines.append("")
    lines.append("**%s**" % ("Top categories" if english else "En çok kategori"))
    lines.append("")
    for slug, count in _top_categories(st):
        title = CATEGORY_TITLES[slug][0 if english else 1]
        page = ("categories/%s.md" if english else "categories/%s.md") % slug
        lines.append("- [%s](%s) — %d" % (title, page, count))
    return "\n".join(lines)


def fill_stats(text, block):
    """Replace what is between the STATS markers. Returns (text, changed, found)."""
    start = text.find(STATS_START)
    end = text.find(STATS_END)
    if start == -1 or end == -1 or end < start:
        return text, False, False
    new = (text[:start] + STATS_START + "\n" + block + "\n" + text[end:])
    return new, new != text, True


# --------------------------------------------------------------------------
# rendering

def _header(page, lang):
    """Banner plus the language switch, with links relative to the page."""
    if lang == "en":
        depth = page.count("/")
        other = "../" * depth + "tr/" + page
        line = "English | [Türkçe](%s)" % other
    else:
        rest = page
        depth = rest.count("/") + 1
        other = "../" * depth + rest
        line = "[English](%s) | Türkçe" % other
    return BANNER + "\n" + line


def _esc(text):
    """Turn somebody else's prose into plain text on our page.

    Everything that markdown or a browser would act on is escaped, never
    deleted: HTML goes to entities, the link and image syntax loses its
    brackets, a pipe or a newline can no longer break the table. Backticks
    survive, because inline code is the one bit of markup that cannot carry a
    link, a script or a tracking pixel.
    """
    out = []
    for ch in (text or ""):
        if ch == "&":
            out.append("&amp;")
        elif ch == "<":
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        elif ch == "\\":
            out.append("\\\\")
        elif ch in "[]()|":
            out.append("\\" + ch)
        elif ord(ch) < 0x20 or ord(ch) == 0x7F:
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out).strip()


def _url(value):
    """Percent-encode a url for a markdown link target."""
    return urllib.parse.quote(str(value or ""), safe="/:?#[]@!$&'*+,;=-._~%")


def _link(label, url):
    """A markdown link whose label is inert and whose target is encoded."""
    return "[%s](%s)" % (_esc(label), _url(url))


def _row(rec, lang):
    summary = rec["summary_en"] if lang == "en" else rec["summary_tr"]
    if not summary:
        summary = rec["summary_tr"] if lang == "en" else rec["summary_en"]
    evidence = "evidence" if lang == "en" else "kanıt"
    cells = [
        _link(rec["repo"], rec["url"]),
        rec["class"],
        str(rec["total"]),
        rec["calls_jev"],
        _esc(summary),
        _link(evidence, rec["evidence_url"]),
    ]
    if rec.get("duplicate_of"):
        marker = "duplicate of " + _link(
            rec["duplicate_of"], "https://github.com/" + rec["duplicate_of"])
        cells[4] = (marker + " — " + cells[4]).strip(" —")
    return "| " + " | ".join(cells) + " |"


def _table_head(lang):
    if lang == "en":
        head = ["Repository", "Class", "Total", "Calls Jev", "What it does", "Evidence"]
    else:
        head = ["Repo", "Sınıf", "Toplam", "Jev çağırıyor", "Ne yapıyor", "Kanıt"]
    return "| " + " | ".join(head) + " |\n|" + "---|" * len(head)


def _sort_key(rec):
    return (CLASSES.index(rec["class"]), -rec["total"], rec["repo"].lower())


def render_repos(records, st, lang):
    english = lang == "en"
    out = [_header("REPOS.md", lang), ""]
    out.append("# %s" % ("All repositories" if english else "Bütün repolar"))
    out.append("")
    out.append(("%d scored repositories, %d marked as duplicates. Data as of %s. "
                "Every row links to the repository and to the page the score rests on."
                if english else
                "%d puanlanmış repo, %d mükerrer. Veri tarihi %s. "
                "Her satır repoya ve puanın dayandığı sayfaya bağlanır.")
               % (st["total"], st["duplicates"], st["generated_at"]))
    out.append("")
    out.append("## %s" % ("Summary" if english else "Özet"))
    out.append("")
    out.append(stats_block(st, lang))
    out.append("")
    out.append("## %s" % ("Categories" if english else "Kategoriler"))
    out.append("")
    out.append("| %s | %s | %s |" % (
        ("Category", "Repositories", "Class A") if english
        else ("Kategori", "Repo", "A sınıfı")))
    out.append("|---|---|---|")
    rows = counted(records)
    for slug, count in sorted(st["categories"], key=lambda item: (-item[1], item[0])):
        a_count = sum(1 for r in rows if r["category"] == slug and r["class"] == "A")
        title = CATEGORY_TITLES[slug][0 if english else 1]
        out.append("| [%s](categories/%s.md) | %d | %d |" % (title, slug, count, a_count))
    out.append("")
    out.append("## %s" % ("Every repository" if english else "Bütün kayıtlar"))
    out.append("")
    out.append(_table_head(lang))
    for rec in sorted(records, key=_sort_key):
        out.append(_row(rec, lang))
    out.append("")
    return "\n".join(out)


def _pick(rec, field, english):
    """The field in the reader's language, falling back to the other one."""
    value = rec.get(field + ("_en" if english else "_tr")) or ""
    return value or rec.get(field + ("_tr" if english else "_en")) or ""


#: Short form of the five axes, in rubric order: D3 R3 N2 M2 E3.
SCORE_LETTERS = [("depth", "D"), ("relevance", "R"), ("novelty", "N"),
                 ("maturity", "M"), ("evidence", "E")]

#: The measured core starts here. Class A alone is a wide door (see the page's
#: own explanation), so the rows that also carry a high total are kept apart.
CORE_MIN_TOTAL = 13


def _scores_short(rec):
    scores = rec.get("scores") or {}
    return " ".join("%s%s" % (letter, scores.get(name, 0))
                    for name, letter in SCORE_LETTERS)


def _top_row(rec, lang):
    english = lang == "en"
    parts = [_link(rec["repo"], rec["url"]), "%d/15" % rec["total"],
             _scores_short(rec)]
    for field in ("summary", "takeaway"):
        text = _esc(_pick(rec, field, english))
        if text:
            parts.append(text)
    # the audit note is bilingual: each page shows the note in its own language
    note = _esc(rec.get("audit_note_en" if english else "audit_note_tr") or "")
    if note:
        parts.append(note)
    parts.append(_link("evidence" if english else "kanıt", rec["evidence_url"]))
    return " — ".join(parts)


def _core_sort_key(rec):
    return (-rec["total"], rec["repo"].lower())


def render_top(records, st, lang):
    english = lang == "en"
    picked = [r for r in counted(records) if r["class"] == "A" and r.get("audited")]
    core = sorted([r for r in picked if r["total"] >= CORE_MIN_TOTAL],
                  key=_core_sort_key)
    rest = [r for r in picked if r["total"] < CORE_MIN_TOTAL]

    out = [_header("TOP.md", lang), ""]
    out.append("# %s" % ("Top of the list" if english else "Listenin başı"))
    out.append("")
    out.append(("Class A repositories that a second pass over the rubric confirmed. "
                "Unaudited rows are not here, however high they scored."
                if english else
                "Ölçeğin ikinci bir gözle uygulanmasından geçmiş A sınıfı repolar. "
                "Denetlenmemiş satırlar puanı ne olursa olsun buraya girmez."))
    out.append("")
    out.append((
        "There are two doors into class A: a total of 11 or more, or "
        "relevance 3 together with novelty 2 or more. The second door is a "
        "wide one — it lets in a repository whose idea transfers even when "
        "little else about it does — so the rows that also carry a high total "
        "are kept in a section of their own."
        if english else
        "A sınıfına iki kapıdan girilir: toplam 11 ve üzeri, ya da relevance 3 "
        "ile novelty 2 ve üzeri. İkinci kapı geniştir — fikri bize geçen ama "
        "başka yanı geçmeyen repo da oradan girer — bu yüzden yüksek toplamı "
        "da olan satırlar ayrı bir bölümde tutulur."))
    out.append("")

    out.append("## %s" % ("Measured core" if english
                          else "Ölçümle desteklenen çekirdek"))
    out.append("")
    out.append(("Audited class A with a total of %d or more, highest first."
                if english else
                "Denetlenmiş, toplamı %d ve üzeri A sınıfı; en yüksekten başlar.")
               % CORE_MIN_TOTAL)
    out.append("")
    if core:
        for rec in core:
            out.append("- " + _top_row(rec, lang))
    else:
        out.append("_%s_" % ("Nothing has cleared that bar yet." if english
                             else "Henüz bu çıtayı aşan satır yok."))
    out.append("")

    out.append("## %s" % ("Other class A" if english else "Diğer A sınıfı"))
    out.append("")
    out.append(("The rest of the audited class A rows, by category."
                if english else
                "Denetlenmiş diğer A sınıfı satırlar, kategoriye göre."))
    out.append("")
    if not rest:
        out.append("_%s_" % ("Every audited class A row is in the core."
                             if english else
                             "Denetlenmiş bütün A sınıfı satırlar çekirdekte."))
        out.append("")
        return "\n".join(out)
    by_category = collections.defaultdict(list)
    for rec in rest:
        by_category[rec["category"]].append(rec)
    for slug in sorted(by_category):
        out.append("### %s" % CATEGORY_TITLES[slug][0 if english else 1])
        out.append("")
        for rec in sorted(by_category[slug], key=_core_sort_key):
            out.append("- " + _top_row(rec, lang))
        out.append("")
    return "\n".join(out)


def render_category(slug, records, lang):
    english = lang == "en"
    title = CATEGORY_TITLES[slug][0 if english else 1]
    page = "categories/%s.md" % slug
    rows = [r for r in records if r["category"] == slug]
    out = [_header(page, lang), ""]
    out.append("# %s" % title)
    out.append("")
    out.append(("%d repositories in this category, sorted by class then score."
                if english else
                "Bu kategoride %d repo; önce sınıf, sonra puan sırasıyla.")
               % len([r for r in rows if not r.get("duplicate_of")]))
    out.append("")
    out.append("[%s](%s)" % ("All repositories" if english else "Bütün repolar",
                             "../REPOS.md"))
    out.append("")
    out.append(_table_head(lang))
    for rec in sorted(rows, key=_sort_key):
        out.append(_row(rec, lang))
    out.append("")
    return "\n".join(out)


def render_sources(sources, lang):
    english = lang == "en"
    out = [_header("SOURCES.md", lang), ""]
    out.append("# %s" % ("Sources" if english else "Kaynaklar"))
    out.append("")
    out.append(("Everything this repository claims rests on one of these. "
                "Every row carries a link; a row without one does not get written."
                if english else
                "Bu depodaki her iddia bunlardan birine dayanır. "
                "Her satır bir bağlantı taşır; bağlantısız satır yazılmaz."))
    out.append("")
    by_type = collections.defaultdict(list)
    for src in sources:
        by_type[src.get("type")].append(src)
    for stype in SOURCE_TYPES:
        group = by_type.get(stype)
        if not group:
            continue
        out.append("## %s" % SOURCE_TYPE_TITLES[stype][0 if english else 1])
        out.append("")
        head = (["Source", "Author", "Date", "Trust", "Status", "Note"] if english
                else ["Kaynak", "Yazar", "Tarih", "Güven", "Durum", "Not"])
        out.append("| " + " | ".join(head) + " |")
        out.append("|" + "---|" * len(head))
        for src in sorted(group, key=lambda s: (-int(s.get("trust") or 0),
                                                str(s.get("id")))):
            note = src.get("note_en") if english else src.get("note_tr")
            out.append("| %s | %s | %s | %s | %s | %s |" % (
                _link(src.get("title") or src.get("id"), src.get("url")),
                _esc(src.get("author")), _esc(src.get("date")),
                src.get("trust"), _esc(src.get("status")), _esc(note)))
        out.append("")
    return "\n".join(out)


def render_all(records, sources):
    st = stats(records, sources)
    pages = {}
    for lang in ("en", "tr"):
        prefix = "" if lang == "en" else "tr/"
        pages[prefix + "SOURCES.md"] = render_sources(sources, lang)
        pages[prefix + "REPOS.md"] = render_repos(records, st, lang)
        pages[prefix + "TOP.md"] = render_top(records, st, lang)
        for slug in sorted({r["category"] for r in records}):
            pages[prefix + "categories/%s.md" % slug] = render_category(
                slug, records, lang)
    return pages


# --------------------------------------------------------------------------
# command line

def load_data(root):
    repos, repo_errors = read_jsonl(os.path.join(root, "data", "repos.jsonl"))
    sources, source_errors = read_jsonl(os.path.join(root, "data", "sources.jsonl"))
    return repos, sources, repo_errors + source_errors


#: Exactly the fields a row of data/repos.jsonl has. An incoming row is a
#: complete row in English field names - no more, no less.
RECORD_FIELDS = frozenset([
    "repo", "url", "source_set", "first_seen", "scored_at", "rubric_version",
    "meta", "category", "calls_jev", "question_types", "scores", "total",
    "class", "summary_en", "summary_tr", "takeaway_en", "takeaway_tr",
    "risk_en", "risk_tr", "evidence_url", "audited", "audit_note_en",
    "audit_note_tr", "duplicate_of", "status",
])

#: What an incoming row may not take away from a repository we already know:
#: the day we first saw it, and the auditor's work. ``audited`` is not in the
#: list because it is not kept either - a new score is an unaudited score.
PRESERVED_ON_MERGE = ("first_seen", "audit_note_en", "audit_note_tr",
                      "duplicate_of")

#: What a scorer cannot award itself. The auditor's pass is the only thing that
#: puts a row in TOP, so a batch that arrives claiming ``audited: true`` with an
#: audit note attached would walk straight past the second pass. On a new row
#: these are reset whatever the batch says; on a known row the auditor's own
#: earlier marks are restored from the existing record instead.
UNEARNED_ON_MERGE = {"audited": False, "audit_note_en": "", "audit_note_tr": "",
                     "duplicate_of": None}


def _incoming_row_problems(label, row):
    missing = sorted(RECORD_FIELDS - set(row))
    extra = sorted(set(row) - RECORD_FIELDS)
    problems = []
    if missing:
        problems.append("%s: eksik alan: %s" % (label, ", ".join(missing)))
    if extra:
        problems.append("%s: şemada olmayan alan: %s" % (label, ", ".join(extra)))
    if problems:
        return problems
    errors, _warnings = validate([row], [])
    return ["%s: %s" % (label, error) for error in errors]


#: Where the record of applied batches lives. Not ``data/incoming/applied/``:
#: that directory is git-ignored, so it is not a record anybody else can see.
LEDGER_PATH = ("data", "applied-batches.jsonl")
DATA_PATH = ("data", "repos.jsonl")

SHA256_RE = re.compile(r"\A[0-9a-f]{64}\Z")


def read_ledger(root):
    """Return (entries, problems) from ``data/applied-batches.jsonl``.

    One line per batch that has been folded into the data: its file name, the
    sha256 of its content and ``applied_at``, the newest ``scored_at`` in the
    batch. The date comes from the batch and not from the clock, so two
    machines applying the same batch write the same line.
    """
    path = os.path.join(root, *LEDGER_PATH)
    entries, fatal = read_jsonl_strict(path)
    problems = ["data/" + line for line in fatal]
    for number, entry in enumerate(entries, 1):
        where = "data/applied-batches.jsonl:%d" % number
        if sorted(entry) != ["applied_at", "name", "sha256"]:
            problems.append("%s: alanlar name, sha256, applied_at değil (%r)"
                            % (where, sorted(entry)))
            continue
        if not isinstance(entry["name"], str) or not entry["name"]:
            problems.append("%s: name metin değil (%r)" % (where, entry["name"]))
        if not (isinstance(entry["sha256"], str)
                and SHA256_RE.match(entry["sha256"])):
            problems.append("%s: sha256 64 onaltılık karakter değil (%r)"
                            % (where, entry["sha256"]))
        if entry["applied_at"] is not None and not is_date(entry["applied_at"]):
            problems.append("%s: applied_at tarih değil (%r)"
                            % (where, entry["applied_at"]))
    return entries, problems


def half_written_problems(root):
    """What a run that died between the two renames left behind.

    ``data/repos.jsonl`` and the ledger are replaced one after the other. If
    the machine stops in between, the tree says two different things about
    the same batch, and only a person can decide what happened - so the build
    stops and says which file to move where instead of guessing.
    """
    data_tmp = os.path.join(root, *DATA_PATH) + ".tmp"
    ledger_tmp = os.path.join(root, *LEDGER_PATH) + ".tmp"
    data_left, ledger_left = os.path.exists(data_tmp), os.path.exists(ledger_tmp)
    if data_left and ledger_left:
        return ["data/repos.jsonl.tmp ve data/applied-batches.jsonl.tmp yarım "
                "kalmış bir yazımdan artakaldı: hiçbir batch uygulanmadı. İki "
                ".tmp dosyasını silin, sonra yeniden çalıştırın."]
    if ledger_left:
        return ["data/applied-batches.jsonl.tmp duruyor: data/repos.jsonl "
                "yenilendi ama uygulanan batch kaydı yazılamadı. "
                "data/applied-batches.jsonl.tmp dosyasını "
                "data/applied-batches.jsonl üzerine taşıyın (yoksa aynı "
                "batch'ler bir kez daha uygulanır), sonra yeniden çalıştırın."]
    if data_left:
        return ["data/repos.jsonl.tmp yarım kalmış bir yazımdan artakaldı; "
                "veri dosyası olduğu gibi duruyor. Dosyayı silin, sonra "
                "yeniden çalıştırın."]
    return []


def write_data_and_ledger(root, records, ledger):
    """Replace ``data/repos.jsonl`` and the ledger in one step.

    Both temporary files are on the disk before either rename happens, so the
    only window left is between the two renames - and
    :func:`half_written_problems` catches that on the next run.
    """
    data_path = os.path.join(root, *DATA_PATH)
    ledger_path = os.path.join(root, *LEDGER_PATH)
    data_tmp = write_tmp(data_path, dump_jsonl(records))
    ledger_tmp = write_tmp(ledger_path, dump_jsonl(ledger))
    os.replace(data_tmp, data_path)
    os.replace(ledger_tmp, ledger_path)


def merge_incoming(root, records):
    """Fold ``data/incoming/*.jsonl`` into *records*, in place.

    An incoming line is a complete repository row written in English field
    names. A repository we do not know is added with the auditor's fields
    cleared, so a batch cannot declare its own row audited; one we do know
    keeps its ``first_seen``, its audit note and its ``duplicate_of`` and loses
    everything else to the new score - including ``audited``, because the new
    numbers have not been through a second pass.

    Nothing is applied unless every line of every file is sound: a half-good
    batch would leave the data file in a state no file on disk describes.

    A batch whose name and sha256 are already in ``data/applied-batches.jsonl``
    has been applied once and is not applied again - only its filing away is
    retried. The same name with different content is a different batch.
    Returns (problems, summary).
    """
    summary = {"files": [], "added": 0, "updated": 0, "rows": 0,
               "entries": [], "ledger": [], "skipped": [], "stale": []}
    problems = []
    ledger, ledger_problems = read_ledger(root)
    problems.extend(ledger_problems)
    summary["ledger"] = list(ledger)
    applied_before = {(entry.get("name"), entry.get("sha256"))
                      for entry in ledger}
    files = sorted(glob.glob(os.path.join(root, "data", "incoming", "*.jsonl")))
    batches = []
    for path in files:
        name = os.path.basename(path)
        digest = sha256_of(path)
        if (name, digest) in applied_before:
            # Already in the data. Re-reading it would be re-applying it, and
            # a batch that lost the race to a newer one would undo it.
            summary["skipped"].append(name)
            summary["files"].append(path)
            continue
        rows, fatal = read_jsonl_strict(path)
        problems.extend("data/incoming/" + line for line in fatal)
        for number, row in enumerate(rows, 1):
            problems.extend(_incoming_row_problems(
                "data/incoming/%s:%d" % (name, number), row))
        batches.append((path, name, digest, rows))
    if problems:
        return problems, summary

    index = {}
    for rec in records:
        index[str(rec.get("repo") or "").lower()] = rec
    for path, name, digest, rows in batches:
        for row in rows:
            key = row["repo"].lower()
            old = index.get(key)
            if old is not None and is_date(old.get("scored_at")) \
                    and row["scored_at"] < old["scored_at"]:
                # Dates are YYYY-MM-DD, so this comparison is the calendar's.
                summary["stale"].append(
                    "data/incoming/%s: %s atlandı - satırın scored_at değeri "
                    "%s, veride %s tarihli daha yeni bir puan var"
                    % (name, row["repo"], row["scored_at"], old["scored_at"]))
                continue
            if old is None:
                new = dict(row)
                new["first_seen"] = row["scored_at"]
                new.update(UNEARNED_ON_MERGE)
                records.append(new)
                index[key] = new
                summary["added"] += 1
            else:
                new = dict(row)
                for field in PRESERVED_ON_MERGE:
                    new[field] = old[field]
                new["audited"] = False
                old.clear()
                old.update(new)
                summary["updated"] += 1
            summary["rows"] += 1
        summary["files"].append(path)
        entry = {"name": name, "sha256": digest,
                 "applied_at": max(row["scored_at"] for row in rows) if rows
                 else None}
        summary["entries"].append(entry)
        summary["ledger"].append(entry)
    records.sort(key=lambda r: str(r.get("repo") or "").lower())
    return problems, summary


def applied_name(target, name):
    """A free name for *name* under *target*: ``x.jsonl``, ``x-2.jsonl``, ...

    A batch file name gets reused - an agent writes ``batch-1.jsonl`` again
    next week. Overwriting the archived one destroys the record of what was
    applied and when. The suffix carries no timestamp on purpose: given the
    same archive, every machine picks the same name.
    """
    candidate = os.path.join(target, name)
    if not os.path.exists(candidate):
        return candidate
    stem, ext = os.path.splitext(name)
    number = 2
    while True:
        candidate = os.path.join(target, "%s-%d%s" % (stem, number, ext))
        if not os.path.exists(candidate):
            return candidate
        number += 1


def file_applied(root, summary):
    """Move every merged batch under ``data/incoming/applied/``.

    Returns the batches that could not be moved. Such a batch is already in
    the data and already in ``data/applied-batches.jsonl``, so the message
    says exactly that: the next run will not apply its rows a second time -
    it will only try to file it away again.
    """
    target = os.path.join(root, "data", "incoming", "applied")
    os.makedirs(target, exist_ok=True)
    stranded = []
    for path in summary["files"]:
        name = os.path.basename(path)
        try:
            destination = applied_name(target, name)
            os.replace(path, destination)
        except OSError as error:
            stranded.append(
                "data/incoming/%s: veriye uygulandı ama arşivlenemedi (%s) - "
                "dosya yerinde duruyor; data/applied-batches.jsonl kaydı "
                "sayesinde satırları yeniden uygulanmaz, sonraki çalıştırma "
                "yalnız arşivlemeyi yeniden dener" % (name, error))
            continue
        print("UYGULANDI: data/incoming/%s -> data/incoming/applied/%s"
              % (name, os.path.basename(destination)))
    return stranded


def main(argv=None, root=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--import-legacy", action="store_true",
                        help="rebuild data/repos.jsonl from repo-analizi/")
    parser.add_argument("--strict", action="store_true",
                        help="missing translations and warnings become failures")
    parser.add_argument("--check", action="store_true",
                        help="write nothing; exit 1 if a page is out of date")
    parser.add_argument("--root", default=None,
                        help="build this tree instead of the one around the script")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if root is None:
        root = args.root or os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

    half_written = half_written_problems(root)
    if half_written:
        for line in half_written:
            print("HATA: " + line)
        return 1

    problems = []
    if args.import_legacy:
        records, report = import_legacy(root)
        for line in report["skipped_detail"]:
            print("ATLANDI: " + line)
        for line in report["warnings"][:40]:
            print("UYARI: " + line)
        if len(report["warnings"]) > 40:
            print("UYARI: ... %d uyarı daha" % (len(report["warnings"]) - 40))
        print("İçe aktarıldı: %d satır, %d atlandı, %d denetlenmiş, %d denetim notu, "
              "%d donanım cezası geri alındı, %d nötrleştirilmiş, "
              "%d üstverisi eksik, %d çevirisi eksik"
              % (len(records), report["skipped"], report["audited"],
                 report["audit_notes"], report["hardware_reverted"],
                 report["neutralised"], report["meta_missing"],
                 report["missing_translation"]))
        problems.extend(report["fatal"])
        if problems:
            for line in problems[:40]:
                print("HATA: " + line)
            return 1
        if not args.check:
            write_text_atomic(os.path.join(root, "data", "repos.jsonl"),
                              dump_jsonl(records))
        if args.strict and report["missing_translation"]:
            problems.append("%d satırın İngilizce çevirisi yok (--strict)"
                            % report["missing_translation"])
        sources, _errors = read_jsonl(os.path.join(root, "data", "sources.jsonl"))
        incoming = {"files": [], "added": 0, "updated": 0, "rows": 0,
                    "entries": [], "ledger": [], "skipped": [], "stale": []}
    else:
        records, sources, read_errors = load_data(root)
        problems.extend(read_errors)
        incoming_problems, incoming = merge_incoming(root, records)
        problems.extend(incoming_problems)
        for line in incoming["stale"]:
            print("ATLANDI: " + line)
        for name in incoming["skipped"]:
            print("ZATEN UYGULANMIŞ: data/incoming/%s (data/applied-batches.jsonl) "
                  "- yalnız arşivlenecek" % name)
        if incoming["rows"]:
            print("data/incoming: %d satır (%d yeni, %d güncellendi), %d dosya"
                  % (incoming["rows"], incoming["added"], incoming["updated"],
                     len(incoming["files"])))

    errors, warnings = validate(records, sources, strict=args.strict)
    problems.extend(errors)
    for line in warnings[:40]:
        print("UYARI: " + line)
    if len(warnings) > 40:
        print("UYARI: ... %d uyarı daha" % (len(warnings) - 40))
    if args.strict and warnings:
        problems.append("%d uyarı (--strict)" % len(warnings))

    pages = render_all(records, sources)
    problems.extend(check_language_parity(pages))
    problems.extend(scan_privacy(root, records, pages))

    if problems:
        for line in problems[:40]:
            print("HATA: " + line)
        if len(problems) > 40:
            print("HATA: ... %d hata daha" % (len(problems) - 40))
        return 1

    # The merge only lands once everything else has agreed. Order matters: the
    # data file and the record of which batches produced it are replaced
    # first, and only then are the batches filed away. A batch that survives
    # its own archiving is no loss - it is in the ledger, so the next run
    # leaves the data alone and only retries the move.
    stranded = []
    if not args.check:
        if incoming["entries"]:
            try:
                write_data_and_ledger(root, records, incoming["ledger"])
            except OSError as error:
                print("HATA: veri ve batch kaydı yazılamadı (%s)" % error)
                return 1
        if incoming["files"]:
            stranded = file_applied(root, incoming)

    st = stats(records, sources)
    stale = []

    # The set on disk must be exactly the set the data asks for - no page left
    # over from a category that no longer exists, and no byte of difference.
    on_disk = discover_generated(root)
    extra = sorted(on_disk - set(pages))
    if args.check:
        for name in extra:
            stale.append(name + " (fazla: veri bu sayfayı istemiyor)")
        for problem in check_language_parity(on_disk):
            stale.append("diskte dil eşleşmesi bozuk: " + problem)

    for name, text in sorted(pages.items()):
        path = os.path.join(root, *name.split("/"))
        if args.check:
            if read_bytes(path) != text.encode("utf-8"):
                stale.append(name)
        else:
            write_text(path, text)

    if not args.check:
        for name in extra:
            os.remove(os.path.join(root, *name.split("/")))
            print("SİLİNDİ (eskimiş üretilmiş sayfa): " + name)
        left = check_language_parity(discover_generated(root))
        if left:
            for problem in left:
                print("HATA: diskte dil eşleşmesi bozuk: " + problem)
            return 1

    for readme, lang in (("README.md", "en"), (os.path.join("tr", "README.md"), "tr")):
        path = os.path.join(root, readme)
        current = read_text(path)
        if current is None:
            continue
        new, changed, found = fill_stats(current, stats_block(st, lang))
        if not found:
            print("UYARI: %s içinde STATS işareti yok - dokunulmadı" % readme)
            continue
        if args.check:
            if changed:
                stale.append(readme)
        elif changed:
            write_text(path, new)

    if args.check and stale:
        for name in stale:
            print("GÜNCEL DEĞİL: " + name)
        return 1

    # Reported last, after the data and the pages are both on disk: the tree is
    # consistent, only the archive is behind.
    if stranded:
        for line in stranded:
            print("HATA: " + line)
        return 1

    print("%d sayfa, %d repo, %d kaynak (veri tarihi %s)"
          % (len(pages), st["total"], st["sources"], st["generated_at"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
