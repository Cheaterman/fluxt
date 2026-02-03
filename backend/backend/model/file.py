from __future__ import annotations
import datetime
import pathlib
import uuid
from typing import Self

import magic
from flask import abort, make_response
from sqlalchemy import Connection, ForeignKey, event, func
from sqlalchemy.orm import (
    Mapped,
    Mapper,
    Session,
    mapped_column,
    object_session,
    relationship,
)
from werkzeug.datastructures import FileStorage
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename

from . import db


EXTENSIONS = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'video/mp4': 'mp4',
    'video/webm': 'webm',
    'application/pdf': 'pdf',
    (
        'application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.sheet'
    ): 'xlsx',
}


def get_extension(file: FileStorage) -> str | None:
    data = file.read(2048)
    file.seek(0)
    return EXTENSIONS.get(magic.from_buffer(data, mime=True))


class File(db.Model):  # type: ignore
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creation_date: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )
    author_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('user.id'))
    filename: Mapped[str] = mapped_column(unique=True, index=True)
    original_filename: Mapped[str]

    author: Mapped[User | None] = relationship(back_populates='files')

    @property
    def path(self) -> pathlib.Path:
        return pathlib.Path('files', self.filename)

    @classmethod
    def from_upload(cls, upload: FileStorage) -> Self:
        extension = get_extension(upload)

        if not extension:
            abort(400, 'invalid_file')

        self = cls()
        self.filename = f'pending_id.{extension}'
        self.original_filename = secure_filename(upload.filename or '')
        db.session.add(self)
        db.session.flush()
        self.filename = f'{self.id}.{extension}'

        upload.save(self.path)
        return self


@event.listens_for(File, 'after_delete')
def mark_deleted_files(
    mapper: Mapper[File],
    connection: Connection,
    target: File,
) -> None:
    session = object_session(target)

    if session is None:
        return

    session.info.setdefault(
        'deleted_file_paths',
        [],
    ).append(target.path)


@event.listens_for(Session, 'after_commit')
def unlink_deleted_files(session: Session) -> None:
    file_path: pathlib.Path

    for file_path in session.info.pop('deleted_file_paths', []):
        file_path.unlink(missing_ok=True)


class FileConverter(BaseConverter):
    def to_python(self, value: str) -> File:
        file = db.session.query(File).filter_by(filename=value).one_or_none()

        if not file:
            abort(make_response({'message': 'file_not_found'}, 404))

        return file

    def to_url(self, value: File) -> str:
        return value.filename


from .user import User  # noqa: E402
