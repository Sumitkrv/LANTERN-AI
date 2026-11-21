import { Activity, Check, Copy } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message } from '../../types/chat'

interface AssistantMessageProps {
  message: Extract<Message, { role: 'assistant' }>
  selected: boolean
  onInspect: () => void
}

export function AssistantMessage({ message, selected, onInspect }: AssistantMessageProps) {
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle')
  const timer = useRef<number>(undefined)
  const { metadata } = message
  const cached = metadata.resolution_source === 'LLM_CACHE'
  useEffect(() => () => window.clearTimeout(timer.current), [])

  async function copy() {
    window.clearTimeout(timer.current)
    try {
      await navigator.clipboard.writeText(message.content)
      setCopyState('copied')
    } catch {
      setCopyState('failed')
    }
    timer.current = window.setTimeout(() => setCopyState('idle'), 2000)
  }

  return (
    <article className="assistant-message" data-testid="assistant-message">
      <div className="message-heading">
        <img src="/lantern.svg" alt="" width="30" height="30" /><strong>Lantern</strong>
        <div className="message-actions">
          <button type="button" className="icon-button" onClick={copy} aria-label="Copy reply" title="Copy reply">
            {copyState === 'copied' ? <Check size={16} /> : <Copy size={16} />}
          </button>
          <span className={copyState === 'failed' ? 'copy-error' : 'sr-only'} role="status">
            {copyState === 'copied' ? 'Reply copied' : copyState === 'failed' ? 'Could not copy' : ''}
          </span>
          <button
            type="button" className="icon-button inspect-button" onClick={onInspect}
            aria-label="Inspect this reply" title="Inspect this reply" aria-pressed={selected}
          ><Activity size={17} /></button>
        </div>
      </div>
      <div className="reply-content">
        <Markdown remarkPlugins={[remarkGfm]} skipHtml disallowedElements={['img']}>{message.content}</Markdown>
      </div>
      <dl className="message-metadata" aria-label="Reply metadata">
        <div><dt className="sr-only">Source</dt><dd className={`source-tag ${cached ? 'cached' : 'live'}`} data-testid="meta-source">{metadata.resolution_source}</dd></div>
        <div><dt className="sr-only">Model</dt><dd className="message-model" data-testid="meta-model">{metadata.model}</dd></div>
        <div><dt className="sr-only">Latency</dt><dd data-testid="meta-latency">{metadata.latency_ms} ms</dd></div>
        <div><dt>Input</dt><dd data-testid="meta-input-tokens">{metadata.input_tokens}</dd></div>
        <div><dt>Output</dt><dd data-testid="meta-output-tokens">{metadata.output_tokens}</dd></div>
      </dl>
    </article>
  )
}
