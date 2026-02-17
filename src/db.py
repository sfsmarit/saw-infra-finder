from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os
import pandas as pd
import re

load_dotenv()


def load(table_name: str) -> pd.DataFrame:
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    db = os.getenv("DB_NAME", "saw")
    ssl_ca = os.getenv("DB_SSL_CA")  # 省略可

    query = f"SELECT * FROM {table_name}"

    connect_args = {}
    if ssl_ca:
        connect_args["ssl"] = {"ca": ssl_ca}

    url = URL.create(
        drivername="mysql+pymysql",
        username=user,
        password=password,   # URL.create が適切にエスケープしてくれる
        host=host,
        database=db,
        query={"charset": "utf8mb4"},
    )

    engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    if "mps" in table_name:
        df = add_piezo_column_for_mps(df)

    return df


def add_piezo_column_for_mps(df: pd.DataFrame) -> pd.DataFrame:
    # MPSの場合: LTxx を抽出して xx_LT に変換
    pat = re.compile(r'(?i)(LT\d{2,3})(?!\d)')
    df['piezo'] = df['name'].str.extract(pat, expand=False)  # type: ignore
    df['piezo'] = (
        df['piezo']
        .str.replace(r'^LT(\d{2,3})(?!\d)$', r'\1_LT', regex=True)
    )
    df['piezo'] = df['piezo'].fillna('42_LT')
    return df


if __name__ == "__main__":
    df = load("comparams")
    print(df)
    # for _, row in df.iterrows():
    #    print(f"piezo={row['piezo']}\t{row['name']}")
