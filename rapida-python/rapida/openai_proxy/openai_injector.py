from dataclasses import dataclass
import functools
from typing import Optional, TypedDict, Union
import uuid
import inspect
from rapida.globals import rapida_global
import openai
import requests
from openai.api_resources import (
    ChatCompletion,
    Completion,
    Edit,
    Embedding,
    Image,
    Moderation,
)
import logging
import threading

logger = logging.getLogger(__name__)


class AttributeDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def normalize_data_type(data_type):
    if isinstance(data_type, str):
        data_type = data_type.lower()

    if data_type in (str, "str", "string"):
        return "string"
    elif data_type in (bool, "bool", "boolean"):
        return "boolean"
    elif data_type in (float, int, "float", "int", "numerical"):
        return "numerical"
    elif data_type in (object, "object", "categorical"):
        return "categorical"
    else:
        raise ValueError(
            "Invalid data_type provided. Please use a valid data type or string.")


def prepare_api_base(**kwargs):
    original_api_base = openai.api_base
    if original_api_base != rapida_global.proxy_url:
        kwargs["headers"].update(
            {"Rapida-OpenAI-Api-Base": original_api_base})

    openai.api_base = rapida_global.proxy_url

    if openai.api_type == "azure":
        if rapida_global.proxy_url.endswith('/v1'):
            if rapida_global.proxy_url != "https://oai.hconeai.com/v1":
                logging.warning(
                    f"Detected likely invalid Azure API URL when proxying Rapida with proxy url {rapida_global.proxy_url}. Removing '/v1' from the end.")
            openai.api_base = rapida_global.proxy_url[:-3]

    return original_api_base, kwargs


@dataclass
class RapidaRetryProps:
    num: Optional[int] = None
    factor: Optional[float] = None
    min_timeout: Optional[float] = None
    max_timeout: Optional[float] = None


@dataclass
class RapidaProxyMeta:
    node_id: Optional[str] = None
    retry: Optional[Union[RapidaRetryProps, bool]] = False
    cache: Optional[bool] = False
    rate_limit_policy: Optional[str] = None


