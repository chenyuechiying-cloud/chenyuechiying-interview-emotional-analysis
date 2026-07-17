"""
用户评论情感分析系统 — 模拟评论数据生成器
生成 10,000+ 条仿真电商评论，覆盖正/负/中性情感，
重点模拟 5 大痛点：充电速度、系统卡顿、售后响应慢、续航不足、做工粗糙
"""

import random
import datetime
import json
from typing import Any

from config import PRODUCTS, GENERATION_CONFIG

# ============================================================
# 评论模板库
# ============================================================

# --- 通用正面评论模板 ---
POSITIVE_TEMPLATES = [
    "用了{time}了，感觉很不错！{aspect}表现优秀，性价比很高。",
    "{aspect}真的很棒，完全超出预期，推荐购买！",
    "第二次购买了，{aspect}一如既往地好，品质稳定。",
    "物流很快，包装完好。{aspect}非常满意，{detail}。",
    "对比了好几家最终选了这款，{aspect}没让我失望，好评！",
    "体验了{time}，{aspect}确实不错，{detail}，值得入手。",
    "颜值很高，{aspect}也很出色，朋友看了也想买。",
    "给家人买的，反馈很好，{aspect}特别实用，{detail}。",
    "性价比炸裂！{aspect}吊打同价位产品，强烈推荐。",
    "手感/质感一级棒，{aspect}体验流畅，五星好评。",
    "买之前担心{aspect}不行，实际用下来完全多虑了，真香！",
    "{aspect}做得越来越好了，支持国货，会继续回购。",
    "用了一个月了，{aspect}依旧很稳，{detail}，非常满意。",
    "做活动买的，价格实惠，{aspect}也没缩水，良心产品。",
]

# --- 通用负面评论模板 ---
NEGATIVE_TEMPLATES = [
    "用了{time}就出问题了，{pain_point}，太让人失望了。",
    "{pain_point}，体验很差，不建议购买。",
    "冲着品牌买的，结果{time}不到就{problem}，质量堪忧。",
    "{pain_point}，客服还推三阻四的，售后体验极差。",
    "很一般，{pain_point}，{detail}，完全不值这个价。",
    "{time}就坏了，{pain_point}，维权太难了。",
    "买完就降价，而且{pain_point}，双重心塞。",
    "好评都是刷的吧？{pain_point}，{detail}，踩坑了。",
    "{pain_point}，联系售后说{pain_point}是正常的，无语了。",
    "做工太差了，{pain_point}，{detail}，还不如便宜一半的竞品。",
    "第一次差评送给你们，{pain_point}，大家慎买。",
    "宣传和实际差距太大，{pain_point}，{detail}，虚假宣传。",
    "好后悔没退货，{pain_point}越来越严重，{time}就彻底不行了。",
    "收到就有瑕疵，{pain_point}，品控形同虚设。",
]

# --- 中性评论模板 ---
NEUTRAL_TEMPLATES = [
    "用了一段时间，{aspect}中规中矩，没有惊喜也没有大问题。",
    "性价比一般吧，{aspect}在这个价位算正常水平。",
    "{aspect}还行，但也没有宣传的那么好，期望值别太高。",
    "够用但不出彩，{aspect}表现平平，日常使用没问题。",
    "做工还行，{aspect}也能接受，就是价格偏高了点。",
    "不好不坏，{aspect}符合预期，物流倒是挺快的。",
    "用着还行，{aspect}没太大亮点，暂时没有换的想法。",
]

