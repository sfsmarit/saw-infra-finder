import re
from pathlib import Path


class Mpar:
    def __init__(self, filepath) -> None:
        self.filepath = Path(filepath)
        self.load(filepath)

    def load(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            self.text = f.read()

        self.id = self._extract_tracking_id()
        self.stack = self._extract_stack()
        self.stack["piezo"], self.tech_ver = self._extract_piezo_and_version()

    def to_dict(self) -> dict:
        return {
            "path": self.filepath.as_posix(),
            "id": self.id,
            "tech_ver": self.tech_ver,
            "stack": self.stack
        }

    @property
    def name(self) -> str:
        return self.filepath.name

    def _extract_piezo_and_version(self):
        header_line = self.text.splitlines()[0]

        # piezo: "MPS/42_LT" のような "MPS/xxx" の xxx 部分
        m1 = re.search(r"MPS/([A-Za-z0-9_]+)", header_line)
        piezo = m1.group(1) if m1 else None

        # tech_ver: "V2.5" の 2.5 部分
        m2 = re.search(r"V([0-9]+(?:\.[0-9]+)?)", header_line)
        tech_ver = m2.group(1) if m2 else None

        return piezo, tech_ver

    def _extract_tracking_id(self) -> str | None:
        m = re.search(r"Tracking ID\s*:\s*([^\n\r]+)", self.text)
        return m.group(1).strip() if m else None        # Tracking ID is expected to be in the format "Tracking ID : <value>" in the .mpar file

    def _extract_stack(self) -> dict:
        m = re.search(r"\(([^)]*)\)", self.text)
        if not m:
            return {}

        inside = m.group(1)
        out: dict[str, float | int] = {}
        for it in inside.split("/"):
            it = it.strip()
            if "=" not in it:
                continue
            k, v = it.split("=", 1)
            k = k.strip()
            v = v.strip()
            # 末尾の n / nm を除去（大文字小文字を無視）
            v = re.sub(r"(?:nm|n)$", "", v, flags=re.IGNORECASE).strip()
            # 数字に変換（小数が無ければ int）
            try:
                num = float(v)
                num = int(num) if num.is_integer() else num
                out[k] = num
            except ValueError:
                # 数字でなければスキップ（必要ならそのまま保持に変更可）
                continue
        return out


if __name__ == "__main__":
    mpar = Mpar("local/MPS2.5_R042_Mo140_Al400_SiN10_LT0900_SiO2_0800_SOITEC_6inch_r0.1_MC5.mpar")
    for k, v in mpar.to_dict().items():
        print(f"{k}: {v}")
