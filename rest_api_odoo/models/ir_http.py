from werkzeug.exceptions import BadRequest

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_my_api_key(cls):
        api_key = request.httprequest.headers.get('Authorization')
        if not api_key:
            raise BadRequest('API key missing')

        if api_key.startswith('Bearer '):
            api_key = api_key[7:]

        user_id = request.env["res.users.apikeys"]._check_credentials(scope='rpc', key=api_key)
        if not user_id:
            raise BadRequest('Access token invalid')

        # take the identity of the API key user
        request.update_env(user=user_id)

        # switch to the user context
        request.update_context(**request.env.user.context_get())
