%global commit  1cb82d6313bbc2f1843ce1b2d1903e796ac2c9a0
%global elements f0e234d309cf6ede50f0689b65b18bcdad25f96f

Name:           nodepool
Version:        0.4.0
Release:        8.20170515.1cb82d6%{?dist}
Summary:        Node pool management for a distributed test infrastructure

License:        ASL 2.0
URL:            http://docs.openstack.org/infra/system-config/
Source0:        https://github.com/openstack-infra/nodepool/archive/%{commit}.tar.gz
Source1:        https://github.com/openstack-infra/project-config/archive/%{elements}.tar.gz
Source2:        nodepool-launcher.service
Source3:        nodepool-builder.service
Source10:       nodepool.yaml
Source11:       secure.conf
Source12:       logging.conf
Source13:       builder-logging.conf
Source14:       sudoer
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
Requires:       python-voluptuous
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


%package launcher
Summary:        Nodepoold service
Requires:       nodepool

%description launcher
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
%autosetup -n %{name}-%{commit} -p1
gzip -dc %{SOURCE1} | tar -xvf -
rm requirements.txt test-requirements.txt


%build
PBR_VERSION=%{version} %{__python2} setup.py build


%install
PBR_VERSION=%{version} %{__python2} setup.py install --skip-build --root %{buildroot}
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/nodepool-launcher.service
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/nodepool-builder.service
install -p -D -m 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/nodepool/nodepool.yaml
install -p -D -m 0640 %{SOURCE11} %{buildroot}%{_sysconfdir}/nodepool/secure.conf
install -p -D -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/nodepool/logging.conf
install -p -D -m 0644 %{SOURCE13} %{buildroot}%{_sysconfdir}/nodepool/builder-logging.conf
install -p -D -m 0640 %{SOURCE14} %{buildroot}%{_sysconfdir}/sudoers.d/nodepool
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


%post launcher
%systemd_post nodepool-launcher.service
%post builder
%systemd_post nodepool-builder.service

%preun launcher
%systemd_preun nodepool-launcher.service
%preun builder
%systemd_preun nodepool-builder.service

%postun launcher
%systemd_postun_with_restart nodepool-launcher.service
%postun builder
%systemd_postun_with_restart nodepool-builder.service


%files
%{_bindir}/nodepool
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/nodepool/logging.conf
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/nodepool/builder-logging.conf
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/nodepool/nodepool.yaml
%config(noreplace) %attr(0640, root, nodepool) %{_sysconfdir}/nodepool/secure.conf
%dir %{_sysconfdir}/nodepool/scripts
%dir %{_sysconfdir}/nodepool/elements
%dir %attr(0750, nodepool, nodepool) %{_var}/log/nodepool
%attr(0750, nodepool, nodepool) %{_sharedstatedir}/nodepool
%{python2_sitelib}/nodepool
%{python2_sitelib}/nodepool-*.egg-info

%files launcher
%{_bindir}/nodepoold
%{_unitdir}/nodepool-launcher.service
%config(noreplace) %{_sysconfdir}/sysconfig/nodepool
%dir %attr(0755, nodepool, nodepool) %{_var}/run/nodepool

%files builder
%{_bindir}/nodepool-builder
%{_unitdir}/nodepool-builder.service
%{_sysconfdir}/sudoers.d/nodepool
%config(noreplace) %{_sysconfdir}/sysconfig/nodepool-builder
%dir %attr(0755, nodepool, nodepool) %{_var}/run/nodepool-builder
%attr(0755, nodepool, nodepool) %{_var}/cache/nodepool

%files elements
/usr/share/nodepool/


%changelog
* Mon Jun 05 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 0.4.0-8
- Bump to latest master, dropping snapshot image and introducing zookeeper service

* Tue May 23 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 0.4.0-7
- Remove nodepoold

* Tue May 23 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 0.4.0-6
- Add nodepool-launcher systemd unit (while keeping the 'nodepool' one for retro compat)

* Wed Apr 12 2017 Tristan Cacqueray - 0.4.0-5
- Cherry-pick fix for paramiko client close

* Thu Mar 30 2017 Tristan Cacqueray - 0.4.0-4
- Depends on python-voluptuous from rdo

* Tue Mar 28 2017 Tristan Cacqueray - 0.4.0-3
- Disable image build on nodepoold service

* Tue Mar 21 2017 Tristan Cacqueray - 0.4.0-2
- Add builder service

* Tue Mar 14 2017 Tristan Cacqueray - 0.4.0-1
- Initial packaging
