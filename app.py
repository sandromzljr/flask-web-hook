from flask import Flask, jsonify, request, send_file, render_template
from flask_socketio import SocketIO
from repository.database import db
from db_models.payment import Payment
from datetime import datetime, timedelta
from payments.pix import Pix

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "SECRET_KEY_WEBSOCKET"

db.init_app(app)
socketio = SocketIO(app)

@app.route("/payments/pix", methods=["POST"])
def create_pix_payment():
    response_json = request.get_json()

    if "value" not in response_json:
        return jsonify({"message": "VALOR INVÁLIDO"}), 400

    expiration_date = datetime.now() + timedelta(minutes=30)

    new_payment = Payment(value=response_json["value"], expiration_date=expiration_date)

    pix_obj = Pix()
    payment_pix_data = pix_obj.create_payment()
    new_payment.bank_payment_id = payment_pix_data["bank_payment_id"]
    new_payment.qr_code = payment_pix_data["qr_code_path"]

    db.session.add(new_payment)
    db.session.commit()

    return jsonify({"message": "PAGAMENTO PIX CRIADO", "payment": new_payment.to_dict()})

@app.route("/payments/pix/qr_code/<file_name>", methods=["GET"])
def get_image(file_name):
    return send_file(f"static/img/{file_name}.png", mimetype="image/png")

@app.route("/payments/pix/confirmation", methods=["POST"])
def confirmation_pix_payment():
    response_json = request.get_json()

    if "bank_payment_id" not in response_json and "value" not in response_json:
        return jsonify({"message": "NÃO FOI POSSÍVEL IDENTIFICAR O PIX"}), 400

    payment = Payment.query.filter_by(bank_payment_id=response_json.get("bank_payment_id")).first()

    if not payment or payment.paid:
        return jsonify({"message": "NÃO FOI POSSÍVEL ENCONTRAR O PAGAMENTO PIX"}), 404

    if response_json.get("value") != payment.value:
        return jsonify({"message": "NÃO FOI POSSÍVEL VALIDAR O PAGAMENTO PIX"}), 400

    payment.paid = True
    db.session.commit()

    socketio.emit(f"pagamento-confirmado-{payment.id}")

    return jsonify({"message": "PAGAMENTO PIX CONFIRMADO"})

@app.route("/payments/pix/<int:payment_id>", methods=["GET"])
def pix_payment_page(payment_id):
    payment = Payment.query.get(payment_id)

    if not payment:
        return render_template("404.html")

    if payment.paid:
        return render_template("confirmed_payment.html", \
                            payment_id=payment.id, \
                            value=payment.value, \
                            host="http://127.0.0.1:5000", \
                            qr_code=payment.qr_code)

    return render_template("payment.html", \
                            payment_id=payment.id, \
                            value=payment.value, \
                            host="http://127.0.0.1:5000", \
                            qr_code=payment.qr_code)

#websockets
@socketio.on("connect")
def handle_connect():
    print("CLIENTE CONECTADO AO SERVIDOR")

@socketio.on("disconnect")
def handle_disconnect():
    print("CLIENTE DESCONECTADO DO SERVIDOR")

if __name__ == "__main__":
    # app.run(debug=True)
    socketio.run(app, debug=True)
