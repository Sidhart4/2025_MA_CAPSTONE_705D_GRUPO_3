
    // Helper: validar email básico
    function esEmail(val){
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
    }

    const form = document.getElementById('formLogin');
    const email = document.getElementById('email');
    const pass = document.getElementById('password');
    const error = document.getElementById('error');
    const btn = document.getElementById('btnLogin');

    // Mostrar / ocultar contraseña
    const toggle = document.getElementById('togglePass');
    const icoEye = document.getElementById('icoEye');
    toggle.addEventListener('click', () => {
      const show = pass.type === 'password';
      pass.type = show ? 'text' : 'password';
      toggle.setAttribute('aria-label', show ? 'Ocultar contraseña' : 'Mostrar contraseña');
      // Cambiar icono (ojo / ojo tachado simple)
      icoEye.innerHTML = show
        ? '<path d="M17.94 17.94A10.94 10.94 0 0 1 12 20C5 20 1 12 1 12a21.86 21.86 0 0 1 5.06-6.94M9.9 4.24A10.94 10.94 0 0 1 12 4c7 0 11 8 11 8a21.86 21.86 0 0 1-3.13 4.65M14.12 9.88A3 3 0 1 1 9.88 14.12M1 1l22 22"></path>'
        : '<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"></path><circle cx="12" cy="12" r="3"></circle>';
    });

    form.addEventListener('submit', (e)=>{
      e.preventDefault();
      error.style.display = 'none';

      const vEmail = email.value.trim();
      const vPass  = pass.value.trim();

      if(!esEmail(vEmail) || vPass.length === 0){
        error.textContent = 'Completa un correo válido y tu contraseña.';
        error.style.display = 'block';
        return;
      }

      // Simulación de login (DEMO): guardamos sesión en sessionStorage
      btn.disabled = true;
      btn.textContent = 'Iniciando…';
      const user = { email:vEmail, ts: Date.now() };
      sessionStorage.setItem('akuma_auth', JSON.stringify(user));

      // Feedback de éxito
      setTimeout(()=>{
        alert('Sesión iniciada (demo). Serás redirigido/a.');
        // En un proyecto real: window.location.href = '/agenda';
        btn.disabled = false;
        btn.textContent = 'LOGIN';
      }, 900);
    });
