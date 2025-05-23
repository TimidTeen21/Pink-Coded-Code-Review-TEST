// frontend/app/auth/signup/page.tsx
'use client';
import SignupForm from '../components/SignupForm';

export default function SignupPage() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-xl p-8 max-w-md w-full">
        <SignupForm onSuccess={(token) => {
          localStorage.setItem('token', token);
          window.location.href = '/dashboard';
        }} />
      </div>
    </div>
  );
}