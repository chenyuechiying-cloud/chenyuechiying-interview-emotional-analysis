package com.sentiment.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sentiment.client.DeepSeekApiClient;
import com.sentiment.model.Comment;
import com.sentiment.model.SentimentResult;
import com.sentiment.repository.CommentRepository;
import com.sentiment.repository.SentimentResultRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

/**
 * 核心情感分析服务
 * 负责调用 DeepSeek API 并对单条评论完成分析+持久化
 */
@Service
public class SentimentService {

    private static final Logger log = LoggerFactory.getLogger(SentimentService.class);

    private final CommentRepository commentRepository;
    private final SentimentResultRepository resultRepository;
    private final DeepSeekApiClient deepSeekClient;
    private final ObjectMapper objectMapper;

    public SentimentService(CommentRepository commentRepository,
                            SentimentResultRepository resultRepository,
                            DeepSeekApiClient deepSeekClient,
                            ObjectMapper objectMapper) {
        this.commentRepository = commentRepository;
        this.resultRepository = resultRepository;
        this.deepSeekClient = deepSeekClient;
        this.objectMapper = objectMapper;
    }

    /**
     * 分析单条评论
     *
     * @param commentId 评论ID
     * @return 分析结果，失败返回 null
     */
    @Transactional
    public SentimentResult analyzeOne(Long commentId) {
        // 检查是否已分析
        SentimentResult existing = resultRepository.findByCommentId(commentId);
        if (existing != null) {
            log.debug("评论 {} 已分析过，跳过", commentId);
            return existing;
        }

        // 获取评论
        Comment comment = commentRepository.findById(commentId).orElse(null);
        if (comment == null) {
            log.warn("评论 {} 不存在", commentId);
            return null;
        }

        try {
            // 调用 DeepSeek API
            DeepSeekApiClient.SentimentPayload payload =
                    deepSeekClient.analyzeSentiment(comment.getReviewText());

            // 构造结果实体
            SentimentResult result = new SentimentResult();
            result.setCommentId(commentId);
            result.setSentimentLabel(payload.sentiment());
            result.setConfidence(payload.confidence());
            result.setKeywords(toJson(payload.keywords()));
            result.setAspectKeywords(toJson(payload.aspect_keywords()));
            result.setRawResponse(null); // 仅保存解析后的关键字段
            result.setAnalysisTime(LocalDateTime.now());
            result.setModelVersion("deepseek-chat");

            return resultRepository.save(result);

        } catch (DeepSeekApiClient.DeepSeekException e) {
            log.error("评论 {} 分析失败: {}", commentId, e.getMessage());
            // 记录失败结果（低置信度）
            SentimentResult failed = new SentimentResult();
            failed.setCommentId(commentId);
            failed.setSentimentLabel("neutral");
            failed.setConfidence(0.0);
            failed.setKeywords("[]");
            failed.setAspectKeywords("{}");
            failed.setRawResponse("ERROR: " + e.getMessage());
            failed.setAnalysisTime(LocalDateTime.now());
            failed.setModelVersion("deepseek-chat-fallback");
            return resultRepository.save(failed);
        }
    }

    /**
     * 多维度条件查询
     */
    public Page<Comment> queryResults(String productName, LocalDateTime startDate,
                                       LocalDateTime endDate, String sentiment,
                                       Pageable pageable) {
        return commentRepository.queryWithFilters(
                productName, startDate, endDate, sentiment, pageable);
    }

    /**
     * 获取某条评论的分析结果
     */
    public SentimentResult getResult(Long commentId) {
        return resultRepository.findByCommentId(commentId);
    }

    /**
     * 对象转 JSON 字符串
     */
    private String toJson(Object obj) {
        try {
            return objectMapper.writeValueAsString(obj);
        } catch (JsonProcessingException e) {
            log.warn("JSON 序列化失败: {}", e.getMessage());
            return "[]";
        }
    }
}
