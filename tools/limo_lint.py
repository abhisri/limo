#!/usr/bin/env python3
"""
limo_lint.py — LIMO v2.5 tooling. Standard library only. Python 3.8+.

  python3 tools/limo_lint.py lint      [Domain ...] [--full]     freshness, integrity, cross-refs, line tags, stalls (exit 1 on findings)
  python3 tools/limo_lint.py bootpack  [Domain ...]              write core/BOOT_PACK.md  (Part A ≤ 60 lines + signpost index)
  python3 tools/limo_lint.py triggers  "<request text>" Domain   print every NEVER_AGAIN / INVARIANT whose Triggers match the request
  python3 tools/limo_lint.py ready     Domain [--agent NAME]     OPEN_ITEMS rows with no open blockers, unclaimed or claimed by you
  python3 tools/limo_lint.py reflect   Domain                    propose merges / archives / moves -> core/_pending/reflect_<date>.md
  python3 tools/limo_lint.py deadends                            write shared/DEAD_END_INDEX.md
  python3 tools/limo_lint.py agentsmd  [Domain ...]              write {Domain}/limo-populated/AGENTS.md from BOOT_PACK Part A
  python3 tools/limo_lint.py commit    Domain --agent NAME --trigger "what fired"   git-commit core/ only, with stale-lock recovery
  python3 tools/limo_lint.py git-init  Domain                    create {Domain}/limo-populated/ repo if the core is not inside one
  python3 tools/limo_lint.py infra     [--probe]                 [Infra] tier: diary migration state, doc drift vs SERVICE_CATALOG, optional reachability
  python3 tools/limo_lint.py all       [Domain ...]              lint + bootpack + trigger index + deadends + agentsmd

Run from the workspace root (the folder that contains */limo-populated/core/), or pass --root.
Spec: LIMO/LIMO_FRAMEWORK.md v2.5 — Tooling, Memory Line Conventions, Git as Write-Ahead Log.

Writes ONLY generated files (BOOT_PACK.md, TRIGGER_INDEX.md, DEAD_END_INDEX.md, AGENTS.md under limo-populated/,
_pending/reflect_*.md) and git commits of core/. It never edits a core file.
"""
import argparse
import datetime as dt
import difflib
import fnmatch
import os
import re
import subprocess
import sys
import time

TODAY = dt.date.today()
CORE = os.path.join("limo-populated", "core")
PART_A_BUDGET = 60

FRESHNESS = {
    "STATUS_SNAPSHOT.md": 7, "OPEN_ITEMS.md": 7, "GOALS.md": 14, "_SESSION_PROMPT.md": 14,
    "INVARIANTS.md": 30, "FOLDER_MAP.md": 30, "KEY_PEOPLE.md": 30, "START_HERE.md": 30,
    "AI_AGENTS_READ_THIS_FIRST.md": 30, "LEARNINGS.md": 60, "ARCHITECTURE.md": 90, "DECISIONS.md": 90,
    "OWNERS.md": 90, "SESSION_DIARY.md": 180, "CHECKPOINTS.md": 180, "NEVER_AGAIN.md": 180,
    "MEMORY_COMPRESSION_PROTOCOL.md": 180,
}
SOURCE_TAGGED = ("STATUS_SNAPSHOT.md", "_SESSION_PROMPT.md", "GOALS.md", "KEY_PEOPLE.md")
COLLECTION_FILES = ("DECISIONS.md", "LEARNINGS.md", "NEVER_AGAIN.md", "INVARIANTS.md")
DIARY_LINE_THRESHOLD = 150
STALL_DAYS = 7
OPINION_STALE_DAYS = 90
CLASSES = {"fabrication", "scope-drift", "tooling", "data-quality", "judgment", "other"}
LINE_CLASSES = {"fact", "opinion", "preference", "episode", "rule"}
GENERATED = ("BOOT_PACK.md", "TRIGGER_INDEX.md")

DONE_WORDS = re.compile(r"\b(DONE|CLOSED|COMPLETE|COMPLETED|RESOLVED|DECIDED|SETTLED|SUPERSEDED|CANCELLED|DEFERRED|ARCHIVED|DROPPED)\b|✅", re.I)
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
LAST_UPDATED_RE = re.compile(r"last\s+updated[^0-9\n]{0,12}(\d{4}-\d{2}-\d{2})", re.I)
MODIFIED_RE = re.compile(r"(?im)^modified:\s*(\d{4}-\d{2}-\d{2})")
DESCRIPTION_RE = re.compile(r"(?im)^description:\s*(.+)$")
NUMBER_RE = re.compile(
    r"($\s?[\d,]+(?:\.\d+)?(?:\s?(?:lakh|lakhs|crore|cr|k|L))?"
    r"|\$\s?[\d,]+(?:\.\d+)?"
    r"|\b\d+(?:\.\d+)?\s?(?:%|U/L|mg/dL|mg/dl|mmol/L|kg|lbs?|sqft|sq\.? ?ft|km|cm|mm|GB|TB|MB)\b"
    r"|\b\d{1,3}(?:,\d{2,3}){1,}\b)"
)
SRC_RE = re.compile(r"\[src:\s*[^\]]+\]")
REF_RE = re.compile(r"`([A-Za-z0-9_./\[\]\- ]+\.md)`")
TAIL_RE = re.compile(r"<!--\s*checkpoint-tail:\s*(.*?)\s*-->", re.S)
TAG_RE = re.compile(r"\{(valid|supersedes|class|confidence|triggers|blocked_by|claimed|started|observed_by):\s*([^}]*)\}")
TRIGGERS_FIELD_RE = re.compile(r"(?im)^[-*\s]*\*{0,2}Triggers:\*{0,2}\s*(.+)$")
ENTRY_RE = re.compile(r"(?m)^(#{2,4})\s*\**((?:D|NA|INV|L|CP|OI)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\**\s*[—:–-]\s*(.*)$")
ID_RE = re.compile(r"\b(?:D|NA|INV|L|CP|OI)-(?=[A-Z0-9-]*\d)[A-Z0-9]+(?:-[A-Z0-9]+){0,3}\b")
DEF_RE = re.compile(r"(?m)^\s*(?:[-*]\s*|\|\s*|#{1,4}\s*)~{0,2}\**((?:D|NA|INV|L|CP|OI)-(?=[A-Z0-9-]*\d)[A-Z0-9]+(?:-[A-Z0-9]+){0,3})\b")


# ----------------------------------------------------------------------------- helpers
def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().replace("\r\n", "\n")
    except OSError:
        return None


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")


def domains(root, only=None):
    out = []
    for name in sorted(os.listdir(root)):
        core = os.path.join(root, name, CORE)
        if os.path.isdir(core) and not name.startswith((".", "_")):
            if only and name not in only:
                continue
            out.append((name, core))
    return out


def freshness_days(fname):
    if fname in FRESHNESS:
        return FRESHNESS[fname]
    for k, v in FRESHNESS.items():
        if k.startswith("_") and fname.endswith(k):
            return v
    return None


