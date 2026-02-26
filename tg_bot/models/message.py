
class Message:
    def __init__(self, role: str, message: str, file_id: str = None):
        self.role = role
        self.message = message
        if file_id is not None:
            self.file_path = file_id