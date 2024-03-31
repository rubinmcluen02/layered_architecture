from flask import Blueprint, request, jsonify
from services.authorization import authorization
from service_instances import authentication, mapper, extraction, datastorage, validation, domain

status_blueprint = Blueprint('status', __name__)

@status_blueprint.route('/admin/authentication-status', methods=['GET', 'POST'])
def change_auth_status():
    if request.method == 'POST':
        new_status = request.json.get('status')
        if new_status is not None:
            if new_status:
                authentication.start()
            else:
                authentication.stop()
            return jsonify({"success": True, "authentication_status": new_status}), 200
    elif request.method == 'GET':
        status = authentication.check_status()
        return jsonify({"authentication_status": status}), 200
    return jsonify({"success": False, "error": "Invalid request"}), 400

@status_blueprint.route('/admin/mapper-status', methods=['GET', 'POST'])
def change_mapper_status():
    if request.method == 'POST':
        new_status = request.json.get('status')
        if new_status is not None:
            if new_status:
                mapper.start()
            else:
                mapper.stop()
            return jsonify({"success": True, "mapper_status": new_status}), 200
    elif request.method == 'GET':
        status = mapper.check_status()
        return jsonify({"mapper_status": status}), 200
    return jsonify({"success": False, "error": "Invalid request"}), 400

@status_blueprint.route('/admin/extraction-status', methods=['GET', 'POST'])
def change_extraction_status():
    if request.method == 'POST':
        new_status = request.json.get('status')
        if new_status is not None:
            if new_status:
                extraction.start()
            else:
                extraction.stop()
            return jsonify({"success": True, "extraction_status": new_status}), 200
    elif request.method == 'GET':
        status = extraction.check_status()
        return jsonify({"extraction_status": status}), 200
    return jsonify({"success": False, "error": "Invalid request"}), 400

@status_blueprint.route('/admin/datastorage-status', methods=['GET', 'POST'])
def change_datastorage_status():
    if request.method == 'POST':
        new_status = request.json.get('status')
        if new_status is not None:
            if new_status:
                datastorage.start()
            else:
                datastorage.stop()
            return jsonify({"success": True, "datastorage_status": new_status}), 200
    elif request.method == 'GET':
        status = datastorage.check_status()
        return jsonify({"datastorage_status": status}), 200
    return jsonify({"success": False, "error": "Invalid request"}), 400

@status_blueprint.route('/admin/validation-status', methods=['GET', 'POST'])
def change_validation_status():
    if request.method == 'POST':
        new_status = request.json.get('status')
        if new_status is not None:
            if new_status:
                validation.start()
            else:
                validation.stop()
            return jsonify({"success": True, "validation_status": new_status}), 200
    elif request.method == 'GET':
        status = validation.check_status()
        return jsonify({"validation_status": status}), 200
    return jsonify({"success": False, "error": "Invalid request"}), 400

@status_blueprint.route('/admin/domain-status', methods=['GET', 'POST'])
def change_domain_status():
    if request.method == 'POST':
        new_status = request.json.get('status')
        if new_status is not None:
            if new_status:
                domain.start()
            else:
                domain.stop()
            return jsonify({"success": True, "domain_status": new_status}), 200
    elif request.method == 'GET':
        status = domain.check_status()
        return jsonify({"domain_status": status}), 200
    return jsonify({"success": False, "error": "Invalid request"}), 400

@status_blueprint.route('/admin/authorization-status', methods=['GET', 'POST'])
def change_authorization_status():
    if request.method == 'POST':
        new_status = request.json.get('status')
        if new_status is not None:
            if new_status:
                authorization.start()
            else:
                authorization.stop()
            return jsonify({"success": True, "authorization_status": new_status}), 200
    elif request.method == 'GET':
        status = authorization.check_status()
        return jsonify({"authorization_status": status}), 200
    return jsonify({"success": False, "error": "Invalid request"}), 400