def last_updated(text, path):
    """(date, source): frontmatter modified: > Last updated header > file mtime."""
    m = MODIFIED_RE.search(text[:1500])
    if m:
        try:
            return dt.date.fromisoformat(m.group(1)), "modified:"
        except ValueError:
            pass
    m = LAST_UPDATED_RE.search(text[:4000])
    if m:
        try:
            return dt.date.fromisoformat(m.group(1)), "header"
        except ValueError:
            pass
    return dt.date.fromtimestamp(os.path.getmtime(path)), "mtime"


def description_of(text, fname):
    m = DESCRIPTION_RE.search(text[:1500])
    if m:
        return m.group(1).strip()
    # fall back to the first non-heading, non-metadata prose line
    for line in text.split("\n")[:25]:
        s = line.strip()
        if s and not s.startswith(("#", "|", "-", "*", "<!--", "```", "Last updated", "Freshness", "---")) and len(s) > 20:
            return (s[:110] + "…") if len(s) > 110 else s
    return "(no description: line — add one to the frontmatter)"


def parse_tags(text):
    return {k: v.strip() for k, v in TAG_RE.findall(text)}


def parse_valid(v):
    """'2026-03-19..' -> (start, None); '2026-03-19..2026-06-01' -> (start, end); '..2026-06-01' -> (None, end)."""
    if not v:
        return None, None
    a, _, b = v.partition("..")
    def d(s):
        m = DATE_RE.search(s or "")
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None
    return d(a), d(b)


def entries(text):
    """Split a collection file into (id, title, body, level) entries."""
    out = []
    ms = list(ENTRY_RE.finditer(text))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out.append({"id": m.group(2).rstrip("-"), "title": m.group(3).strip(), "body": text[m.end():end], "level": len(m.group(1))})
    return out


def section(text, header_regex, until=r"\n## "):
    m = re.search(header_regex, text)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(until, rest)
    return rest[: n.start()] if n else rest


def oi_rows(oi_text):
    """Active OPEN_ITEMS rows -> dicts with id, cols, tags, done flag."""
    rows, in_active = [], False
    for line in oi_text.split("\n"):
        if line.startswith("## "):
            in_active = "active" in line.lower()
        if not in_active:
            continue
        m = re.match(r"^\s*(?:[-*]\s*|\|\s*)(~~)?\**(OI-[A-Za-z0-9-]+)", line)
        if not m:
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append({"id": m.group(2).rstrip("-"), "cols": cols, "line": line, "tags": parse_tags(line),
                     "done": bool(m.group(1)) or bool(DONE_WORDS.search(" ".join(cols[1:4])))})
    return rows


class Finding:
    def __init__(self, domain, sev, kind, file, msg):
        self.domain, self.sev, self.kind, self.file, self.msg = domain, sev, kind, file, msg

    def row(self):
        return f"| {self.domain} | {self.sev} | {self.kind} | {self.file} | {self.msg} |"


