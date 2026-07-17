package com.sentiment.service;

import com.sentiment.dto.AnalysisResponse;
import com.sentiment.dto.TaskStatus;
import com.sentiment.repository.CommentRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 异步分析调度服务
 * 使用线程池并发调用大模型API，提供任务进度追踪
 */
@Service
public class AsyncAnalysisService {

    private static final Logger log = LoggerFactory.getLogger(AsyncAnalysisService.class);

    private final CommentRepository commentRepository;
    private final SentimentService sentimentService;

    /**
     * 任务进度追踪 Map: taskId → Progress
     */
    private final Map<String, AnalysisProgress> progressMap = new ConcurrentHashMap<>();

    public AsyncAnalysisService(CommentRepository commentRepository,
                                SentimentService sentimentService) {
        this.commentRepository = commentRepository;
        this.sentimentService = sentimentService;
    }

    /**
     * 启动批量分析任务
     *
     * @param productName 可选商品名筛选，null 表示全部
     * @return 任务响应（含taskId）
     */
    public AnalysisResponse startAnalysis(String productName) {
        // 获取待分析的评论ID列表
        List<Long> commentIds;
        if (productName != null && !productName.isBlank()) {
            commentIds = commentRepository.findUnanalyzedIdsByProduct(productName);
        } else {
            commentIds = commentRepository.findUnanalyzedIds();
        }

        if (commentIds.isEmpty()) {
            return new AnalysisResponse(null, "没有待分析的评论", 0);
        }

        String taskId = UUID.randomUUID().toString().substring(0, 8);

        // 初始化进度追踪
        AnalysisProgress progress = new AnalysisProgress(commentIds.size());
        progressMap.put(taskId, progress);

        log.info("启动分析任务 {}: 共 {} 条评论待分析", taskId, commentIds.size());

        // 异步提交所有评论分析任务
        for (Long commentId : commentIds) {
            analyzeAsync(commentId, taskId, progress);
        }

        return new AnalysisResponse(taskId,
                "分析任务已启动，共 " + commentIds.size() + " 条评论",
                commentIds.size());
    }

    /**
     * 异步分析单条评论
     */
    @Async("sentimentExecutor")
    public CompletableFuture<Void> analyzeAsync(Long commentId, String taskId,
                                                 AnalysisProgress progress) {
        try {
            sentimentService.analyzeOne(commentId);
            progress.completed.incrementAndGet();
        } catch (Exception e) {
            log.error("评论 {} 分析异常: {}", commentId, e.getMessage());
            progress.failed.incrementAndGet();
        }
        return CompletableFuture.completedFuture(null);
    }

    /**
     * 查询任务进度
     */
    public TaskStatus getProgress(String taskId) {
        AnalysisProgress progress = progressMap.get(taskId);
        if (progress == null) {
            return null;
        }

        long completed = progress.completed.get();
        long failed = progress.failed.get();
        long processed = completed + failed;
        String status = processed >= progress.total ? "COMPLETED" : "RUNNING";

        return new TaskStatus(taskId, status, progress.total, completed, failed);
    }

    /**
     * 进度追踪内部类
     */
    private static class AnalysisProgress {
        final long total;
        final AtomicInteger completed = new AtomicInteger(0);
        final AtomicInteger failed = new AtomicInteger(0);
        final long startedAt = System.currentTimeMillis();

        AnalysisProgress(long total) {
            this.total = total;
        }
    }
}
