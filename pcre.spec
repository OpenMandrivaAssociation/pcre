# pcre is used by glib2.0, which is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%define pcre_major 1
%define pcre16_major 0
%define pcre32_major 0
%define pcrecpp_major 0
%define pcreposix1_major 1
%define pcreposix0_major 0

%define libname %mklibname pcre %{pcre_major}
%define libname16 %mklibname pcre16_ %{pcre16_major}
%define libname32 %mklibname pcre32_ %{pcre32_major}
%define libnamecpp %mklibname pcrecpp %{pcrecpp_major}
%define libnameposix1 %mklibname pcreposix %{pcreposix1_major}
%define libnameposix0 %mklibname pcreposix %{pcreposix0_major}
%define devname %mklibname pcre -d
%define sdevname %mklibname pcre -d -s

%define lib32name libpcre%{pcre_major}
%define lib32name16 libpcre16_%{pcre16_major}
%define lib32name32 libpcre32_%{pcre32_major}
%define lib32namecpp libpcrecpp%{pcrecpp_major}
%define lib32nameposix1 libpcreposix%{pcreposix1_major}
%define lib32nameposix0 libpcreposix%{pcreposix0_major}
%define dev32name libpcre-devel
%define sdev32name libpcre-static-devel

%define build_pcreposix_compat 1
%bcond_with crosscompile
%bcond_without pgo

%ifnarch %{ix86}
# (tpg) optimize it a bit
%global optflags %optflags -O3
%endif

Summary:	Perl-compatible regular expression library
Name:		pcre
Version:	8.45
Release:	1
License:	BSD-Style
Group:		File tools
Url:		http://www.pcre.org/
Source0:	https://ftp.pcre.org/pub/pcre/%{name}-%{version}.tar.bz2
Source1:	pcre.rpmlintrc
Patch0:		pcre-0.6.5-fix-detect-into-kdelibs.patch
Patch1:		pcre-linkage_fix.diff
Patch2:		pcre-8.21-multilib.patch
# from debian:
Patch3:		pcre-pcreposix-glibc-conflict.patch
# from fedora:
Patch10:     pcre-8.32-refused_spelling_terminated.patch
# Fix recursion stack estimator, upstream bug #2173, refused by upstream
Patch11:     pcre-8.41-fix_stack_estimator.patch
BuildRequires:	libtool
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(bzip2)
BuildRequires:	pkgconfig(readline)
BuildRequires:	pkgconfig(libedit)

%description
PCRE has its own native API, but a set of "wrapper" functions that are based on
the POSIX API are also supplied in the library libpcreposix. Note that this
just provides a POSIX calling interface to PCRE: the regular expressions
themselves still follow Perl syntax and semantics.

This package contains a grep variant based on the PCRE library.

%files
%{_bindir}/pcregrep
%{_bindir}/pcretest
%{_mandir}/man1/pcregrep.1*
%{_mandir}/man1/pcretest.1*

#----------------------------------------------------------------------------

%package -n %{libname}
Summary:	Perl-compatible regular expression library
Group:		System/Libraries

%description -n %{libname}
This package contains the shared library libpcre.

%files -n %{libname}
/%{_lib}/libpcre.so.%{pcre_major}*

#----------------------------------------------------------------------------

%package -n %{libname16}
Summary:	Perl-compatible regular expression library
Group:		System/Libraries
Conflicts:	%{_lib}pcre1 < 8.30-3

%description -n %{libname16}
This package contains the shared library libpcre16.

%files -n %{libname16}
%{_libdir}/libpcre16.so.%{pcre16_major}*

#----------------------------------------------------------------------------

%package -n %{libname32}
Summary:	Perl-compatible regular expression library
Group:		System/Libraries

%description -n %{libname32}
This package contains the shared library libpcre32.

%files -n %{libname32}
%{_libdir}/libpcre32.so.%{pcre32_major}*

#----------------------------------------------------------------------------

%package -n %{libnamecpp}
Summary:	Perl-compatible regular expression library
Group:		System/Libraries
Conflicts:	%{_lib}pcre1 < 8.30-3

%description -n %{libnamecpp}
This package contains the shared library libpcrecpp.

%files -n %{libnamecpp}
%{_libdir}/libpcrecpp.so.%{pcrecpp_major}*

#----------------------------------------------------------------------------

%package -n %{libnameposix1}
Summary:	Perl-compatible regular expression library
Group:		System/Libraries
Conflicts:	%{_lib}pcre1 < 8.30-3

%description -n %{libnameposix1}
This package contains the shared library libpcreposix.

%files -n %{libnameposix1}
/%{_lib}/libpcreposix.so.%{pcreposix1_major}*

#----------------------------------------------------------------------------

%package -n %{libnameposix0}
Summary:	Perl-compatible regular expression library
Group:		System/Libraries
Conflicts:	%{_lib}pcre1 < 8.30-3
Conflicts:	%{_lib}pcre0 < 8.21

