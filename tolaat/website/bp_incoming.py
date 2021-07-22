from flask import request, jsonify, Blueprint

from . import incoming_email

incoming_email_blueprint = Blueprint('incoming_email_blueprint', __name__)



@incoming_email_blueprint.route(f'/service-email', methods=['POST'])
def incoming_email_f():
    j = request.json
    if 'mail-source' not in j:
        return jsonify({'error': 1}), 401
    source = j['mail-source']
    if type(source) != str:
        return jsonify({'error': 3}), 401
    valid_sources = 's3://ses-incoming-xwehyvyd/incoming-service/',
    is_valid = False
    for valid in valid_sources:
        if source.startswith(valid):
            is_valid = True
            break

    if not is_valid:
        return jsonify({'error': 2}), 401

    parser = incoming_email.EmailParser()
    parser.parse(source)
    return jsonify({'success': True}), 200