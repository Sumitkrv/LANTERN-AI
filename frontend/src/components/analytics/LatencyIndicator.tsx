import { Timer } from 'lucide-react'

export function LatencyIndicator({ latency }: { latency?: number }) {
  const scale = Math.max(1000, Math.ceil((latency ?? 0) / 1000) * 1000)
  return (
    <section className="intelligence-section latency-section" aria-label="Latency">
      <h3><Timer size={15} /> Server latency</h3>
      <div className="latency-value">{latency ?? '—'} <span>ms</span></div>
      <div className="meter latency-meter" aria-hidden="true">
        <i style={{ width: `${((latency ?? 0) / scale) * 100}%` }} />
      </div>
      {latency !== undefined && <div className="meter-scale"><span>0</span><span>{scale / 1000} s</span></div>}
    </section>
  )
}
