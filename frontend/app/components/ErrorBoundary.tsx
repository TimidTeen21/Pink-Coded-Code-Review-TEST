import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
    state: State = { hasError: false, error: null };

    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("ErrorBoundary caught:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="p-4 bg-red-900/20 rounded-lg">
                    <h3 className="text-red-400">Editor Error</h3>
                    <p className="text-sm text-gray-300">
                        {this.state.error?.toString() || 'Something went wrong'}
                    </p>
                    <button
                        onClick={() => this.setState({ hasError: false, error: null })}
                        className="mt-2 text-sm bg-gray-700 px-3 py-1 rounded"
                    >
                        Try Again
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}
