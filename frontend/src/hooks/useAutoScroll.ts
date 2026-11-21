import { useEffect, useRef } from 'react'

export function useAutoScroll(messageCount: number, pending: boolean, error: string) {
  const viewport = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!viewport.current) return
    const behavior = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
    viewport.current.scrollTo({ top: messageCount || pending || error ? viewport.current.scrollHeight : 0, behavior })
  }, [messageCount, pending, error])
  return viewport
}
