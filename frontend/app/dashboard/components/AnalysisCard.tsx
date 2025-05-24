// frontend/app/dashboard/components/AnalysisCard.tsx
import { FiBarChart2 } from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Jan', issues: 12 },
  { name: 'Feb', issues: 19 },
  { name: 'Mar', issues: 8 },
  { name: 'Apr', issues: 15 },
  { name: 'May', issues: 6 },
];

export default function AnalysisCard() {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold">Analysis Overview</h3>
        <button className="text-sm text-pink-400 hover:underline">View Details</button>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', borderColor: '#4B5563' }}
              itemStyle={{ color: '#F3F4F6' }}
            />
            <Bar 
              dataKey="issues" 
              fill="#EC4899" 
              radius={[4, 4, 0, 0]} 
              animationDuration={1500}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}