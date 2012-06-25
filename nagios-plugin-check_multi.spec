#
# Conditional build:
%bcond_without	tests		# build without tests

%define		plugin	check_multi
%include	/usr/lib/rpm/macros.perl
Summary:	Multi purpose wrapper plugin for Nagios/Icinga
Name:		nagios-plugin-%{plugin}
Version:	0.26
Release:	0.2
License:	GPL v2
Group:		Networking
URL:		http://my-plugin.de/wiki/projects/check_multi/start
Source0:	http://my-plugin.de/check_multi/%{plugin}-stable-%{version}.tar.gz
# Source0-md5:	38f822c3911c0cd5e625e859237ff902
BuildRequires:	perl-base
BuildRequires:	rpm-perlprov >= 4.1-13
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios/plugins
%define		plugindir	%{_prefix}/lib/nagios/plugins

%description
check_multi is a multi purpose wrapper plugin which takes benefit of
the Nagios 3.x capability to display multiple lines of plugin output.
It calls multiple child plugins and displays their output in the
long_plugin_output. A summary is given in the standard plugin output.
The child return code with the highest severity becomes the parent
(check_multi) plugin return code.

The configuration is very simple: a NRPE-stylish config file contains
a tag for each child plugin and then the check command line.

check_multi can cover complex Business Process Views - using a builtin
state evaluation mechanism. The second benefit is cluster monitoring
with no need for extra services. All you need is provided by
check_multi.

%prep
%setup -q -n %{plugin}-%{version}

%build
ETHTOOL=/sbin/ethtool \
GUNZIP=/usr/bin/gunzip \
MAILX=/bin/mailx \
%configure \
	--prefix=%{plugindir} \
	--libexecdir=%{plugindir}

%if %{with tests}
%{__make} test
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	-C plugins \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{plugin}
%{__make} install-config \
	CFGDIR=%{_examplesdir}/%{name}-%{version} \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc Changelog CM_VERSION LICENSE THANKS README
%dir %{_sysconfdir}/%{plugin}
%attr(755,root,root) %{plugindir}/check_multi

%dir %{_examplesdir}/%{name}-%{version}
%{_examplesdir}/%{name}-%{version}/*.cmd

%dir %{_examplesdir}/%{name}-%{version}/cluster
%{_examplesdir}/%{name}-%{version}/cluster/*.cfg
%{_examplesdir}/%{name}-%{version}/cluster/*.cmd

%dir %{_examplesdir}/%{name}-%{version}/feed_passive
%{_examplesdir}/%{name}-%{version}/feed_passive/*.cfg
%{_examplesdir}/%{name}-%{version}/feed_passive/*.cmd
%{_examplesdir}/%{name}-%{version}/feed_passive/*.tpl
%attr(755,root,root) %{_examplesdir}/%{name}-%{version}/feed_passive/gencfg
