(() => {
function parseDomain(desc) {
  const m = desc.match(/^\[([^\]]+)\]/);
  return m ? m[1] : null;
}
function parseTitle(desc) {
  return desc.replace(/^\[[^\]]+\]\s*/, "");
}

const TORONTO_TZ = "America/Toronto";
function formatTorontoTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString("en-CA", {
    timeZone: TORONTO_TZ,
    hour: "2-digit",
    minute: "2-digit",
  });
}
function formatTorontoDateTime(timestamp) {
  return new Date(timestamp).toLocaleString("en-CA", {
    timeZone: TORONTO_TZ,
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function scrollToSection(sectionId) {
  requestAnimationFrame(() => {
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
}

window.ComplianceUI.parseDomain = parseDomain;
window.ComplianceUI.parseTitle = parseTitle;
window.ComplianceUI.formatTorontoTime = formatTorontoTime;
window.ComplianceUI.formatTorontoDateTime = formatTorontoDateTime;
window.ComplianceUI.scrollToSection = scrollToSection;
})();
