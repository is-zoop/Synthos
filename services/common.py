"""Shared helpers for service-layer CRUD logic."""

from core.constants import STATUS_TEXT_MAP


def apply_model_updates(model, **kwargs) -> bool:
    updated = False
    for key, value in kwargs.items():
        if hasattr(model, key):
            setattr(model, key, value)
            updated = True
        else:
            print(f"[WARN] Unknown field ignored: {key}")
    return updated


def status_to_text(value: int) -> str:
    return STATUS_TEXT_MAP.get(value, "否")
