import { useRef, useState } from 'react'
import { ResponseIntelligence } from './components/analytics/ResponseIntelligence'
import { ChatInput } from './components/chat/ChatInput'
import { ChatWindow } from './components/chat/ChatWindow'
import { Dialog } from './components/layout/Dialog'
import { Header } from './components/layout/Header'
import { Sidebar } from './components/layout/Sidebar'
import { SystemPromptSettings } from './components/settings/SystemPromptSettings'
import { useChat } from './hooks/useChat'
import { useHealth } from './hooks/useHealth'

export default function App() {
  const chat = useChat()
  const health = useHealth()
  const input = useRef<HTMLTextAreaElement>(null)
  const [dialog, setDialog] = useState<'settings' | 'details' | null>(null)

  function focusInput() { input.current?.focus() }

  function startConversation() {
    chat.newConversation()
    focusInput()
  }

  function inspect(id: string) {
    chat.setSelectedId(id)
    if (matchMedia('(max-width: 1100px)').matches) setDialog('details')
  }

  return (
    <div className="workspace">
      <Sidebar
        sessionId={chat.sessionId} health={health} onNew={startConversation}
        onSettings={() => setDialog('settings')} onConversation={focusInput}
      />
      <main className="conversation" aria-label="Conversation workspace">
        <Header
          health={health} onNew={startConversation} onSettings={() => setDialog('settings')}
          onDetails={() => setDialog('details')}
        />
        <ChatWindow
          messages={chat.messages} pending={chat.pending} selectedId={chat.selectedId} error={chat.error}
          onSuggestion={(prompt) => { if (!chat.pending) { chat.setDraft(prompt); focusInput() } }}
          onInspect={inspect}
        />
        <ChatInput
          inputRef={input} value={chat.draft} busy={Boolean(chat.pending)}
          onChange={chat.setDraft} onSubmit={() => { void chat.submit() }}
        />
      </main>
      <aside className="intelligence-panel" aria-label="Reply inspector">
        <ResponseIntelligence metadata={chat.metadata} />
      </aside>
      {dialog === 'settings' && (
        <SystemPromptSettings
          prompt={chat.systemPrompt} onSave={chat.setSystemPrompt} onClose={() => setDialog(null)}
        />
      )}
      {dialog === 'details' && (
        <Dialog title="Response intelligence" drawer onClose={() => setDialog(null)}>
          <ResponseIntelligence metadata={chat.metadata} showTitle={false} />
        </Dialog>
      )}
    </div>
  )
}
