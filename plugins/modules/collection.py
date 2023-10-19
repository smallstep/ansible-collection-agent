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
        - name: SMALLSTEP_API_host
        type: str
    api_host:
        description: The Smallstep host used when connecting.
        env:
        - name: SMALLSTEP_API_HOST
        type: str
    slug:
        description:
            - The slug of the collection.
            - Required.
        type: str
    name:
        description:
            - The name of the collection.
            - Required.
        type: str
    admin_emails:
        description:
            - Users that will have admin access to manage the agents authority,
            - Required.
        required: true
        type: list
        elements: str
    device_type:
        description:
            - The device type of the collection
            - Required.
        required: true
        type: dict
        elements: dict
        suboptions:
            aws_vm:
                type: list
                elements: dict
                suboptions:
                    accounts:
                        description:
                            - The list of AWS account IDs that are allowed to use this provisioner.
                            - Required for AWS device type.
                        type: list
                        elements: str
                        required: true
                    disable_custom_sans:
                        description:
                            - By default custom SANs are valid, but if this option is set to true only the SANs available in the instance identity document will be valid.
                            - These are the private IP and the DNS ip-..compute.internal.
                        type: bool
            azure_vm:
                type: dict
                suboptions:
                    audience:
                        description:
                            - Defaults to https://management.azure.com/ but it can be changed if necessary.
                        type: str
                        default: https://management.azure.com/
                        required: false
                    disable_custom_sans:
                        description:
                            - By default custom SANs are valid, but if this option is set to true only the SANs available in the instance identity document will be valid.
                            - These are the private IP and the DNS ip-..compute.internal.
                        type: bool
                        required: false
                    resource_groups:
                        description:
                            - The list of Azure resource group names that are allowed to use this provisioner.
                            - Required for Azure device type.
                        type: list
                        elements: str
                        required: true
                    tenant_id:
                        description:
                            - The Azure account tenant ID for this provisioner.
                            - This ID is the Directory ID available in the Azure Active Directory properties.
                            - Required for Azure device type.
                        type: bool
                        required: true
            gcp_vm:
                type: dict
                suboptions:
                    disable_custom_sans:
                        description:
                            - By default custom SANs are valid, but if this option is set to true only the SANs available in the instance identity document will be valid.
                            - These are the private IP and the DNS entries of the device.
                        type: bool
                        required: false
                    service_accounts:
                        description:
                            - List of GCP service accounts that are allowed to use this provisioner.
                            - Required for GCP device type.
                        type: list
                        elements: str
                        required: true
                    project_ids:
                        description:
                            - List of GCP Project IDs that are allowed to use this provisioner.
                            - Required for GCP device type.
                        type: list
                        elements: str
                        required: true
            tpm:
                type: dict
                suboptions:
                    attestor_roots:
                        description:
                            - The pem-encoded list of intermediate certificates used to build a chain of trust to verify the attestation certificates submitted by agents.
                            - Ignored if the team already has an attestation authority.
                        type: str
                        required: false
                    attestor_intermediates:
                        description:
                            - The pem-encoded list of certificates used to verify the attestation certificates submitted by agents. Ignored if the team already has an attestation authority.
                            - Required if the team does not already have an attestation authority.
                        type: str
                        required: false
                    force_cn:
                        description:
                            - Force one of the SANs to become the Common Name, if a Common Name is not provided.
                        type: bool
                        required: false
                    require_eab:
                        description:
                            - Only ACME clients that have been preconfigured with valid EAB credentials will be able to create an account with this provisioner.
                        type: bool
                        required: false
    state:
        description:
            - State of the instance.
        default: present
        choices: [ absent, present ]
        type: str
"""

EXAMPLES = """
- name: Manage Smallstep Collection for AWS
  smallstep.agent.collection:
    slug: "aws-nginx-demo"
    name: "AWS NGINX Demo"
    admin_emails:
        - jdoss@smallstep.com
    device_type:
        aws_vm:
            accounts:
                - "123456789011"
                - "222233334444"
            disable_custom_sans: True
    api_token: "eyJUzI1NiI..."

