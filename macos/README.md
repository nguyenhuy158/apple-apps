# macOS updater manifests

One `latest-<app>.json` per app, consumed by [`tauri-plugin-updater`](https://v2.tauri.app/plugin/updater/).
Releases (the signed `.app.tar.gz` bundles) live in this repo's own
[Releases](https://github.com/nguyenhuy158/apple-apps/releases), same as the
iOS `.ipa`s — `apple-apps` is the shared host for both platforms.

## Opt an app in (one-time)

1. Add the updater plugin:
   ```sh
   pnpm add @tauri-apps/plugin-updater @tauri-apps/plugin-process
   cargo add tauri-plugin-updater tauri-plugin-process --manifest-path src-tauri/Cargo.toml
   ```
2. In `src-tauri/tauri.conf.json`:
   ```json
   {
     "plugins": {
       "updater": {
         "pubkey": "<contents of macos/pubkey.txt>",
         "endpoints": [
           "https://raw.githubusercontent.com/nguyenhuy158/apple-apps/main/macos/latest-<app>.json"
         ]
       }
     }
   }
   ```
3. Register the plugin in `src-tauri/src/lib.rs`:
   ```rust
   .plugin(tauri_plugin_updater::Builder::new().build())
   .plugin(tauri_plugin_process::init())
   ```
4. Add `"updater:default"` and `"process:default"` to
   `src-tauri/capabilities/default.json`'s `permissions`.
5. Check for updates from the frontend (e.g. on launch):
   ```ts
   import { check } from "@tauri-apps/plugin-updater";
   import { relaunch } from "@tauri-apps/plugin-process";

   const update = await check();
   if (update) {
     await update.downloadAndInstall();
     await relaunch();
   }
   ```
6. Create `macos/latest-<app>.json` here (first publish does this for you,
   see below) and add it to this repo.

## Publish a new version

```sh
# builds + signs locally; needs the private key (ask huyntq, stored in
# Bitwarden Secrets as APPLE_APPS_TAURI_UPDATER_PRIVATE_KEY, local copy at
# ~/.config/tauri-updater/apple-apps.key)
export TAURI_SIGNING_PRIVATE_KEY_PATH=~/.config/tauri-updater/apple-apps.key
pnpm tauri build

./publish-macos.py <app> <version> src-tauri/target/release/bundle/macos/App.app.tar.gz \
  --notes "- what changed"
```

Commit the updated `latest-<app>.json` through a PR.

## Signing key

Public key is in [`pubkey.txt`](pubkey.txt) (safe to read/commit). The
private key is **not** in this repo — it lives in Bitwarden Secrets
(`APPLE_APPS_TAURI_UPDATER_PRIVATE_KEY`, project `admin`) and as a local file
at `~/.config/tauri-updater/apple-apps.key`. Losing it means every
already-shipped app can never verify a future update again — re-signing with
a new key requires a manual reinstall on every machine.
