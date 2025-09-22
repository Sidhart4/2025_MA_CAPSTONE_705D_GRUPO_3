// === Mock temporal (cámbialo por tu backend cuando quieras) ===
const PRODUCTS = [
  {
    id: 1,
    name: "Royal Canin Adult",
    desc: "Alimento premium para perros adultos",
    category: "Alimentos",
    pet: "Perro",
    brand: "Royal Canin",
    price: 45000,
    old: 50000,
    rating: 4.8,
    stock: true,
    badge: "Oferta",
    image: "images/productos/dog-food-bag-royal-canin.jpg",
  },
  {
    id: 2,
    name: "Bravecto Antipulgas",
    desc: "Protección contra pulgas y garrapatas por 3 meses",
    category: "Antiparasitarios",
    pet: "Perro",
    brand: "Bravecto",
    price: 28000,
    rating: 4.9,
    stock: true,
    badge: "Nuevo",
    image: "images/productos/flea-treatment-bravecto-box.jpg",
  },
  {
    id: 3,
    name: "Shampoo Medicado",
    desc: "Especial para pieles sensibles",
    category: "Higiene",
    pet: "Perro",
    brand: "Generic",
    price: 18000,
    rating: 4.6,
    stock: true,
    image: "images/productos/pet-medicated-shampoo-bottle.jpg",
  },
  {
    id: 4,
    name: "Pelota Kong Classic",
    desc: "Juguete resistente para perros activos",
    category: "Juguetes",
    pet: "Perro",
    brand: "Kong",
    price: 12000,
    rating: 4.7,
    stock: true,
    image: "images/productos/kong-classic-red-dog-toy-ball.jpg",
  },
  {
    id: 5,
    name: "Ratón de Juguete Interactivo",
    desc: "Juguete automático para gatos",
    category: "Juguetes",
    pet: "Gato",
    brand: "Generic",
    price: 22000,
    rating: 4.3,
    stock: true,
    badge: "Nuevo",
    image: "images/productos/interactive-cat-mouse-toy-robotic.jpg",
  },
  {
    id: 6,
    name: "Comedero Automático",
    desc: "Dispensador de comida programable",
    category: "Accesorios",
    pet: "Perro",
    brand: "PetSafe",
    price: 85000,
    rating: 4.5,
    stock: true,
    image: "images/productos/automatic-pet-feeder-programmable.jpg",
  },
  {
    id: 7,
    name: "Hill’s Science Diet",
    desc: "Alimento terapéutico para perros senior",
    category: "Alimentos",
    pet: "Perro",
    brand: "Hill's",
    price: 52000,
    rating: 4.7,
    stock: true,
    image: "images/productos/hills-science-diet-senior-dog-food.jpg",
  },
  {
    id: 8,
    name: "Spray Dental",
    desc: "Higiene dental sin cepillado",
    category: "Higiene",
    pet: "Perro",
    brand: "Generic",
    price: 16000,
    rating: 4.2,
    stock: true,
    image: "images/productos/pet-dental-spray-oral-care.jpg",
  },
  {
    id: 9,
    name: "Frontline Plus",
    desc: "Pipeta antipulgas y garrapatas",
    category: "Antiparasitarios",
    pet: "Perro",
    brand: "Frontline",
    price: 15000,
    old: 18000,
    rating: 4.6,
    stock: false,
    badge: "Oferta",
    image: "images/productos/frontline-plus-pipeta-antipulgas.jpg",
  },
  {
    id: 10,
    name: "Royal Canin Indoor",
    desc: "Alimento para gatos de interior",
    category: "Alimentos",
    pet: "Gato",
    brand: "Royal Canin",
    price: 34000,
    old: 38000,
    rating: 4.4,
    stock: true,
    badge: "Oferta",
    image: "images/productos/whiskas-cat-food-bag-adult-chicken.jpg",
  },
  {
    id: 11,
    name: "Rascador 120cm",
    desc: "Rascador multi-nivel con cuevas",
    category: "Accesorios",
    pet: "Gato",
    brand: "Generic",
    price: 69000,
    old: 79000,
    rating: 4.5,
    stock: true,
    badge: "Oferta",
    image: "images/productos/cat-scratching-tower-120cm-multi-level.jpg",
  },
  {
    id: 12,
    name: "Collar LED Recargable",
    desc: "Collar luminoso para paseos nocturnos",
    category: "Accesorios",
    pet: "Perro",
    brand: "Generic",
    price: 25000,
    rating: 4.5,
    stock: false,
    badge: "Nuevo",
    image: "images/productos/led-dog-collar-rechargeable-night-safety.jpg",
  },
];

const $ = (s) => document.querySelector(s);
const fmt = (n) => n.toLocaleString("es-CL");

const state = {
  q: "",
  sort: "relevance",
  cat: new Set(),
  pet: new Set(),
  brands: new Set(),
  min: 0,
  max: 200000,
  inStock: false,
  onlyDeals: false,
  rating: 0,
  size: 12,
  page: 1,
};

// ====== Filtros dinámicos ======
(function buildFilters() {
  const cats = [...new Set(PRODUCTS.map((p) => p.category))].sort();
  const brands = [...new Set(PRODUCTS.map((p) => p.brand))].sort();

  const catsBox = $("#fCats");
  cats.forEach((c) => {
    const lab = document.createElement("label");
    lab.innerHTML = `<input type="checkbox" name="cat" value="${c}">${c}`;
    catsBox.appendChild(lab);
  });

  const brandsBox = $("#fBrands");
  brands.forEach((b) => {
    const lab = document.createElement("label");
    lab.innerHTML = `<input type="checkbox" name="brand" value="${b}">${b}`;
    brandsBox.appendChild(lab);
  });
})();

