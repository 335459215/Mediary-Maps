#!/usr/bin/env python3
"""Build a redistributable, conservative actor_aliases.json from a pinned AVDC XML source.

Only aliases which identify exactly one record are emitted. Values are final display
names (zh_cn fallback zh_tw/jp), not intermediate canonical keys, so Mediary
can resolve them offline without a second lookup. This script does not upload data.
"""
import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

REVISION = "19977d177ea86e979c2a03212f7dde583dfebd83"
URL = f"https://raw.githubusercontent.com/catcat0921/AV_Data_Capture/{REVISION}/MappingTable/mapping_actor.xml"
MAX_BYTES = 2 * 1024 * 1024
from typing import Optional


def clean(value: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--source", default=URL)
    args = ap.parse_args()

    with urllib.request.urlopen(args.source, timeout=30) as response:
        payload = response.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("source exceeds size limit")
    root = ET.fromstring(payload)
    candidates = defaultdict(set)
    for node in root.findall("a"):
        display = clean(node.get("zh_cn")) or clean(node.get("zh_tw")) or clean(node.get("jp"))
        if not display:
            continue
        aliases = [node.get("zh_cn"), node.get("zh_tw"), node.get("jp")]
        aliases.extend((node.get("keyword") or "").strip(",").split(","))
        for alias in aliases:
            alias = clean(alias)
            if alias:
                candidates[alias.casefold()].add(display)

    mapping = {}
    for folded, displays in candidates.items():
        if len(displays) == 1:
            # Keep original normalized alias from the first matching record for JSON readability.
            display = next(iter(displays))
            mapping[folded] = display
    # Runtime lookup is case-insensitive, so case-folded keys retain correct behavior.
    document = {
        "schemaVersion": 1,
        "source": "av_data_capture",
        "sourceRevision": REVISION,
        "license": "GPL-3.0-only",
        "generatedBy": "scripts/build_actor_aliases.py",
        "warning": "Community aliases only; ambiguous aliases are excluded. Review licensing before redistributing.",
        "map": dict(sorted(mapping.items())),
    }
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote={args.output} aliases={len(mapping)}")


if __name__ == "__main__":
    main()
