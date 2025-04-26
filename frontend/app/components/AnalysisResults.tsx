import React from 'react';
import { FiAlertTriangle, FiInfo, FiCheckCircle } from 'react-icons/fi';

interface Issue {
  type: 'error' | 'warning' | 'info' | 'convention' | 'refactor';
  file: string;
  line: number;
  message: string;
  code: string;
  url?: string;
}

interface AnalysisResultProps {
  result?: {
    project_type: string;
    linter: string;
    analysis: {
      success: boolean;
      issues?: Issue[];
      error?: string;
      raw_stderr?: string;
    };
  };
}

const AnalysisResults: React.FC<AnalysisResultProps> = ({ result }) => {
  if (!result) return null;

  const getSeverityIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <FiAlertTriangle className="text-red-500" />;
      case 'warning':
        return <FiAlertTriangle className="text-yellow-500" />;
      default:
        return <FiInfo className="text-blue-500" />;
    }
  };

  const getSeverityColor = (type: string) => {
    switch (type) {
      case 'error':
        return 'bg-red-500/10 border-red-500/30';
      case 'warning':
        return 'bg-yellow-500/10 border-yellow-500/30';
      default:
        return 'bg-blue-500/10 border-blue-500/30';
    }
  };

  const hasError = !!result.analysis.error;
  const issues = result.analysis.issues || [];
  const hasIssues = issues.length > 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 p-4 bg-gray-800/50 rounded-lg">
        <div className="flex-1">
          <h3 className="text-lg font-medium text-pink-flamingo">
            Analysis Results
          </h3>
          <div className="flex gap-4 text-sm text-gray-300">
            <span>Project Type: {result.project_type}</span>
            <span>Linter: {result.linter}</span>
            <span className={hasError ? 'text-red-400' : 'text-green-400'}>
              {hasError ? 'Failed' : 'Success'}
            </span>
          </div>
        </div>
        {!hasError && (
          <div className="px-3 py-1 bg-dark-triangle/50 rounded-full text-xs">
            {hasIssues ? `${issues.length} issues found` : 'No issues found'}
          </div>
        )}
      </div>

      {hasError ? (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <div className="flex items-center gap-2 text-red-400">
            <FiAlertTriangle />
            <span>Error: {result.analysis.error}</span>
          </div>
          {result.analysis.raw_stderr && (
            <pre className="mt-2 text-xs text-red-300 overflow-auto max-h-40">
              {result.analysis.raw_stderr}
            </pre>
          )}
        </div>
      ) : hasIssues ? (
        <div className="space-y-2">
          {issues.map((issue, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getSeverityColor(issue.type)}`}
            >
              <div className="flex items-start gap-3">
                <div className="pt-1">
                  {getSeverityIcon(issue.type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-mono text-sm">
                      {issue.file}:{issue.line}
                    </span>
                    <span className="text-xs bg-gray-700 px-2 py-0.5 rounded">
                      {issue.code}
                    </span>
                  </div>
                  <p className="mt-1 text-sm">{issue.message}</p>
                  {issue.url && (
                    <a
                      href={issue.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 inline-block text-xs text-pink-flamingo hover:underline"
                    >
                      Learn more about this issue
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
          <div className="flex items-center gap-2 text-green-400">
            <FiCheckCircle />
            <span>No issues found!</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;