package com.sentiment.repository;

import com.sentiment.model.SentimentResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 情感分析结果数据访问层
 */
@Repository
public interface SentimentResultRepository extends JpaRepository<SentimentResult, Long> {

    /**
     * 按评论ID查找分析结果
     */
    SentimentResult findByCommentId(Long commentId);

    /**
     * 按情感标签统计
     */
    long countBySentimentLabel(String sentimentLabel);

    /**
     * 按情感标签和时间范围统计
     */
    @Query("SELECT COUNT(sr) FROM SentimentResult sr " +
           "JOIN Comment c ON sr.commentId = c.id " +
           "WHERE sr.sentimentLabel = :label " +
           "AND c.reviewTime BETWEEN :start AND :end")
    long countByLabelAndTimeRange(@Param("label") String label,
                                   @Param("start") LocalDateTime start,
                                   @Param("end") LocalDateTime end);

    /**
     * 获取平均置信度
     */
    @Query("SELECT AVG(sr.confidence) FROM SentimentResult sr")
    Double getAverageConfidence();

    /**
     * 按商品查询负面关键词（用于痛点分析）
     */
    @Query("SELECT sr.keywords FROM SentimentResult sr " +
           "JOIN Comment c ON sr.commentId = c.id " +
           "WHERE sr.sentimentLabel = 'negative' " +
           "AND (:productName IS NULL OR c.productName = :productName)")
    List<String> findNegativeKeywords(@Param("productName") String productName);

    /**
     * 按时间粒度统计情感分布趋势
     * 返回日期 + positive/negative/neutral 计数
     */
    @Query(value = "SELECT DATE_FORMAT(c.review_time, :dateFormat) AS date, " +
           "sr.sentiment_label AS label, COUNT(*) AS cnt " +
           "FROM sentiment_results sr " +
           "JOIN comments c ON sr.comment_id = c.id " +
           "WHERE c.review_time BETWEEN :start AND :end " +
           "GROUP BY date, sr.sentiment_label " +
           "ORDER BY date",
           nativeQuery = true)
    List<Object[]> getTrendRaw(@Param("start") LocalDateTime start,
                               @Param("end") LocalDateTime end,
                               @Param("dateFormat") String dateFormat);
}
