# smallstep.agent.configure

This role can be used can be used to configure the [Smallstep Agent](https://smallstep.com) on your servers.

This role currently supports:

* Fedora (Current Releases)
* Enterprise Linux (RHEL, CentOS Stream, Rocky Linux, Alma Linux, etc)
* Ubuntu (Current Stable and LTS releases)
* Debian (Current Releases)

## Requirements

* Python 3.8 or greater on servers
* `pip` installed on servers
* `pip install sigstore` on servers if using the binary install

## Role Variables

```yaml
smallstep_api_token: eyJhb...
smallstep_collections:
  - collection_slug: hotdog-staging
    display_name: "Hotdog App staging"
    admin_emails:
      - jdoss@smallstep.com
    device_type:
      aws_vm:
        disable_custom_sans: False
        accounts:
        - "123456789011"
    state: present
smallstep_workloads:
  - admin_emails:
      - jdoss@smallstep.com
    display_name: Hotdog App Nginx
    collection_slug: hotdog-staging
    workload_slug: "hotdog-nginx-staging"
    workload_type: nginx
    state: present
smallstep_collection_instances:
  - instance_id: i-0d69ab001748ab4444
    collection_slug: "{{ smallstep_collection }}"
    instance_metadata:
        name: stage-001
        role: nginx
        location: us-east-2
    state: present
```

## Example Playbook

Here's an example playbook for Enterprise Linux based servers. (Fedora, RHEL, CentOS Stream, Rocky Linux, Alma Linux, etc):

```yaml
---
- hosts: all
  become: True

  collections:
    - smallstep.sigstore
    - smallstep.cli
    - smallstep.agent

  pre_tasks:
    - name: Make sure the current version of pip is installed.
      dnf:
        name: python3-pip
        state: latest

  roles:
    - role: smallstep.cli.install
    - role: smallstep.agent.install
    - role: smallstep.agent.configure
      vars:
        smallstep_api_token: eyJhb...
        smallstep_collection: "hotdog-staging"
        smallstep_collections:
          - collection_slug: "{{ smallstep_collection }}"
            display_name: "Hotdog App staging"
            admin_emails:
              - jdoss@smallstep.com
            device_type:
              aws_vm:
                disable_custom_sans: False
                accounts:
                - "123456789011"
            state: present
        smallstep_workloads:
          - admin_emails:
              - jdoss@smallstep.com
            device_metadata_key_sans:
              - Name
            display_name: Hotdog Staging Nginx
            hooks:
                renew:
                    after: ["echo done"]
                    before: ["echo start"]
                    on_error: ["echo failed"]
                    shell: "/bin/bash"
                sign:
                    after: ["echo done"]
                    before: ["echo start"]
                    on_error: ["echo failed"]
                    shell: "/bin/bash"
            key_info:
                format: "DEFAULT"
                type: "DEFAULT"
            reload_info:
                method: "DBUS"
                unit_name: "nginx.service"
            collection_slug: "{{ smallstep_collection }}"
            workload_slug: "hotdog-nginx-staging"
            static_sans:
                - staging.hotdog.app
                - staging.nginx.hotdog.app
                - nginx.hotdog.app
            workload_type: nginx
            state: present
          - admin_emails:
              - jdoss@smallstep.com
            certificate_info:
                crt_file: "/etc/redis/tls/redis.crt"
                duration: "24h0m0s"
                gid: 1001
                key_file: "/etc/redis/tls/redis.key"
                type: "X509"
                uid: 1001
            device_metadata_key_sans:
              - Name
            display_name: Hotdog Staging Redis
            hooks:
                renew:
                    after: ["echo done"]
                    before: ["echo start"]
                    on_error: ["echo failed"]
                    shell: "/bin/bash"
                sign:
                    after: ["echo done"]
                    before: ["echo start"]
                    on_error: ["echo failed"]
                    shell: "/bin/bash"
            key_info:
                format: "DEFAULT"
                type: "DEFAULT"
            reload_info:
                method: "DBUS"
                unit_name: "redis.service"
            collection_slug: "{{ smallstep_collection }}"
            workload_slug: "hotdog-staging-redis"
            static_sans:
                - staging.hotdog.app
                - staging.redis.hotdog.app
                - redis.hotdog.app
            workload_type: redis
            state: present
        smallstep_collection_instances:
          - instance_id: i-0d69ab001748ab4444
            collection_slug: "{{ smallstep_collection }}"
            instance_metadata:
                name: stage-001
                role: nginx
                location: us-east-2
                smallstep_collection: "{{ smallstep_collection }}"
            state: present
          - instance_id: i-0d69ab001748a5555
            collection_slug: "{{ smallstep_collection }}"
            instance_metadata:
                name: stage-002
                role: nginx
                location: us-east-2
                smallstep_collection: "{{ smallstep_collection }}"
            state: present
          - instance_id: i-0d69ab001748a6666
            collection_slug: "{{ smallstep_collection }}"
            instance_metadata:
                name: stage-003
                role: nginx
                location: us-east-2
                smallstep_collection: "{{ smallstep_collection }}"
            state: present
```

## Author Information

* Joe Doss @jdoss
* Smallstep Engineering

## License

[Apache License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

Copyright 2023 Smallstep Labs Inc.
