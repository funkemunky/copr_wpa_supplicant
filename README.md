# wpa_supplicant (Arch Linux Config & Patchset for Fedora 44)

This repository packages the latest `wpa_supplicant` (`1:2.12-2`) using the [Arch Linux `wpa_supplicant` build configuration and patchset](https://gitlab.archlinux.org/archlinux/packaging/packages/wpa_supplicant), adapted for Fedora 44 (`fedora-44-*`) chroots on [Fedora COPR](https://copr.fedorainfracloud.org/) via `rpkg`.

## Features

- **Upstream Version**: `wpa_supplicant` 2.12 (`Epoch: 1` for seamless upgrades over Fedora 44's `1:2.11-*`).
- **Arch Build Config (`wpa_supplicant_config`)**: Includes WEXT, nl80211, MACsec, EAP-SIM/AKA/FAST/TEAP/PEAP/TLS/TTLS/PWD/PAX/SAKE/GPSK/TNC/IKEv2/EKE, PC/SC smartcard support, SAE/WPA3, OCV, Wi-Fi 6/7 (HE/EHT), DPP/DPP2/DPP3, NAN, and `DEFAULT@SECLEVEL=1` TLS cipher compatibility.
- **Arch Patchset (`0001`–`0008`)**:
  - `0001-Enable-TLSv1.0-by-default.patch`: More permissive TLS fallback for legacy enterprise networks.
  - `0002-Disable-Werror-for-eapol_test.patch`: Prevents compiler warning flags from breaking `eapol_test`.
  - `0003-Allow-legacy-renegotiation-to-fix-PEAP-issues-with-s.patch`: Enables `SSL_OP_LEGACY_SERVER_CONNECT` for enterprise PEAP servers without RFC 5746 secure renegotiation.
  - `0004-Tweak-D-Bus-systemd-service-activation-configuration.patch`: Enables syslog and control socket (`/run/wpa_supplicant`) on D-Bus activation.
  - `0005-Add-IgnoreOnIsolate-yes-to-keep-wpa-supplicant-runni.patch`: Adds `IgnoreOnIsolate=true` to systemd unit.
  - `0006-Add-reload-support-to-the-systemd-unit-files.patch`: Adds `ExecReload=/bin/kill -HUP $MAINPID` to systemd units.
  - `0007-nl80211-add-extra-ies-only-if-allowed-by-driver.patch`: Fixes scanning with Broadcom (`broadcom-wl`) drivers that do not support extra scan IEs.
  - `0008-Revert-Mark-authorization-completed-on-driver-indica.patch`: Fixes authentication regressions with Broadcom `brcmfmac` fullmac devices.
- **Fedora Integration**:
  - Preserves Fedora paths (`/usr/sbin/wpa_supplicant`, `/etc/wpa_supplicant/wpa_supplicant.conf`, `/etc/sysconfig/wpa_supplicant`, `/etc/logrotate.d/wpa_supplicant`).
  - Ships both Fedora's main `wpa_supplicant.service` and upstream interface-templated units (`wpa_supplicant@.service`, `wpa_supplicant-nl80211@.service`, `wpa_supplicant-wired@.service`).
  - Includes the `wpa_supplicant-gui` subpackage (`wpa_gui` built against Qt6).

## Building on Fedora COPR (`rpkg`)

1. Create a new COPR project targeting **Fedora 44** (`fedora-44-x86_64`, `fedora-44-aarch64`).
2. Add a package using the **SCM** source type:
   - **Clone URL**: `<your-git-repo-url>`
   - **How to build SRPM**: `rpkg`
   - **Enable internet access during build**: **Checked** *(required so `rpkg` fetches `Source0` from `https://w1.fi/releases/wpa_supplicant-2.12.tar.gz`)*

Or via `copr-cli`:

```bash
copr-cli create wpa_supplicant-arch --chroot fedora-44-x86_64
copr-cli add-package-scm wpa_supplicant-arch \
  --name wpa_supplicant \
  --clone-url <your-git-repo-url> \
  --method rpkg \
  --enable-net on
copr-cli build-package wpa_supplicant-arch --name wpa_supplicant
```

## Local Build Testing

```bash
spectool -g wpa_supplicant.spec
rpkg srpm
mock -r fedora-44-x86_64 *.src.rpm
```
