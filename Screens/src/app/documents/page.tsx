'use client';

import { FC, useState } from 'react';
import { Search, FileText, Folder, Lock, Users, Star, Clock, Download, Share2, MoreVertical } from 'lucide-react';

interface Document {
  id: string;
  title: string;
  type: 'pdf' | 'doc' | 'xls' | 'ppt' | 'txt';
  size: string;
  lastModified: string;
  owner: string;
  department: string;
  accessLevel: 'public' | 'department' | 'restricted';
  tags: string[];
  isStarred: boolean;
}

const DocumentsPage: FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  const [selectedAccess, setSelectedAccess] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Sample documents data - In a real app, this would come from an API
  const documents: Document[] = [
    {
      id: '1',
      title: 'Q1 Financial Report 2024',
      type: 'pdf',
      size: '2.4 MB',
      lastModified: '2024-03-20',
      owner: 'Sarah Johnson',
      department: 'Finance',
      accessLevel: 'department',
      tags: ['finance', 'report', 'q1'],
      isStarred: true,
    },
    {
      id: '2',
      title: 'Product Roadmap 2024',
      type: 'ppt',
      size: '4.1 MB',
      lastModified: '2024-03-19',
      owner: 'Mike Chen',
      department: 'Product',
      accessLevel: 'public',
      tags: ['product', 'roadmap', 'strategy'],
      isStarred: false,
    },
    {
      id: '3',
      title: 'Employee Handbook',
      type: 'pdf',
      size: '1.8 MB',
      lastModified: '2024-03-15',
      owner: 'HR Department',
      department: 'Human Resources',
      accessLevel: 'public',
      tags: ['hr', 'policy', 'handbook'],
      isStarred: true,
    },
    {
      id: '4',
      title: 'Confidential - Merger Strategy',
      type: 'doc',
      size: '3.2 MB',
      lastModified: '2024-03-18',
      owner: 'John Smith',
      department: 'Executive',
      accessLevel: 'restricted',
      tags: ['confidential', 'strategy', 'merger'],
      isStarred: false,
    },
    {
      id: '5',
      title: 'Marketing Campaign Q2',
      type: 'xls',
      size: '1.5 MB',
      lastModified: '2024-03-17',
      owner: 'Emma Davis',
      department: 'Marketing',
      accessLevel: 'department',
      tags: ['marketing', 'campaign', 'q2'],
      isStarred: false,
    },
  ];

  const departments = ['all', 'Finance', 'Product', 'Human Resources', 'Executive', 'Marketing'];
  const accessLevels = ['all', 'public', 'department', 'restricted'];

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return <FileText className="h-6 w-6 text-red-500" />;
      case 'doc':
        return <FileText className="h-6 w-6 text-blue-500" />;
      case 'xls':
        return <FileText className="h-6 w-6 text-green-500" />;
      case 'ppt':
        return <FileText className="h-6 w-6 text-orange-500" />;
      default:
        return <FileText className="h-6 w-6 text-gray-500" />;
    }
  };

  const getAccessIcon = (accessLevel: string) => {
    switch (accessLevel) {
      case 'public':
        return <Users className="h-4 w-4 text-green-500" />;
      case 'department':
        return <Folder className="h-4 w-4 text-blue-500" />;
      case 'restricted':
        return <Lock className="h-4 w-4 text-red-500" />;
      default:
        return <Users className="h-4 w-4 text-gray-500" />;
    }
  };

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesDepartment = selectedDepartment === 'all' || doc.department === selectedDepartment;
    const matchesAccess = selectedAccess === 'all' || doc.accessLevel === selectedAccess;
    return matchesSearch && matchesDepartment && matchesAccess;
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-1">Access and manage your documents</p>
        </div>
        <div className="flex space-x-4">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg ${
              viewMode === 'grid' ? 'bg-gray-100' : 'hover:bg-gray-50'
            }`}
          >
            <Folder className="h-5 w-5 text-gray-600" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg ${
              viewMode === 'list' ? 'bg-gray-100' : 'hover:bg-gray-50'
            }`}
          >
            <FileText className="h-5 w-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <select
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept === 'all' ? 'All Departments' : dept}
              </option>
            ))}
          </select>
          <select
            value={selectedAccess}
            onChange={(e) => setSelectedAccess(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {accessLevels.map((level) => (
              <option key={level} value={level}>
                {level === 'all' ? 'All Access Levels' : level.charAt(0).toUpperCase() + level.slice(1)}
              </option>
            ))}
          </select>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
            Upload Document
          </button>
        </div>
      </div>

      {/* Documents Grid/List */}
      <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
        {filteredDocuments.map((doc) => (
          <div
            key={doc.id}
            className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                {getFileIcon(doc.type)}
                <div>
                  <h3 className="font-medium text-gray-900">{doc.title}</h3>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-sm text-gray-500">{doc.size}</span>
                    <span className="text-gray-300">•</span>
                    <span className="text-sm text-gray-500">{doc.type.toUpperCase()}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {doc.isStarred ? (
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                ) : (
                  <Star className="h-5 w-5 text-gray-400" />
                )}
                <MoreVertical className="h-5 w-5 text-gray-400" />
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-1">
                  {getAccessIcon(doc.accessLevel)}
                  <span className="text-sm text-gray-500">
                    {doc.accessLevel.charAt(0).toUpperCase() + doc.accessLevel.slice(1)}
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-500">{doc.lastModified}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button className="p-1 hover:bg-gray-100 rounded">
                  <Download className="h-4 w-4 text-gray-500" />
                </button>
                <button className="p-1 hover:bg-gray-100 rounded">
                  <Share2 className="h-4 w-4 text-gray-500" />
                </button>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {doc.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentsPage; 