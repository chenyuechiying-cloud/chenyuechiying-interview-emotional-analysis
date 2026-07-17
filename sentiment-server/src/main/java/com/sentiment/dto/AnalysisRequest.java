package com.sentiment.dto;

/**
 * 分析任务请求
 */
public class AnalysisRequest {

    private String productName;     // 可选: 限定商品名称
    private int batchSize = 100;    // 每批分析数量

    public AnalysisRequest() {}

    public AnalysisRequest(String productName, int batchSize) {
        this.productName = productName;
        this.batchSize = batchSize;
    }

    public String getProductName() {
        return productName;
    }

    public void setProductName(String productName) {
        this.productName = productName;
    }

    public int getBatchSize() {
        return batchSize;
    }

    public void setBatchSize(int batchSize) {
        this.batchSize = batchSize;
    }
}
