// ============ Utilidades ============
const $ = (s, ctx=document) => ctx.querySelector(s);
const $$ = (s, ctx=document) => Array.from(ctx.querySelectorAll(s));
const fmtCLP = n => new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n);

// ============ Offcanvas ============
(function offcanvas(){
  const openBtn = $('.open-btn');
  const nav = $('.offcanvas-nav');
  const overlay = $('.overlay');
  const closeBtn = $('.close-btn');
  const open = () => { nav.style.width = '280px'; overlay.style.display = 'block'; };
  const close = () => { nav.style.width = '0'; overlay.style.display = 'none'; };
  openBtn && openBtn.addEventListener('click', open);
  closeBtn && closeBtn.addEventListener('click', close);
  overlay && overlay.addEventListener('click', close);
})();

// ============ Productos / Render inicial ============
const grid = $('#gridProductos');
let allProducts = $$('.producto', grid);

// Colocar precios + badge ahorro
allProducts.forEach(card => {
  const price = Number(card.dataset.price || 0);
  const old = Number(card.dataset.oldPrice || 0);
  const precioEl = $('.precio', card);
  let html = `<span class="actual">${fmtCLP(price)}</span>`;
  if (old && old > price) {
    html += ` <span class="tachado">${fmtCLP(old)}</span>`;
    const ahorro = old - price;
    const badge = $('.descuento', card);
    badge.textContent = `Ahorrar ${fmtCLP(ahorro)}`;
    badge.style.display = 'inline-block';
  }
  precioEl.innerHTML = html;

  // Deshabilitar botón si está agotado
  if (card.dataset.stock === 'out') {
    const btn = $('.agregar-carrito', card);
    btn.setAttribute('disabled', 'disabled');
    btn.textContent = 'Agotado';
  }
});

// ============ Filtros / Orden / Búsqueda ============
const resumen = $('#resumen-listado');
const sortBy = $('#sortBy');
const pageSizeSel = $('#pageSize');
const searchInput = $('#search');

let state = {
  filters: {
    stock: new Set(['in']), // por defecto solo en stock
    categories: new Set(['alimentos','medicamentos','accesorios','camas']),
    price: 'all'
  },
  search: '',
  sort: 'popular',
  page: 1,
  pageSize: Number(pageSizeSel.value)
};

// Acordeones de filtros
$$('.filtro-btn').forEach(btn => {
  btn.addEventListener('click', () => btn.parentElement.classList.toggle('active'));
});
// Abrir todos por defecto
$$('.filtro').forEach(f => f.classList.add('active'));

// Eventos de filtros
$$('.f-check').forEach(chk => {
  chk.addEventListener('change', () => {
    const type = chk.dataset.filter;
    if (type === 'stock') {
      chk.checked ? state.filters.stock.add(chk.value) : state.filters.stock.delete(chk.value);
    } else if (type === 'category') {
      chk.checked ? state.filters.categories.add(chk.value) : state.filters.categories.delete(chk.value);
    }
    state.page = 1;
    apply();
  });
});

$$('.f-radio').forEach(radio => {
  radio.addEventListener('change', () => {
    if (radio.checked) {
      state.filters.price = radio.value;
      state.page = 1;
      apply();
    }
  });
});

sortBy.addEventListener('change', () => { state.sort = sortBy.value; state.page = 1; apply(); });
pageSizeSel.addEventListener('change', () => { state.pageSize = Number(pageSizeSel.value); state.page = 1; apply(); });
searchInput.addEventListener('input', e => { state.search = e.target.value.trim().toLowerCase(); state.page = 1; apply(); });

// Lógica de filtrado
function pasaFiltros(card){
  const price = Number(card.dataset.price || 0);
  const cat = card.dataset.category;
  const stock = card.dataset.stock;

  // Stock
  if (state.filters.stock.size && !state.filters.stock.has(stock)) return false;

  // Categoría
  if (state.filters.categories.size && !state.filters.categories.has(cat)) return false;

  // Precio
  switch (state.filters.price) {
    case 'lt10000': if (!(price < 10000)) return false; break;
    case '10k-20k': if (!(price >= 10000 && price <= 20000)) return false; break;
    case 'gt20000': if (!(price > 20000)) return false; break;
  }

  // Búsqueda por nombre o marca
  if (state.search) {
    const txt = (card.dataset.name + ' ' + card.dataset.brand).toLowerCase();
    if (!txt.includes(state.search)) return false;
  }
  return true;
}

// Orden
function sortNodes(nodes){
  const arr = nodes.slice();
  const getName = n => (n.dataset.name || '').toLowerCase();
  const getPrice = n => Number(n.dataset.price || 0);
  const getPop = n => Number(n.dataset.popular || 0);

  switch (state.sort) {
    case 'price-asc':  arr.sort((a,b)=> getPrice(a)-getPrice(b)); break;
    case 'price-desc': arr.sort((a,b)=> getPrice(b)-getPrice(a)); break;
    case 'name-asc':   arr.sort((a,b)=> getName(a).localeCompare(getName(b),'es')); break;
    default:           arr.sort((a,b)=> getPop(b)-getPop(a)); // popular
  }
  return arr;
}