// ====== UI bindings ======
$("#search").addEventListener("input", (e) => {
  state.q = e.target.value.trim().toLowerCase();
  reset();
});
$("#sort").addEventListener("change", (e) => {
  state.sort = e.target.value;
  render();
});

["minRange", "maxRange", "minInput", "maxInput"].forEach((id) =>
  $("#" + id).addEventListener("input", syncPrice)
);
function syncPrice() {
  const minR = +$("#minRange").value,
    maxR = +$("#maxRange").value;
  const minI = +$("#minInput").value || 0,
    maxI = +$("#maxInput").value || 0;
  if (this.id.includes("Range")) {
    $("#minInput").value = minR;
    $("#maxInput").value = maxR;
  } else {
    $("#minRange").value = Math.min(minI, maxI);
    $("#maxRange").value = Math.max(minI, maxI);
  }
  state.min = +$("#minRange").value;
  state.max = +$("#maxRange").value;
  $("#priceHint").textContent = `$${fmt(state.min)} – $${fmt(state.max)}`;
  reset();
}

$("#filters").addEventListener("change", (e) => {
  if (e.target.name === "cat")
    toggle(state.cat, e.target.value, e.target.checked);
  if (e.target.name === "pet")
    toggle(state.pet, e.target.value, e.target.checked);
  if (e.target.name === "brand")
    toggle(state.brands, e.target.value, e.target.checked);
  if (e.target.id === "inStock") state.inStock = e.target.checked;
  if (e.target.id === "onlyDeals") state.onlyDeals = e.target.checked;
  if (e.target.name === "rating") state.rating = +e.target.value;
  reset();
});

$("#loadMore").addEventListener("click", () => {
  state.page++;
  renderGrid();
});

function toggle(set, v, add) {
  add ? set.add(v) : set.delete(v);
}
function reset() {
  state.page = 1;
  render();
}

// ====== Core ======
function qset() {
  let list = PRODUCTS.slice();

  if (state.q)
    list = list.filter((p) =>
      (p.name + " " + p.desc).toLowerCase().includes(state.q)
    );
  if (state.cat.size) list = list.filter((p) => state.cat.has(p.category));
  if (state.pet.size) list = list.filter((p) => state.pet.has(p.pet));
  if (state.brands.size) list = list.filter((p) => state.brands.has(p.brand));

  list = list.filter((p) => p.price >= state.min && p.price <= state.max);
  if (state.inStock) list = list.filter((p) => p.stock);
  if (state.onlyDeals) list = list.filter((p) => p.old);
  if (state.rating > 0) list = list.filter((p) => p.rating >= state.rating);

  switch (state.sort) {
    case "priceAsc":
      list.sort((a, b) => a.price - b.price);
      break;
    case "priceDesc":
      list.sort((a, b) => b.price - a.price);
      break;
    case "rating":
      list.sort((a, b) => b.rating - a.rating);
      break;
    case "new":
      list.sort((a, b) => (b.badge === "Nuevo") - (a.badge === "Nuevo"));
      break;
    default:
      list.sort(
        (a, b) =>
          (b.old ? 1 : 0) +
          (b.badge === "Nuevo" ? 1 : 0) -
          ((a.old ? 1 : 0) + (a.badge === "Nuevo" ? 1 : 0))
      );
  }
  return list;
}

// ====== Render ======
function render() {
  const all = qset();
  $("#resultCount").textContent = `${all.length} productos encontrados`;
  renderGrid(all);
}

function renderGrid(all = qset()) {
  const grid = $("#grid");
  grid.innerHTML = "";

  const total = all.length;
  const slice = all.slice(0, state.page * state.size);

  slice.forEach((p, i) => {
    const el = document.createElement("article");
    el.className = "card-p mount";
    el.style.animationDelay = `${(i % 8) * 25}ms`;
    el.innerHTML = cardHTML(p);
    grid.appendChild(el);

    el.querySelector(".add").addEventListener("click", (e) => {
      e.currentTarget.animate(
        [
          { transform: "scale(1)" },
          { transform: "scale(.97)" },
          { transform: "scale(1)" },
        ],
        { duration: 160 }
      );
    });
  });

  $("#loadMore").style.display = slice.length < total ? "inline-flex" : "none";
  $(
    "#footInfo"
  ).textContent = `Mostrando ${slice.length} de ${total} productos`;
}

function cardHTML(p) {
  const stars =
    "★★★★★".slice(0, Math.round(p.rating)) +
    "☆☆☆☆☆".slice(0, 5 - Math.round(p.rating));
  return `
    <div class="thumb">
      <div class="badges">
        ${p.badge === "Nuevo" ? '<span class="badge new">Nuevo</span>' : ""}
        ${p.old ? '<span class="badge sale">Oferta</span>' : ""}
      </div>
      <button class="fav" title="Favorito">❤</button>
      <div class="pic"><img src="${p.image}" alt="${p.name}"></div>
    </div>

    <div class="body">
      <div class="ttl">${p.name}</div>
      <div class="desc">${p.desc}</div>

      <div class="meta">
        <span class="stars" aria-label="${p.rating} de 5">★★★★★</span>
        <span>${p.stock ? "En stock" : "Sin stock"}</span>
      </div>

      <div class="price">
        <span class="now">$${fmt(p.price)}</span>
        ${p.old ? `<span class="old">$${fmt(p.old)}</span>` : ""}
      </div>

      <div class="actions">
        <button class="add">Agregar</button>
        <button class="icon" title="Ver">👁</button>
      </div>
    </div>
  `;
}

// init
render();
