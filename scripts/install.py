#!/usr/bin/env python3
"""Install selected AI Dev Assistant features into another repository."""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest" / "features.json"

def load_manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as handle:
        return json.load(handle)

def main() -> int:
    data = load_manifest()
    features = data["features"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", help="Destination project directory")
    parser.add_argument("--features", nargs="+", choices=sorted(features), help="Feature IDs to install")
    parser.add_argument("--all", action="store_true", help="Install all features")
    parser.add_argument("--list", action="store_true", help="List feature IDs and descriptions")
    parser.add_argument("--dry-run", action="store_true", help="Show copies without writing")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing destination files")
    args = parser.parse_args()

    if args.list:
        for name, feature in features.items():
            print(f"{name:26} {feature['description']}")
        return 0
    if not args.target:
        parser.error("--target is required unless --list is used")
    if not args.all and not args.features:
        parser.error("Choose --all or provide one or more --features")

    selected = list(features) if args.all else args.features
    target = Path(args.target).expanduser().resolve()
    if not target.exists() or not target.is_dir():
        parser.error(f"Target directory must already exist: {target}")
    if target == ROOT or ROOT in target.parents:
        parser.error("Target cannot be the toolkit repository itself or one of its subdirectories")

    copied = skipped = 0
    for feature_name in selected:
        feature = features[feature_name]
        print(f"\n[{feature_name}] {feature['description']}")
        for entry in feature["files"]:
            source = (ROOT / entry["source"]).resolve()
            destination = (target / entry["destination"]).resolve()
            if ROOT not in source.parents and source != ROOT:
                print(f"  ERROR: invalid source path in manifest: {entry['source']}", file=sys.stderr)
                return 2
            if entry["kind"] == "directory":
                if not source.is_dir():
                    print(f"  ERROR: source directory missing: {source}", file=sys.stderr)
                    return 2
                source_files = list(source.rglob("*"))
                for source_file in source_files:
                    if not source_file.is_file():
                        continue
                    if "__pycache__" in source_file.parts or source_file.suffix in {".pyc", ".pyo"} or source_file.name == ".DS_Store":
                        continue
                    relative = source_file.relative_to(source)
                    dest_file = destination / relative
                    if dest_file.exists() and not args.overwrite:
                        print(f"  SKIP existing: {dest_file.relative_to(target)}")
                        skipped += 1
                        continue
                    print(f"  {'WOULD COPY' if args.dry_run else 'COPY'}: {entry['source']}/{relative} -> {dest_file.relative_to(target)}")
                    if not args.dry_run:
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, dest_file)
                    copied += 1
            else:
                if not source.is_file():
                    print(f"  ERROR: source file missing: {source}", file=sys.stderr)
                    return 2
                if destination.exists() and not args.overwrite:
                    print(f"  SKIP existing: {entry['destination']}")
                    skipped += 1
                    continue
                print(f"  {'WOULD COPY' if args.dry_run else 'COPY'}: {entry['source']} -> {entry['destination']}")
                if not args.dry_run:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
                copied += 1
    print(f"\nCompleted. {'Would copy' if args.dry_run else 'Copied'}: {copied}; skipped: {skipped}.")
    if not args.dry_run:
        print("Review the changed files and commit them through your normal code-review process.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
