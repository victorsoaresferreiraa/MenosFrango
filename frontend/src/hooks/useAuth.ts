/**
 * Hook de autenticação — wrapper do AuthContext.
 */

import { useAuthContext } from "@/store/auth";

export const useAuth = () => useAuthContext();
