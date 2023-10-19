# Copyright: (c) 2023, Smallstep Labs, Inc. <techadmin@smallstep.com>
# Apache-2.0 (see LICENSE or https://opensource.org/license/apache-2-0/)

import traceback
from collections.abc import Mapping

from ansible.module_utils.basic import env_fallback, missing_required_lib
from smallstep.api import StepAuthority
from smallstep.exceptions import StepException  # noqa: E402

HAS_SMALLSTEP_PYTHON = True

try:
    import smallstep  # noqa: F401
except ImportError:
    HAS_SMALLSTEP_PYTHON = False


class AnsibleStep:
    def __init__(self, module, represent):
        self.module = module
        self.represent = represent
        self.result = {"changed": False, self.represent: None}
        if not HAS_SMALLSTEP_PYTHON:
            module.fail_json(msg=missing_required_lib("smallstep-python"))

    def fail_json(self, exception, msg=None, params=None, **kwargs):
        last_traceback = traceback.format_exc()

        failure = {}

        if params is not None:
            failure["params"] = params

        if isinstance(exception, StepException):
            failure["status_code"] = exception.status_code
            failure["message"] = exception.message
            failure["headers"] = exception.headers

        exception_message = exception
        if msg is not None:
            msg = f"{exception_message}: {msg}"
        else:
            msg = exception_message

        self.module.fail_json(msg=msg, exception=last_traceback, failure=failure, **kwargs)

    def _mark_changed(self):
        self.result["changed"] = True

    def filter_none(self, d):
        if isinstance(d, Mapping):
            return {k: self.filter_none(v) for k, v in d.items() if v is not None}
        else:
            return d

    @classmethod
    def base_module_args(cls):
        return {
            "api_token": {
                "type": "str",
                "required": True,
                "fallback": (env_fallback, ["SMALLSTEP_API_HOST"]),
                "no_log": True,
            },
            "api_host": {"type": "str", "default": "gateway.smallstep.com"},
        }

    @classmethod
    def api_info(self, connectargs):
        self.api_info = {}
        try:
            authority = StepAuthority(**connectargs)
            auths = authority.get_all()

            auths_list = []

            for item in auths:
                auths_list.append(item.to_dict())

            agent_auth = next(
                (item for item in auths_list if item["domain"].startswith("agents.")),
                None,
            )
            self.api_info["fingerprint"] = agent_auth["fingerprint"]
            self.api_info["team"] = agent_auth["domain"].split(".")[1]

        except StepException as exception:
            self.fail_json(
                status_code=exception.status_code,
                headers=exception.headers,
                message=exception.message,
            )
        return self.api_info

    def _prep_result(self):
        """Prep the result for all modules

        :return: dict
        """
        return {}

    def get_result(self):
        if getattr(self, self.represent) is not None:
            self.result[self.represent] = self._prep_result()
        return self.result