# Bash profile commands to start/stop/check services
"""
function authentication_start() {
    curl -X POST http://localhost:5000/admin/authentication-status -H "Content-Type: application/json" -d '{"status": true}'
}

function authentication_stop() {
    curl -X POST http://localhost:5000/admin/authentication-status -H "Content-Type: application/json" -d '{"status": false}'
}

function mapper_start() {
    curl -X POST http://localhost:5000/admin/mapper-status -H "Content-Type: application/json" -d '{"status": true}'
}

function mapper_stop() {
    curl -X POST http://localhost:5000/admin/mapper-status -H "Content-Type: application/json" -d '{"status": false}'
}

function extraction_start() {
    curl -X POST http://localhost:5000/admin/extraction-status -H "Content-Type: application/json" -d '{"status": true}'
}

function extraction_stop() {
    curl -X POST http://localhost:5000/admin/extraction-status -H "Content-Type: application/json" -d '{"status": false}'
}

function datastorage_start() {
    curl -X POST http://localhost:5000/admin/datastorage-status -H "Content-Type: application/json" -d '{"status": true}'
}

function datastorage_stop() {
    curl -X POST http://localhost:5000/admin/datastorage-status -H "Content-Type: application/json" -d '{"status": false}'
}

function validation_start() {
    curl -X POST http://localhost:5000/admin/validation-status -H "Content-Type: application/json" -d '{"status": true}'
}

function validation_stop() {
    curl -X POST http://localhost:5000/admin/validation-status -H "Content-Type: application/json" -d '{"status": false}'
}

function domain_start() {
    curl -X POST http://localhost:5000/admin/domain-status -H "Content-Type: application/json" -d '{"status": true}'
}

function domain_stop() {
    curl -X POST http://localhost:5000/admin/domain-status -H "Content-Type: application/json" -d '{"status": false}'
}

function authorization_start() {
    curl -X POST http://localhost:5000/admin/authorization-status -H "Content-Type: application/json" -d '{"status": true}'
}

function authorization_stop() {
    curl -X POST http://localhost:5000/admin/authorization-status -H "Content-Type: application/json" -d '{"status": false}'
}

function authentication_check() {
    curl http://localhost:5000/admin/authentication-status
}

function mapper_check() {
    curl http://localhost:5000/admin/mapper-status
}

function extraction_check() {
    curl http://localhost:5000/admin/extraction-status
}

function datastorage_check() {
    curl http://localhost:5000/admin/datastorage-status
}

function validation_check() {
    curl http://localhost:5000/admin/validation-status
}

function domain_check() {
    curl http://localhost:5000/admin/domain-status
}

function authorization_check() {
    curl http://localhost:5000/admin/authorization-status
}

function services_on() {
    curl -X POST http://localhost:5000/admin/authentication-status -H "Content-Type: application/json" -d '{"status": true}'
    curl -X POST http://localhost:5000/admin/mapper-status -H "Content-Type: application/json" -d '{"status": true}'
    curl -X POST http://localhost:5000/admin/extraction-status -H "Content-Type: application/json" -d '{"status": true}'
    curl -X POST http://localhost:5000/admin/datastorage-status -H "Content-Type: application/json" -d '{"status": true}'
    curl -X POST http://localhost:5000/admin/validation-status -H "Content-Type: application/json" -d '{"status": true}'
    curl -X POST http://localhost:5000/admin/domain-status -H "Content-Type: application/json" -d '{"status": true}'
    curl -X POST http://localhost:5000/admin/authorization-status -H "Content-Type: application/json" -d '{"status": true}'
    echo "All services turned on."
}

function services_off() {
    curl -X POST http://localhost:5000/admin/authentication-status -H "Content-Type: application/json" -d '{"status": false}'
    curl -X POST http://localhost:5000/admin/mapper-status -H "Content-Type: application/json" -d '{"status": false}'
    curl -X POST http://localhost:5000/admin/extraction-status -H "Content-Type: application/json" -d '{"status": false}'
    curl -X POST http://localhost:5000/admin/datastorage-status -H "Content-Type: application/json" -d '{"status": false}'
    curl -X POST http://localhost:5000/admin/validation-status -H "Content-Type: application/json" -d '{"status": false}'
    curl -X POST http://localhost:5000/admin/domain-status -H "Content-Type: application/json" -d '{"status": false}'
    curl -X POST http://localhost:5000/admin/authorization-status -H "Content-Type: application/json" -d '{"status": false}'
    echo "All layers turned off."
}

function check_services_status() {
    echo -n "Authentication Layer: "
    curl -s http://localhost:5000/admin/authentication-status | grep -o '"authentication_status":[^,]*' | cut -d ':' -f2

    echo -n "Mapper Layer: "
    curl -s http://localhost:5000/admin/mapper-status | grep -o '"mapper_status":[^,]*' | cut -d ':' -f2

    echo -n "Extraction Layer: "
    curl -s http://localhost:5000/admin/extraction-status | grep -o '"extraction_status":[^,]*' | cut -d ':' -f2

    echo -n "Data Storage Layer: "
    curl -s http://localhost:5000/admin/datastorage-status | grep -o '"datastorage_status":[^,]*' | cut -d ':' -f2

    echo -n "Validation Layer: "
    curl -s http://localhost:5000/admin/validation-status | grep -o '"validation_status":[^,]*' | cut -d ':' -f2

    echo -n "Domain Layer: "
    curl -s http://localhost:5000/admin/domain-status | grep -o '"domain_status":[^,]*' | cut -d ':' -f2

    echo -n "Authorization Layer: "
    curl -s http://localhost:5000/admin/authorization-status | grep -o '"authorization_status":[^,]*' | cut -d ':' -f2
}
"""