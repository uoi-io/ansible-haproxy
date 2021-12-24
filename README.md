# Ansible HAproxy (OpenStack ready)

[![Build Status](https://travis-ci.com/uoi-io/ansible-haproxy.svg?branch=master)](https://travis-ci.com/uoi-io/ansible-haproxy) [![Ansible Galaxy](https://img.shields.io/badge/galaxy-uoi.haproxy-green.svg?style=flat)](https://galaxy.ansible.com/uoi-io/haproxy/)

This role provides support for the installation of HAproxy on current distributions:

- CentOS **7.x** / **8.x**
- RedHat **7.x**
- Fedora **33** / **34**
- Debian **9.x** / **10.x**
- Ubuntu **18.04** / **20.04**

The role allows you to configure multiple sections of HAproxy:

- Global section
- Default section
- Listen section
- Frontend section
- Backend section
- Peer section
- Stats section

## Requirements

This role requires at least HAproxy **1.5** _(SSL native support)_ and Ansible **2.8**.

## Role Variables

There are no variables in the `vars` directory, all variables can be override via the playbook.

Empty variable like `haproxy_global_uid` wills appears in the `/etc/haproxy/haproxy.cfg` only if a value is define.

Variable like `haproxy_global_stats: []` are arrays, in this example, the array is empty. This variable can be declare in two different ways:

```yaml
haproxy_global_stats:
  - show-legends
  - show-node
  - refresh 20s
```

```yaml
# file: roles/haproxy/defaults/main.yml
# Sysctl
haproxy_bind_nonlocal_ip: true
haproxy_ip_forward: true

# Common
haproxy_mode: system  # or docker
haproxy_firewalld: true
haproxy_selinux: true
haproxy_apt_backports: false
# default value for macOS & Docker; overridden in `vars/{{ ansible_os_family }}.yml`
haproxy_errors_directory: /usr/local/etc/haproxy/errors

# Package customizations
haproxy_package: haproxy
haproxy_selinux_packages:
  - python3-libselinux
  - python3-policycoreutils
haproxy_service: haproxy
haproxy_bin: haproxy
haproxy_config: /etc/haproxy/haproxy.cfg

# Firewall
haproxy_fw_ports:
  - "{{ haproxy_stats_port }}/tcp"

# Global
haproxy_global_maxconn: 4000
haproxy_global_chroot: /var/lib/haproxy
haproxy_global_group: haproxy
haproxy_global_user: haproxy
haproxy_global_uid:
haproxy_global_gid:
haproxy_global_pidfile: /var/run/haproxy.pid
haproxy_global_ca_base:
haproxy_global_crt_base:
haproxy_global_ssl_options:
haproxy_global_ssl_ciphers:
haproxy_global_ssl_server_verify:
haproxy_global_stats: []
haproxy_global_description:
haproxy_global_ulimit_n:
haproxy_global_logs:
  - 127.0.0.1    local0 debug
haproxy_global_daemon: true
# nbproc is deprecated. Will be removed in version 2.5
# haproxy_global_nbproc: 8
# haproxy_global_cpu_maps: [ 1 0, 2 1, 3 2, 4 3, 5 4, 6 5, 7 6, 8 7 ]
haproxy_global_tunes:
  - tune.ssl.default-dh-param: 2048

# Default
haproxy_default_logs:
  - global
haproxy_default_log_format:
haproxy_default_mode:
haproxy_default_maxconn: 4000
haproxy_default_options:
  - dontlognull
  - forwardfor
  - http-server-close
haproxy_default_retries: 3
haproxy_default_timeouts:
  - http-request 10s
  - queue 1m
  - connect 10s
  - client 1m
  - server 1m
  - http-keep-alive 10s
  - check 10s
haproxy_default_balance:
haproxy_default_errorfiles:
  - "400 {{ haproxy_errors_directory }}/400.http"
  - "403 {{ haproxy_errors_directory }}/403.http"
haproxy_default_http_check:
haproxy_default_monitor_uri:

# Userlist
haproxy_userlist:

# Stats
haproxy_stats: true
haproxy_stats_address: '*'
haproxy_stats_port: 9001
haproxy_stats_ssl: false
haproxy_stats_user: haproxy-stats
haproxy_stats_password: B1Gp4sSw0rD!!
haproxy_stats_uri: /
haproxy_stats_options:
  - refresh 20s
  - show-legends
  - show-node
  - hide-version
haproxy_stats_listener_options:
  - dontlog-normal

# SSL
haproxy_ssl_certificate: /etc/ssl/uoi.io/uoi.io.pem
haproxy_ssl_options: no-sslv3 no-tls-tickets force-tlsv12
haproxy_ssl_ciphers: AES128+EECDH:AES128+EDH
haproxy_ssl: 'ssl crt {{ haproxy_ssl_certificate }} ciphers {{ haproxy_ssl_ciphers }} {{ haproxy_ssl_options }}'

# Docker
# see more details in `tasks/docker.yml` and https://docs.ansible.com/ansible/latest/collections/community/general/docker_container_module.html
haproxy_docker_name: "haproxy"
haproxy_docker_image: "haproxy:alpine"
haproxy_docker_network_mode: default
haproxy_docker_network_name: "haproxy"
haproxy_docker_pull: true
haproxy_docker_recreate: false
haproxy_docker_ports:
  - "8443:8443"
  - "{{ haproxy_stats_port }}:{{ haproxy_stats_port }}"
haproxy_docker_sysctls:
  net.ipv4.ip_nonlocal_bind: "{{ 1 if haproxy_bind_nonlocal_ip|bool else 0 }}"
  net.ipv4.ip_forward: "{{ 1 if haproxy_ip_forward|bool else 0 }}"
  net.core.somaxconn: 4096
  net.ipv4.tcp_syncookies: 1
haproxy_docker_ulimits:
  - "nofile:262144:262144"
haproxy_docker_volumes:
  - {{ haproxy_config }}+":/usr/local/etc/haproxy/haproxy.cfg:ro"
```

## Dependencies

None

## Example Playbook

The below examples show you how to define `frontend`, `backend`, `listen`, `peer`.

```yaml
# Frontend
haproxy_frontend:
  - dashboard_cluster:
      binds_ssl:
        - :443 ssl crt /etc/ssl/uoi.io/uoi.io.pem no-sslv3
      reqadds:
        - X-Forwarded-Proto:\ https
      default_backend: dashboard_backend
      logs:
        - 127.0.0.1 local0 debug
      acls:
        - url_static path_beg -i /static /images /javascript /stylesheets
        - url_static path_end -i .jpg .gif .png .css .js
      bind_process:
        - 1
      use_backends:
        - static if url_static
      capture:
        - request header Host len 64
        - request header X-Forwarded-For len 64
```

```yaml
# Backend
haproxy_backend:
  - dashboard_backend:
      balance: source
      bind_process:
        - 1
      servers:
        - ctrl01 10.0.0.67:80 check inter 2000 rise 2 fall 5
        - ctrl02 10.0.0.68:80 check inter 2000 rise 2 fall 5
        - ctrl03 10.0.0.69:80 check inter 2000 rise 2 fall 5
  - static:
      balance: roundrobin
      compression:
        - algo gzip deflate
        - type text/css text/html application/javascript
      bind_process:
        - 1
      servers:
        - cnd01 10.0.0.70:8080 check
        - cnd02 10.0.0.71:8080 check
        - cnd03 10.0.0.71:8080 check
```

```yaml
# Listen
haproxy_listen:
  - dashboard_cluster:
      mode: http
      description: Horizon Dashboard
      balance: roundrobin
      binds:
        - 10.0.0.100:80
      binds_ssl:
        - :443 ssl crt /etc/ssl/uoi.io/uoi.io.pem no-sslv3
      options: [ tcpka, httpchk, tcplog ]
      http-check: GET /auth/login
      cookie: SERVERID insert indirect nocache
      capture:
        - cookie SERVERID len 32
      timeouts:
        - client 90m
        - server 90m
      bind_process:
        - 1
      http_requests:
        - set-header X-Haproxy-Current-Date %T
      servers:
        - ctrl01 10.0.0.67:80 check cookie ctrl01inter 2000 rise 2 fall 5
        - ctrl02 10.0.0.68:80 check cookie ctrl02 inter 2000 rise 2 fall 5
        - ctrl03 10.0.0.69:80 check cookie ctrl03 inter 2000 rise 2 fall 5

  - neutron_api_cluster:
      binds_ssl:
        - 10.0.0.100:9696 {{ haproxy_ssl }}
      options: [ tcpka, httpchk, tcplog ]
      bind_process: [ 2, 3, 4, 5, 6, 7 ]
      balance: source
      servers:
        - ctrl01 10.0.0.62:9696 check inter 2000 rise 2 fall 5
        - ctrl02 10.0.0.63:9696 check inter 2000 rise 2 fall 5
        - ctrl03 10.0.0.64:9696 check inter 2000 rise 2 fall 5
```

```yaml
# Peer
haproxy_peer:
  - remote_peers:
      peers:
        - lb223 10.0.0.223:1024
        - lb224 10.0.0.224:1024
        - lb225 10.0.0.225:1024
```

```yaml
# Resolvers
haproxy_resolvers:
  - mydns:
      nameservers:
        - 'dns1 10.0.0.1:53'
        - 'dns3 tcp@10.0.0.3:53'
      parse_resolv_conf: true
      resolve_retries: 5
      timeouts:
        - 'resolve 1s'
        - 'retry 1s'
      holds:
        - 'other 30s'
        - 'refused 30s'
        - 'nx 30s'
        - 'valid 30s'
```

### Docker usage example

Here is a short example how to use the role in another playbook and run HAProxy in Docker.

```yaml
# site.yml
- hosts: haproxy
  name: HAProxy load balancer
  tags:
    - all
    - haproxy
  # can be included either via `role` or `include_role`
  # roles:
  #   - uoi-io.haproxy
  tasks:
    - include_role:
        name: uoi-io.haproxy
```

```yaml
# (group_vars|environments/<my env>/group_vars/haproxy.yml)
haproxy_mode: docker
haproxy_config: "{{ docker_persistent_path }}/haproxy/haproxy.cfg"
haproxy_firewalld: false
haproxy_selinux: false
# Global
haproxy_global_chroot: ""
# SSL
haproxy_ssl_certificate: /usr/local/etc/haproxy/ssl/haproxy.crt
# Frontend
haproxy_frontend:
  # ... frontend definition
# Backend
haproxy_backend_checks: "check inter 2000 rise 2 fall 5"
haproxy_backend:
  - my_backend:
      # ... backend definition
      # example that hosts can be dinamically linked based on another group
      servers: |-
        {%- set _list = [] %}
        {%- for _host in groups['MY_BACKEND_GROUP'] %}
          {%- set _list = _list.append(_host.split('.')[0] ~ ' ' ~ _host ~ ':' ~ MY_SERVICE_PORT ~ ' ' ~ haproxy_backend_checks) %}
        {%- endfor %}
        {{- _list }}
# Docker
haproxy_docker_ports:
  - "6443:6443"
  - "{{ haproxy_stats_port }}:{{ haproxy_stats_port }}"
# haproxy_docker_volumes: []
haproxy_docker_volumes:
  - "{{ haproxy_config }}:/usr/local/etc/haproxy/haproxy.cfg:ro"
  - "{{ docker_persistent_path }}/haproxy/haproxy.key:/usr/local/etc/haproxy/ssl/haproxy.crt.key:ro"
  - "{{ docker_persistent_path }}/haproxy/haproxy.crt:/usr/local/etc/haproxy/ssl/haproxy.crt:ro"
```

## RedHat based repository

If you have own repository with HAProxy, you can install repo file.
Next example will add repository with HAProxy 2 for CentOS 8

```
# Repository
haproxy_repo_yum:
  - name: haproxy
    description: HAProxy 2 repository - $basearch
    baseurl: https://download.copr.fedorainfracloud.org/results/pzinchuk/haproxy/epel-8-$basearch/
    priority: 1
    gpgcheck: true
    file: haproxy
    repo_gpgcheck: false
    skip_if_unavailable: true
    gpgkey: https://download.copr.fedorainfracloud.org/results/pzinchuk/haproxy/pubkey.gpg
    enabled: true
    state: present
```

## Testing

This role is using [ansible molecule](https://molecule.readthedocs.io/).
You'll just need to install molecule via `pip` and run it.
Currently the molecule configuration is based on the `docker` driver.

```console
apt/yum install docker
systemctl start docker
pip install docker molecule
molecule test
```

## License

Apache

## Author Information

This role was created in 2016 by Gaëtan Trellu (goldyfruit).
