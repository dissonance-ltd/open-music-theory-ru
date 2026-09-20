"""UTF-8 input, schema errors, hashes and per-file atomic replacement."""

import hashlib
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml
from pydantic import BaseModel, ValidationError

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class InputError(ValueError):
    """An input file or source page cannot be processed."""


def validate_data[Model: BaseModel](data: object, schema: type[Model], source: Path) -> Model:
    try:
        return schema.model_validate(data)
    except ValidationError as error:
        problems = []
        for detail in error.errors(include_url=False, include_input=False):
            location = ".".join(str(part) for part in detail["loc"]) or "<root>"
            problems.append(f"{location}: {detail['msg']}")
        raise InputError(f"{source}:\n  " + "\n  ".join(problems)) from error


def read_json[Model: BaseModel](path: Path, schema: type[Model]) -> Model:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise InputError(f"{path}:{error.lineno}:{error.colno}: {error.msg}") from error
    return validate_data(data, schema, path)


def read_yaml[Model: BaseModel](path: Path, schema: type[Model]) -> Model:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise InputError(f"{path}: invalid YAML: {error}") from error
    return validate_data(data, schema, path)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes())


def encode_json(model: BaseModel) -> bytes:
    """Preserve the existing pretty-printed, non-ASCII-escaped JSON format."""
    data = model.model_dump(mode="json", exclude_unset=True)
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_bytes(path: Path, content: bytes) -> None:
    """Replace one file atomically; this is not a transaction across files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_json(path: Path, model: BaseModel) -> None:
    write_bytes(path, encode_json(model))
