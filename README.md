# Fényképalbum (Django + Render + Supabase)

Ez a repository egy szerveroldali renderelésű (SSR) Django webalkalmazás, amely képek listázását, feltöltését, megnyitását és törlését valósítja meg jogosultságkezeléssel.

Élő környezet (Render):
- https://photoalbum-k6w1.onrender.com

## 1. Cél és architektúra

### 1.1 Mi fut hol?
- Alkalmazás (web szerver): Renderen futó Django + Gunicorn
- Adatbázis: Supabase Postgres
- Fájltárolás: Supabase Storage bucket

### 1.2 Kérések útja
- Böngésző -> Django (HTTP)
- Django -> Supabase Postgres (metaadat lekérdezés/mentés)
- Django -> Supabase Storage (kép feltöltés/törlés)
- Django -> Böngésző (HTML válasz)

### 1.3 Monolit vagy külön frontend-backend?
- Ez egy Django monolit: a frontend (Django template-ek) és backend logika ugyanabban az alkalmazásban van.
- Nincs külön React frontend és külön REST API szolgáltatás.

## 2. Funkciók

- Képek listázása
- Rendezés név szerint és dátum szerint
- Kép részletes megnyitása
- Kép feltöltése (csak belépve)
- Kép törlése (csak belépve)
- Regisztráció, belépés, kilépés

## 3. Követelmény megfelelés

### 3.1 2. beadás
- Külön adatbázis-szerver: Supabase Postgres
- Külön storage: Supabase Storage
- Felhasználókezelés és jogosultság: Django auth + `@login_required`
- Név max 40 karakter: `Photo.name(max_length=40)`
- Feltöltési dátum: `uploaded_at`
- Lista név/dátum rendezéssel: `/?sort=name`, `/?sort=date`

### 3.2 3. beadás előkészítés
- Dockeres futtatás hozzáadva (`Dockerfile`, `scripts/start.sh`)
- Felhőből indítható terhelésteszt workflow (`.github/workflows/loadtest.yml`)
- Locust szkript fő funkciókra (`loadtest/locustfile.py`)

## 4. Projektstruktúra

- `config/` - Django projektkonfiguráció (`settings.py`, `urls.py`, `wsgi.py`)
- `album/` - alkalmazáslogika
- `album/models.py` - `Photo` modell
- `album/views.py` - lista/részletek/feltöltés/törlés/regisztráció
- `album/urls.py` - app URL routing
- `album/templates/` - UI oldalak
- `album/static/album/style.css` - stílus
- `album/supabase_client.py` - Supabase kliens létrehozása
- `loadtest/` - Locust terhelésteszt
- `scripts/start.sh` - konténer startup

## 5. Adatmodell

`Photo` mezők:
- `name` (`CharField(40)`)
- `uploaded_at` (`DateTimeField(auto_now_add=True)`)
- `storage_path` (`CharField(500)`) - bucket objektum útvonala
- `image_url` (`URLField(1000)`) - megjelenítéshez használt URL

## 6. URL-ek és működés

- `GET /` - listázás (default: dátum szerint csökkenő)
- `GET /?sort=name` - név szerinti rendezés
- `GET /?sort=date` - dátum szerinti rendezés
- `GET /photo/<id>/` - részletes oldal
- `GET/POST /upload/` - feltöltés (auth kötelező)
- `GET/POST /photo/<id>/delete/` - törlés (auth kötelező)
- `GET/POST /accounts/register/` - regisztráció
- `GET/POST /accounts/login/` - belépés (Django beépített)
- `POST /accounts/logout/` - kilépés (Django beépített)

## 7. Környezeti változók

Kötelező (production):
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_BUCKET`

Ajánlott:
- `PYTHON_VERSION`
- `WEB_CONCURRENCY` (konténeres futásnál Gunicorn workers)

## 8. Lokális futtatás (nem Docker)

1. Virtuális környezet és csomagok:
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`

2. Migráció:
- `python manage.py migrate`

3. Indítás:
- `python manage.py runserver`

4. Böngésző:
- `http://127.0.0.1:8000`

Megjegyzés:
- Ha nincs `DATABASE_URL`, lokálisan SQLite fallback működik (`db.sqlite3`).

## 9. Konténeres futtatás (Docker)

Build:
- `docker build -t photoalbum:latest .`

Run:
- `docker run --rm -p 8000:8000 --env-file .env photoalbum:latest`

A konténer induláskor:
- `collectstatic`
- `migrate`
- `gunicorn config.wsgi:application`

## 10. Render deploy

### 10.1 Nem konténeres (jelenlegi)
Build command:
- `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`

Start command:
- `gunicorn config.wsgi:application`

### 10.2 Konténeres opció
- Service Docker deployként is futtatható a repository-ból a `Dockerfile` alapján.

## 11. Automatizált tesztelés (funkcióellenőrzés)

A `album/tests.py` lefedi:
- listázás és rendezés
- részletes oldal
- auth védelem upload/delete útvonalakon
- regisztráció
- upload flow (Supabase kliens mockolva)
- delete flow (Supabase kliens mockolva)

Futtatás:
- `.venv/bin/python manage.py test -v 2`

Elvárt eredmény:
- 8/8 teszt sikeres

## 12. Cloud terhelésteszt (Locust)

Fájlok:
- `loadtest/locustfile.py`
- `.github/workflows/loadtest.yml`

Locust forgatókönyv lefedi:
- listaoldal
- rendezés név/dátum szerint
- részletek megnyitása
- login
- feltöltés
- törlés

### 12.1 GitHub Actions beállítás
Repo secrets:
- `LOADTEST_HOST` (pl. `https://photoalbum-k6w1.onrender.com`)
- `LOADTEST_USERNAME`
- `LOADTEST_PASSWORD`

Workflow indítás:
- Actions -> `Cloud Load Test` -> `Run workflow`

Artifactok:
- `loadtest_report.html`
- `loadtest_report_stats.csv`
- `loadtest_report_failures.csv`
- `loadtest_report_exceptions.csv`

## 13. Autoscaling (Render)

Javasolt labor setup:
- Min instances: `1`
- Max instances: `3`
- CPU target: kb. `60%`
- Kisebb instance típus a teszthez (könnyebben triggerelhető scale-up)

Bizonyítékok:
- autoscaling beállítás screenshot
- Render event log screenshot (scale up + scale down)
- Locust riportok

## 14. Beadási checklist

- GitHub repository link
- élő Render URL
- rövid architektúra leírás (Render + Supabase DB + Supabase Storage)
- funkciók bemutatása (upload/list/detail/delete/auth)
- terhelésteszt konfiguráció és eredmények
- autoscaling bizonyítékok
- rövid tanulságok

## 15. Gyakori hibák

- `NoReverseMatch: register`:
  - oka: hiányzó regisztráció route
  - jelenlegi állapot: javítva (`/accounts/register/`)

- Upload 500:
  - oka: hiányzó vagy rossz `SUPABASE_*` env

- Productionban debug:
  - `DJANGO_DEBUG=False` kötelező
