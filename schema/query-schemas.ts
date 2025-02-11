import { z } from 'zod'

export const messageSchema = z.object({
  message: z.string().min(1, 'Message is required'),
})

export const chatMessageSchema = z.object({
  id: z.string(),
  content: z.string(),
  role: z.enum(['user', 'assistant']),
  createdAt: z.string(),
})

export type Message = z.infer<typeof chatMessageSchema>
export type FormData = z.infer<typeof messageSchema> 