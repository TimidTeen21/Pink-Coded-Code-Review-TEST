// frontend/app/dashboard/page.tsx
'use client';
import { FiBarChart2 } from 'react-icons/fi';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="bg-gray-800 p-6 rounded-lg">
        <div className="flex items-center gap-2 text-pink-400">
          <FiBarChart2 />
          <span>Simplified Dashboard Loaded Successfully!</span>
        </div>
      </div>
    </div>
  );
}

/*import { FiUpload, FiBarChart2, FiSettings, FiHelpCircle, FiUser, FiAward, FiZap, FiCheck, FiAlertTriangle, FiStar, FiMessageSquare, FiGrid, FiList, FiShield } from 'react-icons/fi';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import StatsCard from './components/StatsCard';
import QuickActions from './components/QuickActions';
import RecentActivity from './components/RecentActivity';
import RulesQualityGates from './components/RulesQualityGates';
import FlamingoChat from './components/FlamingoChat';

/*export default function DashboardPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activeMainTab, setActiveMainTab] = useState('overview');
  const [userLevel, setUserLevel] = useState('Intermediate');
  const [flamingoPoints, setFlamingoPoints] = useState(420);
  const [isLoading, setIsLoading] = useState(true);
  
  // Handle user logout (placeholder)
  function handleLogout() {
    // TODO: Add logout logic here (e.g., clear auth, redirect, etc.)
    alert('Logged out!');
  }
  

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="animate-bounce text-4xl mb-4">🦩</div>
          <div className="text-pink-400">Loading your flamingo nest...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex">
      {/* Sidebar }
      <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col hidden md:flex">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold text-pink-500 flex items-center gap-2">
            <span className="relative">
              🦩
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-pink-500 rounded-full animate-pulse"></span>
            </span>
            Pink Coded
          </h1>
          <p className="text-xs text-gray-400 mt-1">AI-Powered Code Review</p>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${activeTab === 'dashboard' ? 'bg-pink-600/20 text-pink-400' : 'hover:bg-gray-700'}`}
          >
            <FiBarChart2 />
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('rules')}
            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${activeTab === 'rules' ? 'bg-pink-600/20 text-pink-400' : 'hover:bg-gray-700'}`}
          >
            <FiShield />
            Rules & Quality Gates
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${activeTab === 'chat' ? 'bg-pink-600/20 text-pink-400' : 'hover:bg-gray-700'}`}
          >
            <FiMessageSquare />
            AI Flamingo Chat
          </button>
          <button
            onClick={() => setActiveTab('profile')}
            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${activeTab === 'profile' ? 'bg-pink-600/20 text-pink-400' : 'hover:bg-gray-700'}`}
          >
            <FiUser />
            My Profile
          </button>
          <button
            onClick={() => setActiveTab('achievements')}
            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${activeTab === 'achievements' ? 'bg-pink-600/20 text-pink-400' : 'hover:bg-gray-700'}`}
          >
            <FiAward />
            Achievements
          </button>
        </nav>
        
        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center gap-3 mb-4 p-3 bg-gray-700/50 rounded-lg">
            <div className="w-10 h-10 rounded-full bg-pink-500 flex items-center justify-center text-white font-bold">
              {userLevel.charAt(0)}
            </div>
            <div>
              <p className="text-sm font-medium">Your Level</p>
              <p className="text-xs text-pink-400">{userLevel}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-700 transition-colors text-red-400"
          >
            <FiSettings />
            Log Out
          </button>
        </div>
      </div>
      
      {/* Mobile Header }
      <div className="md:hidden fixed top-0 left-0 right-0 bg-gray-800 z-10 p-4 flex justify-between items-center border-b border-gray-700">
        <h1 className="text-xl font-bold text-pink-500">🦩 Pink Coded</h1>
        <select 
          value={activeTab}
          onChange={(e) => setActiveTab(e.target.value)}
          className="bg-gray-700 text-white p-2 rounded-lg text-sm"
        >
          <option value="dashboard">Dashboard</option>
          <option value="rules">Rules & Gates</option>
          <option value="chat">AI Flamingo</option>
          <option value="profile">Profile</option>
          <option value="achievements">Achievements</option>
        </select>
      </div>
      
      {/* Main Content }
      <div className="flex-1 p-4 md:p-8 overflow-auto mt-16 md:mt-0">
        <div className="max-w-7xl mx-auto">
          {activeTab === 'dashboard' && (
            <>
              {/* Header }
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                  <h2 className="text-2xl md:text-3xl font-bold">Welcome Back!</h2>
                  <p className="text-gray-400">Here's what's happening with your code quality</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2 bg-gray-800 px-4 py-2 rounded-full">
                    <span className="text-pink-400">🦩</span>
                    <span className="font-medium">{flamingoPoints} Flamingo Points</span>
                  </div>
                </div>
              </div>
              
              {/* Stats Cards }
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <StatsCard 
                  title="Projects Analyzed" 
                  value="24" 
                  change="+3 this week" 
                  icon={<FiUpload className="text-pink-400" />}
                  trend="up"
                />
                <StatsCard 
                  title="Issues Resolved" 
                  value="89%" 
                  change="↑5% from last month" 
                  icon={<FiCheck className="text-green-400" />}
                  trend="up"
                />
                <StatsCard 
                  title="Quality Score" 
                  value="87/100" 
                  change="↑2 points" 
                  icon={<FiStar className="text-yellow-400" />}
                  trend="up"
                />
                <StatsCard 
                  title="Security Risks" 
                  value="3" 
                  change="↓1 from last week" 
                  icon={<FiAlertTriangle className="text-red-400" />}
                  trend="down"
                />
              </div>
              
              {/* Tabs }
              <div className="flex border-b border-gray-700 mb-6">
                <button
                  onClick={() => setActiveMainTab('overview')}
                  className={`px-4 py-2 font-medium text-sm ${activeMainTab === 'overview' ? 'text-pink-400 border-b-2 border-pink-500' : 'text-gray-400 hover:text-gray-200'}`}
                >
                  <FiGrid className="inline mr-2" />
                  Overview
                </button>
                <button
                  onClick={() => setActiveMainTab('activity')}
                  className={`px-4 py-2 font-medium text-sm ${activeMainTab === 'activity' ? 'text-pink-400 border-b-2 border-pink-500' : 'text-gray-400 hover:text-gray-200'}`}
                >
                  <FiList className="inline mr-2" />
                  Recent Activity
                </button>
              </div>
              
              {// Main Content Grid }
              {activeMainTab === 'overview' ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 space-y-6">
                    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                      <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold">Start New Analysis</h3>
                        <button className="text-sm text-pink-400 hover:underline">View History</button>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="border-2 border-dashed border-gray-600 rounded-xl p-8 text-center hover:border-pink-400 transition-colors cursor-pointer group">
                          <div className="flex flex-col items-center justify-center">
                            <div className="relative mb-3">
                              <FiUpload className="text-3xl text-pink-500 group-hover:scale-110 transition-transform" />
                              <div className="absolute -inset-2 bg-pink-500/10 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            </div>
                            <p className="font-medium">Drag & Drop your Python project</p>
                            <p className="text-sm text-gray-400 mt-1">or click to browse files</p>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <button 
                            className="bg-gray-700 hover:bg-gray-600 p-4 rounded-lg transition-colors text-left group"
                            onClick={() => router.push('/analyzer')}
                          >
                            <div className="flex items-center gap-3">
                              <div className="p-2 bg-pink-500/20 rounded-lg text-pink-400 group-hover:bg-pink-500/30 transition-colors">
                                <FiZap />
                              </div>
                              <div>
                                <p className="font-medium">Quick Analysis</p>
                                <p className="text-xs text-gray-400">Single file review</p>
                              </div>
                            </div>
                          </button>
                          <button className="bg-gray-700 hover:bg-gray-600 p-4 rounded-lg transition-colors text-left">
                            <div className="flex items-center gap-3">
                              <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                                <FiHelpCircle />
                              </div>
                              <div>
                                <p className="font-medium">Tutorial</p>
                                <p className="text-xs text-gray-400">Learn best practices</p>
                              </div>
                            </div>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-6">
                    <QuickActions />
                    <div className="bg-gradient-to-br from-pink-900/50 to-purple-900/50 p-6 rounded-xl border border-pink-800/50">
                      <div className="flex items-center gap-3 mb-4">
                        <span className="text-2xl">🦩</span>
                        <h3 className="text-lg font-bold">Flamingo Tip</h3>
                      </div>
                      <p className="text-sm text-gray-300 mb-4">
                        Consistent docstrings improve code maintainability. Try using Google or NumPy style docstrings for better readability.
                      </p>
                      <button className="text-sm text-pink-400 hover:underline flex items-center gap-1">
                        Learn more <span>→</span>
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <RecentActivity />
              )}
            </>
          )}

          {activeTab === 'rules' && (
            <RulesQualityGates />
          )}

          {activeTab === 'chat' && (
            <FlamingoChat />
          )}

          {activeTab === 'profile' && (
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h2 className="text-2xl font-bold mb-6">Profile Settings</h2>
              <p className="text-gray-400">Coming soon...</p>
            </div>
          )}

          {activeTab === 'achievements' && (
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h2 className="text-2xl font-bold mb-6">Your Achievements</h2>
              <p className="text-gray-400">Coming soon...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} */