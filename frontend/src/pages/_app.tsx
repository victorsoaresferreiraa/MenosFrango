import type { AppProps } from "next/app";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { Kablammo, Montserrat, Noto_Sans, Open_Sans, Roboto } from "next/font/google";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthContext, User } from "@/store/auth";
import { authApi, usersApi } from "@/lib/api";
import "@/styles/globals.css";

// 🌟 CORREÇÃO 1: Adicionado o "variable" para o Tailwind conseguir ler
const montserrat = Noto_Sans({
  subsets: ["latin"],
  weight: ["400"], 
  variable: "--font-montserrat", 
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
      retryDelay: 1000,
    },
  },
});

const PUBLIC_ROUTES = ["/login", "/register"];

export default function App({ Component, pageProps }: AppProps) {
  const [user,      setUser]      = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setIsLoading(false);
      if (!PUBLIC_ROUTES.includes(router.pathname)) {
        router.replace("/login");
      }
      return;
    }

    usersApi
      .getMe()
      .then((res) => {
        setUser(res.data);
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        if (!PUBLIC_ROUTES.includes(router.pathname)) {
          router.replace("/login");
        }
      })
      .finally(() => {
        setIsLoading(false);
      });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await authApi.login({ email, password });
    const { access_token, refresh_token } = res.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    const meRes = await usersApi.getMe();
    setUser(meRes.data);
  }, []);

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

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    queryClient.clear();
    window.location.href = "/login";
  }, []);

  if (isLoading) {
    return (
      <>
        <Head>
          <title>Carregando... | MENOSFRANGO</title>
          <link rel="icon" href="/frangoloco.svg" type="image/svg+xml" />
        </Head>
        {/* 🌟 CORREÇÃO 2: Aplicando a fonte no Loading */}
        <div className={`${montserrat.variable} font-sans min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-500`}>
          <div className="text-center">
            <div className="text-5xl mb-4 animate-bounce">🐔</div>
            <p className="text-gray-500 dark:text-gray-400 font-medium">Carregando MENOSFRANGO...</p>
          </div>
        </div>
      </>
    );
  }

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
        <Head>
          <title>MENOSFRANGO | Treino Inteligente</title>
          <link rel="icon" href="/frangoloco.svg" type="image/svg+xml" />
        </Head>
        
        {/* 🌟 CORREÇÃO 3: Envelopando todo o site com a sua fonte */}
        <main className={`${montserrat.variable} font-sans h-full`}>
          <Component {...pageProps} />
        </main>
        
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}