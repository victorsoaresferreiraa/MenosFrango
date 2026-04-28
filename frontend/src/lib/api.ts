import axios, { AxiosError, AxiosInstance } from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as any;

    if (
      typeof window !== "undefined" &&
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !original.url?.includes("/auth/login") &&
      !original.url?.includes("/auth/refresh")
    ) {
      original._retry = true;

      const refreshToken = localStorage.getItem("refresh_token");

      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;

          localStorage.setItem("access_token", access_token);
          localStorage.setItem("refresh_token", refresh_token);

          original.headers = original.headers || {};
          original.headers.Authorization = `Bearer ${access_token}`;

          return api(original);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      } else {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export const authApi = {
  register: (data: { email: string; password: string; name: string; role?: string }) =>
    api.post("/auth/register", data),

  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", {
      email: data.email,
      password: data.password,
    }),

  refresh: (refresh_token: string) => api.post("/auth/refresh", { refresh_token }),
};

export const fatsecretApi = {
  searchFoods: (q: string) =>
    api.get("/fatsecret/foods/search", {
      params: { q },
    }),
};

export const usersApi = {
  getMe: () => api.get("/users/me"),
  updateMe: (data: any) => api.put("/users/me", data),
};

export const workoutsApi = {
  list: (params?: { page?: number; page_size?: number; muscle_group?: string }) =>
    api.get("/workouts", { params }),
  create: (data: any) => api.post("/workouts", data),
  update: (id: string, data: any) => api.put(`/workouts/${id}`, data),
  delete: (id: string) => api.delete(`/workouts/${id}`),
};


export const nutritionApi = {
  logFood: (data: any) => api.post("/nutrition/log", data),
  getDay: (date: string) => api.get(`/nutrition/day/${date}`),
  getMacroGoals: () => api.get("/nutrition/macro-goals"),
  deleteLog: (id: string) => api.delete(`/nutrition/log/${id}`),
};

export const dashboardApi = {
  getSummary: () => api.get("/dashboard/summary"),
  getGraphs: (days?: number) => api.get("/dashboard/graphs", { params: { days } }),
};

export const photosApi = {
  list: () => api.get("/photos"),
  upload: (formData: FormData) =>
    api.post("/photos", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  delete: (id: string) => api.delete(`/photos/${id}`),
};

export const aiApi = {
  workoutPlan: (data: any) => api.post("/ai/workout-plan", data),
  nutritionPlan: (data: any) => api.post("/ai/nutrition-plan", data),
  analyzeProgress: (data?: any) => api.post("/ai/analyze-progress", data || {}),
  history: () => api.get("/ai/history"),
};

export const reportsApi = {
  requestMonthly: (year?: number, month?: number) =>
    api.post("/reports/monthly", null, { params: { year, month } }),
};

export const personalApi = {
  getDashboard: () => api.get("/personal/dashboard"),
  listClients: () => api.get("/personal/clients"),
  inviteClient: (data: { client_email: string; notes?: string }) =>
    api.post("/personal/clients/invite", data),
  getClient: (clientId: string) => api.get(`/personal/clients/${clientId}`),
  updateClientNotes: (clientId: string, notes: string) =>
    api.put(`/personal/clients/${clientId}/notes`, { notes }),
  removeClient: (clientId: string) => api.delete(`/personal/clients/${clientId}`),
  getClientWorkouts: (clientId: string, page = 1) =>
    api.get(`/personal/clients/${clientId}/workouts`, { params: { page } }),
  getClientNutrition: (clientId: string) =>
    api.get(`/personal/clients/${clientId}/nutrition`),
  generateWorkoutPlan: (clientId: string, data: any) =>
    api.post(`/personal/clients/${clientId}/ai/workout-plan`, data),
  generateNutritionPlan: (clientId: string, data: any) =>
    api.post(`/personal/clients/${clientId}/ai/nutrition-plan`, data),
  getMyPersonals: () => api.get("/personal/my-personals"),
  acceptInvite: (linkId: string) => api.post(`/personal/accept-invite/${linkId}`),
};
