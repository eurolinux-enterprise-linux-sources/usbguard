%global _hardened_build 1

%define with_gui_qt5 0
%define with_dbus    0

Name:           usbguard
Version:        0.7.0
Release:        8%{?dist}
Summary:        A tool for implementing USB device usage policy
Group:          System Environment/Daemons
License:        GPLv2+
## Not installed
# src/ThirdParty/Catch: Boost Software License - Version 1.0
URL:            https://dkopecek.github.io/usbguard
Source0:        https://github.com/dkopecek/usbguard/releases/download/%{name}-%{version}/%{name}-%{version}.tar.gz
Source1:        usbguard-daemon.conf

Requires: systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

BuildRequires: libqb-devel
BuildRequires: libgcrypt-devel
BuildRequires: libstdc++-devel
BuildRequires: protobuf-devel protobuf-compiler
BuildRequires: PEGTL-static
BuildRequires: catch-devel
BuildRequires: autoconf automake libtool
BuildRequires: bash-completion
BuildRequires: audit-libs-devel
# For `pkg-config systemd` only
BuildRequires: systemd

%if 0%{with_gui_qt5}
BuildRequires: qt5-qtbase-devel qt5-qtsvg-devel qt5-linguist
%endif

%if 0%{with_dbus}
BuildRequires: dbus-glib-devel
BuildRequires: dbus-devel
BuildRequires: glib2-devel
BuildRequires: polkit-devel
BuildRequires: libxslt
BuildRequires: libxml2
%endif

%if 0%{?fedora}
BuildRequires: pandoc
%endif

%ifarch ppc
#
# We need atomic instruction emulation on the 32bit PPC arch
#
BuildRequires: libatomic
%endif

# 1444084 - New defects found in usbguard-0.7.0-1.el7
Patch0: usbguard-0.7.0-covscan-uninit-ctor.patch
# 1449344 - usbguard-daemon.conf(5) documentation issues in usbguard-0.7.0-2.el7
Patch1: usbguard-0.7.0-fixed-usbguard-daemon-conf-man-page.patch
Patch2: usbguard-0.7.0-fixed-usbguard-daemon-man-page.patch
#
# Apply upstream cleanup/refactoring changes to the 0.7.0 source
# code to make it compatible with future upstream patches.
#
Patch3: usbguard-0.7.0-upstream-compat.patch
# 1469399 - RFE: Use Type=forking instead of Type=simple in usbguard.service unit
Patch4: usbguard-0.7.0-daemonization.patch
#
# Disable some tests that require a controlled environment or are not required to
# be executed while building binary RPMs.
#
Patch5: usbguard-0.7.0-make-full-testsuite-conditional.patch
# 1487230 - unknown usbguard-daemon.conf directives don't trigger an error
Patch6: usbguard-0.7.0-strict-configuration-parsing.patch
# 1491313 - [RFE] Integrate USBGuard with Linux Audit subsystem
Patch7: usbguard-0.7.0-linux-audit-integration.patch
# 1516930 - usbguard fails to start on aarch64 (RHEL-ALT)
Patch8: usbguard-0.7.0-kernel-4.13-fix.patch
# 1491313 - [RFE] Integrate USBGuard with Linux Audit subsystem
Patch9: usbguard-0.7.0-libaudit-version.patch

%description
The USBGuard software framework helps to protect your computer against rogue USB
devices by implementing basic whitelisting/blacklisting capabilities based on
USB device attributes.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       pkgconfig
Requires:       libstdc++-devel

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        tools
Summary:        USBGuard Tools
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description    tools
The %{name}-tools package contains optional tools from the USBGuard
software framework.

%if 0%{with_gui_qt5}
###
%package        applet-qt
Summary:        USBGuard Qt 5.x Applet
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description    applet-qt
The %{name}-applet-qt package contains an optional Qt 5.x desktop applet
for interacting with the USBGuard daemon component.
###
%endif

%if 0%{with_dbus}
###
%package        dbus
Summary:        USBGuard D-Bus Service
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
Requires:       dbus
Requires:       polkit

%description    dbus
The %{name}-dbus package contains an optional component that provides
a D-Bus interface to the USBGuard daemon component.
###
%endif

%prep
%setup -q
# Remove bundled library sources before build
rm -rf src/ThirdParty/{Catch,PEGTL}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1

%build
mkdir -p ./m4
autoreconf -i -v --no-recursive ./
%configure \
    --disable-silent-rules \
    --without-bundled-catch \
    --without-bundled-pegtl \
    --enable-systemd \
%if 0%{with_gui_qt5}
    --with-gui-qt=qt5 \
%endif
%if 0%{with_dbus}
    --with-dbus \
    --with-polkit \
