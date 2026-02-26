from telegram import Update


class ImageBatch:
    def __init__(self, chat_id: int, message: str, first_image_path: str, update: Update, timeout: int = 20):
        self.chat_id = chat_id
        self.message = message
        self.image_paths = [first_image_path]
        self.update = update
        self.timeout = timeout

    def add_image(self, image_path: str):
        self.image_paths.append(image_path)

    def set_update(self, update):
        self.update = update