// frontend/app/not-found.tsx
import { FiAlertTriangle } from 'react-icons/fi';
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-xl p-8 max-w-md w-full text-center">
        <div className="flex justify-center text-4xl text-yellow-400 mb-4">
          <FiAlertTriangle />
        </div>
        <h2 className="text-2xl font-bold text-pink-500 mb-2">404 - Page Not Found</h2>
        <p className="text-gray-300 mb-6">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          href="/"
          className="inline-block bg-pink-600 hover:bg-pink-700 text-white px-6 py-2 rounded-lg transition-colors"
        >
          Return Home
        </Link>
      </div>
    </div>
  );
}