"""
用户评论情感分析系统 — 配置文件
请根据实际环境修改数据库连接信息
"""

# ============================================================
# MySQL 数据库配置
# ============================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password_here",
    "database": "sentiment_analysis",
    "charset": "utf8mb4",
}

# ============================================================
# 数据生成配置
# ============================================================
GENERATION_CONFIG = {
    "total_reviews": 10500,       # 生成评论总数
    "start_date": "2024-01-01",   # 评论起始日期
    "end_date": "2024-06-30",     # 评论结束日期
    "batch_size": 500,            # 批量写入大小
}

# ============================================================
# 商品列表 (用于模拟数据生成)
# ============================================================
PRODUCTS = [
    {
        "id": "PHONE_X_PRO",
        "name": "Phone X Pro",
        "category": "智能手机",
        "price_range": "4000-5000元",
    },
    {
        "id": "BUDS_AIR_3",
        "name": "Buds Air 3",
        "category": "无线耳机",
        "price_range": "300-500元",
    },
    {
        "id": "POWERBANK_20W",
        "name": "PowerBank 20W 快充版",
        "category": "充电宝",
        "price_range": "100-200元",
    },
    {
        "id": "PAD_MINI_8",
        "name": "Pad Mini 8",
        "category": "平板电脑",
        "price_range": "2000-3000元",
    },
    {
        "id": "WATCH_GT_4",
        "name": "Watch GT 4",
        "category": "智能手表",
        "price_range": "1500-2000元",
    },
    {
        "id": "SPEAKER_PRO",
        "name": "Speaker Pro 蓝牙音箱",
        "category": "蓝牙音箱",
        "price_range": "300-500元",
    },
]