# ----------------------------------------------------------------------------- lint
def lint_domain(root, domain, core):
    F = []
    files = {f: os.path.join(core, f) for f in os.listdir(core) if f.endswith(".md")}
    texts = {f: read(p) or "" for f, p in files.items()}
    droot = os.path.join(root, domain)

    # 1. freshness (M-minor: modified: frontmatter preferred)
    for f, p in files.items():
        target = freshness_days(f)
        if target is None or f in GENERATED:
            continue
        d, how = last_updated(texts[f], p)
        age = (TODAY - d).days
        if age > target:
            F.append(Finding(domain, "STALE", "freshness", f, f"{age}d old (target {target}d; date from {how}) — treat as hypothesis"))
        if not DESCRIPTION_RE.search(texts[f][:1500]):
            F.append(Finding(domain, "INFO", "frontmatter", f, "no `description:` line — BOOT_PACK signpost falls back to first prose line"))

    # 2. structure
    if "CONTEXT_RESTORE_PROTOCOL.md" in files:
        F.append(Finding(domain, "INFO", "legacy", "CONTEXT_RESTORE_PROTOCOL.md", "legacy since v2.4 — keep, do not update"))
    if "OWNERS.md" not in files:
        F.append(Finding(domain, "WARN", "owners", "OWNERS.md", "missing — add write manifest (one-row version is fine at Core level)"))
    if not os.path.isdir(os.path.join(droot, "Documents")):
        F.append(Finding(domain, "INFO", "documents", "Documents/", "no Documents/ folder — source files belong there, not in core/"))

    # 3. dangling references in bootstrap files
    for f in ("AI_AGENTS_READ_THIS_FIRST.md", "START_HERE.md"):
        if f not in texts:
            if f == "AI_AGENTS_READ_THIS_FIRST.md":
                F.append(Finding(domain, "WARN", "bootstrap", f, "missing"))
            continue
        for ref in set(REF_RE.findall(texts[f])):
            if "[" in ref or ref.startswith(("http", "../")):
                continue
            base = os.path.basename(ref)
            cands = [os.path.join(core, ref), os.path.join(core, base), os.path.join(root, ref), os.path.join(droot, ref)]
            if not any(os.path.exists(c) for c in cands):
                F.append(Finding(domain, "WARN", "dangling-ref", f, f"references `{ref}` which does not exist"))

    # 4. open items: overdue, stalls, blocked_by resolution (M6)
    rows = oi_rows(texts.get("OPEN_ITEMS.md", ""))
    ids_all = {r["id"] for r in rows}
    history = (texts.get("SESSION_DIARY.md", "") + texts.get("CHECKPOINTS.md", ""))
    for r in rows:
        if r["done"]:
            continue
        cols = r["cols"]
        if len(cols) >= 3 and not re.search(r"\b(OPEN|OPENED|ADDED|CREATED|SINCE|ONGOING|ROLLING|STANDING)\b", cols[2], re.I):
            m = DATE_RE.search(cols[2])
            if m:
                try:
                    due = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    if due < TODAY:
                        F.append(Finding(domain, "OVERDUE", "open-item", "OPEN_ITEMS.md", f"{r['id']} due {due} ({(TODAY - due).days}d ago) — close it or re-date it"))
                except ValueError:
                    pass
        t = r["tags"]
        for dep in re.findall(r"OI-[A-Za-z0-9-]+", t.get("blocked_by", "")):
            dep_row = next((x for x in rows if x["id"] == dep), None)
            if dep_row is None:
                F.append(Finding(domain, "WARN", "blocked-by", "OPEN_ITEMS.md", f"{r['id']} blocked_by {dep} which is not in Active"))
            elif dep_row["done"]:
                F.append(Finding(domain, "INFO", "unblocked", "OPEN_ITEMS.md", f"{r['id']} is now unblocked — {dep} is closed"))
        for key in ("claimed", "started"):
            m = DATE_RE.search(t.get(key, ""))
            if m:
                since = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                if (TODAY - since).days > STALL_DAYS and r["id"] not in history:
                    F.append(Finding(domain, "WARN", "stall", "OPEN_ITEMS.md", f"{r['id']} {key} {since} ({(TODAY - since).days}d) with no diary/checkpoint mention — stalled or unlogged"))

    # 5. diary size
    diary = texts.get("SESSION_DIARY.md")
    if diary is not None and diary.count("\n") + 1 > DIARY_LINE_THRESHOLD:
        F.append(Finding(domain, "WARN", "diary-size", "SESSION_DIARY.md", f"{diary.count(chr(10)) + 1} lines (> {DIARY_LINE_THRESHOLD}) — compress (extract dead-ends first) or stub"))

    # 6. checkpoints
    cp = texts.get("CHECKPOINTS.md", "")
    for e in re.split(r"\n(?=### CP-)", cp):
        if not e.startswith("### CP-"):
            continue
        title = e.split("\n", 1)[0][4:].strip()
        if not TAIL_RE.search(e):
            F.append(Finding(domain, "WARN", "checkpoint", "CHECKPOINTS.md", f"{title[:50]} — no checkpoint-tail marker"))
        if re.search(r"\*\*Outcome:\*\*\s*DEAD-END", e):
            cm = re.search(r"\*\*Class:\*\*\s*([a-z\-]+)", e)
            if not cm or cm.group(1) not in CLASSES:
                F.append(Finding(domain, "WARN", "checkpoint", "CHECKPOINTS.md", f"{title[:50]} — DEAD-END without a valid Class:"))

    # 7. untraced numbers (P3)
    for f, t in texts.items():
        if not any(f == s or (s.startswith("_") and f.endswith(s)) for s in SOURCE_TAGGED):
            continue
        untraced, ex = 0, []
        for line in t.split("\n"):
            nums = NUMBER_RE.findall(line)
            if nums and not SRC_RE.search(line):
                untraced += len(nums)
                if len(ex) < 2:
                    ex.append(nums[0].strip())
        if untraced:
            F.append(Finding(domain, "INFO", "untraced", f, f"{untraced} figure(s) without [src:] tag (e.g. {', '.join(ex)}) — summaries, not sources"))

    # 8. line tags (M3): valid ranges, supersedes, duplicates, stale opinions, bad classes
    all_ids = set(ids_all)
    for f, t in texts.items():
        if f in GENERATED:
            continue
        all_ids |= {i.rstrip("-") for i in DEF_RE.findall(t)}
    for f in COLLECTION_FILES:
        for e in entries(texts.get(f, "")):
            all_ids.add(e["id"])
    for f in COLLECTION_FILES:
        open_by_id = {}
        for e in entries(texts.get(f, "")):
            t = parse_tags(e["body"][:600] + " " + e["title"])
            start, end = parse_valid(t.get("valid", ""))
            if t.get("class") and t["class"] not in LINE_CLASSES:
                F.append(Finding(domain, "WARN", "line-tag", f, f"{e['id']} class `{t['class']}` not in {sorted(LINE_CLASSES)}"))
            sup = t.get("supersedes", "")
            for sid in re.findall(r"[A-Z]+-[A-Za-z0-9-]+", sup):
                if sid.rstrip("-") not in all_ids:
                    F.append(Finding(domain, "WARN", "line-tag", f, f"{e['id']} supersedes {sid} which does not exist in core"))
            if end is None:
                open_by_id.setdefault(e["id"], []).append(e)
            if t.get("class") == "opinion" and start and (TODAY - start).days > OPINION_STALE_DAYS and "confidence" not in t:
                F.append(Finding(domain, "INFO", "line-tag", f, f"{e['id']} is an opinion {(TODAY - start).days}d old with no confidence — reinforce, downgrade or close it"))
        for eid, es in open_by_id.items():
            if len(es) > 1:
                F.append(Finding(domain, "WARN", "line-tag", f, f"{eid} defined {len(es)} times with no closed {{valid:}} range — close the superseded one"))

    # 9. cross-artifact (M8): every ID mentioned must exist; GOALS [NEXT] must appear in STATUS next-3 or active OI; ARCHITECTURE paths exist
    mentioned = set()
    for f, t in texts.items():
        if f in GENERATED:
            continue
        mentioned |= set(ID_RE.findall(t))
    prefix_stem = lambda i: i.split("-")[1] if "-" in i else ""
    own_stems = {prefix_stem(i) for i in all_ids}
    missing = sorted(i for i in mentioned if i not in all_ids and prefix_stem(i) in own_stems and not re.search(r"-(?:N+|X+|nnn|xxx)$", i))
    if missing:
        F.append(Finding(domain, "WARN", "cross-ref", "core/", f"{len(missing)} ID(s) referenced but not defined anywhere in core: {', '.join(missing[:6])}{' …' if len(missing) > 6 else ''}"))
    goals = texts.get("GOALS.md", "")
    ss = texts.get("STATUS_SNAPSHOT.md", "")
    nxt = section(ss, r"## What's next[^\n]*\n").lower()
    active_txt = " ".join(r["line"] for r in rows if not r["done"]).lower()
    for m in re.finditer(r"(?m)^- (M\d+):\s*\[NEXT\]\s*(.+)$", goals):
        words = [w for w in re.findall(r"[a-z]{4,}", m.group(2).lower())][:8]
        if words and not any(w in nxt or w in active_txt for w in words):
            F.append(Finding(domain, "WARN", "coherence", "GOALS.md", f"{m.group(1)} is [NEXT] but nothing in STATUS next-3 or active OPEN_ITEMS mentions it"))
    arch = texts.get("ARCHITECTURE.md", "")
    dead = [p for p in re.findall(r"`((?:src|lib|app|packages|tools|scripts)/[A-Za-z0-9_./\-]+)`", arch) if not os.path.exists(os.path.join(droot, p))]
    if dead:
        F.append(Finding(domain, "WARN", "derivable", "ARCHITECTURE.md", f"{len(dead)} mapped path(s) no longer exist (e.g. {dead[0]}) — regenerate the module table from the tree"))

    # 10. generated-file currency
    if "BOOT_PACK.md" in files and "STATUS_SNAPSHOT.md" in files and os.path.getmtime(files["BOOT_PACK.md"]) < os.path.getmtime(files["STATUS_SNAPSHOT.md"]):
        F.append(Finding(domain, "WARN", "bootpack", "BOOT_PACK.md", "older than STATUS_SNAPSHOT.md — regenerate"))
    elif "BOOT_PACK.md" not in files:
        F.append(Finding(domain, "INFO", "bootpack", "BOOT_PACK.md", "not generated yet — `limo_lint.py bootpack`"))
    pend = os.path.join(core, "_pending")
    if os.path.isdir(pend):
        n = len([x for x in os.listdir(pend) if x.endswith(".md")])
        if n:
            F.append(Finding(domain, "INFO", "pending", "_pending/", f"{n} proposal(s) awaiting promotion — review before writing to collection files"))
    return F


