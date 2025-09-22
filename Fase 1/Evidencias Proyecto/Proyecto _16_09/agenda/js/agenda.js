// ====== Datos Mock ======
const PROFESSIONALS = [
  { id: 'all', name: 'Todos los profesionales' },
  { id: 'camila', name: 'Dra. Camila Pérez' },
  { id: 'diego',  name: 'Dr. Diego Rivas'  },
  { id: 'sara',   name: 'Dra. Sara Muñoz'  },
];

const SERVICES = [
  { id: 'all', name: 'Todos los servicios' },
  { id: 'consulta', name: 'Consulta General' },
  { id: 'vacuna',   name: 'Vacunación' },
  { id: 'control',  name: 'Control' },
  { id: 'higiene',  name: 'Higiene dental' },
];

const APPOINTMENTS = [
  // YYYY-MM-DD, time in 24h, duration mins
  { id: 1, date: '2025-09-21', time: '10:00', duration: 30, pro: 'camila', service: 'consulta', pet: 'Luna (Perro)' },
  { id: 2, date: '2025-09-21', time: '12:30', duration: 30, pro: 'diego',  service: 'vacuna',   pet: 'Max (Gato)' },
  { id: 3, date: '2025-09-22', time: '09:30', duration: 30, pro: 'camila', service: 'control',  pet: 'Rocky (Perro)' },
  { id: 4, date: '2025-09-22', time: '11:00', duration: 60, pro: 'sara',   service: 'higiene',  pet: 'Milo (Gato)' },
  { id: 5, date: '2025-09-23', time: '15:00', duration: 30, pro: 'diego',  service: 'consulta', pet: 'Nina (Perro)' },
];

// ====== Utilidades ======
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));

const fmtDateLong = (d) =>
  d.toLocaleDateString('es-CL', { weekday:'long', day:'numeric', month:'long', year:'numeric' });

const toDateStr = (d) => d.toISOString().slice(0,10);

const parseTime = (t) => {
  const [h,m] = t.split(':').map(Number);
  const d = new Date();
  d.setHours(h, m, 0, 0);
  return d;
};

const rangeTimes = (start='09:00', end='18:00', stepMin=30) => {
  const out = [];
  let cur = parseTime(start), stop = parseTime(end);
  while (cur <= stop) {
    out.push(cur.toTimeString().slice(0,5));
    cur = new Date(cur.getTime() + stepMin*60000);
  }
  return out;
};

// ====== Estado ======
let viewMode = 'day';                 // 'day' | 'week'
let current = new Date();             // fecha base
let filters = { pro:'all', srv:'all' };

// ====== DOM ======
const selPro = $('#selPro');
const selSrv = $('#selSrv');
const calTitle = $('#calTitle');

const dayView = $('#dayView');
const weekView = $('#weekView');

const hoursCol = $('#hoursCol');
const apptList = $('#apptList');
const emptyState = $('#emptyState');

const weekGrid = $('#weekGrid');

// ====== Init ======
function initSelects() {
  selPro.innerHTML = PROFESSIONALS.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
  selSrv.innerHTML = SERVICES.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
}

function bindEvents() {
  // switches
  $('#btnDia').addEventListener('click', () => { viewMode='day'; render(); togglePills(); });
  $('#btnSemana').addEventListener('click', () => { viewMode='week'; render(); togglePills(); });

  // nav
  $('#today').addEventListener('click', () => { current = new Date(); render(); });
  $('#prevDay').addEventListener('click', () => { step(-1); });
  $('#nextDay').addEventListener('click', () => { step(1); });

  // filters
  selPro.addEventListener('change', e => { filters.pro = e.target.value; render(); });
  selSrv.addEventListener('change', e => { filters.srv = e.target.value; render(); });
  $('#clearFilters').addEventListener('click', () => {
    filters = { pro:'all', srv:'all' };
    selPro.value = 'all'; selSrv.value = 'all';
    render();
  });

  // “nueva cita” demo
  $('#newAppt').addEventListener('click', () => {
    alert('Aquí abrirías tu modal/form de nueva cita 🤗');
  });
}

function togglePills() {
  $('#btnDia').classList.toggle('active', viewMode==='day');
  $('#btnSemana').classList.toggle('active', viewMode==='week');
}

function step(n) {
  const delta = (viewMode==='day') ? n : n*7;
  current = new Date(current.getFullYear(), current.getMonth(), current.getDate()+delta);
  render();
}

// ====== Render ======
function render() {
  if (viewMode==='day') {
    dayView.classList.remove('hidden');
    weekView.classList.add('hidden');
    renderDay();
  } else {
    dayView.classList.add('hidden');
    weekView.classList.remove('hidden');
    renderWeek();
  }
}

function renderDay() {
  const dateStr = toDateStr(current);
  calTitle.textContent = `Citas — ${fmtDateLong(current)}`;

  // horas columna
  const hours = rangeTimes('09:00','18:00',30);
  hoursCol.innerHTML = hours.map(h => `<div class="t">${h}</div>`).join('');

  // citas del día + filtros
  const items = APPOINTMENTS
    .filter(a => a.date === dateStr)
    .filter(a => (filters.pro==='all' || a.pro===filters.pro))
    .filter(a => (filters.srv==='all' || a.service===filters.srv))
    .sort((a,b)=>a.time.localeCompare(b.time));

  apptList.innerHTML = items.map(a => `
    <li class="appt">
      <div class="ttl">${a.pet}</div>
      <div class="meta">${a.time} · ${SERVICES.find(s=>s.id===a.service)?.name || ''} · ${PROFESSIONALS.find(p=>p.id===a.pro)?.name || ''}</div>
    </li>
  `).join('');

  emptyState.style.display = items.length ? 'none' : 'flex';
}

function renderWeek() {
  // lunes de la semana de “current”
  const d = new Date(current);
  const day = d.getDay() || 7; // 1..7
  const monday = new Date(d.getFullYear(), d.getMonth(), d.getDate() - (day-1));

  const days = [...Array(7)].map((_,i) => new Date(monday.getFullYear(), monday.getMonth(), monday.getDate()+i));
  const span = `${days[0].toLocaleDateString('es-CL')} – ${days[6].toLocaleDateString('es-CL')}`;
  calTitle.textContent = `Semana — ${span}`;

  weekGrid.innerHTML = days.map(dt => {
    const ds = toDateStr(dt);
    const items = APPOINTMENTS
      .filter(a => a.date===ds)
      .filter(a => (filters.pro==='all' || a.pro===filters.pro))
      .filter(a => (filters.srv==='all' || a.service===filters.srv))
      .sort((a,b)=>a.time.localeCompare(b.time));

    const badge = items.length ? `<span class="badge">${items.length}</span>` : '';
    const lis = items.length
      ? items.map(a => `<li>${a.time} — ${a.pet}</li>`).join('')
      : `<li style="color:#9ca3af">Sin citas</li>`;

    const dayName = dt.toLocaleDateString('es-CL', { weekday:'short', day:'2-digit', month:'2-digit' });

    return `
      <div class="day-card">
        <div class="hd"><span class="d">${dayName}</span>${badge}</div>
        <ul>${lis}</ul>
      </div>
    `;
  }).join('');
}

// ====== Arranque ======
initSelects();
bindEvents();
render();
