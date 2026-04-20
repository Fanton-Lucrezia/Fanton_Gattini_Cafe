const BASE_URL = 'http://127.0.0.1:8000/api';
let accessToken = localStorage.getItem('access_token') || null;
let prodottiDisponibili = [];

// ── UI helpers ───────────────────────────────────────────────────────────────

function aggiornaStatusBar() {
  const bar = document.getElementById('status-bar');
  const username = localStorage.getItem('username') || '';
  if (accessToken) {
    bar.textContent = `✅ Autenticato come: ${username}`;
    bar.className = 'logged-in';
  } else {
    bar.textContent = '⚠️ Non autenticato — alcune operazioni non saranno disponibili';
    bar.className = '';
  }
  bar.style.display = 'block';
  document.getElementById('btn-logout').disabled = !accessToken;
}

function mostraRisposta(data) {
  document.getElementById('api-response').textContent = JSON.stringify(data, null, 2);
}

function setMsg(id, testo, tipo = 'error') {
  const el = document.getElementById(id);
  el.textContent = testo;
  el.className = tipo;
}

// ── Fetch con gestione token scaduto ─────────────────────────────────────────

async function apiFetch(url, options = {}) {
  options.headers = options.headers || {};
  if (accessToken) {
    options.headers['Authorization'] = 'Bearer ' + accessToken;
  }
  options.headers['Content-Type'] = 'application/json';

  let res = await fetch(url, options);

  if (res.status === 401) {
    const refreshed = await refreshToken();
    if (refreshed) {
      options.headers['Authorization'] = 'Bearer ' + accessToken;
      res = await fetch(url, options);
    } else {
      logout();
      throw new Error('Sessione scaduta. Esegui di nuovo il login.');
    }
  }
  return res;
}

// ── Auth ─────────────────────────────────────────────────────────────────────

async function login() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();

  if (!username || !password) {
    setMsg('login-msg', 'Inserisci username e password.');
    return;
  }

  try {
    const res = await fetch(`${BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    mostraRisposta(data);

    if (res.ok) {
      accessToken = data.access;
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('username', username);
      aggiornaStatusBar();
      setMsg('login-msg', 'Login effettuato con successo!', 'success');
    } else {
      setMsg('login-msg', data.detail || 'Credenziali non valide.');
    }
  } catch (e) {
    setMsg('login-msg', 'Errore di connessione. Il server è avviato?');
  }
}

async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (res.ok) {
      const data = await res.json();
      accessToken = data.access;
      localStorage.setItem('access_token', data.access);
      return true;
    }
  } catch (_) {}
  return false;
}

function logout() {
  accessToken = null;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username');
  aggiornaStatusBar();
  setMsg('login-msg', 'Logout effettuato.', 'success');
}

// ── Menu ──────────────────────────────────────────────────────────────────────

async function caricaMenu() {
  const container = document.getElementById('menu-container');
  container.innerHTML = 'Caricamento...';

  try {
    const [resCat, resProd] = await Promise.all([
      fetch(`${BASE_URL}/categorie/`),
      fetch(`${BASE_URL}/prodotti/?disponibile=true`),
    ]);
    const categorie = await resCat.json();
    const prodotti = await resProd.json();

    const listaCat = categorie.results ?? categorie;
    const listaProd = prodotti.results ?? prodotti;
    prodottiDisponibili = listaProd;

    mostraRisposta({ categorie: listaCat, prodotti: listaProd });

    let html = '';
    for (const cat of listaCat) {
      const prodottiCat = listaProd.filter(p => p.categoria === cat.id);
      if (prodottiCat.length === 0) continue;
      html += `<h3>${cat.nome}</h3>`;
      for (const p of prodottiCat) {
        html += `
          <div class="prodotto-card">
            <div>
              <strong>${p.nome}</strong><br>
              <span>${p.descrizione || ''}</span>
            </div>
            <div class="prodotto-prezzo">
              <strong>€${p.prezzo.toFixed(2)}</strong>
              <input type="number" id="qty-${p.id}" class="qty-input"
                min="0" value="0" title="Quantità" />
            </div>
          </div>`;
      }
    }
    container.innerHTML = html || '<p>Nessun prodotto disponibile.</p>';
  } catch (e) {
    container.innerHTML = '<p class="error">Errore nel caricare il menu.</p>';
  }
}

// ── Ordine ────────────────────────────────────────────────────────────────────

async function creaOrdine() {
  if (!accessToken) {
    setMsg('ordine-msg', 'Devi fare il login prima di ordinare.');
    return;
  }
  if (prodottiDisponibili.length === 0) {
    setMsg('ordine-msg', 'Carica prima il menu.');
    return;
  }

  const prodottiSelezionati = prodottiDisponibili
    .map(p => ({
      prodotto_id: p.id,
      quantita: parseInt(document.getElementById(`qty-${p.id}`)?.value || 0),
    }))
    .filter(p => p.quantita > 0);

  if (prodottiSelezionati.length === 0) {
    setMsg('ordine-msg', 'Seleziona almeno un prodotto con quantità > 0.');
    return;
  }

  const note = document.getElementById('note-ordine').value.trim();

  try {
    const res = await apiFetch(`${BASE_URL}/ordini/`, {
      method: 'POST',
      body: JSON.stringify({ note, prodotti: prodottiSelezionati }),
    });
    const data = await res.json();
    mostraRisposta(data);

    if (res.ok) {
      setMsg('ordine-msg', `✅ Ordine #${data.id} creato! Totale: €${data.totale.toFixed(2)}`, 'success');
    } else {
      setMsg('ordine-msg', JSON.stringify(data));
    }
  } catch (e) {
    setMsg('ordine-msg', e.message || 'Errore nella creazione dell\'ordine.');
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
aggiornaStatusBar();