def lint_spec(root):
    F = []
    spec = os.path.join(root, "LIMO", "LIMO_FRAMEWORK.md")
    t = read(spec)
    if t is None:
        return F
    d, _ = last_updated(t, spec)
    if (TODAY - d).days > 180:
        F.append(Finding("LIMO", "STALE", "spec", "LIMO_FRAMEWORK.md", f"{(TODAY - d).days}d since last update (target 180d) — re-verify Source: lines"))
    cited = set(re.findall(r"`((?:shared|infra|LIMO|tools|_messages)/[A-Za-z0-9_./\-]+)`", t))
    cited |= set(re.findall(r"Source[s]?:\*?\s*`([^`\s]+/[^`\s]+)`", t))
    for c in sorted(cited):
        if not os.path.exists(os.path.join(root, c.rstrip("/"))):
            F.append(Finding("LIMO", "WARN", "spec-ref", "LIMO_FRAMEWORK.md", f"cites `{c}` which does not exist"))
    return F


def aggregate(findings):
    agg, by = [], {}
    for f in findings:
        if f.kind in ("open-item", "freshness"):
            by.setdefault((f.domain, f.kind), []).append(f)
        else:
            agg.append(f)
    for (dom, kind), fs in by.items():
        if kind == "open-item":
            ids = [f.msg.split(" due ")[0] for f in fs]
            oldest = max(int(re.search(r"\((\d+)d ago\)", f.msg).group(1)) for f in fs)
            agg.append(Finding(dom, "OVERDUE", kind, "OPEN_ITEMS.md", f"{len(fs)} active item(s) past due (oldest {oldest}d): {', '.join(ids[:4])}{' …' if len(ids) > 4 else ''} — `--full` lists all"))
        else:
            fs.sort(key=lambda f: -int(f.msg.split("d old")[0]))
            worst = ", ".join(f"{f.file} {f.msg.split(' (')[0]}" for f in fs[:3])
            agg.append(Finding(dom, "STALE", kind, f"{len(fs)} file(s)", f"past freshness target — worst: {worst}{' …' if len(fs) > 3 else ''} — `--full` lists all"))
    return agg


def cmd_lint(root, only, full=False):
    findings = []
    doms = domains(root, only)
    for name, core in doms:
        findings += lint_domain(root, name, core)
    if not only:
        findings += lint_spec(root)
    if not full:
        findings = aggregate(findings)
    order = {"OVERDUE": 0, "STALE": 1, "WARN": 2, "INFO": 3}
    findings.sort(key=lambda f: (order.get(f.sev, 9), f.domain, f.file))
    print(f"# limo-lint — {TODAY} — {len(findings)} finding(s) across {len(doms)} domain(s)\n")
    print("| Domain | Severity | Check | File | Finding |\n|:--|:--|:--|:--|:--|")
    for f in findings:
        print(f.row())
    if not findings:
        print("| — | — | — | — | clean |")
    return 1 if any(f.sev in ("OVERDUE", "STALE", "WARN") for f in findings) else 0


# ----------------------------------------------------------------------------- triggers (M2)
def trigger_entries(core):
    out = []
    for f in ("NEVER_AGAIN.md", "INVARIANTS.md"):
        t = read(os.path.join(core, f)) or ""
        for e in entries(t):
            trig = []
            m = TRIGGERS_FIELD_RE.search(e["body"][:800])
            if m:
                trig += [x.strip() for x in m.group(1).split(",") if x.strip()]
            tg = parse_tags(e["body"][:800] + " " + e["title"]).get("triggers")
            if tg:
                trig += [x.strip() for x in tg.split(",") if x.strip()]
            if trig:
                out.append({"file": f, "id": e["id"], "title": e["title"], "triggers": trig, "body": e["body"].strip()})
    return out


def cmd_trigger_index(root, only):
    for name, core in domains(root, only):
        te = trigger_entries(core)
        L = [f"<!-- GENERATED by tools/limo_lint.py on {TODAY}. DO NOT EDIT. Add `Triggers:` lines to NEVER_AGAIN / INVARIANTS entries instead. -->",
             f"# Trigger index — {name}", "",
             "Before acting on a request: `python3 tools/limo_lint.py triggers \"<request>\" " + name + "` and read every hit in full.", "",
             "| Trigger | Gate | File |", "|:--|:--|:--|"]
        for e in te:
            for tr in e["triggers"]:
                L.append(f"| `{tr}` | {e['id']} — {e['title'][:70]} | {e['file']} |")
        if not te:
            L.append("| — | no entries carry a `Triggers:` line yet | — |")
        write(os.path.join(core, "TRIGGER_INDEX.md"), "\n".join(L))
        print(f"wrote {name}/{CORE}/TRIGGER_INDEX.md ({sum(len(e['triggers']) for e in te)} trigger(s))")


def cmd_triggers(root, text, domain):
    core = os.path.join(root, domain, CORE)
    low = text.lower()
    words = set(re.findall(r"[A-Za-z0-9_./\-]+", low))
    hits = []
    for e in trigger_entries(core):
        for tr in e["triggers"]:
            trl = tr.lower()
            if any(ch in tr for ch in "*?[") or "/" in tr or tr.startswith("."):
                if any(fnmatch.fnmatch(w, trl) for w in words):
                    hits.append((tr, e)); break
            elif trl in low:
                hits.append((tr, e)); break
    if not hits:
        print(f"[LIMO triggers] {domain}: no gate matches this request.")
        return 0
    print(f"[LIMO triggers] {domain}: {len(hits)} gate(s) match — read in full before acting.\n")
    for tr, e in hits:
        print(f"## {e['id']} — {e['title']}   (matched `{tr}`, {e['file']})\n{e['body']}\n")
    return 0


# ----------------------------------------------------------------------------- ready (M6)
def cmd_ready(root, domain, agent=None):
    core = os.path.join(root, domain, CORE)
    rows = oi_rows(read(os.path.join(core, "OPEN_ITEMS.md")) or "")
    by_id = {r["id"]: r for r in rows}
    ready, blocked, taken = [], [], []
    for r in rows:
        if r["done"]:
            continue
        deps = re.findall(r"OI-[A-Za-z0-9-]+", r["tags"].get("blocked_by", ""))
        open_deps = [d for d in deps if d in by_id and not by_id[d]["done"]]
        claimed = r["tags"].get("claimed", "")
        if open_deps:
            blocked.append((r, open_deps))
        elif claimed and (not agent or agent.lower() not in claimed.lower()):
            taken.append((r, claimed))
        else:
            ready.append(r)
    print(f"# ready — {domain} — {TODAY}\n")
    print(f"## Ready ({len(ready)}) — no open blockers, unclaimed{' or claimed by ' + agent if agent else ''}")
    for r in ready:
        print(f"- {r['line'][:220]}")
    print(f"\n## Claimed by someone else ({len(taken)})")
    for r, c in taken:
        print(f"- {r['id']} — {c}")
    print(f"\n## Blocked ({len(blocked)})")
    for r, deps in blocked:
        print(f"- {r['id']} ← {', '.join(deps)}")
    print("\nTo claim: append `{claimed: <agent> " + str(TODAY) + "}` to the row (one agent per row; lint flags a second claim and a claim with no progress after " + str(STALL_DAYS) + "d).")
    return 0


