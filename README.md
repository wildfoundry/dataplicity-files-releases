# Dataplicity Files downloads

Signed macOS and Windows installers and update metadata for Dataplicity Files.
Application source code is maintained separately; customers need no GitHub account
or token to download a published installer.

As of 27 October 2026, this repository has qualification prereleases and no
general stable release. The `/releases/latest/download/` URLs below become usable
only after an approved stable release publishes all three installers and aliases.
Do not substitute a qualification build for a stable download.

## macOS

Files supports Apple Silicon Macs running macOS 14 or newer. The distribution
format is a Developer ID signed, notarized and stapled DMG. Open it, drag
**Dataplicity Files** to Applications, open the installed app and sign in. Files
appears under Locations in Finder. Intel Mac and PKG downloads are not part of
the supported Files release contract.

## Windows

Files supports Windows 11. Once a stable release is available, choose **x64** for
Intel or AMD PCs and **ARM64** for Windows on Arm from
[Releases](https://github.com/wildfoundry/dataplicity-files-releases/releases).
Windows should identify the verified publisher as **Wildfoundry Ltd**.

Run the installer, open **Dataplicity Files** from Start, and sign in using your usual Dataplicity account. Shared files appear in the **Dataplicity Files** folder in File Explorer (`%USERPROFILE%\dataplicity`). Closing the status window leaves Files running in the notification area; choose **Quit Files** from its tray menu to stop it.

Online-only files download when opened. Use File Explorer’s **Always keep on this device** option for files you need without a connection. Local edits are uploaded when access and connectivity are available. Copies that need review are surfaced in the Files window.

## Release channels

**Stable** installers connect to the production Dataplicity service. Availability follows your organisation’s Files rollout and access settings.

**Canary** prereleases connect to internal staging and are used for acceptance testing. A prerelease is not a stable release. Update feeds are signed independently of the installers; Windows also verifies the installer’s publisher and Files product identity before installation.

This repository contains distribution artifacts and their checksums. It contains no account credentials or user file data.

## Public download URLs

The public website uses these exact aliases within each stable release:

| Platform | Latest stable URL |
| --- | --- |
| macOS Apple Silicon | `https://github.com/wildfoundry/dataplicity-files-releases/releases/latest/download/Dataplicity-Files-macos-arm64.dmg` |
| Windows x64 | `https://github.com/wildfoundry/dataplicity-files-releases/releases/latest/download/dataplicity-files-windows-x64.msi` |
| Windows ARM64 | `https://github.com/wildfoundry/dataplicity-files-releases/releases/latest/download/dataplicity-files-windows-arm64.msi` |

Each alias has a matching `.sha256` asset. Its bytes must equal the versioned
installer in the same release. Pin deployments and recovery downloads to:

```text
https://github.com/wildfoundry/dataplicity-files-releases/releases/download/files-stable-vX.Y.Z/Dataplicity-Files-X.Y.Z-macos-arm64.dmg
https://github.com/wildfoundry/dataplicity-files-releases/releases/download/files-stable-vX.Y.Z/dataplicity-files-X.Y.Z-windows-x64.msi
https://github.com/wildfoundry/dataplicity-files-releases/releases/download/files-stable-vX.Y.Z/dataplicity-files-X.Y.Z-windows-arm64.msi
```

`X.Y.Z` is a placeholder for an actually published stable version. Retain old
release tags and versioned assets; never overwrite an installer at a published
version URL. Qualification and canary releases stay prereleases and must not
become GitHub's latest stable release. Do not link customers to private source
repositories or expiring Actions artifact downloads.

## Publishing and verification

The separately maintained producer must supply production payload audits, all
three stable aliases, checksums, explicit latest publication, and signed
Windows/Sparkle update feeds. Run that producer only after its release acceptance
and review gates are satisfied.
The public repository needs only artifacts, license and distribution documentation.

Signing remains in the producer's `release-signing` environment: Azure Artifact
Signing for Windows, Developer ID plus notarization/stapling for macOS, and
separate signed update metadata. Use a narrowly scoped publisher credential with
Contents write access to this repository. Never put tokens or signing keys in
clients or download URLs. Checksums verify bytes; platform signatures establish
publisher identity. The check below does not replace native signature validation.

Run the **Check public Files downloads** workflow manually after an authorized
stable publication. It downloads through the same anonymous URLs as customers,
hashes alias and versioned installers, and rejects incomplete or prerelease sets.
Pull requests run only the offline contract tests; they do not require a stable
release to exist and cannot publish anything.

```sh
python3 scripts/check_downloads.py                 # metadata, checksums and reachability
python3 scripts/check_downloads.py --verify-bytes  # also download and hash installer bytes
python3 scripts/check_downloads.py --tag files-stable-vX.Y.Z --verify-bytes
```

The script currently fails with "No public stable release exists". That is the
expected distribution blocker, even when signing/build workflows are green.

## Rollback and recovery

For website download rollback, an authorized maintainer may move GitHub's latest
designation to a previous verified stable release with the complete alias set.
Verify its pinned URLs first, then rerun the check against latest. Leave all
versioned assets intact. Changing latest does not change installed clients'
signed update feeds.

Windows uses a monotonic signed update sequence and rejects replayed older
metadata. macOS uses Sparkle version/signature checks. Do not lower a sequence,
replay an old feed, or relabel qualification packages to force an automatic
downgrade. The normal fleet recovery is a new, higher version containing the
reviewed known-good code, freshly signed and qualified for production, followed
by authorized feed publication. Manual installation of an older package needs
platform-specific downgrade and data-compatibility qualification; retaining a
download alone does not prove downgrade safety. A failed Windows MSI transaction
has its own in-transaction rollback, distinct from rolling back an installed fleet.