// Paginación
const prevBtn = $('#prevPage');
const nextBtn = $('#nextPage');
const pageInfo = $('#pageInfo');

prevBtn.addEventListener('click', ()=>{ if (state.page>1){ state.page--; apply(); } });
nextBtn.addEventListener('click', ()=>{ state.page++; apply(); });

function paginate(nodes){
  const total = nodes.length;
  const pages = Math.max(1, Math.ceil(total / state.pageSize));
  if (state.page > pages) state.page = pages;

  const start = (state.page - 1) * state.pageSize;
  const end   = start + state.pageSize;
  prevBtn.disabled = state.page <= 1;
  nextBtn.disabled = state.page >= pages;
  pageInfo.textContent = `Página ${state.page} de ${pages}`;

  const rango = nodes.slice(start, end);
  const desde = total===0 ? 0 : start + 1;
  const hasta = Math.min(end, total);
  resumen.textContent = `Mostrando ${desde} – ${hasta} de ${total} productos`;

  return rango;
}

// Aplicar todo
function apply(){
  // Filtrar
  const visibles = allProducts.filter(pasaFiltros);
  // Ordenar
  const ordenados = sortNodes(visibles);
  // Paginar
  const pagina = paginate(ordenados);

  // Limpiar grid y reinsertar solo los elementos de la página actual
  grid.innerHTML = '';
  pagina.forEach(n => grid.appendChild(n));
}
apply();

// ============ Carrito ============
const btnCarrito = $('#btn-carrito');
const drawer = $('#carritoDrawer');
const cOverlay = $('#carritoOverlay');
const cerrarCarrito = $('#cerrarCarrito');
const listaCarrito = $('#lista-carrito');
const totalEl = $('#total');
const vaciarBtn = $('#vaciar-carrito');
const comprarBtn = $('#comprar');
const cartCount = $('#cartCount');

let cart = JSON.parse(localStorage.getItem('cart') || '[]');

function abrirCarrito(){ drawer.classList.add('abierto'); cOverlay.classList.add('activo'); btnCarrito.setAttribute('aria-expanded','true'); drawer.setAttribute('aria-hidden','false'); cOverlay.setAttribute('aria-hidden','false'); }
function cerrar(){ drawer.classList.remove('abierto'); cOverlay.classList.remove('activo'); btnCarrito.setAttribute('aria-expanded','false'); drawer.setAttribute('aria-hidden','true'); cOverlay.setAttribute('aria-hidden','true'); }

btnCarrito.addEventListener('click', abrirCarrito);
cerrarCarrito.addEventListener('click', cerrar);
cOverlay.addEventListener('click', cerrar);

// Agregar al carrito
grid.addEventListener('click', e => {
  const btn = e.target.closest('.agregar-carrito');
  if (!btn) return;
  const card = btn.closest('.producto');
  const id = card.dataset.name; // simple id por nombre
  const price = Number(card.dataset.price || 0);
  const name = card.dataset.name;

  const idx = cart.findIndex(i => i.id === id);
  if (idx >= 0) cart[idx].qty += 1;
  else cart.push({ id, name, price, qty: 1 });

  saveCart();
  renderCart();
});

// Render carrito
function renderCart(){
  listaCarrito.innerHTML = '';
  let suma = 0, unidades = 0;

  cart.forEach((item, i) => {
    const li = document.createElement('li');
    li.className = 'carrito-item';

    li.innerHTML = `
      <div class="ci-info">
        <div class="ci-nombre">${item.name}</div>
        <div class="ci-precio">${fmtCLP(item.price)} × 
          <button class="menos" aria-label="Restar unidad">–</button>
          <span class="qty">${item.qty}</span>
          <button class="mas" aria-label="Sumar unidad">+</button>
        </div>
      </div>
      <button class="eliminar" aria-label="Quitar del carrito">🗑</button>
    `;

    // Eventos cantidad / eliminar
    li.querySelector('.menos').addEventListener('click', ()=>{
      item.qty = Math.max(1, item.qty-1); saveCart(); renderCart();
    });
    li.querySelector('.mas').addEventListener('click', ()=>{
      item.qty += 1; saveCart(); renderCart();
    });
    li.querySelector('.eliminar').addEventListener('click', ()=>{
      cart.splice(i,1); saveCart(); renderCart();
    });

    listaCarrito.appendChild(li);
    suma += item.price * item.qty;
    unidades += item.qty;
  });

  totalEl.textContent = `Total: ${fmtCLP(suma)}`;
  cartCount.textContent = unidades;
}
function saveCart(){ localStorage.setItem('cart', JSON.stringify(cart)); }

vaciarBtn.addEventListener('click', ()=>{ cart = []; saveCart(); renderCart(); });
comprarBtn.addEventListener('click', ()=>{
  if (!cart.length) return alert('Tu carrito está vacío.');
  alert('¡Gracias por tu compra! (Demo)');
  cart = []; saveCart(); renderCart(); cerrar();
});

// Inicializar carrito al cargar
renderCart();
