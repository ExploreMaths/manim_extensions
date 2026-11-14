// SPDX-FileCopyrightText: 2026 ExploreMaths
// SPDX-License-Identifier: MIT

/* Keep the compact summary in the signature. On expand, move the full repr
   into the same .property span instead of rendering a separate code block. */
(() => {
  const init = () => {
    document.querySelectorAll(".constant-value-payload").forEach((payload) => {
      const entry = payload.closest("dl.py.data");
      const property = entry && entry.querySelector("dt .property");
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
      property.appendChild(full);
      payload.remove();

      toggle.addEventListener("click", () => {
        summary.hidden = true;
        full.hidden = false;
      });
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
