#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Smallstep Labs, Inc. <techadmin@smallstep.com>
# Apache-2.0 (see LICENSE or https://opensource.org/license/apache-2-0/)

DOCUMENTATION = """
---
module: collection

short_description: Manage a Smallstep collection

description:
    - Manage a Smallstep collection

author:
    - Joe Doss (@jdoss)

options:
    api_token:
        description:
        - The Smallstep API Token used when connecting.
        - Required.
        env:
        - name: SMALLSTEP_API_TOKEN
        type: str
    api_host:
        description: The Smallstep host used when connecting.
        env:
        - name: SMALLSTEP_API_HOST
        type: str
    collection_slug:
        description:
            - The slug of the collection.
            - Required.
        type: str
    workload_slug:
        description:
            - The slug of the workload.
            - Required.
        type: str
    admin_emails:
        description:
            - Users that will have admin access to manage the agents authority,
            - Required.
        required: true
        type: list
        elements: str
    certificate_info:
        description:
            - Details on a managed certificate.
        type: dict
        elements: dict
        default: {"duration": "24h0m0s", "type": "X509"}
        suboptions:
            crt_file:
                description:
                    - The filepath where the certificate is to be stored.
                type: str
            duration:
                description:
                    - The certificate lifetime. Parsed as a Golang duration.
                    - https://pkg.go.dev/time#ParseDuration
                type: str
            gid:
                description:
                    - GID of the files where the certificate is stored.
                type: str
            key_file:
                description:
                    - The filepath where the key is to be stored.
                type: str
            mode:
                description:
                    - Permission bits of the files where the certificate is stored.
                type: int
            root_file:
                description:
                    - The filepath where the root certificate is to be stored.
                type: str
            type:
                description:
                    - The type of certificate.
                type: str
                required: true
                choices [ X509, SSH_USER, SSH_HOST ]
            uid:
                description:
                    - UID of the files where the certificate is stored.
                type: int
    device_metadata_key_sans:
        description:
            - SANs that will be populated from the instance data of the device in the device collection.
            - For example, if the device instance data in the collection is {"internal_host": "foo.internal", "external_host", "foo.example.com"} at the time the workload certificate is issued and this field is set to ["internal_host", "external_host"], then the certificate would include the SANs foo.internal and foo.example.com.
        type: dict
        elements: dict
    display_name:
        description:
            - The display name of the workload.
            - Required.
        type: str
    hooks:
        description:
            - The collection of commands to run when a certificate for a managed endpoint is signed or renewed.
        type: dict
        elements: dict
        suboptions:
            renew:
                description:
                    - A list of commands to run before and after a certificate is granted.
                    - Example: {"after":["echo done"],"before":["echo start"],"onError":["echo failed"],"shell":"/bin/bash"}
                type: str
            sign:
                description:
                    - A list of commands to run before and after a certificate is granted.
                    - Example: {"after":["echo done"],"before":["echo start"],"onError":["echo failed"],"shell":"/bin/bash"}
                type: str
    key_info:
        description:
            - The attributes of the cryptographic key.
        type: dict
        elements: dict
        suboptions:
            format:
                description:
                    - The format used to encode the private key.
                    - For X509 keys the default format is SEC 1 for ECDSA keys, PKCS#1 for RSA keys and PKCS#8 for ED25519 keys.
                    - For SSH keys the default format is always the OPENSSH format.
                type: str
                choices: [ DEFAULT, PKCS8, OPENSSH, DER ]
            pub_file:
                description:
                    - A CSR or SSH public key to use instead of generating one.
                type: str
            type:
                description:
                    - The key type used.
                    - The current DEFAULT type is ECDSA_P256.
                type: str
                choices [ DEFAULT, ECDSA_P256, ECDSA_P384, ECDSA_P521, RSA_2048, RSA_3072, RSA_4096, ED25519 ]
    reload_info:
        description:
            - The properties used to reload a service.
        type: dict
        elements: dict
        suboptions:
            method:
                description:
                    - Ways an endpoint can reload a certificate.
                    - AUTOMATIC means the process is able to detect and reload new certificates automatically.
                    - CUSTOM means a custom command must be run to trigger the workload to reload the certificates
                    - SIGNAL will configure the agent to send a signal to the process in pid_file.
                    - DBUS will use the systemd system bus to issue a try-reload-or-restart job for unit specified by unit_name.
                type: str
                required: true
                choices: [ AUTOMATIC, CUSTOM, SIGNAL, DBUS ]
            pid_file:
                description:
                    - File that holds the pid of the process to signal. Required when method is SIGNAL.
                type: str
            signal:
                description:
                    - The signal to send to a process when a certificate should be reloaded. Required when method is SIGNAL.
                type: int
            unit_name:
                description:
                    - The systemd unit name to reload when a certificate should be reloaded. Required when method is DBUS.
                type: str
    static_sans:
        description:
            - SANs that will be added to every certificate issued for this workload. The first will be used as the default Common Name.
        type: list
        elements: str
    workload_type:
        description:
            - The device type of the collection
            - Required.
        choices:
            - etcd
            - generic
            - git
            - grafana
            - haproxy
            - httpd
            - kafka
            - mysql
            - nginx
            - nodejs
            - openvpn
            - postgres
            - redis
            - tomcat
            - zookeeper
        required: true
        type: str
    state:
        description:
            - State of the instance.
        default: present
        choices: [ absent, present ]
        type: str
"""

