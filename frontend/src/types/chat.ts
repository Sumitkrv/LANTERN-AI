import type { ResponseMetadata } from './api'

export type Message =
  | { id: string; role: 'user'; content: string }
  | { id: string; role: 'assistant'; content: string; metadata: ResponseMetadata }
