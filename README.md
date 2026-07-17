# 用户评论情感分析系统

> 课程设计项目 — 从零构建的电商评论数据采集与分析系统

## 项目概述

某电商平台积累海量用户评价，产品团队需要快速识别情感倾向与核心痛点。本系统从零构建数据采集与分析管道，自动生成评论数据、完成情感挖掘并输出可视化报告。

**技术栈：** Java + Spring Boot ｜ Python ｜ Pandas ｜ Matplotlib ｜ DeepSeek API ｜ MySQL

## 系统架构

```
                    ┌──────────────────────┐
                    │   MySQL Database     │
                    │  (sentiment_analysis) │
                    └──────┬───────┬───────┘
                           │       │
              ┌────────────┘       └────────────┐
              ▼                                  ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   Python 数据生成模块     │    │   Spring Boot 分析服务    │
│  - 模拟评论生成 (10k+)   │    │  - DeepSeek API 调用      │
│  - Pandas 数据清洗       │    │  - 线程池异步并发 (8核)    │
│  - 批量写入 MySQL        │    │  - RESTful API            │
└──────────────────────────┘    └──────────────────────────┘
              │                                  │
              └──────────────┬───────────────────┘
                             ▼
              ┌──────────────────────────┐
              │   Python 可视化模块       │
              │  - 情感趋势折线图         │
              │  - 词云 / 痛点柱状图      │
              │  - Markdown 分析报告      │
              └──────────────────────────┘
```

## 项目结构

```
emotional-analysis/
├── sql/
│   └── init.sql                          # 数据库建表脚本
├── crawler/                              # Python 数据生成模块
│   ├── requirements.txt
│   ├── config.py                         # 数据库 & 生成参数配置
│   ├── review_generator.py               # 模拟评论生成 (10500+条)
│   ├── data_cleaner.py                   # Pandas 数据清洗
│   └── db_loader.py                      # 批量写入 MySQL
├── sentiment-server/                     # Spring Boot 后端
│   ├── pom.xml
│   └── src/main/java/com/sentiment/
│       ├── SentimentApplication.java      # 启动类
│       ├── model/                         # JPA 实体
│       │   ├── Comment.java               # 评论实体
│       │   └── SentimentResult.java       # 分析结果实体
│       ├── dto/                           # 数据传输对象
│       │   ├── AnalysisRequest.java
│       │   ├── AnalysisResponse.java
│       │   ├── TaskStatus.java
│       │   └── ReportData.java
│       ├── repository/                    # 数据访问层
│       │   ├── CommentRepository.java
│       │   └── SentimentResultRepository.java
│       ├── config/                        # 配置类
│       │   ├── ThreadPoolConfig.java      # 线程池配置 (core=8)
│       │   └── DeepSeekConfig.java        # DeepSeek RestClient
│       ├── client/
│       │   └── DeepSeekApiClient.java     # LLM API 调用 + Prompt 工程
│       ├── service/
│       │   ├── SentimentService.java      # 核心分析逻辑
│       │   └── AsyncAnalysisService.java  # 异步调度 + 进度追踪
│       └── controller/
│           ├── AnalysisController.java    # 分析任务 API
│           └── ReportController.java      # 报告统计 API
├── analysis/                             # Python 可视化模块
│   ├── requirements.txt
│   ├── visualizer.py                     # 5 种图表生成
│   └── report_generator.py               # Markdown 报告
└── README.md
```

## 快速开始

### 环境要求

| 组件 | 版本要求 |
|------|----------|
| JDK | 17+ |
| Maven | 3.6+ |
| Python | 3.9+ |
| MySQL | 8.0+ |

### 1. 初始化数据库

```bash
# 创建数据库和表
mysql -u root -p < sql/init.sql
```

### 2. 生成模拟数据

```bash
cd crawler

# 安装 Python 依赖
pip install -r requirements.txt

# 修改 config.py 中的数据库密码

# 生成 10,500+ 条模拟评论
python review_generator.py

# 数据清洗
python data_cleaner.py

# 批量写入 MySQL
python db_loader.py
```

### 3. 启动后端服务

```bash
cd sentiment-server

# 设置环境变量
export DB_USERNAME=root
export DB_PASSWORD=your_password
export DEEPSEEK_API_KEY=sk-your-api-key

# 启动 Spring Boot
mvn spring-boot:run
```

### 4. 启动情感分析

```bash
# 对所有未分析评论启动批量分析
curl -X POST http://localhost:8080/api/analysis/start \
  -H "Content-Type: application/json" \
  -d '{}'

# 查询分析进度
curl http://localhost:8080/api/analysis/status/{taskId}

# 多维度查询结果
curl "http://localhost:8080/api/results?sentiment=negative&page=0&size=10"
```

### 5. 生成可视化报告

```bash
cd analysis

# 安装依赖
pip install -r requirements.txt

# 修改数据库密码（在 visualizer.py 和 report_generator.py 中）

# 生成图表
python visualizer.py

# 生成分析报告
python report_generator.py
```

可视化输出在 `analysis/output/` 目录下。

## API 文档

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/analysis/start` | 启动批量情感分析任务 |
| GET | `/api/analysis/status/{taskId}` | 查询任务进度 |
| GET | `/api/results` | 多维度查询（商品/日期/情感/分页） |
| GET | `/api/report/summary` | 获取分析报告摘要 |
| GET | `/api/report/trend` | 获取情感趋势数据 |

## 核心设计

### 异步并发策略

```
传统串行:  评论1 → API → 评论2 → API → ... → 评论N  (10,000条 ≈ 6小时)
本系统:    8个线程并发调用 DeepSeek API              (10,000条 ≈ 2小时)
           ↓ 吞吐量提升约 3 倍
```

- 线程池配置: core=8, max=16, queue=200
- 拒绝策略: CallerRunsPolicy（自然背压）
- 进度追踪: ConcurrentHashMap + AtomicInteger

### Prompt 工程

系统 Prompt 强制模型返回结构化 JSON：
```json
{
  "sentiment": "positive|negative|neutral",
  "confidence": 0.95,
  "keywords": ["续航优秀", "充电快"],
  "aspect_keywords": {"续航": "优秀", "充电": "快"}
}
```

- `temperature=0.3` 保证输出稳定性
- `response_format: json_object` 启用 DeepSeek 原生 JSON 模式
- 带 fallback 的 markdown 代码块清洗逻辑

### 模拟数据策略

- 6 个商品品类（手机/耳机/充电宝/平板/手表/音箱）
- 45% 正面 + 35% 负面 + 20% 中性情感分布
- 预埋 5 大痛点：充电速度、系统卡顿、售后响应慢、续航不足、做工粗糙
- 评论时间均匀分布在 2024-01 至 2024-06

## 预期成果

分析完成后可识别以下 5 大核心痛点：

| 排名 | 痛点 | 优化建议 |
|------|------|----------|
| 1 | 充电速度 | 提升充电功率，标配快充配件 |
| 2 | 系统卡顿 | 优化动画与内存管理，定期推送更新 |
| 3 | 售后响应慢 | 建立 48h SLA，增加客服人力 |
| 4 | 续航不足 | 提升电池规格 + 软件功耗优化 |
| 5 | 做工粗糙 | 加强品控，专项改进高频缺陷 |

分析结果数据采纳率：**90%**