# ============================================================
# 商品专属方面关键词
# ============================================================
PRODUCT_ASPECTS = {
    "PHONE_X_PRO": {
        "positive": [
            "拍照效果", "屏幕显示", "系统流畅度", "手感", "外观设计",
            "人脸识别速度", "游戏性能", "信号稳定性", "扬声器音质", "重量控制",
        ],
        "negative": [
            ("充电速度太慢", "充电速度"),
            ("系统经常卡顿", "系统卡顿"),
            ("电池不耐用", "续航不足"),
            ("售后响应太慢", "售后响应慢"),
            ("边框做工有毛刺", "做工粗糙"),
            ("发热严重", "发热问题"),
            ("WiFi断流", "信号问题"),
            ("拍照偏色", "拍照偏色"),
            ("屏幕有坏点", "屏幕缺陷"),
            ("充电接口松动", "做工粗糙"),
        ],
        "neutral": [
            "续航表现", "日常流畅度", "拍照素质", "屏幕观感", "充电速度",
        ],
    },
    "BUDS_AIR_3": {
        "positive": [
            "音质", "降噪效果", "佩戴舒适度", "续航", "连接稳定性",
            "低音表现", "通话清晰度", "颜值", "充电盒质感", "延迟控制",
        ],
        "negative": [
            ("续航缩水严重", "续航不足"),
            ("连接经常断开", "连接不稳定"),
            ("戴久了耳朵疼", "佩戴不适"),
            ("充电仓接触不良", "做工粗糙"),
            ("售后换新流程太慢", "售后响应慢"),
            ("降噪效果几乎没有", "降噪差"),
            ("音质不如预期", "音质差"),
            ("耳机有底噪", "底噪问题"),
            ("触摸控制不灵敏", "触控失灵"),
            ("左右耳电量不一致", "品控问题"),
        ],
        "neutral": [
            "音质表现", "佩戴感", "续航能力", "连接距离", "降噪水平",
        ],
    },
    "POWERBANK_20W": {
        "positive": [
            "充电速度", "容量", "便携性", "发热控制", "兼容性",
            "外观质感", "LED显示", "多口输出", "充满时间", "性价比",
        ],
        "negative": [
            ("充电速度远不如宣传", "充电速度"),
            ("用了几次就充不进电了", "产品质量"),
            ("体积太大不方便携带", "便携性差"),
            ("售后根本联系不上", "售后响应慢"),
            ("外壳做工有缝隙", "做工粗糙"),
            ("容量虚标", "容量虚标"),
            ("充电时发热烫手", "发热严重"),
            ("Type-C口松动", "做工粗糙"),
            ("给iPhone充电很慢", "充电速度"),
            ("用了两个月就鼓包了", "安全隐患"),
        ],
        "neutral": [
            "充电效率", "容量大小", "便携程度", "发热情况", "做工水平",
        ],
    },
    "PAD_MINI_8": {
        "positive": [
            "屏幕素质", "续航能力", "系统流畅", "轻薄程度", "手写笔体验",
            "分屏功能", "阅读体验", "外放音质", "多任务处理", "性价比",
        ],
        "negative": [
            ("系统卡顿严重", "系统卡顿"),
            ("充电速度太慢了", "充电速度"),
            ("电池掉电快", "续航不足"),
            ("屏幕有漏光", "做工粗糙"),
            ("售后维修周期长", "售后响应慢"),
            ("应用兼容性差", "兼容性问题"),
            ("WiFi信号弱", "信号问题"),
            ("外放破音", "音质问题"),
            ("触控偶尔失灵", "触控问题"),
            ("充电口容易坏", "做工粗糙"),
        ],
        "neutral": [
            "日常使用", "屏幕效果", "续航表现", "便携性", "性能水平",
        ],
    },
    "WATCH_GT_4": {
        "positive": [
            "续航", "屏幕清晰度", "运动模式", "健康监测", "外观设计",
            "GPS精度", "心率监测", "通知提醒", "表盘丰富度", "防水性能",
        ],
        "negative": [
            ("续航远不如宣传", "续航不足"),
            ("系统操作卡顿", "系统卡顿"),
            ("充电速度慢", "充电速度"),
            ("表带做工粗糙", "做工粗糙"),
            ("售后客服态度差", "售后响应慢"),
            ("GPS定位不准", "定位不准"),
            ("心率监测误差大", "数据不准"),
            ("蓝牙断连频繁", "连接问题"),
            ("屏幕容易刮花", "耐用性差"),
            ("应用生态太少", "生态不足"),
        ],
        "neutral": [
            "日常续航", "运动追踪", "佩戴舒适度", "屏幕观感", "系统流畅度",
        ],
    },
    "SPEAKER_PRO": {
        "positive": [
            "音质", "低音效果", "续航", "防水性能", "便携性",
            "蓝牙距离", "外观设计", "音量", "TWS配对", "性价比",
        ],
        "negative": [
            ("电池续航缩水", "续航不足"),
            ("蓝牙连接不稳定", "连接问题"),
            ("充电接口接触不良", "做工粗糙"),
            ("售后维修无门", "售后响应慢"),
            ("音量大了破音", "音质问题"),
            ("防水是假的", "虚假宣传"),
            ("充电速度太慢", "充电速度"),
            ("外壳接缝大", "做工粗糙"),
            ("用了不久就充不进电", "产品质量"),
            ("底噪太大", "底噪问题"),
        ],
        "neutral": [
            "音质表现", "续航能力", "便携程度", "蓝牙稳定性", "音量大小",
        ],
    },
}

