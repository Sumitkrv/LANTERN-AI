import type { ChatRequest, ChatResponse, HealthResponse } from '../types/api'
import { ApiError, apiRequest } from './api'

export function sendChat(payload: ChatRequest, signal: AbortSignal): Promise<ChatResponse> {
  return apiRequest<ChatResponse>('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  })
}

export function getHealth(signal: AbortSignal): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/health', { signal, cache: 'no-store' })
}

export function chatError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 422) return `Check your message. ${error.message}`
    if (error.status === 503) return 'The model providers are temporarily unavailable. Please try again.'
    if (error.status === 502) return 'The model could not complete this request. Try again or shorten the conversation.'
    return 'Something went wrong while sending your message. Please try again.'
  }
  return 'Lantern could not reach the server. Check your connection and try again.'
}
