import { CircleDot, MessageSquare, Plus, SlidersHorizontal } from 'lucide-react'
import type { HealthState } from '../../hooks/useHealth'

interface SidebarProps {
  sessionId: string
  health: HealthState
  onNew: () => void
  onSettings: () => void
  onConversation: () => void
}

export function Sidebar({ sessionId, health, onNew, onSettings, onConversation }: SidebarProps) {
  const ready = health.state === 'ready'
  const serviceLabel = {
    ready: 'Gateway online', checking: 'Checking gateway', offline: 'Gateway unavailable',
  }[health.state]

  return (
    <aside className="sidebar" aria-label="Workspace sidebar">
      <div className="brand">
        <img src="/lantern.svg" width="42" height="42" alt="" />
        <div><b>LANTERN<span> AI</span></b><small>Intelligence that stays connected.</small></div>
      </div>

      <button className="new-conversation" type="button" onClick={onNew}>
        <Plus size={17} /> New conversation
      </button>

      <nav className="workspace-nav" aria-label="Workspace">
        <p className="eyebrow">Workspace</p>
        <button type="button" className="nav-item current" aria-current="page" onClick={onConversation}>
          <MessageSquare size={17} /> Conversation
        </button>
        <button type="button" className="nav-item" onClick={onSettings}>
          <SlidersHorizontal size={17} /> Session settings
        </button>
      </nav>

      <div className="session-label">
        <p className="eyebrow">Active session</p>
        <div><CircleDot size={14} /> <code title={sessionId}>{sessionId.slice(0, 8)}</code></div>
      </div>

      <div className="sidebar-bottom">
        <div className="gateway-status" role="status">
          <div><i className={`status-dot ${health.state}`} /> {serviceLabel}</div>
          <p>{ready ? `${health.data.keys_configured} keys · Cache ${health.data.cache_enabled ? 'enabled' : 'disabled'}` : 'Service health'}</p>
        </div>
        <div className="version">LANTERN AI <span>v1.0</span></div>
      </div>
    </aside>
  )
}
