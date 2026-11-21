import type { ResponseMetadata } from '../../types/api'

export function TokenUsage({ metadata }: { metadata?: ResponseMetadata }) {
  const input = metadata?.input_tokens
  const output = metadata?.output_tokens
  const scale = Math.max(input ?? 0, output ?? 0, 1)

  return (
    <section className="intelligence-section" aria-label="Token usage">
      <h3>Token usage</h3>
      {[{ name: 'Input', value: input }, { name: 'Output', value: output }].map(({ name, value }) => (
        <div className="usage-row" key={name}>
          <div><span>{name}</span><b>{value ?? '—'}</b></div>
          <div className="meter" aria-hidden="true">
            <i className={name.toLowerCase()} style={{ width: `${((value ?? 0) / scale) * 100}%` }} />
          </div>
        </div>
      ))}
    </section>
  )
}
