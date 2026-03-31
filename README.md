# 🐱 Gattini Cafe API

API REST per la gestione del menu e degli ordini di Gattini Cafe, costruita con Django e Django REST Framework con autenticazione JWT.


> ⚠️ Per questo progetto la directory api sarà 'GattiniCafe', mentre config sarà 'Gattini_Cafe'.


---

## ⚙️ Installazione

### 1. Clona il repository e spostati nella cartella del progetto
```bash
git clone <url-repo>
cd Gattini_Cafe
```

### 2. Crea e attiva il virtualenv
```bash
python -m venv venv

# Windows (PyCharm lo fa in automatico)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

```
### 3. Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 4. Assicurati che `gattini_cafe.db` sia nella stessa cartella di `manage.py`

### 5. Esegui le migrazioni (crea le tabelle Django: auth, sessions, ecc.)
```bash
python manage.py migrate
```

> ⚠️ Le tabelle custom (categoria, prodotto, ordine, ordine_prodotto) sono `managed = False`,
> quindi non verranno toccate dal migrate — i dati di esempio nel .db sono al sicuro.

### 6. Crea un superuser (admin)
```bash
python manage.py createsuperuser
```
Usa le credenziali che vuoi. Esempio:
- username: `admin`
- email: `admin@gmail.com`
- password: `admin`

### 7. Avvia il server di sviluppo
```bash
python manage.py runserver
```
L'API è disponibile su: http://127.0.0.1:8000/api/

---

## 🔑 Credenziali admin per i test

Dopo aver eseguito `createsuperuser`:
- **Username**: admin
- **Password**: admin *(o quella scelta al momento della creazione)*

---

## 📡 Esempi di chiamate API

### Registrazione nuovo utente
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "pallino", "email": "pallino@gattini.cafe", "password": "micio123"}'
```

### Login (ottieni i token JWT)
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "pallino", "password": "micio123"}'
```
Risposta: `{"access": "eyJ...", "refresh": "eyJ..."}`

### Lista prodotti (pubblico, con filtri)
```bash
# tutti i prodotti
curl http://127.0.0.1:8000/api/prodotti/

# solo quelli disponibili, categoria 1
curl "http://127.0.0.1:8000/api/prodotti/?disponibile=true&categoria=1"

# ricerca per testo
curl "http://127.0.0.1:8000/api/prodotti/?search=cappuccino"
```

### Dati utente autenticato
```bash
curl http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Crea un ordine
```bash
curl -X POST http://127.0.0.1:8000/api/ordini/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "note": "Senza lattosio!",
    "prodotti": [
      {"prodotto_id": 1, "quantita": 2},
      {"prodotto_id": 3, "quantita": 1}
    ]
  }'
```

### Aggiorna stato ordine (solo admin)
```bash
curl -X PATCH http://127.0.0.1:8000/api/ordini/1/stato/ \
  -H "Authorization: Bearer <access_token_admin>" \
  -H "Content-Type: application/json" \
  -d '{"stato": "in_preparazione"}'
```

### Crea un nuovo prodotto (solo admin)
```bash
curl -X POST http://127.0.0.1:8000/api/prodotti/ \
  -H "Authorization: Bearer <access_token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Frappuccino al Tonno",
    "descrizione": "Specialità felina, non per i deboli di stomaco",
    "prezzo": 4.50,
    "disponibile": 1,
    "categoria": 1
  }'
```

### Rinnova l'access token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

---

## 📋 Mappa degli endpoint

| Metodo | Endpoint | Auth | Descrizione |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Registra nuovo utente |
| POST | `/api/auth/login/` | No | Login, restituisce access + refresh token |
| POST | `/api/auth/token/refresh/` | No | Rinnova access token |
| GET | `/api/auth/me/` | Sì | Dati utente autenticato |
| GET | `/api/categorie/` | No | Lista categorie |
| GET | `/api/categorie/{id}/` | No | Dettaglio categoria |
| POST | `/api/categorie/` | Admin | Crea categoria |
| PUT/DELETE | `/api/categorie/{id}/` | Admin | Modifica/elimina categoria |
| GET | `/api/prodotti/` | No | Lista prodotti (con filtri) |
| GET | `/api/prodotti/{id}/` | No | Dettaglio prodotto |
| POST | `/api/prodotti/` | Admin | Crea prodotto |
| PUT/PATCH/DELETE | `/api/prodotti/{id}/` | Admin | Modifica/elimina prodotto |
| GET | `/api/ordini/` | Sì | Lista ordini (propri o tutti se admin) |
| POST | `/api/ordini/` | Sì | Crea ordine |
| GET | `/api/ordini/{id}/` | Sì | Dettaglio ordine |
| PATCH | `/api/ordini/{id}/stato/` | Admin | Aggiorna stato ordine |
