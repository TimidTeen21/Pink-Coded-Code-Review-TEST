export type Issue = {
  type: 'error' | 'warning' | 'info'
  file: string
  line: number
  message: string
  code: string
}

export type AnalysisResult = {
  project_type: string
  linter: string
  analysis: {
    success: boolean
    issues?: Issue[]
    error?: string
  }
}