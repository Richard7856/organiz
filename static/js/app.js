/* Organiz — lógica del panel.
   Habla con la API JSON de Flask mediante fetch() y refresca la interfaz.
   Sin dependencias externas para mantener la Fase 1 ligera. */

"use strict";

// Formatea importes como moneda local (se puede cambiar la divisa aquí).
const money = new Intl.NumberFormat("es-MX", {
  style: "currency",
  currency: "MXN",
});

const $ = (sel) => document.querySelector(sel);

// --- Llamadas a la API ----------------------------------------------------- //
async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || "Ocurrió un error inesperado.");
  }
  return data;
}

// --- Resumen (tarjetas) ---------------------------------------------------- //
async function loadSummary() {
  const s = await api("/api/summary");
  $("#total-income").textContent = money.format(s.total_income);
  $("#total-expense").textContent = money.format(s.total_expense);
  $("#balance").textContent = money.format(s.balance);
}

// --- Categorías ------------------------------------------------------------ //
// Rellena el desplegable según el tipo (ingreso/gasto) seleccionado.
async function loadCategories(kind) {
  const select = $("#category-select");
  const categories = await api(`/api/categories?kind=${kind}`);
  select.innerHTML = '<option value="">Sin categoría</option>';
  for (const c of categories) {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = c.name;
    select.appendChild(opt);
  }
}

// --- Lista de movimientos -------------------------------------------------- //
async function loadTransactions() {
  const body = $("#tx-body");
  const txs = await api("/api/transactions");

  if (txs.length === 0) {
    body.innerHTML =
      '<tr><td colspan="5" class="empty">Aún no hay movimientos. ¡Añade el primero!</td></tr>';
    return;
  }

  body.innerHTML = "";
  for (const t of txs) {
    const tr = document.createElement("tr");
    const sign = t.kind === "income" ? "+" : "−";
    const cls = t.kind === "income" ? "amount--income" : "amount--expense";

    tr.innerHTML = `
      <td>${t.date}</td>
      <td>${escapeHtml(t.category_name || "Sin categoría")}</td>
      <td>${escapeHtml(t.description || "")}</td>
      <td class="num ${cls}">${sign} ${money.format(t.amount)}</td>
      <td class="num">
        <button class="btn-delete" title="Eliminar" data-id="${t.id}">✕</button>
      </td>
    `;
    body.appendChild(tr);
  }
}

// Evita inyección de HTML al volcar texto del usuario en la tabla.
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// --- Eventos --------------------------------------------------------------- //
function setupKindToggle() {
  document.querySelectorAll('input[name="kind"]').forEach((radio) => {
    radio.addEventListener("change", (e) => loadCategories(e.target.value));
  });
}

function setupForm() {
  const form = $("#tx-form");
  const errorEl = $("#form-error");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";

    const formData = new FormData(form);
    const payload = {
      kind: formData.get("kind"),
      amount: formData.get("amount"),
      date: formData.get("date"),
      description: formData.get("description"),
      category_id: formData.get("category_id") || null,
    };

    try {
      await api("/api/transactions", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      // Conserva el tipo y la fecha; limpia importe y descripción para
      // encadenar varias altas rápidas.
      form.amount.value = "";
      form.description.value = "";
      await refresh();
    } catch (err) {
      errorEl.textContent = err.message;
    }
  });
}

function setupDelete() {
  // Delegación: un único listener cubre todos los botones de la tabla.
  $("#tx-body").addEventListener("click", async (e) => {
    const btn = e.target.closest(".btn-delete");
    if (!btn) return;
    if (!confirm("¿Eliminar este movimiento?")) return;

    try {
      await api(`/api/transactions/${btn.dataset.id}`, { method: "DELETE" });
      await refresh();
    } catch (err) {
      alert(err.message);
    }
  });
}

// --- Arranque -------------------------------------------------------------- //
async function refresh() {
  await Promise.all([loadSummary(), loadTransactions()]);
}

document.addEventListener("DOMContentLoaded", async () => {
  // Por defecto la fecha es hoy.
  $("#date-input").value = new Date().toISOString().slice(0, 10);

  setupKindToggle();
  setupForm();
  setupDelete();

  await loadCategories("income"); // 'income' es el tipo marcado por defecto
  await refresh();
});
