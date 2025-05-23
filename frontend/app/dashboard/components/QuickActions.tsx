// frontend/app/dashboard/components/QuickActions.tsx
import { FiZap, FiClock, FiBookmark, FiStar } from 'react-icons/fi';

export default function QuickActions() {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-lg font-bold mb-6">Quick Actions</h3>
      
      <div className="space-y-3">
        <button className="w-full flex items-center gap-3 p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
          <div className="p-2 bg-pink-500/20 rounded-lg text-pink-400">
            <FiZap />
          </div>
          <span>Analyze Recent Project</span>
        </button>
        
        <button className="w-full flex items-center gap-3 p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
          <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
            <FiClock />
          </div>
          <span>View Analysis History</span>
        </button>
        
        <button className="w-full flex items-center gap-3 p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
          <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
            <FiBookmark />
          </div>
          <span>Saved Fixes</span>
        </button>
        
        <button className="w-full flex items-center gap-3 p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
          <div className="p-2 bg-yellow-500/20 rounded-lg text-yellow-400">
            <FiStar />
          </div>
          <span>Rate Our Service</span>
        </button>
      </div>
    </div>
  );
}