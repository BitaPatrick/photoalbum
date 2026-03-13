# Fényképalbum

Ez a projekt egy Django alapú fényképalbum alkalmazás, amely Renderen fut, az adatait Supabase Postgresben tárolja, a képfájlokat pedig Supabase Storage-ban kezeli. A felület szerveroldali rendereléssel készül, tehát nincs külön React frontend és külön API backend: ugyanaz a Django alkalmazás szolgálja ki az oldalakat és végzi az adatkezelést.

Az alkalmazás célja egy egyszerű, de teljes fotókezelési folyamat bemutatása: képek listázása, megnyitása, feltöltése és törlése, valamint felhasználói belépés-regisztráció kezelése. A listát név vagy feltöltési dátum szerint lehet rendezni, a feltöltés és a törlés pedig csak bejelentkezett felhasználónak engedélyezett.

## Működés röviden

Amikor egy felhasználó megnyitja az oldalt, a böngésző a Renderen futó Django alkalmazáshoz küld kérést. A Django lekéri a képek metaadatait a PostgreSQL adatbázisból, majd HTML oldalt renderel vissza. Feltöltéskor a képfájl először Supabase Storage-ba kerül, ezután az adatbázisba mentésre kerül a kép neve, feltöltési ideje, a storage útvonal és a megjelenítéshez használt URL. Törléskor ugyanez fordítva történik: előbb a storage objektum törlődik, majd az adatbázis rekord.

## Fő technikai elemek

A projekt központi beállításait a `config` csomag tartalmazza (`settings.py`, `urls.py`, `wsgi.py`). Az alkalmazáslogika az `album` appban van: a `models.py` írja le a `Photo` modellt, a `views.py` kezeli a listázást, részletoldalt, feltöltést, törlést és regisztrációt, a `templates` mappában találhatók a HTML oldalak, a `static` mappában pedig a stílusok.

A bejelentkezés és kijelentkezés Django auth alapon működik. A regisztráció saját nézettel történik (`/accounts/register/`), a kijelentkezés külön POST végponttal van kezelve, hogy stabil legyen production környezetben is.

## Környezeti változók

A futáshoz szükség van a Django titkos kulcsára és a Supabase kapcsolati adatokra. Production környezetben a `DJANGO_DEBUG` értéke `False`.

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_BUCKET`

Ha `DATABASE_URL` nincs megadva, lokálisan SQLite fallback működik.

## Futtatás

Lokális futtatásnál virtuális környezetben a `requirements.txt` csomagjai telepítendők, majd migráció után indítható a Django szerver. Renderen jelenleg Gunicornnal fut a projekt.

A repository tartalmaz Docker alapú futtatást is (`Dockerfile`, `scripts/start.sh`), így a projekt konténerben is elindítható. A start script a statikus fájlgyűjtést, migrációt és a Gunicorn indítását automatizálja.

## Terhelésteszt

A cloud alapú terhelésméréshez Locust forgatókönyv került a projektbe (`loadtest/locustfile.py`), valamint GitHub Actions workflow (`.github/workflows/loadtest.yml`). A teszt lefedi a fő felhasználói útvonalakat: listázás, rendezés, részletoldal, belépés, feltöltés és törlés.

A workflow futása után HTML és CSV riportok készülnek artifactként. Ezek alapján ellenőrizhető a válaszidő, hibaarány és a rendszer viselkedése terhelés alatt.
