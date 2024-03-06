from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/payments/pix", methods=["POST"])
def create_pix_payment():
    return jsonify({"message": "PAGAMENTO PIX CRIADO"})

@app.route("/payments/pix/confirmation", methods=["POST"])
def confirmation_pix_payment():
    return jsonify({"message": "PAGAMENTO PIX CONFIRMADO"})

@app.route("/payments/pix/<int:payment_id>", methods=["GET"])
def pix_payment_page():
    return jsonify({"message": "PAGAMENTO PIX"})

if __name__ == "main":
    app.run(debug=True)
