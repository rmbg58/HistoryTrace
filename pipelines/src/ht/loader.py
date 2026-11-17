"""数据加载与 JSON Schema 校验。"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

import jsonschema

from . import DATA_DIR


class LoadError(Exception):
    """数据装载/校验失败。"""


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except OSError as e:
        raise LoadError(f"无法读取 {path}: {e}") from e
    except json.JSONDecodeError as e:
        raise LoadError(f"JSON 解析失败 {path}: {e}") from e


@cache
def _schema(name: str) -> dict[str, Any]:
    return load_json(DATA_DIR / "schema" / f"{name}.schema.json")


def validate_against_schema(instance: dict[str, Any], schema_name: str, origin: Path) -> None:
    schema = _schema(schema_name)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    errors = sorted(validator_cls(schema).iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        loc = "/".join(str(p) for p in first.path) or "<root>"
        raise LoadError(f"schema 校验失败 {origin} @ {loc}: {first.message}")


@cache
def load_registry() -> dict[str, dict[str, Any]]:
    """加载全部 Source 注册,返回 {id: source}。"""
    registry: dict[str, dict[str, Any]] = {}
    for path in sorted((DATA_DIR / "registry" / "sources").glob("src_*.json")):
        src = load_json(path)
        validate_against_schema(src, "source", path)
        if src["id"] != path.stem:
            raise LoadError(f"来源 id 与文件名不一致: {path}")
        registry[src["id"]] = src
    return registry


@cache
def load_whitelist() -> dict[str, list[str]]:
    return load_json(DATA_DIR / "registry" / "whitelist.json")


def load_claims() -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for path in sorted((DATA_DIR / "claims").glob("clm_*.json")):
        claim = load_json(path)
        validate_against_schema(claim, "claim", path)
        claims.append(claim)
    return claims


def load_places() -> dict[str, Any]:
    path = DATA_DIR / "places.json"
    data = load_json(path)
    if not data.get("places"):
        raise LoadError(f"{path} 缺少 places")
    return data


def load_dynasties() -> list[dict[str, Any]]:
    return load_json(DATA_DIR / "dynasties.json")