%else
    --without-dbus \
    --without-polkit \
%endif
    --with-crypto-library=gcrypt

make %{?_smp_mflags}

%check
make check

%install
make install INSTALL='install -p' DESTDIR=%{buildroot}

# Overwrite configuration with distribution defaults
mkdir -p %{buildroot}%{_sysconfdir}/usbguard
install -p -m 600 %{SOURCE1} %{buildroot}%{_sysconfdir}/usbguard/usbguard-daemon.conf

# Cleanup
find %{buildroot} \( -name '*.la' -o -name '*.a' \) -exec rm -f {} ';'

%preun
%systemd_preun usbguard.service

%post
/sbin/ldconfig
%systemd_post usbguard.service

%postun
/sbin/ldconfig
%systemd_postun usbguard.service

%files
%defattr(-,root,root,-)
%doc README.md CHANGELOG.md
%license LICENSE
%{_libdir}/*.so.*
%{_sbindir}/usbguard-daemon
%{_bindir}/usbguard
%dir %{_localstatedir}/log/usbguard
%dir %{_sysconfdir}/usbguard
%dir %{_sysconfdir}/usbguard/IPCAccessControl.d
%config(noreplace) %attr(0600,-,-) %{_sysconfdir}/usbguard/usbguard-daemon.conf
%config(noreplace) %attr(0600,-,-) %{_sysconfdir}/usbguard/rules.conf
%{_unitdir}/usbguard.service
%{_datadir}/man/man8/usbguard-daemon.8.gz
%{_datadir}/man/man5/usbguard-daemon.conf.5.gz
%{_datadir}/man/man5/usbguard-rules.conf.5.gz
%{_datadir}/man/man1/usbguard.1.gz
%{_datadir}/bash-completion/completions/usbguard

%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files tools
%defattr(-,root,root,-)
%{_bindir}/usbguard-rule-parser

%if 0%{with_gui_qt5}
###
%files applet-qt
%defattr(-,root,root,-)
%{_bindir}/usbguard-applet-qt
%{_mandir}/man1/usbguard-applet-qt.1.gz
%{_datadir}/applications/usbguard-applet-qt.desktop
%{_datadir}/icons/hicolor/scalable/apps/usbguard-icon.svg
###
%endif

%if 0%{with_dbus}
###
%files dbus
%defattr(-,root,root,-)
%{_sbindir}/usbguard-dbus
%{_datadir}/dbus-1/system-services/org.usbguard.service
%{_datadir}/dbus-1/system.d/org.usbguard.conf
%{_datadir}/polkit-1/actions/org.usbguard.policy
%{_unitdir}/usbguard-dbus.service
%{_mandir}/man8/usbguard-dbus.8.gz

%preun dbus
%systemd_preun usbguard-dbus.service

%post dbus
%systemd_post usbguard-dbus.service

%postun dbus
%systemd_postun_with_restart usbguard-dbus.service
###
%endif

%changelog
* Wed Dec 13 2017 Daniel Kopeček <dkopecek@redhat.com> 0.7.0-8
- RHEL 7.5 erratum
  - Require a lower version of libaudit during build-time
  Resolves: rhbz#1491313

* Mon Nov 27 2017 Daniel Kopeček <dkopecek@redhat.com> 0.7.0-7
- RHEL 7.5 erratum
  - Fixed usbguard-daemon on systems with kernel >= 4.13
  - Use distribution specific usbguard-daemon.conf instead
    of the upstream version
  Resolves: rhbz#1516930

* Fri Nov  3 2017 Daniel Kopeček <dkopecek@redhat.com> 0.7.0-6
- RHEL 7.5 erratum
  - Add Linux Audit integration
  Resolves: rhbz#1491313

* Thu Nov  2 2017 Daniel Kopeček <dkopecek@redhat.com> 0.7.0-5
- RHEL 7.5 erratum
  - Make parsing of configuration file strict
  Resolves: rhbz#1487230

* Tue Oct 17 2017 Daniel Kopeček <dkopecek@redhat.com> 0.7.0-4
- RHEL 7.5 erratum
  - Implemented double-fork daemonization support
  Resolves: rhbz#1469399

* Fri May 12 2017 Daniel Kopeček <dkopecek@redhat.com> 0.7.0-3
- Fixed usbguard-daemon and usbguard-daemon.conf man-pages
  Resolves: rhbz#1449344

* Thu Apr 20 2017 Daniel Kopeček <dkopecek@redhat.com> 0.7.0-2
- Fixed UNINIT_CTOR issues found by coverity scan
  Resolves: rhbz#1444084

* Fri Apr 14 2017 Daniel Kopeček <dkopecek@redhat.com> 0.7.0-1
- Import
