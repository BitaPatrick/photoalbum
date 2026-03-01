# Fényképalbum

Egyszerű Django-s fényképalbum alkalmazás.

## Élő verzió

https://photoalbum-k6w1.onrender.com

## Röviden mit tud

- Kép feltöltése
- Kép törlése
- Lista név vagy dátum szerinti rendezéssel
- Kattintásra kép megnyitása
- Regisztráció / belépés / kilépés
- Feltöltés és törlés csak bejelentkezve

## Technikai felépítés

- Web app: Render (Django + Gunicorn)
- Adatbázis: Supabase Postgres
- Fájltárolás: Supabase Storage

## Render környezeti változók

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`False`)
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_BUCKET`
- `PYTHON_VERSION`

## Deploy

Render automatikusan deployol GitHub push után.

Build command:
`pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`

Start command:
`gunicorn config.wsgi:application`

## Beadás bontás

### 1. beadás

- Lokális SQLite
- Alap funkciók (feltöltés, listázás, rendezés, részletek)

### 2. beadás

- Külön adatbázis szerver (Supabase Postgres)
- Külön storage (Supabase Storage)
- Felhasználókezelés + jogosultság
