// Alle communicatie met de Flask-backend loopt via dit bestand. Zie Frontend/API.md.

import { CONFIG } from "./config.js";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = "GET", body } = {}) {
  let response;
  try {
    response = await fetch(CONFIG.apiBase + path, {
      method,
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("Geen verbinding met de server.", 0);
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(data.error || `Serverfout (${response.status})`, response.status);
  }
  return data;
}

export const api = {
  getState: () => request("/state"),
  spin: (bet) => request("/spin", { method: "POST", body: bet }),
  buyUpgrade: (id) => request(`/upgrades/${encodeURIComponent(id)}/buy`, { method: "POST" }),
  save: () => request("/save", { method: "POST" }),
  reset: () => request("/reset", { method: "POST" }),
  // Werkt ook als het tabblad gesloten wordt.
  saveOnExit: () => navigator.sendBeacon(CONFIG.apiBase + "/save"),
};
