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

  interface Issue {
    type: string;
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
  main_analysis?: {
    issues?: Issue[];
    error?: string;
    success?: boolean;
    raw?: {
      stderr?: string;
    };
  };
  complexity_analysis?: {
    issues?: Issue[];
    error?: string;
    success?: boolean;
  };
  security_scan?: {
    issues?: Issue[];
    error?: string;
    success?: boolean;
  };
  
  project_type: string;
  linter: string;
}

/* Deepseek version
interface AnalysisResult {
  project_type: string;
  linter: string;
  main_analysis: {
    issues: Issue[];
    error?: string;
  };
  complexity_analysis: {
    issues: Issue[];
    error?: string;
  };
  security_scan: {
    issues: Issue[];
    error?: string;
  };
}
*/

export interface UserProfile {
  experienceLevel: ExperienceLevel;
  preferredExplanationStyle: 'technical' | 'balanced' | 'simple';
  learnedConcepts: string[];
  weakAreas: string[];
}

