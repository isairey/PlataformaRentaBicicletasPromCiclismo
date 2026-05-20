import { Outlet } from 'react-router-dom';

export default function PublicLayout() {
  return (
    <div className="flex flex-col min-h-screen bg-surface">
      <header className="flex items-center h-14 px-6 border-b border-border flex-shrink-0">
        <span className="font-semibold text-text">Bike Network System</span>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
