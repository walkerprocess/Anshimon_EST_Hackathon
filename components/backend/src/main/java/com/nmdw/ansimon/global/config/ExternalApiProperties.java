package com.nmdw.ansimon.global.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "ansimon.external")
public record ExternalApiProperties(
        Endpoint kma,
        Endpoint shelter,
        Endpoint tmap,
        Endpoint ml,
        Endpoint phone
) {

    public record Endpoint(
            String baseUrl,
            String apiKey
    ) {
    }
}
