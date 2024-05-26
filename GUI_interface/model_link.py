from flask import Flask, send_file

app = Flask(__name__)
5
@app.route('/')
def siva():
    return "Hi! this is running on Siva's Laptop"

# Define routes for downloading files
@app.route('/model1')
def download_model1():
    # Assuming model1 is located in the same directory as this script
    file_path = 'models/1.pt'
    return send_file(file_path, as_attachment=True)

@app.route('/model2')
def download_model2():
    # Assuming model2 is located in the same directory as this script
    file_path = 'models/2.pt'
    return send_file(file_path, as_attachment=True)

@app.route('/model3')
def download_model3():
    # Assuming model3 is located in the same directory as this script
    file_path = 'models/3.pt'
    return send_file(file_path, as_attachment=True)

@app.route('/model4')
def download_model4():
    # Assuming model4 is located in the same directory as this script
    file_path = 'models/4.pt'
    return send_file(file_path, as_attachment=True)

@app.route('/update_status')
def update_status():
    # Assuming model4 is located in the same directory as this script
    # file_path = 'models/4.pt'
    return "Update Not_Available!"

@app.route('/gui')
def gui():
    # Assuming model4 is located in the same directory as this script
    file_path = 'gui.py'
    return send_file(file_path, as_attachment=True)

@app.route('/config')
def config():
    # Assuming model4 is located in the same directory as this script
    file_path = 'config.db'
    return send_file(file_path, as_attachment=True)

@app.route('/configuration')
def configuration():
    # Assuming model4 is located in the same directory as this script
    file_path = 'configuration.py'
    return send_file(file_path, as_attachment=True)

@app.route('/db')
def txt():
    # Assuming model4 is located in the same directory as this script
    file_path = 'db.txt'
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(port=3553)
