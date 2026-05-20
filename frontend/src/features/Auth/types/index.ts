export interface AuthUser {
  uid: string;
  email: string;
}

export interface AuthSession {
  user: AuthUser;
  idToken: string;
  refreshToken: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  Name: string;
  rol?: string;
}

export interface RegisterResponse {
  uid: string;
  email: string;
  createdAt: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  idToken: string;
  refreshToken: string;
  expiresIn: string;
  localId: string;
  email: string;
}
