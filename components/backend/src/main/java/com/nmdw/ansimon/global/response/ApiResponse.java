package com.nmdw.ansimon.global.response;

public record ApiResponse<T>(
        boolean success,
        T data,
        String error
) {

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, data, null);
    }

    public static <T> ApiResponse<T> failure(String error) {
        return new ApiResponse<>(false, null, error);
    }
}
