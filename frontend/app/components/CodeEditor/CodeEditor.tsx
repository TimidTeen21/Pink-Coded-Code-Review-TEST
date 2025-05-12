import { useEffect, useRef, useState } from 'react';
import Editor, { Monaco, useMonaco } from '@monaco-editor/react';
import type { Issue } from '@/types';
import { FiWind, FiX, FiCheck, FiCopy } from 'react-icons/fi';

interface CodeEditorProps {
  code: string;
  issues: Issue[];
  activeFile: string;
  onClose: () => void;
  onFix: (issue: Issue, fix: string) => void;
  onContentChange: (newContent: string) => void;
}

export function CodeEditor({ 
  code, 
  issues, 
  activeFile, 
  onClose, 
  onFix, 
  onContentChange 
}: CodeEditorProps) {
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<Monaco | null>(null);
  const decorationsRef = useRef<string[]>([]);
  const [hoveredIssue, setHoveredIssue] = useState<Issue | null>(null);
  const [showFixPopup, setShowFixPopup] = useState(false);
  const [fixPosition, setFixPosition] = useState({ x: 0, y: 0 });

  const handleEditorMount = (editor: any, monaco: Monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    
    // Set up hover provider
    monaco.languages.registerHoverProvider('python', {
      provideHover: (model, position) => {
        const lineNumber = position.lineNumber;
        const issue = issues.find(i => i.line === lineNumber);
        
        if (!issue) return null;
        
        return {
          contents: [
            {
              value: `**${issue.code}** - ${issue.type.toUpperCase()}`,
            },
            {
              value: issue.message,
            },
            {
              value: `[🦩 Show Fix](#fix-${issue.code})`,
            }
          ]
        };
      }
    });

    // Handle click on hover links
    editor.onMouseDown(async (e: any) => {
      if (e.target.type === 6 && e.target.element?.tagName === 'A') {
        const match = e.target.element.href.match(/#fix-(.+)$/);
        if (match) {
          const issueCode = match[1];
          const issue = issues.find(i => i.code === issueCode);
          if (issue) {
            showFixAtPosition(issue, e.event.posx, e.event.posy);
          }
        }
      }
    });

    // Track mouse moves for popup positioning
    editor.onMouseMove((e: any) => {
      if (e.target.position) {
        const issue = issues.find(i => i.line === e.target.position.lineNumber);
        setHoveredIssue(issue || null);
      }
    });

    // Set initial error markers
    updateDecorations();
    
    // Real-time validation
    editor.onDidChangeModelContent(() => {
      const currentCode = editor.getValue();
      onContentChange(currentCode);
    });
  };

  const showFixAtPosition = (issue: Issue, x: number, y: number) => {
    setFixPosition({ x, y });
    setShowFixPopup(true);
  };

  const applyFixAndClose = (issue: Issue) => {
    if (issue.explanation?.fix) {
      onFix(issue, issue.explanation.fix);
    }
    setShowFixPopup(false);
  };

  const updateDecorations = () => {
    if (!monacoRef.current || !editorRef.current) return;
    
    const monaco = monacoRef.current;
    const model = editorRef.current.getModel();
    
    // Clear old decorations
    decorationsRef.current = editorRef.current.deltaDecorations(
      decorationsRef.current,
      []
    );
    
    // Add new decorations
    decorationsRef.current = editorRef.current.deltaDecorations(
      decorationsRef.current,
      issues.map(issue => ({
        range: new monaco.Range(issue.line, 1, issue.line, 100),
        options: {
          className: `squiggly-${issue.type}`,
          glyphMarginClassName: `glyph-${issue.type}`,
          hoverMessage: {
            value: [
              `**${issue.code}**: ${issue.message}`,
              issue.explanation?.why ? `\n\n**Why**: ${issue.explanation.why}` : '',
              `\n\n[🦩 Show Fix](#fix-${issue.code})`
            ].join(''),
            isTrusted: true
          },
          minimap: {
            position: monaco.editor.MinimapPosition.Gutter,
            color: 
              issue.type === 'error' ? '#ff4d4f' :
              issue.type === 'warning' ? '#faad14' :
              issue.type === 'security' ? '#9254de' :
              '#13c2c2'
          },
          stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
        }
      }))
    );
  };

  // Register quick fixes
  useEffect(() => {
    if (!monacoRef.current) return;

    const monaco = monacoRef.current;
    monaco.languages.registerCodeActionProvider('python', {
      provideCodeActions: (model, range, context, token) => {
        const lineNumber = range.startLineNumber;
        const issue = issues.find(i => i.line === lineNumber);
        
        if (!issue) return {
          actions: [],
          dispose: () => {}
        };

        return {
          actions: [{
            title: `🦩 Fix: ${issue.message}`,
            id: 'flamingo-fix',
            kind: 'quickfix',
            command: {
              id: 'flamingo-fix-command',
              title: `🦩 Fix: ${issue.message}`,
              arguments: [issue, issue.explanation?.fix]
            }
          }],
          dispose: () => {}
        };
      }
    });

    // Add custom commands
    editorRef.current?.addAction({
      id: 'flamingo-fix-command',
      label: 'Apply Flamingo Fix',
      run: (editor: any, ...args: any[]) => {
        const [issue, fix] = args;
        if (issue && fix) {
          onFix(issue, fix);
        }
      }
    });
  }, [issues]);

  // Update decorations when issues change
  useEffect(() => {
    updateDecorations();
  }, [issues]);

  // Handle clicks outside the popup
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (showFixPopup && !(e.target as Element).closest('.fix-popup')) {
        setShowFixPopup(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showFixPopup]);

  return (
    <div className="relative h-full">
      <div className="flex justify-between items-center bg-gray-700 p-2">
        <span className="text-sm font-mono">Editing: {activeFile}</span>
        <button onClick={onClose} className="text-gray-300 hover:text-white">
          <FiX className="h-4 w-4" />
        </button>
      </div>
      
      <Editor
        height="90vh"
        language="python"
        value={code}
        onMount={handleEditorMount}
        options={{
          minimap: { enabled: true },
          glyphMargin: true,
          lineNumbers: 'on',
          lightbulb: { enabled: true },
          quickSuggestions: true,
          suggestOnTriggerCharacters: true,
          hover: {
            enabled: true,
            delay: 100,
            sticky: true
          },
          contextmenu: true
        }}
      />

      {/* Fix Popup */}
      {showFixPopup && hoveredIssue && (
        <div 
          className="fix-popup absolute z-50 bg-gray-800 border border-pink-500 rounded-lg shadow-lg p-3"
          style={{
            left: `${fixPosition.x}px`,
            top: `${fixPosition.y}px`,
            maxWidth: '400px'
          }}
        >
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-bold text-pink-400">{hoveredIssue.code}</h4>
            <button 
              onClick={() => setShowFixPopup(false)}
              className="text-gray-400 hover:text-white"
            >
              <FiX className="h-4 w-4" />
            </button>
          </div>
          <p className="text-sm text-gray-200 mb-3">{hoveredIssue.message}</p>
          
          {hoveredIssue.explanation?.fix ? (
            <>
              <div className="bg-gray-700/50 p-2 rounded mb-3">
                <pre className="text-xs text-gray-100 whitespace-pre-wrap">
                  {hoveredIssue.explanation.fix}
                </pre>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => applyFixAndClose(hoveredIssue)}
                  className="flex items-center gap-1 text-xs bg-pink-600 hover:bg-pink-700 text-white px-3 py-1 rounded"
                >
                  <FiCheck className="h-3 w-3" /> Apply Fix
                </button>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(hoveredIssue.explanation?.fix || '');
                    setShowFixPopup(false);
                  }}
                  className="flex items-center gap-1 text-xs bg-gray-600 hover:bg-gray-500 text-white px-3 py-1 rounded"
                >
                  <FiCopy className="h-3 w-3" /> Copy Fix
                </button>
              </div>
            </>
          ) : (
            <p className="text-sm text-yellow-400">No fix available for this issue</p>
          )}
        </div>
      )}

      {/* Hover indicator */}
      {hoveredIssue && !showFixPopup && (
        <div 
          className="absolute z-40 pointer-events-none bg-pink-500/10 border-l-2 border-pink-500"
          style={{
            left: '0',
            top: `${(hoveredIssue.line - 1) * 19}px`,
            height: '19px',
            width: '100%'
          }}
        />
      )}
    </div>
  );
}