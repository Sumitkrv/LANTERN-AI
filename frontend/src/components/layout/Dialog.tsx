import { useEffect, useId, useRef } from 'react'
import type { ReactNode } from 'react'
import { X } from 'lucide-react'

interface DialogProps {
  title: string
  children: ReactNode
  onClose: () => void
  drawer?: boolean
}

export function Dialog({ title, children, onClose, drawer = false }: DialogProps) {
  const dialog = useRef<HTMLDialogElement>(null)
  const titleId = useId()

  useEffect(() => {
    const element = dialog.current
    element?.showModal()
    return () => { element?.close() }
  }, [])

  return (
    <dialog
      className={drawer ? 'dialog drawer' : 'dialog'} aria-labelledby={titleId} ref={dialog}
      onCancel={(event) => { event.preventDefault(); onClose() }}
      onClick={(event) => { if (event.target === event.currentTarget) onClose() }}
    >
      <div className="dialog-inner">
        <header className="dialog-header">
          <h2 id={titleId}>{title}</h2>
          <button type="button" className="icon-button" aria-label="Close" onClick={onClose}><X size={20} /></button>
        </header>
        {children}
      </div>
    </dialog>
  )
}
