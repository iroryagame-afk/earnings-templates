(function () {
  var errors = [];

  window.addEventListener("error", function (ev) {
    errors.push(String((ev && ev.message) || "error"));
  });
  window.addEventListener("unhandledrejection", function (ev) {
    errors.push(String((ev && ev.reason) || "rejection"));
  });

  function collect(phase) {
    var root = document.querySelector("[data-accept-root]");
    var overflows = [];
    if (!root) {
      errors.push("missing data-accept-root");
    } else {
      var nodes = root.querySelectorAll("*");
      for (var i = 0; i < nodes.length; i += 1) {
        var el = nodes[i];
        if (el.id === "accept-report") continue;
        if (!el.clientWidth || !el.clientHeight) continue;
        var extraW = el.scrollWidth - el.clientWidth;
        var extraH = el.scrollHeight - el.clientHeight;
        var style = window.getComputedStyle(el);
        var clipsY = style.overflowY === "hidden" || style.overflowY === "clip" || style.overflowY === "auto" || style.overflowY === "scroll";
        var horizontal = extraW > 2;
        var verticalClip = extraH > 2 && clipsY;
        if (horizontal || verticalClip) {
          overflows.push({
            tag: el.tagName,
            cls: String(el.className || "").slice(0, 80),
            extraW: extraW,
            extraH: extraH,
            text: String(el.innerText || "").replace(/\s+/g, " ").slice(0, 48)
          });
        }
      }
    }

    var box = root ? root.getBoundingClientRect() : { width: 0, height: 0, left: 0 };
    var fonts = [];
    if (document.fonts) {
      document.fonts.forEach(function (face) {
        fonts.push(face.family + ":" + face.status);
      });
    }
    var text = document.body ? document.body.innerText : "";
    var report = {
      phase: phase,
      demo: text.indexOf("演示数据") !== -1,
      fictional: text.indexOf("虚构") !== -1,
      synthetic: text.indexOf("合成") !== -1,
      pageWidth: Math.round(box.width),
      pageHeight: Math.round(box.height),
      pageLeft: Math.round(box.left),
      innerWidth: window.innerWidth,
      innerHeight: window.innerHeight,
      overflows: overflows,
      errors: errors.slice(),
      fonts: fonts,
      fontStatus: document.fonts ? document.fonts.status : "unknown"
    };
    var pre = document.getElementById("accept-report");
    if (pre) pre.textContent = JSON.stringify(report);
    document.documentElement.setAttribute("data-accept-phase", phase);
  }

  function settle() {
    collect("fonts-ready");
  }

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(settle).catch(function (err) {
      errors.push(String(err));
      collect("fonts-error");
    });
  } else {
    settle();
  }
  window.addEventListener("load", function () {
    collect("load");
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(settle);
    }
  });
})();
