%define pcre_major 1
%define pcre16_major 0
%define pcrecpp_major 0
%define pcreposix1_major 1
%define pcreposix0_major 0

%define libname		%mklibname pcre %{pcre_major}
%define libname16	%mklibname pcre16_ %{pcre16_major}
%define libnamecpp	%mklibname pcrecpp %{pcrecpp_major}
%define libnameposix1	%mklibname pcreposix %{pcreposix1_major}
%define libnameposix0	%mklibname pcreposix %{pcreposix0_major}
%define develname %mklibname -d pcre

%define build_pcreposix_compat 1

Summary:	Perl-compatible regular expression library
Name:		pcre
Version:	8.32
Release:	5
License:	BSD-Style
Group:		File tools
URL:		http://www.pcre.org/
Source0:	ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/%name-%version.tar.bz2
Source1:	ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/%name-%version.tar.bz2.sig
Requires: 	%{libname} = %{version}-%{release}
BuildRequires:	autoconf automake libtool
Patch1:		pcre-0.6.5-fix-detect-into-kdelibs.patch
Patch2:		pcre-linkage_fix.diff
# from debian:
Patch4:		pcre-pcreposix-glibc-conflict.patch

%description
PCRE has its own native API, but a set of "wrapper" functions that are based on
the POSIX API are also supplied in the library libpcreposix. Note that this
just provides a POSIX calling interface to PCRE: the regular expressions
themselves still follow Perl syntax and semantics. 
This package contains a grep variant based on the PCRE library.

%package -n	%{libname}
Group:		System/Libraries
Summary:	Perl-compatible regular expression library

%description -n	%{libname}
This package contains the shared library libpcre.

%package -n	%{libname16}
Group:		System/Libraries
Summary:	Perl-compatible regular expression library
Conflicts:	%{_lib}pcre1 < 8.30-3

%description -n	%{libname16}
This package contains the shared library libpcre16.

%package -n	%{libnamecpp}
Group:		System/Libraries
Summary:	Perl-compatible regular expression library
Conflicts:	%{_lib}pcre1 < 8.30-3

%description -n	%{libnamecpp}
This package contains the shared library libpcrecpp.

%package -n	%{libnameposix1}
Group:		System/Libraries
Summary:	Perl-compatible regular expression library
Conflicts:	%{_lib}pcre1 < 8.30-3

%description -n	%{libnameposix1}
This package contains the shared library libpcreposix.

%package -n	%{libnameposix0}
Group:		System/Libraries
Summary:	Perl-compatible regular expression library
Conflicts:	%{_lib}pcre1 < 8.30-3
Conflicts:	%{_lib}pcre0 < 8.21

%description -n	%{libnameposix0}
This package contains the shared library libpcreposix compat.

%package -n	%{develname}
Group:		Development/C
Summary:	Headers and static lib for pcre development
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libname16} = %{version}-%{release}
Requires:	%{libnamecpp} = %{version}-%{release}
Requires:	%{libnameposix1} = %{version}-%{release}
Requires:	%{libnameposix0} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname pcre 0 -d} < 8.31

%description -n	%{develname}
Install this package if you want do compile applications using the pcre
library.

The header file for the POSIX-style functions is called pcreposix.h. The 
official POSIX name is regex.h, but I didn't want to risk possible problems 
with existing files of that name by distributing it that way. To use it with an
existing program that uses the POSIX API, it will have to be renamed or pointed
at by a link.

%prep
%setup -q
%patch1 -p1 -b .detect_into_kdelibs
%patch2 -p0


# bork
perl -pi -e "s|ln -s|ln -snf|g" Makefile.am

%if %{build_pcreposix_compat}
  # pcre-pcreposix-glibc-conflict patch below breaks compatibility,
  # create a libpcreposix.so.0 without the patch
  cp -a . ../pcre-with-pcreposix_compat && mv ../pcre-with-pcreposix_compat .
%endif
%patch4 -p1 -b .symbol-conflict

%build
%if %{build_pcreposix_compat}
dirs="pcre-with-pcreposix_compat ."
%else
dirs="."
%endif
for i in $dirs; do
  cd $i
  mkdir -p m4
  autoreconf -fi
  %configure2_5x \
	--disable-static \
%ifarch %ix86 x86_64 %arm ppc ppc64 mips
	--enable-jit \
