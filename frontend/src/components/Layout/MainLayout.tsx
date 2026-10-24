import { Outlet } from 'react-router-dom';
import Header from './Header.tsx';
import Sidebar from './Sidebar';
import RightSidebar from './RightSidebar';
export default function MainLayout() {
  return <><Header /><div className="velo-shell"><Sidebar /><main className="velo-main"><Outlet /></main><RightSidebar /></div></>;
}
