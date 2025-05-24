// frontend/app/dashboard/components/UsageStatsCard.tsx
'use client';
import { FiTrendingUp, FiTrendingDown } from 'react-icons/fi';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Jan', issues: 400, projects: 5 },
  { name: 'Feb', issues: 300, projects: 8 },
  { name: 'Mar', issues: 500, projects: 10 },
  { name: 'Apr', issues: 278, projects: 7 },
  { name: 'May', issues: 189, projects: 4 },
  { name: 'Jun', issues: 239, projects: 6 },
  { name: 'Jul', issues: 349, projects: 9 },
];

export default function UsageStatsCard() {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold">Usage Statistics</h3>
        <div className="flex gap-4">
          <span className="text-sm text-green-400 flex items-center gap-1">
            <FiTrendingUp /> 12%
          </span>
          <span className="text-sm text-gray-400">Last 6 months</span>
        </div>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorIssues" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EC4899" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#EC4899" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorProjects" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                borderColor: '#4B5563',
                borderRadius: '0.5rem'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="issues" 
              stroke="#EC4899" 
              fillOpacity={1} 
              fill="url(#colorIssues)" 
            />
            <Area 
              type="monotone" 
              dataKey="projects" 
              stroke="#8B5CF6" 
              fillOpacity={1} 
              fill="url(#colorProjects)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      
      <div className="flex justify-between mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-pink-500"></div>
          <span className="text-gray-300">Issues Found</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-500"></div>
          <span className="text-gray-300">Projects Analyzed</span>
        </div>
      </div>
    </div>
  );
}