"use server";

import { cookies } from "next/headers";

export async function createSession(token: string, userData: any) {
  // Define o tempo de expiração do cookie (ex: 7 dias)
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

  // Salva o token em um cookie seguro no lado do servidor
  cookies().set("lumay_session", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    expires: expiresAt,
    sameSite: "lax",
    path: "/",
  });

  // Opcional: Se você quiser salvar o ID ou cargo (role) do usuário no cookie também
  if (userData && userData.id) {
    cookies().set("lumay_user_id", String(userData.id), {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      expires: expiresAt,
      sameSite: "lax",
      path: "/",
    });
  }
}

export async function deleteSession() {
  // Função extra: útil para quando você for fazer a tela de Logout!
  cookies().delete("lumay_session");
  cookies().delete("lumay_user_id");
}