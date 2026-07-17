package com.sentiment;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * 用户评论情感分析系统 — Spring Boot 启动类
 */
@SpringBootApplication
@EnableAsync
public class SentimentApplication {

    public static void main(String[] args) {
        SpringApplication.run(SentimentApplication.class, args);
    }
}
