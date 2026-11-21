import { Activity, ChevronRight, Plus, SlidersHorizontal } from 'lucide-react'
import type { HealthState } from '../../hooks/useHealth'

interface HeaderProps {
  health: HealthState
  onNew: () => void
  onSettings: () => void
  onDetails: () => void
}

export function Header({ health, onNew, onSettings, onDetails }: HeaderProps) {
  const status = { ready: 'Gateway online', offline: 'Gateway unavailable', checking: 'Connecting' }
  return (
    <header className="workspace-header">
      <div className="breadcrumb">
        <img className="mobile-brand" src="/lantern.svg" width="30" height="30" alt="LANTERN AI" />
        <span>Workspace</span><ChevronRight size={15} /><b>Conversation</b>
      </div>
      <div className="header-actions">
        <div className="header-health">
          <i className={`status-dot ${health.state}`} />{status[health.state]}
        </div>
        <button className="icon-button mobile-action" type="button" aria-label="New conversation" title="New conversation" onClick={onNew}><Plus size={19} /></button>
        <button className="icon-button mobile-action" type="button" aria-label="Session settings" title="Session settings" onClick={onSettings}><SlidersHorizontal size={18} /></button>
        <button className="icon-button details-action" type="button" aria-label="Response intelligence" title="Response intelligence" onClick={onDetails}><Activity size={19} /></button>
      </div>
    </header>
  )
}
