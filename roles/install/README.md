# smallstep.agent.install

This role can be used can be used to install the [Smallstep Agent](https://smallstep.com) on your servers.

This role currently supports:

* Fedora (Current Releases)
* Enterprise Linux (RHEL, CentOS Stream, Rocky Linux, Alma Linux, etc)
* Ubuntu (Current Stable and LTS releases)
* Debian (Current Releases)

## Requirements

* Python 3.8 or greater on servers
* `pip` installed on servers
* `pip install sigstore` on servers that are using the binary install

## Role Variables

```yaml
smallstep_agent_version: # (Optional) Format: v0.0.1. Default: latest version
smallstep_agent_download_url: # (Optional) Default: https://dl.smallstep.com/step-agent-plugin
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
```

## Author Information

* Joe Doss @jdoss
* Smallstep Engineering

## License

[Apache License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

Copyright 2023 Smallstep Labs Inc.
