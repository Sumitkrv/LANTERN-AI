import { ArrowUpRight, BookOpen, CodeXml, Compass, PenLine } from 'lucide-react'

const suggestions = [
  {
    label: 'Explore an idea', description: 'Why do fireflies glow?', Icon: Compass, tint: 'jade',
    prompt: 'Why do fireflies glow? Explain the science in plain language.',
  },
  {
    label: 'Write something', description: 'Draft a thoughtful thank-you', Icon: PenLine, tint: 'amber',
    prompt: 'Help me write a short, thoughtful note thanking a colleague for their help.',
  },
  {
    label: 'Build with code', description: 'Understand async in JavaScript', Icon: CodeXml, tint: 'sage',
    prompt: 'Explain async and await in JavaScript with one short, practical example.',
  },
  {
    label: 'Learn a skill', description: 'Plan a week of language practice', Icon: BookOpen, tint: 'sand',
    prompt: 'Build a one-week practice plan for a beginner learning a new language.',
  },
]

export function ChatEmptyState({ onSuggestion }: { onSuggestion: (prompt: string) => void }) {
  return (
    <div className="empty-state">
      <section className="welcome">
        <div className="welcome-content">
          <h1>What would you<br className="wide-break" /> like to explore?</h1>
          <p>Start with a question, a rough idea, or something you’re curious about.</p>
        </div>
      </section>
      <section className="suggestions" aria-labelledby="suggestions-heading">
        <h2 id="suggestions-heading" className="eyebrow">Try a prompt</h2>
        <div className="suggestion-grid">
          {suggestions.map(({ label, description, Icon, tint, prompt }) => (
            <button key={label} type="button" className="suggestion" onClick={() => onSuggestion(prompt)}>
              <span className={`suggestion-icon ${tint}`}><Icon size={18} strokeWidth={1.7} /></span>
              <span className="suggestion-copy"><strong>{label}</strong><small>{description}</small></span>
              <ArrowUpRight size={15} className="suggestion-arrow" />
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}
