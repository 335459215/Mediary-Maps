#!/usr/bin/env python3
"""Build Mediary-Maps artifacts from the three li-peifeng upstream repositories.

Sources (pinned by URL, fetched on demand):
  1. Jav-Actors-Mapping  actor-mapping.xml  -> enrich actor_map.json / actor_aliases.json
  2. gfriends            Filetree.json      -> actor_avatars.json  (avatar index)
  3. Jalbum              Filetree.json      -> actor_photoalbums.json (photo album index)

Rules:
  - Existing curated entries in actor_map.json / actor_aliases.json always win;
    upstream only fills the gaps (never overwrites a human-verified mapping).
  - An upstream alias that resolves to more than one actor is discarded (ambiguous).
  - Avatars/albums store RELATIVE paths only; the URL template lives in the file so
    the plugin composes the final HTTPS raw URL without redistributing any bytes.
  - Image/album indexes include every upstream name (Japanese romaji aliases too);
    the plugin resolves via ResolveActorIdentity first, then falls back here.

This script does not upload anything; review the diff and push manually.
"""
import argparse
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

MAPPING_URL = "https://raw.githubusercontent.com/li-peifeng/Jav-Actors-Mapping/main/actor-mapping.xml"
GFRIENDS_URL = "https://raw.githubusercontent.com/li-peifeng/gfriends/main/Filetree.json"
JALBUM_URL = "https://raw.githubusercontent.com/li-peifeng/Jalbum/main/Filetree.json"

GFRIENDS_TEMPLATE = "https://raw.githubusercontent.com/li-peifeng/gfriends/main/Content/{path}"
JALBUM_TEMPLATE = "https://raw.githubusercontent.com/li-peifeng/Jalbum/main/Content/{folder}/{actor}/{file}"

MAX_BYTES = 64 * 1024 * 1024


def clean(value):
    return re.sub(r"\s+", " ", (value or "").strip())


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = response.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError(f"{url} exceeds {MAX_BYTES} bytes")
    return payload


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def build_mapping(existing_map_path, existing_alias_path):
    """Enrich actor_map/actor_aliases from Jav-Actors-Mapping. Returns (actor_map_doc, alias_doc, stats)."""
    actor_doc = json.loads(existing_map_path.read_text(encoding="utf-8"))
    alias_doc = json.loads(existing_alias_path.read_text(encoding="utf-8"))
    actor_map = actor_doc.setdefault("map", {})
    alias_map = alias_doc.setdefault("map", {})

    root = ET.fromstring(fetch(MAPPING_URL))

    # zh_cn -> set(keywords) ; count alias usage to drop ambiguous ones
    display_keywords = {}
    for node in root.iter("a"):
        zh = clean(node.get("zh_cn")) or clean(node.get("zh_tw")) or clean(node.get("jp"))
        if not zh:
            continue
        keywords = [clean(k) for k in (node.get("keyword") or "").split(",")]
        keywords.append(clean(node.get("jp")))
        keywords = [k for k in keywords if k]
        display_keywords.setdefault(zh, set()).update(keywords)

    alias_owner = defaultdict(set)
    for zh, keywords in display_keywords.items():
        for keyword in keywords:
            alias_owner[keyword].add(zh)

    added_actor = added_alias = 0
    for zh, keywords in display_keywords.items():
        for keyword in keywords:
            if len(alias_owner[keyword]) != 1:
                continue  # ambiguous alias, discard
            # actor_map: original name -> Chinese display name (curated entries win)
            if keyword not in actor_map and keyword != zh and keyword not in alias_map:
                actor_map[keyword] = zh
                added_actor += 1
            # actor_aliases: alias -> display name (curated entries win)
            if keyword != zh and keyword not in alias_map and keyword not in actor_map:
                alias_map[keyword] = zh
                added_alias += 1

    actor_doc["version"] = today()
    alias_doc["version"] = today()
    stats = {"canonical": len(display_keywords), "added_actor_map": added_actor,
             "added_aliases": added_alias, "total_actor_map": len(actor_map),
             "total_aliases": len(alias_map)}
    return actor_doc, alias_doc, stats


def build_avatars():
    payload = json.loads(fetch(GFRIENDS_URL))
    avatars = {}
    for folder, files in payload.get("Content", {}).items():
        if not isinstance(files, dict) or folder == "_Symbols":
            continue
        for name, value in files.items():
            actual = str(value).split("?")[0].strip()
            key = clean(name).rsplit(".", 1)[0].strip()
            if not key or not actual:
                continue
            # first folder wins; duplicates across studios are common and equivalent
            if key not in avatars:
                avatars[key] = f"{folder}/{urllib.parse.quote(actual)}"
    return {
        "schemaVersion": 1,
        "updatedAt": today(),
        "source": "li-peifeng/gfriends (avatar index; no image bytes redistributed)",
        "urlTemplate": GFRIENDS_TEMPLATE,
        "avatars": avatars,
    }


def build_photoalbums():
    payload = json.loads(fetch(JALBUM_URL))
    albums = {}
    for folder, performers in payload.get("Content", {}).items():
        if not isinstance(performers, dict):
            continue
        for performer, files in performers.items():
            if not isinstance(files, dict) or not files:
                continue
            name = clean(performer)
            if not name:
                continue
            entry = albums.setdefault(name, {"d": folder, "f": []})
            entry["f"].extend(sorted(files.keys()))
    return {
        "schemaVersion": 1,
        "updatedAt": today(),
        "source": "li-peifeng/Jalbum (photo album index; no image bytes redistributed)",
        "urlTemplate": JALBUM_TEMPLATE,
        "albums": albums,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, type=Path, help="Mediary-Maps repo root")
    ap.add_argument("--skip-mapping", action="store_true")
    args = ap.parse_args()
    repo = args.repo

    if not args.skip_mapping:
        actor_doc, alias_doc, stats = build_mapping(repo / "actor_map.json", repo / "actor_aliases.json")
        (repo / "actor_map.json").write_text(
            json.dumps(actor_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (repo / "actor_aliases.json").write_text(
            json.dumps(alias_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("mapping:", json.dumps(stats, ensure_ascii=False))

    avatars = build_avatars()
    (repo / "actor_avatars.json").write_text(
        json.dumps(avatars, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("avatars:", len(avatars["avatars"]),
          "MB:", round((repo / "actor_avatars.json").stat().st_size / 1e6, 2))

    albums = build_photoalbums()
    (repo / "actor_photoalbums.json").write_text(
        json.dumps(albums, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("albums:", len(albums["albums"]),
          "MB:", round((repo / "actor_photoalbums.json").stat().st_size / 1e6, 2))


if __name__ == "__main__":
    import urllib.parse
    main()
