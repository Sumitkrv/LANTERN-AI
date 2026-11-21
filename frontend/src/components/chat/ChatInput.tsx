import { ArrowUp, CornerDownLeft } from 'lucide-react'
import { useLayoutEffect } from 'react'
import type { RefObject } from 'react'

interface ChatInputProps {
  inputRef: RefObject<HTMLTextAreaElement | null>
  value: string
  busy: boolean
  onChange: (value: string) => void
  onSubmit: () => void
}

export function ChatInput({ inputRef, value, busy, onChange, onSubmit }: ChatInputProps) {
  useLayoutEffect(() => {
    const input = inputRef.current
    if (!input) return
    input.style.height = '0px'
    input.style.height = `${input.scrollHeight}px`
  }, [inputRef, value])

  return (
    <div className="composer-wrap">
      <form className="composer" onSubmit={(event) => { event.preventDefault(); onSubmit() }}>
        <label className="sr-only" htmlFor="chat-message">Message Lantern</label>
        <textarea
          ref={inputRef} id="chat-message" data-testid="chat-input" value={value} rows={1}
          placeholder="Ask Lantern anything…" readOnly={busy}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
              event.preventDefault()
              onSubmit()
            }
          }}
        />
        <button
          className="send-button" type="submit" data-testid="send-button"
          aria-label="Send message" disabled={busy || !value.trim()}
        >
          <ArrowUp size={21} strokeWidth={2.2} />
        </button>
      </form>
      <div className="composer-hints">
        <span><CornerDownLeft size={13} /> Enter to send</span>
        <span>Shift + Enter for a new line</span>
      </div>
    </div>
  )
}
