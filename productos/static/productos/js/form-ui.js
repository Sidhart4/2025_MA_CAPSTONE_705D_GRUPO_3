(function () {
  const $ = (s, r=document) => r.querySelector(s);

  const nameIn  = $('#id_nombre')   || $('[name="nombre"]');
  const priceIn = $('#id_precio')   || $('[name="precio"]');
  const oldIn   = $('#id_precio_anterior') || $('[name="precio_anterior"]');
  const stockIn = $('#id_stock')    || $('[name="stock"]');
  const descIn  = $('#id_descripcion') || $('[name="descripcion"]');
  const descCount = $('#descCount');

  const prevName  = $('#prevName');
  const prevPrice = $('#prevPrice');
  const prevStock = $('#prevStock');
  const prevImg   = $('#prevImg');

  const drop = $('#dropArea');
  const file = $('#id_imagen') || (drop && drop.querySelector('input[type=file]'));
  const mini = $('#miniHolder');
  const miniImg = $('#miniImg');

  // aseguramos placeholder para activar :placeholder-shown
  [nameIn, priceIn, oldIn, stockIn, descIn].filter(Boolean).forEach(el => el.placeholder = ' ');

  // formato CLP con miles
  const nf = new Intl.NumberFormat('es-CL');
  function onlyDigits(v){ return (v||'').toString().replace(/[^\d]/g,''); }
  function fmt(el){
    if (!el) return;
    const raw = onlyDigits(el.value);
    el.value = raw ? nf.format(parseInt(raw,10)) : '';
  }
  [priceIn, oldIn, stockIn].filter(Boolean).forEach(el=>{
    el.addEventListener('blur', ()=> fmt(el));
    el.addEventListener('focus', ()=> el.select());
  });

  // preview vivo
  nameIn?.addEventListener('input', ()=> prevName.textContent = nameIn.value || 'Nombre del producto');
  priceIn?.addEventListener('input', ()=> prevPrice.textContent = priceIn.value ? ('$'+priceIn.value) : '$0');
  stockIn?.addEventListener('input', ()=> prevStock.textContent = 'Stock: ' + (stockIn.value||'0'));
  descIn?.addEventListener('input', ()=> descCount && (descCount.textContent = descIn.value.length));

  // uploader + miniatura + imagen grande
  if (drop && file){
    const toggleDrag = v => drop.classList.toggle('drag', v);
    ['dragenter','dragover'].forEach(ev => drop.addEventListener(ev, e=>{e.preventDefault(); toggleDrag(true);}));
    ['dragleave','drop'].forEach(ev => drop.addEventListener(ev, e=>{e.preventDefault(); toggleDrag(false);}));
    drop.addEventListener('drop', e => { if(e.dataTransfer.files[0]) file.files = e.dataTransfer.files; file.dispatchEvent(new Event('change')); });
    file.addEventListener('change', ()=>{
      const f = file.files && file.files[0];
      if (!f) return;
      const url = URL.createObjectURL(f);
      prevImg.src = url;
      if (mini && miniImg){ mini.hidden = false; miniImg.src = url; }
    });
  }

  // validación suave
  const form = $('#productForm');
  form?.addEventListener('submit', (e)=>{
    const errs = [];
    const priceVal = parseInt(onlyDigits(priceIn?.value),10) || 0;
    const stockVal = parseInt(onlyDigits(stockIn?.value),10) || 0;
    if (!nameIn?.value.trim()) errs.push('nombre');
    if (priceVal < 0) errs.push('precio');
    if (stockVal < 0) errs.push('stock');
    if (errs.length){
      e.preventDefault();
      [priceIn, stockIn].forEach(fmt);
      (!nameIn?.value.trim()) && nameIn.focus();
    }
  });

  // iniciales
  [priceIn, oldIn, stockIn].forEach(fmt);
  if (descIn) descCount.textContent = descIn.value.length;
})();
