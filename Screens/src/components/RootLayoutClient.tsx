'use client';

import { FC, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';

interface RootLayoutClientProps {
  children: React.ReactNode;
}

const RootLayoutClient: FC<RootLayoutClientProps> = ({ children }) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true);

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar onCollapseChange={setIsSidebarCollapsed} />
      <div
        className={`transition-all duration-300 ease-in-out ${
          isSidebarCollapsed ? 'ml-16' : 'ml-64'
        }`}
      >
        <Header />
        <main className="py-6">
          <div className="mx-auto px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default RootLayoutClient; 