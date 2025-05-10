// frontend/app/components/CodeEditor/FixWidget.tsx
import { Issue } from '@/types';

interface FixWidgetProps {
  issue: Issue;
  onApplyFix: () => void;
  onClose: () => void;
}

export function FixWidget({ issue, onApplyFix, onClose }: FixWidgetProps) {
  return (
    <div className="absolute bg-gray-800 p-4 rounded shadow-lg z-10">
      <h3 className="font-bold mb-2">{issue.code}: {issue.message}</h3>
      <div className="flex gap-2">
        <button 
          onClick={onApplyFix}
          className="px-3 py-1 bg-green-600 rounded"
        >
          Apply Fix
        </button>
        <button
          onClick={onClose}
          className="px-3 py-1 bg-gray-600 rounded"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}