- name: Manage Smallstep Collection for Azure
  smallstep.agent.collection:
    slug: "azure-nginx-demo"
    name: "Azure NGINX Demo"
    admin_emails:
        - jdoss@smallstep.com
    device_type:
        azure_vm:
            resource_groups:
                - my-resource-group
                - my-other-resource-group
            tenant_id:
                - 847cb745-de21-4622-9c05-f15b069c3f04
            disable_custom_sans: True
    api_token: "eyJUzI1NiI..."

- name: Manage Smallstep Collection for GCP
  smallstep.agent.collection:
    slug: "gcp-nginx-demo"
    name: "GCP NGINX Demo"
    admin_emails:
        - jdoss@smallstep.com
    device_type:
        gcp_vm:
            project_ids:
            - prod
            - dev
            service_accounts:
                - production@prod.iam.gserviceaccount.com
                - development@dev.iam.gserviceaccount.com
            disable_custom_sans: True
    api_token: "eyJUzI1NiI..."
"""

RETURN = """
smallstep_collection:
    description: Manage a Smallstep Collection
    returned: Always
    type: complex
    contains:
    smallstep_collection:
        collection_slug: hotdog-production
        device_type:
          aws_vm:
            accounts:
            - '123456787908'
            disable_custom_sans: false
        display_name: Hotdog App production
        fingerprint: 6a57e47f8aee2ff162415f9d592ccf52ab3681c964c66c122aadd1287ff57112
        response:
          deviceType: aws-vm
          deviceTypeConfiguration:
            accounts:
            - '123456787908'
          displayName: Hotdog App production
          slug: hotdog-production
        team: jdoss
    """

# noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible.module_utils.common.text.converters import to_native  # noqa: E402
from smallstep import api as step  # noqa: E402
from smallstep.exceptions import StepException  # noqa: E402

from ..module_utils.agent import AnsibleStep  # noqa: E402


class AnsibleStepCollection(AnsibleStep):
    def __init__(self, module):
        super().__init__(module, "smallstep_collection")
        self.smallstep_collection = None

        self.api_host = self.module.params.get("api_host")
        self.connectargs = {
            "smallstep_api_host": f"https://{self.api_host}/api",
            "smallstep_api_token": self.module.params.get("api_token"),
        }

    def _prep_result(self):
        api_info = super().api_info(connectargs=self.connectargs)
        return {
            "collection_slug": to_native(self.module.params.get("collection_slug")),
            "display_name": to_native(self.module.params.get("display_name")),
            "device_type": self.module.params.get("device_type"),
            "team": api_info["team"],
            "fingerprint": api_info["fingerprint"],
            "response": self.smallstep_collection,
        }

    def _get_collection(self):
        self.module.fail_on_missing_params(required_params=["collection_slug"])
        try:
            if self.module.params.get("collection_slug") is not None:
                collection = step.StepDeviceCollection(**self.connectargs)
                res = collection.get(collection_slug=self.module.params.get("collection_slug")).to_dict()
                self.smallstep_collection = res

        except StepException as exception:
            if exception.status_code == 404:
                self.smallstep_collection = None
                return
            if exception.status_code == 409:
                self.smallstep_collection = res
                return
            else:
                self.fail_json(
                    status_code=exception.status_code,
                    headers=exception.headers,
                    message=exception.message,
                )

    def _create_collection(self):
        self.module.fail_on_missing_params(required_params=["collection_slug", "display_name", "device_type"])

        params = {
            "display_name": self.module.params.get("display_name"),
            "collection_slug": self.module.params.get("collection_slug"),
            "admin_emails": self.module.params.get("admin_emails"),
            "device_type": self.module.params.get("device_type"),
        }

        admin_emails = params["admin_emails"]
        device_type = next(iter(params["device_type"]))
        device_type_config = params["device_type"][device_type]

        if not self.module.check_mode:
            try:
                collection = step.StepDeviceCollection(**self.connectargs)
                collection.create(
                    collection_slug=params["collection_slug"],
                    collection_name=params["display_name"],
                    admin_emails=admin_emails,
                    device_type=device_type.replace("_", "-"),
                    **device_type_config,
                ).to_dict()
                self._mark_changed()
                self._get_collection()
            except StepException as exception:
                self.fail_json(
                    status_code=exception.status_code,
                    headers=exception.headers,
                    message=exception.message,
                )

    def _update_collection(self):
        self.module.fail_on_missing_params(required_params=["display_name", "collection_slug"])
        name = self.module.params.get("display_name")
        if name is not None and self.smallstep_collection["displayName"] != name:
            if not self.module.check_mode:
                try:
                    current = step.StepDeviceCollection(**self.connectargs)
                    data = current.get(collection_slug=self.module.params.get("collection_slug")).to_dict()
                    collection = step.StepDeviceCollection(**self.connectargs)
                    collection.update(
                        collection_slug=self.module.params.get("collection_slug"),
                        collection_name=self.module.params.get("display_name"),
                        collection_data=data,
                    )
                    self._mark_changed()
                    self._get_collection()
                except StepException as exception:
                    self.fail_json(
                        status_code=exception.status_code,
                        headers=exception.headers,
                        message=exception.message,
                    )

    def check_collection(self):
        self._get_collection()
        if self.smallstep_collection is None:
            self._create_collection()
        else:
            self._update_collection()

    def destroy_collection(self):
        self.module.fail_on_missing_params(required_params=["collection_slug"])
        self._get_collection()
        if self.smallstep_collection is not None:
            if not self.module.check_mode:
                try:
                    collection = step.StepDeviceCollection(**self.connectargs)
                    collection.destroy(collection_slug=self.module.params.get("collection_slug"))
                    self._mark_changed()
                    self._get_collection()
                except StepException as exception:
                    self.fail_json(exception)

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                collection_slug=dict(type="str", required=True),
                display_name=dict(type="str"),
                admin_emails=dict(type="list"),
                device_type=dict(
                    type="dict",
                    required_one_of=[("aws_vm", "azure_vm", "gcp_vm", "tpm")],
                    mutually_exclusive=[("aws_vm", "azure_vm", "gcp_vm", "tpm")],
                    options=dict(
                        aws_vm=dict(
                            type="dict",
                            options=dict(
                                accounts=dict(type="list", elements="str", required=True),
                                disable_custom_sans=dict(type="bool"),
                            ),
                        ),
                        azure_vm=dict(
                            type="dict",
                            options=dict(
                                resource_groups=dict(type="list", elements="str", required=True),
                                tenant_id=dict(type="str", required=True),
                                disable_custom_sans=dict(type="bool"),
                            ),
                        ),
                        gcp_vm=dict(
                            type="dict",
                            options=dict(
                                project_ids=dict(type="list", elements="str", required=True),
                                service_accounts=dict(type="list", elements="str", required=True),
                                disable_custom_sans=dict(type="bool"),
                            ),
                        ),
                        tpm=dict(
                            type="dict",
                            options=dict(
                                attestor_intermediates=dict(type="str"),
                                attestor_roots=dict(type="str"),
                                force_cn=dict(type="bool"),
                                require_eab=dict(type="bool"),
                            ),
                        ),
                    ),
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
                        "device_type",
                        "display_name",
                        "collection_slug",
                    ],
                ],
                ["state", "absent", ["collection_slug"]],
            ],
            supports_check_mode=True,
        )


def main():
    module = AnsibleStepCollection.define_module()

    module.params["device_type"] = {k: v for k, v in module.params["device_type"].items() if v is not None}

    agent = AnsibleStepCollection(module)
    state = module.params.get("state")
    if state == "absent":
        agent.destroy_collection()
    elif state == "present":
        agent.check_collection()

    module.exit_json(**agent.get_result())


if __name__ == "__main__":
    main()
