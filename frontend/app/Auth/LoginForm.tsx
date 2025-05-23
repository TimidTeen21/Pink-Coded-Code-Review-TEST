//frontend/app/auth/LoginForm.tsx
import { useState } from 'react'
import { FiMail, FiLock, FiLogIn } from 'react-icons/fi'

export default function LoginForm({ onSuccess }: { onSuccess: (token: string) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,
          password,
          grant_type: 'password'
        })
      })

      if (!response.ok) {
        throw new Error('Invalid credentials')
      }

      const { access_token } = await response.json()
      onSuccess(access_token)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-pink-500 mb-6 text-center">Welcome Back!</h2>
      
      {error && (
        <div className="bg-red-900/50 text-red-300 p-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div className="space-y-2">
        <label className="text-gray-300 text-sm">Email</label>
        <div className="relative">
          <FiMail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-gray-700 text-gray-200 rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-pink-500"
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-gray-300 text-sm">Password</label>
        <div className="relative">
          <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-gray-700 text-gray-200 rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-pink-500"
            required
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className={`w-full bg-pink-600 text-white py-2 rounded-lg flex items-center justify-center gap-2 ${
          loading ? 'opacity-70' : 'hover:bg-pink-700'
        }`}
      >
        {loading ? (
          <span className="animate-pulse">Logging in...</span>
        ) : (
          <>
            Log In <FiLogIn />
          </>
        )}
      </button>
    </form>
  )
}