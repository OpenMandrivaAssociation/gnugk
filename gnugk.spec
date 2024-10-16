Summary:	OpenH323 Gatekeeper - The GNU Gatekeeper
Name:		gnugk
Version:	2.3.1
Release:	%mkrel 6
License:	GPL+
Group:		System/Servers
URL:		https://www.gnugk.org/
Source:		http://downloads.sourceforge.net/openh323gk/%{name}-%{version}.tar.gz
Source1:	gnugk.init
Source2:	gnugk.sysconfig
BuildRequires:	linuxdoc-tools
BuildRequires:	openh323-devel
BuildRequires:	pwlib-devel
BuildRequires:	pkgconfig
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The GNU Gatekeeper (GnuGk) is a full featured H.323 gatekeeper. It is
based on the Open H.323 (H323plus) stack. Both components together
form the basis for a free IP telephony system (VOIP).

%prep
%setup -q

%build
autoconf

export CFLAGS="%{optflags} -DLDAP_DEPRECATED"
export CXXFLAGS="%{optflags} -DLDAP_DEPRECATED"

%configure2_5x

%make \
    OPTCCFLAGS="%{optflags}" \
    OH323_LIBDIR=%{_libdir} \
    PWLIBDIR=%{_datadir}/pwlib \
    OPENH323DIR=%{_prefix} \
    PREFIX=%{_prefix} \
    PWLIB_BUILD=1 \
    LDFLAGS="%{?ldflags}" \
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
install -m0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
install -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

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
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

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
%doc changes.txt docs/manual/*.html docs/*.txt etc contrib
%attr(0755,root,root) %{_initrddir}/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}.ini
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(0755,root,root) %{_sbindir}/%{name}
%attr(0755,root,root) %{_sbindir}/%{name}-addpasswd
%dir %attr(0755,%{name},%{name}) %{_var}/run/%{name}
%dir %attr(0755,%{name},%{name}) %{_var}/log/%{name}

