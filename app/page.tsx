'use client'
import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type Message, type FormData, messageSchema } from '@/schema/query-schemas'
import { v4 as uuidv4 } from 'uuid'
import { LanguageToggle } from '@/components/LanguageToggle'
import { generateComponent, type GenerateResponse } from '@/app/actions/search'
import { CodeBlock } from '@/components/CodeBlock'
import { GenerationSteps } from '@/components/GenerationSteps'
import { SimilarComponents } from '@/components/SimilarComponents'
import { toast } from 'react-hot-toast'

type Language = 'tsx' | 'html' | 'javascript' | 'typescript'

const INITIAL_MESSAGE: Message = {
  id: uuidv4(),
  content: "I am S0, your AI assistant. How can I help you today?",
  role: 'assistant',
  createdAt: new Date().toISOString(),
}

const Page = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(messageSchema),
  })

  const queryClient = useQueryClient()

  // Query for fetching messages
  const { data: messages = [] } = useQuery<Message[]>({
    queryKey: ['messages'],
    initialData: [INITIAL_MESSAGE],
  })

  const [language, setLanguage] = useState<Language>('tsx')
  const [generationStep, setGenerationStep] = useState(0)
  const [similarCount, setSimilarCount] = useState(4)

  const mutation = useMutation({
    mutationFn: async (data: FormData) => {
      setGenerationStep(0)
      
      const outputFormat = language === 'html' 
        ? 'html' 
        : language === 'typescript' 
          ? 'jsx-ts' 
          : 'jsx-js'

      await new Promise(resolve => setTimeout(resolve, 1000))
      setGenerationStep(1)
      await new Promise(resolve => setTimeout(resolve, 1000))
      setGenerationStep(2)

      const result = await generateComponent(
        data.message,
        outputFormat,
        similarCount
      )
      
      return {
        message: {
          id: uuidv4(),
          content: `${result.explanation}\n\n\`\`\`${language}\n${result.generated_code}\n\`\`\``,
          role: 'assistant' as const,
          createdAt: new Date().toISOString(),
        },
        explanation: result.explanation,
        similarComponents: result.similar_components,
      }
    },
    onMutate: async (newMessage) => {
      await queryClient.cancelQueries({ queryKey: ['messages'] })
      const previousMessages = queryClient.getQueryData(['messages'])

      const optimisticMessage: Message = {
        id: uuidv4(),
        content: newMessage.message,
        role: 'user',
        createdAt: new Date().toISOString(),
      }

      queryClient.setQueryData<Message[]>(['messages'], (old = []) => [
        ...old,
        optimisticMessage,
      ])

      return { previousMessages }
    },
    onError: (error) => {
      toast.error('Failed to generate component')
    },
    onSuccess: (data) => {
      queryClient.setQueryData<Message[]>(['messages'], (old = []) => [
        ...old,
        data.message,
      ])

      // You can also store the explanation and similar components in another query
      queryClient.setQueryData(['lastGeneration'], {
        explanation: data.explanation,
        similarComponents: data.similarComponents,
      })
    },
    onSettled: () => {
      setGenerationStep(0)
      queryClient.invalidateQueries({ queryKey: ['messages'] })
      reset()
    },
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate(data)
  }

  const SimilarCountSelector = () => (
    <div className="flex items-center space-x-2">
      <label className="text-sm text-[rgb(var(--color-text-secondary))]">
        Similar files:
      </label>
      <select
        value={similarCount}
        onChange={(e) => setSimilarCount(Number(e.target.value))}
        className="bg-[rgb(var(--color-surface))] text-[rgb(var(--color-text-primary))] 
          rounded-md px-2 py-1 text-sm border border-[rgb(var(--color-border))]
          focus:outline-none focus:ring-2 focus:ring-[rgb(var(--color-primary))]"
      >
        {[2, 4, 6, 8, 10].map(num => (
          <option key={num} value={num}>{num}</option>
        ))}
      </select>
    </div>
  )

  return (
    <div className="flex flex-col min-h-screen chat-gradient">
      {/* Header */}
      <header className="fixed top-0 w-full bg-[rgb(var(--color-surface))] border-b border-[rgb(var(--color-border))] shadow-[var(--shadow-sm)] z-10">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-[rgb(var(--color-text-primary))]">
              s0.dev
            </h1>
            <div className="flex items-center space-x-4">
              <LanguageToggle language={language} onChange={setLanguage} />
              <SimilarCountSelector />
            </div>
          </div>
        </div>
      </header>

      {/* Main Chat Area - Add blur when loading */}
      <main className={`flex-1 max-w-5xl w-full mx-auto px-4 pt-24 pb-32 transition-all duration-200 ${
        mutation.isPending ? 'blur-sm' : ''
      }`}>
        <div className="bg-[rgb(var(--color-surface))] rounded-lg shadow-[var(--shadow-md)] p-6 mb-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div 
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div className="flex-shrink-0">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.role === 'user' 
                      ? 'bg-[rgb(var(--color-success))]' 
                      : 'bg-[rgb(var(--color-primary))]'
                  }`}>
                    <span className="text-[rgb(var(--color-text-inverse))] text-sm font-medium">
                      {message.role === 'user' ? 'U' : 'AI'}
                    </span>
                  </div>
                </div>
                <div className={`flex-1 rounded-lg p-4 ${
                  message.role === 'user' 
                    ? 'bg-[rgb(var(--color-user-bubble))]' 
                    : 'bg-[rgb(var(--color-assistant-bubble))]'
                }`}>
                  {message.role === 'assistant' && message.content.includes('```') ? (
                    <div className="space-y-4">
                      <p className="text-[rgb(var(--color-text-primary))]">
                        {message.content.split('```')[0].trim()}
                      </p>
                      <CodeBlock 
                        code={message.content.split('```')[1].split('\n').slice(1, -1).join('\n')}
                        language={language === 'html' ? 'html' : 'typescript'}
                      />
                      {queryClient.getQueryData<{similarComponents: any[]}>(['lastGeneration'])?.similarComponents && (
                        <SimilarComponents 
                          components={queryClient.getQueryData<{similarComponents: any[]}>(['lastGeneration'])!.similarComponents} 
                        />
                      )}
                    </div>
                  ) : (
                    <p className="text-[rgb(var(--color-text-primary))]">
                      {message.content}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Loading Steps - Add backdrop */}
      {mutation.isPending && (
        <>
          <div className="fixed inset-0 bg-black/20 z-40" />
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
            <div className="w-full max-w-2xl">
              <GenerationSteps currentStep={generationStep} />
            </div>
          </div>
        </>
      )}

      {/* Input Form - Add blur when loading */}
      <div className={`fixed bottom-0 left-0 right-0 bg-[rgb(var(--color-surface))] border-t border-[rgb(var(--color-border))] transition-all duration-200 ${
        mutation.isPending ? 'blur-sm' : ''
      }`}>
        <div className="max-w-5xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="relative">
              <textarea
                {...register('message')}
                className="w-full px-4 py-3 pr-24 rounded-lg border border-[rgb(var(--color-border))] 
                  focus:outline-none focus:ring-2 focus:ring-[rgb(var(--color-primary))] focus:border-transparent 
                  resize-none bg-[rgb(var(--color-surface))] text-[rgb(var(--color-text-primary))]"
                rows={3}
                placeholder="Type your message here..."
                style={{ minHeight: '80px' }}
              />
              <button
                type="submit"
                disabled={mutation.isPending}
                className="absolute bottom-3 right-3 px-4 py-2 
                  bg-[rgb(var(--color-primary))] hover:bg-[rgb(var(--color-primary-dark))]
                  text-[rgb(var(--color-text-inverse))] rounded-md 
                  focus:outline-none focus:ring-2 focus:ring-[rgb(var(--color-primary))] focus:ring-offset-2 
                  disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {mutation.isPending ? (
                  <div className="flex items-center space-x-2">
                    <svg className="animate-spin h-4 w-4 text-[rgb(var(--color-text-inverse))]" 
                      xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" 
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                      </path>
                    </svg>
                    <span>Sending</span>
                  </div>
                ) : (
                  'Send'
                )}
              </button>
            </div>
            
            {errors.message && (
              <p className="text-sm text-[rgb(var(--color-error))] mt-1">
                {errors.message.message}
              </p>
            )}
            
            {mutation.isError && (
              <div className="p-3 bg-[rgb(var(--color-error-light))] text-[rgb(var(--color-error))] rounded-md text-sm">
                {mutation.error.message || 'Something went wrong'}
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}

export default Page