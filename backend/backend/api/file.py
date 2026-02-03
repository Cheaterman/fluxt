import typing

from flask import abort, request, send_file
from flask.typing import ResponseReturnValue

from backend.model import db
from backend.model.file import EXTENSIONS, File
from backend.model.user import Role
from . import api
from .auth import Authable, auth


@api.post('/files')
@auth.login_required(role=(Role.ADMINISTRATOR, Role.USER))
def upload_file() -> ResponseReturnValue:
    upload = request.files.get('file')

    if not upload:
        abort(400, 'expected_file')

    file = File.from_upload(upload)
    db.session.commit()

    return {'filename': file.filename}, 201


@api.delete('/files/<file:file>')
@auth.login_required(role=(Role.ADMINISTRATOR, Role.USER))
def delete_file(file: File) -> ResponseReturnValue:
    current_user = typing.cast(Authable, auth.current_user())

    if (
        current_user.get_role() is Role.USER
        and file.author is not current_user
    ):
        abort(403, 'invalid_author')

    db.session.delete(file)
    db.session.commit()
    return '', 204


EXTENSION_TO_MIMETYPE = {
    extension: mimetype
    for mimetype, extension in EXTENSIONS.items()
}


@api.get('/files/<file:file>')
def download_file(file: File) -> ResponseReturnValue:
    path = file.path
    mimetype = EXTENSION_TO_MIMETYPE[path.suffix[1:]]
    # Send an open file to let frontend pick a filename, see note in:
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#download
    # Flask would otherwise auto-populate the filename header
    return send_file(path.resolve().open('rb'), mimetype=mimetype)
