import React, { useState, useEffect } from 'react';
import { 
  FiAlertTriangle, FiInfo, FiCheckCircle, FiShield, 
  FiCpu, FiFile, FiExternalLink, FiChevronDown, 
  FiChevronUp, FiThumbsUp, FiThumbsDown, FiEdit,
  FiLoader, FiAlertCircle
} from 'react-icons/fi';
import { Issue, AnalysisResult } from '@/types';
import { CodeEditor } from '@/components/CodeEditor/CodeEditor';

interface AnalysisResultProps {
  result?: AnalysisResult;
  userId: string;
}

const AnalysisResults: React.FC<AnalysisResultProps> = ({ result, userId }) => {
  const [expandedIssues, setExpandedIssues] = useState<Record<string, boolean>>({});
  const [feedbackGiven, setFeedbackGiven] = useState<Record<string, boolean>>({});
  const [loadingExplanations, setLoadingExplanations] = useState<Record<string, boolean>>({});
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [issuesWithExplanations, setIssuesWithExplanations] = useState<Issue[]>([]);

  // Initialize with all issues
  useEffect(() => {
    if (result) {
      const allIssues = [
        ...(result.main_analysis?.issues || []),
        ...(result.complexity_analysis?.issues || []),
        ...(result.security_scan?.issues || [])
      ];
      setIssuesWithExplanations(allIssues);
    }
  }, [result]);

  const fetchFileContent = async (filePath: string) => {
    try {
      // In a real implementation, fetch actual file content from backend
      const mockContent = `// Mock content for ${filePath}\n// This would be fetched from the server`;
      setFileContent(mockContent);
      setActiveFile(filePath);
    } catch (error) {
      console.error('Failed to load file:', error);
    }
  };

  const toggleExpand = (issue: Issue) => {
    const issueId = `${issue.file}-${issue.line}-${issue.code}`;
    setExpandedIssues((prev) => ({
      ...prev,
      [issueId]: !prev[issueId],
    }));
  };

  const fetchExplanation = async (issue: Issue) => {
    const issueId = `${issue.file}-${issue.line}-${issue.code}`;
    setLoadingExplanations(prev => ({ ...prev, [issueId]: true }));
    
    try {
      const response = await fetch(
        `/api/v1/explanations?issue_code=${issue.code}&message=${encodeURIComponent(issue.message)}&file=${encodeURIComponent(issue.file)}&line=${issue.line}&user_id=${userId}`
      );
      
      if (!response.ok) {
        throw new Error(await response.text());
      }
  
      const explanation = await response.json();
      
      // Handle Gemini-specific response format
      if (explanation.source?.includes('gemini')) {
        setIssuesWithExplanations(prev => 
          prev.map(i => 
            i.file === issue.file && i.line === issue.line && i.code === issue.code 
              ? { 
                  ...i, 
                  explanation: {
                    why: explanation.why || "No explanation available",
                    fix: explanation.fix || "No fix suggestion available",
                    example: explanation.example,
                    source: explanation.source
                  }
                } 
              : i
          )
        );
      } else {
        // Handle template responses
        setIssuesWithExplanations(prev => 
          prev.map(i => 
            i.file === issue.file && i.line === issue.line && i.code === issue.code 
              ? { ...i, explanation } 
              : i
          )
        );
      }
    } catch (error) {
      console.error('Failed to fetch explanation:', error);
      setIssuesWithExplanations(prev => 
        prev.map(i => 
          i.file === issue.file && i.line === issue.line && i.code === issue.code 
            ? { 
                ...i, 
                explanation: {
                  why: "Failed to load explanation",
                  fix: "Please try again later",
                  source: "error"
                }
              } 
            : i
        )
      );
    } finally {
      setLoadingExplanations(prev => ({ ...prev, [issueId]: false }));
    }
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

  if (!result) {
    return (
      <div className="p-4 bg-gray-800 rounded-lg text-center">
        <p className="text-gray-400">No analysis results available</p>
      </div>
    );
  }

  const hasError = !!result.main_analysis?.error;
  const hasIssues = issuesWithExplanations.length > 0;
  
  // Group issues by file
  const issuesByFile = issuesWithExplanations.reduce((acc, issue) => {
    const issueId = `${issue.file}-${issue.line}-${issue.code}`;
    if (!acc[issue.file]) acc[issue.file] = [];
    acc[issue.file].push({ ...issue, id: issueId });
    return acc;
  }, {} as Record<string, any[]>);

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
            {hasIssues ? `${issuesWithExplanations.length} issues found` : 'No issues found'}
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
                  onClick={() => fetchFileContent(file)}
                  className="flex items-center gap-1 text-xs text-pink-400 hover:text-pink-300"
                >
                  <FiEdit className="h-3 w-3" />
                  View File
                </button>
              </div>
              
              <div className="space-y-3 mt-2">
                {fileIssues.map((issue) => {
                  const isLoading = loadingExplanations[issue.id];
                  const hasExplanation = !!issue.explanation;
                  const isExpanded = expandedIssues[issue.id];
                  
                  return (
                    <div
                      key={issue.id}
                      className={`p-4 rounded-lg border ${
                        issue.type === 'error' ? 'bg-red-900/20 border-red-400/30' :
                        issue.type === 'warning' ? 'bg-yellow-900/20 border-yellow-400/30' :
                        issue.type === 'security' ? 'bg-purple-900/20 border-purple-400/30' :
                        issue.type === 'complexity' ? 'bg-orange-900/20 border-orange-400/30' :
                        'bg-blue-900/20 border-blue-400/30'
                      } hover:bg-opacity-30 transition-colors`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="pt-1">
                          {issue.type === 'error' ? <FiAlertTriangle className="h-4 w-4 text-red-400" /> :
                           issue.type === 'warning' ? <FiAlertTriangle className="h-4 w-4 text-yellow-400" /> :
                           issue.type === 'security' ? <FiShield className="h-4 w-4 text-purple-400" /> :
                           issue.type === 'complexity' ? <FiCpu className="h-4 w-4 text-orange-400" /> :
                           <FiInfo className="h-4 w-4 text-blue-400" />}
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
                              {issue.type.charAt(0).toUpperCase() + issue.type.slice(1)}
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
                          {isExpanded && (
                            <div className="mt-3 space-y-3">
                              {isLoading ? (
                                <div className="flex items-center justify-center p-4 text-gray-400">
                                  <FiLoader className="animate-spin mr-2" />
                                  Generating explanation...
                                </div>
                              ) : hasExplanation ? (
                                <>
                                  <div className="bg-gray-800/70 p-3 rounded">
                                    <h4 className="font-medium text-blue-300 mb-1">Why this matters:</h4>
                                    <p className="text-sm text-gray-300">{issue.explanation?.why || 'No explanation available'}</p>
                                  </div>
                                  <div className="bg-gray-800/70 p-3 rounded">
                                    <h4 className="font-medium text-green-300 mb-1">How to fix:</h4>
                                    <pre className="text-sm text-gray-300 whitespace-pre-wrap">{issue.explanation?.fix}</pre>
                                  </div>
                                  {issue.explanation?.example && (
                                    <div className="bg-gray-800/70 p-3 rounded">
                                      <h4 className="font-medium text-yellow-300 mb-1">Example:</h4>
                                      <pre className="text-sm text-gray-300 whitespace-pre-wrap">{issue.explanation.example}</pre>
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
                                </>
                              ) : (
                                <div className="flex items-center p-3 bg-gray-800/50 text-yellow-400 rounded">
                                  <FiAlertCircle className="mr-2" />
                                  <span>Explanation unavailable</span>
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
                            <button
                              onClick={() => toggleExpand(issue)}
                              className="text-xs flex items-center gap-1 text-gray-400 hover:text-gray-200"
                              disabled={isLoading}
                            >
                              {isLoading ? (
                                <>
                                  <FiLoader className="animate-spin h-3 w-3" /> Loading...
                                </>
                              ) : isExpanded ? (
                                <>
                                  <FiChevronUp className="h-3 w-3" /> Hide details
                                </>
                              ) : (
                                <>
                                  <FiChevronDown className="h-3 w-3" /> Show explanation
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
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
        <CodeEditor 
          code={fileContent}
          issues={issuesWithExplanations.filter(i => i.file === activeFile)}
          onClose={() => setActiveFile(null)}
        />
      )}
    </div>
  );
};

export default AnalysisResults;