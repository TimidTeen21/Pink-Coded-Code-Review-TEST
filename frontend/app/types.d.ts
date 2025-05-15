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
    id: string;
    flamingo_message?: string;
    explanation?: {
      why: string;
      fix: string;
      example?: string;
      advanced_tip?: string
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

  session_id?: string;
  temp_dir?: string;
  
  project_type: string;
  linter: string;
  temp_dir?: string;
  session_id?: string;
  complexity: string;
   security_scan: {
        success: boolean;
        issues: Issue[];
        error?: string;
  };
}

type OnFixType = (updatedIssues: Issue[]) => void;

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

