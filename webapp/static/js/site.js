const modal = document.getElementById("lead-modal");
const openButtons = document.querySelectorAll("[data-open]");
const closeButtons = document.querySelectorAll("[data-close]");

openButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    modal?.classList.add("show");
  });
});

closeButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    modal?.classList.remove("show");
  });
});

modal?.addEventListener("click", (event) => {
  if (event.target === modal) {
    modal.classList.remove("show");
  }
});

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener("click", (event) => {
    const targetId = link.getAttribute("href");
    const target = targetId ? document.querySelector(targetId) : null;
    if (target) {
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});
