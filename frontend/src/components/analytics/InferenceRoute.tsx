import { ArrowRight, CircleCheck, Database, KeyRound, Workflow } from 'lucide-react'
import type { ResponseMetadata } from '../../types/api'

export function InferenceRoute({ metadata }: { metadata?: ResponseMetadata }) {
  const route = metadata?.resolution_source === 'LLM_CACHE'
    ? [{ label: 'Cache', Icon: Database, state: 'cache' }]
    : metadata
      ? [
          ...Array.from({ length: metadata.fallback_attempts }, (_, i) => ({
            label: `key_${i + 1}`, Icon: KeyRound, state: 'failed',
          })),
          { label: metadata.key_id ?? 'Provider', Icon: KeyRound, state: 'success' },
        ]
      : [{ label: 'Provider or cache', Icon: Workflow, state: 'waiting' }]

  return (
    <section className="intelligence-section" aria-label="Inference route">
      <h3>Inference route</h3>
      <div className="route" aria-label={metadata ? 'Observed route' : 'Route appears after a reply'}>
        {route.map(({ label, Icon, state }) => (
          <span className="route-step" key={label}>
            <span className={`route-node ${state}`} title={state === 'failed' ? 'Failed attempt' : undefined}>
              <Icon size={13} /> {label}{state === 'failed' && <span className="sr-only"> failed</span>}
            </span>
            <ArrowRight size={13} className="route-arrow" aria-hidden="true" />
          </span>
        ))}
        <span className={`route-node ${metadata ? 'success' : 'waiting'}`}><CircleCheck size={13} /> Reply</span>
      </div>
      {metadata && (
        <p className="route-note">{metadata.fallback_attempts} fallback {metadata.fallback_attempts === 1 ? 'attempt' : 'attempts'}</p>
      )}
    </section>
  )
}
