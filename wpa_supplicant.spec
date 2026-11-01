%global _hardened_build 1
%if 0%{?fedora}
%bcond_without gui
%else
%bcond_with gui
%endif

Summary: WPA/WPA2/WPA3/IEEE 802.1X Supplicant
Name: wpa_supplicant
Epoch: 1
Version: 2.12
Release: 2%{?dist}
License: BSD-3-Clause
URL: https://w1.fi/wpa_supplicant/

Source0: https://w1.fi/releases/%{name}-%{version}.tar.gz
Source1: wpa_supplicant.conf
Source2: wpa_supplicant.service
Source3: wpa_supplicant.sysconfig
Source4: wpa_supplicant.logrotate
# Arch Linux wpa_supplicant build configuration
Source5: wpa_supplicant_config

# Arch Linux patchset:
# More permissive TLS fallback
Patch1: 0001-Enable-TLSv1.0-by-default.patch
# https://salsa.debian.org/debian/wpa/-/commit/13e1d28e4f987a220c546df94df86bb9b2371874
Patch2: 0002-Disable-Werror-for-eapol_test.patch
# https://lists.infradead.org/pipermail/hostap/2022-May/040511.html
# https://bugs.archlinux.org/task/76474
Patch3: 0003-Allow-legacy-renegotiation-to-fix-PEAP-issues-with-s.patch
# Unit improvements from Ubuntu
Patch4: 0004-Tweak-D-Bus-systemd-service-activation-configuration.patch
Patch5: 0005-Add-IgnoreOnIsolate-yes-to-keep-wpa-supplicant-runni.patch
# More unit improvements from Debian
Patch6: 0006-Add-reload-support-to-the-systemd-unit-files.patch
# https://lists.infradead.org/pipermail/hostap/2022-January/040178.html
Patch7: 0007-nl80211-add-extra-ies-only-if-allowed-by-driver.patch
# Fix authentication regressions with Broadcom brcmfmac fullmac devices
Patch8: 0008-Revert-Mark-authorization-completed-on-driver-indica.patch

# Allow overriding Qt build tool names for wpa_gui
Patch9: wpa_supplicant-gui-qt4.patch

%if %with gui
BuildRequires: qt6-qtbase-devel
BuildRequires: qt6-linguist
BuildRequires: gcc-c++
%endif
BuildRequires: openssl-devel
%if 0%{?fedora} >= 41 && 0%{?fedora} < 45
BuildRequires: openssl-devel-engine
%endif
BuildRequires: readline-devel
BuildRequires: dbus-devel
BuildRequires: libnl3-devel
BuildRequires: pcsc-lite-devel
BuildRequires: systemd-units
BuildRequires: systemd-rpm-macros
BuildRequires: docbook-utils
BuildRequires: gcc
BuildRequires: make

Requires(post): systemd-sysv
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%if 0%{?rhel} >= 10 || 0%{?fedora} >= 45
Requires: pkcs11-provider >= 1.0
%endif

Obsoletes: libeap < %{epoch}:%{version}-%{release}
Obsoletes: libeap-devel < %{epoch}:%{version}-%{release}

%description
wpa_supplicant is a WPA Supplicant for Linux, BSD and Windows with support
for WPA, WPA2 (IEEE 802.11i / RSN), and WPA3. Supplicant is the IEEE 802.1X/WPA
component that is used in the client stations. It implements key negotiation
with a WPA Authenticator and it controls the roaming and IEEE 802.11
authentication/association of the wlan driver.

This package is built with the Arch Linux wpa_supplicant configuration and
patchset, packaged for Fedora integration.

%if %with gui
%package gui
Summary: Graphical User Interface for %{name}

%description gui
Graphical User Interface for wpa_supplicant written using Qt.
%endif


%prep
%autosetup -p1 -n %{name}-%{version}


%build
pushd wpa_supplicant
  cp %{SOURCE5} .config
  export CFLAGS="${CFLAGS:-%optflags} -fPIE -DPIE"
%if 0%{?rhel} >= 10 || 0%{?fedora} >= 45
  export CFLAGS="$CFLAGS -DOPENSSL_NO_ENGINE"
%endif
  export CXXFLAGS="${CXXFLAGS:-%optflags} -fPIE -DPIE"
  export LDFLAGS="${LDFLAGS:-%optflags} -pie -Wl,-z,now"
  export BINDIR="%{_sbindir}"
  export LIBDIR="%{_libdir}"
  make %{_smp_mflags} V=1
%if %with gui
  make %{_smp_mflags} V=1 wpa_gui-qt4 QTDIR=%{_libdir}/qt6 \
     QMAKE='%{qmake_qt6}' LRELEASE='%{_qt6_bindir}/lrelease'
%endif
  make eapol_test V=1
  make -C doc/docbook man V=1
%if !%with gui
  rm -f doc/docbook/wpa_gui.8
