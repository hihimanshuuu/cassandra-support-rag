"""Upload the downloaded Cassandra docs (Markdown) into a Confluence Cloud space.

Usage (project root, venv active):
    python scripts/upload_to_confluence.py --dry-run          # convert only, no upload
    python scripts/upload_to_confluence.py --limit 2          # upload 2 pages as a trial
    python scripts/upload_to_confluence.py                    # upload everything

Reads from .env:
    CONFLUENCE_URL      e.g. https://your-site.atlassian.net   (nothing after .net)
    ATLASSIAN_EMAIL     the email you signed up with
    ATLASSIAN_API_KEY   your Atlassian API token

Safe to re-run: pages whose title already exists in the space are skipped.
Results are written to data/confluence_pages.json (page IDs and URLs), which we
will need later for the evaluation ground truth.
"""
import argparse
import html
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import markdown
import requests
from dotenv import load_dotenv

DOCS_DIR = Path("data/raw_docs")
RESULT_FILE = Path("data/confluence_pages.json")
DELAY_SECONDS = 0.5

SECTION_LABELS = {
    "getting_started": "Getting Started",
    "configuration": "Configuration",
    "operating": "Operating",
    "tools": "Tools",
    "troubleshooting": "Troubleshooting",
    "architecture": "Architecture",
    "cql": "CQL",
    "new": "What's New",
    "faq": "FAQ",
}

CODE_SPLIT = re.compile(r"(```.*?```|`[^`\n]+`)", re.S)
CODE_RE = re.compile(r"<pre><code(?: class=\"[^\"]*\")?>(.*?)</code></pre>", re.S)


# ---------- reading and converting the Markdown files ----------

def read_page(path):
    """Return (metadata dict, markdown body) for one downloaded page."""
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n\n?(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            key, _, value = line.partition(": ")
            meta[key.strip()] = value.strip()
        body = m.group(2)
    if meta.get("title", "").startswith('"'):
        meta["title"] = json.loads(meta["title"])
    meta["cassandra_version"] = meta.get("cassandra_version", "").strip('"')
    return meta, body


def clean_markdown(body):
    # The Confluence page title already shows the heading, so drop the first H1.
    body = re.sub(r"^# .*\n+", "", body, count=1, flags=re.M)
    # Relative links would be broken in Confluence: keep the link text only.
    body = re.sub(r"\[([^\]]+)\]\((?!https?://|#)[^)]*\)", r"\1", body)
    # Garbled ellipsis seen in the source pages.
    body = body.replace("\u00e2\u0080\u00a6", "...").replace("\u00e2\u00a6", "...")
    return escape_stray_tags(body)


def escape_stray_tags(md_text):
    """Text like <keyspace_name> outside code would be read as an HTML tag and
    break the page, so escape '<' everywhere except code and real URLs."""
    parts = CODE_SPLIT.split(md_text)
    for i in range(0, len(parts), 2):  # even items are outside code
        parts[i] = re.sub(r"<(?!https?://)", "&lt;", parts[i])
    return "".join(parts)


def code_macro(code):
    code = code.replace("]]>", "]]]]><![CDATA[>")
    return ('<ac:structured-macro ac:name="code"><ac:plain-text-body>'
            f"<![CDATA[{code}]]></ac:plain-text-body></ac:structured-macro>")


def md_to_storage(md_text):
    """Convert Markdown to Confluence 'storage format' (XHTML plus macros)."""
    html_text = markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables", "def_list", "sane_lists"],
        output_format="xhtml",
    )
    return CODE_RE.sub(lambda m: code_macro(html.unescape(m.group(1))), html_text)


def build_title(meta, slug, used):
    section = meta.get("section", slug.split("__")[0])
    label = SECTION_LABELS.get(section, section.replace("_", " ").title())
    title = meta.get("title", slug)
    if "nodetool" in slug and not title.lower().startswith("nodetool"):
        title = f"nodetool {title}"
    full = f"{label}: {title} ({meta.get('cassandra_version', '?')})"
    if full in used:  # make titles unique inside the space
        full = f"{full} [{slug}]"
    used.add(full)
    return full


# ---------- Confluence API ----------

class Confluence:
    def __init__(self, site, email, token):
        # Keep only https://your-site.atlassian.net and drop any path after it.
        parsed = urlparse(site.strip() if "://" in site else "https://" + site.strip())
        self.site = f"{parsed.scheme}://{parsed.netloc}"
        self.session = requests.Session()
        self.session.auth = (email, token)
        self.session.headers.update({"Accept": "application/json"})

    def request(self, method, path, **kwargs):
        resp = None
        for _ in range(5):
            resp = self.session.request(method, f"{self.site}{path}", timeout=60, **kwargs)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", "5"))
                print(f"  rate limited, waiting {wait}s")
                time.sleep(wait)
                continue
            break
        return resp

    def space_id(self, key):
        resp = self.request("GET", "/wiki/api/v2/spaces", params={"keys": key})
        if resp.status_code == 401:
            sys.exit("Login failed (401). Check ATLASSIAN_EMAIL and ATLASSIAN_API_KEY in .env.")
        if resp.status_code != 200:
            sys.exit(f"Could not read spaces: {resp.status_code} from {resp.url}\n{resp.text[:200]}")
        results = resp.json().get("results", [])
        if not results:
            sys.exit(f"No space with key '{key}' found. Check the key and CONFLUENCE_URL.")
        return results[0]["id"]

    def find_page(self, space_id, title):
        resp = self.request("GET", "/wiki/api/v2/pages",
                            params={"space-id": space_id, "title": title})
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                return results[0]
        return None

    def create_page(self, space_id, title, storage_html):
        payload = {
            "spaceId": space_id,
            "status": "current",
            "title": title,
            "body": {"representation": "storage", "value": storage_html},
        }
        return self.request("POST", "/wiki/api/v2/pages", json=payload)

    def add_labels(self, page_id, names):
        payload = [{"prefix": "global", "name": n} for n in names]
        return self.request("POST", f"/wiki/rest/api/content/{page_id}/label", json=payload)

    def page_url(self, page):
        links = page.get("_links", {})
        base = links.get("base", f"{self.site}/wiki")
        return base + links.get("webui", "")


