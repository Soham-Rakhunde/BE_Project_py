import base64, os

class DataHandler:
    file_path: str = None
    data: bytes = None
    cipher: bytes = None
    AESNonce: bytes = None
    MACtag: bytes = None

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.read_file()

    def read_file(self):
        with open(self.file_path, 'rb') as f:
            # self.data = base64.b64encode(f.read())
            self.data = f.read()
            print("File Size:",len(self.data))

    def write_file(self, save_path = 'C:\\Users\\soham\\OneDrive\\Desktop\\3433.jpg'):
        # TODO ask for file path
        with open(save_path, 'wb') as f:
            f.write(self.data)
            # self.data = base64.b64decode(f.read())
        print(os.path.exists(save_path))
        print("File saved at", save_path)