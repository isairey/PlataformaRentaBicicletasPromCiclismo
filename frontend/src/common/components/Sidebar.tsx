import { NavLink } from 'react-router-dom';

interface SidebarLink {
  to: string;
  label: string;
}

interface SidebarProps {
  links: SidebarLink[];
}

export default function Sidebar({ links }: SidebarProps) {
  return (
    <aside className="flex flex-col w-56 flex-shrink-0 bg-brand-50 border-r border-brand-100 h-full overflow-y-auto py-4">
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) =>
            [
              'px-4 py-2 text-sm mx-2 rounded transition-colors',
              isActive
                ? 'bg-brand-100 text-brand-500 font-medium'
                : 'text-text-muted hover:bg-brand-50 hover:text-text',
            ].join(' ')
          }
        >
          {link.label}
        </NavLink>
      ))}
    </aside>
  );
}
