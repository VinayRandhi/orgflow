'use client';

import { FC } from 'react';
import {
  Calendar,
  FileText,
  Users,
  Clock,
  CheckCircle,
  AlertCircle,
  ChevronRight,
  Flag,
  User,
  Users as UsersIcon,
  Check,
  Mail,
  Star,
  Bell,
} from 'lucide-react';

interface Task {
  id: string;
  title: string;
  dueDate: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in-progress' | 'completed';
}

interface EmailNotification {
  id: string;
  subject: string;
  sender: string;
  time: string;
  priority: 'high' | 'medium' | 'low';
  isRead: boolean;
  summary?: string;
}

const Dashboard: FC = () => {
  // Sample tasks data
  const tasks: Task[] = [
    {
      id: '1',
      title: 'Review Q1 Project Proposals',
      dueDate: '2024-03-25',
      priority: 'high',
      status: 'pending',
    },
    {
      id: '2',
      title: 'Team Performance Review',
      dueDate: '2024-03-28',
      priority: 'medium',
      status: 'in-progress',
    },
    {
      id: '3',
      title: 'Update Documentation',
      dueDate: '2024-03-30',
      priority: 'low',
      status: 'pending',
    },
  ];

  // Sample email notifications data
  const emailNotifications: EmailNotification[] = [
    {
      id: '1',
      subject: 'Urgent: Client Project Deadline Extension Request',
      sender: 'client@example.com',
      time: '10:30 AM',
      priority: 'high',
      isRead: false,
      summary: 'Client requesting 2-week extension for the current milestone. Need immediate attention.'
    },
    {
      id: '2',
      subject: 'Team Meeting Minutes - March 20',
      sender: 'team@company.com',
      time: '9:15 AM',
      priority: 'medium',
      isRead: true,
      summary: 'Summary of yesterday\'s team meeting and action items.'
    },
    {
      id: '3',
      subject: 'New Feature Request from Product Team',
      sender: 'product@company.com',
      time: 'Yesterday',
      priority: 'medium',
      isRead: false,
      summary: 'Proposal for new dashboard analytics feature.'
    },
    {
      id: '4',
      subject: 'Weekly Newsletter',
      sender: 'newsletter@company.com',
      time: 'Yesterday',
      priority: 'low',
      isRead: true,
      summary: 'Company updates and announcements for the week.'
    }
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      case 'medium':
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      case 'low':
        return <AlertCircle className="h-4 w-4 text-green-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-semibold text-gray-900">Welcome back, Vinay!</h1>
        <p className="text-gray-600 mt-1">Here's what's happening today.</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Today's Meetings</p>
              <p className="text-2xl font-semibold text-gray-900 mt-1">3</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Tasks</p>
              <p className="text-2xl font-semibold text-gray-900 mt-1">5</p>
            </div>
            <div className="bg-yellow-100 p-3 rounded-full">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Team Members</p>
              <p className="text-2xl font-semibold text-gray-900 mt-1">12</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <Users className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Tasks and Email Notifications */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tasks Section - Shrunk */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Your Tasks</h2>
            <button className="text-sm text-blue-600 hover:text-blue-700">View All</button>
          </div>
          <div className="space-y-4">
            {tasks.map((task) => (
              <div
                key={task.id}
                className={`flex items-center justify-between p-4 rounded-lg transition-all ${
                  task.priority === 'high'
                    ? 'bg-red-50 border-l-4 border-red-500 scale-105 shadow-md'
                    : task.priority === 'medium'
                    ? 'bg-yellow-50 border-l-4 border-yellow-500'
                    : 'bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-full ${
                    task.status === 'completed' 
                      ? 'bg-green-100' 
                      : task.priority === 'high'
                      ? 'bg-red-100'
                      : task.priority === 'medium'
                      ? 'bg-yellow-100'
                      : 'bg-gray-100'
                  }`}>
                    <Check className={`h-4 w-4 ${
                      task.status === 'completed'
                        ? 'text-green-600'
                        : task.priority === 'high'
                        ? 'text-red-600'
                        : task.priority === 'medium'
                        ? 'text-yellow-600'
                        : 'text-gray-400'
                    }`} />
                  </div>
                  <div>
                    <p className={`font-medium ${
                      task.priority === 'high'
                        ? 'text-red-900'
                        : task.priority === 'medium'
                        ? 'text-yellow-900'
                        : 'text-gray-900'
                    }`}>
                      {task.title}
                    </p>
                    <div className="flex items-center space-x-2 mt-1">
                      <p className={`text-xs ${
                        task.priority === 'high'
                          ? 'text-red-600'
                          : task.priority === 'medium'
                          ? 'text-yellow-600'
                          : 'text-gray-500'
                      }`}>
                        Due: {task.dueDate}
                      </p>
                      {task.priority === 'high' && (
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">
                          Urgent
                        </span>
                      )}
                      {task.priority === 'medium' && (
                        <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                          Important
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getPriorityIcon(task.priority)}
                  {task.priority === 'high' && (
                    <div className="animate-pulse">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Email Notifications Section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Email Notifications</h2>
            <button className="text-sm text-blue-600 hover:text-blue-700">View All</button>
          </div>
          <div className="space-y-4">
            {emailNotifications.map((email) => (
              <div
                key={email.id}
                className={`p-4 rounded-lg ${
                  email.priority === 'high' ? 'bg-red-50' : 'bg-gray-50'
                } ${!email.isRead ? 'border-l-4 border-blue-500' : ''}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <Mail className={`h-4 w-4 ${
                        email.priority === 'high' ? 'text-red-600' : 'text-gray-400'
                      }`} />
                      <p className={`text-sm font-medium ${
                        !email.isRead ? 'text-gray-900' : 'text-gray-600'
                      }`}>
                        {email.subject}
                      </p>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      From: {email.sender} • {email.time}
                    </p>
                    {email.summary && (
                      <p className="text-sm text-gray-600 mt-2">{email.summary}</p>
                    )}
                  </div>
                  {email.priority === 'high' && (
                    <div className="ml-2">
                      <Bell className="h-4 w-4 text-red-600" />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 p-2 rounded-full">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">New document uploaded</p>
              <p className="text-xs text-gray-500">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 p-2 rounded-full">
              <Check className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Task completed</p>
              <p className="text-xs text-gray-500">4 hours ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
