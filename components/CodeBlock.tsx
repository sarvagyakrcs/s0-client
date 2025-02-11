'use client'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { nightOwl } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { FaCopy, FaCheck } from 'react-icons/fa'
import { useState } from 'react'

interface CodeBlockProps {
  code: string
  language: string
}

export function CodeBlock({ code, language }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative group rounded-lg">
      <button
        onClick={handleCopy}
        className="absolute right-2 top-2 p-2 rounded-lg bg-[rgba(255,255,255,0.1)] 
          text-[rgb(var(--color-text-inverse))] opacity-0 group-hover:opacity-100 
          transition-opacity duration-200 z-10"
        title="Copy code"
      >
        {copied ? <FaCheck className="w-4 h-4" /> : <FaCopy className="w-4 h-4" />}
      </button>
      <div className="overflow-x-auto max-w-4xl" >
        <SyntaxHighlighter
          language={language}
          style={nightOwl}
          customStyle={{
            margin: 0,
            borderRadius: '0.5rem',
            padding: '1.5rem',
          }}
          showLineNumbers
          wrapLines={true}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  )
} 