from flask import request, jsonify, Blueprint

from . import ugc


ugc_blueprint = Blueprint('ugc_blueprint', __name__)

#curl -X POST https://xn----8hcborozt8bdd.xn--9dbq2a/test-admin-email -H Content-Type: application/json --data {"subject":"1", "body":"2"}
@ugc_blueprint.route(f'/test-admin-email', methods=['POST'])
def test_admin_email():
    j = request.json
    ugc.send_admin_email(j['subject'], j['body'])
    return jsonify({"ok": True})

@ugc_blueprint.route(f'/add-incoming-email', methods=['POST'])
def incoming_email():
    j = request.json
    if 'mail-source' not in j:
        return jsonify({'error': 1}), 401
    source = j['mail-source']
    if type(source) != str:
        return jsonify({'error': 3}), 401
    valid_sources = 's3://ses-incoming-xwehyvyd/incoming-submissions-from-net-hamishpat/',
    is_valid = False
    for valid in valid_sources:
        if source.startswith(valid):
            is_valid = True
            break
    if not is_valid:
        return jsonify({'error': 2}), 401


    parser = ugc.EmailParser()
    parser.parse(source)
    return jsonify({'success': True}), 200
