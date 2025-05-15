import React, { useState, useEffect } from 'react';
import { 
  FiAlertTriangle, FiInfo, FiCheckCircle, FiShield, 
  FiCpu, FiFile, FiExternalLink, FiChevronDown, 
  FiChevronUp, FiThumbsUp, FiThumbsDown, FiEdit,
  FiLoader, FiAlertCircle, FiCheck, FiRotateCw, FiX, FiDownload
} from 'react-icons/fi';
import { MdAutoFixHigh } from 'react-icons/md';
import { Issue, AnalysisResult } from '@/types';
import { CodeEditor } from '@/components/CodeEditor/CodeEditor';

interface AnalysisResultsProps {
  result?: AnalysisResult;
  userId: string;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ result, userId }) => {
  const [expandedIssues, setExpandedIssues] = useState<Record<string, boolean>>({});
  const [feedbackStates, setFeedbackStates] = useState<Record<string, 'idle' | 'loading' | 'success' | 'error'>>({});
  const [lastFeedbackActions, setLastFeedbackActions] = useState<Record<string, 'helpful' | 'confusing'>>({});
  const [loadingExplanations, setLoadingExplanations] = useState<Record<string, boolean>>({});
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [issuesWithExplanations, setIssuesWithExplanations] = useState<Issue[]>([]);
  const [showFixPopup, setShowFixPopup] = useState<{ visible: boolean; fix?: string; explanation?: string; issue?: Issue }>({ 
    visible: false 
  });

  // Initialize with all issues
  useEffect(() => {
    if (result) {
      // Normalize all issues to include required fields
      const allIssues = [
        ...(result.main_analysis?.issues?.map(issue => ({
          ...issue,
          flamingo_message: issue.flamingo_message || `🦩 ${issue.message}`,
          url: issue.url || '',
          explanation: issue.explanation ?? undefined
        })) || []),
        ...(result.complexity_analysis?.issues?.map(issue => ({
          ...issue,
          flamingo_message: issue.flamingo_message || `🦩 Complexity: ${issue.message}`,
          url: issue.url || '',
          explanation: issue.explanation ?? undefined
        })) || []),
        ...(result.security_scan?.issues?.map(issue => ({
          ...issue,
          flamingo_message: issue.flamingo_message || `🦩 Security: ${issue.message}`,
          url: issue.url || '',
          explanation: issue.explanation ?? undefined
        })) || [])
      ];

      setIssuesWithExplanations(allIssues);
      
      const initialFeedbackStates = allIssues.reduce((acc, issue) => {
        const issueId = `${issue.file}-${issue.line}-${issue.code}`;
        acc[issueId] = 'idle';
        return acc;
      }, {} as Record<string, 'idle' | 'loading' | 'success' | 'error'>);
      
      setFeedbackStates(initialFeedbackStates);
    }
  }, [result]);

  const fetchFileContent = async (filePath: string) => {
    try {
      const params = new URLSearchParams({
        path: filePath,
        session_id: result?.session_id || '',
        ...(result?.temp_dir && { temp_dir: result.temp_dir })
      });

      const response = await fetch(
        `http://localhost:8000/api/v1/files?${params.toString()}`
      );
      
      if (!response.ok) throw new Error(await response.text());
      
      const { content } = await response.json();
      setFileContent(content);
      setActiveFile(filePath);
      
    } catch (error) {
      console.error('Failed to load file:', error);
      setFileContent(`# Error loading ${filePath}\n# ${error instanceof Error ? error.message : 'Unknown error'}`);
      setActiveFile(filePath);
    }
  };

  const toggleExpand = (issue: Issue) => {
    const issueId = `${issue.file}-${issue.line}-${issue.code}`;
    setExpandedIssues(prev => ({
      ...prev,
      [issueId]: !prev[issueId],
    }));

    if (!expandedIssues[issueId] && !issue.explanation) {
      fetchExplanation(issue);
    }
  };

  const fetchExplanation = async (issue: Issue) => {
    const issueId = `${issue.file}-${issue.line}-${issue.code}`;
    setLoadingExplanations(prev => ({ ...prev, [issueId]: true }));
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/explanations?issue_code=${issue.code}&message=${encodeURIComponent(issue.message)}&file=${encodeURIComponent(issue.file)}&line=${issue.line}&user_id=${userId}`
      );
      
      if (!response.ok) {
        throw new Error(await response.text());
      }
  
      const explanation = await response.json();
      
      setIssuesWithExplanations(prev => 
        prev.map(i => 
          i.file === issue.file && i.line === issue.line && i.code === issue.code 
            ? { ...i, explanation } 
            : i
        )
      );
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
    const issueCode = issueId.split('-').pop() || '';
    setFeedbackStates(prev => ({ ...prev, [issueId]: 'loading' }));
    setLastFeedbackActions(prev => ({ ...prev, [issueId]: isHelpful ? 'helpful' : 'confusing' }));
  
    try {
      const response = await fetch('http://localhost:8000/api/v1/feedback/explanation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          issue_code: issueCode,
          was_helpful: isHelpful,
          explanation_level: "intermediate"
        })
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Feedback submission failed');
      }
  
      setFeedbackStates(prev => ({ ...prev, [issueId]: 'success' }));
      setTimeout(() => setFeedbackStates(prev => ({ ...prev, [issueId]: 'idle' })), 3000);
    } catch (error) {
      console.error('Feedback error:', error);
      setFeedbackStates(prev => ({ ...prev, [issueId]: 'error' }));
    }
  };

  const handleRetryFeedback = (issueId: string) => {
    const action = lastFeedbackActions[issueId];
    if (action) {
      handleFeedback(issueId, action === 'helpful');
    }
  };

  const applyFix = async (issue: Issue, fix: string) => {
    if (!activeFile) return;
    
    try {
      const response: Response = await fetch('http://localhost:8000/api/v1/analysis/apply-fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: activeFile,
          issue,
          fix,
          session_id: result?.session_id,
          temp_dir: result?.temp_dir,
          user_id: userId
        })
      });
      
      const applyFixResult = await response.json();
      if (applyFixResult.success) {
        setFileContent(applyFixResult.new_content);
      }
    } catch (error) {
      console.error('Fix failed:', error);
    }
  };
  
  const handleCodeChange = async (newContent: string) => {
    if (!activeFile) return;
  
    try {
      const response = await fetch('http://localhost:8000/api/v1/analysis/analyze-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: newContent,
          file_path: activeFile,
          user_id: userId,
          session_id: result?.session_id,
          temp_dir: result?.temp_dir
        })
      });
  
      if (!response.ok) throw new Error(await response.text());
  
      const data = await response.json();
      const issues = [
        ...(data.main_analysis?.issues || []),
        ...(data.complexity_analysis?.issues || []),
        ...(data.security_scan?.issues || [])
      ];
      
      setIssuesWithExplanations(prev => [
        ...prev.filter(i => i.file !== activeFile.split('/').pop()),
        ...issues.map((issue: any) => ({
          ...issue,
          file: activeFile,
          flamingo_message: issue.flamingo_message || `🦩 ${issue.message}`,
          url: issue.url || ''
        }))
      ]);
      
      setFileContent(newContent);
  
    } catch (error) {
      console.error('Real-time analysis failed:', error);
    }
  };

  const handleShowFix = async (issue: Issue) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/analysis/generate-fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: fileContent,
          issue,
          user_id: userId
        })
      });
  
      if (!response.ok) throw new Error(await response.text());
      const { fix, explanation } = await response.json();
  
      setShowFixPopup({
        visible: true,
        fix,
        explanation,
        issue
      });
  
    } catch (error) {
      console.error('Fix failed:', error);
      alert(`Fix failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleViewFile = (filePath: string) => {
    fetchFileContent(filePath);
    
    setTimeout(() => {
      const editorElement = document.getElementById('code-editor-container');
      if (editorElement) {
        editorElement.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  const scrollToFirstIssue = () => {
    if (issuesWithExplanations.length > 0) {
      const firstIssue = issuesWithExplanations[0];
      fetchFileContent(firstIssue.file);
      
      setTimeout(() => {
        const editorElement = document.getElementById('code-editor-container');
        if (editorElement) {
          editorElement.scrollIntoView({ behavior: 'smooth' });
        }
        
        const lineElement = document.querySelector(`[data-line-number="${firstIssue.line}"]`);
        if (lineElement) {
          lineElement.classList.add('flash-highlight');
          setTimeout(() => lineElement.classList.remove('flash-highlight'), 2000);
        }
      }, 100);
    }
  };
  
  const handleExport = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/analysis/export-project', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: result?.session_id,
          temp_dir: result?.temp_dir
        })
      });
  
      if (!response.ok) throw new Error(await response.text());
  
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pink-coded-export-${result?.session_id?.slice(0, 8) || 'project'}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
  
    } catch (error) {
      console.error('Export failed:', error);
      alert(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Group issues by file
  const issuesByFile = issuesWithExplanations.reduce((acc, issue) => {
    const issueId = `${issue.file}-${issue.line}-${issue.code}`;
    if (!acc[issue.file]) acc[issue.file] = [];
    acc[issue.file].push({ ...issue, id: issueId });
    return acc;
  }, {} as Record<string, any[]>);

  if (!result) {
    return (
      <div className="p-4 bg-gray-800 rounded-lg text-center">
        <p className="text-gray-400">No analysis results available</p>
      </div>
    );
  }

  const hasError = !!result.main_analysis?.error;
  const hasIssues = issuesWithExplanations.length > 0;

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
                  onClick={() => handleViewFile(file)}
                  className="flex items-center gap-1 text-xs text-pink-400 hover:text-pink-300"
                >
                  <FiEdit className="h-3 w-3" />
                  Peck at the solutions
                </button>
              </div>
              
              <div className="space-y-3 mt-2">
                {fileIssues.map((issue) => {
                  const isLoading = loadingExplanations[issue.id];
                  const hasExplanation = !!issue.explanation;
                  const isExpanded = expandedIssues[issue.id];
                  const feedbackState = feedbackStates[issue.id] || 'idle';
                  
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

                                  {/* Feedback Section */}
                                  <div className="flex gap-2 mt-2">
                                    {feedbackState === 'idle' ? (
                                      <>
                                        <button 
                                          onClick={() => handleFeedback(issue.id, true)}
                                          className="text-xs flex items-center gap-1 bg-green-900/30 hover:bg-green-900/50 px-2 py-1 rounded text-green-300 transition-colors"
                                        >
                                          <FiThumbsUp className="h-3 w-3" /> Helpful
                                        </button>
                                        <button 
                                          onClick={() => handleFeedback(issue.id, false)}
                                          className="text-xs flex items-center gap-1 bg-red-900/30 hover:bg-red-900/50 px-2 py-1 rounded text-red-300 transition-colors"
                                        >
                                          <FiThumbsDown className="h-3 w-3" /> Confusing
                                        </button>
                                      </>
                                    ) : feedbackState === 'loading' ? (
                                      <span className="text-xs text-gray-400">Sending feedback...</span>
                                    ) : feedbackState === 'success' ? (
                                      <span className="text-xs flex items-center gap-1 text-green-500 animate-[fadeInOut_3s_ease-in-out]">
                                        <FiCheck className="h-4 w-4" /> Thanks for your feedback!
                                      </span>
                                    ) : feedbackState === 'error' ? (
                                      <div className="flex items-center gap-2">
                                        <span className="text-xs text-red-500">Failed to send</span>
                                        <button 
                                          onClick={() => handleRetryFeedback(issue.id)}
                                          className="text-xs flex items-center gap-1 bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded"
                                        >
                                          <FiRotateCw className="h-3 w-3" /> Retry
                                        </button>
                                      </div>
                                    ) : null}
                                  </div>
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
                              onClick={() => handleShowFix(issue)}
                              className="text-xs flex items-center gap-1 bg-blue-900/30 hover:bg-blue-900/50 px-2 py-1 rounded text-blue-300 transition-colors"
                            >
                              <MdAutoFixHigh className="h-3 w-3" />
                              Show Fix
                            </button>

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
      <div id="code-editor-container" className="relative h-full">
        {activeFile && (
          <CodeEditor
            code={fileContent}
            issues={issuesWithExplanations.filter(i => i.file === activeFile.split('/').pop())}
            activeFile={activeFile}
            onClose={() => setActiveFile(null)}
            onFix={applyFix}
            onContentChange={handleCodeChange}
          />
        )}

        {activeFile && (
          <div className="flex justify-between items-center p-2 bg-gray-800 border-t border-gray-700">
            <span className="text-sm text-gray-300">Editing: {activeFile}</span>
            <div className="flex gap-2">
              <button
                onClick={() => setActiveFile(null)}
                className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded"
              >
                Close
              </button>
              <button
                onClick={handleExport}
                className="px-3 py-1 text-sm bg-green-600 hover:bg-green-500 rounded flex items-center gap-1"
              >
                <FiDownload className="h-3 w-3" />
                Export Project
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Fix Popup */}
      {showFixPopup.visible && showFixPopup.issue && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 border border-pink-500 rounded-lg p-6 max-w-lg w-full">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-bold text-pink-400">
                Fix for {showFixPopup.issue.code}
              </h3>
              <button
                onClick={() => setShowFixPopup({ visible: false })}
                className="text-gray-400 hover:text-white"
              >
                <FiX className="h-5 w-5" />
              </button>
            </div>
            
            <div className="mb-4">
              <h4 className="font-medium text-gray-200 mb-1">Issue:</h4>
              <p className="text-gray-300">{showFixPopup.issue.message}</p>
            </div>
            
            {showFixPopup.explanation && (
              <div className="mb-4">
                <h4 className="font-medium text-blue-300 mb-1">Explanation:</h4>
                <p className="text-gray-300">{showFixPopup.explanation}</p>
              </div>
            )}
            
            {showFixPopup.fix && (
              <div className="mb-6">
                <h4 className="font-medium text-green-300 mb-1">Suggested Fix:</h4>
                <pre className="bg-gray-700 p-3 rounded text-sm text-gray-100 overflow-auto">
                  {showFixPopup.fix}
                </pre>
              </div>
            )}
            
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  if (showFixPopup.fix && showFixPopup.issue) {
                    applyFix(showFixPopup.issue, showFixPopup.fix);
                  }
                  setShowFixPopup({ visible: false });
                }}
                className="px-4 py-2 bg-pink-600 hover:bg-pink-700 rounded text-white"
              >
                Apply Fix
              </button>
              <button
                onClick={() => setShowFixPopup({ visible: false })}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;