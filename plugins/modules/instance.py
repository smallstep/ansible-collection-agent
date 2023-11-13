#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Smallstep Labs, Inc. <techadmin@smallstep.com>
# Apache-2.0 (see LICENSE or https://opensource.org/license/apache-2-0/)

DOCUMENTATION = """
---
module: collection

short_description: Manage a Smallstep Device Collection instance

description:
    - Manage a Smallstep Device Collection instance

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
            - The Device Collection slug of the instance.
            - This is the Device Collection you are adding the instance to.
            - Required.
        type: str
    instance_id:
        description:
            - The ID of the instance.
            - Example AWS i-0eebba999846bb1 EC2 instance ID
            - Example GCP 33322448555564760720 VM instance ID
            - Example Azure 6481a05f-1887-4156-ba64-4d1650811b48 This is the instances Managed Identity UUID
            - Example TPM urn ek sha256 RAzbOveN1Y45fYubuTxu5jOXWtOK1HbfZ7yHjBuWlyE This is the SHA256 hash of the endorsement key
            - Required.
        type: str
    instance_metadata:
        description:
            - The metadata on the Device Collection instance.
            - A list of dictionaries Name nginx-01, role webserver, env prod
        type: dict
        default: {}
        elements: dict
    state:
        description:
            - State of the instance.
        default: present
        choices: [ absent, present ]
        type: str
"""

EXAMPLES = """
- name: Create a Smallstep Device Collection instance
  smallstep.agent.instance:
    collection_slug: hotdog-production
    instance_id: i-0d69ab001748abd98
    instance_metadata:
        name: nginx-01
        role: webserver
        env: prod
    api_token: "eyJUzI1NiI..."
    state: present
"""

RETURN = """
smallstep_instance:
    description: Manage Smallstep Collection Instances
    returned: Always
    type: complex
    contains:
    smallstep_instance:
        collection_slug: hotdog-production
        fingerprint: 6a57e47f8aee2ff162415f9d592ccf52ab3681c964c66c122aadd1287ff57112
        instance_id: i-0d69ab001748abd98
        instance_metadata:
          Name: nginx-01
          demo_family: ubuntu
          driver: jdoss
          location: us-east-2
          role: webserver
          env: prod
          smallstep_collection: hotdog-production
        response:
          createdAt: '2023-10-06T17:43:16.878098+00:00'
          data:
            Name: smallstep-demo
            location: us-east-2
            smallstep_collection: hotdog-production
          id: i-0d69ab001748abd98
          updatedAt: '2023-10-06T17:43:16.878098+00:00'
        team: jdoss
    """

# noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible.module_utils.common.text.converters import to_native  # noqa: E402
from smallstep import api as step  # noqa: E402
from smallstep.exceptions import StepException  # noqa: E402

from ..module_utils.agent import AnsibleStep  # noqa: E402


class AnsibleStepInstance(AnsibleStep):
    def __init__(self, module):
        super().__init__(module, "smallstep_instance")
        self.smallstep_instance = None

        self.api_host = self.module.params.get("api_host")
        self.connectargs = {
            "smallstep_api_host": f"https://{self.api_host}/api",
            "smallstep_api_token": self.module.params.get("api_token"),
        }

    def _prep_result(self):
        api_info = super().api_info(connectargs=self.connectargs)
        return {
            "collection_slug": to_native(self.module.params.get("collection_slug")),
            "instance_metadata": self.module.params.get("instance_metadata"),
            "instance_id": self.module.params.get("instance_id"),
            "team": api_info["team"],
            "fingerprint": api_info["fingerprint"],
            "response": self.smallstep_instance,
        }

    def _get_instance(self):
        self.module.fail_on_missing_params(required_params=["collection_slug", "instance_id"])
        try:
            if self.module.params.get("collection_slug") and self.module.params.get("instance_id") is not None:
                instance = step.StepCollection(**self.connectargs)
                res = instance.get_instance(
                    collection_slug=self.module.params.get("collection_slug"),
                    instance_id=self.module.params.get("instance_id"),
                ).to_dict()
                self.smallstep_instance = res

        except StepException as exception:
            if exception.status_code == 404:
                self.smallstep_instance = None
                return
            if exception.status_code == 409:
                self.smallstep_instance = res
                return
            else:
                self.fail_json(
                    status_code=exception.status_code,
                    headers=exception.headers,
                    message=exception.message,
                )

    def _create_instance(self):
        self.module.fail_on_missing_params(required_params=["collection_slug", "instance_metadata", "instance_id"])

        params = {
            "collection_slug": self.module.params.get("collection_slug"),
            "instance_id": self.module.params.get("instance_id"),
            "instance_metadata": self.module.params.get("instance_metadata"),
        }

        if not self.module.check_mode:
            try:
                instance = step.StepCollection(**self.connectargs)
                instance.create_instance(
                    collection_slug=params["collection_slug"],
                    instance_metadata=params["instance_metadata"],
                    instance_id=params["instance_id"],
                ).to_dict()
                self._mark_changed()
                self._get_instance()
            except StepException as exception:
                self.fail_json(
                    status_code=exception.status_code,
                    headers=exception.headers,
                    message=exception.message,
                )

    def _update_instance(self):
        self.module.fail_on_missing_params(required_params=["instance_metadata", "collection_slug"])

        new_data = self.module.params.get("instance_metadata")
        old_data = self.smallstep_instance["data"]
        old_data.pop("smallstep:host:id", None)

        if new_data is not None and old_data != new_data:
            if not self.module.check_mode:
                try:
                    instance = step.StepCollection(**self.connectargs)
                    instance.update_instance(
                        collection_slug=self.module.params.get("collection_slug"),
                        instance_id=self.module.params.get("instance_id"),
                        instance_metadata=new_data,
                    )
                    self._mark_changed()
                    self._get_instance()
                except StepException as exception:
                    self.fail_json(
                        status_code=exception.status_code,
                        headers=exception.headers,
                        message=exception.message,
                    )

    def check_instance(self):
        self._get_instance()
        if self.smallstep_instance is None:
            self._create_instance()
        else:
            self._update_instance()

    def destroy_instance(self):
        self.module.fail_on_missing_params(required_params=["collection_slug", "instance_id"])
        self._get_instance()
        if self.smallstep_instance is not None:
            if not self.module.check_mode:
                try:
                    instance = step.StepCollection(**self.connectargs)
                    instance.destroy_instance(
                        collection_slug=self.module.params.get("collection_slug"),
                        instance_id=self.module.params.get("instance_id"),
                    )
                    self._mark_changed()
                    self._get_instance()
                except StepException as exception:
                    self.fail_json(
                        status_code=exception.status_code,
                        headers=exception.headers,
                        message=exception.message,
                    )

    @classmethod
    def define_module(cls):
        return AnsibleModule(
            argument_spec=dict(
                collection_slug=dict(type="str", required=True),
                instance_id=dict(type="str", required=True),
                instance_metadata=dict(type="dict", default={}),
                state=dict(type="str", default="present", choices=["absent", "present"]),
                **super().base_module_args(),
            ),
            required_if=[
                [
                    "state",
                    "present",
                    [
                        "instance_id",
                        "instance_metadata",
                        "collection_slug",
                    ],
                ],
                ["state", "absent", ["collection_slug", "instance_id"]],
            ],
            supports_check_mode=True,
        )


def main():
    module = AnsibleStepInstance.define_module()

    agent = AnsibleStepInstance(module)
    state = module.params.get("state")
    if state == "absent":
        agent.destroy_instance()
    elif state == "present":
        agent.check_instance()

    module.exit_json(**agent.get_result())


if __name__ == "__main__":
    main()