class OpenAIInjector:
    def __init__(self):
        self.openai = openai
        self.headers_store = {}

    def log_feedback(self, response, name, value, data_type=None):
        rapida_id = response.get("rapida", {}).get("id")
        if not rapida_id:
            raise ValueError(
                "The provided response does not have a valid Rapida ID.")

        feedback_data = {
            "rapida-id": rapida_id,
            "name": name,
            "value": value,
        }
        if data_type:
            feedback_data["data-type"] = normalize_data_type(data_type)

        url = f"{rapida_global.proxy_url}/feedback"

        headers = {
            "Content-Type": "application/json",
            "Rapida-Auth": f"Bearer {rapida_global.api_key}",
        }

        response = requests.post(url, headers=headers, json=feedback_data)
        if response.status_code != 200:
            logger.error(f"HTTP error occurred: {response.status_code}")
            logger.error(
                f"Response content: {response.content.decode('utf-8', 'ignore')}")

            response.raise_for_status()
        return response.json()

    def _pull_out_meta(self, **kwargs) -> tuple[RapidaProxyMeta, dict]:
        if ("rapidaMeta" in kwargs and isinstance(kwargs["rapidaMeta"], RapidaProxyMeta)):
            return kwargs.pop("rapidaMeta"), kwargs

        meta = RapidaProxyMeta()
        for key in RapidaProxyMeta.__annotations__.keys():
            if key in kwargs:
                setattr(meta, key, kwargs.pop(key))

        return meta, kwargs

    def _push_meta_to_headers(self, meta: RapidaProxyMeta, headers: dict) -> dict:
        if (meta.cache):
            headers["Rapida-Cache-Enabled"] = "true"
        if (meta.retry):
            if (isinstance(meta.retry, bool)):
                headers["Rapida-Retry-Enabled"] = "true" if meta.retry else "false"
            else:
                headers["Rapida-Retry-Enabled"] = "true"
                headers.update(self._get_retry_headers(meta.retry))
        if (meta.rate_limit_policy):
            headers["Rapida-RateLimit-Policy"] = meta.rate_limit_policy
        if (meta.node_id):
            headers["Rapida-Node-Id"] = meta.node_id
        return headers

    def _prepare_headers(self, **kwargs):
        headers = kwargs.get("headers", {})

        if "Rapida-Auth" not in headers and rapida_global.api_key:
            headers["Rapida-Auth"] = f"Bearer {rapida_global.api_key}"

        # Generate a UUID and add it to the headers
        rapida_request_id = str(uuid.uuid4())
        headers["rapida-request-id"] = rapida_request_id

        headers.update(self._get_property_headers(
            kwargs.pop("properties", {})))

        meta, kwargs = self._pull_out_meta(**kwargs)
        headers = self._push_meta_to_headers(meta, headers)

        kwargs["headers"] = headers

        return rapida_request_id, kwargs

    def update_response_headers(self, result, rapida_request_id):
        headers = self.headers_store.get(rapida_request_id, {})
        result["rapida"] = AttributeDict(
            id=headers.get("Rapida-Id"),
            status=headers.get("Rapida-Status"),
            cache=headers.get("Rapida-Cache"),
            rate_limit=AttributeDict(
                limit=headers.get("Rapida-RateLimit-Limit"),
                remaining=headers.get("Rapida-RateLimit-Remaining"),
                reset=headers.get("Rapida-RateLimit-Reset"),
                policy=headers.get("Rapida-RateLimit-Policy"),
            ) if headers.get("Rapida-RateLimit-Policy") else None,
        )

    def _modify_result(self, result, rapida_request_id):
        def result_with_rapida():
            for r in result:
                self.update_response_headers(r, rapida_request_id)
                yield r

        if inspect.isgenerator(result):
            return result_with_rapida()
        else:
            self.update_response_headers(result, rapida_request_id)
            return result

    async def _modify_result_async(self, result, rapida_request_id):
        async def result_with_rapida_async():
            async for r in result:
                self.update_response_headers(r, rapida_request_id)
                yield r

        if inspect.isasyncgen(result):
            return result_with_rapida_async()
        else:
            self.update_response_headers(result, rapida_request_id)
            return result

    def _with_rapida_auth(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            rapida_request_id, kwargs = self._prepare_headers(**kwargs)
            original_api_base, kwargs = prepare_api_base(**kwargs)

            try:
                result = func(*args, **kwargs)
            finally:
                openai.api_base = original_api_base

            return self._modify_result(result, rapida_request_id)

        return wrapper

    def _with_rapida_auth_async(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            rapida_request_id, kwargs = self._prepare_headers(**kwargs)
            original_api_base, kwargs = prepare_api_base(**kwargs)

            try:
                result = await func(*args, **kwargs)
            finally:
                openai.api_base = original_api_base

            return await self._modify_result_async(result, rapida_request_id)

        return wrapper

    def _get_property_headers(self, properties):
        return {f"Rapida-Property-{key}": str(value) for key, value in properties.items()}

    def _get_cache_headers(self, cache):
        return {"Rapida-Cache-Enabled": "true"} if cache is True else {}

    def _get_retry_headers(self, retry: Optional[RapidaRetryProps]) -> dict:
        headers = {}
        if (retry.num):
            headers["Rapida-Retry-Num"] = str(retry.num)
        if (retry.factor):
            headers["Rapida-Retry-Factor"] = str(retry.factor)
        if (retry.min_timeout):
            headers["Rapida-Retry-Min-Timeout"] = str(retry.min_timeout)
        if (retry.max_timeout):
            headers["Rapida-Retry-Max-Timeout"] = str(retry.max_timeout)
        return headers

    def apply_rapida_auth(self_parent):
        def request_raw_patched(self, *args, **kwargs):
            rapida_id = kwargs["supplied_headers"]["rapida-request-id"]
            response = original_request_raw(self, *args, **kwargs)
            if rapida_id:
                with threading.Lock():
                    self_parent.headers_store[rapida_id] = response.headers
            return response

        async def arequest_raw_patched(self, *args, **kwargs):
            rapida_id = kwargs["supplied_headers"]["rapida-request-id"]
            response = await original_arequest_raw(self, *args, **kwargs)
            if rapida_id:
                with threading.Lock():
                    self_parent.headers_store[rapida_id] = response.headers
            return response

        original_request_raw = openai.api_requestor.APIRequestor.request_raw
        openai.api_requestor.APIRequestor.request_raw = request_raw_patched

        original_arequest_raw = openai.api_requestor.APIRequestor.arequest_raw
        openai.api_requestor.APIRequestor.arequest_raw = arequest_raw_patched

        api_resources_classes = [
            (ChatCompletion, "create", "acreate"),
            (Completion, "create", "acreate"),
            (Edit, "create", "acreate"),
            (Embedding, "create", "acreate"),
            (Image, "create", "acreate"),
            (Moderation, "create", "acreate"),
        ]

        for api_resource_class, method, async_method in api_resources_classes:
            create_method = getattr(api_resource_class, method)
            setattr(api_resource_class, method,
                    self_parent._with_rapida_auth(create_method))

            async_create_method = getattr(api_resource_class, async_method)
            setattr(api_resource_class, async_method,
                    self_parent._with_rapida_auth_async(async_create_method))


injector = OpenAIInjector()
injector.apply_rapida_auth()
