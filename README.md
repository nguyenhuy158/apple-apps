# apple-apps

Unsigned builds of personal apps, served two ways:

- **iOS** (`source.json`, `icons/`, `publish.py`) — [SideStore](https://sidestore.io)
  source. SideStore signs IPAs on the phone, refreshes every 7 days and shows
  new versions under My Apps.
- **macOS** (`macos/`) — [Tauri updater](https://v2.tauri.app/plugin/updater/)
  manifests. Each desktop app checks its `macos/latest-<app>.json` on launch
  and self-updates (signed, no manual download).

## iOS: add the source

SideStore → Sources → `+`:

```
https://raw.githubusercontent.com/nguyenhuy158/apple-apps/main/source.json
```

(Renamed from `ios-apps`; the old URL still 200s via GitHub's redirect, but
use this one for new installs.)

### Publish a new iOS version

1. Bump the app version (semver) in its repo, then build unsigned: `pnpm tauri ios build --no-sign --target aarch64 --ci`.
2. `./publish.py path/to/App.ipa --notes "- what changed"` creates the GitHub release `<app>-v<version>` with those notes and adds the version to `source.json`; SideStore shows the notes under What's New and Version History.
3. Commit `source.json` through a PR.

The IPAs hold no tokens or data; each app signs in on the device.

## macOS: how an app opts in

See [`macos/README.md`](macos/README.md).
