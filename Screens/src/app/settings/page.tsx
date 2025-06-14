'use client';

import { FC, useState } from 'react';
import { 
  User, 
  Bell, 
  Lock, 
  Shield, 
  FileText, 
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';

interface SettingSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  description: string;
  content: React.ReactNode;
}

const SettingsPage: FC = () => {
  const [activeSection, setActiveSection] = useState<string>('profile');
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    updates: true,
    marketing: false,
  });

  // Mock user role and permissions
  const userRole = {
    name: 'Project Manager',
    level: 'Mid-level',
    department: 'Engineering',
    permissions: [
      'View project documents',
      'Edit project timelines',
      'Manage team assignments',
      'Access financial reports',
      'Review performance metrics'
    ],
    accessibleDocuments: [
      'Project Roadmaps',
      'Team Performance Reports',
      'Financial Summaries',
      'Resource Allocation Plans',
      'Client Communication Templates'
    ]
  };

  const handleNotificationChange = (key: keyof typeof notifications) => {
    setNotifications(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const sections: SettingSection[] = [
    {
      id: 'profile',
      title: 'Profile Settings',
      icon: <User className="h-5 w-5" />,
      description: 'Manage your personal information and preferences',
      content: (
        <div className="space-y-6">
          <div className="flex items-center space-x-4">
            <div className="h-20 w-20 rounded-full bg-gray-200 flex items-center justify-center">
              <User className="h-10 w-10 text-gray-500" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">John Smith</h3>
              <p className="text-sm text-gray-500">john.smith@company.com</p>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">First Name</label>
              <input
                type="text"
                defaultValue="John"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Last Name</label>
              <input
                type="text"
                defaultValue="Smith"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                defaultValue="john.smith@company.com"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Phone</label>
              <input
                type="tel"
                defaultValue="+1 (555) 123-4567"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'notifications',
      title: 'Notification Preferences',
      icon: <Bell className="h-5 w-5" />,
      description: 'Configure how you receive updates and alerts',
      content: (
        <div className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
                <p className="text-sm text-gray-500">Receive updates via email</p>
              </div>
              <button
                onClick={() => handleNotificationChange('email')}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  notifications.email ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    notifications.email ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">Push Notifications</h3>
                <p className="text-sm text-gray-500">Receive push notifications on your devices</p>
              </div>
              <button
                onClick={() => handleNotificationChange('push')}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  notifications.push ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    notifications.push ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">Product Updates</h3>
                <p className="text-sm text-gray-500">Stay informed about new features and improvements</p>
              </div>
              <button
                onClick={() => handleNotificationChange('updates')}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  notifications.updates ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    notifications.updates ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">Marketing Communications</h3>
                <p className="text-sm text-gray-500">Receive marketing and promotional content</p>
              </div>
              <button
                onClick={() => handleNotificationChange('marketing')}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  notifications.marketing ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    notifications.marketing ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'access',
      title: 'Access Control',
      icon: <Shield className="h-5 w-5" />,
      description: 'View your role and document access permissions',
      content: (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Access Control</h3>
              <p className="mt-1 text-sm text-gray-500">
                Manage your role-based access and permissions
              </p>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1 bg-blue-50 rounded-full">
              <Shield className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-600">Active Role</span>
            </div>
          </div>

          {/* Role Information Card */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h4 className="text-base font-medium text-gray-900">Role Information</h4>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-gray-500">Role</p>
                  <p className="text-base text-gray-900">Project Manager</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-gray-500">Level</p>
                  <p className="text-base text-gray-900">Senior</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-gray-500">Department</p>
                  <p className="text-base text-gray-900">Product Development</p>
                </div>
              </div>
            </div>
          </div>

          {/* Permissions Card */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h4 className="text-base font-medium text-gray-900">Permissions</h4>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  'View Documents',
                  'Edit Documents',
                  'Create Documents',
                  'Delete Documents',
                  'Manage Team',
                  'Schedule Meetings',
                  'View Analytics',
                  'Manage Projects'
                ].map((permission) => (
                  <div key={permission} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0">
                      <div className="h-6 w-6 rounded-full bg-green-100 flex items-center justify-center">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      </div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{permission}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Accessible Documents Card */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h4 className="text-base font-medium text-gray-900">Accessible Documents</h4>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {[
                  'Q2 Strategy Document',
                  'Product Roadmap',
                  'Team Meeting Notes',
                  'Project Timeline',
                  'Resource Allocation',
                  'Budget Overview'
                ].map((document) => (
                  <div key={document} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0">
                      <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center">
                        <FileText className="h-4 w-4 text-blue-600" />
                      </div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{document}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Access Control Notice */}
          <div className="rounded-lg bg-blue-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <Info className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">Access Control Notice</h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>
                    Your access is based on your role as a Project Manager in the Product Development department.
                    You have full access to project-related documents and team management features.
                    Contact your administrator if you need additional permissions.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
          </div>
          <div className="bg-white shadow rounded-lg">
            <div className="grid grid-cols-12">
              {/* Sidebar */}
              <div className="col-span-12 sm:col-span-3 border-r border-gray-200">
                <nav className="p-4 space-y-1">
                  {sections.map((section) => (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                        activeSection === section.id
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {section.icon}
                      <span>{section.title}</span>
                    </button>
                  ))}
                </nav>
              </div>

              {/* Content */}
              <div className="col-span-12 sm:col-span-9 p-6">
                {sections.map((section) => (
                  <div
                    key={section.id}
                    className={activeSection === section.id ? 'block' : 'hidden'}
                  >
                    <div className="mb-6">
                      <h2 className="text-xl font-semibold text-gray-900">
                        {section.title}
                      </h2>
                      <p className="mt-1 text-sm text-gray-500">
                        {section.description}
                      </p>
                    </div>
                    {section.content}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 