# ============================================================
# 辅助文本片段
# ============================================================
TIME_PHRASES = [
    "两天", "三天", "一周", "一个星期", "十来天", "半个月",
    "一个月", "两个月", "三个月", "半年", "一个多月",
]

DETAIL_PHRASES_POSITIVE = [
    "比我之前用的好太多",
    "相同价位里应该是最好的了",
    "功能齐全，操作也简单",
    "做工精细，细节到位",
    "客服态度也很好",
    "还送了赠品，很惊喜",
    "包装很用心",
    "续航完全够用",
    "日常使用绰绰有余",
    "各种场景都能应对",
]

DETAIL_PHRASES_NEGATIVE = [
    "现在只能凑合用",
    "下次不会再买了",
    "申请退货中",
    "已经影响到正常使用了",
    "找了客服也没解决",
    "准备投诉了",
    "建议大家避开",
    "跟宣传的完全是两码事",
    "现在每天都很糟心",
    "再观望观望吧",
]

# ============================================================
# 数据生成函数
# ============================================================

def _random_date(start: datetime.date, end: datetime.date) -> datetime.datetime:
    """生成随机日期时间"""
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_hour = random.randint(8, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    return datetime.datetime.combine(
        start + datetime.timedelta(days=random_days),
        datetime.time(random_hour, random_minute, random_second),
    )


def _generate_nickname() -> str:
    """生成随机昵称"""
    prefixes = ["小", "大", "老", "阿", "", "", ""]
    names = ["明", "红", "刚", "芳", "强", "丽", "勇", "敏", "静", "涛",
             "龙", "凤", "鑫", "磊", "洋", "宇", "浩", "然", "远", "晨",
             "阳光", "清风", "星辰", "大海", "流年", "浅梦", "暖阳"]
    formats = [
        "{prefix}{name}",
        "{name}{name}",
        "{name}***",
        "{prefix}{name}123",
        "用户{random_num}",
        "tb{random_num}",
        "{name}的购物之旅",
        "{name}爱购物",
        "{prefix}{name}子",
        "匿名{name}",
    ]
    fmt = random.choice(formats)
    return fmt.format(
        prefix=random.choice(prefixes),
        name=random.choice(names),
        random_num=random.randint(10000, 99999),
    )


def _fill_template(template: str, aspects: list[str], pain_points: list[tuple[str, str]],
                   sentiment: str) -> str:
    """填充评论模板"""
    text = template

    if "{time}" in text:
        text = text.replace("{time}", random.choice(TIME_PHRASES))

    if "{aspect}" in text:
        if sentiment == "negative":
            pair = random.choice(pain_points)
            text = text.replace("{aspect}", pair[0])
            text = text.replace("{pain_point}", pair[0])
        else:
            text = text.replace("{aspect}", random.choice(aspects))

    if "{pain_point}" in text:
        pair = random.choice(pain_points)
        text = text.replace("{pain_point}", pair[0])

    if "{detail}" in text:
        if sentiment == "positive":
            text = text.replace("{detail}", random.choice(DETAIL_PHRASES_POSITIVE))
        else:
            text = text.replace("{detail}", random.choice(DETAIL_PHRASES_NEGATIVE))

    if "{problem}" in text:
        problems = ["出了故障", "开始出问题", "就坏了", "出现各种小毛病"]
        text = text.replace("{problem}", random.choice(problems))

    return text


def generate_review(product: dict[str, str], sentiment: str) -> dict[str, Any]:
    """
    生成一条评论

    Args:
        product: 商品信息字典
        sentiment: 'positive' | 'negative' | 'neutral'

    Returns:
        评论字典
    """
    product_id = product["id"]
    aspects_data = PRODUCT_ASPECTS[product_id]

    if sentiment == "positive":
        template = random.choice(POSITIVE_TEMPLATES)
        aspects = aspects_data["positive"]
        pain_points = []
    elif sentiment == "negative":
        template = random.choice(NEGATIVE_TEMPLATES)
        aspects = []
        pain_points = aspects_data["negative"]
    else:
        template = random.choice(NEUTRAL_TEMPLATES)
        aspects = aspects_data["neutral"]
        pain_points = []

    review_text = _fill_template(template, aspects, pain_points, sentiment)

    # 评分映射
    if sentiment == "positive":
        rating = random.randint(4, 5)
    elif sentiment == "negative":
        rating = random.randint(1, 2)
    else:
        rating = 3

    return {
        "product_name": product["name"],
        "product_id": product_id,
        "review_text": review_text,
        "rating": rating,
        "review_time": _random_date(
            datetime.date.fromisoformat(GENERATION_CONFIG["start_date"]),
            datetime.date.fromisoformat(GENERATION_CONFIG["end_date"]),
        ),
        "reviewer_name": _generate_nickname(),
        "source": random.choice(["京东", "淘宝", "拼多多", "天猫"]),
    }


def generate_all_reviews() -> list[dict[str, Any]]:
    """
    生成全部模拟评论数据

    Returns:
        评论列表
    """
    total = GENERATION_CONFIG["total_reviews"]
    products = PRODUCTS

    # 情感分布: 45% 正面, 35% 负面, 20% 中性
    # 负面略多以便充分挖掘痛点
    sentiment_weights = ["positive"] * 45 + ["negative"] * 35 + ["neutral"] * 20

    reviews = []
    for i in range(total):
        product = random.choice(products)
        sentiment = random.choice(sentiment_weights)
        review = generate_review(product, sentiment)
        reviews.append(review)

        if (i + 1) % 1000 == 0:
            print(f"  已生成 {i + 1}/{total} 条评论...")

    # 按评论时间排序
    reviews.sort(key=lambda r: r["review_time"])
    print(f"✓ 评论数据生成完成，共 {len(reviews)} 条")
    return reviews


def print_statistics(reviews: list[dict[str, Any]]) -> None:
    """打印数据统计信息"""
    print("\n" + "=" * 50)
    print("数据统计")
    print("=" * 50)

    # 情感分布
    pos = sum(1 for r in reviews if r["rating"] >= 4)
    neg = sum(1 for r in reviews if r["rating"] <= 2)
    neu = sum(1 for r in reviews if r["rating"] == 3)
    print(f"  正面评论 (4-5星): {pos} ({pos/len(reviews)*100:.1f}%)")
    print(f"  中性评论 (3星):   {neu} ({neu/len(reviews)*100:.1f}%)")
    print(f"  负面评论 (1-2星): {neg} ({neg/len(reviews)*100:.1f}%)")

    # 商品分布
    from collections import Counter
    product_dist = Counter(r["product_name"] for r in reviews)
    print(f"\n  商品分布:")
    for name, count in product_dist.most_common():
        print(f"    {name}: {count}")

    # 时间范围
    dates = [r["review_time"] for r in reviews]
    print(f"\n  时间范围: {min(dates)} ~ {max(dates)}")

    # 来源分布
    source_dist = Counter(r["source"] for r in reviews)
    print(f"\n  来源分布:")
    for s, c in source_dist.most_common():
        print(f"    {s}: {c}")

    print("=" * 50)


if __name__ == "__main__":
    random.seed(42)  # 固定种子确保可复现
    reviews = generate_all_reviews()
    print_statistics(reviews)

    # 保存为 JSON 文件备用
    output_path = "generated_reviews.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✓ 数据已保存至 {output_path}")
