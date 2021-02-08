import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_package_installed(host):
    p = host.package('haproxy')
    assert p.is_installed


def test_service_running_and_enabled(host):
    s = host.service('haproxy')
    assert s.is_enabled
    assert s.is_running


def test_main_config(host):
    f = host.file('/etc/haproxy/haproxy.cfg')
    assert f.exists
    assert f.is_file
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o640
    assert f.contains('mode       http')
    assert f.contains('stats      enable')
    assert f.contains('listen dashboard_cluster')
    assert f.contains('listen neutron_api_cluster')


@pytest.mark.parametrize('protocol,port', [
    ('tcp', '80'),
    ('tcp', '9001'),
    ('tcp', '9696'),
])
def test_listening_socket(host, protocol, port):
    s = host.socket('%s://0.0.0.0:%s' % (protocol, port))
    assert s.is_listening


@pytest.mark.parametrize('filename,key,value', [
    ('10-ip_nonlocal_bind.conf', 'net.ipv4.ip_nonlocal_bind', '1'),
    ('10-ip_forward.conf', 'net.ipv4.ip_forward', '1')
])
def test_sysctl_config(host, filename, key, value):
    f = host.file('/etc/sysctl.d/%s' % filename)
    assert f.exists
    assert f.is_file
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o644
    assert f.contains('%s=%s' % (key, value))


@pytest.mark.parametrize('key,value', [
    ('net.ipv4.ip_nonlocal_bind', 1),
    ('net.ipv4.ip_forward', 1)
])
def test_sysctl_value(host, key, value):
    assert host.sysctl(key) == value


@pytest.mark.parametrize('user,password,status', [
    ('haproxy-stats', 'B1Gp4sSw0rD!!', 200),
    ('foo', 'bar', 401)
])
def test_haproxy_stats(host, user, password, status):
    assert host.ansible(
       'uri',
       'url=http://127.0.0.1:9001 \
        user=%s \
        password=%s' % (user, password),
       check=False)['status'] == status


@pytest.mark.parametrize('port', [
    ('80'),
    ('9696')
])
def test_haproxy_listen(host, port):
    assert host.ansible(
       'uri',
       'url=http://127.0.0.1:%s' % port,
       check=False)['status'] == 200
