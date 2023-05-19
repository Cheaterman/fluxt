from . import api, auth


@api.get('/auth')
@auth.login_required
def authenticate():
    return ''
