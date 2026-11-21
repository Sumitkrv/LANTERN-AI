import { useEffect, useState } from 'react'
import { getHealth } from '../services/chatService'
import type { HealthResponse } from '../types/api'

export type HealthState = { state: 'checking' | 'offline' } | { state: 'ready'; data: HealthResponse }

export function useHealth(): HealthState {
  const [health, setHealth] = useState<HealthState>({ state: 'checking' })

  useEffect(() => {
    const request = new AbortController()
    let timer: number
    const check = async () => {
      try {
        const data = await getHealth(AbortSignal.any([request.signal, AbortSignal.timeout(8000)]))
        if (!request.signal.aborted) setHealth({ state: 'ready', data })
      } catch {
        if (!request.signal.aborted) setHealth({ state: 'offline' })
      }
      if (!request.signal.aborted) timer = window.setTimeout(check, 30000)
    }
    void check()
    return () => {
      request.abort()
      window.clearTimeout(timer)
    }
  }, [])

  return health
}
