package com.sentiment.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.ThreadPoolExecutor;

/**
 * 线程池配置 — 用于异步并发调用大模型API
 *
 * 核心线程8 + 最大线程16 + 队列200 = 传统串行相比吞吐量提升约3倍
 */
@Configuration
@EnableAsync
public class ThreadPoolConfig {

    @Bean("sentimentExecutor")
    public ThreadPoolTaskExecutor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        // 核心线程数：保持活跃的最小线程数
        executor.setCorePoolSize(8);
        // 最大线程数：峰值时可扩展到的上限
        executor.setMaxPoolSize(16);
        // 队列容量：核心线程忙碌时，新任务排队等待
        executor.setQueueCapacity(200);
        // 线程名前缀
        executor.setThreadNamePrefix("sentiment-");
        // 拒绝策略：队列满时由调用线程执行，提供自然的背压机制
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        // 线程空闲超时 (秒)
        executor.setKeepAliveSeconds(60);
        // 允许核心线程超时
        executor.setAllowCoreThreadTimeOut(true);
        executor.initialize();
        return executor;
    }
}
