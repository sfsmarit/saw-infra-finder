import os
from pathlib import Path
import json

from mpar import Mpar


SUFFIX = ".mpar"


def get_mpar_paths(root_dir: str) -> list[Path]:
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

    result = {}
    for tech, root_dir in root_dirs.items():
        # Find all .mpar files in the root directory and its subdirectories
        paths = get_mpar_paths(root_dir)

        # Filter the paths to keep only those that are not contained in another path with a longer name
        paths = filter_by_name_containment_keep_longer(paths)

        # Create Mpar objects from the paths and store their dictionary representations in the mpars dictionary
        for i, path in enumerate(paths):
            mpar = Mpar(path)
            result[mpar.name] = mpar.to_dict()
            print(f"[{i+1}/{len(paths)}] {mpar.name}")

    # Write the mpars dictionary to a JSON file
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
