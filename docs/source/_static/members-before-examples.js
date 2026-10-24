/* Move auto-listed attribute/property members above the "Examples"
   rubric of their class block.  autodoc renders the class docstring
   (description + Examples) first and the collected members after it,
   so a property such as ``Array.values`` lands below the example video.
   Moving attributes first, then properties, right before the Examples
   rubric makes them read as part of the attribute block — properties
   directly after the attributes.  Order is preserved by inserting every
   block at the same anchor. */
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("dl.py.class").forEach(function (dl) {
    var dd = dl.querySelector(":scope > dd");
    if (!dd) return;
    var rubrics = dd.querySelectorAll(":scope > p.rubric");
    var anchor = null;
    for (var i = 0; i < rubrics.length; i++) {
      if (rubrics[i].textContent.trim() === "Examples") {
        anchor = rubrics[i];
        break;
      }
    }
    if (!anchor) return;
    var blocks = dd.querySelectorAll(
      ":scope > dl.py.attribute, :scope > dl.py.property"
    );
    Array.prototype.forEach.call(blocks, function (b) {
      dd.insertBefore(b, anchor);
    });
  });
});
