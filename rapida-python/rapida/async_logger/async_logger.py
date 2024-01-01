import dataclasses
import datetime
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from rapida.requester import Requests

from rapida.globals.rapida import rapida_global


@dataclass
class ProviderRequest:
    url: str
    json: dict
    meta: dict


@dataclass
class ProviderResponse:
    json: dict
    status: int
    headers: dict


@dataclass
class UnixTimeStamp:
    seconds: int
    milliseconds: int

    @staticmethod
    def from_datetime(dt: datetime) -> 'UnixTimeStamp':
        timestamp = dt.timestamp()
        seconds = int(timestamp)
        milliseconds = int((timestamp - seconds) * 1000)
        return UnixTimeStamp(seconds, milliseconds)


@dataclass
class Timing:
    startTime: UnixTimeStamp
    endTime: UnixTimeStamp

    @staticmethod
    def from_datetimes(start: datetime, end: datetime) -> 'Timing':
        start_timestamp = UnixTimeStamp.from_datetime(start)
        end_timestamp = UnixTimeStamp.from_datetime(end)
        return Timing(start_timestamp, end_timestamp)


@dataclass
class RapidaAyncLogRequest:
    providerRequest: ProviderRequest
    providerResponse: ProviderResponse
    timing: Timing


@dataclass
class RapidaMeta:
    custom_properties: Optional[dict]
    user_id: Optional[str]


class Provider(Enum):
    OPENAI = "openai"
    AZURE_OPENAI = "azure-openai"
    ANTHROPIC = "anthropic"


class RapidaAsyncLogger:
    requests: Requests

    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key:  Optional[str] = None,
                 ) -> None:
        self.requests = Requests(base_url, api_key)

    @staticmethod
    def from_rapida_global() -> 'RapidaAsyncLogger':
        return RapidaAsyncLogger()

    def log(self, request: RapidaAyncLogRequest,
            provider: Provider,
            meta: Optional[RapidaMeta] = None
            ):
        if provider == Provider.OPENAI:
            self.requests.post(
                json=dataclasses.asdict(request),
                path="/oai/v1/log"
            )
        elif provider == Provider.AZURE_OPENAI:
            self.requests.post(
                path="/oai/v1/log",
                json=dataclasses.asdict(request),
            )
        elif provider == Provider.ANTHROPIC:
            self.requests.post(
                path="/anthropic/v1/log",
                json=dataclasses.asdict(request),
            )
        else:
            raise ValueError(f"Unknown provider {provider}")