%endif
	--enable-utf \
	--enable-pcre16 \
	--enable-unicode-properties
  %make
  cd -
done

%check
export LC_ALL=C
# Tests, patch out actual pcre_study_size in expected results
#echo 'int main() { printf("%d", sizeof(pcre_study_data)); return 0; }' | \
#%{__cc} -xc - -include "pcre_internal.h" -I. -o study_size
#STUDY_SIZE=`./study_size`
#perl -pi -e "s,(Study size\s+=\s+)\d+,\${1}$STUDY_SIZE," testdata/testoutput*
make check

%install
%if %{build_pcreposix_compat}
%makeinstall_std -C pcre-with-pcreposix_compat
%endif
%makeinstall_std

install -d %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/libpcre.so.%{pcre_major}.* %{buildroot}/%{_lib}
ln -srf %{buildroot}/%{_lib}/libpcre.so.%{pcre_major}.*.* %{buildroot}%{_libdir}/libpcre.so
mv %{buildroot}%{_libdir}/libpcreposix.so.%{pcreposix1_major}.* %{buildroot}/%{_lib}
ln -srf %{buildroot}/%{_lib}/libpcreposix.so.%{pcreposix1_major}.*.* %{buildroot}%{_libdir}/libpcreposix.so

# Remove unwanted files
rm -rf %{buildroot}%{_docdir}/pcre*

%files
%doc AUTHORS COPYING LICENCE NEWS README
%{_bindir}/pcregrep
%{_bindir}/pcretest
%{_mandir}/man1/pcregrep.1*
%{_mandir}/man1/pcretest.1*

%files -n %{libname}
/%{_lib}/libpcre.so.%{pcre_major}*

%files -n %{libname16}
%{_libdir}/libpcre16.so.%{pcre16_major}*

%files -n %{libnamecpp}
%{_libdir}/libpcrecpp.so.%{pcrecpp_major}*

%files -n %{libnameposix1}
/%{_lib}/libpcreposix.so.%{pcreposix1_major}*

%files -n %{libnameposix0}
%{_libdir}/libpcreposix.so.%{pcreposix0_major}*

