import json

import pytest
from django.urls import reverse
from rest_framework import status

from core.models import File, Header, FileHeader
from django.core.files.uploadedfile import SimpleUploadedFile


class TestFileViews:
    @pytest.fixture
    def create_file(self):
        def _create_file(user, name="test_file.csv"):
            return File.objects.create(name=name, user=user)

        return _create_file

    @pytest.mark.django_db
    def test_listFiles_authenticatedUser_success(
        self, create_file, authenticated_client, authenticated_user
    ):
        create_file(user=authenticated_user)
        create_file(user=authenticated_user, name="another_file.csv")

        url = reverse("core:file-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    @pytest.mark.django_db
    def test_createFile_validData_success(self, authenticated_client):
        url = reverse("core:file-list")
        file_content = b"header1,header2\nvalue1,value2"
        uploaded_file = SimpleUploadedFile(
            "test_file.csv", file_content, content_type="text/csv"
        )

        data = {
            "file": uploaded_file,
            "file_headers": json.dumps(
                [
                    {"name": "header1", "data_type": "string"},
                    {"name": "header2", "data_type": "string"},
                ]
            ),
        }

        response = authenticated_client.post(url, data=data)
        print(response.content)
        assert response.status_code == status.HTTP_201_CREATED
        assert File.objects.count() == 1
        assert Header.objects.count() == 2
        assert FileHeader.objects.count() == 2

    @pytest.mark.django_db
    def test_retrieveFile_existingFile_success(
        self, create_file, authenticated_client, authenticated_user
    ):
        file = create_file(user=authenticated_user)

        url = reverse("core:file-detail", kwargs={"pk": file.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == file.id
        assert response.data["name"] == file.name

    @pytest.mark.django_db
    def test_multiUpload_validFiles_success(self, authenticated_client):
        url = reverse("core:file-multi-upload")
        Header.objects.create(name="header1", data_type="string")
        Header.objects.create(name="header2", data_type="string")
        file1_content = b"header1,header2\nvalue1,value2"
        file2_content = b"header1,header2\nvalue3,value4"
        uploaded_file1 = SimpleUploadedFile(
            "test_file1.csv", file1_content, content_type="text/csv"
        )
        uploaded_file2 = SimpleUploadedFile(
            "test_file2.csv", file2_content, content_type="text/csv"
        )

        data = {"files": [uploaded_file1, uploaded_file2]}

        response = authenticated_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data
        assert File.objects.count() == 2
