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
* `pip install sigstore` on servers

## Role Variables

```yaml
step_agent_team: # (Required) Your team ID.
step_agent_fingerprint: # (Required) Your Smallstep Agents CA fingerprint
step_agent_ca_url: # (Optional) The agent CA URL. Defaults to agents.<team-id>.ca.smallstep.com
step_agent_provisioner: # (Optional) The provisioner to use. Defaults to acme-da
step_agent_user: step-agent
step_agent_user_privileged: False
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
        step_agent_team: YourTeamID
        step_agent_fingerprint: ourCAfingerprintHere22ba483f7d97a7e43f92d7d4eb084d52xfoofoofoo
        # step_agent_ca_url: # (Optional) The agent CA URL. Defaults to agents.<team-id>.ca.smallstep.com
        # step_agent_provisioner: # (Optional) The provisioner to use. Defaults to acme-da
        # step_agent_user: # (Optional) The systemd unit dynamic username. Defaults to step-agent
        # step_agent_user_privileged: # (Optional) Add SupplementaryGroups=root so the step-agent can send Signals to processes. Defaults to False
```

## Author Information

* Joe Doss @jdoss
* Smallstep Engineering

## License

[Apache License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

Copyright 2023 Smallstep Labs Inc.
