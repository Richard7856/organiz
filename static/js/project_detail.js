/* Organiz — detalle de un proyecto y sus avances (Fase 2). */

"use strict";

const $ = (sel) => document.querySelector(sel);
const projectId = $("#project-root").dataset.projectId;

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

// Pinta la barra de progreso del encabezado con el avance más reciente.
function renderHeaderProgress(updates) {
  const withProgress = updates.find((u) => u.progress != null);
  const fill = $("#progress-fill");
  const label = $("#progress-label");
  if (withProgress) {
    fill.style.width = withProgress.progress + "%";
    label.textContent = `${withProgress.progress}% completado`;
  } else {
    fill.style.width = "0%";
    label.textContent = "Sin porcentaje de avance registrado";
  }
}

// Carga y dibuja la línea de tiempo de avances.
async function loadProgress() {
  const list = $("#progress-list");
  const updates = await api(`/api/projects/${projectId}/progress`);
  renderHeaderProgress(updates);

  if (updates.length === 0) {
    list.innerHTML = '<p class="empty">Aún no hay avances. ¡Registra el primero!</p>';
    return;
  }

  list.innerHTML = "";
  for (const u of updates) {
    const item = document.createElement("div");
    item.className = "timeline__item";
    item.innerHTML = `
      <div class="timeline__head">
        <span class="timeline__date">${u.date}</span>
        ${u.progress != null ? `<span class="badge badge--active">${u.progress}%</span>` : ""}
        <button class="btn-delete" data-id="${u.id}" title="Eliminar avance">✕</button>
      </div>
      ${u.note ? `<p class="timeline__note">${escapeHtml(u.note)}</p>` : ""}
    `;
    list.appendChild(item);
  }
}

function setupProgressForm() {
  const form = $("#progress-form");
  const errorEl = $("#form-error");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    const fd = new FormData(form);
    try {
      await api(`/api/projects/${projectId}/progress`, {
        method: "POST",
        body: JSON.stringify({
          note: fd.get("note"),
          progress: fd.get("progress") || null,
          date: fd.get("date"),
        }),
      });
      form.note.value = "";
      form.progress.value = "";
      await loadProgress();
    } catch (err) {
      errorEl.textContent = err.message;
    }
  });
}

function setupDeleteProgress() {
  $("#progress-list").addEventListener("click", async (e) => {
    const btn = e.target.closest(".btn-delete");
    if (!btn) return;
    if (!confirm("¿Eliminar este avance?")) return;
    try {
      await api(`/api/progress/${btn.dataset.id}`, { method: "DELETE" });
      await loadProgress();
    } catch (err) {
      alert(err.message);
    }
  });
}

function setupStatusChange() {
  const select = $("#status-select");
  select.addEventListener("change", async () => {
    try {
      await api(`/api/projects/${projectId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: select.value }),
      });
    } catch (err) {
      alert(err.message);
    }
  });
}

function setupDeleteProject() {
  $("#delete-project").addEventListener("click", async () => {
    if (!confirm("¿Eliminar el proyecto y todos sus avances?")) return;
    try {
      await api(`/api/projects/${projectId}`, { method: "DELETE" });
      window.location.href = "/projects";
    } catch (err) {
      alert(err.message);
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  $("#date-input").value = new Date().toISOString().slice(0, 10);
  // Refleja en el desplegable el estado actual del proyecto.
  $("#status-select").value = $("#project-root").dataset.status || "active";

  setupProgressForm();
  setupDeleteProgress();
  setupStatusChange();
  setupDeleteProject();
  await loadProgress();
});
