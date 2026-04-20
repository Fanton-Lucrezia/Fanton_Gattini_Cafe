# 🐱 Gattini Cafe API

API REST per la gestione del menu e degli ordini di Gattini Cafe, costruita con Django e Django REST Framework con autenticazione JWT.


> ⚠️ Per questo progetto la directory api sarà 'GattiniCafe', mentre config sarà 'Gattini_Cafe'.


---


## ⚙️ Installazione

### 1. Clona il repository
```bash
git clone <url-repo>
cd Gattini_Cafe
```

### 2. Crea e attiva il virtualenv
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 4. Assicurati che `gattini_cafe.db` sia nella stessa cartella di `manage.py`

### 5. Esegui le migrazioni
```bash
python manage.py migrate
```

> Le tabelle custom (categoria, prodotto, ordine, ordine_prodotto) hanno
> `managed = False` quindi non vengono toccate — i dati di esempio restano intatti.

### 6. Crea un superuser
```bash
python manage.py createsuperuser
```

### 7. Avvia il server
```bash
python manage.py runserver
```

L'API è disponibile su: http://127.0.0.1:8000/api/

---

## 🔑 Credenziali admin per i test

Dopo `createsuperuser`, usa le credenziali scelte. Esempio:
- **Username**: `admin`
- **Password**: `admin`

---

## 📡 Esempi di chiamate API

### Registrazione nuovo utente
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "pallino", "email": "pallino@gattini.cafe", "password": "micio123"}'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "pallino", "password": "micio123"}'
```

### Lista prodotti disponibili con filtro categoria
```bash
curl "http://127.0.0.1:8000/api/prodotti/?disponibile=true&categoria=1"
```

### Ricerca prodotto per testo
```bash
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

### Crea un prodotto (solo admin)
```bash
curl -X POST http://127.0.0.1:8000/api/prodotti/ \
  -H "Authorization: Bearer <access_token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Frappuccino al Tonno",
    "descrizione": "Specialità felina",
    "prezzo": 4.50,
    "disponibile": 1,
    "categoria": 1
  }'
```

### Upload immagine prodotto (solo admin)
```bash
curl -X POST http://127.0.0.1:8000/api/prodotti/1/immagine/ \
  -H "Authorization: Bearer <access_token_admin>" \
  -F "immagine=@/percorso/immagine.jpg"
```

### Statistiche admin
```bash
curl http://127.0.0.1:8000/api/admin/stats/ \
  -H "Authorization: Bearer <access_token_admin>"
```

### Filtro ordini per data
```bash
curl "http://127.0.0.1:8000/api/ordini/?data_da=2025-01-01&data_a=2025-12-31" \
  -H "Authorization: Bearer <access_token>"
```

### Rinnova access token
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
| PUT | `/api/categorie/{id}/` | Admin | Modifica categoria |
| DELETE | `/api/categorie/{id}/` | Admin | Elimina categoria |
| GET | `/api/prodotti/` | No | Lista prodotti (con filtri) |
| GET | `/api/prodotti/{id}/` | No | Dettaglio prodotto |
| POST | `/api/prodotti/` | Admin | Crea prodotto |
| PUT | `/api/prodotti/{id}/` | Admin | Modifica prodotto |
| PATCH | `/api/prodotti/{id}/` | Admin | Aggiornamento parziale prodotto |
| DELETE | `/api/prodotti/{id}/` | Admin | Elimina prodotto |
| POST | `/api/prodotti/{id}/immagine/` | Admin | Upload immagine prodotto |
| GET | `/api/ordini/` | Sì | Lista ordini (propri o tutti se admin) |
| POST | `/api/ordini/` | Sì | Crea ordine |
| GET | `/api/ordini/{id}/` | Sì | Dettaglio ordine |
| PATCH | `/api/ordini/{id}/stato/` | Admin | Aggiorna stato ordine |
| GET | `/api/admin/stats/` | Admin | Statistiche generali |

---

## 🎁 Funzionalità bonus implementate

| Bonus | Implementato       |
|-------|--------------------|
| Paginazione lista prodotti e ordini | Si (20 per pagina) |
| Endpoint statistiche admin `/api/admin/stats/` | Si                 |
| Upload immagine prodotto | Si                 |
| Filtro ordini per data `?data_da=&data_a=` | Si                 |
| Test unitari (almeno 5) | Si (12 test)       |
| Client per le API (+10 punti) | Si                 |

---

## 🧪 Esecuzione dei test

```bash
python manage.py test api
```

---

## 🖥️ Client

Il client è una singola pagina HTML in `client/index.html`.
Non richiede installazione: apri il file direttamente nel browser.

**Requisiti:** il server Django deve essere avviato (`python manage.py runserver`).

**Funzionalità:**
- Login con salvataggio automatico del token JWT
- Rinnovo automatico del token scaduto
- Visualizzazione del menu diviso per categorie
- Creazione ordine con selezione quantità per ogni prodotto
- Gestione errori (token scaduto, prodotto non disponibile, server offline)

---

## 📁 Struttura del progetto

```
Gattini_Cafe/
├── gattini_cafe.db
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── Gattini_Cafe/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── GattiniCafe/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   └── tests.py
└── client/
    ├── index.html
    ├── style.css
    └── app.js
```
