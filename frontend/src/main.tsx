import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource-variable/dm-sans'
import '@fontsource/instrument-serif/latin-400.css'
import './styles/tokens.css'
import './styles/globals.css'
import './styles/layout.css'
import './styles/chat.css'
import './styles/intelligence.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode><App /></StrictMode>,
)
