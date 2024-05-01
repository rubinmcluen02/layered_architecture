from flask import request, jsonify
from service_instances import extraction

def init_appointment_routes(app):
    @app.route('/get_appointment', methods=['GET'])
    def handle_get_appointment():
        appointment_id = request.args.get('id')
        if not appointment_id:
            return jsonify({'status': 'error', 'message': 'No appointment ID provided'}), 400

        try:
            appointment = extraction.get_appointment_from_db(appointment_id)
            if appointment:
                FHIR_keys = {
                    'status': 'Pending',
                    'serviceCategory': 'CheckUp',
                    'cancellationReason': 'NULL',
                    'description': 'NULL',
                    'duration': 'NULL'
                }
                appointment.update(FHIR_keys)
                return jsonify({'status': 'success', 'data': appointment}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
