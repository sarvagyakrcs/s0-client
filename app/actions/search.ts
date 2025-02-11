'use server'

export type GenerateResponse = {
  generated_code: string
  similar_components: Array<{
    id: string
    title: string
    summary: string
    code_snippet: string
    similarity_score: number
  }>
  explanation: string
}

export async function generateComponent(
  query: string,
  output_format: 'html' | 'jsx-js' | 'jsx-ts',
  similar_count: number = 3
): Promise<GenerateResponse> {
  try {
    const response = await fetch('http://127.0.0.1:8000/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        output_format,
        similar_count,
      }),
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to generate component')
    }

    return data
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to generate component')
  }
} 