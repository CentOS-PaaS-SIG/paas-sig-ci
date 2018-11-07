%global origin_release_dot 3.11
%global origin_release_nodot 311

Summary:   Yum configuration for OpenShift Origin %{origin_release_dot} packages
Name:      centos-release-openshift-origin%{origin_release_nodot}
Version:   1
Release:   2%{?dist}
License:   GPLv2
Source1:   LICENSE
URL:       https://wiki.centos.org/SpecialInterestGroup/PaaS/OpenShift
Provides:  %{name} = %{version}-%{release}
# This provides the public key
Requires:  centos-release-paas-common, centos-release-ansible26
BuildArch: noarch

%description
yum configuration for OpenShift Origin %{origin_release_dot} packages as delivered via the 
CentOS PaaS SIG.

%prep
%setup -q -n %{name} -T -c

%install
# Install License
install -m 644 %SOURCE1 .
# Install repo file
mkdir -p %{buildroot}%{_sysconfdir}/yum.repos.d/
cat << EOF >> %{buildroot}%{_sysconfdir}/yum.repos.d/CentOS-OpenShift-Origin%{origin_release_nodot}.repo
[centos-openshift-origin%{origin_release_nodot}]
name=CentOS OpenShift Origin
baseurl=http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin%{origin_release_nodot}/
enabled=1
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-SIG-PaaS

[centos-openshift-origin%{origin_release_nodot}-testing]
name=CentOS OpenShift Origin Testing
baseurl=http://buildlogs.centos.org/centos/7/paas/x86_64/openshift-origin%{origin_release_nodot}/
enabled=0
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-SIG-PaaS

[centos-openshift-origin%{origin_release_nodot}-debuginfo]
name=CentOS OpenShift Origin DebugInfo
baseurl=http://debuginfo.centos.org/centos/7/paas/x86_64/
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-SIG-PaaS

[centos-openshift-origin%{origin_release_nodot}-source]
name=CentOS OpenShift Origin Source
baseurl=http://vault.centos.org/centos/7/paas/Source/openshift-origin%{origin_release_nodot}/
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-SIG-PaaS

EOF
chmod 644 %{buildroot}%{_sysconfdir}/yum.repos.d/CentOS-OpenShift-Origin%{origin_release_nodot}.repo

%files
%license LICENSE
%config(noreplace) %{_sysconfdir}/yum.repos.d/CentOS-OpenShift-Origin%{origin_release_nodot}.repo

%changelog
* Wed Nov 07 2018 Dani Comnea <dani_comnea@yahoo.com> - 1-2
- Add the centos-release-ansible26 rpm dependency 
* Fri Dec 08 2017 Troy Dawson <tdawson@redha.com> - 1-1
- Initial version
