export interface AuthUser {
  uid: string;
  email: string;
}

export interface AuthSession {
  user: AuthUser;
  idToken: string;
  refreshToken: string;
}

export interface AuthContextValue {
  user: AuthUser | null;
  idToken: string | null;
  isAdmin: boolean;
  login(session: AuthSession): void;
  logout(): void;
}
