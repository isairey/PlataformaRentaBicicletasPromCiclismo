import { Outlet } from 'react-router-dom';
import Navbar from '../common/components/Navbar';
import Sidebar from '../common/components/Sidebar';

const SIDEBAR_LINKS = [
  { to: '/bikes', label: 'Bikes' },
  { to: '/map', label: 'Map' },
  { to: '/rentals', label: 'Rentals' },
  { to: '/events', label: 'Events' },
  { to: '/routes', label: 'Routes' },
  { to: '/competitions', label: 'Competitions' },
];

export default function AppLayout() {
  return (
    <div className="flex flex-col h-screen bg-surface">
      <Navbar brandName="Bike Network System" />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar links={SIDEBAR_LINKS} />
        <main className="flex-1 overflow-y-auto p-6 bg-surface">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
