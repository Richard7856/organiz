/* Organiz — listado y creación de proyectos (Fase 2). */

"use strict";

const $ = (sel) => document.querySelector(sel);

const STATUS_LABELS = {
  active: "En curso",
  paused: "En pausa",
  completed: "Terminado",
};

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Ocurrió un error inesperado.");
  return data;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// Dibuja la lista de proyectos como tarjetas enlazadas a su detalle.
async function loadProjects() {
  const container = $("#projects-list");
  const projects = await api("/api/projects");

  if (projects.length === 0) {
    container.innerHTML =
      '<p class="empty">Aún no tienes proyectos. ¡Crea el primero!</p>';
    return;
  }

  container.innerHTML = "";
  for (const p of projects) {
    const progress = p.latest_progress;
    const card = document.createElement("a");
    card.className = "project-card";
    card.href = `/projects/${p.id}`;
    card.innerHTML = `
      <div class="project-card__head">
        <span class="project-card__name">${escapeHtml(p.name)}</span>
        <span class="badge badge--${p.status}">${STATUS_LABELS[p.status]}</span>
      </div>
      ${p.description ? `<p class="project-card__desc">${escapeHtml(p.description)}</p>` : ""}
      <div class="progress-bar">
        <div class="progress-bar__fill" style="width: ${progress ?? 0}%"></div>
      </div>
      <span class="project-card__meta">
        ${progress != null ? progress + "% · " : ""}${p.updates_count} avance(s)
      </span>
    `;
    container.appendChild(card);
  }
}

function setupForm() {
  const form = $("#project-form");
  const errorEl = $("#form-error");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    const fd = new FormData(form);
    try {
      await api("/api/projects", {
        method: "POST",
        body: JSON.stringify({
          name: fd.get("name"),
          description: fd.get("description"),
          status: fd.get("status"),
        }),
      });
      form.reset();
      await loadProjects();
    } catch (err) {
      errorEl.textContent = err.message;
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  setupForm();
  await loadProjects();
});
