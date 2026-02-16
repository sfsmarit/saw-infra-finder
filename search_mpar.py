import os
from pathlib import Path
import json

from mpar import Mpar


def get_mpar_paths(root_dir: str) -> list[Path]:
    result = []
    root = Path(root_dir)
    if root.is_dir():
        result.extend(root.rglob("*.mpar"))
    elif root.is_file() and root.suffix == ".mpar":
        result.append(root)
    return result


def filter_by_name_containment_keep_longer(paths: list[Path]) -> list[Path]:
    items = [(p, p.stem) for p in paths]
    items.sort(key=lambda x: len(x[1]), reverse=True)
    kept: list[tuple[Path, str]] = []
    for p, stem in items:
        if any(stem in kept_stem for _, kept_stem in kept):
            continue
        kept.append((p, stem))
    return [p for p, _ in kept]


if __name__ == "__main__":
    if os.name == "nt":
        root_dirs = {
            "mps": "local/"
        }
    else:
        root_dirs = {
            "mps": "/prj/SAW_INFRA/MPS/"
        }

    dst = "output/mpar_path.json"

    mpars = {}
    for tech, root_dir in root_dirs.items():
        paths = get_mpar_paths(root_dir)
        paths = filter_by_name_containment_keep_longer(paths)

        for path in paths:
            mpar = Mpar(paths[0])
            mpars[mpar.name] = mpar.to_dict()

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(mpars, f, indent=4, ensure_ascii=False)
