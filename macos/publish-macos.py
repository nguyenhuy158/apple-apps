#!/usr/bin/env python3
"""Publish a signed Tauri macOS update bundle and update its latest-<app>.json.

Usage:
    ./publish-macos.py <app-name> <version> path/to/App.app.tar.gz --notes "- what changed"

Expects `path/to/App.app.tar.gz.sig` next to the bundle (written by
`cargo tauri build` when TAURI_SIGNING_PRIVATE_KEY[_PATH] is set).
"""

import argparse
import datetime
import json
import pathlib
import platform
import subprocess
import sys

REPO = "nguyenhuy158/apple-apps"
MACOS_DIR = pathlib.Path(__file__).parent


def publish(
    app: str, version: str, bundle: pathlib.Path, notes: str, target: str
) -> None:
    sig_path = bundle.with_suffix(bundle.suffix + ".sig")
    if not sig_path.exists():
        sys.exit(f"missing signature file: {sig_path}")
    signature = sig_path.read_text().strip()

    manifest_path = MACOS_DIR / f"latest-{app}.json"
    manifest = (
        json.loads(manifest_path.read_text())
        if manifest_path.exists()
        else {"version": "", "notes": "", "pub_date": "", "platforms": {}}
    )
    if manifest.get("version") == version and target in manifest.get("platforms", {}):
        sys.exit(
            f"{app} {version} ({target}) is already published; bump the version first"
        )

    tag = f"{app}-macos-v{version}"
    asset = f"{app}-{target}-v{version}.app.tar.gz"
    staged = bundle.with_name(asset)
    staged.write_bytes(bundle.read_bytes())

    existing_tags = subprocess.run(
        [
            "gh",
            "release",
            "list",
            "--repo",
            REPO,
            "--json",
            "tagName",
            "-q",
            ".[].tagName",
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    if tag not in existing_tags:
        subprocess.run(
            [
                "gh",
                "release",
                "create",
                tag,
                "--repo",
                REPO,
                "--title",
                f"{app} v{version} (macOS)",
                "--notes",
                notes,
            ],
            check=True,
        )
    subprocess.run(
        ["gh", "release", "upload", tag, str(staged), "--repo", REPO, "--clobber"],
        check=True,
    )
    staged.unlink()

    url = f"https://github.com/{REPO}/releases/download/{tag}/{asset}"
    manifest["version"] = version
    manifest["notes"] = notes
    manifest["pub_date"] = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    manifest.setdefault("platforms", {})[target] = {"signature": signature, "url": url}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"published {app} {version} ({target}) -> {url}")
    print(f"updated {manifest_path}; commit it through a PR")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "app", help="app id, e.g. nix-gui (manifest: latest-<app>.json)"
    )
    parser.add_argument("version", help="semver, e.g. 0.1.0")
    parser.add_argument("bundle", type=pathlib.Path, help="path to App.app.tar.gz")
    parser.add_argument("--notes", required=True, help="What's New text")
    parser.add_argument(
        "--target",
        default="darwin-aarch64" if platform.machine() == "arm64" else "darwin-x86_64",
        help="Tauri updater platform key (default: current machine's arch)",
    )
    args = parser.parse_args()
    publish(args.app, args.version, args.bundle, args.notes, args.target)
