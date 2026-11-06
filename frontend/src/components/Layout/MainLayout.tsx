import { Outlet, useLocation } from 'react-router-dom';
import { useLayoutEffect } from 'react';
import Header from './Header.tsx';
import Sidebar from './Sidebar';
import RightSidebar from './RightSidebar';
export default function MainLayout() {
  const {pathname}=useLocation();
  useLayoutEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  }, [pathname]);
  const profile=pathname==='/profile';
  const focused=pathname==='/profile/edit';
  return <><Header /><div className={`velo-shell ${focused ? "settings-shell" : profile ? "profile-shell" : pathname === "/feed" ? "feed-shell" : ""}`}><Sidebar /><main className="velo-main"><Outlet /></main>{!focused && <RightSidebar />}</div></>;
}
