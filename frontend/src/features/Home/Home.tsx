import { Link } from "react-router-dom";
import { useAuth } from "../../services/useAuth";

export default function Home() {
  const { idToken, user } = useAuth();

  return (
    <div className="p-12">
      <h1 className="text-3xl font-semibold text-text mb-6">
        Bike Network System
      </h1>
      {idToken ? (
        <div>
          <p className="text-lg text-text-muted mb-6">
            Welcome{user?.email ? `, ${user.email}` : ""}!
          </p>
          <Link
            to="/bikes"
            className="inline-block px-6 py-3 bg-brand-500 text-white rounded hover:bg-brand-600 no-underline"
          >
            Explore
          </Link>
        </div>
      ) : (
        <div className="flex gap-4 mt-6">
          <Link
            to="/register"
            className="px-6 py-3 bg-brand-500 text-white rounded hover:bg-brand-600 no-underline"
          >
            Register
          </Link>
          <Link
            to="/login"
            className="px-6 py-3 border border-brand-500 text-brand-500 rounded hover:bg-brand-50 no-underline"
          >
            Login
          </Link>
        </div>
      )}
    </div>
  );
}
