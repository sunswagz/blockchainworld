"""Contracts for read-only DEX adapters; intentionally no transaction interface."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class AdapterCapability:
    chain_key: str
    protocol_key: str
    capabilities: tuple[str, ...]
    read_only: bool = True

class ReadOnlyDexAdapter(ABC):
    @property
    @abstractmethod
    def capability(self) -> AdapterCapability: ...

    @abstractmethod
    def discover_pools(self, **filters: Any) -> list[dict[str, Any]]:
        """Return normalized pool candidates with source provenance."""

    @abstractmethod
    def discover_positions(self, wallet: str, **filters: Any) -> list[dict[str, Any]]:
        """Return wallet positions; missing fields must remain None."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        forbidden = {"sign","approve","send_transaction","broadcast","transact"}
        if forbidden.intersection(name.lower() for name in cls.__dict__):
            raise TypeError("DEX adapters must remain read-only")
