import { Tab } from '@headlessui/react'
import { SimilarComponent } from '@/app/types'
import { cn } from '@/app/lib/utils'
import { CodeBlock } from '@/components/CodeBlock'
import { useState } from 'react'

interface Props {
  components: SimilarComponent[]
}

export function SimilarComponents({ components }: Props) {
  const [selectedIndex, setSelectedIndex] = useState(0)

  return (
    <div className="mt-8 bg-[rgb(var(--color-surface))] rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4 text-[rgb(var(--color-text-primary))]">
        Similar Components ({components.length})
      </h3>
      
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <div className="relative">
          <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-[rgb(var(--color-surface))] pointer-events-none" />
          <Tab.List className="flex overflow-x-scroll scrollbar-hide pb-2 mb-4 gap-2 relative">
            {components.map((component, idx) => (
              <Tab
                key={component.id}
                className={({ selected }) =>
                  cn(
                    'flex-shrink-0 px-4 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer',
                    'focus:outline-none focus:ring-2 focus:ring-[rgb(var(--color-primary))] focus:ring-offset-2',
                    selected
                      ? 'bg-[rgb(var(--color-primary))] text-[rgb(var(--color-text-inverse))]'
                      : 'bg-[rgb(var(--color-background))] text-[rgb(var(--color-text-secondary))] hover:bg-[rgb(var(--color-primary-dark))] hover:text-[rgb(var(--color-text-inverse))]'
                  )
                }
              >
                <span className="whitespace-nowrap">Component {idx + 1}</span>
                <span className="ml-2 opacity-75">
                  ({Math.round(component.similarity_score * 100)}%)
                </span>
              </Tab>
            ))}
          </Tab.List>
        </div>
        
        <Tab.Panels>
          {components.map((component) => (
            <Tab.Panel
              key={component.id}
              className="focus:outline-none"
            >
              <div className="space-y-4">
                <div>
                  <h4 className="text-lg font-medium text-[rgb(var(--color-text-primary))]">
                    {component.title}
                  </h4>
                  <p className="mt-2 text-[rgb(var(--color-text-secondary))]">
                    {component.summary}
                  </p>
                </div>
                
                <CodeBlock 
                  code={component.code_snippet} 
                  language="typescript"
                />
              </div>
            </Tab.Panel>
          ))}
        </Tab.Panels>
      </Tab.Group>
    </div>
  )
} 