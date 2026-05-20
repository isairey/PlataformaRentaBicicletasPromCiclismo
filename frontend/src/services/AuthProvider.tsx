import { useState, useCallback } from "react";
import type { ReactNode } from "react";
import { AuthContext } from "./AuthContextDef";
import type { AuthUser, AuthSession } from "./authTypes";

interface AuthProviderProps {
  children: ReactNode;
}

function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64)) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function computeIsAdmin(token: string | null): boolean {
  if (!token) return false;
  const payload = decodeJwtPayload(token);
  return payload.role === "admin";
}

/** Restore session user from JWT so queries work after full page reload. */
function userFromStoredToken(token: string | null): AuthUser | null {
  if (!token) return null;
  const payload = decodeJwtPayload(token);
  const uid = payload.sub;
  if (typeof uid !== "string" || !uid) return null;
  const email = payload.email;
  return {
    uid,
    email: typeof email === "string" ? email : "",
  };
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(() =>
    userFromStoredToken(localStorage.getItem("bns_id_token")),
  );
  const [idToken, setIdToken] = useState<string | null>(() =>
    localStorage.getItem("bns_id_token"),
  );
  const [isAdmin, setIsAdmin] = useState<boolean>(() =>
    computeIsAdmin(localStorage.getItem("bns_id_token")),
  );

  const login = useCallback((session: AuthSession) => {
    localStorage.setItem("bns_id_token", session.idToken);
    localStorage.setItem("bns_refresh_token", session.refreshToken);
    const payload = decodeJwtPayload(session.idToken);
    setUser({
      uid: payload.sub as string,
      email: payload.email as string,
    });
    setIdToken(session.idToken);
    setIsAdmin(computeIsAdmin(session.idToken));
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("bns_id_token");
    localStorage.removeItem("bns_refresh_token");
    setUser(null);
    setIdToken(null);
    setIsAdmin(false);
  }, []);

  return (
    <AuthContext.Provider value={{ user, idToken, isAdmin, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
