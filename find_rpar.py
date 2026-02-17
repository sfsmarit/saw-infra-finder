import os
from pathlib import Path
import json
import re

from rpar import Rpar


SUFFIX = ".rpar"


def get_filepaths(root_dir: str) -> list[Path]:
    result = []
    root = Path(root_dir)
    if root.is_dir():
        result.extend(root.rglob(f"*{SUFFIX}"))
    elif root.is_file() and root.suffix == SUFFIX:
        result.append(root)
    return result


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]


def sort_dict_natural(d: dict[str, object]) -> dict[str, object]:
    keys = sorted(d.keys(), key=natural_key)
    return {k: d[k] for k in keys}


if __name__ == "__main__":
    dst = "output/rpar.json"

    if os.name == "nt":
        root_dirs = {
            "all": "local/"
        }
    else:
        root_dirs = {
            "all": "/rds/devel/R/HOTCODE/amslibs/oa614/cdslibs/saw2_lb/comLib/COM/"
        }

    mpars = {}
    if Path("output/mpar.json").exists():
        with open("output/mpar.json", "r", encoding="utf-8") as f:
            mpars = json.load(f)

    result = {}
    for tech, root_dir in root_dirs.items():
        # Find all .mpar files in the root directory and its subdirectories
        paths = get_filepaths(root_dir)

        # Create Mpar objects from the paths and store their dictionary representations in the mpars dictionary
        for i, path in enumerate(paths):
            rpar = Rpar(path)

            # 対応するMparが分かっている場合は、MparのスタックをRparのスタックに追加する
            if mpars and rpar.mpar_stem:
                mpar = mpars.get(rpar.mpar_stem, {})
                mpar_stack = mpar.get("stack", {})
                rpar.stack |= mpar_stack

            result[rpar.name] = rpar.to_dict()
            print(f"[{i+1}/{len(paths)}] {rpar.name}")

    # Write the mpars dictionary to a JSON file
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(sort_dict_natural(result), f, indent=4, ensure_ascii=False)