%description -n %{libnameposix0}
This package contains the shared library libpcreposix compat.

%files -n %{libnameposix0}
%{_libdir}/libpcreposix.so.%{pcreposix0_major}*

#----------------------------------------------------------------------------

%package -n %{devname}
Summary:	Headers for pcre development
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Requires:	%{libname16} = %{EVRD}
Requires:	%{libname32} = %{EVRD}
Requires:	%{libnamecpp} = %{EVRD}
Requires:	%{libnameposix1} = %{EVRD}
Requires:	%{libnameposix0} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
Install this package if you want do compile applications using the PCRE
library.

The header file for the POSIX-style functions is called pcreposix.h. The
official POSIX name is regex.h, but I didn't want to risk possible problems
with existing files of that name by distributing it that way. To use it with an
existing program that uses the POSIX API, it will have to be renamed or pointed
at by a link.

%files -n %{devname}

%{_bindir}/pcre-config
%{_libdir}/lib*.so
%{_includedir}/*.h
%{_libdir}/pkgconfig/libpcre16.pc
%{_libdir}/pkgconfig/libpcre32.pc
%{_libdir}/pkgconfig/libpcrecpp.pc
%{_libdir}/pkgconfig/libpcre.pc
%{_libdir}/pkgconfig/libpcreposix.pc
%{_mandir}/man1/pcre-config.1*
%{_mandir}/man3/*.3*

#----------------------------------------------------------------------------

%package -n %{sdevname}
Summary:	Library file for linking statically to PCRE
Group:		Development/C
Provides:	%{name}-static-devel = %{EVRD}
Requires:	%{devname} = %{EVRD}

%description -n %{sdevname}
Library file for linking statically to PCRE.

%files -n %{sdevname}
%{_libdir}/*.a

#----------------------------------------------------------------------------

%if %{with compat32}
%package -n %{lib32name}
Summary:	Perl-compatible regular expression library (32-bit)
Group:		System/Libraries

%description -n %{lib32name}
This package contains the shared library libpcre. (32-bit)

%files -n %{lib32name}
%{_prefix}/lib/libpcre.so.%{pcre_major}*

#----------------------------------------------------------------------------

%package -n %{lib32name16}
Summary:	Perl-compatible regular expression library (32-bit)
Group:		System/Libraries

%description -n %{lib32name16}
This package contains the shared library libpcre16. (32-bit)

%files -n %{lib32name16}
%{_prefix}/lib/libpcre16.so.%{pcre16_major}*

#----------------------------------------------------------------------------

%package -n %{lib32name32}
Summary:	Perl-compatible regular expression library (32-bit)
Group:		System/Libraries

%description -n %{lib32name32}
This package contains the shared library libpcre32. (32-bit)

%files -n %{lib32name32}
%{_prefix}/lib/libpcre32.so.%{pcre32_major}*

#----------------------------------------------------------------------------

%package -n %{lib32namecpp}
Summary:	Perl-compatible regular expression library (32-bit)
Group:		System/Libraries

%description -n %{lib32namecpp}
This package contains the shared library libpcrecpp. (32-bit)

%files -n %{lib32namecpp}
%{_prefix}/lib/libpcrecpp.so.%{pcrecpp_major}*

#----------------------------------------------------------------------------

%package -n %{lib32nameposix1}
Summary:	Perl-compatible regular expression library (32-bit)
Group:		System/Libraries
Conflicts:	%{_lib}pcre1 < 8.30-3

%description -n %{lib32nameposix1}
This package contains the shared library libpcreposix. (32-bit)

%files -n %{lib32nameposix1}
%{_prefix}/lib/libpcreposix.so.%{pcreposix1_major}*

#----------------------------------------------------------------------------

%package -n %{lib32nameposix0}
Summary:	Perl-compatible regular expression library (32-bit)
Group:		System/Libraries

%description -n %{lib32nameposix0}
This package contains the shared library libpcreposix compat. (32-bit)

%files -n %{lib32nameposix0}
%{_prefix}/lib/libpcreposix.so.%{pcreposix0_major}*

#----------------------------------------------------------------------------

%package -n %{dev32name}
Summary:	Headers for pcre development (32-bit)
Group:		Development/C
Requires:	%{lib32name} = %{EVRD}
Requires:	%{lib32name16} = %{EVRD}
Requires:	%{lib32name32} = %{EVRD}
Requires:	%{lib32namecpp} = %{EVRD}
Requires:	%{lib32nameposix1} = %{EVRD}
Requires:	%{lib32nameposix0} = %{EVRD}
Requires:	%{devname} = %{EVRD}

%description -n %{dev32name}
Install this package if you want do compile applications using the PCRE
library. (32-bit)

The header file for the POSIX-style functions is called pcreposix.h. The
official POSIX name is regex.h, but I didn't want to risk possible problems
with existing files of that name by distributing it that way. To use it with an
existing program that uses the POSIX API, it will have to be renamed or pointed
at by a link.

%files -n %{dev32name}
%{_prefix}/lib/lib*.so
%{_prefix}/lib/pkgconfig/libpcre16.pc
%{_prefix}/lib/pkgconfig/libpcre32.pc
%{_prefix}/lib/pkgconfig/libpcrecpp.pc
%{_prefix}/lib/pkgconfig/libpcre.pc
%{_prefix}/lib/pkgconfig/libpcreposix.pc

#----------------------------------------------------------------------------

%package -n %{sdev32name}
Summary:	Library file for linking statically to PCRE (32-bit)
Group:		Development/C
Requires:	%{dev32name} = %{EVRD}

%description -n %{sdev32name}
Library file for linking statically to PCRE. (32-bit)

%files -n %{sdev32name}
%{_prefix}/lib/*.a
%endif

#----------------------------------------------------------------------------

%package doc
Summary:	Documentation for %{name}
Group:		Books/Computer books
Conflicts:	%{mklibname -d %{name}} < 2.54.3-2

%description doc
Documentation for %{name}.

%files doc
%doc AUTHORS COPYING LICENCE NEWS README
%doc doc/html

#----------------------------------------------------------------------------

%prep
%setup -q
%patch0 -p1 -b .detect_into_kdelibs
%patch1 -p1
%patch2 -p1

# bork
sed -i -e "s|ln -s|ln -snf|g" Makefile.am

%if %{build_pcreposix_compat}
  # pcre-pcreposix-glibc-conflict patch below breaks compatibility,
  # create a libpcreposix.so.0 without the patch
  cp -a . ../pcre-with-pcreposix_compat && mv ../pcre-with-pcreposix_compat .
%endif
%patch3 -p1 -b .symbol-conflict
%patch10 -p1
%patch11 -p2

# Because of rpath patch
libtoolize --copy --force

%build
%if %{build_pcreposix_compat}
dirs="pcre-with-pcreposix_compat ."
%else
dirs="."
%endif

%if %{with compat32}
for i in $dirs; do
  pushd $i
  mkdir -p m4 build32
  autoreconf -fi
  export CONFIGURE_TOP="$(pwd)"
  cd build32
  %configure32 \
	--enable-static \
  %ifarch %{ix86} %{x86_64} %{armx}
	--enable-jit \
  %endif
	--enable-utf \
	--enable-pcre16 \
	--enable-pcre32 \
	--enable-unicode-properties
  %make_build
  popd
done
%endif

for i in $dirs; do
  pushd $i
  mkdir -p m4 build
  autoreconf -fi
  export CONFIGURE_TOP="$(pwd)"
  cd build
  # The static lib is needed for qemu-static-* targets.
  # Please don't remove it.
  %if %{with pgo}
    CFLAGS="%{optflags} -fprofile-instr-generate" \
    CXXFLAGS="%{optflags} -fprofile-instr-generate" \
    LDFLAGS="%{ldflags} -fprofile-instr-generate" \
    %configure \
	--enable-static \
    %ifarch %{ix86} %{x86_64} %{armx}
	--enable-jit \
    %endif
	--enable-utf \
	--enable-pcre16 \
	--enable-pcre32 \
	--enable-unicode-properties
    %make_build

    export LLVM_PROFILE_FILE=libpng-%p.profile.d
    export LD_LIBRARY_PATH="$(pwd)"

    make check

    unset LD_LIBRARY_PATH
    unset LLVM_PROFILE_FILE
    llvm-profdata merge --output=%{name}.profile *.profile.d
    rm -f *.profile.d

    make clean

    CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
    CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
    LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
    %endif
    %configure \
	--enable-static \
    %ifarch %{ix86} %{x86_64} %{armx}
	--enable-jit \
    %endif
	--enable-utf \
	--enable-pcre16 \
	--enable-pcre32 \
	--enable-unicode-properties
  %make_build
  popd
done

%install
%if %{with compat32}
%if %{build_pcreposix_compat}
%make_install -C pcre-with-pcreposix_compat/build32
%endif
%make_install -C build32
%endif
%if %{build_pcreposix_compat}
%make_install -C pcre-with-pcreposix_compat/build
%endif
%make_install -C build

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

%check
export LC_ALL=C
# Tests, patch out actual pcre_study_size in expected results
#echo 'int main() { printf("%d", sizeof(pcre_study_data)); return 0; }' | \
#%{__cc} -xc - -include "pcre_internal.h" -I. -o study_size
#STUDY_SIZE=`./study_size`
#perl -pi -e "s,(Study size\s+=\s+)\d+,\${1}$STUDY_SIZE," testdata/testoutput*
make check -C build
