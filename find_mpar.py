import os
from pathlib import Path
import json
import re

from mpar import Mpar


SUFFIX = ".mpar"


def get_filepaths(root_dir: str) -> list[Path]:
    result = []
    root = Path(root_dir)
    if root.is_dir():
        result.extend(root.rglob(f"*{SUFFIX}"))
    elif root.is_file() and root.suffix == SUFFIX:
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


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]


def sort_dict_natural(d: dict[str, object]) -> dict[str, object]:
    keys = sorted(d.keys(), key=natural_key)
    return {k: d[k] for k in keys}


if __name__ == "__main__":
    dst = "output/mpar.json"

    if os.name == "nt":
        root_dirs = {
            "mps": "local/"
        }
    else:
        root_dirs = {
            "mps": "/prj/SAW_INFRA/MPS/"
        }

    result = {}
    for tech, root_dir in root_dirs.items():
        # Find all .mpar files in the root directory and its subdirectories
        paths = get_filepaths(root_dir)

        # Filter the paths to keep only those that are not contained in another path with a longer name
        paths = filter_by_name_containment_keep_longer(paths)

        # Create Mpar objects from the paths and store their dictionary representations in the mpars dictionary
        for i, path in enumerate(paths):
            mpar = Mpar(path)
            result[mpar.name] = mpar.to_dict()
            print(f"[{i+1}/{len(paths)}] {mpar.name}")

    # Write the mpars dictionary to a JSON file
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(sort_dict_natural(result), f, indent=4, ensure_ascii=False)
