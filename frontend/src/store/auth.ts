/**
 * Store de autenticação — versão 2.0
 *
 * NOVIDADE: interface User agora tem o campo 'role'
 * e a função register aceita o parâmetro 'role'.
 *
 * INSTRUÇÕES:
 * Substitua o arquivo frontend/src/store/auth.ts por este.
 */

import { createContext, useContext } from "react";

export interface User {
  id:        string;
  email:     string;
  name:      string;
  role:      "aluno" | "personal" | "admin"; // NOVO
  goal?:     string;
  level?:    string;
  weight_kg?: number;
  height_cm?: number;
  age?:      number;
  bio?:      string;
  is_admin:  boolean;
}

export interface AuthState {
  user:            User | null;
  isAuthenticated: boolean;
  isLoading:       boolean;
  // ATUALIZADO: register agora aceita role
  login:    (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, role?: string) => Promise<void>;
  logout:   () => void;
  setUser:  (user: User) => void;
}

export const AuthContext = createContext<AuthState>({
  user:            null,
  isAuthenticated: false,
  isLoading:       true,
  login:           async () => {},
  register:        async () => {},
  logout:          () => {},
  setUser:         () => {},
});

export const useAuthContext = () => useContext(AuthContext);
