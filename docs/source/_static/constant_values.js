// SPDX-FileCopyrightText: 2026 ExploreMaths
// SPDX-License-Identifier: MIT

/* Keep the compact summary in the signature. On expand, move the full repr
   into the same .property span instead of rendering a separate code block. */
(() => {
  const init = () => {
    document.querySelectorAll(".constant-value-payload").forEach((payload) => {
      const entry = payload.closest("dl.py.data");
      const dt = entry && entry.querySelector("dt");
      const property = dt && dt.querySelector(".property");
      const fullValue = payload.querySelector(".constant-value-full-value");
      if (!property || !fullValue) {
        return;
      }

      const summary = document.createElement("span");
      summary.className = "constant-value-summary";
      while (property.firstChild) {
        summary.appendChild(property.firstChild);
      }

      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "constant-value-toggle";
      toggle.textContent = "Show";
      toggle.title = "Show full value";
      toggle.setAttribute("aria-label", "Show full value");
      summary.appendChild(toggle);
      property.appendChild(summary);

      const full = document.createElement("span");
      full.className = "constant-value-full";
      full.hidden = true;
      full.appendChild(fullValue);
      const close = payload.querySelector(".constant-value-close");
      if (close) {
        full.appendChild(close);
      }
      property.appendChild(full);
      payload.remove();

      toggle.addEventListener("click", () => {
        summary.hidden = true;
        full.hidden = false;
        dt.classList.add("constant-value-expanded");
      });

      if (close) {
        close.addEventListener("click", () => {
          full.hidden = true;
          summary.hidden = false;
          dt.classList.remove("constant-value-expanded");
          toggle.focus();
        });
      }
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
