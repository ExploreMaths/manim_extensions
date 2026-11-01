// SPDX-FileCopyrightText: 2026 ExploreMaths
// SPDX-License-Identifier: MIT

/* Icon Gallery — search filter + copy-to-clipboard.
   Only activates when the gallery grid is present on the page. */
(function () {
    var grid = document.getElementById("ig-grid");
    if (!grid) {
        return;
    }
    var search = document.getElementById("ig-search");
    var count = document.getElementById("ig-count");
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".ig-card"));
    var total = parseInt(grid.getAttribute("data-total"), 10) || cards.length;
    var empty = document.createElement("div");
    empty.className = "ig-empty";
    empty.textContent = "No icons match your search.";
    grid.appendChild(empty);

    function refresh() {
        var q = search.value.trim().toLowerCase();
        var shown = 0;
        cards.forEach(function (card) {
            var hit = !q ||
                card.getAttribute("data-name").toLowerCase().indexOf(q) !== -1 ||
                card.getAttribute("data-codepoint").indexOf(q) !== -1;
            card.hidden = !hit;
            if (hit) {
                shown += 1;
            }
        });
        empty.hidden = shown !== 0;
        count.textContent = shown === total ? String(total) : shown + " / " + total;
    }

    search.addEventListener("input", refresh);
    count.textContent = String(total);

    grid.addEventListener("click", function (event) {
        var card = event.target.closest(".ig-card");
        if (!card) {
            return;
        }
        var name = card.getAttribute("data-name");
        var done = function () {
            card.classList.add("copied");
            card.title = "Copied: " + name;
            setTimeout(function () {
                card.classList.remove("copied");
            }, 900);
        };
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(name).then(done).catch(done);
        } else {
            done();
        }
    });
})();
