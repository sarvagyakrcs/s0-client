'use client'
import { CodeBlock } from './CodeBlock'
import { useState } from 'react'

interface SimilarComponent {
  id: string
  title: string
  summary: string
  code_snippet: string
  similarity_score: number
}

interface SimilarComponentsProps {
  components: SimilarComponent[]
}

export function SimilarComponents({ components }: SimilarComponentsProps) {
  const [activeTab, setActiveTab] = useState(0)

  return (
    <div className="space-y-4 mt-4 border-t border-[rgb(var(--color-border))] pt-4">
      <div className="flex flex-col">
        <h3 className="text-sm font-medium text-[rgb(var(--color-text-secondary))] mb-4">
          Similar Components
        </h3>
        <div className="flex space-x-2 mb-4 overflow-x-auto pb-2">
          {components.map((component, index) => (
            <button
              key={component.id}
              onClick={() => setActiveTab(index)}
              className={`px-4 py-2 rounded-md text-sm whitespace-nowrap transition-colors ${
                activeTab === index
                  ? 'bg-[rgb(var(--color-primary))] text-[rgb(var(--color-text-inverse))]'
                  : 'bg-[rgb(var(--color-assistant-bubble))] text-[rgb(var(--color-text-secondary))] hover:bg-[rgb(var(--color-primary-light))]'
              }`}
            >
              Component {index + 1} ({Math.round(component.similarity_score * 100)}%)
            </button>
          ))}
        </div>
        
        {components[activeTab] && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-[rgb(var(--color-text-primary))]">
              {components[activeTab].title}
            </h4>
            <p className="text-sm text-[rgb(var(--color-text-secondary))]">
              {components[activeTab].summary}
            </p>
            <CodeBlock 
              code={components[activeTab].code_snippet} 
              language="typescript"
            />
          </div>
        )}
      </div>
    </div>
  )
} 