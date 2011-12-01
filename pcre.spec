%define major 0
%define pcreposix_major 1
%define libname_orig	lib%{name}
%define libname	%mklibname pcre %{major}
%define develname %mklibname -d pcre

%define build_pcreposix_compat 1

Summary: 	Perl-compatible regular expression library
Name:	 	pcre
Version:	8.20
Release:	%mkrel 1
License: 	BSD-Style
Group:  	File tools
URL: 		http://www.pcre.org/
Source0:	ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/%name-%version.tar.bz2
Source1:	ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/%name-%version.tar.bz2.sig
Requires: 	%{libname} = %{version}-%{release}
BuildRequires:	automake
Patch1:		pcre-0.6.5-fix-detect-into-kdelibs.patch
Patch2:		pcre-linkage_fix.diff
# from debian:
Patch4:		pcre-pcreposix-glibc-conflict.patch
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
PCRE has its own native API, but a set of "wrapper" functions that are based on
the POSIX API are also supplied in the library libpcreposix. Note that this
just provides a POSIX calling interface to PCRE: the regular expressions
themselves still follow Perl syntax and semantics. 
This package contains a grep variant based on the PCRE library.

%package -n	%{libname}
Group:		System/Libraries
Summary:	Perl-compatible regular expression library
Provides:	%{libname_orig} = %{version}-%{release}
Conflicts:	pcre <= 4.0

%description -n	%{libname}
PCRE has its own native API, but a set of "wrapper" functions that are based on
the POSIX API are also supplied in the library libpcreposix. Note that this
just provides a POSIX calling interface to PCRE: the regular expressions
themselves still follow Perl syntax and semantics. The header file
for the POSIX-style functions is called pcreposix.h. The official POSIX name is
regex.h, but I didn't want to risk possible problems with existing files of
that name by distributing it that way. To use it with an existing program that
uses the POSIX API, it will have to be renamed or pointed at by a link.

%package -n	%{develname}
Group:		Development/C
Summary:	Headers and static lib for pcre development
Requires:	%{libname} = %{version}-%{release}
Provides:	%{libname_orig}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%mklibname pcre 0 -d
Conflicts:	pcre <= 4.0

%description -n	%{develname}
Install this package if you want do compile applications using the pcre
library.

%prep

%setup -q
%patch1 -p1 -b .detect_into_kdelibs
%patch2 -p0

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
  autoreconf -fis
  %configure2_5x --enable-utf8 --enable-unicode-properties --enable-jit
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
rm -rf %{buildroot}

%if %{build_pcreposix_compat}
%makeinstall_std -C pcre-with-pcreposix_compat
%endif
%makeinstall_std

%multiarch_binaries %{buildroot}%{_bindir}/pcre-config

mkdir -p %{buildroot}/%_lib
mv %{buildroot}/%_libdir/lib%{name}.so.%{major}.* %{buildroot}/%_lib
cd %{buildroot}/%_libdir
ln -s ../../%_lib/lib%{name}.so.%{major}.* .

# Remove unwanted files
rm -f %{buildroot}/%_docdir/pcre/{AUTHORS,ChangeLog,COPYING,LICENCE,NEWS}
rm -f %{buildroot}/%_docdir/pcre/{pcre-config.txt,pcre.txt,pcregrep.txt}
rm -f %{buildroot}/%_docdir/pcre/{pcretest.txt,README}
rm -rf %{buildroot}/%_docdir/pcre/html

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%_mandir/man1/pcregrep.1*
%_mandir/man1/pcretest.1*
%_bindir/pcregrep  
%_bindir/pcretest

%files -n %{libname}
%defattr(-,root,root)
%doc AUTHORS COPYING LICENCE NEWS README
/%_lib/lib*.so.%{major}*
%_libdir/lib*.so.%{major}*
%_libdir/libpcreposix.so.%{pcreposix_major}*

%files -n %{develname}
%defattr(-,root,root)
%doc doc/html
%doc ChangeLog 
%_libdir/lib*.a
%_libdir/lib*.la
%_libdir/lib*.so
%_includedir/*.h
%_libdir/pkgconfig/libpcre.pc
%_libdir/pkgconfig/libpcrecpp.pc
%_libdir/pkgconfig/libpcreposix.pc

%_bindir/pcre-config
%{multiarch_bindir}/pcre-config

%_mandir/man1/pcre-config.1*
%_mandir/man3/*.3*
