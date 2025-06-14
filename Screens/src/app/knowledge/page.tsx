'use client';

import { FC } from 'react';
import {
  Search,
  Database,
  Network,
  FileText,
  Link2,
  Plus,
  Filter,
} from 'lucide-react';

const knowledgeItems = [
  {
    id: 1,
    title: 'Product Development Process',
    type: 'process',
    description: 'Complete guide to our product development lifecycle',
    connections: 12,
    lastUpdated: '2 days ago',
    tags: ['Product', 'Development', 'Process'],
  },
  {
    id: 2,
    title: 'API Integration Guide',
    type: 'technical',
    description: 'Technical documentation for API integration',
    connections: 8,
    lastUpdated: '1 week ago',
    tags: ['Technical', 'API', 'Integration'],
  },
  {
    id: 3,
    title: 'Team Communication Guidelines',
    type: 'policy',
    description: 'Best practices for team communication',
    connections: 15,
    lastUpdated: '3 days ago',
    tags: ['Communication', 'Policy', 'Team'],
  },
  {
    id: 4,
    title: 'Security Protocols',
    type: 'security',
    description: 'Security guidelines and protocols',
    connections: 10,
    lastUpdated: '5 days ago',
    tags: ['Security', 'Protocols', 'Guidelines'],
  },
];

const KnowledgePage: FC = () => {
  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Knowledge Base
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Access and explore organizational knowledge
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            Add Knowledge
          </button>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex space-x-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" aria-hidden="true" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Search knowledge base..."
                />
              </div>
            </div>
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Filter className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
              Filter
            </button>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {knowledgeItems.map((item) => (
              <div
                key={item.id}
                className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200"
              >
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      {item.type === 'process' && (
                        <Database className="h-5 w-5 text-blue-500" />
                      )}
                      {item.type === 'technical' && (
                        <Network className="h-5 w-5 text-purple-500" />
                      )}
                      {item.type === 'policy' && (
                        <FileText className="h-5 w-5 text-green-500" />
                      )}
                      {item.type === 'security' && (
                        <Link2 className="h-5 w-5 text-red-500" />
                      )}
                      <h3 className="ml-2 text-lg font-medium text-gray-900">
                        {item.title}
                      </h3>
                    </div>
                  </div>
                  <p className="mt-2 text-sm text-gray-500">
                    {item.description}
                  </p>
                  <div className="mt-4">
                    <div className="flex flex-wrap gap-2">
                      {item.tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center">
                      <Link2 className="h-4 w-4 mr-1" />
                      {item.connections} connections
                    </div>
                    <div>Updated {item.lastUpdated}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium text-gray-900">
              Vector Database Stats
            </h3>
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Total Documents</span>
                <span className="text-sm font-medium text-gray-900">1,234</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Average Query Time</span>
                <span className="text-sm font-medium text-gray-900">0.8s</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Storage Used</span>
                <span className="text-sm font-medium text-gray-900">2.4 GB</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium text-gray-900">
              Graph Database Stats
            </h3>
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Total Nodes</span>
                <span className="text-sm font-medium text-gray-900">5,678</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Total Relationships</span>
                <span className="text-sm font-medium text-gray-900">12,345</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Query Performance</span>
                <span className="text-sm font-medium text-gray-900">98.5%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgePage; 