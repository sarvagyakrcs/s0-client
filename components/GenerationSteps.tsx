'use client'
import { FaCode, FaSearch, FaBrain } from 'react-icons/fa'

interface GenerationStepsProps {
  currentStep: number
}

export function GenerationSteps({ currentStep }: GenerationStepsProps) {
  const steps = [
    {
      icon: FaSearch,
      title: 'Finding Similar Components',
      description: 'Searching through component database using BERT embeddings'
    },
    {
      icon: FaBrain,
      title: 'Analyzing Code Patterns',
      description: 'Processing code structure with CodeBERT embeddings'
    },
    {
      icon: FaCode,
      title: 'Generating Component',
      description: 'Creating optimized code with Gemini AI'
    }
  ]

  return (
    <div className="w-full max-w-2xl mx-auto bg-[rgb(var(--color-surface))] rounded-lg p-4 shadow-[var(--shadow-md)]">
      <div className="flex justify-between relative">
        {/* Progress Bar */}
        <div 
          className="absolute top-5 left-0 h-1 bg-[rgb(var(--color-primary))] transition-all duration-500"
          style={{ width: `${(currentStep / steps.length) * 100}%` }}
        />
        
        {steps.map((step, index) => (
          <div 
            key={step.title} 
            className={`flex flex-col items-center relative z-10 transition-opacity duration-300 ${
              index <= currentStep ? 'opacity-100' : 'opacity-40'
            }`}
          >
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              index <= currentStep 
                ? 'bg-[rgb(var(--color-primary))]' 
                : 'bg-[rgb(var(--color-border))]'
            }`}>
              <step.icon className="w-5 h-5 text-[rgb(var(--color-text-inverse))]" />
            </div>
            <h3 className="mt-2 text-sm font-medium text-[rgb(var(--color-text-primary))]">
              {step.title}
            </h3>
            <p className="mt-1 text-xs text-[rgb(var(--color-text-secondary))] text-center max-w-[120px]">
              {step.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
} 