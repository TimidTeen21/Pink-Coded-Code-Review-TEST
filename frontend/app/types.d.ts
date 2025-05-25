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

interface AnalysisResult {
  project_type: string;
  experience_level: string;
  // Either flattened structure
  main_analysis?: {
    issues?: Issue[];
    error?: string;
    raw_stderr?: string;
    success?: boolean;
  };
  complexity_analysis?: {
    issues?: Issue[];
  };
  security_scan?: {
    issues?: Issue[];
  };
  // OR nested structure
  result?: {
    main_analysis?: {
      issues?: Issue[];
      error?: string;
      raw_stderr?: string;
      success?: boolean;
    };
    complexity_analysis?: {
      issues?: Issue[];
    };
    security_scan?: {
      issues?: Issue[];
    };
  };
  session_id?: string;
  temp_dir?: string;
  linter?: string;
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
