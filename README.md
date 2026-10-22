# Dataplicity Files downloads

Signed Windows installers and update metadata for Dataplicity Files. Application source code is maintained separately.

## Windows

Download the installer for your PC from [Releases](https://github.com/wildfoundry/dataplicity-files-releases/releases). Choose **x64** for Intel or AMD PCs and **ARM64** for Windows on Arm. Windows should identify the verified publisher as **Wildfoundry Ltd**.

Run the installer, open **Dataplicity Files** from Start, and sign in using your usual Dataplicity account. Shared files appear in the **Dataplicity Files** folder in File Explorer (`%USERPROFILE%\dataplicity`). Closing the status window leaves Files running in the notification area; choose **Quit Files** from its tray menu to stop it.

Online-only files download when opened. Use File Explorer’s **Always keep on this device** option for files you need without a connection. Local edits are uploaded when access and connectivity are available. Copies that need review are surfaced in the Files window.

## Release channels

**Stable** installers connect to the production Dataplicity service. Availability follows your organisation’s Files rollout and access settings.

**Canary** prereleases connect to internal staging and are used for acceptance testing. A prerelease is not a stable release. Update feeds are signed independently of the installers; Windows also verifies the installer’s publisher and Files product identity before installation.

This repository contains distribution artifacts and their checksums. It contains no account credentials or user file data.
