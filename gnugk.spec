%define openh323_version 1.15.3
%define pwlib_version 1.8.4

Summary:	OpenH323 Gatekeeper - The GNU Gatekeeper
Name:		gnugk
Version:	2.2.3
Release:	%mkrel 5
License:	GPL
Group:		System/Servers
URL:		http://www.gnugk.org/
Source0:	http://prdownloads.sourceforge.net/openh323gk/%{name}-%{version}-2.tar.bz2
Source2:	gnugk.init.bz2
Source3:	gnugk.sysconfig.bz2
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	file
BuildRequires:	linuxdoc-tools
BuildRequires:	openh323-devel >= %{openh323_version} pwlib-devel >= %{pwlib_version}
Requires:	openh323_1 >= %{openh323_version}
BuildRequires:	pkgconfig
BuildRequires:	MySQL-devel
BuildRequires:	postgresql-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The GNU Gatekeeper (GnuGk) is a full featured H.323 gatekeeper,
available freely under GPL license. It is based on the Open H.323
stack. Both components together form the basis for a free IP
telephony system (VOIP).

%prep

%setup -q -n openh323gk-%{version}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

bzcat %{SOURCE2} > gnugk.init
bzcat %{SOURCE3} > gnugk.sysconfig

%build
autoconf

export CFLAGS="%{optflags} -DLDAP_DEPRECATED"
export CXXFLAGS="%{optflags} -DLDAP_DEPRECATED"

%configure

%make \
    OPTCCFLAGS="%{optflags}" \
    OH323_LIBDIR=%{_libdir} \
    PWLIBDIR=%{_datadir}/pwlib \
    OPENH323DIR=%{_prefix} \
    PREFIX=%{_prefix} \
    PWLIB_BUILD=1 \
    LDFLAGS="-L%{_libdir}" \
    optshared addpasswd

make doc

%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_var}/log/%{name}
install -d %{buildroot}%{_var}/run/%{name}

install -m0755 obj_*/%{name} %{buildroot}%{_sbindir}/
install -m0755 obj_*/addpasswd %{buildroot}%{_sbindir}/%{name}-addpasswd

install -m0644 etc/complete.ini %{buildroot}%{_sysconfdir}/%{name}.ini
install -m0755 gnugk.init %{buildroot}%{_initrddir}/%{name}
install -m0644 gnugk.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}

cat > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} << EOF
/var/log/%{name}/%{name}.log {
    rotate 30
    size=100M
    notifempty
    missingok
    postrotate
        %{_initrddir}/%{name} condrestart
    endscript
}
EOF

%pre
%_pre_useradd %{name} %{_localstatedir}/%{name} /bin/false

%postun
%_postun_userdel %{name}

%post
%_post_service %{name}

%preun
%_preun_service %{name}


%clean
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc billing.pl changes.txt copying docs/manual/*.html docs/*.txt etc contrib
%attr(0755,root,root) %{_initrddir}/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}.ini
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(0755,root,root) %{_sbindir}/%{name}
%attr(0755,root,root) %{_sbindir}/%{name}-addpasswd
%dir %attr(0755,%{name},%{name}) %{_var}/run/%{name}
%dir %attr(0755,%{name},%{name}) %{_var}/log/%{name}

