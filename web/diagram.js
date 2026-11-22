/* Standalone browser view for the computed project report. */
window.drawProjectView = function (host, report, input) {
  "use strict";
  function el(tag, text, css) {
    const item = document.createElement(tag);
    if (text != null) item.textContent = String(text);
    if (css) item.style.cssText = css;
    return item;
  }
  const figure = el("figure", null, "box-sizing:border-box;margin:12px 0 16px;padding:12px 14px;border-radius:9px;background:#172329;color:#f4f5f2;max-height:210px;overflow:auto;font:13px/1.35 system-ui,sans-serif;text-align:left");
  const head = el("figcaption", "Mix timeline by cue priority", "font-size:15px;font-weight:700;letter-spacing:-.015em;color:#d5c4fd;margin-bottom:7px");
  figure.append(head);
  host.replaceChildren(figure);
  const rows = Array.isArray(report && report.rows) ? report.rows : [];
  if (!rows.length) {
    figure.append(el("p", "No findings to display.", "margin:0"));
    return;
  }

  const events = new Map((input.cues || []).map(c => [c.id.trim(),c]));
  const shown = rows.slice(0,6).map(row => ({row,c:events.get(row.Cue)})).filter(e=>e.c);
  if (!shown.length) return;
  const begin = Math.min(...shown.map(e=>e.c.start));
  const end = Math.max(...shown.map(e=>e.c.start+e.c.duration));
  const colors = ["","#7c9e9b","#8ebcaf","#9acde8","#d1b5f5","#f6af80"];
  for (const {row,c} of shown) {
    const lane = el("div", null, "display:grid;grid-template-columns:minmax(70px,25%) minmax(0,1fr) 25px;align-items:center;gap:6px;margin:3px 0");
    const name = el("span", row.Cue, "font:11px system-ui;white-space:nowrap;overflow:hidden;text-overflow:ellipsis");
    name.title = row.Cue+" · "+row.Bus;
    const bar = el("div", null, "position:relative;height:12px;overflow:hidden;border-radius:2px;background:#344249");
    const part = el("div", null, "position:absolute;top:1px;bottom:1px;border-radius:2px;min-width:1px;background:"+colors[row.Priority]+";left:"+((c.start-begin)/(end-begin)*100)+"%;width:"+(c.duration/(end-begin)*100)+"%");
    bar.setAttribute("aria-label", row.Cue+" on "+row.Bus+", "+c.start+"–"+(c.start+c.duration).toFixed(3)+" seconds. "+row["Mix note"]);
    part.title = row["Mix note"];
    bar.append(part); lane.append(name,bar,el("small","P"+row.Priority,"font:10px ui-monospace,monospace;text-align:right"));
    figure.append(lane);
  }
  figure.append(el("div","Source "+begin.toFixed(2)+"–"+end.toFixed(2)+" s · higher P = higher priority · first "+shown.length+" cues", "font-size:10px;color:#c5d2d0;margin-top:5px"));

};
