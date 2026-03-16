const BACKEND_URL = window.BACKEND_URL || "http://localhost:8000";

const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");
const historyList = document.getElementById("history-list");
const resultsBody = document.getElementById("results-body");
const statusEl = document.getElementById("status");
const toastEl = document.getElementById("toast");

let currentResults = [];
let currentSort = { field: "name", direction: "asc" };

function getSelectedMode() {
  const el = document.querySelector('input[name="mode"]:checked');
  return el ? el.value : "broad_web";
}

function setStatus(text) {
  statusEl.textContent = text || "";
}

function showToast(message) {
  toastEl.textContent = message;
  toastEl.classList.remove("hidden");
  setTimeout(() => toastEl.classList.add("hidden"), 2500);
}

async function fetchJSON(path, options = {}) {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`Request failed with status ${res.status}`);
  }
  return res.json();
}

function renderHistory(items) {
  historyList.innerHTML = "";
  for (const item of items) {
    const li = document.createElement("li");
    li.className = "history-item";
    li.innerHTML = `
      <span>${item.query}</span>
      <span class="history-item-mode">${item.mode}</span>
    `;
    li.addEventListener("click", () => {
      searchInput.value = item.query;
      const modeRadio = document.querySelector(
        'input[name="mode"][value="' + item.mode + '"]'
      );
      if (modeRadio) modeRadio.checked = true;
      runSearch();
    });
    historyList.appendChild(li);
  }
}

function renderResults() {
  resultsBody.innerHTML = "";
  const sorted = [...currentResults].sort((a, b) => {
    const field = currentSort.field;
    const dir = currentSort.direction === "asc" ? 1 : -1;
    const av = (a[field] || "").toString().toLowerCase();
    const bv = (b[field] || "").toString().toLowerCase();
    if (av < bv) return -1 * dir;
    if (av > bv) return 1 * dir;
    return 0;
  });

  for (const s of sorted) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>
        <div class="supplier-name"><a href="${s.url}" target="_blank" rel="noreferrer">${s.name}</a></div>
        ${
          s.snippet
            ? `<div class="supplier-snippet">${s.snippet}</div>`
            : ""
        }
      </td>
      <td>${s.source || ""}</td>
      <td>${s.estimated_price || ""}</td>
      <td>
        <div class="actions">
          <button class="action-btn" data-action="buy">Buy Now</button>
          <button class="action-btn secondary" data-action="inquire">Inquire</button>
          <button class="action-btn secondary" data-action="shopify">Connect to Shopify</button>
        </div>
      </td>
    `;

    tr.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        const action = btn.getAttribute("data-action");
        handleAction(action, s);
      });
    });

    resultsBody.appendChild(tr);
  }
}

async function refreshHistory() {
  try {
    const data = await fetchJSON("/history");
    renderHistory(data.items || []);
  } catch (e) {
    // history is non-critical; ignore errors
  }
}

async function runSearch() {
  const query = searchInput.value.trim();
  if (!query) {
    showToast("Please enter a product name.");
    return;
  }

  const mode = getSelectedMode();
  searchButton.disabled = true;
  setStatus("Running Nova Act search...");

  try {
    const data = await fetchJSON("/search", {
      method: "POST",
      body: JSON.stringify({ query, mode }),
    });
    currentResults = data.suppliers || [];
    renderResults();
    setStatus(
      `Found ${currentResults.length} suppliers via ${data.used_sites.join(
        " → "
      )}`
    );
    await refreshHistory();
  } catch (e) {
    console.error(e);
    setStatus("Search failed. Check backend logs or configuration.");
    showToast("Search failed.");
  } finally {
    searchButton.disabled = false;
  }
}

async function handleAction(kind, supplier) {
  try {
    let path;
    if (kind === "buy") path = "/actions/buy";
    else if (kind === "inquire") path = "/actions/inquire";
    else path = "/actions/connect-shopify";

    const res = await fetchJSON(path, {
      method: "POST",
      body: JSON.stringify({
        supplier_url: supplier.url,
        supplier_name: supplier.name,
      }),
    });
    showToast(res.message || "Action completed.");
  } catch (e) {
    console.error(e);
    showToast("Action failed.");
  }
}

searchButton.addEventListener("click", runSearch);
searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    runSearch();
  }
});

document.querySelectorAll(".results-table th[data-sort]").forEach((th) => {
  th.addEventListener("click", () => {
    const field = th.getAttribute("data-sort");
    if (!field) return;
    if (currentSort.field === field) {
      currentSort.direction = currentSort.direction === "asc" ? "desc" : "asc";
    } else {
      currentSort = { field, direction: "asc" };
    }
    renderResults();
  });
});

(async function init() {
  await refreshHistory();
})();

