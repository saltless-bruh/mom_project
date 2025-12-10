import yaml
from pathlib import Path

def load_config():
    root_dir = Path(__file__).parent.parent.parent
    config_path = root_dir / "config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
