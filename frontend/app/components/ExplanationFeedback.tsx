// frontend/app/components/ExplanationFeedback.tsx
import { useState } from 'react';
import { FiThumbsUp, FiThumbsDown, FiCheck, FiX, FiRotateCw } from 'react-icons/fi';

export function ExplanationFeedback({ issueCode, userId }: {
    issueCode: string;
    userId: string;
}) {
    const [feedbackState, setFeedbackState] = useState<
        'idle' | 'loading' | 'success' | 'error' | 'retry'
    >('idle');
    const [lastAction, setLastAction] = useState<'helpful' | 'confusing' | null>(null);

    const sendFeedback = async (wasHelpful: boolean) => {
        setLastAction(wasHelpful ? 'helpful' : 'confusing');
        setFeedbackState('loading');
        
        try {
            const response = await fetch('/api/v1/feedback/explanation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    issue_code: issueCode,
                    was_helpful: wasHelpful,
                    explanation_level: "intermediate"
                })
            });

            if (!response.ok) {
                throw new Error('Feedback submission failed');
            }

            setFeedbackState('success');
            // Reset after 2 seconds
            setTimeout(() => setFeedbackState('idle'), 2000);
        } catch (error) {
            console.error('Feedback error:', error);
            setFeedbackState('error');
        }
    };

    const handleRetry = () => {
        if (lastAction) {
            sendFeedback(lastAction === 'helpful');
        }
    };

    return (
        <div className="flex gap-2 mt-3 items-center">
            {feedbackState === 'idle' ? (
                <>
                    <button 
                        onClick={() => sendFeedback(true)}
                        className="text-xs flex items-center gap-1 bg-green-500/20 hover:bg-green-500/30 px-3 py-1 rounded transition-colors"
                    >
                        <FiThumbsUp className="h-3 w-3" /> Helpful
                    </button>
                    <button
                        onClick={() => sendFeedback(false)}
                        className="text-xs flex items-center gap-1 bg-red-500/20 hover:bg-red-500/30 px-3 py-1 rounded transition-colors"
                    >
                        <FiThumbsDown className="h-3 w-3" /> Confusing
                    </button>
                </>
            ) : feedbackState === 'loading' ? (
                <span className="text-xs text-gray-400">Sending...</span>
            ) : feedbackState === 'success' ? (
                <span className="text-xs flex items-center gap-1 text-green-500">
                    <FiCheck className="h-4 w-4" /> Thanks!
                </span>
            ) : feedbackState === 'error' ? (
                <div className="flex items-center gap-2">
                    <span className="text-xs text-red-500">Failed to send</span>
                    <button 
                        onClick={handleRetry}
                        className="text-xs flex items-center gap-1 bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded"
                    >
                        <FiRotateCw className="h-3 w-3" /> Retry
                    </button>
                </div>
            ) : null}
        </div>
    );
}