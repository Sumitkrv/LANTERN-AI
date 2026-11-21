import { TriangleAlert } from 'lucide-react'
import { useAutoScroll } from '../../hooks/useAutoScroll'
import type { Message } from '../../types/chat'
import { AssistantMessage } from './AssistantMessage'
import { ChatEmptyState } from './ChatEmptyState'

interface ChatWindowProps {
  messages: Message[]
  pending: Message | null
  selectedId: string | null
  error: string
  onSuggestion: (prompt: string) => void
  onInspect: (id: string) => void
}

export function ChatWindow({ messages, pending, selectedId, error, onSuggestion, onInspect }: ChatWindowProps) {
  const viewport = useAutoScroll(messages.length, Boolean(pending), error)
  const visible = pending ? [...messages, pending] : messages

  return (
    <div className="chat-scroll" ref={viewport}>
      <div className="conversation-content">
        {visible.length === 0 && <ChatEmptyState onSuggestion={onSuggestion} />}
        {visible.length > 0 && (
          <section className="transcript" aria-label="Conversation messages" role="log">
            {visible.map((message) => message.role === 'user' ? (
              <article className="user-message" key={message.id}>
                <strong>You</strong><p>{message.content}</p>
              </article>
            ) : (
              <AssistantMessage
                key={message.id} message={message} selected={message.id === selectedId}
                onInspect={() => onInspect(message.id)}
              />
            ))}
          </section>
        )}
        {pending && (
          <div className="pending-message" role="status">
            <img src="/lantern.svg" width="28" height="28" alt="" />
            <span>Lantern is thinking</span><i /><i /><i />
          </div>
        )}
        {error && <div className="chat-error" role="alert"><TriangleAlert size={18} /> {error}</div>}
      </div>
    </div>
  )
}
