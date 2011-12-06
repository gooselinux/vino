%define glib2_version 2.12.0
%define gtk2_version 2.6.0
%define libglade2_version 2.3.6
%define gconf2_version 2.14.0
%define libgnomeui_version 2.6.0
%define libgcrypt_version 1.2.0
%define libnotify_version 0.4.3
%define telepathy_glib_version 0.7.31

%define with_telepathy 1
%if 0%{?rhel:%{?rhel} <= 6}
%define with_telepathy 0
%endif

Summary: A remote desktop system for GNOME
Name: vino
Version: 2.28.1
Release: 3%{?dist}
URL: http://www.gnome.org
Source0: http://download.gnome.org/sources/vino/2.28/%{name}-%{version}.tar.bz2

Patch0: vino-smclient.patch
# https://bugzilla.gnome.org/show_bug.cgi?id=596548
Patch1: restart-command.patch
Patch3: mdns-crash.patch
Patch4: translation-fixes.patch

License: GPLv2+
Group: User Interface/Desktops
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires(pre): GConf2 >= %{gconf2_version}
Requires(post): GConf2 >= %{gconf2_version}
Requires(preun): GConf2 >= %{gconf2_version}

BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: libglade2-devel >= %{libglade2_version}
BuildRequires: GConf2-devel >= %{gconf2_version}
BuildRequires: libgnomeui-devel >= %{libgnomeui_version}
BuildRequires: libgcrypt-devel >= %{libgcrypt_version}
BuildRequires: libnotify-devel >= %{libnotify_version}
%if %{with_telepathy}
BuildRequires: telepathy-glib-devel >= %{telepathy_glib_version}
%endif
BuildRequires: libXt-devel, libXtst-devel, libXdamage-devel, avahi-glib-devel
BuildRequires: desktop-file-utils
BuildRequires: intltool
BuildRequires: gettext
BuildRequires: dbus-glib-devel
BuildRequires: libsoup-devel
BuildRequires: NetworkManager-devel
BuildRequires: libSM-devel
BuildRequires: gnome-keyring-devel
BuildRequires: unique-devel
BuildRequires: autoconf automake libtool
BuildRequires: gnome-common

%description
Vino is a VNC server for GNOME. It allows remote users to
connect to a running GNOME session using VNC.

%prep
%setup -q
%patch0 -p1 -b .smclient
%patch3 -p1 -b .mdns-crash
%patch4 -p1 -b .translation-fixes

autoreconf -i -f

%build
%configure                   	\
  --enable-avahi             	\
  --enable-gnome-keyring       	\
  --disable-gnutls           	\
  --disable-http-server		\
  --enable-libnotify 		\
  --enable-network-manager	\
%if %{with_telepathy}
  --enable-telepathy
%else
  --disable-telepathy
%endif

# drop unneeded direct library deps with --as-needed
# libtool doesn't make this easy, so we do it the hard way
sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0 /g' -e 's/    if test "$export_dynamic" = yes && test -n "$export_dynamic_flag_spec"; then/      func_append compile_command " -Wl,-O1,--as-needed"\n      func_append finalize_command " -Wl,-O1,--as-needed"\n\0/' libtool

make

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

desktop-file-install --vendor gnome --delete-original                   \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications                         \
  --add-only-show-in GNOME                                              \
  $RPM_BUILD_ROOT%{_datadir}/applications/vino-preferences.desktop

# stuff we don't want
rm -rf $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/icon-theme.cache

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/vino-server.schemas >& /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/vino-server.schemas >& /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/vino-server.schemas >& /dev/null || :
fi

