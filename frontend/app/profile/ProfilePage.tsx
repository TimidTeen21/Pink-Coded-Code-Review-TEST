// frontend/app/profile/page.tsx
'use client'
import { useState, useEffect } from 'react'
import { FiUser, FiAward, FiSettings, FiLogOut, FiHelpCircle} from 'react-icons/fi'
import { useRouter } from 'next/navigation'

type UserProfile = {
  email: string
  username: string
  experience_level: string | null
  quiz_completed: boolean
  quiz_score?: number
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const router = useRouter()

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          router.push('/')
          return
        }

        const response = await fetch('http://localhost:8000/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (!response.ok) {
          throw new Error('Failed to fetch profile')
        }

        const data = await response.json()
        setProfile(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Profile load failed')
      } finally {
        setLoading(false)
      }
    }

    fetchProfile()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    router.push('/')
  }

  const updateExperienceLevel = async (level: string) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return

      const response = await fetch('http://localhost:8000/api/v1/profile/experience-level', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ level })
      })

      if (!response.ok) {
        throw new Error('Update failed')
      }

      setProfile(prev => prev ? { ...prev, experience_level: level } : null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-pink-500"></div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <p className="text-gray-300 mb-4">{error || 'Profile not found'}</p>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-pink-600 rounded-lg text-white"
          >
            Go Home
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12 px-4">
      <div className="max-w-2xl mx-auto bg-gray-800 rounded-xl overflow-hidden">
        <div className="bg-pink-500/10 p-6 border-b border-pink-500/20">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-pink-500/20 flex items-center justify-center">
              <FiUser className="text-pink-500 text-2xl" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-pink-400">{profile.username}</h1>
              <p className="text-gray-400">{profile.email}</p>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div className="bg-gray-700/50 p-4 rounded-lg">
            <h2 className="flex items-center gap-2 text-lg font-medium text-gray-200 mb-4">
              <FiAward className="text-pink-400" />
              Experience Level
            </h2>
            
            <div className="flex gap-2">
              {['beginner', 'intermediate', 'advanced'].map((level) => (
                <button
                  key={level}
                  onClick={() => updateExperienceLevel(level)}
                  className={`px-4 py-2 rounded-lg text-sm capitalize ${
                    profile.experience_level === level
                      ? 'bg-pink-600 text-white'
                      : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>

            {profile.quiz_completed && (
              <p className="text-sm text-gray-400 mt-3">
                Quiz score: {profile.quiz_score} (initial recommendation)
              </p>
            )}
          </div>

          {!profile.quiz_completed && (
            <div className="bg-blue-900/10 p-4 rounded-lg border border-blue-500/20">
              <h2 className="flex items-center gap-2 text-lg font-medium text-blue-300 mb-2">
                <FiHelpCircle />
                Complete Onboarding
              </h2>
              <p className="text-sm text-gray-400 mb-4">
                Take our quick quiz to help us calibrate your experience level.
              </p>
              <button
                onClick={() => router.push('/onboarding')}
                className="px-4 py-2 bg-blue-600 rounded-lg text-white text-sm"
              >
                Start Quiz
              </button>
            </div>
          )}

          <div className="pt-4 border-t border-gray-700">
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-gray-400 hover:text-red-400"
            >
              <FiLogOut />
              Log Out
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}