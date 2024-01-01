from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from uuid import uuid4
from typing import Optional

from rapida.requester import Requests


class RapidaStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass(kw_only=True)
class RapidaNodeConfig:
    parent_job_id: Optional[str] = None
    name: Optional[str] = None
    description: str = ""
    custom_properties: dict[str, str] = field(default_factory=dict)


@dataclass(kw_only=True)
class RapidaNode(RapidaNodeConfig):
    job: "RapidaJob"
    id: str = field(default_factory=lambda: str(uuid4()))
    status: RapidaStatus = RapidaStatus.PENDING
    requester: Requests = field(default_factory=Requests)

    def to_dict(self):
        return {
            "id": self.id,
            "job": self.job.id,
            "parentJobId": self.parent_job_id,
            "name": self.name,
            "description": self.description,
            "customProperties": self.custom_properties,
        }

    def __post_init__(self):
        self.requester.post(
            "/node",
            json=self.to_dict(),
        )

    def create_child_node(self, config: RapidaNodeConfig) -> "RapidaNode":
        task_data = asdict(config)
        task_data["parent_job_id"] = self.id
        return RapidaNode(job=self.job, **task_data)

    def _is_completed(self) -> bool:
        return self.status == RapidaStatus.SUCCESS or self.status == RapidaStatus.FAILED

    def set_status(self, status: RapidaNodeConfig):
        self.requester.patch(
            f"/node/{self.id}/status",
            json={
                "status": status.name
            }
        )
        self.status = status

    def success(self):
        self.set_status(RapidaStatus.SUCCESS)

    def fail(self):
        self.set_status(RapidaStatus.FAILED)

    def cancel(self):
        self.set_status(RapidaStatus.CANCELLED)


@dataclass
class RapidaJob:
    name: str
    description: str = ""
    custom_properties: dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 60
    status: RapidaStatus = RapidaStatus.PENDING
    requester: Requests = field(default_factory=Requests)
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "customProperties": self.custom_properties,
            "timeoutSeconds": self.timeout_seconds,
            "status": self.status.name
        }

    def __post_init__(self):
        self.requester.post(
            "/job",
            json=self.to_dict()
        )

    def _is_completed(self) -> bool:
        return self.status == RapidaStatus.SUCCESS or self.status == RapidaStatus.FAILED

    def create_node(self, config: RapidaNodeConfig) -> RapidaNode:
        task_data = asdict(config)
        return RapidaNode(job=self, **task_data)

    def set_status(self, status: RapidaStatus):
        self.requester.patch(
            f"/job/{self.id}/status",
            json={
                "status": status.name
            }
        )
        self.status = status

    def success(self):
        self.set_status(RapidaStatus.SUCCESS)

    def fail(self):
        self.set_status(RapidaStatus.FAILED)

    def cancel(self):
        self.set_status(RapidaStatus.CANCELLED)
