import os
import requests
import psycopg2
from clickhouse_driver import Client
import redis
from dotenv import load_dotenv
load_dotenv()

COINS = ["bitcoin", "ethereum"]


def fetch_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": ",".join(COINS)}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def write_clickhouse(data):
    client = Client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 9000)),
        user=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "default"),
    )
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS market (
            id String,
            symbol String,
            price Float64,
            ts DateTime DEFAULT now()
        ) ENGINE = MergeTree ORDER BY ts
        """
    )
    rows = [(d["id"], d["symbol"], d["current_price"]) for d in data]
    client.execute("INSERT INTO market (id, symbol, price) VALUES", rows)


def write_postgres(data):
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        dbname=os.getenv("POSTGRES_DB", "app"),
    )
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS market(
            id text,
            symbol text,
            price double precision,
            ts timestamp DEFAULT now()
        );
        """
    )
    for d in data:
        cur.execute(
            "INSERT INTO market (id, symbol, price) VALUES (%s, %s, %s)",
            (d["id"], d["symbol"], d["current_price"]),
        )
    conn.commit()
    cur.close()
    conn.close()


def write_redis(data):
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True,
    )
    for d in data:
        r.hset(
            f"coin:{d['id']}",
            mapping={"symbol": d["symbol"], "price": d["current_price"]},
        )


def main():
    data = fetch_prices()
    write_clickhouse(data)
    write_postgres(data)
    write_redis(data)


if __name__ == "__main__":
    main()
