package com.sentiment.controller;

import com.sentiment.dto.AnalysisRequest;
import com.sentiment.dto.AnalysisResponse;
import com.sentiment.dto.TaskStatus;
import com.sentiment.model.Comment;
import com.sentiment.model.SentimentResult;
import com.sentiment.service.AsyncAnalysisService;
import com.sentiment.service.SentimentService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 分析任务 REST API
 */
@RestController
@RequestMapping("/api/analysis")
public class AnalysisController {

    private final AsyncAnalysisService asyncAnalysisService;
    private final SentimentService sentimentService;

    public AnalysisController(AsyncAnalysisService asyncAnalysisService,
                               SentimentService sentimentService) {
        this.asyncAnalysisService = asyncAnalysisService;
        this.sentimentService = sentimentService;
    }

    /**
     * 启动批量分析任务
     * POST /api/analysis/start
     */
    @PostMapping("/start")
    public ResponseEntity<AnalysisResponse> startAnalysis(@RequestBody AnalysisRequest request) {
        AnalysisResponse response = asyncAnalysisService.startAnalysis(
                request.getProductName());
        if (response.getTaskId() == null) {
            return ResponseEntity.ok(response);
        }
        return ResponseEntity.accepted().body(response);
    }

    /**
     * 查询任务进度
     * GET /api/analysis/status/{taskId}
     */
    @GetMapping("/status/{taskId}")
    public ResponseEntity<TaskStatus> getStatus(@PathVariable String taskId) {
        TaskStatus status = asyncAnalysisService.getProgress(taskId);
        if (status == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(status);
    }

    /**
     * 多维度查询分析结果
     * GET /api/results?product=&startDate=&endDate=&sentiment=&page=0&size=20
     */
    @GetMapping("/results")
    public ResponseEntity<Map<String, Object>> queryResults(
            @RequestParam(required = false) String product,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate,
            @RequestParam(required = false) String sentiment,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {

        Page<Comment> commentPage = sentimentService.queryResults(
                product, startDate, endDate, sentiment, PageRequest.of(page, size));

        // 构造带分析结果的响应
        var content = commentPage.getContent().stream().map(comment -> {
            SentimentResult result = sentimentService.getResult(comment.getId());
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("commentId", comment.getId());
            item.put("productName", comment.getProductName());
            item.put("reviewText", comment.getReviewText());
            item.put("rating", comment.getRating());
            item.put("reviewTime", comment.getReviewTime());
            item.put("reviewerName", comment.getReviewerName());
            if (result != null) {
                item.put("sentiment", Map.of(
                        "label", result.getSentimentLabel(),
                        "confidence", result.getConfidence(),
                        "keywords", result.getKeywords()
                ));
            }
            return item;
        }).toList();

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("content", content);
        response.put("page", page);
        response.put("size", size);
        response.put("totalElements", commentPage.getTotalElements());
        response.put("totalPages", commentPage.getTotalPages());

        return ResponseEntity.ok(response);
    }
}
