// frontend/app/dashboard/components/AnalysisTester.tsx
'use client';
import { useState } from 'react';

interface TestIssue {
  type: string;
  file: string;
  line: number;
  message: string;
  code: string;
  flamingo_message: string;
}

interface TestAnalysisResult {
  project_type: string;
  experience_level: string;
  result: {
    main_analysis: {
      issues: TestIssue[];
      success: boolean;
    };
    complexity_analysis: {
      issues: TestIssue[];
      success: boolean;
    };
    security_scan: {
      issues: TestIssue[];
      success: boolean;
    };
  };
  session_id: string;
  temp_dir: string;
}

export default function AnalysisTester() {
  const [testResult, setTestResult] = useState<TestAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const runTest = () => {
    setLoading(true);
    setError('');
    setTestResult(null);

    try {
      // Simulate API call with timeout
      setTimeout(() => {
        const mockResponse: TestAnalysisResult = {
          project_type: "web",
          experience_level: "intermediate",
          result: {
            main_analysis: {
              issues: [
                {
                  type: "error",
                  file: "test.py",
                  line: 1,
                  message: "Test error message",
                  code: "T001",
                  flamingo_message: "[Test] This is a test error"
                },
                {
                  type: "warning",
                  file: "test.py",
                  line: 5,
                  message: "Test warning message",
                  code: "T002",
                  flamingo_message: "[Test] This is a test warning"
                }
              ],
              success: true
            },
            complexity_analysis: {
              issues: [],
              success: true
            },
            security_scan: {
              issues: [],
              success: true
            }
          },
          session_id: "test-session-123",
          temp_dir: "/tmp/test"
        };
        setTestResult(mockResponse);
        setLoading(false);
      }, 1000);
    } catch (err) {
      setError('Test failed');
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg border border-pink-500 max-w-md mx-auto">
      <h2 className="text-xl font-bold text-pink-400 mb-4">Analysis Pipeline Tester</h2>
      
      <button 
        onClick={runTest}
        disabled={loading}
        className={`mb-4 px-4 py-2 rounded ${
          loading ? 'bg-gray-600 cursor-not-allowed' : 'bg-pink-600 hover:bg-pink-700'
        }`}
      >
        {loading ? 'Running Test...' : 'Run Diagnostic Test'}
      </button>

      {error && (
        <div className="p-4 mb-4 bg-red-900/20 border border-red-400 rounded">
          <h3 className="font-bold text-red-400">Error</h3>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {testResult && (
        <div className="space-y-4">
          <div className="p-4 bg-gray-700 rounded">
            <h3 className="font-medium mb-2">Test Results</h3>
            <div className="space-y-2">
              <p><span className="font-semibold">Project Type:</span> {testResult.project_type}</p>
              <p><span className="font-semibold">Issues Found:</span> {testResult.result.main_analysis.issues.length}</p>
              <p><span className="font-semibold">Session ID:</span> {testResult.session_id}</p>
            </div>
          </div>

          <div className="p-4 bg-gray-700 rounded">
            <h3 className="font-medium mb-2">Sample Issue</h3>
            <pre className="text-xs bg-gray-800 p-2 rounded overflow-auto">
              {JSON.stringify(testResult.result.main_analysis.issues[0], null, 2)}
            </pre>
          </div>
        </div>
      )}

      {!testResult && !loading && !error && (
        <div className="text-gray-400 text-sm">
          Click the button to run a diagnostic test
        </div>
      )}
    </div>
  );
}