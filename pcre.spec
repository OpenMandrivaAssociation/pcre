%define pcre_major 1
%define pcre16_major 0
%define pcrecpp_major 0
%define pcreposix1_major 1
%define pcreposix0_major 0

%define libname %mklibname pcre %{pcre_major}
%define libname16 %mklibname pcre16_ %{pcre16_major}
%define libnamecpp %mklibname pcrecpp %{pcrecpp_major}
%define libnameposix1 %mklibname pcreposix %{pcreposix1_major}
%define libnameposix0 %mklibname pcreposix %{pcreposix0_major}
%define develname %mklibname -d pcre
%define staticname %mklibname -s -d pcre

%define build_pcreposix_compat 1
%bcond_with	crosscompile

Summary:	Perl-compatible regular expression library
Name:		pcre
Version:	8.35
Release:	1
License:	BSD-Style
Group:		File tools
Url:		http://www.pcre.org/
Source0:	ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/%name-%version.tar.bz2
Patch1:		pcre-0.6.5-fix-detect-into-kdelibs.patch
Patch2:		pcre-linkage_fix.diff
# from debian:
Patch4:		pcre-pcreposix-glibc-conflict.patch
BuildRequires:	libtool

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
Summary:	Headers for pcre development
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libname16} = %{version}-%{release}
Requires:	%{libnamecpp} = %{version}-%{release}
Requires:	%{libnameposix1} = %{version}-%{release}
Requires:	%{libnameposix0} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{develname}
Install this package if you want do compile applications using the pcre
library.

The header file for the POSIX-style functions is called pcreposix.h. The 
official POSIX name is regex.h, but I didn't want to risk possible problems 
with existing files of that name by distributing it that way. To use it with an
existing program that uses the POSIX API, it will have to be renamed or pointed
at by a link.

%package -n	%{staticname}
Group:		Development/C
Summary:	Library file for linking statically to PCRE
Requires:	%{develname} = %{EVRD}

%description -n	%{staticname}
Library file for linking statically to PCRE

%prep
%setup -q
%patch1 -p1 -b .detect_into_kdelibs
%patch2 -p0

# bork
sed -i -e "s|ln -s|ln -snf|g" Makefile.am

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
  # The static lib is needed for qemu-static-* targets.
  # Please don't remove it.
  %configure2_5x \
	--enable-static \
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
# strange thing 
# see https://issues.openmandriva.org/show_bug.cgi?id=389
%if %{with crosscompile}
ln -srf %{buildroot}/%{_lib}/libpcre.so.%{pcre_major}.*.* %{buildroot}/%{_lib}/libpcre.so.1
%endif
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

%files -n %{staticname}
%{_libdir}/*.a
