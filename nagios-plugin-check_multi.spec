#
# Conditional build:
%bcond_without	tests		# build without tests

%define		plugin	check_multi
%include	/usr/lib/rpm/macros.perl
Summary:	Multi purpose wrapper plugin for Nagios/Icinga
Name:		nagios-plugin-%{plugin}
Version:	0.26
Release:	0.19
License:	GPL v2
Group:		Networking
URL:		http://my-plugin.de/wiki/projects/check_multi/start
Source0:	http://my-plugin.de/check_multi/%{plugin}-stable-%{version}.tar.gz
# Source0-md5:	38f822c3911c0cd5e625e859237ff902
Source1:	%{plugin}.cfg
Patch0:		issue-6.patch
Patch1:		nstats.patch
BuildRequires:	perl-base
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	sed >= 4.0
Requires:	perl(Getopt::Long) >= 2.27
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir		/etc/nagios/plugins
%define		_localstatedir	/var/lib/nagios
%define		plugindir		%{_prefix}/lib/nagios/plugins

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
%patch0 -p1
%patch1 -p1

%{__sed} -i -e '
	s,@sysconfdir@/send_nsca.cfg,/etc/nagios/send_nsca.cfg,
' plugins/check_multi.in

%build
ETHTOOL=/sbin/ethtool \
GUNZIP=/usr/bin/gunzip \
MAILX=/bin/mailx \
%configure \
	--libexecdir=%{plugindir} \
	--with-plugin_path=%{plugindir} \
	--with-checkresults_dir=/var/spool/nagios/checkresults \
	--with-tmp_dir=/var/spool/nagios/%{plugin} \
	--with-tmp_etc=/var/spool/nagios/%{plugin}/etc \
	--with-tmp_dir_permissions=0770 \
	%{nil}

%if %{with tests}
%{__make} test
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/spool/nagios/%{plugin}/etc
%{__make} install \
	-C plugins \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{plugin}/{cluster,feed_passive}

# package contrib and sample config as examples
%{__make} install-config \
	CFGDIR=%{_examplesdir}/%{name}-%{version}/config \
	DESTDIR=$RPM_BUILD_ROOT

%{__make} install-contrib \
	CGIDIR=%{_examplesdir}/%{name}-%{version}/contrib \
	HTMLDIR=%{_examplesdir}/%{name}-%{version}/contrib \
	LIBEXECDIR=%{_examplesdir}/%{name}-%{version}/contrib \
	DESTDIR=$RPM_BUILD_ROOT

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/%{plugin}.cfg

cd $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}/config
# this one seems useful, package as config
cp -p nagiostats.cmd $RPM_BUILD_ROOT%{_sysconfdir}/%{plugin}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc Changelog CM_VERSION LICENSE THANKS README
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{plugin}.cfg
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{plugin}/*.cmd
%dir %{_sysconfdir}/%{plugin}
%attr(755,root,root) %{plugindir}/check_multi

%dir %attr(770,root,nagios) /var/spool/nagios/%{plugin}
%dir %attr(770,root,nagios) /var/spool/nagios/%{plugin}/etc

%{_examplesdir}/%{name}-%{version}/contrib

%dir %{_examplesdir}/%{name}-%{version}/config
%{_examplesdir}/%{name}-%{version}/config/*.cmd

%dir %{_examplesdir}/%{name}-%{version}/config/cluster
%{_examplesdir}/%{name}-%{version}/config/cluster/*.cfg
%{_examplesdir}/%{name}-%{version}/config/cluster/*.cmd

%dir %{_examplesdir}/%{name}-%{version}/config/feed_passive
%{_examplesdir}/%{name}-%{version}/config/feed_passive/*.cfg
%{_examplesdir}/%{name}-%{version}/config/feed_passive/*.cmd
%{_examplesdir}/%{name}-%{version}/config/feed_passive/*.tpl
%attr(755,root,root) %{_examplesdir}/%{name}-%{version}/config/feed_passive/gencfg
