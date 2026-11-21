import { Activity, CircleHelp, Database, Radio } from 'lucide-react'
import type { ResponseMetadata } from '../../types/api'
import { InferenceRoute } from './InferenceRoute'
import { LatencyIndicator } from './LatencyIndicator'
import { TokenUsage } from './TokenUsage'

interface IntelligenceProps {
  metadata?: ResponseMetadata
  showTitle?: boolean
}

export function ResponseIntelligence({ metadata, showTitle = true }: IntelligenceProps) {
  const isCached = metadata?.resolution_source === 'LLM_CACHE'

  return (
    <section className="intelligence" aria-label="Response intelligence">
      {showTitle && (
        <header className="intelligence-header">
          <span className="intelligence-icon"><Activity size={18} /></span>
          <div><h2>Response intelligence</h2><p>How the selected reply was generated</p></div>
        </header>
      )}
      <div className={`resolution-card ${metadata ? 'resolved' : ''}`}>
        <span className="resolution-icon">
          {!metadata ? <Activity size={19} /> : isCached ? <Database size={19} /> : <Radio size={19} />}
        </span>
        <div>
          <span className="eyebrow">{metadata ? 'Resolution source' : 'Response status'}</span>
          <strong>{metadata ? metadata.resolution_source : 'Awaiting a reply'}</strong>
        </div>
      </div>
      <dl className="provider-data">
        <div><dt>Model</dt><dd>{metadata?.model ?? '—'}</dd></div>
        <div><dt>Key identifier</dt><dd>{metadata?.key_id ?? '—'}</dd></div>
      </dl>
      <InferenceRoute metadata={metadata} />
      <LatencyIndicator latency={metadata?.latency_ms} />
      <TokenUsage metadata={metadata} />
      <div className="intelligence-note">
        <CircleHelp size={16} />
        <p><b>Live or cached?</b> Live replies come from the model. A cache hit reuses a reply for the same conversation context.</p>
      </div>
    </section>
  )
}
