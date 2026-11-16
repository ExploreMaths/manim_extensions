/*
 * SPDX-FileCopyrightText: 2026 ExploreMaths
 * SPDX-License-Identifier: MIT
 *
 * Attributes blocks rendered by autodoc (".. rubric:: Attributes" followed by
 * dl.py.attribute / dl.py.property entries) are styled as a bulleted list.
 * When a block contains exactly one entry the bullet is suppressed, matching
 * the "only one item, no bullet" requirement for the Parameters-style list.
 */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("p.rubric").forEach((rubric) => {
    const text = rubric.textContent.trim().replace(/\s+/g, " ").toLowerCase();
    if (text !== "attributes") return;
    const entries = [];
    let node = rubric.nextElementSibling;
    while (
      node &&
      node.tagName === "DL" &&
      node.classList.contains("py") &&
      (node.classList.contains("attribute") ||
        node.classList.contains("property"))
    ) {
      entries.push(node);
      node = node.nextElementSibling;
    }
    if (entries.length === 1) {
      entries[0].classList.add("attributes-single");
    }
  });
});
