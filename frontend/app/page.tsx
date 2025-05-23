//frontend/app/page.tsx
'use client'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
// import {LoadingThreeDotsJumping} from '@/components/animations/ThreeDotLoader'
import LoadingThreeDotsJumping from '@/animations/ThreeDotLoader'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Check auth status and redirect
    const token = localStorage.getItem('token')
    if (token) {
      router.push('/analyzer')
    } else {
      router.push('/auth/login')
    }
  }, [router])

  return <LoadingThreeDotsJumping />
}

/*import { useState, useRef, ChangeEvent, useEffect } from 'react'
import { FiUpload, FiCode, FiCheckCircle, FiFolder, FiFile, FiX, FiUser, FiAward,
FiLogIn, FiUserPlus, FiLoader } from 'react-icons/fi'
import { AnalysisResults } from '@/components'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { ExperienceLevel, AnalysisResult } from '@/types'
import { useRouter } from 'next/navigation'
import LoginForm from '@/components/Auth/LoginForm'
import SignupForm from '@/components/Auth/SignupForm'
import OnboardingQuiz from '@/components/Auth/OnboardingQuiz'
import Analyzer from './analyzer/AnalyzerPage'*/

/*export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showLogin, setShowLogin] = useState(true)
  const [showQuiz, setShowQuiz] = useState(false)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('token')
    if (token) {
      verifyToken(token)
    } else {
      setLoading(false)
    }
  }, [])

  const verifyToken = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const user = await response.json()
        setIsAuthenticated(true)
        
        // Check if user needs to complete onboarding
        if (!user.quiz_completed) {
          setShowQuiz(true)
        } else {
          router.push('/analyzer')
        }
      }
    } catch (error) {
      localStorage.removeItem('token')
    } finally {
      setLoading(false)
    }
  }

  const handleLoginSuccess = (token: string) => {
    localStorage.setItem('token', token)
    verifyToken(token)
  }

  const handleQuizComplete = () => {
    setShowQuiz(false)
    router.push('/analyzer')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <FiLoader className="animate-spin text-pink-500 text-4xl" />
      </div>
    )
  }

  if (isAuthenticated && showQuiz) {
    return <OnboardingQuiz onComplete={handleQuizComplete} />
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-gray-800 rounded-xl p-8 max-w-md w-full">
          {showLogin ? (
            <>
              <LoginForm onSuccess={handleLoginSuccess} />
              <p className="text-center text-gray-400 mt-4">
                Don't have an account?{' '}
                <button 
                  onClick={() => setShowLogin(false)}
                  className="text-pink-500 hover:underline"
                >
                  Sign up
                </button>
              </p>
            </>
          ) : (
            <>
              <SignupForm onSuccess={handleLoginSuccess} />
              <p className="text-center text-gray-400 mt-4">
                Already have an account?{' '}
                <button 
                  onClick={() => setShowLogin(true)}
                  className="text-pink-500 hover:underline"
                >
                  Log in
                </button>
              </p>
            </>
          )}
        </div>
      </div>
    )
  }

  // Render Analyzer if authenticated and quiz is not needed
  if (isAuthenticated && !showQuiz) {
    return <Analyzer />
  }

  return null
} */