# ----------------------------------------------------------------------------- reflect (M4)
def cmd_reflect(root, domain):
    core = os.path.join(root, domain, CORE)
    proposals = []
    pool = []
    for f in COLLECTION_FILES:
        for e in entries(read(os.path.join(core, f)) or ""):
            pool.append((f, e))
    # near-duplicates
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            fa, a = pool[i]; fb, b = pool[j]
            sa = (a["title"] + " " + a["body"][:300]).lower()
            sb = (b["title"] + " " + b["body"][:300]).lower()
            r = difflib.SequenceMatcher(None, sa, sb).ratio()
            if r >= 0.6:
                proposals.append(("MERGE", f"{a['id']} ({fa}) ≈ {b['id']} ({fb}) similarity {r:.2f} — keep one, close the other with {{valid: ..{TODAY}}} {{supersedes: <kept>}}"))
    # closed ranges still in the live file
    for f, e in pool:
        t = parse_tags(e["body"][:600] + " " + e["title"])
        s, en = parse_valid(t.get("valid", ""))
        if en and en < TODAY:
            proposals.append(("ARCHIVE", f"{e['id']} ({f}) closed {en} — move to _archive/{f} (keep the text; never delete)"))
    # misplaced content
    for f, e in pool:
        b = e["body"]
        if f == "LEARNINGS.md" and re.search(r"(?m)^\s*-\s*\*{0,2}Decision:\*{0,2}", b):
            proposals.append(("MOVE", f"{e['id']} in LEARNINGS.md has a Decision: field — belongs in DECISIONS.md"))
        if f == "DECISIONS.md" and re.search(r"(?m)^\s*-\s*\*{0,2}Prevention gate:\*{0,2}", b):
            proposals.append(("MOVE", f"{e['id']} in DECISIONS.md has a Prevention gate: — belongs in NEVER_AGAIN.md"))
        if f == "NEVER_AGAIN.md" and not re.search(r"Prevention gate", b):
            proposals.append(("FIX", f"{e['id']} in NEVER_AGAIN.md has no Prevention gate: field — it is a story, not a gate"))
    out = os.path.join(core, "_pending", f"reflect_{TODAY}.md")
    L = [f"<!-- GENERATED by tools/limo_lint.py reflect on {TODAY}. Proposals only. Nothing here is applied until a human, or a session told to, promotes it. -->",
         f"# Reflect proposals — {domain} — {TODAY}", "",
         f"{len(proposals)} proposal(s). Apply by editing the source file per LIMO v2.5 Memory Line Conventions, then delete this file.", ""]
    for kind, msg in proposals or [("NONE", "nothing to merge, archive or move")]:
        L.append(f"- [ ] **{kind}** — {msg}")
    write(out, "\n".join(L))
    print(f"wrote {domain}/{CORE}/_pending/reflect_{TODAY}.md ({len(proposals)} proposal(s))")
    return 0


# ----------------------------------------------------------------------------- bootpack (M1)
def settled_tables(root, domain):
    out, base = [], os.path.join(root, domain)
    for dirpath, dirnames, files in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in ("_archive", "archive", "node_modules", ".git", "_pending")]
        for f in sorted(files):
            if not f.endswith(".md") or f in GENERATED:
                continue
            t = read(os.path.join(dirpath, f)) or ""
            for m in re.finditer(r"(?im)^(#{1,4}\s*SETTLED[^\n]*)\n((?:\|[^\n]*\n?)+)", t):
                rel = os.path.relpath(os.path.join(dirpath, f), base)
                out.append(f"**{rel}**\n{m.group(2).strip()}")
    return out


def titles(text, prefix):
    return [f"- {e['id']} — {e['title'][:90]}" for e in entries(text) if e["id"].startswith(prefix)]


def tree(path, depth=2):
    out = []
    if not os.path.isdir(path):
        return out
    base = path.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, files in os.walk(path):
        d = dirpath.count(os.sep) - base
        dirnames[:] = sorted(x for x in dirnames if not x.startswith("."))
        if d >= depth:
            dirnames[:] = []
        out.append(f"{'  ' * d}{os.path.basename(dirpath)}/  ({len(files)} files)")
    return out


