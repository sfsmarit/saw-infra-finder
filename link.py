from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.mpar import MparDict
    from src.rpar import RparDict

from pathlib import Path
import json


def _get_layer_value(stack: dict, layer: str):
    """スタック情報から指定した layer_name の値を取得する"""
    for s in stack.keys():
        if layer.lower() in s.lower():
            return stack[s]
    return None


def _is_same_mps_stack(mpar_stack: dict, rpar_stack: dict) -> bool:
    """m_stack と r_stack が同じスタックを表しているかどうかを判定する"""
    target_layers = ["Al", "Mo", "LT", "SiO2", "piezo"]
    for layer in target_layers:
        mpar_value = _get_layer_value(mpar_stack, layer)
        rpar_value = _get_layer_value(rpar_stack, layer)
        # print(layer, mpar_value, rpar_value)
        # print("---")
        # 両方とも値がない場合はスタックに含まれないとみなす
        if mpar_value is None and rpar_value is None:
            continue
        # 片方に値があってもう片方に値がない場合や、両方に値があって値が異なる場合はスタックが異なるとみなす
        if mpar_value != rpar_value:
            return False
    return True


def _is_same_tcsaw_stack(mpar_stack: dict, rpar_stack: dict) -> bool:
    return False


def find_rpars_from_mpar(rpars: dict[str, RparDict], mpar: MparDict) -> list[str]:
    mpar_name = Path(mpar["path"]).name
    mpar_stack = mpar["stack"]
    is_mps = "mps" in mpar_name.lower()

    rpar_names = []
    for name, rpar in rpars.items():
        # mpar 名が一致する rpar を探す
        if rpar["mpar"] == mpar_name:
            rpar_names.append(name)
            continue

        # mpar と rpar のスタックが同じであれば、mpar 名が一致しなくても rpar をリンクする
        r_stack = rpar["stack"]

        if is_mps:
            if _is_same_mps_stack(mpar_stack, r_stack):
                rpar_names.append(name)
        else:
            if _is_same_tcsaw_stack(mpar_stack, r_stack):
                rpar_names.append(name)

    return rpar_names


def link_mpar():
    dst = "output/link_mpar.json"

    # Mpar 読み込み
    with open("output/mpar.json", "r", encoding="utf-8") as f:
        mpars: dict[str, MparDict] = json.load(f)

    # Rpar 読み込み
    with open("output/rpar.json", "r", encoding="utf-8") as f:
        rpars: dict[str, RparDict] = json.load(f)

    link = {}
    for name, mpar in mpars.items():
        link[name] = {
            "rpar": find_rpars_from_mpar(rpars, mpar),
        }
        # print(name)
        # print("\t", link[name])

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(link, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    link_mpar()
