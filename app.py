from flask import Flask, render_template, request, jsonify
import subprocess
import os
import logging

# Initialize Flask app
app = Flask(__name__, static_url_path='/static')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/alive', methods=['GET'])
def alive():
    logging.debug("Received a GET request on /alive endpoint.")
    response = "I'm alive!"
    logging.debug(f"Responding with: {response}")
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session_id = request.form.get('session_id')
        new_username = request.form.get('new_username')

        logging.debug(f"Received POST request with session_id={session_id} and new_username={new_username}")

        if not session_id or not new_username:
            logging.warning("Missing session_id or new_username in POST data")
            response = {"error": "Missing session_id or new_username"}
            logging.debug(f"Responding with: {response}")
            return jsonify(response), 400

        try:
            script_command = ["python", "tiktok.py", session_id, new_username]
            logging.debug(f"Executing command: {' '.join(script_command)}")

            # Execute the tiktok.py script with the provided session ID and new username
            result = subprocess.run(
                script_command,
                capture_output=True,
                text=True
            )

            # Log the command output
            logging.debug(f"Command output: {result.stdout}")
            logging.debug(f"Command error (if any): {result.stderr}")

            if result.returncode == 0:
                logging.info("Script executed successfully.")
                response = {"message": f"Script executed successfully: {result.stdout}"}
                logging.debug(f"Responding with: {response}")
                return jsonify(response)
            else:
                logging.error(f"Script execution failed with return code {result.returncode}")
                response = {"error": f"Script execution failed: {result.stderr}"}
                logging.debug(f"Responding with: {response}")
                return jsonify(response), 500
        except FileNotFoundError as e:
            logging.exception("FileNotFoundError: The tiktok.py script was not found.")
            response = {"error": "Script file not found"}
            logging.debug(f"Responding with: {response}")
            return jsonify(response), 404
        except Exception as e:
            logging.exception("An unexpected error occurred.")
            response = {"error": f"An error occurred: {str(e)}"}
            logging.debug(f"Responding with: {response}")
            return jsonify(response), 500

    logging.debug("Received GET request, rendering index.html.")
    return render_template('index.html')

if __name__ == "__main__":
    logging.debug("Starting Flask server directly in the main thread.")
    
    # Log environment variables (be careful with sensitive information)
    logging.debug("Environment variables:")
    for key, value in os.environ.items():
        logging.debug(f"{key}: {value}")

    app.run(host='0.0.0.0', port=8081, debug=True)

    try:
        while True:
            logging.debug("Keeping the Repl alive...")
            time.sleep(15)  # Sleep for 15 seconds before printing again
    except KeyboardInterrupt:
        logging.info("Repl keep-alive loop interrupted, shutting down.")
