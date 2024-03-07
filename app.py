from flask import Flask, jsonify, request, send_file, render_template
from repository.database import db
from db_models.payment import Payment
from datetime import datetime, timedelta
from payments.pix import Pix

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "SECRET_KEY_WEBSOCKET"

db.init_app(app)

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

@app.route("/payments/pix/qrcode/<file_name>", methods=["GET"])
def get_image(file_name):
    return send_file(f"static/img/{file_name}.png", mimetype="image/png")

@app.route("/payments/pix/confirmation", methods=["POST"])
def confirmation_pix_payment():
    return jsonify({"message": "PAGAMENTO PIX CONFIRMADO"})

@app.route("/payments/pix/<int:payment_id>", methods=["GET"])
def pix_payment_page(payment_id):
    return render_template("payment.html")

if __name__ == "__main__":
    app.run(debug=True)
