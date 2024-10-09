import json
import base64
from datetime import datetime
import logging
from odoo import http, _, models
from odoo.http import request, Response

_logger = logging.getLogger(__name__)
ERROR_METHOD_NOT_ALLOWED = _('Method Not Allowed')
ERROR_INVALID_JSON_DATA = _('Invalid JSON Data')
ERROR_NO_ID_PROVIDED = _('No ID Provided')
ERROR_RESOURCE_NOT_FOUND = _('Resource not found')


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # Convert datetime objects to string (ISO format)
            return obj.isoformat()
        elif isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')

        return super(DateTimeEncoder, self).default(obj)


def generate_response(method, model, rec_id):
    """This function is used to generate the response based on the type
    of request and the parameters given"""
    option = request.env['connection.api'].search(
        [('model_id', '=', model)], limit=1)
    model_name = option.model_id.model

    data = {}

    try:
        json_body = json.loads(request.httprequest.data)
        data = json_body
    except Exception as e:
        _logger.warning(_('No JSON Data'))

    fields = data.get('fields', False)

    if not option:
        raise ValueError(_('No Record Created for the model'))

    if method == 'GET':
        conditions = data.get('conditions', {})

        if not option.is_get:
            raise ValueError(ERROR_METHOD_NOT_ALLOWED)

        try:
            domain = []

            if rec_id != 0:
                domain.append(('id', '=', rec_id))

            if conditions:
                for field, value in conditions.items():
                    domain.append((field, '=', value))

            partner_records = request.env[str(model_name)].search_read(
                domain=domain,
                fields=fields
            )

            if not partner_records:
                raise ValueError(ERROR_RESOURCE_NOT_FOUND)

            return partner_records
        except Exception as e:
            raise ValueError(f"{ERROR_INVALID_JSON_DATA}: {str(e)}")

    if method == 'POST':
        if not option.is_post:
            raise ValueError(ERROR_METHOD_NOT_ALLOWED)

        try:
            data = json.loads(request.httprequest.data)
            new_resource = request.env[str(model_name)].create(
                data['values'])
            partner_records = request.env[
                str(model_name)].search_read(
                domain=[('id', '=', new_resource.id)],
                fields=fields
            )

            return partner_records
        except Exception as e:
            raise ValueError(f"{ERROR_INVALID_JSON_DATA}: {str(e)}")

    if method == 'PUT':
        conditions = data.get('conditions', {})

        if not option.is_put:
            raise ValueError(ERROR_METHOD_NOT_ALLOWED)

        if rec_id == 0:
            raise ValueError(ERROR_NO_ID_PROVIDED)

        resource = request.env[str(model_name)].browse(
            int(rec_id))

        if not resource.exists():
            raise ValueError(ERROR_RESOURCE_NOT_FOUND)

        check_conditions(resource, conditions)

        try:
            data = json.loads(request.httprequest.data)
            resource.write(data['values'])
            partner_records = request.env[
                str(model_name)].search_read(
                domain=[('id', '=', resource.id)],
                fields=fields
            )

            return partner_records

        except Exception as e:
            raise ValueError(f"{ERROR_INVALID_JSON_DATA}: {str(e)}")

    if method == 'DELETE':
        conditions = data.get('conditions', {})

        if not option.is_delete:
            raise ValueError(ERROR_METHOD_NOT_ALLOWED)

        if rec_id == 0:
            raise ValueError(ERROR_NO_ID_PROVIDED)

        resource = request.env[str(model_name)].browse(
            int(rec_id))

        if not resource.exists():
            raise ValueError(ERROR_RESOURCE_NOT_FOUND)

        check_conditions(resource, conditions)

        try:
            records = request.env[
                str(model_name)].search_read(
                domain=[('id', '=', resource.id)],
                fields=['id', 'display_name']
            )
            resource.unlink()

            return records
        except Exception as e:
            raise ValueError(f"{ERROR_INVALID_JSON_DATA}: {str(e)}")


def check_conditions(data, conditions):
    """
    Check if the conditions match the data attributes.
    :param data: The resource object to check.
    :param conditions: A dictionary of expected conditions.
    :raises ValueError: If any condition is not met.
    """
    # Check each property in conditions against the resource
    for key, expected_value in conditions.items():
        resource_value = getattr(data, key, None)

        if isinstance(resource_value, models.Model):
            resource_value = resource_value.id

        if resource_value != expected_value:
            raise ValueError(f"Condition not met: {key} must be {expected_value}, found {resource_value}")


class RestApi(http.Controller):
    """This is a controller which is used to generate responses based on the
    api requests"""

    @http.route(['/send_request'], type='http',
                auth='my_api_key',
                methods=['GET', 'POST', 'PUT', 'DELETE'], csrf=False)
    def fetch_data(self, **kw):
        """This controller will be called when sending a request to the
        specified url, and it will authenticate the api-key and then will
        generate the result"""
        http_method = request.httprequest.method
        model = kw.get('model')

        try:
            model_id = request.env['ir.model'].search(
                [('model', '=', model)])

            if not model_id:
                raise ValueError(_('Invalid model, check spelling or maybe the related module is not installed'))

            if not kw.get('Id'):
                rec_id = 0
            else:
                rec_id = int(kw.get('Id'))

            result = generate_response(http_method, model_id.id, rec_id)

            response_data = {
                'success': True,
                'data': result
            }

            return Response(json.dumps(response_data, cls=DateTimeEncoder), content_type='application/json', status=200)
        except Exception as e:
            _logger.error("Error: %s", e, exc_info=True)
            response_data = {'success': False, 'error': str(e)}
            return Response(json.dumps(response_data), content_type='application/json', status=500)
