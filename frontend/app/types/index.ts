// frontend/app/types/index.ts
export interface Issue {
    type: 'error' | 'warning' | 'info'
    file: string
    line: number
    message: string
    code: string
  }
  
  export interface AnalysisResult {
    project_type: string
    linter: string
    analysis: {
      success: boolean
      issues?: Issue[]
      error?: string
    }
  }