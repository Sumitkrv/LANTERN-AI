import { useEffect, useRef, useState } from 'react'
import { chatError, sendChat } from '../services/chatService'
import type { Message } from '../types/chat'

function newId(): string {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID()
  return Array.from(crypto.getRandomValues(new Uint8Array(16)), (byte) =>
    byte.toString(16).padStart(2, '0'),
  ).join('')
}

export function useChat() {
  const [sessionId, setSessionId] = useState<string>(() => {
  return localStorage.getItem('lantern-session-id') || newId()
  })

  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const saved = localStorage.getItem('lantern-messages')
      return saved ? JSON.parse(saved) as Message[] : []
    } catch {
      return []
    }
  })
  const [pending, setPending] = useState<Message | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [draft, setDraft] = useState('')
  const [systemPrompt, setSystemPrompt] = useState<string>()
  const [error, setError] = useState('')
  const activeRequest = useRef<AbortController | null>(null)

  useEffect(() => () => activeRequest.current?.abort(), [])
  useEffect(() => {
    localStorage.setItem('lantern-session-id', sessionId)
  }, [sessionId])

  useEffect(() => {
    localStorage.setItem('lantern-messages', JSON.stringify(messages))
  }, [messages])

  function newConversation() {
    activeRequest.current?.abort()
    activeRequest.current = null
    setSessionId(newId())
    setMessages([])
    setPending(null)
    setSelectedId(null)
    setSystemPrompt(undefined)
    setDraft('')
    setError('')
  }

  async function submit() {
    const message = draft.trim()
    if (!message || activeRequest.current) return

    const request = new AbortController()
    const userMessage: Message = { id: newId(), role: 'user', content: message }
    activeRequest.current = request
    setPending(userMessage)
    setError('')

    try {
      const result = await sendChat(
        { session_id: sessionId, message, system_prompt: systemPrompt },
        request.signal,
      )
      if (activeRequest.current !== request) return
      const assistant: Message = {
        id: newId(), role: 'assistant', content: result.reply, metadata: result.metadata,
      }
      setMessages((existing) => [...existing, userMessage, assistant])
      setSelectedId(assistant.id)
      setDraft('')
    } catch (cause) {
      if (activeRequest.current === request && !request.signal.aborted) setError(chatError(cause))
    } finally {
      if (activeRequest.current === request) {
        activeRequest.current = null
        setPending(null)
      }
    }
  }

  const selected = messages.find((message) => message.id === selectedId)
  const metadata = selected?.role === 'assistant' ? selected.metadata : undefined

  return {
    sessionId, messages, pending, selectedId, setSelectedId, metadata, draft, setDraft,
    systemPrompt, setSystemPrompt, error, submit, newConversation,
  }
}
