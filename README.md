# Ansible Collection - smallstep.agent

This collection provides the `smallstep.agent.install`, `smallstep.agent.configure` roles and `smallstep.agent.install_step_agent` playbook which can be used to install and configure the [Smallstep Agent](https://smallstep.com) on your servers. It uses the [smallstep.sigstore](https://github.com/smallstep/ansible-collection-sigstore) collection to verify the [Sigstore](https://sigstore.dev/) signatures which Smallstep uses to sign our software artifacts.

This collection currently supports:

* Fedora (Current Releases)
* Enterprise Linux (RHEL, CentOS Stream, Rocky Linux, Alma Linux, etc)
* Ubuntu (Current Stable and LTS releases)
* Debian (Current Releases)

## Requirements

* `ansible-galaxy collection install smallstep.sigstore` on control node
* Python 3.8 or greater on servers
* `pip` installed on servers
* `pip install sigstore` on servers

## Role: smallstep.agent.install

### smallstep.agent.install Role variables

```yaml
step_agent_version: # (Optional) Format: v0.0.1. Default: latest version
step_agent_install_path: # (Optional) Default: /usr/local/bin
step_agent_download_url: # (Optional) Default: https://dl.smallstep.com/step-agent-plugin
step_agent_verify_signature: # (Optional) Default: True
```

## Role: smallstep.agent.configure

### smallstep.agent.configure Role variables

```yaml
step_agent_team: YourTeamID # (Required) Your team ID.
step_agent_fingerprint: yourCAfingerprintHere22ba483f7d97a7e43f92d7d4eb084d52xfoofoofoo # (Required) Your Smallstep Agents CA fingerprint
step_agent_ca_url: # (Optional) The agent CA URL. Defaults to agents.<team-id>.ca.smallstep.com
step_agent_provisioner: # (Optional) The provisioner to use. Defaults to acme-da
step_agent_user: # (Optional) The systemd unit dynamic username. Defaults to step-agent
step_agent_user_privileged: # (Optional) Add SupplementaryGroups=root so the step-agent can send Signals to processes. Defaults to False
```

### Example Playbook

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
```

## Playbook: smallstep.agent.install_step_agent

Assuming you have the requirements listed above, run this collection playbook to install the most recent version of `step-agent-plugin`.

### Install the most recent version of step agent

```bash
export STEP_AGENT_TEAM=myteam
export STEP_AGENT_FINGERPRINT=yourCAfingerprintf03da2ba483f7d97a7e43f92d7d4eb084d52xfoofoofoo
ansible-playbook smallstep.agent.install_step_agent -i ansible_inventory -e "step_agent_team=${TEAM}" -e "step_agent_fingerprint=${CA_FINGERPRINT}"`
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

## Local uninstall

```bash
rm -rf ~/.ansible/collections/ansible_collections/smallstep/agent/
```

## License

[Apache License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

Copyright 2023 Smallstep Labs Inc.
