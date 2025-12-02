// Loader + scroll animations
(function () {
  const loader = document.getElementById('pageLoader');
  const markLoaded = () => {
    document.documentElement.classList.add('page-loaded');
    document.body.classList.add('page-loaded');
    if (loader) {
      loader.setAttribute('aria-hidden', 'true');
    }
  };

  window.addEventListener('load', () => {
    window.setTimeout(markLoaded, 200);
  });
  // Fallback in case load never fires (cached resources, etc.)
  window.setTimeout(markLoaded, 4000);

  const revealEls = document.querySelectorAll('[data-reveal]');
  if (!revealEls.length) {
    return;
  }

  const applyDelay = (el) => {
    const { revealDelay } = el.dataset;
    if (revealDelay) {
      const delay = parseInt(revealDelay, 10);
      if (!Number.isNaN(delay)) {
        el.style.setProperty('--reveal-delay', `${delay}ms`);
      }
    }
  };

  const showElement = (el) => {
    el.classList.add('is-visible');
  };

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            showElement(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.15,
        rootMargin: '0px 0px -5% 0px',
      }
    );

    revealEls.forEach((el) => {
      applyDelay(el);
      observer.observe(el);
    });
  } else {
    revealEls.forEach((el) => {
      applyDelay(el);
      showElement(el);
    });
  }

  const flashes = document.querySelectorAll('[data-flash]');
  const hideAlert = (el) => {
    if (!el || el.classList.contains('is-hidden')) return;
    el.classList.add('is-hidden');
    window.setTimeout(() => {
      if (el.parentNode) {
        el.parentNode.removeChild(el);
      }
    }, 350);
  };

  flashes.forEach((flash, index) => {
    const btn = flash.querySelector('[data-flash-close]');
    if (btn) {
      btn.addEventListener('click', (evt) => {
        evt.preventDefault();
        hideAlert(flash);
      });
    }
    window.setTimeout(() => hideAlert(flash), 6000 + index * 300);
  });
})();
