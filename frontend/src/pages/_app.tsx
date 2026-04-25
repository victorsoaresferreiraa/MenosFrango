/**
 * _app.tsx atualizado — versão 2.0
 *
 * NOVIDADE:
 * - Interface User agora tem o campo 'role'
 * - A função register aceita o parâmetro 'role'
 * - O AuthContext distribui o role para toda a app
 *
 * INSTRUÇÕES:
 * Substitua o arquivo frontend/src/pages/_app.tsx por este.
 */

import type { AppProps } from "next/app";
import { useState, useEffect, useCallback } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthContext, User } from "@/store/auth";
import { authApi, usersApi } from "@/lib/api";
import "@/styles/globals.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutos
      retry: 1,
    },
  },
});

export default function App({ Component, pageProps }: AppProps) {
  const [user,      setUser]      = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Ao iniciar, verifica se já tem sessão salva
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      usersApi.getMe()
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  // Login: salva tokens e busca perfil
  const login = useCallback(async (email: string, password: string) => {
    const res = await authApi.login({ email, password });
    const { access_token, refresh_token } = res.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);

    const meRes = await usersApi.getMe();
    setUser(meRes.data);
  }, []);

  // Registro: agora aceita o role (aluno ou personal)
  const register = useCallback(
    async (name: string, email: string, password: string, role = "aluno") => {
      const res = await authApi.register({ name, email, password, role });
      const { access_token, refresh_token } = res.data;
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);

      const meRes = await usersApi.getMe();
      setUser(meRes.data);
    },
    []
  );

  // Logout: limpa tudo
  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    queryClient.clear();
    window.location.href = "/login";
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          user,
          isAuthenticated: !!user,
          isLoading,
          login,
          register,
          logout,
          setUser,
        }}
      >
        <Component {...pageProps} />
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}
