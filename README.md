# ios-apps

Unsigned iOS builds of personal apps (Home, Zalo Viewer), served as a [SideStore](https://sidestore.io) source. SideStore signs them on the phone, refreshes them every 7 days and shows new versions under My Apps.

Add the source in SideStore → Sources → `+`:

```
https://raw.githubusercontent.com/nguyenhuy158/ios-apps/main/source.json
```

## Publish a new version

1. Bump the app version (semver) in its repo, then build unsigned: `pnpm tauri ios build --no-sign --target aarch64 --ci`.
2. `./publish.py path/to/App.ipa --notes "- what changed"` creates the GitHub release `<app>-v<version>` with those notes and adds the version to `source.json`; SideStore shows the notes under What's New and Version History.
3. Commit `source.json` through a PR.

The IPAs hold no tokens or data; each app signs in on the device.
