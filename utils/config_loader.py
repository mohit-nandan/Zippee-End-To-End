import os
import string
import functools
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_config_path = Path(__file__).resolve().parent.parent / "config" / "config.yaml"
_devices_path = Path(__file__).resolve().parent.parent / "config" / "devices.yaml"


def _expand_env(value: str) -> str:
    if isinstance(value, str) and "${" in value:
        try:
            return string.Template(value).substitute(os.environ)
        except KeyError as exc:
            raise EnvironmentError(
                f"Required environment variable {exc} is not set. "
                f"Copy .env.example to .env and fill in the value."
            ) from exc
    return value


def _resolve(data):
    if isinstance(data, dict):
        return {k: _resolve(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_resolve(i) for i in data]
    return _expand_env(data)


def _load_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Config file not found at {path}. "
            "Ensure the file exists in the project root."
        )


@functools.lru_cache(maxsize=None)
def get_config(env: str = None) -> dict:
    env = env or os.environ.get("ENV", "staging")
    raw = _load_yaml(_config_path)
    return _resolve(raw.get(env, {}))


@functools.lru_cache(maxsize=None)
def get_device_caps(platform: str) -> dict:
    raw = _load_yaml(_devices_path)
    return _resolve(raw.get(platform, {}))
