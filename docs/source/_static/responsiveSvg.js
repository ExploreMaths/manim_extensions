window.addEventListener("load", function () {
    const diagrams = document.querySelectorAll("object.inheritance.graphviz");

    function hasPythonNodes(diagram) {
        const svgDoc = diagram.contentDocument;
        if (!svgDoc) return false;
        const polygons = svgDoc.getElementsByTagNameNS("http://www.w3.org/2000/svg", "polygon");
        for (const p of polygons) {
            const fill = (p.getAttribute("fill") || "").toLowerCase();
            if (fill === "#ffffff" || fill === "#fff" || fill === "white") {
                return true;
            }
        }
        return false;
    }

    function addLegend(diagram, includePython) {
        if (!diagram.parentNode || diagram.parentNode.querySelector(".inheritance-legend")) return;
        const legend = document.createElement("div");
        legend.className = "inheritance-legend";
        const pythonItem = includePython ? `
            <span class="legend-item">
                <span class="legend-swatch python-swatch"></span>
                <span class="legend-label">Python</span>
            </span>
        ` : "";
        legend.innerHTML = `
            ${pythonItem}
            <span class="legend-item">
                <span class="legend-swatch manim-swatch"></span>
                <span class="legend-label">Manim</span>
            </span>
            <span class="legend-item">
                <span class="legend-swatch extensions-swatch"></span>
                <span class="legend-label">Manim Extensions</span>
            </span>
        `;
        diagram.parentNode.insertBefore(legend, diagram);
    }

    function updateLegend(diagram) {
        const existing = diagram.parentNode ? diagram.parentNode.querySelector(".inheritance-legend") : null;
        if (!existing) {
            addLegend(diagram, hasPythonNodes(diagram));
            return;
        }
        if (hasPythonNodes(diagram) && !existing.querySelector(".python-swatch")) {
            const pythonItem = document.createElement("span");
            pythonItem.className = "legend-item";
            pythonItem.innerHTML = `
                <span class="legend-swatch python-swatch"></span>
                <span class="legend-label">Python</span>
            `;
            existing.insertBefore(pythonItem, existing.firstChild);
        }
    }

    for (const diagram of diagrams) {
        addLegend(diagram, false);
    }

    // Determine the currently-active color scheme. Furo stores its theme choice
    // in localStorage["theme"] ("auto" | "dark" | "light") and reflects the
    // effective value on <body data-theme="...">. Prefer the real state over the
    // OS-level prefers-color-scheme so manual theme toggles are honoured.
    function getDark() {
        const bodyTheme =
            document.body && document.body.getAttribute("data-theme");
        if (bodyTheme === "dark") return true;
        if (bodyTheme === "light") return false;

        const stored = localStorage.getItem("theme");
        if (stored === "dark") return true;
        if (stored === "light") return false;

        // auto (or unset) -> follow the OS preference.
        return window.matchMedia("(prefers-color-scheme: dark)").matches;
    }

    function injectStyle(diagram) {
        const svgRoot =
            diagram.contentDocument && diagram.contentDocument.firstElementChild;
        if (!svgRoot) {
            return null;
        }
        const style = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "style"
        );
        svgRoot.appendChild(style);
        return style;
    }

    const styleElements = [];
    for (const diagram of diagrams) {
        let style = injectStyle(diagram);
        if (!style) {
            diagram.addEventListener("load", function () {
                style = injectStyle(diagram);
                if (style) {
                    styleElements.push(style);
                    setColorScheme();
                }
                updateLegend(diagram);
            });
        } else {
            styleElements.push(style);
            updateLegend(diagram);
        }
    }

    function setColorScheme() {
        let colors, additions = "";
        if (getDark()) {
            colors = {
                edge: "#d0d0d0",
                background: "#131416"
            };
        } else {
            colors = {
                edge: "#413c3c",
                background: "#ffffff"
            };
            additions = `
            .node polygon {
                filter: drop-shadow(0 1px 3px #0002);
            }
            `;
        }
        for (const style of styleElements) {
            style.textContent = `
                svg {
                    background-color: ${colors.background};
                }

                .edge polygon {
                    fill: ${colors.edge};
                    stroke: ${colors.edge};
                }

                .edge path {
                    stroke: ${colors.edge};
                }
                ${additions}
            `;
        }
    }

    setColorScheme();

    // React to Furo's manual theme toggle (sets / removes data-theme on <body>).
    if (document.body) {
        const observer = new MutationObserver(setColorScheme);
        observer.observe(document.body, {
            attributes: true,
            attributeFilter: ["data-theme"],
        });
    }
    // React to OS-level auto-theme changes.
    window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", setColorScheme);
});