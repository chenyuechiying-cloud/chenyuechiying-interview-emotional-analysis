package com.sentiment.dto;

/**
 * 分析任务启动响应
 */
public class AnalysisResponse {

    private String taskId;
    private String message;
    private long totalCount;

    public AnalysisResponse() {}

    public AnalysisResponse(String taskId, String message, long totalCount) {
        this.taskId = taskId;
        this.message = message;
        this.totalCount = totalCount;
    }

    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public long getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(long totalCount) {
        this.totalCount = totalCount;
    }
}
