from __future__ import annotations

import shutil
from pathlib import Path
from typing import Tuple

from app.config import get_settings

settings = get_settings()


def save_pdf(filename: str, data: bytes) -> Tuple[Path, Path]:
    originals_dir = settings.storage_path / "originals"
    summaries_dir = settings.storage_path / "summaries"
    originals_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir.mkdir(parents=True, exist_ok=True)

    original_path = originals_dir / filename
    with open(original_path, "wb") as f:
        f.write(data)

    summary_path = summaries_dir / f"summary-{filename}"
    # For MVP we keep the same content as a placeholder summary document.
    shutil.copyfile(original_path, summary_path)

    return original_path, summary_path
