// frontend/app/dashboard/components/RulesQualityGates.tsx
import { FiShield, FiCheckCircle, FiAlertTriangle, FiInfo, FiList } from 'react-icons/fi';

export default function RulesQualityGates() {
  const rules = [
    {
      category: 'Code Style',
      enabled: true,
      rules: [
        { name: 'PEP 8 Compliance', severity: 'warning', description: 'Enforce PEP 8 style guidelines' },
        { name: 'Docstring Presence', severity: 'info', description: 'Require docstrings for public methods' },
        { name: 'Type Hinting', severity: 'warning', description: 'Encourage type hints for better code clarity' }
      ]
    },
    {
      category: 'Security',
      enabled: true,
      rules: [
        { name: 'SQL Injection', severity: 'critical', description: 'Detect potential SQL injection vulnerabilities' },
        { name: 'Hardcoded Secrets', severity: 'critical', description: 'Flag potential hardcoded credentials' },
        { name: 'Insecure Deserialization', severity: 'high', description: 'Identify unsafe deserialization patterns' }
      ]
    },
    {
      category: 'Performance',
      enabled: false,
      rules: [
        { name: 'Time Complexity', severity: 'medium', description: 'Warn about potentially inefficient algorithms' },
        { name: 'Memory Usage', severity: 'medium', description: 'Flag excessive memory consumption patterns' }
      ]
    }
  ];

  const qualityGates = [
    { 
      name: 'Critical Issues', 
      threshold: 0, 
      description: 'No critical severity issues allowed',
      status: 'passed'
    },
    { 
      name: 'Test Coverage', 
      threshold: 80, 
      description: 'Minimum 80% test coverage required',
      status: 'failed'
    },
    { 
      name: 'Code Duplication', 
      threshold: 5, 
      description: 'Maximum 5% duplicated code allowed',
      status: 'passed'
    }
  ];

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold">Rules & Quality Gates</h2>
          <p className="text-gray-400">Configure your code analysis rules and quality standards</p>
        </div>
        <button className="bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <FiShield /> Save Changes
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
            <FiList /> Active Rules
          </h3>
          
          <div className="space-y-6">
            {rules.map((group) => (
              <div key={group.category} className="border-b border-gray-700 pb-6 last:border-0 last:pb-0">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="font-medium">{group.category}</h4>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" checked={group.enabled} />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-600"></div>
                  </label>
                </div>
                
                <div className="space-y-3">
                  {group.rules.map((rule) => (
                    <div key={rule.name} className="flex items-start gap-3 p-3 bg-gray-700/50 rounded-lg">
                      <div className={`pt-1 ${rule.severity === 'critical' ? 'text-red-400' : rule.severity === 'high' ? 'text-orange-400' : rule.severity === 'warning' ? 'text-yellow-400' : 'text-blue-400'}`}>
                        {rule.severity === 'critical' || rule.severity === 'high' ? <FiAlertTriangle /> : <FiCheckCircle />}
                      </div>
                      <div>
                        <p className="font-medium">{rule.name}</p>
                        <p className="text-sm text-gray-400">{rule.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
            <FiShield /> Quality Gates
          </h3>
          
          <div className="space-y-4">
            {qualityGates.map((gate) => (
              <div key={gate.name} className={`p-4 rounded-lg border ${gate.status === 'passed' ? 'border-green-500/20 bg-green-500/10' : 'border-red-500/20 bg-red-500/10'}`}>
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium">{gate.name}</h4>
                  <span className={`px-2 py-1 rounded text-xs ${gate.status === 'passed' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {gate.status === 'passed' ? 'Passing' : 'Failing'}
                  </span>
                </div>
                <p className="text-sm text-gray-300 mb-3">{gate.description}</p>
                <div className="flex items-center gap-2 text-sm">
                  <span>Threshold:</span>
                  <span className="font-mono">{gate.threshold}{gate.name === 'Critical Issues' ? '' : '%'}</span>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-gray-700/50 rounded-lg border border-gray-600">
            <h4 className="font-medium mb-2 flex items-center gap-2 text-pink-400">
              <FiInfo /> Quality Gate Status
            </h4>
            <p className="text-sm text-gray-300">
              Your project is currently <span className="text-red-400">not passing</span> all quality gates. 
              Address the failing gates to ensure code quality standards.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}