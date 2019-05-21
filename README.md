Ansible HAproxy (OpenStack ready)
=========


[![Build Status](https://travis-ci.org/uoi-io/ansible-haproxy.svg?branch=master)](https://travis-ci.org/uoi-io/ansible-haproxy) [![Ansible Galaxy](https://img.shields.io/badge/galaxy-uoi.haproxy-green.svg?style=flat)](https://galaxy.ansible.com/uoi-io/haproxy/)

This role provides support for the installation of HAproxy on current distributions:

 - CentOS **7.x**
 - RedHat **7.x**
 - Fedora **29**
 - Ubuntu **14.xx** / **15.xx** / **16.xx** / **18.04**
 - Debian **7.x** / **8.x** / **9.x**

The role allows you to configure multiple sections of HAproxy:
 
 - Global section
 - Default section
 - Listen section
 - Frontend section
 - Backend section
 - Peer section
 - Stats section

Requirements
------------

This role requires at least HAproxy **1.5** *(SSL native support)* and Ansible **2.x**.

Role Variables
--------------

There are no variables in the ``vars`` directory, all variables can be override via the playbook.

Empty variable like ``haproxy_global_uid`` wills appears in the ``/etc/haproxy/haproxy.cfg`` only if a value is define.

Variable like ``haproxy_global_stats: []`` are arrays, in this example, the array is empty. This variable can be declare in two different ways:
```
haproxy_global_stats: [ show-legends, show-node, refresh 20s]
haproxy_global_stats:
  - show-legends
  - show-node
  - refresh 20s
```

```
# file: roles/haproxy/defaults/main.yml
# Sysctl
haproxy_bind_nonlocal_ip: true
haproxy_ip_forward: true

# Common
haproxy_firewalld: true
haproxy_selinux: true
haproxy_apt_backports: false

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
haproxy_global_nbproc: 8
haproxy_global_cpu_maps: [ 1 0, 2 1, 3 2, 4 3, 5 4, 6 5, 7 6, 8 7 ]
haproxy_global_tunes:
  - tune.ssl.default-dh-param: 2048

# Default
haproxy_default_logs:
  - global
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
  - 400 {{ haproxy_errors_directory }}/400.http
  - 403 {{ haproxy_errors_directory }}/403.http
haproxy_default_http_check:
haproxy_default_monitor_uri:

# Stats
haproxy_stats: true
haproxy_stats_address: '*'
haproxy_stats_port: 9001
haproxy_stats_user: haproxy-stats
haproxy_stats_password: B1Gp4sSw0rD!!
haproxy_stats_uri: /
haproxy_stats_options:
  - refresh 20s
  - show-legends
  - show-node
  - hide-version

# SSL
haproxy_ssl_certificate: /etc/ssl/uoi.io/uoi.io.pem
haproxy_ssl_options: no-sslv3 no-tls-tickets force-tlsv12
haproxy_ssl_ciphers: AES128+EECDH:AES128+EDH
haproxy_ssl: 'ssl crt {{ haproxy_ssl_certificate }} ciphers {{ haproxy_ssl_ciphers }} {{ haproxy_ssl_options }}'
```

Dependencies
------------

None

Example Playbook
----------------

The below examples show you how to define ``frontend``, ``backend``, ``listen``, ``peer``.

```
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
```
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
      bind_process:
        - 1
      servers:
        - cnd01 10.0.0.70:8080 check
        - cnd02 10.0.0.71:8080 check
        - cnd03 10.0.0.71:8080 check
```
```
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
```
# Peer
haproxy_peer:
  - remote_peers:
      peers:
        - lb223 10.0.0.223:1024
        - lb224 10.0.0.224:1024
        - lb225 10.0.0.225:1024
```

Testing
-------

This role is using [ansible molecule](https://molecule.readthedocs.io/).
You'll just need to install molecule via pip and run it.
Currently the molecule configuration is based on the docker driver.

```console
$ apt/yum install docker
$ systemctl start docker
$ pip install docker molecule
$ molecule test
```

License
-------

Apache

Author Information
------------------

This role was created in 2016 by Gaëtan Trellu (goldyfruit).
