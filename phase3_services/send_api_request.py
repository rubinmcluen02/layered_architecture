from flask import jsonify, request
import requests

def send_request_route(app):
    @app.route('/send_request', methods=['GET'])
    def send_request():
        appointment_id = request.args.get('id')
        if not appointment_id:
            return jsonify({'status': 'error', 'message': 'No appointment ID provided'}), 400
        
        try:
            response = requests.get(f'http://localhost:5001/get_appointment?id={appointment_id}')
            response.raise_for_status()
            response_data = response.json()
            
            from .store_api_data import store_data
            store_data(response_data)
            return jsonify({"status": "Success", "message": "Data stored successfully"}), 200

        except requests.HTTPError as http_err:
            return jsonify({"status": "Error", "message": f"HTTP error occurred: {http_err}"}), 500

        except Exception as err:
            return jsonify({"status": "Error", "message": f"General error occurred: {err}"}), 500

def init_send_request_route(app):
    send_request_route(app)
