"""
用户评论情感分析系统 — 数据清洗模块
使用 Pandas 对生成的评论数据进行去重、去空、标准化处理
"""

import json
import pandas as pd
import re
from typing import Any


def load_reviews(filepath: str) -> list[dict[str, Any]]:
    """从 JSON 文件加载评论数据"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_reviews(reviews: list[dict[str, Any]]) -> pd.DataFrame:
    """
    清洗评论数据

    处理步骤:
    1. 转为 DataFrame
    2. 去除空值
    3. 去除重复评论
    4. 文本标准化（去除多余空格、特殊字符）
    5. 过滤过短评论（< 5 字符）
    6. 评分范围校验

    Args:
        reviews: 原始评论列表

    Returns:
        清洗后的 DataFrame
    """
    print(f"原始数据: {len(reviews)} 条")

    # Step 1: 转 DataFrame
    df = pd.DataFrame(reviews)
    print(f"  DataFrame 加载完成: {df.shape}")

    # Step 2: 去除空值（review_text 或 product_id 为空）
    before = len(df)
    df = df.dropna(subset=["review_text", "product_id", "product_name"])
    print(f"  去除空值: {before} → {len(df)} (移除 {before - len(df)} 条)")

    # Step 3: 去除完全重复的评论
    before = len(df)
    df = df.drop_duplicates(subset=["review_text"])
    print(f"  去除重复: {before} → {len(df)} (移除 {before - len(df)} 条)")

    # Step 4: 文本标准化
    def normalize_text(text: str) -> str:
        if not isinstance(text, str):
            return ""
        # 去除多余空白（包括全角空格）
        text = re.sub(r"[　\s]+", " ", text)
        # 去除首尾空白
        text = text.strip()
        # 统一省略号
        text = text.replace("…", "...").replace("。。。", "...")
        # 去除连续标点
        text = re.sub(r"！+", "！", text)
        text = re.sub(r"？+", "？", text)
        return text

    df["review_text"] = df["review_text"].apply(normalize_text)

    # Step 5: 过滤过短评论（纯标点或 < 5 个有效字符）
    def count_chinese_chars(text: str) -> int:
        """统计中文字符数"""
        return len(re.findall(r"[一-鿿]", text))

    before = len(df)
    df["chinese_count"] = df["review_text"].apply(count_chinese_chars)
    df = df[df["chinese_count"] >= 5]
    df = df.drop(columns=["chinese_count"])
    print(f"  过滤过短评论: {before} → {len(df)} (移除 {before - len(df)} 条)")

    # Step 6: 评分范围校验
    before = len(df)
    df = df[(df["rating"] >= 1) & (df["rating"] <= 5)]
    # 评分必须是整数
    df["rating"] = df["rating"].astype(int)
    print(f"  评分校验: {before} → {len(df)} (移除 {before - len(df)} 条)")

    # Step 7: review_time 转为标准 datetime
    df["review_time"] = pd.to_datetime(df["review_time"])

    print(f"\n✓ 清洗完成，最终数据: {len(df)} 条")

    # 打印质量报告
    print("\n" + "=" * 50)
    print("数据质量报告")
    print("=" * 50)
    print(f"  总记录数:     {len(df)}")
    print(f"  平均评论长度: {df['review_text'].str.len().mean():.1f} 字符")
    print(f"  平均评分:     {df['rating'].mean():.2f}")
    print(f"  评分分布:")
    for r in sorted(df["rating"].unique()):
        count = (df["rating"] == r).sum()
        print(f"    {r}分: {count} ({count/len(df)*100:.1f}%)")
    print(f"  商品数:       {df['product_id'].nunique()}")
    print(f"  时间跨度:     {df['review_time'].min()} ~ {df['review_time'].max()}")
    print(f"  空值检查:     review_text={df['review_text'].isna().sum()}, "
          f"product_id={df['product_id'].isna().sum()}")
    print("=" * 50)

    return df


if __name__ == "__main__":
    reviews = load_reviews("generated_reviews.json")
    df = clean_reviews(reviews)

    # 保存清洗后的数据
    output_path = "cleaned_reviews.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n✓ 清洗后数据已保存至 {output_path}")
