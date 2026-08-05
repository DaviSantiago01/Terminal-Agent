const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api";

const ERROR_MESSAGES: Record<string, string> = {
  invalid_credentials: "E-mail ou senha incorretos.",
  user_already_exists: "Já existe uma conta com este e-mail.",
  authentication_required: "Faça login para continuar.",
  invalid_request: "Confira as informações informadas.",
};

function getErrorMessage(status: number, payload: unknown): string {
  if (status >= 500) {
    return "Não foi possível concluir sua solicitação. Tente novamente em instantes.";
  }

  const detail =
    payload && typeof payload === "object" && "detail" in payload
      ? (payload as { detail?: unknown }).detail
      : undefined;

  const code =
    detail && typeof detail === "object" && "code" in detail
      ? (detail as { code?: unknown }).code
      : detail;

  if (typeof code === "string" && ERROR_MESSAGES[code]) {
    return ERROR_MESSAGES[code];
  }

  if (status === 401) {
    return "Faça login para continuar.";
  }
  if (status === 409) {
    return "Estas informações já estão em uso.";
  }
  if (status === 422) {
    return "Confira as informações informadas.";
  }

  return "Não foi possível concluir sua solicitação. Tente novamente.";
}

interface ChatPayload {
  message: string;
  session_id?: string;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  let res: Response;

  try {
    res = await fetch(`${API_BASE}${path}`, {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });
  } catch {
    throw new Error("Não foi possível conectar ao servidor. Tente novamente.");
  }

  if (!res.ok) {
    const error = await res.json().catch(() => null);
    throw new Error(getErrorMessage(res.status, error));
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
};
