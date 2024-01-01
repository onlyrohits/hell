from dataclasses import dataclass
import datetime
import functools
import inspect
import json
from typing import Callable, Optional
import openai  # noqa
from openai.api_resources import (ChatCompletion, Completion, Edit, Embedding,
                                  Image, Moderation)

from rapida.async_logger.async_logger import (RapidaAsyncLogger,
                                                RapidaAyncLogRequest,
                                                Provider, ProviderRequest,
                                                ProviderResponse, Timing)


@dataclass
class RapidaMeta:
    custom_properties: Optional[dict] = None
    user_id: Optional[str] = None
    node_id: Optional[str] = None

    def build(self) -> dict:
        meta = {}
        if self.custom_properties:
            for key, value in self.custom_properties.items():
                meta[f"Rapida-Property-{key}"] = value

        if self.user_id:
            meta["Rapida-User-Id"] = self.user_id

        if self.node_id:
            meta["Rapida-Node-Id"] = self.node_id

        return meta


class CreateArgsExtractor:
    _rapida_meta: Optional[RapidaMeta]

    def __init__(self,
                 api_key=None,
                 api_base=None,
                 api_type=None,
                 request_id=None,
                 api_version=None,
                 organization=None,
                 **kwargs):
        self.kwargs = kwargs
        self.kwargs["api_key"] = api_key
        self.kwargs["api_base"] = api_base
        self.kwargs["api_type"] = api_type
        self.kwargs["request_id"] = request_id
        self.kwargs["api_version"] = api_version
        self.kwargs["organization"] = organization
        self._rapida_meta = kwargs.get("rapida_meta")
        self.kwargs.pop("rapida_meta", None)

    def get_args(self):
        return self.kwargs

    def get_body(self):
        return self.kwargs

    def get_rapida_meta(self) -> dict:
        if (self._rapida_meta is None):
            return {}
        return self._rapida_meta.build()


class OpenAIInjector:
    def __init__(self):
        pass

    def update_response_headers(self, result, rapida_request_id):
        result["rapida_request_id"] = rapida_request_id

    def _result_interceptor(self,
                            result,
                            rapida_meta: dict,
                            send_response: Callable[[dict], None] = None):

        def generator_intercept_packets():
            response = {}
            response["streamed_data"] = []
            for r in result:
                r["rapida_meta"] = rapida_meta
                response["streamed_data"].append(json.loads(r.__str__()))
                yield r
            send_response(response)

        if inspect.isgenerator(result):
            return generator_intercept_packets()
        else:
            result["rapida_meta"] = rapida_meta
            send_response(json.loads(result.__str__()))

            return result

    def _result_interceptor_async(self,
                                  result,
                                  rapida_meta: dict,
                                  send_response: Callable[[dict], None] = None):

        async def generator_intercept_packets():
            response = {}
            response["streamed_data"] = []
            for r in result:
                r["rapida_meta"] = rapida_meta
                response["streamed_data"].append(json.loads(r.__str__()))
                yield r
            send_response(response)

        if inspect.isgenerator(result):
            return generator_intercept_packets()
        else:
            result["rapida_meta"] = rapida_meta
            send_response(json.loads(result.__str__()))

            return result

    def _with_rapida_auth(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = RapidaAsyncLogger.from_rapida_global()

            arg_extractor = CreateArgsExtractor(*args, **kwargs)
            now = datetime.datetime.now()

            providerRequest = ProviderRequest(
                url="N/A",
                json=arg_extractor.get_body(),
                meta=arg_extractor.get_rapida_meta()
            )
            print("providerRequest", providerRequest)
            try:
                result = func(**arg_extractor.get_args())
            except Exception as e:
                later = datetime.datetime.now()
                async_log = RapidaAyncLogRequest(
                    providerRequest=providerRequest,
                    providerResponse=ProviderResponse(
                        json={
                            "error": str(e)
                        },
                        status=500,
                        headers={
                            "openai-version": "ligmaligma"
                        }
                    ),
                    timing=Timing.from_datetimes(now, later)
                )
                logger.log(async_log, Provider.OPENAI)

                raise e

            def send_response(response):
                later = datetime.datetime.now()
                async_log = RapidaAyncLogRequest(
                    providerRequest=providerRequest,
                    providerResponse=ProviderResponse(
                        json=response,
                        status=200,
                        headers={
                            "openai-version": "ligmaligma"
                        }

                    ),
                    timing=Timing.from_datetimes(now, later)
                )
                logger.log(async_log, Provider.OPENAI)

            return self._result_interceptor(result,
                                            {},
                                            send_response)

        return wrapper

    def _with_rapida_auth_async(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = RapidaAsyncLogger.from_rapida_global()

            arg_extractor = CreateArgsExtractor(*args, **kwargs)
            now = datetime.datetime.now()

            providerRequest = ProviderRequest(
                url="N/A",
                json=arg_extractor.get_body(),
                meta=arg_extractor.get_rapida_meta()
            )
            try:
                result = await func(**arg_extractor.get_args())
            except Exception as e:
                later = datetime.datetime.now()
                async_log = RapidaAyncLogRequest(
                    providerRequest=providerRequest,
                    providerResponse=ProviderResponse(
                        json={
                            "error": str(e)
                        },
                        status=500,
                        headers={
                            "openai-version": "ligmaligma"
                        }
                    ),
                    timing=Timing.from_datetimes(now, later)
                )
                logger.log(async_log, Provider.OPENAI)

                raise e

            def send_response(response):
                later = datetime.datetime.now()
                async_log = RapidaAyncLogRequest(
                    providerRequest=providerRequest,
                    providerResponse=ProviderResponse(
                        json=response,
                        status=200,
                        headers={
                            "openai-version": "ligmaligma"
                        }

                    ),
                    timing=Timing.from_datetimes(now, later)
                )

                logger.log(async_log, Provider.OPENAI)

            return self._result_interceptor_async(result,
                                                  {},
                                                  send_response)

        return wrapper

    def apply_rapida_auth(self_parent):
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
