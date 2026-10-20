import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import RightSidebar from './RightSidebar';

interface MainLayoutProps {
  showSidebar?: boolean;
  showRightSidebar?: boolean;
}

const MainLayout: React.FC<MainLayoutProps> = ({ 
  showSidebar = true,
  showRightSidebar = true 
}) => {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <div className="flex max-w-[1440px] mx-auto">
        {showSidebar && <Sidebar />}
        <main className="flex-1 min-w-0 bg-[#f5f3f0]">
          <Outlet />
        </main>
        {showRightSidebar && <RightSidebar />}
      </div>
    </div>
  );
};

export default MainLayout;
