import uuid
import qrcode

class Pix:
    def __init__(self) -> None:
        pass

    def create_payment(self, base_dir=""):
        # Gerando um uuid aleatório
        bank_payment_id = str(uuid.uuid4())

        # Gerando um qr code e salvando na pasta static
        # hash_payment = f"hash_payment_{bank_payment_id}"
        hash_payment = "https://github.com/sandromzljr/flask-web-hook"

        img = qrcode.make(hash_payment)
        img.save(f"{base_dir}static/img/qr_code_payment_{bank_payment_id}.png")

        return {
            "bank_payment_id": bank_payment_id,
            "qr_code_path": f"qr_code_payment_{bank_payment_id}"
        }
