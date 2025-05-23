// frontend/app/dashboard/components/AnalysisCard.tsx
import { FiUpload } from 'react-icons/fi';

export default function AnalysisCard() {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold">Start New Analysis</h3>
        <button className="text-sm text-pink-400 hover:underline">View All</button>
      </div>
      
      <div className="space-y-4">
        <div className="border-2 border-dashed border-gray-600 rounded-xl p-8 text-center hover:border-pink-400 transition-colors cursor-pointer">
          <div className="flex flex-col items-center justify-center">
            <FiUpload className="text-3xl text-pink-500 mb-3" />
            <p className="font-medium">Drag & Drop your Python project</p>
            <p className="text-sm text-gray-400 mt-1">or click to browse files</p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <button className="bg-gray-700 hover:bg-gray-600 p-4 rounded-lg transition-colors">
            <p className="font-medium text-left">Recent Project 1</p>
            <p className="text-xs text-gray-400 text-left">Last analyzed 2 days ago</p>
          </button>
          <button className="bg-gray-700 hover:bg-gray-600 p-4 rounded-lg transition-colors">
            <p className="font-medium text-left">Recent Project 2</p>
            <p className="text-xs text-gray-400 text-left">Last analyzed 1 week ago</p>
          </button>
        </div>
      </div>
    </div>
  );
}