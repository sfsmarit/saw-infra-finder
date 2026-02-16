import re
from pathlib import Path


class Rpar:
    def __init__(self, filepath) -> None:
        self.filepath = Path(filepath)
        self.load(filepath)

    def load(self, filepath):
        self.mpar: str = ""
        self.stack: dict = {}

        with open(filepath, "r", encoding="utf-8") as f:
            self.text = f.read()

        if "#parameter" in self.text:
            param = self._extract_parameter()
            if ".mpar" in param:
                self.mpar = param
            else:
                self.stack = self._extract_stack_from_parameter()

        if "#range" in self.text:
            self.stack = self._extract_stack_from_range()

    def to_dict(self) -> dict:
        return {
            "path": self.filepath.as_posix(),
            "mpar": self.mpar,
            "stack": self.stack
        }

    @property
    def name(self) -> str:
        return self.filepath.name

    def _extract_parameter(self) -> str:
        m = re.search(r'#parameter\s*"([^"]*)"', self.text)
        return m.group(1).strip() if m else ""

    def _extract_stack_from_range(self) -> dict:
        in_range = False
        current_key = None
        result: dict[str, float | int] = {}
        lines = self.text.splitlines()

        for raw in lines:
            line = raw.strip()
            if not line:
                continue

            # セクション開始/終了の検出
            if line.startswith("#"):
                in_range = line.lower() == "#range"
                current_key = None
                continue

            if not in_range:
                continue

            # キー行: 末尾が ":" の行（例: "Mo:"）
            if line.endswith(":"):
                current_key = line[:-1].strip()
                continue

            # 数値行（キー直下の最初のデータ行だけ処理）
            if current_key is not None:
                parts = [p.strip() for p in line.split(",") if p.strip()]
                if parts:
                    # 左端だけ取得
                    v = parts[0]
                    v = re.sub(r"[^0-9.+-Ee]", "", v)  # 万一の余計な記号を除去
                    try:
                        num = float(v)
                        num = int(num) if num.is_integer() else num
                        result[current_key] = num
                    except ValueError:
                        pass
                current_key = None  # そのキーは1行目だけ対象
        return result

    def _extract_stack_from_parameter(self) -> dict:
        m = re.search(r'"([^"]+)"', self.text)
        if not m:
            return {}
        inside = m.group(1)

        out: dict[str, float | int] = {}
        for item in inside.split(","):
            if "=" not in item:
                continue
            k, v = item.split("=", 1)
            k = k.strip()
            v = re.sub(r"\(.*?\)", "", v).strip()           # 注記の括弧を削除
            v = re.sub(r"[^0-9.+-]", "", v)                 # 単位など数字以外を全削除
            if not v:
                continue
            try:
                num = float(v)
                out[k] = int(num) if num.is_integer() else num
            except ValueError:
                continue
        return out


if __name__ == "__main__":
    rpar = Rpar("local/COMlib_15.mps.rpar")
    for k, v in rpar.to_dict().items():
        print(f"{k}: {v}")
