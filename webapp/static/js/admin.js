const dataCache = { items: null };

async function loadData() {
  const response = await fetch("/api/data");
  dataCache.items = await response.json();
}

async function submitForm(form) {
  const endpoint = form.dataset.endpoint;
  const formData = new FormData(form);
  if (endpoint) {
    const response = await fetch(endpoint, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      alert("Ошибка сохранения");
      return;
    }
    await loadData();
    alert("Сохранено");
    window.location.reload();
  }
}

async function deleteItem(type, id) {
  const endpoints = {
    services: "/api/services",
    pricing: "/api/prices",
    groups: "/api/groups",
    testimonials: "/api/testimonials",
  };
  const endpoint = endpoints[type];
  if (!endpoint) return;
  const formData = new FormData();
  formData.set("mode", "delete");
  formData.set("item_id", id);
  formData.set("name", "");
  formData.set("description", "");
  formData.set("duration", "");
  formData.set("price", "");
  formData.set("schedule", "");
  formData.set("format_name", "");
  formData.set("text", "");
  formData.set("tag", "");
  await fetch(endpoint, { method: "POST", body: formData });
  await loadData();
  window.location.reload();
}

function fillForm(form, item, type) {
  if (!item) return;
  form.querySelector('[name="item_id"]').value = item.id;
  form.querySelector('[name="name"]').value = item.name || "";
  const map = {
    services: ["description", "duration", "price"],
    pricing: ["description", "price"],
    groups: ["description", "schedule", "format_name", "price"],
    testimonials: ["text", "tag"],
  };
  (map[type] || []).forEach((field) => {
    const input = form.querySelector(`[name="${field}"]`);
    if (!input) return;
    const key = field === "format_name" ? "format" : field;
    input.value = item[key] || "";
  });
}

async function parseContent(form, mode) {
  const formData = new FormData(form);
  const endpoint = mode === "content" ? "/api/parser/content" : "/api/parser/reviews";
  const response = await fetch(endpoint, { method: "POST", body: formData });
  const resultEl = document.querySelector(`[data-result="${mode}"]`);
  if (!response.ok) {
    resultEl.textContent = "Ошибка парсинга.";
    return;
  }
  const data = await response.json();
  if (mode === "content") {
    resultEl.innerHTML = `
      <strong>Title:</strong> ${data.title || "-"}<br />
      <strong>Description:</strong> ${data.description || "-"}<br />
      <strong>H1:</strong> ${data.h1 || "-"}<br />
      <strong>Summary:</strong> ${data.summary || "-"}<br />
      <strong>Keywords:</strong> ${(data.keywords || []).join(", ") || "-"}
    `;
  } else {
    resultEl.innerHTML = data.items
      .map((item) => `<div>• ${item.text}</div>`)
      .join("");
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadData();

  document.querySelectorAll("form[data-endpoint]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const type = form.dataset.type;
      if (type) {
        const mode = form.querySelector('[name="item_id"]').value ? "update" : "create";
        const formData = new FormData(form);
        formData.set("mode", mode);
        const response = await fetch(form.dataset.endpoint, {
          method: "POST",
          body: formData,
        });
        if (!response.ok) {
          alert("Ошибка сохранения");
          return;
        }
        await loadData();
        window.location.reload();
        return;
      }
      await submitForm(form);
    });
  });

  document.querySelectorAll("[data-edit]").forEach((button) => {
    button.addEventListener("click", () => {
      const type = button.dataset.edit;
      const id = button.dataset.id;
      const items = dataCache.items?.[type] || [];
      const item = items.find((entry) => entry.id === id);
      const form = document.querySelector(`form[data-type="${type}"]`);
      if (form) {
        fillForm(form, item, type);
      }
    });
  });

  document.querySelectorAll("[data-delete]").forEach((button) => {
    button.addEventListener("click", () => {
      const type = button.dataset.delete;
      const id = button.dataset.id;
      if (confirm("Удалить элемент?")) {
        deleteItem(type, id);
      }
    });
  });

  document.querySelectorAll("form[data-parser]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const mode = form.dataset.parser;
      await parseContent(form, mode);
    });
  });
});
