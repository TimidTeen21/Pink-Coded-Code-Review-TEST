// frontend/app/components/ExplanationFeedback.tsx
export function ExplanationFeedback({ issueCode, userId }: {
    issueCode: string;
    userId: string;
}) {
    const sendFeedback = async (wasHelpful: boolean) => {
        await fetch('/api/v1/feedback/explanation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                issue_code: issueCode,
                was_helpful: wasHelpful,
                complexity: "intermediate" // Adjust based on current explanation
            })
        });
    };

    return (
        <div className="flex gap-2 mt-3">
            <button 
                onClick={() => sendFeedback(true)}
                className="text-xs bg-green-500/20 px-3 py-1 rounded"
            >
                Helpful
            </button>
            <button
                onClick={() => sendFeedback(false)}
                className="text-xs bg-red-500/20 px-3 py-1 rounded"
            >
                Confusing
            </button>
        </div>
    );
}