EXAMPLES = """
- name: Manage a Smallstep Workload
  smallstep.agent.workload:
    admin_emails:
        - jdoss@smallstep.com
    device_metadata_key_sans:
        - Name
    display_name: Nginx
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
        format: DEFAULT
        type: DEFAULT
    reload_info:
        method: DBUS
        unit_name: nginx.service
    collection_slug: hotdog-production
    workload_slug: hotdog-nginx-production
    static_sans:
        - production.hotdog.app
        - production.nginx.hotdog.app
        - nginx.hotdog.app
    workload_type: nginx
    state: present
    api_token: "eyJUzI1NiI..."
"""

RETURN = """
smallstep_workload:
    description: Manage a Smallstep Workload
    returned: Always
    type: complex
    contains:
    smallstep_workload:
        admin_emails:
            - jdoss@smallstep.com
        collection_slug: hotdog-production
        device_metadata_key_sans:
            - Name
        display_name: Hotdog Nginx
        hooks:
          renew:
            after:
            - echo done
            before:
            - echo start
            on_error:
            - echo failed
            shell: /bin/bash
          sign:
            after:
            - echo done
            before:
            - echo start
            on_error:
            - echo failed
            shell: /bin/bash
        key_info:
          format: DEFAULT
          type: DEFAULT
        reload_info:
          method: DBUS
          unit_name: nginx.service
        static_sans:
            - production.hotdog.app
            - production.nginx.hotdog.app
            - nginx.hotdog.app
        workload_slug: hotdog-nginx-production
        workload_type: nginx
        state: present
    """

# noqa: E402
import json  # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible.module_utils.common.text.converters import to_native  # noqa: E402
from humps import decamelize  # noqa: E402
from smallstep import api as step  # noqa: E402
from smallstep.exceptions import StepException  # noqa: E402

from ..module_utils.agent import AnsibleStep  # noqa: E402


