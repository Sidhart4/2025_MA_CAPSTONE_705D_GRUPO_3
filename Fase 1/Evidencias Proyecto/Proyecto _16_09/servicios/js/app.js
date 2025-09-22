
  (function(){
    const chips = document.querySelectorAll('.servicios-page .chip');
    const cards = document.querySelectorAll('.servicios-page .servicio-card');
    const search = document.getElementById('buscaServicio');

    function filtrar(){
      const activo = document.querySelector('.servicios-page .chip.active')?.dataset.cat || 'todos';
      const q = (search?.value || '').toLowerCase().trim();

      cards.forEach(card => {
        const cat = card.dataset.cat;
        const texto = (card.textContent || '').toLowerCase();
        const porCat = (activo === 'todos' || cat === activo);
        const porTexto = (q === '' || texto.includes(q));
        card.style.display = (porCat && porTexto) ? '' : 'none';
      });
    }

    chips.forEach(ch => {
      ch.addEventListener('click', () => {
        chips.forEach(c => c.classList.remove('active'));
        ch.classList.add('active');
        filtrar();
      });
    });

    if (search){
      search.addEventListener('input', filtrar);
    }

    // Primera pasada
    filtrar();
  })();

