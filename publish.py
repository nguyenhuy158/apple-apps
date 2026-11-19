#!/usr/bin/env python3
import argparse
import datetime
import json
import pathlib
import plistlib
import subprocess
import sys
import zipfile

REPO = "nguyenhuy158/ios-apps"
SOURCE = pathlib.Path(__file__).with_name("source.json")
MIN_OS = "15.0"


def app_info(ipa: pathlib.Path) -> dict:
    with zipfile.ZipFile(ipa) as archive:
        plist = next(
            name for name in archive.namelist()
            if name.count("/") == 2 and name.endswith(".app/Info.plist")
        )
        return plistlib.loads(archive.read(plist))


def publish(ipa: pathlib.Path, notes: str) -> None:
    info = app_info(ipa)
    bundle_id = info["CFBundleIdentifier"]
    version = info["CFBundleShortVersionString"]
    build = info["CFBundleVersion"]
    tag = f"{bundle_id.rsplit('.', 1)[-1]}-v{version}"
    asset = f"{tag}.ipa"

    source = json.loads(SOURCE.read_text())
    app = next(item for item in source["apps"] if item["bundleIdentifier"] == bundle_id)
    if any(entry["version"] == version for entry in app["versions"]):
        sys.exit(f"{bundle_id} {version} is already published; bump the app version first")

    staged = ipa.with_name(asset)
    staged.write_bytes(ipa.read_bytes())
    subprocess.run(
        ["gh", "release", "create", tag, str(staged), "--repo", REPO,
         "--title", f"{info.get('CFBundleDisplayName', info['CFBundleName'])} {version}",
         "--notes", notes],
        check=True,
    )
    staged.unlink()

    app["versions"].insert(0, {
        "version": version,
        "buildVersion": build,
        "date": datetime.date.today().isoformat(),
        "localizedDescription": notes,
        "size": ipa.stat().st_size,
        "downloadURL": f"https://github.com/{REPO}/releases/download/{tag}/{asset}",
        "minOSVersion": MIN_OS,
    })
    SOURCE.write_text(json.dumps(source, indent=2, ensure_ascii=False) + "\n")
    print(f"published {tag}; commit source.json via a PR")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publish an unsigned IPA to the SideStore source")
    parser.add_argument("ipa", type=pathlib.Path)
    parser.add_argument("--notes", required=True, help="release notes shown under What's New")
    args = parser.parse_args()
    if not args.notes.strip():
        sys.exit("--notes must not be empty")
    publish(args.ipa, args.notes.strip())
