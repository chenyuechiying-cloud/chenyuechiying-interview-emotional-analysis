package com.sentiment.client;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * DeepSeek API 客户端
 * 负责构造结构化 Prompt、调用大模型API、解析 JSON 响应
 */
@Component
public class DeepSeekApiClient {

    private static final Logger log = LoggerFactory.getLogger(DeepSeekApiClient.class);
    private static final Pattern CODE_FENCE_PATTERN =
            Pattern.compile("```(?:json)?\\s*|```", Pattern.CASE_INSENSITIVE);

    private final RestClient restClient;
    private final ObjectMapper objectMapper;

    @Value("${deepseek.model:deepseek-chat}")
    private String model;

    public DeepSeekApiClient(RestClient deepSeekRestClient, ObjectMapper objectMapper) {
        this.restClient = deepSeekRestClient;
        this.objectMapper = objectMapper;
    }

    /**
     * 情感分析结果 POJO
     */
    public record SentimentPayload(
            String sentiment,
            double confidence,
            List<String> keywords,
            Map<String, String> aspect_keywords
    ) {}

    /**
     * 调用 DeepSeek API 对单条评论进行情感分析
     *
     * @param reviewText 评论原文
     * @return 解析后的情感分析结果
     * @throws DeepSeekException API 调用或解析失败
     */
    public SentimentPayload analyzeSentiment(String reviewText) throws DeepSeekException {
        String systemPrompt = buildSystemPrompt();
        String userPrompt = buildUserPrompt(reviewText);

        Map<String, Object> requestBody = Map.of(
                "model", model,
                "temperature", 0.3,
                "response_format", Map.of("type", "json_object"),
                "messages", List.of(
                        Map.of("role", "system", "content", systemPrompt),
                        Map.of("role", "user", "content", userPrompt)
                )
        );

        try {
            String responseJson = restClient.post()
                    .uri("/v1/chat/completions")
                    .body(requestBody)
                    .retrieve()
                    .body(String.class);

            return parseResponse(responseJson);

        } catch (DeepSeekException e) {
            throw e;
        } catch (Exception e) {
            log.error("DeepSeek API 调用失败: {}", e.getMessage());
            throw new DeepSeekException("API 调用失败: " + e.getMessage(), e);
        }
    }

    /**
     * 构造系统 Prompt
     */
    private String buildSystemPrompt() {
        return """
            你是一个专业的电商评论情感分析专家。你的任务是分析中文商品评论的情感倾向。

            请严格按以下 JSON 格式返回分析结果（只返回 JSON，不要包含任何其他文本）：
            {
              "sentiment": "positive|negative|neutral",
              "confidence": 0.0-1.0,
              "keywords": ["关键词1", "关键词2"],
              "aspect_keywords": {"方面": "关键词", ...}
            }

            判断规则：
            1. sentiment: 表达满意、赞美、推荐 → positive；表达不满、抱怨、问题 → negative；中性描述或好坏参半 → neutral
            2. confidence: 情感明确 → 0.85-1.0；较为明确 → 0.7-0.85；模糊 → 0.5-0.7
            3. keywords: 提取 2-5 个情感核心关键词（功能、体验、质量相关短语）
            4. aspect_keywords: 按 "充电"、"系统"、"售后"、"续航"、"做工"、"性价比" 等方面归类关键词
            """;
    }

    /**
     * 构造用户 Prompt（包含待分析评论）
     */
    private String buildUserPrompt(String reviewText) {
        return "请分析以下用户评论的情感倾向：\n\n评论内容：" + reviewText;
    }

    /**
     * 解析 DeepSeek API 响应
     */
    private SentimentPayload parseResponse(String responseJson) throws DeepSeekException {
        try {
            JsonNode root = objectMapper.readTree(responseJson);
            JsonNode choices = root.path("choices");

            if (choices.isEmpty()) {
                throw new DeepSeekException("API 返回的 choices 为空");
            }

            String content = choices.get(0).path("message").path("content").asText();
            if (content == null || content.isBlank()) {
                throw new DeepSeekException("API 返回的 content 为空");
            }

            // 尝试直接解析 JSON
            try {
                return parseContent(content);
            } catch (JsonProcessingException e) {
                // 如果失败，尝试去掉 markdown 代码块标记后重试
                log.warn("JSON 解析失败，尝试去除代码块标记后重试");
                String cleaned = CODE_FENCE_PATTERN.matcher(content).replaceAll("").trim();
                return parseContent(cleaned);
            }

        } catch (DeepSeekException e) {
            throw e;
        } catch (Exception e) {
            throw new DeepSeekException("响应解析失败: " + e.getMessage(), e);
        }
    }

    /**
     * 解析 content 中的 JSON
     */
    private SentimentPayload parseContent(String jsonContent) throws JsonProcessingException {
        JsonNode payload = objectMapper.readTree(jsonContent);

        String sentiment = payload.path("sentiment").asText("neutral");
        double confidence = payload.path("confidence").asDouble(0.0);

        List<String> keywords = objectMapper.convertValue(
                payload.path("keywords"),
                objectMapper.getTypeFactory().constructCollectionType(List.class, String.class)
        );

        Map<String, String> aspectKeywords = objectMapper.convertValue(
                payload.path("aspect_keywords"),
                objectMapper.getTypeFactory().constructMapType(Map.class, String.class, String.class)
        );

        // 规范化情感标签
        String normalizedSentiment = switch (sentiment.toLowerCase()) {
            case "positive", "正面", "积极" -> "positive";
            case "negative", "负面", "消极" -> "negative";
            default -> "neutral";
        };

        return new SentimentPayload(normalizedSentiment, confidence, keywords, aspectKeywords);
    }

    /**
     * 自定义异常
     */
    public static class DeepSeekException extends Exception {
        public DeepSeekException(String message) {
            super(message);
        }

        public DeepSeekException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
