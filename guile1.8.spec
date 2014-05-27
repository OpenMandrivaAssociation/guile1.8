%define oname      guile

%define major      17
%define libname    %mklibname %{oname} %{major}
%define develname  %mklibname %{oname}1.8 -d

%define mver 1.8

%define __noautoreq '/usr/bin/guile|devel\\(libguile(.*)\\)'
%define __noautoreqfiles 'libguile-srfi-srfi.*so$'

Name:	        guile%{mver}
Version:	        1.8.8
Release:	        16
Summary:	        GNU implementation of Scheme for application extensibility
License:        LGPLv2+
Group:	        Development/Other
URL:	        http://www.gnu.org/software/guile/guile.html
Source0:	        ftp://ftp.gnu.org/pub/gnu/guile/guile-%{version}.tar.gz
Source1:	        ftp://ftp.gnu.org/pub/gnu/guile/guile-%{version}.tar.gz.sig
Patch0:		guile-1.8.3-64bit-fixes.patch
Patch1:		guile-1.6.4-amd64.patch
Patch2:		guile-1.8.5-drop-ldflags-from-pkgconfig.patch
Patch3:		guile-1.8.7-testsuite.patch
Patch5:		guile-1.8.7-fix-doc.patch
Patch6:		guile-1.8.8-make-sockets.test-more-robust.patch
Patch7:		guile-1.8.8-amtests.patch
Requires(pre,post):	%{libname} = %{version}-%{release}
Requires(pre,post):	%{name}-runtime = %{version}-%{release}
BuildRequires:	chrpath
BuildRequires:	gmp-devel
BuildRequires:	texinfo
BuildRequires:	libltdl-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	readline-devel
BuildRequires:	gettext-devel
# for srfi-19.test
BuildRequires:	timezone
Obsoletes:	%{oname} < 1.8.8-7
Conflicts:	%{oname} >= 2.0.3

%package -n %{libname}
Summary:	        Libraries for Guile %{version}
Group:		System/Libraries
Requires:       %{name}-runtime = %{version}-%{release}

%package -n %{develname}
Summary:	Development headers and static library for libguile
Group:	Development/C
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{_lib}%{oname}-devel < 1.8.8-7
Obsoletes:	%{_lib}%{oname}17-devel
Conflicts:	%{_lib}%{oname}-devel >= 2.0.3
Requires:	gmp-devel
Requires:	libtool-devel

%package runtime
Summary:	Guile runtime library
Group:		System/Libraries
Conflicts:      %{name} < 1.8.8-10

