const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface ChatPayload {
  message: string;
  session_id?: string;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "Erro desconhecido");
  }

  return res.json() as Promise<T>;
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      request("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),

    register: (email: string, password: string) =>
      request("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),

    logout: () => request("/auth/logout", { method: "POST" }),

    me: () => request("/auth/me"),
  },

  chat: (payload: ChatPayload) =>
    request<{ output: string; session_id: string }>("/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  health: () => request("/health"),
};
