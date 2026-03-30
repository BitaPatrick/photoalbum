import os
import random
import re
import time
from io import BytesIO

from locust import HttpUser, between, task


PHOTO_ID_RE = re.compile(r'href=[\'"](?:https?://[^/]+)?/photo/(\d+)/[\'"]')
PHOTO_TITLE_LINK_RE = re.compile(r'<a href="/photo/(\d+)/">([^<]+)</a>')
CSRF_RE = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')


def _extract_csrf_token(html: str) -> str | None:
    match = CSRF_RE.search(html)
    if not match:
        return None
    return match.group(1)


def _build_tiny_png() -> bytes:
    # 1x1 PNG file for upload tests
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00"
        b"\x00\x03\x01\x01\x00\x18\xdd\x8d\x18\x00\x00\x00\x00IEND\xaeB`\x82"
    )


class PhotoAlbumUser(HttpUser):
    wait_time = between(0.2, 1.0)

    def on_start(self) -> None:
        self.username = os.getenv("LOADTEST_USERNAME")
        self.password = os.getenv("LOADTEST_PASSWORD")
        self.is_authenticated = False
        self._maybe_login()

    def _maybe_login(self) -> None:
        if not self.username or not self.password:
            return

        for _ in range(3):
            response = self.client.get("/accounts/login/")
            token = _extract_csrf_token(response.text)
            if not token:
                time.sleep(0.5)
                continue

            login_response = self.client.post(
                "/accounts/login/",
                data={
                    "username": self.username,
                    "password": self.password,
                    "csrfmiddlewaretoken": token,
                },
                headers={"Referer": f"{self.host}/accounts/login/"},
                name="POST /accounts/login/",
                allow_redirects=True,
            )
            self.is_authenticated = login_response.status_code == 200
            if self.is_authenticated:
                return
            time.sleep(0.5)

    def _get_photo_ids(self) -> list[int]:
        list_response = self.client.get("/", name="GET / (for ids)")
        return [int(photo_id) for photo_id in PHOTO_ID_RE.findall(list_response.text)]

    def _get_photo_id_by_name(self, photo_name: str) -> int | None:
        list_response = self.client.get("/", name="GET / (for cycle ids)")
        for photo_id, title in PHOTO_TITLE_LINK_RE.findall(list_response.text):
            if title.strip() == photo_name:
                return int(photo_id)
        return None

    @task(3)
    def list_photos(self) -> None:
        self.client.get("/", name="GET /")

    @task(2)
    def list_sorted_by_name(self) -> None:
        self.client.get("/?sort=name", name="GET /?sort=name")

    @task(2)
    def list_sorted_by_date(self) -> None:
        self.client.get("/?sort=date", name="GET /?sort=date")

    @task(1)
    def open_photo_detail(self) -> None:
        photo_ids = self._get_photo_ids()
        if not photo_ids:
            return
        photo_id = random.choice(photo_ids)
        self.client.get(f"/photo/{photo_id}/", name="GET /photo/<id>/")

    @task(3)
    def upload_photo_if_authenticated(self) -> None:
        if not self.is_authenticated:
            return

        upload_page = self.client.get("/upload/", name="GET /upload/")
        token = _extract_csrf_token(upload_page.text)
        if not token:
            return

        file_name = f"loadtest-{random.randint(1000, 9999)}.png"
        file_content = BytesIO(_build_tiny_png())
        self.client.post(
            "/upload/",
            data={
                "name": f"LoadTest {random.randint(1000, 9999)}",
                "csrfmiddlewaretoken": token,
            },
            files={"image": (file_name, file_content, "image/png")},
            headers={"Referer": f"{self.host}/upload/"},
            name="POST /upload/",
            allow_redirects=True,
        )

    @task(1)
    def delete_photo_if_authenticated(self) -> None:
        if not self.is_authenticated:
            return

        photo_ids = self._get_photo_ids()
        if not photo_ids:
            return
        photo_id = random.choice(photo_ids)
        delete_page = self.client.get(f"/photo/{photo_id}/delete/", name="GET /photo/<id>/delete/")
        token = _extract_csrf_token(delete_page.text)
        if not token:
            return

        self.client.post(
            f"/photo/{photo_id}/delete/",
            data={"csrfmiddlewaretoken": token},
            headers={"Referer": f"{self.host}/photo/{photo_id}/delete/"},
            name="POST /photo/<id>/delete/",
            allow_redirects=True,
        )

    @task(2)
    def upload_then_delete_cycle(self) -> None:
        """Ensure delete/detail endpoints are always exercised in each run."""
        if not self.is_authenticated:
            return

        upload_page = self.client.get("/upload/", name="GET /upload/ (cycle)")
        token = _extract_csrf_token(upload_page.text)
        if not token:
            return

        file_name = f"cycle-{random.randint(1000, 9999)}.png"
        file_content = BytesIO(_build_tiny_png())
        photo_name = f"Cycle {random.randint(100000, 999999)}"
        self.client.post(
            "/upload/",
            data={
                "name": photo_name,
                "csrfmiddlewaretoken": token,
            },
            files={"image": (file_name, file_content, "image/png")},
            headers={"Referer": f"{self.host}/upload/"},
            name="POST /upload/ (cycle)",
            allow_redirects=True,
        )

        photo_id = self._get_photo_id_by_name(photo_name)
        if not photo_id:
            return

        self.client.get(f"/photo/{photo_id}/", name="GET /photo/<id>/ (cycle)")
        delete_page = self.client.get(
            f"/photo/{photo_id}/delete/",
            name="GET /photo/<id>/delete/ (cycle)",
        )
        delete_token = _extract_csrf_token(delete_page.text)
        if not delete_token:
            return

        self.client.post(
            f"/photo/{photo_id}/delete/",
            data={"csrfmiddlewaretoken": delete_token},
            headers={"Referer": f"{self.host}/photo/{photo_id}/delete/"},
            name="POST /photo/<id>/delete/ (cycle)",
            allow_redirects=True,
        )
