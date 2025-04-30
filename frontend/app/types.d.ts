// frontend/app/types.d.ts
export type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced';

export type IssueType = 
  | 'error' 
  | 'warning' 
  | 'info' 
  | 'convention' 
  | 'refactor' 
  | 'security' 
  | 'complexity';

export interface Issue {
  id: string;
  type: IssueType;
  file: string;
  line: number;
  message: string;
  code: string;
  url?: string;
  explanation?: {
    why: string;
    fix: string;
    example?: string;
  };
}

export interface AnalysisResult {
  project_type: string;
  linter: string;
  analysis: {
    success: boolean;
    issues?: Issue[];
    error?: string;
    raw_stderr?: string;
  };
}

export interface UserProfile {
  experienceLevel: ExperienceLevel;
  preferredExplanationStyle: 'technical' | 'balanced' | 'simple';
  learnedConcepts: string[];
  weakAreas: string[];
}