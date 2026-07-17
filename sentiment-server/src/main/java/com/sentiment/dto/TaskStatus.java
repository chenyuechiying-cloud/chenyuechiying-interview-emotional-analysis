package com.sentiment.dto;

/**
 * 任务进度状态
 */
public class TaskStatus {

    private String taskId;
    private String status;          // RUNNING / COMPLETED / FAILED
    private long total;
    private long completed;
    private long failed;
    private double percentage;

    public TaskStatus() {}

    public TaskStatus(String taskId, String status, long total,
                      long completed, long failed) {
        this.taskId = taskId;
        this.status = status;
        this.total = total;
        this.completed = completed;
        this.failed = failed;
        this.percentage = total > 0 ? (completed + failed) * 100.0 / total : 0;
    }

    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public long getTotal() {
        return total;
    }

    public void setTotal(long total) {
        this.total = total;
    }

    public long getCompleted() {
        return completed;
    }

    public void setCompleted(long completed) {
        this.completed = completed;
    }

    public long getFailed() {
        return failed;
    }

    public void setFailed(long failed) {
        this.failed = failed;
    }

    public double getPercentage() {
        return percentage;
    }

    public void setPercentage(double percentage) {
        this.percentage = percentage;
    }
}
