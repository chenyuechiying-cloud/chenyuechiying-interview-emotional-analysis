package com.sentiment.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sentiment.dto.ReportData;
import com.sentiment.repository.CommentRepository;
import com.sentiment.repository.SentimentResultRepository;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;

/**
 * 报告与统计 REST API
 */
@RestController
@RequestMapping("/api/report")
public class ReportController {

    private final SentimentResultRepository resultRepository;
    private final CommentRepository commentRepository;
    private final ObjectMapper objectMapper;

    public ReportController(SentimentResultRepository resultRepository,
                             CommentRepository commentRepository,
                             ObjectMapper objectMapper) {
        this.resultRepository = resultRepository;
        this.commentRepository = commentRepository;
        this.objectMapper = objectMapper;
    }

    /**
     * 获取报告摘要
     * GET /api/report/summary
     */
    @GetMapping("/summary")
    public ResponseEntity<ReportData> getSummary(
            @RequestParam(required = false) String product) {

        ReportData report = new ReportData();

        // 总分析数
        report.setTotalAnalyzed(resultRepository.count());

        // 情感分布
        Map<String, Long> distribution = new LinkedHashMap<>();
        distribution.put("positive", resultRepository.countBySentimentLabel("positive"));
        distribution.put("negative", resultRepository.countBySentimentLabel("negative"));
        distribution.put("neutral", resultRepository.countBySentimentLabel("neutral"));
        report.setSentimentDistribution(distribution);

        // 平均置信度
        Double avgConf = resultRepository.getAverageConfidence();
        report.setAverageConfidence(avgConf != null ? avgConf : 0.0);

        // Top 5 痛点
        report.setTopPainPoints(analyzePainPoints(product));

        // 优化建议
        report.setSuggestions(generateSuggestions(product));

        return ResponseEntity.ok(report);
    }

    /**
     * 获取情感趋势数据
     * GET /api/report/trend?startDate=&endDate=&granularity=month
     */
    @GetMapping("/trend")
    public ResponseEntity<List<ReportData.TrendPoint>> getTrend(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate,
            @RequestParam(defaultValue = "%Y-%m") String granularity) {

        String dateFormat = switch (granularity) {
            case "day" -> "%Y-%m-%d";
            case "week" -> "%Y-%u";
            default -> "%Y-%m";
        };

        List<Object[]> raw = resultRepository.getTrendRaw(startDate, endDate, dateFormat);

        // 按日期聚合
        Map<String, ReportData.TrendPoint> trendMap = new LinkedHashMap<>();
        for (Object[] row : raw) {
            String date = (String) row[0];
            String label = (String) row[1];
            long count = ((Number) row[2]).longValue();

            trendMap.putIfAbsent(date, new ReportData.TrendPoint(date, 0, 0, 0));
            ReportData.TrendPoint point = trendMap.get(date);
            switch (label) {
                case "positive" -> point.setPositive(count);
                case "negative" -> point.setNegative(count);
                case "neutral" -> point.setNeutral(count);
            }
        }

        return ResponseEntity.ok(new ArrayList<>(trendMap.values()));
    }

    /**
     * 痛点分析：从负面评论中提取高频关键词
     */
    private List<ReportData.PainPoint> analyzePainPoints(String product) {
        List<String> keywordJsons = resultRepository.findNegativeKeywords(product);

        // 统计关键词频率
        Map<String, Long> keywordCount = new LinkedHashMap<>();
        for (String json : keywordJsons) {
            if (json == null || json.isBlank()) continue;
            try {
                @SuppressWarnings("unchecked")
                List<String> keywords = objectMapper.readValue(json, List.class);
                for (String kw : keywords) {
                    keywordCount.merge(kw, 1L, Long::sum);
                }
            } catch (JsonProcessingException e) {
                // 跳过解析失败的关键词
            }
        }

        // 排序取 Top 5
        var sorted = keywordCount.entrySet().stream()
                .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                .limit(5)
                .toList();

        List<ReportData.PainPoint> painPoints = new ArrayList<>();
        for (var entry : sorted) {
            String suggestion = SUGGESTION_MAP.getOrDefault(entry.getKey(),
                    "建议关注「" + entry.getKey() + "」相关问题，收集更多用户反馈，针对性优化产品体验。");
            painPoints.add(new ReportData.PainPoint(
                    entry.getKey(),
                    entry.getValue(),
                    (double) entry.getValue() / keywordCount.size() * 100,
                    List.of(), // 示例评论可在需要时查询
                    suggestion
            ));
        }

        return painPoints;
    }

    /**
     * 基于痛点生成优化建议
     */
    private String generateSuggestions(String product) {
        return """
            基于情感分析结果，产品优化建议如下：

            1. 充电速度：优先提升充电功率或优化充电协议兼容性，考虑标配快充配件。
            2. 系统卡顿：加强系统性能优化，定期推送固件更新，优化内存管理策略。
            3. 售后响应：建立快速响应机制，增加在线客服人力，缩短退换货处理周期。
            4. 续航不足：优化电池容量或软件功耗管理，在宣传中如实标注续航数据。
            5. 做工质量：加强品控流程，对高频缺陷（接口松动、缝隙等）进行专项改进。

            建议产品团队按优先级分阶段推进上述优化，并以季度为单位追踪用户反馈变化。
            """;
    }

    /**
     * 痛点 → 优化建议映射
     */
    private static final Map<String, String> SUGGESTION_MAP;

    static {
        Map<String, String> map = new java.util.HashMap<>();
        map.put("充电速度", "建议提升充电功率至更高瓦数，或标配快充充电器，优化充电协议兼容性。");
        map.put("充电慢", "建议提升充电功率至更高瓦数，或标配快充充电器，优化充电协议兼容性。");
        map.put("系统卡顿", "建议优化系统动画流畅度，减少预装应用，定期推送性能优化更新。");
        map.put("卡顿", "建议优化系统动画流畅度，减少预装应用，定期推送性能优化更新。");
        map.put("售后响应慢", "建议建立售后响应SLA标准，增加在线客服人数，缩短退换货周期至3天内。");
        map.put("售后", "建议建立售后响应SLA标准，增加在线客服人数，缩短退换货周期至3天内。");
        map.put("续航不足", "建议提升电池容量或优化功耗管理，在宣传中如实标注典型续航时长。");
        map.put("续航", "建议提升电池容量或优化功耗管理，在宣传中如实标注典型续航时长。");
        map.put("做工粗糙", "建议加强来料检验和出厂品控，对接口松动、外壳缝隙等问题进行专项改进。");
        map.put("做工", "建议加强来料检验和出厂品控，对接口松动、外壳缝隙等问题进行专项改进。");
        map.put("发热", "建议优化散热设计，控制高负载场景下的温度，增加过热保护机制。");
        map.put("音质差", "建议升级音频硬件或调优软件算法，提供均衡器功能满足不同用户偏好。");
        map.put("连接不稳定", "建议升级蓝牙/无线芯片固件，优化天线设计提升连接稳定性。");
        SUGGESTION_MAP = java.util.Collections.unmodifiableMap(map);
    }
}
