# Fényképalbum alkalmazás (Django + Render + Supabase)

Ez egy Django alapú fényképalbum webalkalmazás, amit PaaS környezetben futtatok.
A végleges változat többrétegű és skálázható felépítésű:

- Web réteg: Render (Django + Gunicorn)
- Adatbázis réteg: Supabase Postgres
- Fájltárolás: Supabase Storage

## Publikus alkalmazás

- URL: `https://<sajat-render-app>.onrender.com`

## Funkciók

- Kép feltöltése (név + fájl)
- Kép törlése
- Képek listázása név vagy dátum szerinti rendezéssel
- Listaelemre kattintva részletes nézet (kép megjelenítése)
- Felhasználókezelés: regisztráció, bejelentkezés, kijelentkezés
- Jogosultság: feltöltés és törlés csak bejelentkezett felhasználónak
- Kép neve maximum 40 karakter
- Feltöltési dátum automatikus mentése és megjelenítése (`ÉÉÉÉ-HH-NN ÓÓ:PP`)

## Miért többrétegű és skálázható?

- A webalkalmazás, az adatbázis és a fájltárolás külön szolgáltatásban fut.
- Emiatt az egyes rétegek külön-külön skálázhatók és kezelhetők.
- A renderes deploy GitHub push-ra automatikusan elindul.

## Környezeti változók (Render Environment)

A Render szolgáltatásban ezeket a változókat kell beállítani:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`False` éles környezetben)
- `DATABASE_URL` (Supabase Postgres connection string)
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_BUCKET` (pl. `photos`)
- `PYTHON_VERSION` (pl. `3.11.9`)

Megjegyzés: a `SUPABASE_ANON_KEY` nálam be van állítva, de a backend kód jelenleg nem használja.

## Supabase beállítás

1. Hozz létre egy projektet Supabase-ben.
2. Hozz létre egy Storage bucketet (pl. `photos`).
3. Másold ki:
   - Project URL -> `SUPABASE_URL`
   - `service_role` kulcs -> `SUPABASE_SERVICE_ROLE_KEY`
4. A Postgres kapcsolatból másold ki a `DATABASE_URL` értéket.
5. Ezt add meg a Render Environment-ben.

## Render beállítás (pontos lépések)

1. Renderben hozz létre egy `Web Service`-t GitHub repo-ból.
2. Build Command:
   `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
3. Start Command:
   `gunicorn config.wsgi:application`
4. Állítsd be a fenti környezeti változókat az Environment oldalon.
5. Mentsd el, majd indíts deployt (vagy pusholj GitHubra).

## Lokális futtatás

1. Virtuális környezet létrehozása/aktiválása
2. Függőségek telepítése:
   `pip install -r requirements.txt`
3. Környezeti változók beállítása
4. Migráció:
   `python manage.py migrate`
5. Indítás:
   `python manage.py runserver`

## Beadás felosztása

### 1. beadás (minimum verzió)

- Lokális SQLite adatbázis
- Alap funkciók: feltöltés, listázás, rendezés, részletek
- Első PaaS deploy

### 2. beadás (végleges verzió)

- Külön adatbázis szerver: Supabase Postgres
- Külön storage: Supabase Storage
- Felhasználókezelés + jogosultságkezelés
- Törlésnél storage objektum + DB rekord együtt kezelve
