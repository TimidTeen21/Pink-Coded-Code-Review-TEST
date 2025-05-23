// frontend/app/auth/login/page.tsx
'use client';
import LoginForm from 'app/Auth/components/LoginForm'; // Update import path to match folder casing

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-xl p-8 max-w-md w-full">
        <LoginForm onSuccess={(token) => {
          localStorage.setItem('token', token);
          window.location.href = '/dashboard';
        }} />
      </div>
    </div>
  );
}