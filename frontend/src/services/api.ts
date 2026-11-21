const baseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '')

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

function detailMessage(detail: unknown): string {
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail)) {
    const item = detail.find((entry: unknown) =>
      typeof entry === 'object' && entry !== null && 'msg' in entry && typeof entry.msg === 'string',
    )
    if (item) return String(item.msg)
  }
  return 'Please check the message and try again.'
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, options)
  if (!response.ok) {
    const body: { detail?: unknown } | null = await response.json().catch(() => null)
    throw new ApiError(response.status, detailMessage(body?.detail))
  }
  return response.json() as Promise<T>
}
