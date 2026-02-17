import os
from pathlib import Path
import json
import re
import pandas as pd

from src import db
from src.rpar import Rpar


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


def merge_mpar_stack(mpars: dict, rpar: Rpar):
    if not mpars or not rpar.mpar:
        return
    s = Path(rpar.mpar).stem
    for name, mpar in mpars.items():
        if s in name:
            rpar.stack |= mpar["stack"]
            return


def merge_db_stack_for_mps(rpar: Rpar, db: pd.DataFrame):
    row = db.loc[db["id"] == rpar.id, "piezo"]
    rpar.stack['piezo'] = row.iloc[0] if not row.empty else '42_LT'


def merge_db_stack_for_tcsaw(rpar: Rpar, db: pd.DataFrame):
    rpar.stack['piezo'] = ""


def is_valid(rpar: Rpar, db: pd.DataFrame) -> bool:
    row = db.loc[db["id"] == rpar.id, "version"]
    try:
        return int(row.iloc[0]) > 1
    except:
        return False


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

    df_mpsdb = db.load("comparamsmps2")
    df_tcsaw = db.load("comparams")

    result = {}
    for tech, root_dir in root_dirs.items():
        # Find all .mpar files in the root directory and its subdirectories
        paths = get_filepaths(root_dir)

        # Create Mpar objects from the paths and store their dictionary representations in the mpars dictionary
        for i, path in enumerate(paths):
            rpar = Rpar(path)

            if rpar.is_mps:
                df = df_mpsdb
            else:
                df = df_tcsaw

            if not is_valid(rpar, df):
                continue

            # Mpar が指定されていればMparのスタックを追加する
            merge_mpar_stack(mpars, rpar)

            # DB からもスタック情報を取得する
            if rpar.is_mps:
                merge_db_stack_for_mps(rpar, df_mpsdb)
            else:
                merge_db_stack_for_tcsaw(rpar, df_tcsaw)

            result[rpar.name] = rpar.to_dict()
            print(f"[{i+1}/{len(paths)}] {rpar.name}")

    # Write the mpars dictionary to a JSON file
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(sort_dict_natural(result), f, indent=4, ensure_ascii=False)