%postun
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS COPYING NEWS README docs/TODO docs/remote-desktop.txt
%{_datadir}/vino
%{_datadir}/applications/*.desktop
%{_datadir}/dbus-1/services/org.gnome.Vino.service
%{_bindir}/*
%{_libexecdir}/*
%{_sysconfdir}/gconf/schemas/*.schemas
%{_sysconfdir}/xdg/autostart/vino-server.desktop

%changelog
* Wed Jun 30 2010 Soren Sandmann <ssp@redhat.com> - 2.28.1-4
- Translation updates.
  Related: rhbz 575682

* Wed Jun 30 2010 Soren Sandmann <ssp@redhat.com> - 2.28.1-3
- Fix for crash: 
  Related: rhbz 588626

* Wed Jan 13 2010 Owen Taylor <otaylor@redhat.com> - 2.28.1-2
- Build without telepathy support
  Related: rhbz 554517

* Mon Oct 19 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.1-1
- Update to 2.28.1

* Sun Sep 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-3
- Even better, just rely on autostart

* Sun Sep 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-2
- Make vino-server set a proper restart command

* Wed Sep 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Mon Sep  7 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.92-1
- Update to 2.27.92

* Tue Aug 25 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.91-1
- Update to 2.27.91

* Tue Aug 11 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.90-1
- Update to 2.27.90

* Mon Aug  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.5-2
- Enable telepathy

* Tue Jul 28 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.5-1
- Update to 2.27.5

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.26.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul  9 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-5
- Rebuild to shrink GConf schemas

* Tue Jun 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-4
- Try again: rebuild with new gcc

* Mon Jun 15 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-3
- Rebuild with new gcc

* Fri Jun 12 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-2
- Drop unneeded direct dependencies

* Mon Apr 13 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/vino/2.26/vino-2.26.1.news

* Mon Mar 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Mon Mar  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.92-1
- Update to 2.25.92
- Enable NetworkManager support

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Feb  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.90-1
- Update to 2.25.90

* Fri Jan 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.5-1
- Update to 2.25.5

* Tue Jan  6 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.4-1
- Update to 2.25.4

* Wed Dec 17 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.3-1
- Update to 2.25.3

* Mon Oct 20 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1

* Mon Sep 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-1
- Update to 2.24.0

* Mon Sep  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.92-1
- Update to 2.23.92

* Tue Sep  2 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Fri Aug 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.90-1
- Update to 2.23.90

* Fri Jul 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-3
- Use autostart to have gnome-session start the server

* Fri Jul 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-2
- Use standard icon names

* Tue Jul 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-1
- Update to 2.23.5

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Mon Feb 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update 2.21.92

* Tue Feb 12 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91

* Tue Jan 29 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Wed Dec  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.3-1
- Update to 2.21.3

* Tue Nov 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.2-1
- Update to 2.21.2

* Tue Oct 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-2
- Rebuild against new dbus-glib

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1 (translation updates)

* Tue Oct  2 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-2
- Fix a directory ownership issue

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Tue Sep  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.92-1
- Update to 2.19.92

* Mon Aug 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.90-1
- Update to 2.19.90
- Update the license field

* Mon Jul  9 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.5-1
- Update to 2.19.5

* Sun May 20 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.1-1
- Update to 2.18.1

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.92-1
- Update to 2.17.92
- Drop obsolete patches

* Wed Jan 24 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.5-2
- Fix some careless gconf value handling
- use libnotify
- Improve category in the desktop file

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.5-1
- Update to 2.17.5

* Tue Dec 19 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.4-1
- Update to 2.17.4

* Mon Nov  6 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.2-1
- Update to 2.17.2

* Sat Oct 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-1
- Update to 2.16.0

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-6
- Fix scripts according to the packaging guidelines

* Tue Oct 17 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-5
- Fix #191160

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.13.5-4.1
- rebuild

* Sat Jun 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-4
- More missing BuildRequires

* Mon May 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-3
- Add missing BuildRequires

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.5-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.5-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 17 2006 Mark McLoughlin <markmc@redhat.com> 2.13.5-2
- Build with --enable-avahi

* Tue Jan 17 2006 Matthias Clasen <mclasen@redhat.com> 2.13.5-1
- Update to 2.13.5

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Sep 26 2005 Mark McLoughlin <markmc@redhat.com> 2.12.0-2
- Add patch from Alexandre Oliva <oliva@lsd.ic.unicamp.br> to fix
  more keyboard brokeness (#158713)

* Wed Sep  7 2005 Matthias Clasen <mclasen@redhat.com> 2.12.0-1
- Update to 2.12.0

* Wed Aug 17 2005 Matthias Clasen <mclasen@redhat.com> 2.11.90-2
- Rebuild

* Thu Aug  4 2005 Matthias Clasen <mclasen@redhat.com> 2.11.90-1
- New upstream version

* Mon Jul 11 2005 Matthias Clasen <mclasen@redhat.com> 2.11.1.2-1
- Newer upstream version
- Drop upstreamed patches

* Fri May 20 2005 Mark McLoughlin <markmc@redhat.com> 2.10.0-4
- Fix various keyboarding handling issues:
   + bug #142974: caps lock not working
   + bug #140515: shift not working with some keys
   + bug #134451: over-eager key repeating

* Wed Apr 27 2005 Jeremy Katz <katzj@redhat.com> - 2.10.0-3
- silence %%post

* Mon Mar 28 2005 Christopher Aillon <caillon@redhat.com>
- rebuilt

* Fri Mar 25 2005 Christopher Aillon <caillon@redhat.com> 2.10.0-1
- Update to 2.10.0
- Update the GTK+ theme icon cache on (un)install

* Wed Mar  2 2005 Mark McLoughlin <markmc@redhat.com> 2.9.2-2
- Rebuild with gcc4

* Thu Jan 27 2005 Matthias Clasen <mclasen@redhat.com> 2.9.2-1
- Update to 2.9.2

* Tue Oct 12 2004 Mark McLoughlin <markmc@redhat.com> 2.8.1-1
- Update to 2.8.1
- Remove backported fixes

* Thu Oct  7 2004 Mark McLoughlin <markmc@redhat.com> 2.8.0.1-1.1
- Don't hang with metacity's "reduced resources" mode (#134240) 
- Improve the key repeat rate situation a good deal (#134451)

* Wed Sep 29 2004 Mark McLoughlin <markmc@redhat.com> 2.8.0.1-1
- Update to 2.8.0.1

* Tue Sep 21 2004 Mark McLoughlin <markmc@redhat.com> 2.8.0-1
- Update to 2.8.0
- Remove upstreamed work-without-gnutls patch

* Tue Sep  7 2004 Matthias Clasen <mclasen@redhat.com> 2.7.92-3
- Disable help button until there is help (#131632)
 
* Wed Sep  1 2004 Mark McLoughlin <markmc@redhat.com> 2.7.92-2
- Add patch to fix hang without GNU TLS (bug #131354)

* Mon Aug 30 2004 Mark McLoughlin <markmc@redhat.com> 2.7.92-1
- Update to 2.7.92

* Tue Aug 17 2004 Mark McLoughlin <markmc@redhat.com> 2.7.91-1
- Update to 2.7.91

* Mon Aug 16 2004 Mark McLoughlin <markmc@redhat.com> 2.7.90-2
- Define libgcrypt_version

* Thu Aug 12 2004 Mark McLoughlin <markmc@redhat.com> 2.7.90-1
- Update to 2.7.90

* Wed Aug  4 2004 Mark McLoughlin <markmc@redhat.com> 2.7.4-1
- Update to 2.7.4

* Tue Jul 13 2004 Mark McLoughlin <markmc@redhat.com> 2.7.3.1-1
- Initial build.
