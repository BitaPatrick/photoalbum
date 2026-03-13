from io import BytesIO
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Photo


class PhotoAlbumTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="secret123")

    def test_photo_list_default_sort_is_date_desc(self):
        old = Photo.objects.create(name="Old", image_url="https://x/old.png", storage_path="old.png")
        new = Photo.objects.create(name="New", image_url="https://x/new.png", storage_path="new.png")

        response = self.client.get(reverse("photo_list"))

        self.assertEqual(response.status_code, 200)
        photos = list(response.context["photos"])
        self.assertEqual(photos[0].id, new.id)
        self.assertEqual(photos[1].id, old.id)

    def test_photo_list_sort_by_name(self):
        Photo.objects.create(name="Zulu", image_url="https://x/z.png", storage_path="z.png")
        Photo.objects.create(name="Alpha", image_url="https://x/a.png", storage_path="a.png")

        response = self.client.get(reverse("photo_list"), {"sort": "name"})

        self.assertEqual(response.status_code, 200)
        names = [p.name for p in response.context["photos"]]
        self.assertEqual(names, ["Alpha", "Zulu"])

    def test_photo_detail(self):
        photo = Photo.objects.create(name="One", image_url="https://x/1.png", storage_path="1.png")

        response = self.client.get(reverse("photo_detail", args=[photo.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["photo"].pk, photo.pk)

    def test_upload_requires_login(self):
        response = self.client.get(reverse("photo_upload"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_delete_requires_login(self):
        photo = Photo.objects.create(name="One", image_url="https://x/1.png", storage_path="1.png")

        response = self.client.get(reverse("photo_delete", args=[photo.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_logout_post_redirects_to_home(self):
        self.client.login(username="tester", password="secret123")
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("photo_list"))

    def test_register_page_and_post(self):
        response_get = self.client.get(reverse("register"))
        self.assertEqual(response_get.status_code, 200)

        response_post = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(response_post.url, reverse("photo_list"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    @patch("album.views.get_client")
    def test_upload_authenticated_creates_photo(self, mock_get_client):
        self.client.login(username="tester", password="secret123")

        mock_bucket = MagicMock()
        mock_bucket.get_public_url.return_value = "https://cdn.example.com/photo.png"

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket

        mock_client = MagicMock()
        mock_client.storage = mock_storage
        mock_get_client.return_value = mock_client

        image_bytes = BytesIO()
        Image.new("RGB", (1, 1), color="white").save(image_bytes, format="PNG")
        image = SimpleUploadedFile("tiny.png", image_bytes.getvalue(), content_type="image/png")

        response = self.client.post(
            reverse("photo_upload"),
            {"name": "Uploaded", "image": image},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("photo_list"))
        self.assertEqual(Photo.objects.count(), 1)

        photo = Photo.objects.first()
        self.assertEqual(photo.name, "Uploaded")
        self.assertEqual(photo.image_url, "https://cdn.example.com/photo.png")
        self.assertTrue(photo.storage_path)

        self.assertEqual(mock_storage.from_.call_count, 2)
        mock_bucket.upload.assert_called_once()

    @patch("album.views.get_client")
    def test_delete_authenticated_deletes_photo_and_storage_object(self, mock_get_client):
        self.client.login(username="tester", password="secret123")

        photo = Photo.objects.create(
            name="DeleteMe",
            image_url="https://cdn.example.com/d.png",
            storage_path="path/in/bucket.png",
        )

        mock_bucket = MagicMock()

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket

        mock_client = MagicMock()
        mock_client.storage = mock_storage
        mock_get_client.return_value = mock_client

        response = self.client.post(reverse("photo_delete", args=[photo.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("photo_list"))
        self.assertFalse(Photo.objects.filter(pk=photo.pk).exists())
        mock_bucket.remove.assert_called_once_with(["path/in/bucket.png"])
