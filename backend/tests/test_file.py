from __future__ import annotations

from io import BytesIO
from pathlib import Path
from unittest.mock import Mock

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy.session import Session
from sqlalchemy.orm import scoped_session

from backend.model.file import (
    File,
    FileConverter,
    mark_deleted_files,
    unlink_deleted_files,
)
from backend.model.user import User


def test_upload_file_expected_file(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    response = test_client.post('/files')
    assert response.status_code == 400
    assert response.json == {'message': 'expected_file'}


def test_upload_file_invalid_file(
    test_client: FlaskClient,
    admin_session: None,
) -> None:
    response = test_client.post(
        '/files',
        data={'file': (BytesIO(b'not-a-real-file'), 'file.bin')},
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    assert response.json == {'message': 'invalid_file'}


def test_upload_file_success(
    test_client: FlaskClient,
    admin_session: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        File,
        'path',
        property(lambda self: tmp_path / self.filename),
    )

    response = test_client.post(
        '/files',
        data={
            'file': (
                BytesIO(b'%PDF-1.7\n1 0 obj\n<<>>\nendobj\n'),
                'report.pdf',
            ),
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 201
    data = response.get_json()
    assert isinstance(data, dict)
    assert data['filename'].endswith('.pdf')


def test_delete_file_invalid_author(
    test_client: FlaskClient,
    user_session: None,
    db_session: scoped_session[Session],
    user: User,
    other_user: User,
) -> None:
    file = File()
    file.filename = 'other-file.pdf'
    file.original_filename = 'other.pdf'
    file.author = other_user
    db_session.add(file)
    db_session.flush()

    response = test_client.delete(f'/files/{file.filename}')
    assert response.status_code == 403
    assert response.json == {'message': 'invalid_author'}

    file.author = user
    db_session.flush()
    response = test_client.delete(f'/files/{file.filename}')
    assert response.status_code == 204


def test_download_file(
    test_client: FlaskClient,
    db_session: scoped_session[Session],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file = File()
    file.filename = 'download-file.pdf'
    file.original_filename = 'download.pdf'
    db_session.add(file)
    db_session.flush()

    path = tmp_path / file.filename
    path.write_bytes(b'hello-download')

    monkeypatch.setattr(File, 'path', property(lambda self: path))

    response = test_client.get(f'/files/{file.filename}')
    assert response.status_code == 200
    assert response.data == b'hello-download'
    response.close()


def test_download_file_not_found(
    test_client: FlaskClient,
) -> None:
    response = test_client.get('/files/missing-file.pdf')
    assert response.status_code == 404
    assert response.get_json() == {'message': 'file_not_found'}


def test_mark_deleted_files_tracks_deleted_path(
    db_session: scoped_session[Session],
) -> None:
    file = File()
    file.filename = 'orphan.pdf'
    file.original_filename = 'orphan.pdf'
    db_session.add(file)
    db_session.flush()

    mark_deleted_files(Mock(), Mock(), file)

    deleted_paths = db_session.info['deleted_file_paths']
    assert isinstance(deleted_paths, list)
    assert file.path in deleted_paths


def test_mark_deleted_files_without_session() -> None:
    file = File()
    file.filename = 'no-session.pdf'
    file.original_filename = 'no-session.pdf'
    mark_deleted_files(Mock(), Mock(), file)


def test_unlink_deleted_files(
    db_session: scoped_session[Session],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / 'deleted.pdf'
    file_path.write_bytes(b'temp')

    session = db_session()
    session.info['deleted_file_paths'] = [file_path]
    unlink_deleted_files(session)

    assert not file_path.exists()
    assert session.info == {}


def test_file_converter_to_url(app: Flask) -> None:
    file = File()
    file.filename = 'converter.pdf'
    file.original_filename = 'converter.pdf'
    converter = FileConverter(app.url_map)
    assert converter.to_url(file) == 'converter.pdf'
