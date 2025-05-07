// frontend/app/components/AnalysisResults.tsx
import React, { useState } from 'react';
import { 
  FiAlertTriangle, 
  FiInfo, 
  FiCheckCircle,
  FiShield,
  FiCpu,
  FiFile,
  FiExternalLink,
  FiChevronDown,
  FiChevronUp,
  FiThumbsUp,
  FiThumbsDown,
  FiEdit
} from 'react-icons/fi';
import { Issue, AnalysisResult } from '@/types';

interface AnalysisResultProps {
  result?: AnalysisResult;
  userId: string; // Added for user tracking
}

const AnalysisResults: React.FC<AnalysisResultProps> = ({ result, userId }) => {
  const [expandedIssues, setExpandedIssues] = useState<Record<string, boolean>>({});
  const [feedbackGiven, setFeedbackGiven] = useState<Record<string, boolean>>({});
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [editorContent, setEditorContent] = useState('');

  if (!result) {
    console.log("No results available");
    return null;
  }
  console.log("Full results object:", result);

  // Helper functions
  const getSeverityIcon = (type: Issue['type']) => {
    const className = "h-4 w-4";
    switch (type) {
      case 'error': return <FiAlertTriangle className={`text-red-400 ${className}`} />;
      case 'warning': return <FiAlertTriangle className={`text-yellow-400 ${className}`} />;
      case 'security': return <FiShield className={`text-purple-400 ${className}`} />;
      case 'complexity': return <FiCpu className={`text-orange-400 ${className}`} />;
      default: return <FiInfo className={`text-blue-400 ${className}`} />;
    }
  };

  const getSeverityColor = (type: Issue['type']) => {
    switch (type) {
      case 'error': return 'bg-red-900/20 border-red-400/30';
      case 'warning': return 'bg-yellow-900/20 border-yellow-400/30';
      case 'security': return 'bg-purple-900/20 border-purple-400/30';
      case 'complexity': return 'bg-orange-900/20 border-orange-400/30';
      default: return 'bg-blue-900/20 border-blue-400/30';
    }
  };

  const getSeverityLabel = (type: Issue['type']) => {
    switch (type) {
      case 'error': return 'Error';
      case 'warning': return 'Warning';
      case 'security': return 'Security';
      case 'complexity': return 'Complexity';
      case 'info': return 'Info';
      case 'convention': return 'Convention';
      case 'refactor': return 'Refactor';
      default: return type;
    }
  };

  // Event handlers
  const toggleExpand = (issueId: string) => {
    setExpandedIssues(prev => ({
      ...prev,
      [issueId]: !prev[issueId]
    }));
  };

  const handleFeedback = async (issueId: string, isHelpful: boolean) => {
    try {
      await fetch('http://localhost:8000/api/v1/feedback/explanation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          issue_code: issueId.split('-').pop(),
          was_helpful: isHelpful,
          complexity: "intermediate"
        })
      });
      setFeedbackGiven(prev => ({ ...prev, [issueId]: true }));
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const handleOpenEditor = (filePath: string) => {
    setActiveFile(filePath);
    // In a real implementation, fetch file content here
    setEditorContent(`// Sample content for ${filePath}\n// This would be the actual file content`);
  };

  // Data processing
  const hasError = !!result.main_analysis?.error;
  const issues = [
    ...(result.main_analysis?.issues || []),
    ...(result.complexity_analysis?.issues || []),
    ...(result.security_scan?.issues || [])
  ];
  console.log("Collected issues:", issues);
  const hasIssues = issues.length > 0;

  const issuesWithIds = issues.map(issue => ({
    ...issue,
    id: `${issue.file}-${issue.line}-${issue.code}`
  }));

  const issuesByFile = issuesWithIds.reduce((acc, issue) => {
    if (!acc[issue.file]) acc[issue.file] = [];
    acc[issue.file].push(issue);
    return acc;
  }, {} as Record<string, typeof issuesWithIds>);

  return (
    <div className="space-y-4">
      {/* Results Header */}
      <div className="flex items-center gap-4 p-4 bg-gray-800 rounded-lg">
        <div className="flex-1">
          <h3 className="text-lg font-medium text-pink-500">
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
          <div className="px-3 py-1 bg-gray-700 rounded-full text-xs">
            {hasIssues ? `${issues.length} issues found` : 'No issues found'}
          </div>
        )}
      </div>

      {/* Error Display */}
      {hasError ? (
        <div className="p-4 bg-red-900/20 border border-red-400/30 rounded-lg">
          <div className="flex items-center gap-2 text-red-400">
            <FiAlertTriangle className="h-4 w-4" />
            <span>Error: {result.main_analysis?.error}</span>
          </div>
          {result.main_analysis?.raw?.stderr && (
            <pre className="mt-2 text-xs text-red-300 overflow-auto max-h-40">
              {result.main_analysis.raw.stderr}
            </pre>
          )}
        </div>
      ) : hasIssues ? (
        <div className="space-y-6">
          {Object.entries(issuesByFile).map(([file, fileIssues]) => (
            <div key={file} className="space-y-3 bg-gray-800/50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-mono text-gray-200">
                  <FiFile className="flex-shrink-0 h-4 w-4" />
                  <span className="truncate">{file}</span>
                  <span className="text-xs bg-gray-700 px-2 py-0.5 rounded">
                    {fileIssues.length} issue{fileIssues.length > 1 ? 's' : ''}
                  </span>
                </div>
                <button
                  onClick={() => handleOpenEditor(file)}
                  className="flex items-center gap-1 text-xs text-pink-400 hover:text-pink-300"
                >
                  <FiEdit className="h-3 w-3" />
                  Edit File
                </button>
              </div>
              
              <div className="space-y-3 mt-2">
                {fileIssues.map((issue) => (
                  <div
                    key={issue.id}
                    className={`p-4 rounded-lg border ${getSeverityColor(issue.type)} hover:bg-opacity-30 transition-colors`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="pt-1">
                        {getSeverityIcon(issue.type)}
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className={`text-xs font-medium px-2 py-0.5 rounded ${
                            issue.type === 'error' ? 'bg-red-500/20 text-red-100' :
                            issue.type === 'warning' ? 'bg-yellow-500/20 text-yellow-100' :
                            issue.type === 'security' ? 'bg-purple-500/20 text-purple-100' :
                            issue.type === 'complexity' ? 'bg-orange-500/20 text-orange-100' :
                            'bg-blue-500/20 text-blue-100'
                          }`}>
                            {getSeverityLabel(issue.type)}
                          </span>
                          <span className="text-xs font-mono text-gray-300">
                            Line {issue.line}
                          </span>
                          <span className="text-xs font-mono bg-gray-700/70 text-gray-200 px-2 py-0.5 rounded">
                            {issue.code}
                          </span>
                        </div>
                        <p className="text-sm text-gray-100">{issue.message}</p>

                        {/* Explanation Section */}
                        {issue.explanation && (
                          <div className={`mt-3 space-y-3 ${expandedIssues[issue.id] ? 'block' : 'hidden'}`}>
                            <div className="bg-gray-800/70 p-3 rounded">
                              <h4 className="font-medium text-gray-200 mb-1">Why this matters:</h4>
                              <p className="text-sm text-gray-300">{issue.explanation.why}</p>
                            </div>
                            <div className="bg-gray-800/70 p-3 rounded">
                              <h4 className="font-medium text-gray-200 mb-1">How to fix:</h4>
                              <pre className="text-sm text-gray-300 whitespace-pre-wrap">{issue.explanation.fix}</pre>
                            </div>
                            {issue.explanation.example && (
                              <div className="bg-gray-800/70 p-3 rounded">
                                <h4 className="font-medium text-gray-200 mb-1">Example:</h4>
                                <pre className="text-sm text-gray-300 whitespace-pre-wrap">{issue.explanation.example}</pre>
                              </div>
                            )}
                            {issue.explanation?.advanced_tip && (
                            <div className="mt-3 p-3 bg-gray-800/50 border-l-4 border-purple-500">
                              <h4 className="font-medium text-purple-300">Pro Tip:</h4>
                               <p className="text-sm text-gray-200">{issue.explanation.advanced_tip}</p>
                             </div>
                             )}

                            {!feedbackGiven[issue.id] && (
                              <div className="flex gap-2 mt-2">
                                <button 
                                  onClick={() => handleFeedback(issue.id, true)}
                                  className="text-xs flex items-center gap-1 bg-green-900/30 hover:bg-green-900/50 px-2 py-1 rounded text-green-300"
                                >
                                  <FiThumbsUp className="h-3 w-3" /> Helpful
                                </button>
                                <button 
                                  onClick={() => handleFeedback(issue.id, false)}
                                  className="text-xs flex items-center gap-1 bg-red-900/30 hover:bg-red-900/50 px-2 py-1 rounded text-red-300"
                                >
                                  <FiThumbsDown className="h-3 w-3" /> Not helpful
                                </button>
                              </div>
                            )}
                          </div>
                        )}

                        <div className="flex justify-between items-center mt-2">
                          {issue.url && (
                            <a
                              href={issue.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-xs text-pink-300 hover:text-pink-200 hover:underline"
                            >
                              Learn more <FiExternalLink className="h-3 w-3" />
                            </a>
                          )}
                          {issue.explanation && (
                            <button
                              onClick={() => toggleExpand(issue.id)}
                              className="text-xs flex items-center gap-1 text-gray-400 hover:text-gray-200"
                            >
                              {expandedIssues[issue.id] ? (
                                <>
                                  <FiChevronUp className="h-3 w-3" /> Hide details
                                </>
                              ) : (
                                <>
                                  <FiChevronDown className="h-3 w-3" /> Show explanation
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 bg-green-900/20 border border-green-400/30 rounded-lg">
          <div className="flex items-center gap-2 text-green-400">
            <FiCheckCircle className="h-4 w-4" />
            <span>No issues found!</span>
          </div>
        </div>
      )}

      {/* Code Editor Section */}
      {activeFile && (
        <div className="mt-6 bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
          <div className="flex items-center justify-between bg-gray-700/50 p-3">
            <div className="flex items-center gap-2 text-sm font-mono text-gray-300">
              <FiFile className="h-4 w-4" />
              <span>{activeFile}</span>
            </div>
            <button
              onClick={() => setActiveFile(null)}
              className="text-gray-400 hover:text-gray-200"
            >
              <FiChevronDown className="h-4 w-4" />
            </button>
          </div>
          <div className="h-96 p-4 bg-gray-900">
            <pre className="h-full overflow-auto font-mono text-sm text-gray-300">
              {editorContent}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;