class AnsibleStepWorkload(AnsibleStep):
    def __init__(self, module):
        super().__init__(module, "smallstep_workload")
        self.smallstep_workload = None

        self.api_host = self.module.params.get("api_host")
        self.connectargs = {
            "smallstep_api_host": f"https://{self.api_host}/api",
            "smallstep_api_token": self.module.params.get("api_token"),
        }

    def _prep_result(self):
        api_info = super().api_info(connectargs=self.connectargs)
        return {
            "admin_emails": self.module.params.get("admin_emails"),
            "collection_slug": to_native(self.module.params.get("collection_slug")),
            "display_name": to_native(self.module.params.get("display_name")),
            "workload_slug": to_native(self.module.params.get("workload_slug")),
            "workload_type": self.module.params.get("workload_type"),
            "team": api_info["team"],
            "fingerprint": api_info["fingerprint"],
            "response": self.smallstep_workload,
        }

    def _get_workload(self):
        self.module.fail_on_missing_params(required_params=["workload_slug", "collection_slug"])
        try:
            workload = step.StepWorkload(**self.connectargs)
            res = workload.get(
                collection_slug=self.module.params.get("collection_slug"),
                workload_slug=self.module.params.get("workload_slug"),
            ).to_dict()
            self.smallstep_workload = res

        except StepException as exception:
            if exception.status_code == 404:
                self.smallstep_workload = None
                return
            else:
                self.fail_json(exception.message)

    def _create_workload(self):
        self.module.fail_on_missing_params(
            required_params=[
                "admin_emails",
                "collection_slug",
                "display_name",
                "workload_slug",
                "workload_type",
            ]
        )
        module_params = self.module.params
        filtered_params = self.filter_none(module_params)

        params = {
            "workload_slug": filtered_params.get("workload_slug"),
            "collection_slug": filtered_params.get("collection_slug"),
            "display_name": filtered_params.get("display_name"),
            "workload_type": filtered_params.get("workload_type"),
        }

        optional_params = [
            "admin_emails",
            "certificate_info",
            "device_metadata_key_sans",
            "hooks",
            "key_info",
            "reload_info",
            "static_sans",
        ]

        optparams = {}
        for oprams in optional_params:
            if filtered_params.get(oprams):
                optparams[oprams] = filtered_params.get(oprams) if filtered_params.get(oprams) else None

        if not self.module.check_mode:
            try:
                workload = step.StepWorkload(**self.connectargs)
                workload.create(
                    collection_slug=params["collection_slug"],
                    display_name=params["display_name"],
                    workload_slug=params["workload_slug"],
                    workload_type=params["workload_type"],
                    **optparams,
                ).to_dict()
                self._mark_changed()
                self._get_workload()
            except StepException as exception:
                self.fail_json(exception.message)

    def _update_workload(self, **kwargs):
        self.module.fail_on_missing_params(
            required_params=[
                "collection_slug",
                "workload_slug",
            ]
        )

        params = {
            "collection_slug": self.module.params.get("collection_slug"),
            "workload_slug": self.module.params.get("workload_slug"),
            "display_name": self.module.params.get("display_name"),
        }

        workload_params = decamelize(self.smallstep_workload)
        workload_params["device_metadata_key_sans"] = workload_params.pop("device_metadata_key_sa_ns", None)
        workload_params["static_sans"] = workload_params.pop("static_sa_ns", None)
        workload_params.pop("slug", None)

        module_params = self.filter_none(self.module.params)
        mod_params_remove = (
            "admin_emails",
            "api_host",
            "api_token",
            "collection_slug",
            "state",
            "workload_slug",
        )
        for k in mod_params_remove:
            module_params.pop(k, None)

        if self.module.params.get("certificate_info") is None:
            module_params["certificate_info"] = {"duration": "24h0m0s", "type": "X509"}

        if json.dumps(workload_params, sort_keys=True) != json.dumps(module_params, sort_keys=True):
            modargs = module_params
            modargs.pop("workload_type")
            modargs.pop("display_name")
            if not self.module.check_mode:
                try:
                    workload = step.StepWorkload(**self.connectargs)
                    workload.update(
                        workload_slug=params["workload_slug"],
                        collection_slug=params["collection_slug"],
                        workload_type=workload_params["workload_type"],
                        display_name=params["display_name"],
                        **modargs,
                    ).to_dict()
                    self._mark_changed()
                    self._get_workload()
                except StepException as exception:
                    self.fail_json(exception.message)

    def check_workload(self):
        self._get_workload()
        if self.smallstep_workload is None:
            self._create_workload()
        else:
            self._update_workload()

    def destroy_workload(self):
        self.module.fail_on_missing_params(required_params=["workload_slug", "collection_slug"])
        self._get_workload()
        if self.smallstep_workload is not None:
            if not self.module.check_mode:
                try:
                    workload = step.StepWorkload(**self.connectargs)
                    workload.destroy(
                        collection_slug=self.module.params.get("collection_slug"),
                        workload_slug=self.module.params.get("workload_slug"),
                    )
                    self._mark_changed()
                    self._get_workload()
                except StepException as exception:
                    self.fail_json(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                admin_emails=dict(type="list", elements="str", required=True),
                certificate_info=dict(
                    type="dict",
                    options=dict(
                        crt_file=dict(type="str"),
                        duration=dict(type="str"),
                        gid=dict(type="int"),
                        key_file=dict(type="str"),
                        mode=dict(type="int"),
                        root_file=dict(type="str"),
                        type=dict(
                            type="str",
                            required=True,
                            choices=["X509", "SSH_USER", "SSH_HOST"],
                        ),
                        uid=dict(type="int"),
                    ),
                ),
                collection_slug=dict(type="str", required=True),
                device_metadata_key_sans=dict(type="list", elements="str"),
                display_name=dict(type="str", required=True),
                hooks=dict(
                    type="dict",
                    options=dict(renew=dict(type="dict"), sign=dict(type="dict")),
                ),
                key_info=dict(
                    type="dict",
                    options=dict(
                        format=dict(
                            type="str",
                            choices=[
                                "DEFAULT",
                                "PKCS8",
                                "OPENSSH",
                                "DER",
                            ],
                        ),
                        pub_file=dict(type="str"),
                        type=dict(
                            type="str",
                            required=True,
                            choices=[
                                "DEFAULT",
                                "ECDSA_P256",
                                "ECDSA_P384",
                                "ECDSA_P521",
                                "RSA_2048",
                                "RSA_3072",
                                "RSA_4096",
                                "ED25519",
                            ],
                        ),
                    ),
                ),
                reload_info=dict(
                    type="dict",
                    required_if=[
                        ("method", "DBUS", ("unit_name",)),
                        ("method", "SIGNAL", ("pid_file", "signal")),
                    ],
                    mutually_exclusive=[
                        ("unit_name", "pid_file"),
                        ("unit_name", "signal"),
                    ],
                    options=dict(
                        method=dict(
                            type="str",
                            required=True,
                            choices=[
                                "AUTOMATIC",
                                "CUSTOM",
                                "SIGNAL",
                                "DBUS",
                            ],
                        ),
                        pid_file=dict(type="str"),
                        signal=dict(type="int"),
                        unit_name=dict(type="str"),
                    ),
                ),
                static_sans=dict(type="list", elements="str"),
                workload_slug=dict(type="str", required=True),
                workload_type=dict(
                    type="str",
                    required=True,
                    choices=[
                        "etcd",
                        "generic",
                        "git",
                        "grafana",
                        "haproxy",
                        "httpd",
                        "kafka",
                        "mysql",
                        "nginx",
                        "nodejs",
                        "openvpn",
                        "postgres",
                        "redis",
                        "tomcat",
                        "zookeeper",
                    ],
                ),
                state=dict(type="str", default="present", choices=["absent", "present"]),
                **super().base_module_args(),
            ),
            required_if=[
                [
                    "state",
                    "present",
                    [
                        "admin_emails",
                        "collection_slug",
                        "display_name",
                        "workload_slug",
                        "workload_type",
                    ],
                ],
                ["state", "absent", ["workload_slug"]],
            ],
            supports_check_mode=True,
        )


def main():
    module = AnsibleStepWorkload.define_module()

    agent = AnsibleStepWorkload(module)
    state = module.params.get("state")
    if state == "absent":
        agent.destroy_workload()
    elif state == "present":
        agent.check_workload()

    module.exit_json(**agent.get_result())


if __name__ == "__main__":
    main()
