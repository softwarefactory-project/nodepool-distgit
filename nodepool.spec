%global commit  fb8bda31a30ee03a65707c230214abe411530e29
%global elements f0e234d309cf6ede50f0689b65b18bcdad25f96f

Name:           nodepool
Version:        0.4.0
Release:        2.20160617.fb8bda3%{?dist}
Summary:        Node pool management for a distributed test infrastructure

License:        ASL 2.0
URL:            http://docs.openstack.org/infra/system-config/
Source0:        https://github.com/openstack-infra/nodepool/archive/%{commit}.tar.gz
Source1:        https://github.com/openstack-infra/project-config/archive/%{elements}.tar.gz
Source2:        nodepool.service
Source3:        nodepool-builder.service
Source10:       nodepool.yaml
Source11:       secure.conf
Source12:       logging.conf
Source13:       builder-logging.conf
Source20:       sysconfig

BuildArch:      noarch

Requires:       python-pbr
Requires:       python-gear
Requires:       PyYAML
Requires:       python-jenkins
Requires:       python2-paramiko
Requires:       python-daemon
Requires:       python-extras
Requires:       python2-statsd
Requires:       python2-APScheduler
Requires:       python-sqlalchemy
Requires:       python-zmq
Requires:       python2-PyMySQL
Requires:       python-prettytable
Requires:       python-six
Requires:       python2-os-client-config
Requires:       python2-shade
Requires:       diskimage-builder
Requires:       python2-voluptuous


BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  systemd


%description
Nodepool is a service used by the OpenStack CI team to deploy and manage a pool
of devstack images on a cloud server for use in OpenStack project testing.


%package -n nodepoold
Summary:        Nodepoold service
Requires:       nodepool

%description -n nodepoold
Nodepoold service


%package builder
Summary:        Nodepool builder service
Requires:       nodepool
Requires:       yum-utils
Requires:       sudo

%description builder
Nodepool builder service


%package elements
Summary:        Nodepool infra elements

%description elements
Nodepool infra elements


%prep
%autosetup -n %{name}-%{commit}
gzip -dc %{SOURCE1} | tar -xvf -
rm requirements.txt test-requirements.txt


%build
PBR_VERSION=%{version} %{__python2} setup.py build


%install
PBR_VERSION=%{version} %{__python2} setup.py install --skip-build --root %{buildroot}
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/nodepool.service
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/nodepool-builder.service
install -p -D -m 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/nodepool/nodepool.yaml
install -p -D -m 0640 %{SOURCE11} %{buildroot}%{_sysconfdir}/nodepool/secure.conf
install -p -D -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/nodepool/logging.conf
install -p -D -m 0644 %{SOURCE13} %{buildroot}%{_sysconfdir}/nodepool/builder-logging.conf
install -p -D -m 0644 %{SOURCE20} %{buildroot}%{_sysconfdir}/sysconfig/nodepool
install -p -D -m 0644 %{SOURCE20} %{buildroot}%{_sysconfdir}/sysconfig/nodepool-builder
install -p -d -m 0755 %{buildroot}%{_sysconfdir}/nodepool/scripts
install -p -d -m 0755 %{buildroot}%{_sysconfdir}/nodepool/elements
install -p -d -m 0700 %{buildroot}%{_sharedstatedir}/nodepool
install -p -d -m 0700 %{buildroot}%{_sharedstatedir}/nodepool/dib
install -p -d -m 0700 %{buildroot}%{_sharedstatedir}/nodepool/.config/openstack
install -p -d -m 0700 %{buildroot}%{_var}/log/nodepool
install -p -d -m 0755 %{buildroot}%{_var}/run/nodepool
install -p -d -m 0755 %{buildroot}%{_var}/run/nodepool-builder
install -p -d -m 0755 %{buildroot}%{_var}/cache/nodepool/dib_cache
install -p -d -m 0755 %{buildroot}%{_var}/cache/nodepool/dib_tmp
install -p -d -m 0755 %{buildroot}/usr/share/nodepool/
mv project-config-%{elements}/nodepool/elements %{buildroot}/usr/share/nodepool/
mv project-config-%{elements}/nodepool/scripts %{buildroot}/usr/share/nodepool/


%pre
getent group nodepool >/dev/null || groupadd -r nodepool
if ! getent passwd nodepool >/dev/null; then
  useradd -r -g nodepool -G nodepool -d %{_sharedstatedir}/nodepool -s /sbin/nologin -c "Nodepool Daemon" nodepool
fi
exit 0


%post -n nodepoold
%systemd_post nodepool.service
%post builder
%systemd_post nodepool-builder.service

%preun -n nodepoold
%systemd_preun nodepool.service
%preun builder
%systemd_preun nodepool-builder.service

%postun -n nodepoold
%systemd_postun_with_restart nodepool.service
%postun builder
%systemd_postun_with_restart nodepool-builder.service


%files
%{_bindir}/nodepool
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/nodepool/logging.conf
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/nodepool/builder-logging.conf
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/nodepool/nodepool.yaml
%config(noreplace) %attr(0640, root, nodepool) %{_sysconfdir}/nodepool/secure.conf
%dir %attr(0750, nodepool, nodepool) %{_var}/log/nodepool
%attr(0750, nodepool, nodepool) %{_sharedstatedir}/nodepool
%{python2_sitelib}/nodepool
%{python2_sitelib}/nodepool-*.egg-info

%files -n nodepoold
%{_bindir}/nodepoold
%{_unitdir}/nodepool.service
%config(noreplace) %{_sysconfdir}/sysconfig/nodepool
%dir %attr(0755, nodepool, nodepool) %{_var}/run/nodepool

%files builder
%{_bindir}/nodepool-builder
%{_unitdir}/nodepool-builder.service
%config(noreplace) %{_sysconfdir}/sysconfig/nodepool-builder
%dir %attr(0755, nodepool, nodepool) %{_var}/run/nodepool-builder
%attr(0755, nodepool, nodepool) %{_var}/cache/nodepool

%files elements
/usr/share/nodepool/

%changelog
* Tue Mar 21 2017 Tristan Cacqueray - 0.3.1-2
- Add builder service

* Tue Mar 14 2017 Tristan Cacqueray - 0.3.1-1
- Initial packaging
