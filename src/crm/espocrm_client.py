import logging
import urllib
from typing import Any

import requests

from ..models import ContactData
from ..settings import settings

logger = logging.getLogger(__name__)


class EspoAPIError(Exception):
    pass


def http_build_query(data: Any) -> str:
    parents = []
    pairs = {}

    def renderKey(parents: list[Any]) -> str:
        depth, outStr = 0, ""
        for x in parents:
            s = "[%s]" if depth > 0 or isinstance(x, int) else "%s"
            outStr += s % str(x)
            depth += 1
        return outStr

    def r_urlencode(data: Any) -> None:
        if isinstance(data, list) or isinstance(data, tuple):
            for i in range(len(data)):
                parents.append(i)
                r_urlencode(data[i])
                parents.pop()
        elif isinstance(data, dict):
            for key, value in data.items():
                parents.append(key)
                r_urlencode(value)
                parents.pop()
        else:
            pairs[renderKey(parents)] = str(data)

    r_urlencode(data)
    return urllib.parse.urlencode(pairs)


class EspoAPI:
    def __init__(self, url: str, api_key: str) -> None:
        self.url = url
        self.api_key = api_key
        self.status_code: int | None = None

    def request(
        self, method: str, action: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if params is None:
            params = {}

        headers = {"X-Api-Key": self.api_key}
        url = self.normalize_url(action)

        if method in ["POST", "PATCH", "PUT"]:
            response = requests.request(method, url, headers=headers, json=params)
        else:
            if params:
                url = url + "?" + http_build_query(params)
            response = requests.request(method, url, headers=headers)

        self.status_code = response.status_code

        if self.status_code != 200:
            reason = self.parse_reason(response.headers)
            raise EspoAPIError(
                f"Wrong request, status code is {response.status_code}, reason is {reason}"
            )

        data = response.content
        if not data:
            raise EspoAPIError("Wrong request, content response is empty")

        json_data = response.json()
        if not isinstance(json_data, dict):
            raise EspoAPIError("API response is not a JSON object")
        return json_data

    def download_file(self, action: str, params: dict[str, Any] | None = None) -> bytes:
        if params is None:
            params = {}

        headers = {"X-Api-Key": self.api_key}
        url = self.normalize_url(action)

        if params:
            url = url + "?" + http_build_query(params)

        response = requests.get(url, headers=headers)
        self.status_code = response.status_code

        if self.status_code != 200:
            reason = self.parse_reason(response.headers)
            raise EspoAPIError(
                f"Wrong request, status code is {response.status_code}, reason is {reason}"
            )

        return response.content

    def normalize_url(self, action: str) -> str:
        return self.url + "/" + action

    @staticmethod
    def parse_reason(headers: Any) -> str:
        if "X-Status-Reason" not in headers:
            return "Unknown Error"
        return str(headers["X-Status-Reason"])


class EspoCRMClient:
    def __init__(self) -> None:
        self.base_url = settings.espocrm_url.rstrip("/")
        self.api = EspoAPI(f"{self.base_url}/api/v1", settings.espocrm_api_key)

    def get_contact(self, contact_id: str) -> ContactData:
        try:
            data = self.api.request("GET", f"Contact/{contact_id}")
            return ContactData(
                id=data["id"],
                name=data.get("name"),
                firstName=data.get("firstName"),
                lastName=data.get("lastName"),
                emailAddress=data.get("emailAddress"),
                skills=data.get("skills"),
            )
        except EspoAPIError as e:
            logger.error(f"Error getting contact {contact_id}: {e}")
            raise ValueError(f"Failed to get contact: {e}")

    def get_contact_attachments(self, contact_id: str) -> list[dict[str, Any]]:
        try:
            data = self.api.request("GET", f"Contact/{contact_id}/attachments")
            return data.get("list", [])
        except EspoAPIError as e:
            logger.error(f"Error getting attachments for {contact_id}: {e}")
            return []

    def download_attachment(self, attachment_id: str) -> bytes | None:
        try:
            return self.api.download_file(f"Attachment/{attachment_id}/download")
        except EspoAPIError as e:
            logger.error(f"Error downloading attachment {attachment_id}: {e}")
            return None

    def update_contact_skills(self, contact_id: str, skills: list[str]) -> bool:
        try:
            skills_text = ", ".join(skills)
            self.api.request("PATCH", f"Contact/{contact_id}", {"skills": skills_text})
            logger.info(f"Successfully updated skills for contact {contact_id}")
            return True
        except EspoAPIError as e:
            logger.error(f"Error updating contact {contact_id}: {e}")
            return False

    def health_check(self) -> bool:
        try:
            self.api.request("GET", "")
            return True
        except Exception:
            return False
