'use client';

import { FC } from 'react';
import { Plus, Settings, Play, Pause, Trash2 } from 'lucide-react';

const agents = [
  {
    id: 1,
    name: 'Meeting Scheduler',
    description: 'Automatically schedules and manages team meetings',
    status: 'active',
    lastActive: '2 minutes ago',
  },
  {
    id: 2,
    name: 'Document Analyzer',
    description: 'Analyzes and categorizes internal documents',
    status: 'active',
    lastActive: '5 minutes ago',
  },
  {
    id: 3,
    name: 'Task Prioritizer',
    description: 'Prioritizes and assigns tasks based on importance',
    status: 'paused',
    lastActive: '1 hour ago',
  },
  {
    id: 4,
    name: 'Email Digest',
    description: 'Generates daily email digests for team updates',
    status: 'active',
    lastActive: '30 minutes ago',
  },
];

const AgentsPage: FC = () => {
  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            AI Agents
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Manage and monitor your AI agents for task automation
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            New Agent
          </button>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul role="list" className="divide-y divide-gray-200">
          {agents.map((agent) => (
            <li key={agent.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <p className="text-sm font-medium text-blue-600 truncate">
                      {agent.name}
                    </p>
                    <span
                      className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        agent.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {agent.status}
                    </span>
                  </div>
                  <div className="ml-2 flex-shrink-0 flex">
                    <button
                      type="button"
                      className="mr-2 inline-flex items-center p-1.5 border border-transparent rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      {agent.status === 'active' ? (
                        <Pause className="h-5 w-5" aria-hidden="true" />
                      ) : (
                        <Play className="h-5 w-5" aria-hidden="true" />
                      )}
                    </button>
                    <button
                      type="button"
                      className="mr-2 inline-flex items-center p-1.5 border border-transparent rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <Settings className="h-5 w-5" aria-hidden="true" />
                    </button>
                    <button
                      type="button"
                      className="inline-flex items-center p-1.5 border border-transparent rounded-full text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      <Trash2 className="h-5 w-5" aria-hidden="true" />
                    </button>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      {agent.description}
                    </p>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <p>Last active {agent.lastActive}</p>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Agent Statistics
          </h3>
          <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total Tasks Completed
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  1,234
                </dd>
              </div>
            </div>
            <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Average Response Time
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  2.5s
                </dd>
              </div>
            </div>
            <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Success Rate
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  98.5%
                </dd>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentsPage; 