window.addEventListener("load", function () {
    const colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const diagrams = document.querySelectorAll("object.inheritance.graphviz");

    function injectStyle(diagram) {
        const svgRoot = diagram.contentDocument && diagram.contentDocument.firstElementChild;
        if (!svgRoot) {
            return null;
        }
        const style = document.createElementNS("http://www.w3.org/2000/svg", "style");
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
                    setColorScheme(colorSchemeQuery);
                }
            });
        } else {
            styleElements.push(style);
        }
    }

    function setColorScheme(e) {
        let colors, additions = "";
        if (e.matches) {
            // Dark
            colors = {
                text: "#e07a5f",
                box: "#383838",
                edge: "#d0d0d0",
                background: "#131416"
            };
        } else {
            // Light
            colors = {
                text: "#e07a5f",
                box: "#fff",
                edge: "#413c3c",
                background: "#ffffff"
            };
            additions = `
            .node polygon {
                filter: drop-shadow(0 1px 3px #0002);
            }
            `
        }
        for (const style of styleElements) {
            style.textContent = `
                svg {
                    background-color: ${colors.background};
                }

                .node text {
                    fill: ${colors.text};
                }

                .node polygon {
                    fill: ${colors.box};
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

    setColorScheme(colorSchemeQuery);
    colorSchemeQuery.addEventListener("change", setColorScheme);
});
