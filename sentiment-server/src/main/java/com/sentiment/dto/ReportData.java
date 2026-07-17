package com.sentiment.dto;

import java.util.List;
import java.util.Map;

/**
 * 报告摘要数据
 */
public class ReportData {

    private long totalAnalyzed;
    private Map<String, Long> sentimentDistribution;
    private double averageConfidence;
    private List<PainPoint> topPainPoints;
    private List<TrendPoint> trendData;
    private String suggestions;

    public ReportData() {}

    // === Inner classes ===

    public static class PainPoint {
        private String keyword;
        private long mentionCount;
        private double negativeRatio;
        private List<String> sampleReviews;
        private String suggestion;

        public PainPoint() {}

        public PainPoint(String keyword, long mentionCount, double negativeRatio,
                         List<String> sampleReviews, String suggestion) {
            this.keyword = keyword;
            this.mentionCount = mentionCount;
            this.negativeRatio = negativeRatio;
            this.sampleReviews = sampleReviews;
            this.suggestion = suggestion;
        }

        public String getKeyword() { return keyword; }
        public void setKeyword(String keyword) { this.keyword = keyword; }
        public long getMentionCount() { return mentionCount; }
        public void setMentionCount(long mentionCount) { this.mentionCount = mentionCount; }
        public double getNegativeRatio() { return negativeRatio; }
        public void setNegativeRatio(double negativeRatio) { this.negativeRatio = negativeRatio; }
        public List<String> getSampleReviews() { return sampleReviews; }
        public void setSampleReviews(List<String> sampleReviews) { this.sampleReviews = sampleReviews; }
        public String getSuggestion() { return suggestion; }
        public void setSuggestion(String suggestion) { this.suggestion = suggestion; }
    }

    public static class TrendPoint {
        private String date;
        private long positive;
        private long negative;
        private long neutral;

        public TrendPoint() {}

        public TrendPoint(String date, long positive, long negative, long neutral) {
            this.date = date;
            this.positive = positive;
            this.negative = negative;
            this.neutral = neutral;
        }

        public String getDate() { return date; }
        public void setDate(String date) { this.date = date; }
        public long getPositive() { return positive; }
        public void setPositive(long positive) { this.positive = positive; }
        public long getNegative() { return negative; }
        public void setNegative(long negative) { this.negative = negative; }
        public long getNeutral() { return neutral; }
        public void setNeutral(long neutral) { this.neutral = neutral; }
    }

    // === Getters & Setters ===

    public long getTotalAnalyzed() { return totalAnalyzed; }
    public void setTotalAnalyzed(long totalAnalyzed) { this.totalAnalyzed = totalAnalyzed; }
    public Map<String, Long> getSentimentDistribution() { return sentimentDistribution; }
    public void setSentimentDistribution(Map<String, Long> sentimentDistribution) { this.sentimentDistribution = sentimentDistribution; }
    public double getAverageConfidence() { return averageConfidence; }
    public void setAverageConfidence(double averageConfidence) { this.averageConfidence = averageConfidence; }
    public List<PainPoint> getTopPainPoints() { return topPainPoints; }
    public void setTopPainPoints(List<PainPoint> topPainPoints) { this.topPainPoints = topPainPoints; }
    public List<TrendPoint> getTrendData() { return trendData; }
    public void setTrendData(List<TrendPoint> trendData) { this.trendData = trendData; }
    public String getSuggestions() { return suggestions; }
    public void setSuggestions(String suggestions) { this.suggestions = suggestions; }
}
