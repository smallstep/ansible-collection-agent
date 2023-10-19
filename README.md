# Ansible Collection - smallstep.agent

This collection provides the `smallstep.agent.install`, `smallstep.agent.configure` roles and `smallstep.agent.install_step_agent` playbook which can be used to install and configure the [Smallstep Agent](https://smallstep.com) on your servers. It uses the [smallstep.sigstore](https://github.com/smallstep/ansible-collection-sigstore) collection to verify the [Sigstore](https://sigstore.dev/) signatures which Smallstep uses to sign our software artifacts for binary installs only.

For Fedora, EL, Debian and Ubuntu installs, it will default to using our system packages (RPM and Deb) over installing the binary. Please note the binary install only installs the binary. It does not install all of the other supporting files (systemd unit, polkit policy rules etc..) and we highly recommend that you use the officially supported Linux distributions below with the system packages.

This collection currently supports:

* Fedora (Current Releases)
* Enterprise Linux (RHEL, CentOS Stream, Rocky Linux, Alma Linux, etc)
* Ubuntu (Current Stable and LTS releases)
* Debian (Current Releases)

## Requirements

* `ansible-galaxy collection install smallstep.sigstore` on control node
* Python 3.8 or greater on servers
* `pip` installed on servers
* `pip install sigstore` on servers that are using the binary install

## Role: smallstep.agent.install

### smallstep.agent.install Role variables

```yaml
smallstep_agent_version: # (Optional) Format: v0.0.1. Default: latest version
smallstep_agent_download_url: # (Optional) Default: https://dl.smallstep.com/step-agent-plugin
```

## Role: smallstep.agent.configure

### smallstep.agent.configure Role variables

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

### Example Playbook

Here's an example playbook for Enterprise Linux based servers. (Fedora, RHEL, CentOS Stream, Rocky Linux, Alma Linux, etc) on AWS:

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
                role: staging
                location: us-east-2
                smallstep_collection: "{{ smallstep_collection }}"
            state: present
          - instance_id: i-0d69ab001748a5555
            collection_slug: "{{ smallstep_collection }}"
            instance_metadata:
                name: stage-002
                role: staging
                location: us-east-2
                smallstep_collection: "{{ smallstep_collection }}"
            state: present
          - instance_id: i-0d69ab001748a6666
            collection_slug: "{{ smallstep_collection }}"
            instance_metadata:
                name: stage-003
                role: staging
                location: us-east-2
                smallstep_collection: "{{ smallstep_collection }}"
            state: present
```

## Playbook: smallstep.agent.install_step_agent

Assuming you have the requirements listed above, run this collection playbook to install the most recent version of `step-agent-plugin`.

### Install the most recent version of step agent

```bash
ansible-playbook smallstep.agent.install_step_agent -i ansible_inventory`
```

## Local development

### Setup Ansible Collections workspace

In your source code directory do the following:

```bash
mkdir ansible_collections
cd ansible_collections
git git@github.com:smallstep/ansible-collection-cli.git smallstep/cli
git clone git@github.com:smallstep/ansible-collection-sigstore.git smallstep/sigstore
git clone git@github.com:ansible-collections/ansible.windows.git ansible/windows
cd smallstep/cli
```

Then make your changes and then run the `ansible-test` commands in the Testing section.

## Testing

### ansible-test sanity

```bash
ansible-test sanity --docker --skip-test validate-modules
```

### ansible-test integration

```bash
ansible-test integration --docker
```

## Local install

### Install the collection dependencies

```bash
ansible-galaxy collection install git+https://github.com/smallstep/ansible-collection-sigstore.git
ansible-galaxy collection install git+https://github.com/smallstep/ansible-collection-cli.git
ansible-galaxy collection install ansible.windows # Only needed for Windows installs (Untested!!)
```

### Install the smallstep.agent collection

```bash
ansible-galaxy collection build --output-path /tmp --force
ansible-galaxy collection install /tmp/smallstep-agent-0.0.1.tar.gz --force
```

### Symlink your development env to

```bash
ln -s /path/to/development/ansible_collections/smallstep/agent ~/.ansible/collections/ansible_collections/smallstep/agent
```

## Local uninstall or remove symlink

```bash
rm -rf ~/.ansible/collections/ansible_collections/smallstep/agent/
```

## License

[Apache License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

Copyright 2023 Smallstep Labs Inc.
