%global commit  ed62ff990953e73a264f25d38814895b662216dc

Name:           nodepool
Version:        0.3.1
Release:        1%{?dist}
Summary:        Node pool management for a distributed test infrastructure

License:        ASL 2.0
URL:            http://docs.openstack.org/infra/system-config/
Source0:        https://github.com/openstack-infra/nodepool/archive/%{commit}.tar.gz
Source1:        nodepool.service
Source10:       nodepool.yaml
Source11:       secure.conf
Source12:       logging.conf
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
Requires:       python2-PyMySQL
Requires:       python-zmq
Requires:       python-prettytable
Requires:       python-six
Requires:       python2-os-client-config
Requires:       python2-shade
Requires:       diskimage-builder
Requires:       python2-voluptuous
Requires:       python-kazoo
Requires:       python-paste
Requires:       python-webob


BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  systemd


%description
Nodepool is a service used by the OpenStack CI team to deploy and manage a pool
of devstack images on a cloud server for use in OpenStack project testing.


%prep
%autosetup -n %{name}-%{commit}
rm requirements.txt test-requirements.txt


%build
PBR_VERSION=%{version} %{__python2} setup.py build


%install
PBR_VERSION=%{version} %{__python2} setup.py install --skip-build --root %{buildroot}
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/nodepool.service
install -p -D -m 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/nodepool/nodepool.yaml
install -p -D -m 0640 %{SOURCE11} %{buildroot}%{_sysconfdir}/nodepool/secure.conf
install -p -D -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/nodepool/logging.conf
install -p -D -m 0644 %{SOURCE20} %{buildroot}%{_sysconfdir}/sysconfig/nodepool
install -p -d -m 0755 %{buildroot}%{_sysconfdir}/nodepool/scripts
install -p -d -m 0700 %{buildroot}%{_sharedstatedir}/nodepool
install -p -d -m 0700 %{buildroot}%{_var}/log/nodepool


%pre
getent group nodepool >/dev/null || groupadd -r nodepool
if ! getent passwd nodepool >/dev/null; then
  useradd -r -g nodepool -G nodepool -d %{_sharedstatedir}/nodepool -s /sbin/nologin -c "Nodepool Daemon" nodepool
fi
exit 0


%post
%systemd_post nodepool.service


%preun
%systemd_preun nodepool.service


%postun
%systemd_postun_with_restart nodepool.service


%files
%{_bindir}/nodepool
%{_bindir}/nodepoold
%{_bindir}/nodepool-builder
%{_unitdir}/nodepool.service
%{_sysconfdir}/nodepool/*
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/nodepool/nodepool.yaml
%config(noreplace) %attr(0640, root, nodepool) %{_sysconfdir}/nodepool/secure.conf
%config(noreplace) %{_sysconfdir}/sysconfig/nodepool
%dir %attr(0750, nodepool, nodepool) %{_sharedstatedir}/nodepool
%dir %attr(0750, nodepool, nodepool) %{_var}/log/nodepool
%{python2_sitelib}/nodepool
%{python2_sitelib}/nodepool-*.egg-info


%changelog
* Tue Mar 14 2017 Tristan Cacqueray - 0.3.1-1
- Initial packaging
