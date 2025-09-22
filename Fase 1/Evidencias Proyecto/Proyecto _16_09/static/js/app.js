(() => {
  const carousel = document.querySelector('.p-carousel');
  if (!carousel) return;

  const track = carousel.querySelector('#destacadosTrack');
  const prev  = carousel.querySelector('.p-nav.prev');
  const next  = carousel.querySelector('.p-nav.next');
  const dotsC = document.querySelector('#destacadosDots');

  const cards = Array.from(track.children);
  if (!cards.length) return;

  let perView = getPerView();
  let page = 0;
  let pageCount = getPageCount();

  function getPerView() {
    if (window.matchMedia('(max-width:680px)').matches)  return 1;
    if (window.matchMedia('(max-width:1100px)').matches) return 2;
    return 3;
  }

  function getPageCount() {
    return Math.max(1, Math.ceil(cards.length / perView));
  }

  function getPageOffsetPx(p) {
    const firstIndex = p * perView;
    const base = cards[0].offsetLeft;
    const first = cards[firstIndex] ?? cards[cards.length - 1];
    return (first.offsetLeft - base);
  }

  function update() {
    page = Math.max(0, Math.min(page, pageCount - 1));
    track.style.transform = `translateX(${-getPageOffsetPx(page)}px)`;
    prev.disabled = page === 0;
    next.disabled = page === pageCount - 1;
    updateDots();
  }

  function buildDots() {
    if (!dotsC) return;
    dotsC.innerHTML = '';
    for (let i = 0; i < pageCount; i++) {
      const dot = document.createElement('span');
      dot.className = 'p-dot' + (i === page ? ' is-active' : '');
      dot.addEventListener('click', () => { page = i; update(); });
      dotsC.appendChild(dot);
    }
  }

  function updateDots() {
    if (!dotsC) return;
    dotsC.querySelectorAll('.p-dot').forEach((d, i) => {
      d.classList.toggle('is-active', i === page);
    });
  }

  next.addEventListener('click', () => { if (page < pageCount - 1) { page++; update(); } });
  prev.addEventListener('click', () => { if (page > 0) { page--; update(); } });

  let resizeRAF;
  window.addEventListener('resize', () => {
    if (resizeRAF) cancelAnimationFrame(resizeRAF);
    resizeRAF = requestAnimationFrame(() => {
      const n = getPerView();
      if (n !== perView) {
        perView = n;
        pageCount = getPageCount();
        if (page > pageCount - 1) page = pageCount - 1;
        buildDots();
      }
      update();
    });
  });

  // init
  pageCount = getPageCount();
  buildDots();
  update();
})();
