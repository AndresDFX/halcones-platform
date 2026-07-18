// Utilidades ligeras de UI (sin dependencias externas).

// Confirmación para acciones destructivas
document.addEventListener('submit', function (e) {
  const f = e.target;
  if (f.dataset.confirm && !window.confirm(f.dataset.confirm)) {
    e.preventDefault();
  }
});

// Mostrar/ocultar bloques (formularios inline)
function toggle(id, btn) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.display = (el.style.display === 'none' || !el.style.display) ? 'block' : 'none';
}

// Autocompletar login demo
function fillLogin(email, pass) {
  const e = document.querySelector('input[name=email]');
  const p = document.querySelector('input[name=password]');
  if (e && p) { e.value = email; p.value = pass; }
}

// Formateo en vivo de montos en COP mientras se escribe
document.addEventListener('input', function (e) {
  if (e.target.classList && e.target.classList.contains('money')) {
    let v = e.target.value.replace(/\D/g, '');
    if (v) e.target.value = parseInt(v, 10).toLocaleString('es-CO');
  }
});

// PWA: registro del service worker (instalable / offline).
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {});
  });
}
