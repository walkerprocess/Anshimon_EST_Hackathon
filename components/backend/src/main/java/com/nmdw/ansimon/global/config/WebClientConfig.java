package com.nmdw.ansimon.global.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.util.StringUtils;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
@EnableConfigurationProperties(ExternalApiProperties.class)
public class WebClientConfig {

    @Bean
    public WebClient kmaWebClient(WebClient.Builder builder, ExternalApiProperties properties) {
        return build(builder, properties.kma());
    }

    @Bean
    public WebClient shelterWebClient(WebClient.Builder builder, ExternalApiProperties properties) {
        return build(builder, properties.shelter());
    }

    @Bean
    public WebClient tmapWebClient(WebClient.Builder builder, ExternalApiProperties properties) {
        return build(builder, properties.tmap());
    }

    @Bean
    public WebClient mlWebClient(WebClient.Builder builder, ExternalApiProperties properties) {
        return build(builder, properties.ml());
    }

    @Bean
    public WebClient phoneWebClient(WebClient.Builder builder, ExternalApiProperties properties) {
        return build(builder, properties.phone());
    }

    private WebClient build(WebClient.Builder builder, ExternalApiProperties.Endpoint endpoint) {
        WebClient.Builder configuredBuilder = builder.clone().baseUrl(endpoint.baseUrl());
        if (StringUtils.hasText(endpoint.apiKey())) {
            configuredBuilder.defaultHeader("Authorization", "Bearer " + endpoint.apiKey());
        }
        return configuredBuilder.build();
    }
}
