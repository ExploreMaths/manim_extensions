/* nbcell: show an inset edge shadow on the input/output areas only while
 * content is clipped on that side, and keep everything aligned after
 * fonts load. Shadow styling lives in nbcell.css (.has-left/.has-right). */
(function () {
    function update(el) {
        var max = el.scrollWidth - el.clientWidth;
        el.classList.toggle("has-left", el.scrollLeft > 1);
        el.classList.toggle("has-right", el.scrollLeft < max - 1);
    }

    function refresh() {
        document
            .querySelectorAll(
                "div.nbinput.container div.input_area, div.nboutput.container div.output_area"
            )
            .forEach(function (el) {
                update(el);
                if (!el.dataset.nbcellBound) {
                    el.dataset.nbcellBound = "1";
                    el.addEventListener("scroll", function () {
                        update(el);
                    }, { passive: true });
                }
            });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", refresh);
    } else {
        refresh();
    }
    window.addEventListener("load", refresh);
    window.addEventListener("resize", refresh);
})();
