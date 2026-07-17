"""
用户评论情感分析系统 — 数据库入库模块
将清洗后的评论数据批量写入 MySQL
"""

import pymysql
import pandas as pd
from datetime import datetime
from typing import Optional

from config import DB_CONFIG, GENERATION_CONFIG


def create_connection() -> pymysql.Connection:
    """创建数据库连接"""
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset=DB_CONFIG["charset"],
        cursorclass=pymysql.cursors.DictCursor,
    )


def init_database(conn: pymysql.Connection) -> None:
    """初始化数据库表（运行 schema SQL）"""
    print("正在初始化数据库表...")
    with open("../sql/init.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    # 拆分为单条语句执行
    with conn.cursor() as cursor:
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                try:
                    cursor.execute(statement)
                except pymysql.err.ProgrammingError as e:
                    # 忽略 "database/table already exists" 及 USE 语句错误
                    if "exists" not in str(e).lower() and "Unknown database" not in str(e):
                        print(f"  [WARN] {e}")
    conn.commit()
    print("✓ 数据库表初始化完成")


def _parse_time(val) -> datetime:
    """解析时间字段，支持 datetime 和 str 类型"""
    if isinstance(val, datetime):
        return val
    return pd.to_datetime(val).to_pydatetime()


def batch_insert(df: pd.DataFrame, conn: pymysql.Connection) -> int:
    """
    批量插入评论数据

    Args:
        df: 评论 DataFrame
        conn: 数据库连接

    Returns:
        插入记录数
    """
    batch_size = GENERATION_CONFIG["batch_size"]
    total = len(df)

    insert_sql = """
        INSERT INTO comments
            (product_name, product_id, review_text, rating, review_time,
             reviewer_name, source)
        VALUES
            (%(product_name)s, %(product_id)s, %(review_text)s, %(rating)s,
             %(review_time)s, %(reviewer_name)s, %(source)s)
    """

    inserted = 0
    with conn.cursor() as cursor:
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            batch = df.iloc[start:end]

            # DataFrame rows → list of dicts
            records = []
            for _, row in batch.iterrows():
                records.append({
                    "product_name": row["product_name"],
                    "product_id": row["product_id"],
                    "review_text": row["review_text"],
                    "rating": int(row["rating"]),
                    "review_time": _parse_time(row["review_time"]),
                    "reviewer_name": row.get("reviewer_name", "匿名用户"),
                    "source": row.get("source", "模拟数据"),
                })

            cursor.executemany(insert_sql, records)
            conn.commit()
            inserted += len(records)
            print(f"  已写入 {inserted}/{total} 条记录...")

    return inserted


def verify_data(conn: pymysql.Connection) -> None:
    """验证入库数据"""
    print("\n" + "=" * 50)
    print("数据验证")
    print("=" * 50)

    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS cnt FROM comments")
        total = cursor.fetchone()["cnt"]
        print(f"  comments 表总记录: {total}")

        cursor.execute("""
            SELECT
                CASE
                    WHEN rating >= 4 THEN 'positive'
                    WHEN rating = 3 THEN 'neutral'
                    ELSE 'negative'
                END AS sentiment,
                COUNT(*) AS cnt
            FROM comments
            GROUP BY sentiment
            ORDER BY sentiment
        """)
        for row in cursor.fetchall():
            print(f"    {row['sentiment']}: {row['cnt']}")

        cursor.execute("""
            SELECT product_name, COUNT(*) AS cnt
            FROM comments
            GROUP BY product_name
            ORDER BY cnt DESC
        """)
        print(f"\n  商品分布:")
        for row in cursor.fetchall():
            print(f"    {row['product_name']}: {row['cnt']}")


def load_csv_to_db(csv_path: str = "cleaned_reviews.csv") -> None:
    """
    主流程: 读取 CSV → 写入 MySQL

    Args:
        csv_path: 清洗后 CSV 文件路径
    """
    print("=" * 50)
    print("数据入库模块")
    print("=" * 50)

    # 读取 CSV
    print(f"\n正在读取 {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"  读取到 {len(df)} 条记录")

    # 连接数据库
    print("\n正在连接 MySQL...")
    try:
        conn = create_connection()
        print("✓ 数据库连接成功")
    except pymysql.err.OperationalError as e:
        print(f"✗ 数据库连接失败: {e}")
        print("\n请检查 config.py 中的数据库配置:")
        print(f"  Host: {DB_CONFIG['host']}")
        print(f"  Port: {DB_CONFIG['port']}")
        print(f"  User: {DB_CONFIG['user']}")
        print(f"  Database: {DB_CONFIG['database']}")
        return

    try:
        # 批量插入
        print(f"\n正在批量写入 (batch_size={GENERATION_CONFIG['batch_size']})...")
        inserted = batch_insert(df, conn)
        print(f"\n✓ 入库完成，共写入 {inserted} 条记录")

        # 验证
        verify_data(conn)

    finally:
        conn.close()
        print("\n✓ 数据库连接已关闭")


if __name__ == "__main__":
    load_csv_to_db()