# ---------- main ----------

def check_login():
    """Diagnose login problems without printing any secret."""
    load_dotenv()
    site = os.getenv("CONFLUENCE_URL") or ""
    email = os.getenv("ATLASSIAN_EMAIL") or ""
    token = os.getenv("ATLASSIAN_API_KEY") or ""
    print("CONFLUENCE_URL  :", site or "MISSING")
    shape = (email[0] + "***@" + email.split("@")[-1]) if "@" in email else "NOT AN EMAIL ADDRESS"
    print("ATLASSIAN_EMAIL :", shape if email else "MISSING")
    print("ATLASSIAN_API_KEY: length", len(token),
          "| contains space or quote:", any(c in token for c in ' "\''),
          "| starts with:", token[:5] + "..." if token else "MISSING")
    if not (site and email and token):
        sys.exit("Fix the missing values in .env first.")
    api = Confluence(site, email, token)
    tests = [
        ("current user", "/wiki/rest/api/user/current"),
        ("list spaces (v1)", "/wiki/rest/api/space?limit=1"),
        ("list spaces (v2)", "/wiki/api/v2/spaces?limit=1"),
    ]
    for label, path in tests:
        resp = api.request("GET", path)
        print(f"{label:18}: HTTP {resp.status_code}")
        if resp.status_code == 200 and "user" in path:
            data = resp.json()
            got = (data.get("email") or "").lower()
            print("  logged in as   :", data.get("publicName") or data.get("displayName"))
            if got:
                print("  email matches .env:", got == email.strip().lower())
        elif resp.status_code != 200:
            print("  ", resp.text[:150].replace("\n", " "))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="convert only, no upload")
    parser.add_argument("--limit", type=int, default=0, help="only process N pages")
    parser.add_argument("--space", default="CD", help="Confluence space key (default CD)")
    parser.add_argument("--check", action="store_true", help="test the Confluence login and exit")
    args = parser.parse_args()

    if args.check:
        check_login()
        return

    files = sorted(DOCS_DIR.glob("*/*.md"))
    if not files:
        sys.exit(f"No Markdown files found in {DOCS_DIR}/. Run the download script first.")
    if args.limit:
        files = files[: args.limit]

    api = space_id = None
    if not args.dry_run:
        load_dotenv()
        site = os.getenv("CONFLUENCE_URL")
        email = os.getenv("ATLASSIAN_EMAIL")
        token = os.getenv("ATLASSIAN_API_KEY")
        missing = [n for n, v in [("CONFLUENCE_URL", site), ("ATLASSIAN_EMAIL", email),
                                  ("ATLASSIAN_API_KEY", token)] if not v]
        if missing:
            sys.exit(f"Missing in .env: {', '.join(missing)}")
        api = Confluence(site, email, token)
        space_id = api.space_id(args.space)
        print(f"Connected. Space '{args.space}' has id {space_id}.")

    results, used_titles = [], set()
    created = skipped = failed = 0
    label_warning_shown = False

    for i, path in enumerate(files, 1):
        slug = path.stem
        meta, body = read_page(path)
        title = build_title(meta, slug, used_titles)
        storage = md_to_storage(clean_markdown(body))
        print(f"[{i}/{len(files)}] {title}  ({len(storage)} chars)")
        if args.dry_run:
            continue

        existing = api.find_page(space_id, title)
        if existing:
            page, status = existing, "skipped (already exists)"
            skipped += 1
        else:
            resp = api.create_page(space_id, title, storage)
            if resp.status_code == 400:
                # Some page text confused the converter: store it as plain text instead.
                print("  WARN converter output rejected; retrying as plain text")
                resp = api.create_page(space_id, title, code_macro(clean_markdown(body)))
            if resp.status_code not in (200, 201):
                print(f"  FAILED {resp.status_code}: {resp.text[:300]}")
                failed += 1
                continue
            page, status = resp.json(), "created"
            created += 1
            labels = ["cassandra", "v" + meta["cassandra_version"].replace(".", "-"),
                      meta.get("section", "docs").replace("_", "-")]
            lab = api.add_labels(page["id"], labels)
            if lab.status_code not in (200, 201) and not label_warning_shown:
                print(f"  WARN could not add labels ({lab.status_code}); continuing without labels")
                label_warning_shown = True
            time.sleep(DELAY_SECONDS)

        results.append({
            "slug": slug,
            "title": title,
            "version": meta["cassandra_version"],
            "section": meta.get("section"),
            "page_id": page["id"],
            "url": api.page_url(page),
            "source_url": meta.get("source_url"),
            "status": status,
        })

    if args.dry_run:
        print(f"\nDry run complete: {len(files)} pages converted, nothing uploaded.")
        return

    RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)
    RESULT_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nDone. created={created} skipped={skipped} failed={failed}. "
          f"Details in {RESULT_FILE}")


if __name__ == "__main__":
    main()