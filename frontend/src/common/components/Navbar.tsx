import { useAuth } from "../../services/useAuth";
import { useNavigate } from "react-router-dom";

interface NavbarProps {
  brandName: string;
}

export default function Navbar({ brandName }: NavbarProps) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  function handleHome() {
    navigate("/");
  }

  return (
    <header className="flex items-center justify-between h-14 px-6 bg-surface border-b border-border flex-shrink-0">
      <span
        onClick={handleHome}
        className="font-semibold text-text cursor-pointer"
      >
        {brandName}
      </span>
      <button
        onClick={handleLogout}
        className="px-3 py-1.5 text-sm border border-border rounded text-text-muted hover:bg-surface-muted cursor-pointer bg-transparent"
      >
        Logout
      </button>
    </header>
  );
}
