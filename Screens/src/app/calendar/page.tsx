'use client';

import { FC, useState } from 'react';
import { Calendar, Plus, Settings, ChevronLeft, ChevronRight } from 'lucide-react';

interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  source: 'google' | 'outlook' | 'other';
  description?: string;
  location?: string;
  attendees?: string[];
}

const CalendarPage: FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedView, setSelectedView] = useState<'day' | 'week' | 'month'>('week');
  const [connectedCalendars, setConnectedCalendars] = useState([
    { id: 'google', name: 'Google Calendar', connected: false },
    { id: 'outlook', name: 'Microsoft Outlook', connected: false },
  ]);

  const handleConnectCalendar = (calendarId: string) => {
    setConnectedCalendars(calendars =>
      calendars.map(cal =>
        cal.id === calendarId ? { ...cal, connected: true } : cal
      )
    );
  };

  const handleDisconnectCalendar = (calendarId: string) => {
    setConnectedCalendars(calendars =>
      calendars.map(cal =>
        cal.id === calendarId ? { ...cal, connected: false } : cal
      )
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Calendar
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            View and manage your organization's calendar events
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-3">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            New Event
          </button>
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Settings className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            Calendar Settings
          </button>
        </div>
      </div>

      {/* Calendar Navigation */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => {
                  const newDate = new Date(currentDate);
                  newDate.setMonth(newDate.getMonth() - 1);
                  setCurrentDate(newDate);
                }}
                className="p-2 hover:bg-gray-100 rounded-full"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <h3 className="text-lg font-medium text-gray-900">
                {currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })}
              </h3>
              <button
                onClick={() => {
                  const newDate = new Date(currentDate);
                  newDate.setMonth(newDate.getMonth() + 1);
                  setCurrentDate(newDate);
                }}
                className="p-2 hover:bg-gray-100 rounded-full"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setSelectedView('day')}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
                  selectedView === 'day'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Day
              </button>
              <button
                onClick={() => setSelectedView('week')}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
                  selectedView === 'week'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Week
              </button>
              <button
                onClick={() => setSelectedView('month')}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
                  selectedView === 'month'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Month
              </button>
            </div>
          </div>

          {/* Calendar View */}
          <div className="border rounded-lg">
            {/* Calendar grid will be implemented here */}
            <div className="min-h-[600px] flex items-center justify-center text-gray-500">
              Calendar view will be implemented here
            </div>
          </div>
        </div>
      </div>

      {/* Connected Calendars */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Connected Calendars
          </h3>
          <div className="space-y-4">
            {connectedCalendars.map((calendar) => (
              <div
                key={calendar.id}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div className="flex items-center">
                  <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">
                      {calendar.name}
                    </h4>
                    <p className="text-sm text-gray-500">
                      {calendar.connected
                        ? 'Connected'
                        : 'Not connected'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() =>
                    calendar.connected
                      ? handleDisconnectCalendar(calendar.id)
                      : handleConnectCalendar(calendar.id)
                  }
                  className={`px-4 py-2 rounded-md text-sm font-medium ${
                    calendar.connected
                      ? 'bg-red-100 text-red-700 hover:bg-red-200'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  {calendar.connected ? 'Disconnect' : 'Connect'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarPage; 