def build_part_a(root, name, core, texts):
    A = [f"# BOOT PACK — {name}",
         f"Generated {TODAY}. Summaries of summaries: every line is a pointer. Open the source before quoting a figure. Run `limo_lint.py triggers \"<request>\" {name}` before acting."]
    st = settled_tables(root, name)
    A.append("\n## SETTLED — DO NOT RE-LITIGATE")
    A += st[:3] if st else ["_(none)_"]
    ss = texts.get("STATUS_SNAPSHOT.md", "")
    for h, label in ((r"## Goal[^\n]*\n", "Goal"), (r"## Blockers[^\n]*\n", "Blockers"), (r"## What's next[^\n]*\n", "Next 3")):
        sec = section(ss, h).strip()
        if sec:
            A.append(f"\n## {label}")
            A += sec.split("\n")[:5]
    na = titles(texts.get("NEVER_AGAIN.md", ""), "NA-")
    A.append(f"\n## NEVER_AGAIN gates ({len(na)}) — titles; bodies in NEVER_AGAIN.md, keyword hits via `triggers`")
    A += na[:10] + ([f"- … {len(na) - 10} more"] if len(na) > 10 else [])
    inv = titles(texts.get("INVARIANTS.md", ""), "INV-")
    A.append(f"\n## INVARIANTS ({len(inv)}) — titles")
    A += inv[:10] + ([f"- … {len(inv) - 10} more"] if len(inv) > 10 else [])
    fs = [f for f in lint_domain(root, name, core) if f.kind not in ("bootpack", "frontmatter")]
    counts = {}
    for f in fs:
        counts[f.sev] = counts.get(f.sev, 0) + 1
    A.append("\n## Lint: " + (", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "clean") + " — `limo_lint.py lint " + name + "`")
    return A


def cmd_bootpack(root, only):
    rc = 0
    for name, core in domains(root, only):
        texts = {f: read(os.path.join(core, f)) or "" for f in os.listdir(core) if f.endswith(".md")}
        A = build_part_a(root, name, core, texts)
        over = len(A) - PART_A_BUDGET
        banner = f"<!-- GENERATED by tools/limo_lint.py bootpack on {TODAY}. DO NOT EDIT. Fix the source file and regenerate. -->"
        if over > 0:
            A = A[:PART_A_BUDGET] + [f"\n**OVER BUDGET by {over} line(s)** — compress at source: SETTLED tables, Blockers, Next 3. Part A is capped at {PART_A_BUDGET} lines."]
            rc = 1
        # Part B — signposts
        B = ["\n---\n## Signposts — read on demand (path — description — last updated)"]
        for f in sorted(texts):
            if f in GENERATED:
                continue
            d, how = last_updated(texts[f], os.path.join(core, f))
            tgt = freshness_days(f)
            state = "" if tgt is None else (" ⚠️stale" if (TODAY - d).days > tgt else "")
            B.append(f"- `core/{f}` — {description_of(texts[f], f)} — {d}{state}")
        B.append("- `core/TRIGGER_INDEX.md` — keyword → gate map (generated)")
        tr = tree(os.path.join(root, name, "Documents"))
        B.append("\n**Documents/ (facts live here — grep before asserting)**")
        B.append("```\n" + ("\n".join(tr) if tr else "(no Documents/ folder)") + "\n```")
        tails = TAIL_RE.findall(texts.get("CHECKPOINTS.md", ""))
        if tails:
            B.append("\n**Last 3 checkpoint tails**")
            B += [f"- {t.strip()[:160]}" for t in tails[-3:]]
        body = "\n".join([banner] + A + B + [banner])
        write(os.path.join(core, "BOOT_PACK.md"), body)
        print(f"wrote {name}/{CORE}/BOOT_PACK.md (Part A {min(len(A), PART_A_BUDGET)}/{PART_A_BUDGET} lines{' OVER BUDGET' if over > 0 else ''}, total {body.count(chr(10)) + 1})")
    return rc


def cmd_agentsmd(root, only):
    for name, core in domains(root, only):
        wt, gd, status = memory_repo_for(root, name)
        if status == "no-marker":
            print(f"{name}: skipped AGENTS.md — limo-populated/ is inside a human-driven repository ({os.path.relpath(wt, root)}); nearest-file-wins would shadow the hand-written one")
            continue
        texts = {f: read(os.path.join(core, f)) or "" for f in os.listdir(core) if f.endswith(".md")}
        A = build_part_a(root, name, core, texts)[:PART_A_BUDGET]
        owners = texts.get("OWNERS.md", "").strip()
        L = [f"<!-- GENERATED by tools/limo_lint.py agentsmd on {TODAY} from BOOT_PACK Part A + OWNERS.md. DO NOT EDIT. -->",
             f"# {name} — AGENTS.md (LIMO v2.5, generated)", "",
             "Any agent (Codex, Copilot, Cursor, Gemini, Claude) starts here. Full spec: `../../LIMO/LIMO_FRAMEWORK.md`.", "",
             "## Boot", f"1. Read `core/BOOT_PACK.md` (this file's Part A is a copy), then `core/{name.upper().replace(' ', '_')}_SESSION_PROMPT.md` if present, then `core/OWNERS.md`.",
             "2. `ls -R ../Documents/` and grep before claiming anything is absent.",
             f"3. Before acting on a request: `python3 tools/limo_lint.py triggers \"<request>\" \"{name}\"` from the workspace root.",
             "4. First line of your first reply: `[LIMO: " + name + " booted from BOOT_PACK <date>]`.", "",
             "## Fences", "- Files marked `propose` in OWNERS.md are written only via your own diary / `core/_pending/`; the owner promotes.",
             "- The human drives git for code. Memory commits go through `limo_lint.py commit` only, and only touch `core/`.",
             "- Never delete a superseded line — close its `{valid: ..date}` and point the new one with `{supersedes:}`.",
             "- Assume interruption: write STATUS next-3 + one diary line before any long step, and before context compaction.", "",
             "## Write authority (OWNERS.md)", owners or "_(no OWNERS.md yet — treat every core file as propose-only)_", "", "---", ""]
        target = os.path.join(root, name, "limo-populated", "AGENTS.md")
        existing = read(target)
        if existing is not None and "GENERATED by tools/limo_lint.py agentsmd" not in existing[:300]:
            print(f"{name}: skipped AGENTS.md — a hand-written one exists at limo-populated/AGENTS.md; not overwriting")
            continue
        write(target, "\n".join(L + A))
        print(f"wrote {name}/limo-populated/AGENTS.md")
    return 0


# ----------------------------------------------------------------------------- deadends (P5)
def cmd_deadends(root):
    rows = []
    for name, core in domains(root):
        cp = read(os.path.join(core, "CHECKPOINTS.md")) or ""
        for e in re.split(r"\n(?=### CP-)", cp):
            if not e.startswith("### CP-") or not re.search(r"\*\*Outcome:\*\*\s*DEAD-END", e):
                continue
            cid = e.split("\n", 1)[0][4:].split("—")[0].strip()
            agent = (re.search(r"\*\*Agent:\*\*\s*([^\n]+)", e) or [None, "?"])[1].strip()
            date = (re.search(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", e) or [None, "?"])[1]
            cls = (re.search(r"\*\*Class:\*\*\s*([a-z\-]+)", e) or [None, "unclassified"])[1]
            tm = TAIL_RE.search(e)
            rows.append((agent, cls, name, date, "DEAD-END", cid, (tm.group(1).strip() if tm else "(no tail)")[:180], f"{name}/{CORE}/CHECKPOINTS.md"))
        for e in entries(read(os.path.join(core, "NEVER_AGAIN.md")) or ""):
            if not e["id"].startswith("NA-"):
                continue
            gate = re.search(r"Prevention gate:\*{0,2}\s*(.*)", e["body"])
            cls = next((c for c in CLASSES if re.search(rf"\bClass:\*{{0,2}}\s*{c}", e["body"])), "unclassified")
            rows.append(("(domain)", cls, name, "", "NEVER-AGAIN", e["id"], (gate.group(1) if gate else e["title"]).strip().lstrip("*: ")[:180], f"{name}/{CORE}/NEVER_AGAIN.md"))
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    L = [f"<!-- GENERATED by tools/limo_lint.py deadends on {TODAY}. DO NOT EDIT. -->", "# Dead-End Index (cross-domain)", "",
         f"Generated {TODAY}. One row per `Outcome: DEAD-END` checkpoint and per NEVER_AGAIN entry, sorted by agent then class. Read at boot only when your task's class has entries. Routing rule (LIMO v2.5): an agent with repeated dead-ends of one class does not get that class again without a written reason.",
         f"Rows: {len(rows)}. Unclassified rows need a `Class:` line at source.", "",
         "| Agent | Class | Domain | Date | Kind | ID | Summary | File |", "|:--|:--|:--|:--|:--|:--|:--|:--|"]
    L += ["| " + " | ".join(x.replace("|", "\\|") for x in r) + " |" for r in rows]
    tally = {}
    for r in rows:
        if r[4] == "DEAD-END":
            tally[(r[0], r[1])] = tally.get((r[0], r[1]), 0) + 1
    if tally:
        L += ["", "## Dead-ends by agent × class", "", "| Agent | Class | Count |", "|:--|:--|--:|"] + [f"| {a} | {c} | {n} |" for (a, c), n in sorted(tally.items(), key=lambda kv: -kv[1])]
    write(os.path.join(root, "shared", "DEAD_END_INDEX.md"), "\n".join(L + ["", f"<!-- GENERATED by tools/limo_lint.py deadends on {TODAY}. DO NOT EDIT. -->"]))
    print(f"wrote shared/DEAD_END_INDEX.md ({len(rows)} rows)")
    return 0


# ----------------------------------------------------------------------------- git (M7)
MAC_ROOT = os.environ.get("LIMO_HOST_ROOT", "")  # host path of the workspace, for remapping worktree .git files inside a sandbox
MARKER = ".limo-memory-repo"   # present at a repo's work-tree root => agents may commit core/ there


def find_repo(start, root):
    """Walk up from `start` to `root` looking for .git (dir or worktree file). Returns (work_tree, git_dir) or None.
    Worktree files that point at Mac paths are remapped onto this root so the sandbox can use them."""
    cur = os.path.abspath(start)
    root = os.path.abspath(root)
    while True:
        g = os.path.join(cur, ".git")
        if os.path.isdir(g):
            return cur, g
        if os.path.isfile(g):
            m = re.search(r"gitdir:\s*(.+)", read(g) or "")
            if m:
                gd = m.group(1).strip()
                if not os.path.isabs(gd):
                    gd = os.path.normpath(os.path.join(cur, gd))
                if not os.path.exists(gd) and gd.startswith(MAC_ROOT):
                    gd = os.path.join(root, os.path.relpath(gd, MAC_ROOT))
                if os.path.exists(gd):
                    return cur, gd
        if cur == root or os.path.dirname(cur) == cur:
            return None
        cur = os.path.dirname(cur)


def can_unlink(git_dir):
    """The Cowork sandbox mounts the workspace without delete permission unless granted; git cannot clean its
    lock files there and every commit leaves HEAD.lock / index.lock behind. Probe before touching the repo."""
    probe = os.path.join(git_dir, f".limo-probe-{os.getpid()}")
    try:
        with open(probe, "w") as f:
            f.write("probe")
        os.remove(probe)
        return True
    except OSError:
        return False


def clear_stale_lock(git_dir, max_age=120):
    notes = []
    for name in os.listdir(git_dir):
        if not name.endswith(".lock"):
            continue
        lock = os.path.join(git_dir, name)
        age = time.time() - os.path.getmtime(lock)
        running = subprocess.run(["pgrep", "-x", "git"], capture_output=True).returncode == 0
        if age > max_age and not running:
            try:
                os.remove(lock)
                notes.append(f"removed stale {name} ({int(age)}s old, no git process)")
            except OSError as e:
                notes.append(f"cannot remove {name}: {e}")
        else:
            notes.append(f"{name} present ({int(age)}s old{', git running' if running else ''}) — not removed")
    return "; ".join(notes) or None


def git(work_tree, git_dir, *args, agent="limo"):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    cmd = ["git", "--git-dir", git_dir, "--work-tree", work_tree, "-c", "core.fsmonitor=false", "-c", "core.filemode=false",
           "-c", f"user.name=LIMO ({agent})", "-c", f"user.email=limo+{agent}@local", *args]
    for attempt in range(3):
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if p.returncode == 0 or ".lock" not in (p.stderr or ""):
            return p
        note = clear_stale_lock(git_dir)
        print(f"  git: {note}")
        time.sleep(1.5)
    return p


def memory_repo_for(root, domain):
    """(work_tree, git_dir, status) — status in: ok | no-repo | no-marker | tracked-elsewhere."""
    core = os.path.join(root, domain, CORE)
    lp = os.path.join(root, domain, "limo-populated")
    nested = os.path.join(lp, ".git")
    if os.path.exists(nested):
        found = find_repo(lp, root)
        if found:
            wt, gd = found
            return wt, gd, ("ok" if os.path.exists(os.path.join(wt, MARKER)) else "no-marker")
    found = find_repo(core, root)
    if not found:
        return None, None, "no-repo"
    wt, gd = found
    return wt, gd, ("ok" if os.path.exists(os.path.join(wt, MARKER)) else "no-marker")


def cmd_commit(root, domain, agent, trigger):
    core = os.path.join(root, domain, CORE)
    wt, gd, status = memory_repo_for(root, domain)
    if status == "no-repo":
        print(f"{domain}: core/ is not inside a git repository — run `limo_lint.py git-init \"{domain}\"` first.")
        return 2
    if status == "no-marker":
        print(f"{domain}: core/ lives in the repository at {os.path.relpath(wt, root)} which has no `{MARKER}` file at its root.\n"
              f"  That repository is human-driven (the 'The human drives git' fence). Agent commits are disabled there.\n"
              f"  Either run `limo_lint.py git-init \"{domain}\"` (creates a nested memory-only repo if the enclosing one ignores limo-populated/),\n"
              f"  or, if you want agents committing into that repository, create the marker yourself: `touch \"{os.path.join(wt, MARKER)}\"`.")
        return 2
    if not can_unlink(gd):
        print(f"{domain}: this environment cannot delete files under {os.path.relpath(gd, root)} — git would leave lock files behind.\n"
              f"  Commit from the Mac or from Codex instead, or grant delete permission for the workspace to this session. Nothing was changed.")
        return 2
    note = clear_stale_lock(gd)
    if note:
        print(f"  git: {note}")
    rel = os.path.relpath(core, wt)
    p = git(wt, gd, "status", "--porcelain", "--", rel, agent=agent)
    changed = [ln[3:] for ln in p.stdout.splitlines() if ln.strip() and not any(ln.rstrip().endswith(g) for g in GENERATED)]
    if not changed:
        print(f"{domain}: nothing to commit under {rel}/" + (f" ({p.stderr.strip()[:120]})" if p.stderr.strip() else ""))
        return 0
    git(wt, gd, "add", "--", rel, agent=agent)
    for g in GENERATED:
        git(wt, gd, "reset", "-q", "--", os.path.join(rel, g), agent=agent)
    files = ", ".join(sorted({os.path.basename(c.strip().strip('"')) for c in changed if c.strip()}))[:120]
    msg = f"{domain}: {files} — {trigger or 'write-back'} — {agent} — {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    p = git(wt, gd, "commit", "-q", "-m", msg, "--", rel, agent=agent)
    if p.returncode != 0:
        print(f"{domain}: commit failed — {p.stderr.strip()[:300]}")
        return 1
    h = git(wt, gd, "rev-parse", "--short", "HEAD", agent=agent).stdout.strip()
    left = clear_stale_lock(gd, max_age=0)
    print(f"{domain}: committed {h} — {msg}" + (f"\n  git: {left}" if left else ""))
    return 0


def cmd_git_init(root, domain):
    core = os.path.join(root, domain, CORE)
    lp = os.path.join(root, domain, "limo-populated")
    wt, gd, status = memory_repo_for(root, domain)
    if status == "ok":
        print(f"{domain}: memory repo already enabled at {os.path.relpath(wt, root)}")
        return 0
    if status == "no-marker":
        if os.path.abspath(wt) == os.path.abspath(lp):
            print(f"{domain}: {os.path.relpath(wt, root)} is already a repository without `{MARKER}` — it is human-driven. "
                  f"To let agents commit memory there: `touch \"{os.path.join(wt, MARKER)}\"` (your call). Not changed.")
            return 2
        tracked = git(wt, gd, "ls-files", "--", os.path.relpath(core, wt)).stdout.strip()
        if tracked:
            print(f"{domain}: core/ is tracked by the enclosing repository at {os.path.relpath(wt, root)}; a nested memory repo would hide it from that repo. "
                  f"Either keep memory human-committed there, or add `{MARKER}` at that root to allow agent commits (your call). Not changed.")
            return 2
        # enclosing repo ignores limo-populated/ (Venture pattern) -> nested memory repo is safe
    if not can_unlink(os.path.join(root, domain)):
        print(f"{domain}: this environment cannot delete files here — git init would leave locks behind. Run from the Mac or grant delete permission. Not changed.")
        return 2
    p = subprocess.run(["git", "init", "-q", lp], capture_output=True, text=True)
    if p.returncode != 0:
        print(f"{domain}: git init failed — {p.stderr.strip()}")
        return 1
    gd = os.path.join(lp, ".git")
    gi = os.path.join(lp, ".gitignore")
    if not os.path.exists(gi):
        write(gi, "# LIMO memory repo — generated files are rebuilt by tools/limo_lint.py\ncore/BOOT_PACK.md\ncore/TRIGGER_INDEX.md\nAGENTS.md\n.DS_Store\n")
    write(os.path.join(lp, MARKER), f"LIMO memory-only repository. Agents may commit core/ here via tools/limo_lint.py commit. Created {TODAY}.\n")
    git(lp, gd, "add", "-A", agent="init")
    p = git(lp, gd, "commit", "-q", "-m", f"{domain}: LIMO memory repository initialised — v2.5 — {TODAY}", agent="init")
    clear_stale_lock(gd, max_age=0)
    print(f"{domain}: initialised memory repo at {os.path.relpath(lp, root)} ({'committed' if p.returncode == 0 else p.stderr.strip()[:120]})")
    return 0


# ----------------------------------------------------------------------------- infra
def cmd_infra(root, probe=False):
    """Documentation-vs-reality checks for the [Infra] tier. Never prints keys."""
    rows = []
    for name, core in domains(root):
        d = read(os.path.join(core, "SESSION_DIARY.md"))
        if d is None:
            state = "no diary"
        elif d.count("\n") + 1 <= 40 and re.search(r"(?i)stub|event api|events api", d):
            state = "stub (migrated)"
        else:
            state = f"full flat diary ({d.count(chr(10)) + 1} lines) — history not yet on the Events API"
        rows.append((name, state))
    print(f"# limo infra — {TODAY}\n\n## Diary migration state\n\n| Domain | SESSION_DIARY |\n|:--|:--|")
    for n, st in rows:
        print(f"| {n} | {st} |")
    cat = read(os.path.join(root, "infra", "SERVICE_CATALOG.md")) or ""
    cat_dates = sorted(d for d in set("-".join(m) for m in DATE_RE.findall(cat)) if d <= str(TODAY))
    latest = cat_dates[-1] if cat_dates else "?"
    print(f"\n## Documentation drift (catalog's latest dated change: {latest})\n\n| File | Last updated | Days behind catalog |\n|:--|:--|--:|")
    for rel in ("shared/SESSION_BOOT_PROTOCOL.md", "LIMO/MY_SETUP.md", "LIMO/SERVICES_GUIDE.md", "infra/MEMORY_ARCHITECTURE.md", "shared/MEMORY_CLASSES.md"):
        p = os.path.join(root, rel)
        t = read(p)
        if t is None:
            print(f"| {rel} | missing | — |"); continue
        d, how = last_updated(t, p)
        try:
            behind = (dt.date.fromisoformat(latest) - d).days
        except ValueError:
            behind = "?"
        print(f"| {rel} | {d} ({how}) | {behind} |")
    stale_claims = []
    for rel, pat, why in (("LIMO/MY_SETUP.md", r"auto-extracts entities into Neo4j", "mem0 2.x has no graph backend (catalog 2026-06-16)"),
                          ("shared/SESSION_BOOT_PROTOCOL.md", r"replaces STATUS_SNAPSHOT \+ GOALS", "STATUS_SNAPSHOT/GOALS stay flat at every level (v2.5)")):
        t = read(os.path.join(root, rel)) or ""
        if re.search(pat, t) and not re.search(r"(?i)superseded|corrected 2026", t):
            stale_claims.append(f"- `{rel}` still says “{pat}” — {why}")
    if stale_claims:
        print("\n## Stale claims\n" + "\n".join(stale_claims))
    if probe:
        import urllib.request
        det = read(os.path.join(root, "infra", "EC2_DETAILS.md")) or ""
        hosts = sorted(h for h in set(re.findall(r"https?://[A-Za-z0-9.\-]+(?::\d+)?", det)) if "127.0.0.1" not in h and "localhost" not in h)[:6]
        print("\n## Reachability probe (from this machine; no auth sent)\n")
        for h in hosts:
            try:
                urllib.request.urlopen(urllib.request.Request(h, method="HEAD"), timeout=6)
                print(f"- {h} — reachable")
            except Exception as e:  # noqa
                print(f"- {h} — {type(e).__name__}: {str(e)[:60]}")
    else:
        print("\nRun with `--probe` from a machine that can reach the stack to test endpoint reachability. Container versions must be read on the box: `docker ps --format '{{.Names}}\t{{.Image}}'`.")
    return 0


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["lint", "bootpack", "triggers", "ready", "reflect", "deadends", "agentsmd", "commit", "git-init", "infra", "all"])
    ap.add_argument("args", nargs="*", help="domain names, or for `triggers`: \"<request text>\" Domain")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--full", action="store_true", help="lint: list every overdue item and stale file")
    ap.add_argument("--agent", default=os.environ.get("LIMO_AGENT", "cowork"), help="agent name for ready/commit")
    ap.add_argument("--trigger", default="", help="commit: which write-back trigger fired")
    ap.add_argument("--probe", action="store_true", help="infra: probe endpoint reachability")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if not domains(root):
        sys.exit(f"no */limo-populated/core/ under {root} — run from the workspace root or pass --root")
    c = a.command
    if c == "lint":
        sys.exit(cmd_lint(root, set(a.args) or None, a.full))
    if c == "bootpack":
        sys.exit(cmd_bootpack(root, set(a.args) or None))
    if c == "triggers":
        if len(a.args) < 2:
            sys.exit("usage: triggers \"<request text>\" Domain")
        sys.exit(cmd_triggers(root, a.args[0], a.args[1]))
    if c == "ready":
        sys.exit(cmd_ready(root, a.args[0], a.agent))
    if c == "reflect":
        sys.exit(cmd_reflect(root, a.args[0]))
    if c == "deadends":
        sys.exit(cmd_deadends(root))
    if c == "agentsmd":
        sys.exit(cmd_agentsmd(root, set(a.args) or None))
    if c == "commit":
        sys.exit(cmd_commit(root, a.args[0], a.agent, a.trigger))
    if c == "git-init":
        sys.exit(cmd_git_init(root, a.args[0]))
    if c == "infra":
        sys.exit(cmd_infra(root, a.probe))
    if c == "all":
        only = set(a.args) or None
        rc = cmd_lint(root, only, a.full)
        cmd_bootpack(root, only); cmd_trigger_index(root, only); cmd_deadends(root); cmd_agentsmd(root, only)
        sys.exit(rc)


if __name__ == "__main__":
    main()
