import os
import yaml
from dotenv import load_dotenv

load_dotenv()

_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
_devices_path = os.path.join(os.path.dirname(__file__), "..", "config", "devices.yaml")


def _expand_env(value: str) -> str:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        key = value[2:-1]
        return os.environ.get(key, "")
    return value


def _resolve(data):
    if isinstance(data, dict):
        return {k: _resolve(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_resolve(i) for i in data]
    return _expand_env(data)


def get_config() -> dict:
    env = os.environ.get("ENV", "staging")
    with open(_config_path) as f:
        raw = yaml.safe_load(f)
    return _resolve(raw.get(env, {}))


def get_device_caps(platform: str) -> dict:
    with open(_devices_path) as f:
        raw = yaml.safe_load(f)
    return _resolve(raw.get(platform, {}))
