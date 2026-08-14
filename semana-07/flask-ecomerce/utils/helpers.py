import cloudinary
import cloudinary.uploader
import cloudinary.utils
import os


class CloudinaryHelper:
    # La configuracion de Cloudinary
    def __init__(self):
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True
        )

    # Funcion para subir las imagenes
    def upload_image(self, file, folder="products"):
        try:
            response = cloudinary.uploader.upload(file, folder=folder)
            # Vamos a obtener las URLS
            secure_url = response.get("secure_url")
            public_id = response.get("public_id")
            return secure_url, public_id
        except Exception as e:
            print("ERROR CLOUDINARY:", repr(e))
            return None

    def delete_image(self, public_id):
        try:
            cloudinary.uploader.destroy(public_id)
            return True
        except Exception:
            return False

    # products/mpk5tgfpenf94hfqtwjc
    # https://res.cloudinary.com/db6m1hsce/image/upload/v1786677418/products/mpk5tgfpenf94hfqtwjc.jpg
    def get_full_url(self, public_id):
        try:
            secure_url = cloudinary.utils.cloudinary_url(public_id, secure=True)
            return secure_url[0]
        except Exception:
            return None