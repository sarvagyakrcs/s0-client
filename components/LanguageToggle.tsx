'use client'
import { FaCode, FaHtml5 } from 'react-icons/fa'
import { SiTypescript, SiJavascript } from 'react-icons/si'
import { useState } from 'react'

type Language = 'tsx' | 'html' | 'javascript' | 'typescript'

interface LanguageToggleProps {
  language: Language
  onChange: (language: Language) => void
}

export function LanguageToggle({ language, onChange }: LanguageToggleProps) {
  const [showTooltip, setShowTooltip] = useState<string | null>(null)

  const isTsxSelected = language === 'tsx' || language === 'javascript' || language === 'typescript'

  const handleTsxChange = (newLang: Language) => {
    if (language === 'tsx' && (newLang === 'javascript' || newLang === 'typescript')) {
      onChange(newLang)
    } else if (newLang === 'tsx' || newLang === 'html') {
      onChange(newLang)
    }
  }

  return (
    <div className="flex items-center space-x-2 bg-[rgb(var(--color-surface))] p-2 rounded-lg shadow-[var(--shadow-sm)]">
      <div className="relative">
        <button
          onClick={() => handleTsxChange('html')}
          onMouseEnter={() => setShowTooltip('html')}
          onMouseLeave={() => setShowTooltip(null)}
          className={`p-2 rounded-md transition-colors ${
            language === 'html'
              ? 'bg-[rgb(var(--color-primary))] text-[rgb(var(--color-text-inverse))]'
              : 'hover:bg-[rgb(var(--color-primary-light))] text-[rgb(var(--color-text-secondary))]'
          }`}
        >
          <FaHtml5 className="w-5 h-5" />
        </button>
        {showTooltip === 'html' && (
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-[rgb(var(--color-text-inverse))] bg-[rgb(var(--color-text-primary))] rounded shadow-md whitespace-nowrap">
            Generate HTML
          </div>
        )}
      </div>

      <div className="relative">
        <button
          onClick={() => handleTsxChange('tsx')}
          onMouseEnter={() => setShowTooltip('tsx')}
          onMouseLeave={() => setShowTooltip(null)}
          className={`p-2 rounded-md transition-colors ${
            isTsxSelected
              ? 'bg-[rgb(var(--color-primary))] text-[rgb(var(--color-text-inverse))]'
              : 'hover:bg-[rgb(var(--color-primary-light))] text-[rgb(var(--color-text-secondary))]'
          }`}
        >
          <FaCode className="w-5 h-5" />
        </button>
        {showTooltip === 'tsx' && (
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-[rgb(var(--color-text-inverse))] bg-[rgb(var(--color-text-primary))] rounded shadow-md whitespace-nowrap">
            Generate React Code
          </div>
        )}
      </div>

      {isTsxSelected && (
        <>
          <div className="relative">
            <button
              onClick={() => handleTsxChange('javascript')}
              onMouseEnter={() => setShowTooltip('js')}
              onMouseLeave={() => setShowTooltip(null)}
              className={`p-2 rounded-md transition-colors ${
                language === 'javascript'
                  ? 'bg-[rgb(var(--color-primary))] text-[rgb(var(--color-text-inverse))]'
                  : 'hover:bg-[rgb(var(--color-primary-light))] text-[rgb(var(--color-text-secondary))]'
              }`}
            >
              <SiJavascript className="w-5 h-5" />
            </button>
            {showTooltip === 'js' && (
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-[rgb(var(--color-text-inverse))] bg-[rgb(var(--color-text-primary))] rounded shadow-md whitespace-nowrap">
                Use JavaScript
              </div>
            )}
          </div>

          <div className="relative">
            <button
              onClick={() => handleTsxChange('typescript')}
              onMouseEnter={() => setShowTooltip('ts')}
              onMouseLeave={() => setShowTooltip(null)}
              className={`p-2 rounded-md transition-colors ${
                language === 'typescript'
                  ? 'bg-[rgb(var(--color-primary))] text-[rgb(var(--color-text-inverse))]'
                  : 'hover:bg-[rgb(var(--color-primary-light))] text-[rgb(var(--color-text-secondary))]'
              }`}
            >
              <SiTypescript className="w-5 h-5" />
            </button>
            {showTooltip === 'ts' && (
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-[rgb(var(--color-text-inverse))] bg-[rgb(var(--color-text-primary))] rounded shadow-md whitespace-nowrap">
                Use TypeScript
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
} 