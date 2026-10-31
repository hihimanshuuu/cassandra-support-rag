"""Download selected Apache Cassandra doc pages for the Confluence snapshot.

Usage (run from the project root, with the venv active):
    python scripts/download_cassandra_docs.py --dry-run   # list pages only
    python scripts/download_cassandra_docs.py             # download everything

Output:
    data/raw_docs/<version>/<section>__<page>.md   (one file per page)
    data/raw_docs/manifest.json                    (list of all saved pages)

Docs are licensed under the Apache License 2.0. Each saved page starts with
a source/attribution line, which we also keep when importing to Confluence.
"""
import argparse
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import urldefrag, urljoin

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

SITE = "https://cassandra.apache.org/doc"
MAIN_VERSION = "5.0"    # current set
OLDER_VERSION = "4.0"   # small older set for "outdated resolution" tickets
OUT_DIR = Path("data/raw_docs")
DELAY_SECONDS = 1.0     # be polite to the Apache servers
HEADERS = {"User-Agent": "rag-learning-project/0.1 (personal learning project)"}

# Pages we read only to discover links to other pages.
SEEDS = [
    "troubleshooting/index.html",
    "getting_started/index.html",
    "configuration/index.html",
    "operating/index.html",
    "operating/compaction/index.html",
    "tools/index.html",
    "tools/nodetool/nodetool.html",
    "tools/sstable/index.html",
    "faq/index.html",
    "architecture/index.html",
    # 5.0-style locations (pages that don't exist are skipped with a warning)
    "getting-started/index.html",
    "managing/configuration/index.html",
    "managing/operating/index.html",
    "managing/operating/compaction/index.html",
    "managing/tools/index.html",
    "managing/tools/nodetool/nodetool.html",
    "managing/tools/sstable/index.html",
]

# Selection rules (paths are relative to /<version>/cassandra/).
FULL_SECTIONS = {"troubleshooting", "getting_started", "configuration",
                 "operating", "faq", "architecture"}
CQL_ALLOWED = {"ddl", "dml", "types", "security"}
NEW_ALLOWED = {"java11", "virtualtables", "auditlogging"}
NODETOOL_ALLOWED = {"nodetool", "status", "repair", "compactionstats", "tpstats",
                    "info", "describecluster", "netstats", "tablestats", "cfstats",
                    "gcstats", "drain", "cleanup", "flush", "ring", "compact",
                    "snapshot"}
SSTABLE_ALLOWED = {"index", "sstablescrub", "sstableverify", "sstabledump",
                   "sstableloader"}

# Small hand-picked set from the older version.
OLDER_PAGES = [
    "getting_started/installing.html",
    "getting_started/configuring.html",
    "configuration/cass_yaml_file.html",
    "configuration/cass_env_sh_file.html",
    "operating/repair.html",
    "operating/backups.html",
    "operating/topo_changes.html",
    "operating/hardware.html",
]

_cache = {}


def norm_parts(rel):
    """Normalise paths so 4.0 and 5.0 layouts look the same.

    5.0 uses hyphens (getting-started, storage-engine) and nests pages under
    managing/ or developing/. We drop those differences before matching.
    """
    parts = rel.removesuffix(".html").replace("-", "_").split("/")
    if len(parts) > 1 and parts[0] in {"managing", "developing", "reference"}:
        parts = parts[1:]
    return parts


def should_include(rel):
    parts = norm_parts(rel)
    section, name = parts[0], parts[-1]
    if section in FULL_SECTIONS:
        return True
    if section == "cql":
        return len(parts) == 2 and name in CQL_ALLOWED
    if section == "new":
        return name in NEW_ALLOWED
    if section == "tools":
        if len(parts) == 2:           # cqlsh, cassandra_stress, index
            return True
        if parts[1] == "nodetool":
            return name in NODETOOL_ALLOWED
        if parts[1] == "sstable":
            return name in SSTABLE_ALLOWED
    return False


def fetch(session, url):
    if url in _cache:
        return _cache[url]
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  WARN could not fetch {url}: {exc}")
        return None
    _cache[url] = resp.text
    return resp.text


def collect_links(session, version):
    """Read the seed pages and return {relative_path: url} for pages to keep."""
    base = f"{SITE}/{version}/cassandra/"
    found = {}
    for seed in SEEDS:
        url = base + seed
        html = fetch(session, url)
        if html is None:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            link, _ = urldefrag(urljoin(url, a["href"]))
            if link.startswith(base) and link.endswith(".html"):
                rel = link[len(base):]
                if should_include(rel):
                    found[rel] = link
        time.sleep(DELAY_SECONDS)
    return found


def extract(html):
    """Return (title, markdown_body) from a doc page."""
    soup = BeautifulSoup(html, "html.parser")
    node = soup.select_one("article.doc") or soup.find("article") or soup.find("main")
    if node is None:
        print("  WARN no <article>/<main> found; using whole page (may include menus)")
        node = soup.body
    h1 = node.find("h1") or soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "Untitled"
    for tag in node.select("nav, script, style, footer, .toolbar, .nav-container"):
        tag.decompose()
    text = md(str(node), heading_style="ATX")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return title, text


def save(version, rel, url, title, body):
    parts = norm_parts(rel)
    slug = "__".join(parts)
    path = OUT_DIR / version / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    section = parts[0]
    front = (
        "---\n"
        f"title: {json.dumps(title)}\n"
        f"source_url: {url}\n"
        f"cassandra_version: \"{version}\"\n"
        f"section: {section}\n"
        f"retrieved: {date.today().isoformat()}\n"
        "---\n\n"
    )
    note = (f"> Source: Apache Cassandra documentation, version {version}, {url}. "
            "Licensed under the Apache License 2.0.\n\n")
    path.write_text(front + note + body + "\n", encoding="utf-8")
    return {"title": title, "version": version, "section": section,
            "source_url": url, "file": str(path), "chars": len(body)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="list the pages that would be downloaded, then stop")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(HEADERS)

    plan = []
    for rel, url in sorted(collect_links(session, MAIN_VERSION).items()):
        plan.append((MAIN_VERSION, rel, url))
    for rel in OLDER_PAGES:
        plan.append((OLDER_VERSION, rel, f"{SITE}/{OLDER_VERSION}/cassandra/{rel}"))

    print(f"\n{len(plan)} pages selected "
          f"({MAIN_VERSION}: {sum(1 for p in plan if p[0] == MAIN_VERSION)}, "
          f"{OLDER_VERSION}: {sum(1 for p in plan if p[0] == OLDER_VERSION)})")
    if args.dry_run:
        for version, rel, _ in plan:
            print(f"  {version}  {rel}")
        return

    manifest = []
    for i, (version, rel, url) in enumerate(plan, 1):
        print(f"[{i}/{len(plan)}] {version} {rel}")
        html = fetch(session, url)
        if html is None:
            continue
        title, body = extract(html)
        manifest.append(save(version, rel, url, title, body))
        time.sleep(DELAY_SECONDS)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nSaved {len(manifest)} pages to {OUT_DIR}/ (manifest.json written)")


if __name__ == "__main__":
    main()
