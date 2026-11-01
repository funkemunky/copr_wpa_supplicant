# wpa_supplicant 2.12 for Fedora 44

This repository packages `wpa_supplicant` `1:2.12-1` using the upstream Fedora spec and patchset, targeting **Fedora 44** (`fedora-44-*`) chroots on [Fedora COPR](https://copr.fedorainfracloud.org/) via `rpkg`.

## Building on Fedora COPR (`rpkg`)

1. Ensure your COPR package is configured with:
   - **Source Type**: SCM (Git)
   - **How to build SRPM**: `rpkg`
   - **Enable internet access during build**: **Checked** *(so `rpkg` downloads `Source0`)*

Or via `copr-cli`:

```bash
copr-cli create wpa_supplicant --chroot fedora-44-x86_64
copr-cli add-package-scm wpa_supplicant \
  --name wpa_supplicant \
  --clone-url <your-git-repo-url> \
  --method rpkg \
  --enable-net on
copr-cli build-package wpa_supplicant --name wpa_supplicant
```

## Local Build Testing

```bash
spectool -g wpa_supplicant.spec
rpkg local
```
