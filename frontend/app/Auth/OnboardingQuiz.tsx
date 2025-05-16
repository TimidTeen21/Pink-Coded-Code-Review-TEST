// frontend/app/components/Auth/OnboardingQuiz.tsx
import { useState } from 'react'
import { FiAward, FiCheck, FiX, FiHelpCircle } from 'react-icons/fi'

type Question = {
  id: number
  code: string
  question: string
  options: string[]
  correctAnswer: number
  explanation: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
}

const questions: Question[] = [
  {
    id: 1,
    code: `def greet(name):
    return f"Hello, {name}!"`,
    question: "What's wrong with this function?",
    options: [
      "Nothing - it's perfectly fine",
      "Missing type hints",
      "Should use string concatenation instead of f-strings",
      "Missing docstring"
    ],
    correctAnswer: 3,
    explanation: "While the function works, Python best practices recommend including docstrings to explain the function's purpose.",
    difficulty: 'beginner'
  },
  {
    id: 2,
    code: `numbers = [1, 2, 3, 4, 5]
squared = map(lambda x: x**2, numbers)`,
    question: "How would you improve this code?",
    options: [
      "Use a list comprehension instead",
      "Keep it as is - it's optimal",
      "Use a for loop instead",
      "Add type hints"
    ],
    correctAnswer: 0,
    explanation: "List comprehensions are generally more readable than map+lambda for simple transformations in Python.",
    difficulty: 'intermediate'
  },
  // Add more questions...
]

export default function OnboardingQuiz({ onComplete }: { onComplete: () => void }) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)
  const [showExplanation, setShowExplanation] = useState(false)
  const [score, setScore] = useState(0)
  const [quizComplete, setQuizComplete] = useState(false)

  const handleAnswerSelect = (index: number) => {
    setSelectedAnswer(index)
    
    // Check if answer is correct
    if (index === questions[currentQuestion].correctAnswer) {
      setScore(prev => prev + 1)
    }
    
    // Show explanation
    setShowExplanation(true)
  }

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1)
      setSelectedAnswer(null)
      setShowExplanation(false)
    } else {
      // Quiz complete
      setQuizComplete(true)
      
      // Calculate experience level based on score
      const percentage = (score / questions.length) * 100
      let level = 'intermediate'
      if (percentage < 40) level = 'beginner'
      if (percentage > 75) level = 'advanced'
      
      // Save quiz results to backend
      const token = localStorage.getItem('token')
      if (token) {
        fetch('http://localhost:8000/api/v1/profile/quiz', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            score,
            level
          })
        })
      }
    }
  }

  const getExperienceLevel = () => {
    const percentage = (score / questions.length) * 100
    if (percentage < 40) return 'Beginner'
    if (percentage > 75) return 'Advanced'
    return 'Intermediate'
  }

  if (quizComplete) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-gray-800 rounded-xl p-8 max-w-md w-full text-center">
          <div className="w-20 h-20 bg-pink-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <FiAward className="text-pink-500 text-3xl" />
          </div>
          <h2 className="text-2xl font-bold text-pink-500 mb-2">Quiz Complete!</h2>
          <p className="text-gray-300 mb-6">
            You scored {score} out of {questions.length}
          </p>
          
          <div className="bg-gray-700/50 p-4 rounded-lg mb-6">
            <p className="text-sm text-gray-400">Your recommended level:</p>
            <p className="text-xl font-bold text-pink-400">{getExperienceLevel()}</p>
          </div>
          
          <p className="text-gray-400 text-sm mb-6">
            Don't worry - you can change this anytime in your profile settings.
          </p>
          
          <button
            onClick={onComplete}
            className="w-full bg-pink-600 text-white py-2 rounded-lg hover:bg-pink-700 transition-colors"
          >
            Continue to Pink Coded
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-xl p-8 max-w-2xl w-full">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-pink-500">
            Flamingo Onboarding Quiz 🦩
          </h2>
          <div className="text-sm text-gray-400">
            Question {currentQuestion + 1} of {questions.length}
          </div>
        </div>
        
        <div className="mb-6">
          <div className="bg-gray-700 p-4 rounded-lg mb-4">
            <pre className="text-sm text-gray-200 overflow-x-auto">
              {questions[currentQuestion].code}
            </pre>
          </div>
          <p className="text-gray-200">
            {questions[currentQuestion].question}
          </p>
        </div>
        
        <div className="space-y-3 mb-6">
          {questions[currentQuestion].options.map((option, index) => (
            <button
              key={index}
              onClick={() => !showExplanation && handleAnswerSelect(index)}
              disabled={showExplanation}
              className={`w-full text-left p-3 rounded-lg transition-colors ${
                selectedAnswer === index
                  ? index === questions[currentQuestion].correctAnswer
                    ? 'bg-green-900/50 text-green-300'
                    : 'bg-red-900/50 text-red-300'
                  : showExplanation && index === questions[currentQuestion].correctAnswer
                    ? 'bg-green-900/30 text-green-300'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
              }`}
            >
              <div className="flex items-center gap-3">
                {selectedAnswer === index ? (
                  index === questions[currentQuestion].correctAnswer ? (
                    <FiCheck className="flex-shrink-0" />
                  ) : (
                    <FiX className="flex-shrink-0" />
                  )
                ) : (
                  <span className="w-5 h-5 rounded-full border border-gray-500 flex-shrink-0"></span>
                )}
                {option}
              </div>
            </button>
          ))}
        </div>
        
        {showExplanation && (
          <div className="bg-gray-700/50 p-4 rounded-lg mb-6">
            <div className="flex items-center gap-2 text-pink-400 mb-2">
              <FiHelpCircle />
              <span className="font-medium">Flamingo Explains:</span>
            </div>
            <p className="text-gray-300 text-sm">
              {questions[currentQuestion].explanation}
            </p>
          </div>
        )}
        
        <button
          onClick={handleNextQuestion}
          disabled={!showExplanation}
          className={`w-full bg-pink-600 text-white py-2 rounded-lg ${
            !showExplanation ? 'opacity-50 cursor-not-allowed' : 'hover:bg-pink-700'
          }`}
        >
          {currentQuestion < questions.length - 1 ? 'Next Question' : 'See Results'}
        </button>
      </div>
    </div>
  )
}