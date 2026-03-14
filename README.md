# Fényképalbum

Publikus elérés: https://photoalbum-k6w1.onrender.com

Ez a projekt egy egyszerű, de teljesen működő fényképalbum alkalmazás Django alapon. A cél az volt, hogy a laborfeladat követelményeit stabilan teljesítse: lehessen képeket listázni, rendezni, megnyitni, feltölteni és törölni, illetve legyen rendes felhasználókezelés (regisztráció, belépés, kilépés), jogosultságokkal.

A futtatás Renderen történik, az adatok Supabase Postgresben vannak, a fájlok pedig Supabase Storage-ban. Ezt azért választottam, mert így a webalkalmazás, az adatbázis és a fájltárolás tisztán szét van választva, és production környezetben is ugyanaz a működés marad, mint amit a feladat kér.

## Mit tud jelenleg az alkalmazás?

A képek listája és részletoldala bejelentkezés nélkül is elérhető. Bejelentkezett felhasználó ezen felül képet tud feltölteni és törölni. A képek név szerint vagy feltöltési dátum szerint rendezhetők. Minden képnél tárolva van a név, a feltöltési idő, valamint a storage útvonal és a megjelenítési URL.

## Funkcionális feltételek teljesülése

A feladatban megadott fő funkcionális pontok megvalósultak: a képek feltöltése és törlése működik, minden képhez név és feltöltési dátum tartozik (a név hossza korlátozott), a lista név és dátum szerint rendezhető, a listából kattintva elérhető a részletes képnézet, továbbá a felhasználókezelés (regisztráció, belépés, kilépés) is működik. Jogosultság oldalon a feltöltés és törlés csak bejelentkezett felhasználónak engedélyezett.

## Miért ezt a megoldást választottam?

A Django választásának fő oka az volt, hogy a laborfeladat funkcióit gyorsan és megbízhatóan le tudjam fedni egyetlen, jól áttekinthető kódbázissal. A felületet a Django template-ek szolgálják ki, ezért nem kell külön kliensoldali alkalmazást és külön API-t karbantartani ehhez a feladathoz.

A Render mellett szólt, hogy egyszerű a deploy, automatikus a GitHub integráció, és a futtatási környezet könnyen reprodukálható. A Supabase Postgres + Storage páros azért lett jó választás, mert a képek bináris fájlként kerülnek tárolásra, miközben az alkalmazásadatok relációs adatbázisban maradnak.

## Működés rövid folyamata

Oldalmegnyitáskor a kérés a Renderen futó Django alkalmazáshoz megy, amely lekéri a szükséges rekordokat a PostgreSQL adatbázisból, és HTML választ küld vissza. Feltöltéskor a kép először Storage-ba kerül, majd az adatbázisba mentésre kerül a metaadat. Törléskor előbb a storage objektum törlődik, utána a hozzá tartozó adatbázis rekord.

## Projekt felépítése

- `config/`: projektbeállítások (`settings.py`, `urls.py`, `wsgi.py`)
- `album/`: alkalmazáslogika (modellek, nézetek, űrlapok)
- `album/templates/`: oldalsablonok
- `album/static/`: stílus
- `loadtest/`: Locust terhelésteszt fájlok

## Fontos fájlok röviden

- `manage.py`: Django parancsok futtatása (migrate, runserver, test)
- `config/settings.py`: környezeti változók, DB kapcsolat, static/media, auth redirectek
- `config/urls.py`: fő URL belépési pont (`album` app + auth route-ok)
- `album/models.py`: `Photo` modell (név, dátum, storage_path, image_url)
- `album/views.py`: fő működés (lista, részletek, feltöltés, törlés, regisztráció, logout)
- `album/urls.py`: app endpointok
- `album/forms.py`: feltöltési űrlap
- `album/supabase_client.py`: Supabase kliens inicializálása
- `album/templates/base.html`: közös layout és navigáció
- `album/tests.py`: funkcionális regressziós tesztek
- `Dockerfile`, `scripts/start.sh`: konténeres indítás
- `.github/workflows/loadtest.yml`: felhőből futó Locust workflow
- `loadtest/locustfile.py`: terheléses user flow leírása

## Környezeti változók

A futáshoz ezek szükségesek: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_BUCKET`.

Ha nincs `DATABASE_URL`, akkor lokálisan SQLite fallback működik.

## Futtatás

Lokálisan a `requirements.txt` telepítése után migrációval indítható (`manage.py migrate`, majd `runserver`).

A repository tartalmaz Docker futtatást is (`Dockerfile`, `scripts/start.sh`), ahol az indításkor automatikusan lefut a `collectstatic`, a `migrate`, majd a Gunicorn szerver indul.

## Terhelésteszt

A terhelésteszt Locust-tal készült (`loadtest/locustfile.py`), a futtatást GitHub Actions workflow végzi (`.github/workflows/loadtest.yml`), így a mérés felhőből reprodukálható.

Az aktuális futásban 813 kérés ment le 0 hibával, tehát a rendszer stabil volt. A válaszidők viszont magasak lettek, ami a Render free instance korlátai mellett várható.

Az eredmények itt vannak a repóban:
- `loadtest/results/loadtest_report.html`
- `loadtest/results/loadtest_report_stats.csv`
- `loadtest/results/loadtest_report_failures.csv`
- `loadtest/results/loadtest_report_exceptions.csv`
