package com.sentiment.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 情感分析结果实体
 */
@Entity
@Table(name = "sentiment_results")
public class SentimentResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "comment_id", nullable = false)
    private Long commentId;

    @Column(name = "sentiment_label", nullable = false, length = 20)
    private String sentimentLabel;

    @Column(nullable = false)
    private Double confidence;

    @Column(columnDefinition = "TEXT")
    private String keywords;

    @Column(name = "aspect_keywords", columnDefinition = "TEXT")
    private String aspectKeywords;

    @Column(name = "raw_response", columnDefinition = "TEXT")
    private String rawResponse;

    @Column(name = "analysis_time")
    private LocalDateTime analysisTime;

    @Column(name = "model_version", length = 50)
    private String modelVersion;

    @PrePersist
    protected void onCreate() {
        if (analysisTime == null) {
            analysisTime = LocalDateTime.now();
        }
        if (modelVersion == null) {
            modelVersion = "deepseek-chat";
        }
    }

    // ===== Getters & Setters =====

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getCommentId() {
        return commentId;
    }

    public void setCommentId(Long commentId) {
        this.commentId = commentId;
    }

    public String getSentimentLabel() {
        return sentimentLabel;
    }

    public void setSentimentLabel(String sentimentLabel) {
        this.sentimentLabel = sentimentLabel;
    }

    public Double getConfidence() {
        return confidence;
    }

    public void setConfidence(Double confidence) {
        this.confidence = confidence;
    }

    public String getKeywords() {
        return keywords;
    }

    public void setKeywords(String keywords) {
        this.keywords = keywords;
    }

    public String getAspectKeywords() {
        return aspectKeywords;
    }

    public void setAspectKeywords(String aspectKeywords) {
        this.aspectKeywords = aspectKeywords;
    }

    public String getRawResponse() {
        return rawResponse;
    }

    public void setRawResponse(String rawResponse) {
        this.rawResponse = rawResponse;
    }

    public LocalDateTime getAnalysisTime() {
        return analysisTime;
    }

    public void setAnalysisTime(LocalDateTime analysisTime) {
        this.analysisTime = analysisTime;
    }

    public String getModelVersion() {
        return modelVersion;
    }

    public void setModelVersion(String modelVersion) {
        this.modelVersion = modelVersion;
    }
}
