// frontend/app/components/CodeEditor/CodeEditor.tsx
import { useState } from 'react';
import Editor, { Monaco } from '@monaco-editor/react';
import type { Issue } from '@/types';

interface CodeEditorProps {
  code: string;
  issues: Issue[];
  onClose: () => void;
}

export function CodeEditor({ code, issues, onClose }: CodeEditorProps) {
  const [editor, setEditor] = useState<any>(null);
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);

  const handleEditorMount = (editor: any, monaco: Monaco) => {
    setEditor(editor);
    
    // Set error markers
    monaco.editor.setModelMarkers(
      editor.getModel(),
      "owner",
      issues.map(issue => ({
        startLineNumber: issue.line,
        startColumn: 1,
        endLineNumber: issue.line,
        endColumn: 100,
        message: `${issue.code}: ${issue.message}`,
        severity: monaco.MarkerSeverity.Error
      }))
    );
  };

  return (
    <div className="relative h-full">
      <div className="flex justify-between items-center bg-gray-700 p-2">
        <span className="text-sm font-mono">Editing: {selectedIssue?.file}</span>
        <button 
          onClick={onClose}
          className="text-gray-300 hover:text-white"
        >
          Close
        </button>
      </div>
      <Editor
        height="90vh"
        language="python"
        value={code}
        onMount={handleEditorMount}
        options={{
          minimap: { enabled: false },
          glyphMargin: true,
          lineNumbers: 'on',
        }}
      />
    </div>
  );
}