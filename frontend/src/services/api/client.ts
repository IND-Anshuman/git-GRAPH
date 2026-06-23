/**
 * Axios-based API client with interceptors, retry logic, and error normalization.
 * Spec: Task 2.2, 2.3 — 10s timeout, 3 retry attempts, exponential backoff.
 */
import axios, { AxiosInstance, AxiosError } from "axios";
import { API_BASE_URL, API_TIMEOUT_MS } from "@/lib/constants";
import { DomainError, HTTP_ERROR_CODES } from "@/types/platform";

// Retry configuration
const MAX_RETRIES = 2; // 3 total attempts
const RETRY_DELAYS_MS = [1000, 2000, 4000]; // 1s, 2s, 4s

/** Status codes that should NOT be retried */
const NO_RETRY_STATUSES = new Set([400, 401, 403, 404, 422]);

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isRetryable(status?: number): boolean {
  if (!status) return true; // network error
  return !NO_RETRY_STATUSES.has(status);
}

function normalizeError(error: AxiosError): DomainError {
  const status = error.response?.status ?? 0;
  const code = HTTP_ERROR_CODES[status] ?? "UNKNOWN_ERROR";

  const responseData = error.response?.data as Record<string, unknown> | undefined;
  let message = "An unexpected error occurred. Please try again.";

  if (responseData && typeof responseData === "object") {
    const detail = responseData.detail;
    if (typeof detail === "string") message = detail;
  }

  if (error.code === "ECONNABORTED" || error.message.includes("timeout")) {
    return new DomainError("TIMEOUT", "Request timed out. Please try again.", 408);
  }

  if (!error.response) {
    return new DomainError(
      "NETWORK_ERROR",
      "Unable to connect to the server. Please check your connection.",
      0
    );
  }

  return new DomainError(code, message, status, responseData as Record<string, unknown>);
}

/** Create a configured axios instance with retry logic. */
function createAPIClient(): AxiosInstance {
  const instance = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT_MS,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  });

  // Request interceptor — dev logging
  instance.interceptors.request.use((config) => {
    const requestId = Math.random().toString(36).slice(2, 9);
    config.headers["X-Request-Id"] = requestId;

    if (process.env.NODE_ENV === "development") {
      console.debug(
        `[API] → ${config.method?.toUpperCase()} ${config.url}`,
        { requestId, params: config.params }
      );
    }

    return config;
  });

  // Response interceptor — dev logging + error normalization + retry
  instance.interceptors.response.use(
    (response) => {
      if (process.env.NODE_ENV === "development") {
        const requestId = response.config.headers["X-Request-Id"];
        console.debug(
          `[API] ← ${response.status} ${response.config.url}`,
          { requestId, duration: "~" }
        );
      }
      return response;
    },
    async (error: AxiosError) => {
      const config = error.config as (typeof error.config & { _retryCount?: number }) | undefined;
      if (!config) throw normalizeError(error);

      config._retryCount = config._retryCount ?? 0;

      const shouldRetry =
        config._retryCount < MAX_RETRIES &&
        isRetryable(error.response?.status);

      if (shouldRetry) {
        config._retryCount++;
        const delay = RETRY_DELAYS_MS[config._retryCount - 1] ?? 4000;

        if (process.env.NODE_ENV === "development") {
          console.warn(
            `[API] Retry #${config._retryCount} in ${delay}ms — ${config.url}`,
            { status: error.response?.status }
          );
        }

        await sleep(delay);
        return instance(config);
      }

      throw normalizeError(error);
    }
  );

  return instance;
}

export const apiClient = createAPIClient();
