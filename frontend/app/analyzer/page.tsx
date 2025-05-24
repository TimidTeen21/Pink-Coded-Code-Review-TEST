// frontend/app/analyzer/page.tsx
import { useState, useRef, ChangeEvent, useEffect } from 'react'
import { FiUpload, FiCode, FiCheckCircle, FiFolder, FiFile, FiX, FiUser, FiAward,
FiLogIn, FiUserPlus, FiLoader } from 'react-icons/fi'
import { AnalysisResults } from '@/components'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { ExperienceLevel, AnalysisResult } from '@/types'
import { useRouter } from 'next/navigation'


export default function Analyzer() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState('')
  const [selectedZip, setSelectedZip] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel>('intermediate')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.name.endsWith('.zip')) {
        setSelectedZip(file)
        setError('')
      } else {
        setError('Please upload a .zip file only')
      }
    }
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.name.endsWith('.zip')) {
        setSelectedZip(file)
        setError('')
      } else {
        setError('Please upload a .zip file only')
      }
    }
  }

  const removeZip = () => {
    setSelectedZip(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  const handleZipUpload = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsAnalyzing(true);
  setError('');
  setResults(null);

  if (!selectedZip) {
    setError('Please select a ZIP file first');
    setIsAnalyzing(false);
    return;
  }

  const formData = new FormData();
  formData.append('zip_file', selectedZip);

  try {
    const response = await fetch('http://localhost:8000/api/v1/analysis/analyze-zip', {
      method: 'POST',
      body: formData
      // No auth headers needed now
    });

    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `Analysis failed with status: ${response.status}`);
    }

    console.log("Raw response:", response); // Add this
    const data = await response.json();
    console.log("Parsed data:", data); // Add this
    setResults(data);
    setSessionId(data.session_id);
  } catch (err) {
    console.error('Analysis error:', err);
    setError(err instanceof Error ? err.message : 'Upload failed');
  } finally {
    setIsAnalyzing(false);
  }
};
      const router = useRouter();



  
  return (
    <main className="min-h-screen bg-gradient-to-b from-dark-triangle to-gray-900">
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="text-center mb-12">
          <div className="w-24 h-24 mx-auto mb-6 relative">
            <div className="absolute inset-0 bg-dark-triangle clip-triangle"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <FiCode className="text-pink-flamingo text-4xl" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-pink-flamingo mb-2">Pink Coded</h1>
          <p className="text-gray-300">AI-powered code analysis for your projects</p>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl p-8 border border-pink-flamingo/20">
          <form onSubmit={handleZipUpload} className="space-y-6">
            {/* Experience Level Selector */}
            <div className="flex flex-col space-y-2">
              <label className="text-sm text-gray-300 flex items-center gap-2">
                <FiUser className="h-4 w-4" />
                Your Experience Level
              </label>
              <div className="flex gap-2">
                {(['beginner', 'intermediate', 'advanced'] as ExperienceLevel[]).map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setExperienceLevel(level)}
                    className={`px-3 py-1 text-sm rounded-full flex items-center gap-1 transition-colors ${
                      experienceLevel === level
                        ? 'bg-pink-flamingo text-dark-triangle'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <FiAward className="h-3 w-3" />
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* File Upload Area */}
            <div 
              className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                dragActive 
                  ? 'border-pink-flamingo bg-pink-flamingo/10' 
                  : 'border-gray-600 hover:border-pink-flamingo/50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="flex flex-col items-center justify-center gap-2">
                <FiUpload className="text-pink-flamingo text-2xl" />
                <p className="text-gray-300">
                  Drag & drop your project ZIP here or{' '}
                  <button
                    type="button"
                    onClick={triggerFileInput}
                    className="text-pink-flamingo hover:underline focus:outline-none"
                  >
                    browse files
                  </button>
                </p>
                <p className="text-xs text-gray-400">ZIP archives only (.zip)</p>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".zip"
                  className="hidden"
                />
              </div>
            </div>

            {selectedZip && (
              <div className="flex items-center justify-between bg-gray-700/50 p-3 rounded-lg">
                <span className="text-sm text-gray-300 truncate">
                  {selectedZip.name}
                </span>
                <button
                  type="button"
                  onClick={removeZip}
                  className="text-gray-400 hover:text-red-400 p-1"
                >
                  <FiX className="h-4 w-4" />
                </button>
              </div>
            )}

            {error && (
              <div className="text-red-400 p-3 bg-gray-900/50 rounded-lg">
                <p className="text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isAnalyzing || !selectedZip}
              className={`w-full px-6 py-3 bg-pink-flamingo text-dark-triangle font-medium rounded-lg transition-colors flex items-center justify-center gap-2 ${
                isAnalyzing || !selectedZip
                  ? 'opacity-50 cursor-not-allowed' 
                  : 'hover:bg-pink-flamingo/90'
              }`}
            >
              {isAnalyzing ? (
                <>
                  <span className="animate-pulse">Analyzing...</span>
                  <FiCheckCircle className="animate-spin" />
                </>
              ) : (
                <>
                  Analyze Project
                  <FiUpload />
                </>
              )}
            </button>
          </form>

          <div className="mt-8">
            {results && (
              <ErrorBoundary>
              <div className="animate-fade-in">
                <AnalysisResults result={results} userId="exampleUserId" />
              </div>
              </ErrorBoundary>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}