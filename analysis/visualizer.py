"""
用户评论情感分析系统 — 数据可视化模块
生成：情感分布饼图、趋势折线图、痛点柱状图、词云
"""

import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import json
import os
from collections import Counter
from wordcloud import WordCloud
import jieba

# ============================================================
# 全局配置
# ============================================================

# matplotlib 样式
plt.style.use('seaborn-v0_8-whitegrid')

# 中文字体配置（必须在样式设置之后，否则会被覆盖）
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'STXihei']
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['axes.unicode_minus'] = False
# 清除字体缓存
matplotlib.font_manager._load_fontmanager(try_read_cache=False)

# 数据库配置（与 crawler/config.py 保持一致）
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password_here",
    "database": "sentiment_analysis",
    "charset": "utf8mb4",
}

# 输出目录
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 中文字体文件路径（wordcloud 需要显式指定）
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

# 颜色方案
COLORS = {
    "positive": "#4CAF50",
    "negative": "#F44336",
    "neutral": "#9E9E9E",
}


def get_connection() -> pymysql.Connection:
    """创建数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def load_data(conn: pymysql.Connection) -> pd.DataFrame:
    """
    从数据库加载评论+分析结果合并数据
    """
    query = """
        SELECT
            c.id AS comment_id,
            c.product_name,
            c.review_text,
            c.rating,
            c.review_time,
            sr.sentiment_label,
            sr.confidence,
            sr.keywords,
            sr.aspect_keywords,
            sr.analysis_time
        FROM comments c
        LEFT JOIN sentiment_results sr ON c.id = sr.comment_id
    """
    df = pd.read_sql(query, conn)
    print(f"  加载数据: {len(df)} 条记录")
    return df


# ============================================================
# 图表1: 情感分布饼图
# ============================================================
def plot_sentiment_distribution(df: pd.DataFrame) -> None:
    """情感分布饼图"""
    print("\n[1/5] 生成情感分布饼图...")

    counts = df["sentiment_label"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ["正面", "负面", "中性"]
    label_keys = {"positive": "正面", "negative": "负面", "neutral": "中性"}
    sizes = [counts.get(k, 0) for k in ["positive", "negative", "neutral"]]
    colors_list = [COLORS["positive"], COLORS["negative"], COLORS["neutral"]]
    explode = (0.02, 0.02, 0.02)

    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors_list,
        autopct='%1.1f%%', startangle=140,
        textprops={'fontsize': 13}
    )
    for at in autotexts:
        at.set_fontweight('bold')

    total = len(df[df["sentiment_label"].notna()])
    ax.set_title(f"用户评论情感分布 (共 {total} 条分析评论)", fontsize=16, fontweight='bold', pad=20)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "sentiment_distribution.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ 保存至 {path}")


# ============================================================
# 图表2: 情感趋势折线图
# ============================================================
def plot_sentiment_trend(df: pd.DataFrame) -> None:
    """情感趋势折线图（按月统计）"""
    print("\n[2/5] 生成情感趋势折线图...")

    if df["review_time"].dtype == 'object':
        df["review_time"] = pd.to_datetime(df["review_time"])

    df_analyzed = df[df["sentiment_label"].notna()].copy()
    df_analyzed["month"] = df_analyzed["review_time"].dt.to_period("M")

    trend = df_analyzed.groupby(["month", "sentiment_label"]).size().unstack(fill_value=0)
    # 确保三列都存在
    for col in ["positive", "negative", "neutral"]:
        if col not in trend.columns:
            trend[col] = 0

    fig, ax = plt.subplots(figsize=(14, 6))

    x = range(len(trend.index))
    months_str = [str(m) for m in trend.index]

    ax.plot(x, trend["positive"], color=COLORS["positive"], marker='o', linewidth=2,
            markersize=6, label="正面")
    ax.plot(x, trend["negative"], color=COLORS["negative"], marker='s', linewidth=2,
            markersize=6, label="负面")
    ax.plot(x, trend["neutral"], color=COLORS["neutral"], marker='^', linewidth=2,
            markersize=6, label="中性")

    # 填充区域
    ax.fill_between(x, 0, trend["positive"], color=COLORS["positive"], alpha=0.1)
    ax.fill_between(x, 0, trend["negative"], color=COLORS["negative"], alpha=0.08)

    ax.set_xticks(x)
    ax.set_xticklabels(months_str, rotation=45, ha='right')
    ax.set_xlabel("月份", fontsize=12)
    ax.set_ylabel("评论数量", fontsize=12)
    ax.set_title("情感趋势分析 (月度)", fontsize=16, fontweight='bold')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "sentiment_trend.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ 保存至 {path}")


# ============================================================
# 图表3: 各商品情感对比柱状图
# ============================================================
def plot_product_comparison(df: pd.DataFrame) -> None:
    """各商品情感对比分组柱状图"""
    print("\n[3/5] 生成商品情感对比图...")

    df_analyzed = df[df["sentiment_label"].notna()]
    product_sentiment = df_analyzed.groupby(["product_name", "sentiment_label"]).size().unstack(fill_value=0)

    for col in ["positive", "negative", "neutral"]:
        if col not in product_sentiment.columns:
            product_sentiment[col] = 0

    product_sentiment = product_sentiment.sort_values("positive", ascending=False)

    fig, ax = plt.subplots(figsize=(14, 7))

    x = np.arange(len(product_sentiment.index))
    width = 0.25

    bars1 = ax.bar(x - width, product_sentiment["positive"], width,
                   color=COLORS["positive"], label="正面", edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x, product_sentiment["negative"], width,
                   color=COLORS["negative"], label="负面", edgecolor='white', linewidth=0.5)
    bars3 = ax.bar(x + width, product_sentiment["neutral"], width,
                   color=COLORS["neutral"], label="中性", edgecolor='white', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(product_sentiment.index, rotation=30, ha='right', fontsize=10)
    ax.set_ylabel("评论数量", fontsize=12)
    ax.set_title("各商品情感对比", fontsize=16, fontweight='bold')
    ax.legend(fontsize=11)

    # 数值标签
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., height + 5,
                        str(int(height)), ha='center', va='bottom', fontsize=7)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "product_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ 保存至 {path}")


# ============================================================
# 图表4: 负面评论词云
# ============================================================
def plot_wordcloud(df: pd.DataFrame) -> None:
    """负面评论词云"""
    print("\n[4/5] 生成词云...")

    # 提取所有负面评论的关键词
    negative_keywords = df[df["sentiment_label"] == "negative"]["keywords"].dropna()

    all_words = []
    for kw_json in negative_keywords:
        try:
            keywords = json.loads(kw_json) if isinstance(kw_json, str) else kw_json
            all_words.extend(keywords)
        except (json.JSONDecodeError, TypeError):
            continue

    if not all_words:
        # 如果没有足够的负面关键词，从评论文本中分词提取
        negative_texts = df[df["sentiment_label"] == "negative"]["review_text"].dropna()
        for text in negative_texts:
            words = jieba.cut(str(text))
            all_words.extend([w for w in words if len(w) >= 2])

    # 统计词频
    word_freq = Counter(all_words)

    if not word_freq:
        print("  ⚠ 没有足够的负面关键词生成词云")
        return

    # 生成词云（必须指定中文字体路径）
    wc = WordCloud(
        font_path=FONT_PATH,
        width=1200,
        height=600,
        background_color='white',
        colormap='Reds',
        max_words=100,
        max_font_size=150,
        min_font_size=10,
        relative_scaling=0.5,
        collocations=False,
    ).generate_from_frequencies(word_freq)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title("用户负面评论关键词词云", fontsize=20, fontweight='bold', pad=20)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "wordcloud_negative.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ 保存至 {path}")


# ============================================================
# 图表5: 痛点柱状图
# ============================================================
def plot_pain_points(df: pd.DataFrame) -> None:
    """Top 10 痛点柱状图"""
    print("\n[5/5] 生成痛点柱状图...")

    negative_keywords = df[df["sentiment_label"] == "negative"]["keywords"].dropna()

    keyword_counter = Counter()
    for kw_json in negative_keywords:
        try:
            keywords = json.loads(kw_json) if isinstance(kw_json, str) else kw_json
            for kw in keywords:
                keyword_counter[kw] += 1
        except (json.JSONDecodeError, TypeError):
            continue

    if not keyword_counter:
        print("  ⚠ 没有足够的痛点数据")
        return

    top_10 = keyword_counter.most_common(10)
    labels = [item[0] for item in top_10]
    values = [item[1] for item in top_10]

    fig, ax = plt.subplots(figsize=(12, 7))
    colors_grad = plt.cm.Reds(np.linspace(0.4, 0.9, len(values)))

    bars = ax.barh(range(len(labels)), values, color=colors_grad, edgecolor='white',
                   linewidth=0.8, height=0.6)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=12)
    ax.invert_yaxis()
    ax.set_xlabel("提及次数", fontsize=12)
    ax.set_title("用户核心痛点 Top 10", fontsize=16, fontweight='bold')

    # 数值标签
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', fontsize=11, fontweight='bold')

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "pain_points.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ 保存至 {path}")


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("用户评论情感分析系统 — 数据可视化")
    print("=" * 60)

    # 连接数据库
    print("\n正在连接数据库...")
    try:
        conn = get_connection()
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        print("\n请先完成以下步骤：")
        print("  1. 执行 sql/init.sql 初始化数据库")
        print("  2. 运行 crawler/review_generator.py 生成数据")
        print("  3. 运行 crawler/db_loader.py 导入数据")
        print("  4. 启动 Spring Boot 后端并触发分析")
        return

    try:
        # 加载数据
        print("\n正在加载数据...")
        df = load_data(conn)

        if len(df) == 0:
            print("⚠ 数据库中没有评论数据，请先生成并导入数据。")
            return

        # 检查分析是否完成
        analyzed = df["sentiment_label"].notna().sum()
        print(f"  其中已分析: {analyzed} 条")
        if analyzed == 0:
            print("⚠ 尚未执行情感分析，请先通过 POST /api/analysis/start 启动分析。")
            print("  图表将不包含情感分析相关数据，但仍可生成基本统计。")

        # 生成图表
        print("\n" + "-" * 40)
        print("开始生成图表")
        print("-" * 40)

        plot_sentiment_distribution(df)
        plot_sentiment_trend(df)
        plot_product_comparison(df)
        plot_wordcloud(df)
        plot_pain_points(df)

        print("\n" + "=" * 60)
        print("✓ 所有图表生成完成！")
        print(f"  输出目录: {os.path.abspath(OUTPUT_DIR)}")
        print("=" * 60)

    finally:
        conn.close()
        print("\n✓ 数据库连接已关闭")


if __name__ == "__main__":
    main()