%endif
popd


%install
# config
install -D -m 0600 %{SOURCE1} %{buildroot}/%{_sysconfdir}/wpa_supplicant/wpa_supplicant.conf

# systemd unit files & init config
install -D -m 0644 %{SOURCE2} %{buildroot}/%{_unitdir}/wpa_supplicant.service
install -D -m 0644 wpa_supplicant/systemd/wpa_supplicant@.service %{buildroot}/%{_unitdir}/wpa_supplicant@.service
install -D -m 0644 wpa_supplicant/systemd/wpa_supplicant-nl80211@.service %{buildroot}/%{_unitdir}/wpa_supplicant-nl80211@.service
install -D -m 0644 wpa_supplicant/systemd/wpa_supplicant-wired@.service %{buildroot}/%{_unitdir}/wpa_supplicant-wired@.service
install -D -m 0644 %{SOURCE3} %{buildroot}/%{_sysconfdir}/sysconfig/wpa_supplicant
install -D -m 0644 %{SOURCE4} %{buildroot}/%{_sysconfdir}/logrotate.d/wpa_supplicant

# binaries
install -d %{buildroot}/%{_sbindir}
install -m 0755 wpa_supplicant/wpa_passphrase %{buildroot}/%{_sbindir}
install -m 0755 wpa_supplicant/wpa_cli %{buildroot}/%{_sbindir}
install -m 0755 wpa_supplicant/wpa_supplicant %{buildroot}/%{_sbindir}
install -m 0755 wpa_supplicant/eapol_test %{buildroot}/%{_sbindir}
install -D -m 0644 wpa_supplicant/dbus/dbus-wpa_supplicant.conf \
  %{buildroot}/%{_datadir}/dbus-1/system.d/wpa_supplicant.conf
install -D -m 0644 wpa_supplicant/dbus/fi.w1.wpa_supplicant1.service \
  %{buildroot}/%{_datadir}/dbus-1/system-services/fi.w1.wpa_supplicant1.service

%if %with gui
# gui
install -d %{buildroot}/%{_bindir}
install -m 0755 wpa_supplicant/wpa_gui-qt4/wpa_gui %{buildroot}/%{_bindir}
%endif

# man pages
install -d %{buildroot}%{_mandir}/man{5,8}
install -m 0644 wpa_supplicant/doc/docbook/*.8 %{buildroot}%{_mandir}/man8
install -m 0644 wpa_supplicant/doc/docbook/*.5 %{buildroot}%{_mandir}/man5

# some cleanup in docs and examples
rm -f wpa_supplicant/doc/.cvsignore
rm -rf wpa_supplicant/doc/docbook
chmod -R 0644 wpa_supplicant/examples/*.py


%post
%systemd_post wpa_supplicant.service


%preun
%systemd_preun wpa_supplicant.service


%postun
%systemd_postun_with_restart wpa_supplicant.service


%files
%config(noreplace) %{_sysconfdir}/wpa_supplicant/wpa_supplicant.conf
%config(noreplace) %{_sysconfdir}/sysconfig/wpa_supplicant
%dir %{_sysconfdir}/logrotate.d
%config(noreplace) %{_sysconfdir}/logrotate.d/wpa_supplicant
%{_unitdir}/wpa_supplicant.service
%{_unitdir}/wpa_supplicant@.service
%{_unitdir}/wpa_supplicant-nl80211@.service
%{_unitdir}/wpa_supplicant-wired@.service
%{_datadir}/dbus-1/system.d/wpa_supplicant.conf
%{_datadir}/dbus-1/system-services/fi.w1.wpa_supplicant1.service
%{_sbindir}/wpa_passphrase
%{_sbindir}/wpa_supplicant
%{_sbindir}/wpa_cli
%{_sbindir}/eapol_test
%dir %{_sysconfdir}/wpa_supplicant
%{_mandir}/man8/wpa_supplicant.8.gz
%{_mandir}/man8/wpa_priv.8.gz
%{_mandir}/man8/wpa_passphrase.8.gz
%{_mandir}/man8/wpa_cli.8.gz
%{_mandir}/man8/wpa_background.8.gz
%{_mandir}/man8/eapol_test.8.gz
%{_mandir}/man5/*
%doc README
%doc wpa_supplicant/ChangeLog
%doc wpa_supplicant/eap_testing.txt
%doc wpa_supplicant/todo.txt
%doc wpa_supplicant/wpa_supplicant.conf
%doc wpa_supplicant/examples
%license COPYING


%if %with gui
%files gui
%{_bindir}/wpa_gui
%{_mandir}/man8/wpa_gui.8.gz
%endif


%changelog
* Sat Oct 31 2026 Dawson Hessler - 1:2.12-2
- Package wpa_supplicant 2.12 using Arch Linux build config and patchset (2.12-2) for Fedora 44
