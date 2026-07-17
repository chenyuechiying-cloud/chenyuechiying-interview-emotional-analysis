package com.sentiment.repository;

import com.sentiment.model.Comment;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 评论数据访问层
 */
@Repository
public interface CommentRepository extends JpaRepository<Comment, Long> {

    /**
     * 查询未分析的评论ID列表（不在 sentiment_results 表中的）
     */
    @Query("SELECT c.id FROM Comment c WHERE c.id NOT IN " +
           "(SELECT sr.commentId FROM SentimentResult sr)")
    List<Long> findUnanalyzedIds();

    /**
     * 按商品名查询未分析的评论ID
     */
    @Query("SELECT c.id FROM Comment c WHERE c.productName = :productName " +
           "AND c.id NOT IN (SELECT sr.commentId FROM SentimentResult sr)")
    List<Long> findUnanalyzedIdsByProduct(@Param("productName") String productName);

    /**
     * 多维度查询（分页）
     */
    @Query("SELECT c FROM Comment c " +
           "LEFT JOIN SentimentResult sr ON c.id = sr.commentId " +
           "WHERE (:productName IS NULL OR c.productName = :productName) " +
           "AND (:startDate IS NULL OR c.reviewTime >= :startDate) " +
           "AND (:endDate IS NULL OR c.reviewTime <= :endDate) " +
           "AND (:sentiment IS NULL OR sr.sentimentLabel = :sentiment)")
    Page<Comment> queryWithFilters(@Param("productName") String productName,
                                    @Param("startDate") LocalDateTime startDate,
                                    @Param("endDate") LocalDateTime endDate,
                                    @Param("sentiment") String sentiment,
                                    Pageable pageable);

    /**
     * 按时间范围统计
     */
    long countByReviewTimeBetween(LocalDateTime start, LocalDateTime end);

    /**
     * 按商品统计
     */
    long countByProductName(String productName);
}
