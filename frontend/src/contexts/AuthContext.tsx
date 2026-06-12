import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { AuthSession } from "../types";

const sessionKey = "ecommerce-ai-session";

function readSession(): AuthSession | null {
  const raw = localStorage.getItem(sessionKey);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    localStorage.removeItem(sessionKey);
    return null;
  }
}

interface AuthContextType {
  session: AuthSession | null;
  token: string;
  isOperator: boolean;
  login: (nextSession: AuthSession) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  session: null,
  token: "",
  isOperator: false,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(readSession);

  const token = session?.access || "";
  const isOperator = session?.user.role === "admin" || session?.user.role === "staff";

  function login(nextSession: AuthSession) {
    localStorage.setItem(sessionKey, JSON.stringify(nextSession));
    setSession(nextSession);
  }

  function logout() {
    localStorage.removeItem(sessionKey);
    setSession(null);
  }

  return (
    <AuthContext.Provider value={{ session, token, isOperator, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