%files -n %{develname}
%doc doc/html ChangeLog
%{_bindir}/pcre-config
%{_libdir}/lib*.so
%{_includedir}/*.h
%{_libdir}/pkgconfig/libpcre16.pc
%{_libdir}/pkgconfig/libpcrecpp.pc
%{_libdir}/pkgconfig/libpcre.pc
%{_libdir}/pkgconfig/libpcreposix.pc
%{_mandir}/man1/pcre-config.1*
%{_mandir}/man3/*.3*

%changelog
* Thu Jan 17 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 8.31-2
- move libpcreposix.so.1 under /%%{_lib} as it's required by /bin/rpm

* Mon Jul 09 2012 Oden Eriksson <oeriksson@mandriva.com> 8.31-1
+ Revision: 808561
- 8.31

* Fri Feb 10 2012 Matthew Dawkins <mattydaw@mandriva.org> 8.30-4
+ Revision: 772522
- removed conflict to libpcre0

* Fri Feb 10 2012 Matthew Dawkins <mattydaw@mandriva.org> 8.30-3
+ Revision: 772497
- split libraries into separate pkgs
- disables static instead of removing the files

* Tue Feb 07 2012 Oden Eriksson <oeriksson@mandriva.com> 8.30-2
+ Revision: 771509
- rebuild
- work around a bug in rpm
- add back the pcreposix-glibc-conflict patch
- add a conflict on the old pcre lib

* Sun Feb 05 2012 Oden Eriksson <oeriksson@mandriva.com> 8.30-1
+ Revision: 771231
- 8.30
- spec file overhaulin'
- rediffed the linkage patch
- dropped the multilib crap
- dropped the pcreposix-glibc-conflict patch, should not be needed anymore

* Tue Dec 13 2011 Oden Eriksson <oeriksson@mandriva.com> 8.21-1
+ Revision: 740608
- 8.21

* Sun Dec 04 2011 Oden Eriksson <oeriksson@mandriva.com> 8.20-2
+ Revision: 737626
- drop the static lib and the libtool *.la file
- various fixes

* Sun Oct 23 2011 Oden Eriksson <oeriksson@mandriva.com> 8.20-1
+ Revision: 705782
- 8.20
- enable just-in-time compiler support (--enable-jit)

* Fri Aug 19 2011 Oden Eriksson <oeriksson@mandriva.com> 8.13-1
+ Revision: 695283
- 8.13

* Mon May 02 2011 Oden Eriksson <oeriksson@mandriva.com> 8.12-2
+ Revision: 661712
- multiarch fixes

* Tue Jan 18 2011 Oden Eriksson <oeriksson@mandriva.com> 8.12-1
+ Revision: 631526
- 8.12

* Thu Dec 23 2010 Oden Eriksson <oeriksson@mandriva.com> 8.11-1mdv2011.0
+ Revision: 624188
- 8.11

* Mon Jul 12 2010 Oden Eriksson <oeriksson@mandriva.com> 8.10-1mdv2011.0
+ Revision: 551258
- 8.10

* Fri Mar 19 2010 Funda Wang <fwang@mandriva.org> 8.02-1mdv2010.1
+ Revision: 525255
- update to new version 8.02

* Thu Jan 21 2010 Oden Eriksson <oeriksson@mandriva.com> 8.01-1mdv2010.1
+ Revision: 494479
- 8.01

* Fri Nov 06 2009 Oden Eriksson <oeriksson@mandriva.com> 8.00-1mdv2010.1
+ Revision: 461850
- fix build
- 8.00

* Wed Jun 10 2009 Oden Eriksson <oeriksson@mandriva.com> 7.9-1mdv2010.0
+ Revision: 384818
- 7.9
- rediff patches

* Thu Jan 15 2009 Pixel <pixel@mandriva.com> 7.8-3mdv2009.1
+ Revision: 329849
- add patch (from debian) to avoid symbol conflicts between libpcreposix and glibc
- change libpcreposix major since it is not backward compatible
- keep the previous libpcreposix.so.0 for backward compatibility

* Sun Dec 21 2008 Oden Eriksson <oeriksson@mandriva.com> 7.8-2mdv2009.1
+ Revision: 317123
- fix build with -Werror=format-security (P3)

* Fri Sep 05 2008 Frederik Himpe <fhimpe@mandriva.org> 7.8-1mdv2009.0
+ Revision: 281699
- Update to new version 7.8
- Use bz2 source tarballs instead of gz
- Remove CVE-2008-2371 patch, a fix for this security problem was
  integrated upstream

* Wed Jul 16 2008 Oden Eriksson <oeriksson@mandriva.com> 7.7-2mdv2009.0
+ Revision: 236328
- fix linkage
- P0: security fix for CVE-2008-2371

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Wed May 07 2008 Oden Eriksson <oeriksson@mandriva.com> 7.7-1mdv2009.0
+ Revision: 203261
- 7.7

* Mon Feb 18 2008 Thierry Vignaud <tv@mandriva.org> 7.6-2mdv2008.1
+ Revision: 171018
- rebuild
- fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake

* Tue Jan 29 2008 Funda Wang <fwang@mandriva.org> 7.6-1mdv2008.1
+ Revision: 159594
- update to new version 7.6

* Sat Jan 26 2008 Götz Waschk <waschk@mandriva.org> 7.5-3mdv2008.1
+ Revision: 158423
- enable unicode properties (bug #37183)

* Thu Jan 17 2008 Thierry Vignaud <tv@mandriva.org> 7.5-2mdv2008.1
+ Revision: 154148
- do not package big changelog

* Thu Jan 10 2008 Götz Waschk <waschk@mandriva.org> 7.5-1mdv2008.1
+ Revision: 147716
- new version

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Dec 03 2007 Funda Wang <fwang@mandriva.org> 7.4-2mdv2008.1
+ Revision: 114471
- rebuild
- clean old conditions

* Sat Oct 13 2007 Funda Wang <fwang@mandriva.org> 7.4-1mdv2008.1
+ Revision: 97867
- New version 7.4

* Wed Aug 29 2007 Funda Wang <fwang@mandriva.org> 7.3-1mdv2008.0
+ Revision: 73286
- New version 7.3

  + Thierry Vignaud <tv@mandriva.org>
    - replace %%_datadir/man by %%_mandir!

* Tue Jun 19 2007 Götz Waschk <waschk@mandriva.org> 7.2-1mdv2008.0
+ Revision: 41508
- new version

* Wed May 16 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 7.1-1mdv2008.0
+ Revision: 27456
- Updated to 7.1.
- Some cleanups.

