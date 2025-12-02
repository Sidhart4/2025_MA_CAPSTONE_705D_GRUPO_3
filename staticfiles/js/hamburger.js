// Controla la apertura/cierre del menu movil del header
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btnMenu');
  const panel = document.getElementById('panelMovil');
  const navbar = document.getElementById('navbar');
  const root = document.body;
  const html = document.documentElement;
  const overlay = document.getElementById('mobileOverlay');

  if (!btn || !panel) {
    return;
  }

  const setOpenState = (isOpen) => {
    root.classList.toggle('mobile-open', isOpen);
    html.classList.toggle('mobile-open', isOpen);
    navbar?.classList.toggle('menu-open', isOpen);
    btn.classList.toggle('menu-btn--open', isOpen);
    btn.setAttribute('aria-expanded', String(isOpen));
    overlay?.setAttribute('aria-hidden', String(!isOpen));
  };

  const closePanel = () => setOpenState(false);

  btn.addEventListener('click', (evt) => {
    evt.stopPropagation();
    const nextState = !root.classList.contains('mobile-open');
    setOpenState(nextState);
  });

  panel.querySelectorAll('a, button').forEach((el) => {
    el.addEventListener('click', closePanel);
  });

  overlay?.addEventListener('click', (evt) => {
    evt.stopPropagation();
    closePanel();
  });

  document.addEventListener('click', (evt) => {
    const target = evt.target;
    if (!panel.contains(target) && !btn.contains(target)) {
      closePanel();
    }
  });

  document.addEventListener('keydown', (evt) => {
    if (evt.key === 'Escape') {
      closePanel();
    }
  });
});
