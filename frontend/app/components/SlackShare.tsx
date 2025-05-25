// frontend/app/components/SlackShare.tsx
'use client';
import { useState } from 'react';
import { FiSlack, FiExternalLink, FiAlertCircle } from 'react-icons/fi';

interface SlackShareProps {
  codeSnippet?: string;
  analysisResult?: string;
  className?: string;
}

export default function SlackShare({ codeSnippet, analysisResult, className }: SlackShareProps) {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [error, setError] = useState<string | null>(null);

const handleSendToSlack = async () => {
  if (!message.trim()) return;

  setIsSending(true);
  setError(null);
  try {
    const response = await fetch('/api/slack', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: `${message}\n\n${codeSnippet ? '```' + codeSnippet + '```' : ''}\n${analysisResult ? 'Analysis: ' + analysisResult : ''}`,
      }),
    });

    const data = await response.json();
    console.log('Raw response:', response);
    console.log('Parsed data:', data);

    if (!response.ok) {
      throw new Error(data.error || 'Failed to send message');
    }

    setIsSuccess(true);
    setTimeout(() => setIsSuccess(false), 3000);
    setMessage('');
  } catch (err) {
    console.error('Slack share error:', err);
    setError(err instanceof Error ? err.message : 'An unknown error occurred');
  } finally {
    setIsSending(false);
  }
};
  return (
    <div className={`bg-gray-800 rounded-xl border border-gray-700 overflow-hidden ${className}`}>
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-700/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-pink-500/20 rounded-lg text-pink-400">
            <FiSlack className="text-lg" />
          </div>
          <div>
            <h3 className="font-medium">Share with Team</h3>
            <p className="text-xs text-gray-400">Discuss this analysis in Slack</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <a 
            href="https://slack.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-pink-400 transition-colors p-1"
            onClick={(e) => e.stopPropagation()}
          >
            <FiExternalLink className="text-sm" />
          </a>
          <div className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 9l6 6 6-6" />
            </svg>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="p-4 border-t border-gray-700 space-y-4">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Add your comments about this code..."
            className="w-full bg-gray-700 text-gray-100 p-3 rounded-lg text-sm focus:ring-2 focus:ring-pink-500/50 focus:border-pink-500/50 border border-gray-600 transition-all"
            rows={3}
          />
          
          <div className="flex justify-between items-center">
            <a 
              href="https://slack.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-sm text-pink-400 hover:text-pink-300 hover:underline flex items-center gap-1 transition-colors"
            >
              Open Slack <FiExternalLink className="text-xs" />
            </a>
            
            <button
              onClick={handleSendToSlack}
              disabled={isSending || !message.trim()}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all 
                ${isSending ? 'bg-pink-700' : 
                  isSuccess ? 'bg-green-600' : 
                  'bg-pink-600 hover:bg-pink-500 shadow-md hover:shadow-pink-500/20'}
                ${!message.trim() ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isSending ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Sending...
                </>
              ) : isSuccess ? (
                '✓ Sent to Slack!'
              ) : (
                <>
                  <FiSlack /> Share Now
                </>
              )}
            </button>
            {error && (
  <div className="text-red-400 text-sm mt-2 flex items-center gap-2">
    <FiAlertCircle />
    {error}
  </div>
)}
          </div>
        </div>
      )}
    </div>
  );
};
