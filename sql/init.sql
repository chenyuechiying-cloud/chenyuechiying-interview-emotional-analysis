-- ============================================================
-- 用户评论情感分析系统 — 数据库初始化脚本
-- 使用方式: mysql -u root -p < sql/init.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS sentiment_analysis
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE sentiment_analysis;

-- ============================================================
-- 原始评论表
-- ============================================================
CREATE TABLE IF NOT EXISTS comments (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_name    VARCHAR(255)    NOT NULL COMMENT '商品名称',
    product_id      VARCHAR(100)    NOT NULL COMMENT '商品ID',
    review_text     TEXT            NOT NULL COMMENT '评论正文',
    rating          TINYINT         NOT NULL COMMENT '评分 1-5',
    review_time     DATETIME        NOT NULL COMMENT '评论时间',
    reviewer_name   VARCHAR(100)    DEFAULT '匿名用户' COMMENT '评论者昵称',
    source          VARCHAR(50)     DEFAULT '模拟数据' COMMENT '来源平台',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',

    INDEX idx_product_id (product_id),
    INDEX idx_product_name (product_name),
    INDEX idx_review_time (review_time),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='原始评论数据';


-- ============================================================
-- 情感分析结果表
-- ============================================================
CREATE TABLE IF NOT EXISTS sentiment_results (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    comment_id      BIGINT          NOT NULL COMMENT '关联评论ID',
    sentiment_label VARCHAR(20)     NOT NULL COMMENT 'positive / negative / neutral',
    confidence      DOUBLE          NOT NULL COMMENT '置信度 0.0-1.0',
    keywords        TEXT            COMMENT 'JSON数组: 情感关键词',
    aspect_keywords TEXT            COMMENT 'JSON对象: 方面级关键词 {"充电":"慢","系统":"卡顿"}',
    raw_response    TEXT            COMMENT 'DeepSeek API原始返回',
    analysis_time   DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '分析时间',
    model_version   VARCHAR(50)     DEFAULT 'deepseek-chat' COMMENT '模型标识',

    INDEX idx_comment_id (comment_id),
    INDEX idx_sentiment_label (sentiment_label),
    INDEX idx_analysis_time (analysis_time),
    INDEX idx_confidence (confidence),

    CONSTRAINT fk_comment
        FOREIGN KEY (comment_id) REFERENCES comments(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情感分析结果';


-- ============================================================
-- 分析任务记录表 (可选，用于追踪批量任务)
-- ============================================================
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id         VARCHAR(64)     NOT NULL UNIQUE COMMENT '任务UUID',
    total_count     INT             NOT NULL DEFAULT 0 COMMENT '总评论数',
    completed_count INT             NOT NULL DEFAULT 0 COMMENT '已完成数',
    failed_count    INT             NOT NULL DEFAULT 0 COMMENT '失败数',
    status          VARCHAR(20)     NOT NULL DEFAULT 'RUNNING' COMMENT 'RUNNING / COMPLETED / FAILED',
    started_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    completed_at    DATETIME        DEFAULT NULL,

    INDEX idx_task_id (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='分析任务记录';
