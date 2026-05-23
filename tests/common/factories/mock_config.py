from dataclasses import asdict, dataclass, fields
from typing import TypeVar

MC = TypeVar("MC", bound="MockConfig")


@dataclass(frozen=True)
class MockConfig:
    @classmethod
    def from_child(cls: type[MC], child: "MockConfig") -> MC:
        cls_fields = {f.name for f in fields(cls)}
        filtered_child_dict = {k: v for k, v in asdict(child).items() if k in cls_fields}
        return cls(**filtered_child_dict)
