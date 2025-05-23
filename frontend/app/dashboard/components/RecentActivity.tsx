// frontend/app/dashboard/components/RecentActivity.tsx
import { FiCheckCircle, FiAlertTriangle, FiInfo } from 'react-icons/fi';

export default function RecentActivity() {
  const activities = [
    {
      id: 1,
      type: 'fix',
      title: 'Applied fix for unused import',
      project: 'ecommerce-api',
      time: '2 hours ago',
      icon: <FiCheckCircle className="text-green-400" />
    },
    {
      id: 2,
      type: 'warning',
      title: 'Security vulnerability detected',
      project: 'auth-service',
      time: '1 day ago',
      icon: <FiAlertTriangle className="text-yellow-400" />
    },
    {
      id: 3,
      type: 'info',
      title: 'New Flamingo achievement unlocked',
      project: '',
      time: '2 days ago',
      icon: <FiInfo className="text-pink-400" />
    }
  ];

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold">Recent Activity</h3>
        <button className="text-sm text-pink-400 hover:underline">View All</button>
      </div>
      
      <div className="space-y-4">
        {activities.map(activity => (
          <div key={activity.id} className="flex items-start gap-4 p-3 hover:bg-gray-700/50 rounded-lg transition-colors cursor-pointer">
            <div className="p-2 bg-gray-700 rounded-lg mt-1">
              {activity.icon}
            </div>
            <div className="flex-1">
              <p className="font-medium">{activity.title}</p>
              <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
                {activity.project && (
                  <span className="bg-gray-700 px-2 py-1 rounded">{activity.project}</span>
                )}
                <span>{activity.time}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}