%description
GUILE (GNU's Ubiquitous Intelligent Language for Extension) is a
library implementation of the Scheme programming language, written in
C. GUILE provides a machine-independent execution platform that can
be linked in as a library during the building of extensible programs.

Install the guile package if you'd like to add extensibility to
programs that you are developing. You'll also need to install the
guile-devel package.

%description -n %{libname}
This package contains Guile shared object libraries. Guile is the GNU
Ubiquitous Intelligent Language for Extension.

%description -n %{develname}
This package contains the development headers and the static library
for libguile. C headers, aclocal macros, the `guile1.4-snarf' and
`guile-config' utilities, and static `libguile' library for Guile, the
GNU Ubiquitous Intelligent Language for Extension

%description runtime
This package contains Scheme runtime for GUILE, including ice-9
Scheme module.


%prep
%setup -q -n %{oname}-%{version}
%patch0 -p1 -b .64bit-fixes
%patch1 -p1 -b .amd64
%patch2 -p0 -b .pkgconfig
%patch3 -p1 -b .testsuite

%patch5 -p1 -b .doc
%patch6 -p1 -b .robust
%patch7 -p0 -b .amtests

%build
autoreconf -vfi
%configure2_5x \
    --disable-error-on-warning \
    --disable-rpath \
    --enable-dynamic-linking \
    --with-threads \
    --disable-static

chmod +x scripts/snarf-check-and-output-texi

%make

%check
%ifarch ia64
# FAIL: r4rs.test: (6 9): (#<procedure leaf-eq? (x y)> (a (b (c))) ((a) b c))
%{__make} check -k || :
%else
# all tests must pass
%{__make} check
%endif

%install
%makeinstall_std

%{__mkdir_p} %{buildroot}%{_datadir}/%{oname}/site

%multiarch_includes %{buildroot}%{_includedir}/lib%{oname}/scmconfig.h

%{_bindir}/chrpath -d %{buildroot}{%{_bindir}/%{oname},%{_libdir}/*.so.*.*.*}

# create ghost file for packaging
touch %{buildroot}%{_datadir}/%{oname}/%{mver}/slib %{buildroot}%{_datadir}/%{oname}/%{mver}/slibcat

rm -f ${RPM_BUILD_ROOT}%{_libdir}/libguile*.la


%triggerin -- slib
# Remove files created in guile < 1.8.7-4mdv
ln -sfT ../../slib %{_datadir}/guile/%{mver}/slib

rm -f %{_datadir}/guile/%{mver}/slibcat
export SCHEME_LIBRARY_PATH=%{_datadir}/slib/

# Build SLIB catalog
for pre in \
    "(use-modules (ice-9 slib))" \
    "(load \"%{_datadir}/slib/guile.init\")"
do
    %{_bindir}/guile -c "$pre
        (set! implementation-vicinity (lambda () \"%{_datadir}/guile/%{mver}/\"))
        (require 'new-catalog)" &> /dev/null && break
    rm -f %{_datadir}/guile/%{mver}/slibcat
done
:

%triggerun -- slib
if [ "$1" = 0 -o "$2" = 0 ]; then
    rm -f %{_datadir}/guile/%{mver}/slib{,cat}
fi


%files
%doc AUTHORS ChangeLog GUILE-VERSION LICENSE README THANKS
%{_bindir}/%{oname}
%{_bindir}/%{oname}-tools
%exclude %{_datadir}/%{oname}/%{mver}
%{_mandir}/man1/guile.1.*
%{_infodir}/*

%files -n %{libname}
%{_libdir}/lib*.so.%{major}*
%{_libdir}/lib%{oname}-srfi-srfi-13-14-v-3.so.3*
%{_libdir}/lib%{oname}-srfi-srfi-4-v-3.so.3*
%{_libdir}/lib%{oname}-srfi-srfi-1-v-3.so.3*
%{_libdir}/lib%{oname}-srfi-srfi-60-v-2.so.2*

%files -n %{develname}
%doc ABOUT-NLS HACKING NEWS INSTALL libguile/ChangeLog*
%{multiarch_includedir}/lib%{oname}/scmconfig.h
%{_bindir}/%{oname}-config
%{_bindir}/%{oname}-snarf
%{_datadir}/aclocal/*
%{_includedir}/lib%{oname}*
%{_includedir}/%{oname}*
%{_libdir}/lib%{oname}*.so
%exclude %{_libdir}/lib%{oname}-srfi*.so
%{_libdir}/pkgconfig/%{oname}*.pc

%files runtime
%{_libdir}/lib%{oname}-srfi*.so
%{_datadir}/%{oname}/%{mver}/guile-procedures.txt
%{_datadir}/%{oname}/%{mver}/ice-9/*.scm
%{_datadir}/%{oname}/%{mver}/ice-9/psyntax.*
%{_datadir}/%{oname}/%{mver}/ice-9/debugging/*.scm
%{_datadir}/%{oname}/%{mver}/ice-9/debugger/*.scm
%{_datadir}/%{oname}/%{mver}/srfi/srfi*.scm
%{_datadir}/%{oname}/%{mver}/scripts/*
%{_datadir}/%{oname}/%{mver}/slib
%{_datadir}/%{oname}/%{mver}/slibcat
%{_datadir}/%{oname}/%{mver}/lang/elisp/*
%{_datadir}/%{oname}/%{mver}/oop/goops.scm
%{_datadir}/%{oname}/%{mver}/oop/goops/*.scm

%changelog
* Sun Jul 22 2012 Thomas Spuhler <tspuhler@mandriva.org> 1.8.8-1mdv2012.0
+ Revision: 810562
- imported package guile1.8

