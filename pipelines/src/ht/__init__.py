"""HistoryTrace 数据管线包。"""

__version__ = "0.1.0"

# 仓库根目录(pipelines/ 的上一级)
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
WEB_PUBLIC_DATA = REPO_ROOT / "web" / "public" / "data"
