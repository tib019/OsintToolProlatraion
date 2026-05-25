from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import asyncio
import time


class EntityType(str, Enum):
    PHONE_NUMBER = "PhoneNumber"
    EMAIL_ADDRESS = "EmailAddress"
    PERSON = "Person"
    USERNAME = "Username"
    SOCIAL_PROFILE = "SocialProfile"
    IP_ADDRESS = "IPAddress"
    DOMAIN = "Domain"
    ORGANIZATION = "Organization"
    LOCATION = "Location"
    LEAK_RECORD = "LeakRecord"


@dataclass
class Entity:
    type: EntityType
    value: str
    properties: dict[str, Any] = field(default_factory=dict)
    label: Optional[str] = None


@dataclass
class TransformResult:
    entities: list[Entity] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: int = 0


class BaseTransform(ABC):
    name: str = ""
    description: str = ""
    input_types: list[EntityType] = []
    output_types: list[EntityType] = []
    timeout: int = 10
    rate_limit: int = 10  # requests per minute

    @abstractmethod
    async def run(self, entity: Entity, api_keys: dict[str, str]) -> TransformResult:
        pass

    async def execute(self, entity: Entity, api_keys: dict[str, str]) -> TransformResult:
        start = time.monotonic()
        try:
            result = await asyncio.wait_for(
                self.run(entity, api_keys),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            result = TransformResult(error=f"Transform timed out after {self.timeout}s")
        except Exception as e:
            result = TransformResult(error=str(e))
        result.duration_ms = int((time.monotonic() - start) * 1000)
        return result
