// frontend/app/dashboard/components/StatsCard.tsx
import { ReactNode } from 'react';

export default function StatsCard({ title, value, change, icon, trend }: { 
  title: string; 
  value: string; 
  change: string; 
  icon: ReactNode;
  trend: 'up' | 'down';
}) {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-pink-500/30 transition-colors">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          <p className="text-xs mt-2 text-gray-500">{change}</p>
        </div>
        <div className="p-2 bg-gray-700 rounded-lg">
          {icon}
        </div>
      </div>
    </div>
  );
}