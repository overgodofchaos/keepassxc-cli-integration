from pathlib import Path

PROJECT_PATH = Path().home() / ".keepassxc-cli-integration"
PROJECT_PATH.mkdir(exist_ok=True, parents=True)
ASSOCIATE_FILE = PROJECT_PATH / "associates.json"