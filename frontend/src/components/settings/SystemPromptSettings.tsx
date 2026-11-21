import { useState } from 'react'
import { Dialog } from '../layout/Dialog'

interface SystemPromptSettingsProps {
  prompt: string | undefined
  onSave: (prompt: string) => void
  onClose: () => void
}

export function SystemPromptSettings({ prompt, onSave, onClose }: SystemPromptSettingsProps) {
  const [value, setValue] = useState(prompt ?? '')
  return (
    <Dialog title="Session settings" onClose={onClose}>
      <form className="settings-form" onSubmit={(event) => {
        event.preventDefault()
        onSave(value)
        onClose()
      }}>
        <label htmlFor="system-prompt">System prompt</label>
        <p id="system-prompt-help">Set instructions for future replies in this conversation. Saving an empty prompt removes the instructions.</p>
        <textarea
          id="system-prompt" data-testid="system-prompt-input" aria-describedby="system-prompt-help"
          value={value} onChange={(event) => setValue(event.target.value)}
          placeholder="For example, use plain language and keep replies brief."
        />
        <div className="settings-actions">
          <button className="secondary-button" type="button" onClick={onClose}>Cancel</button>
          <button className="primary-button" type="submit">Save settings</button>
        </div>
      </form>
    </Dialog>
  )
}
