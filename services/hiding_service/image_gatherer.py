import os
import pickle
from threading import Thread
from typing import Iterator

from pathlib import Path
from PIL import Image
# from services.key_handling_module import KeyHandlerUI
from utils.constants import CHUNK_SIZE
from utils.singleton_meta import SingletonMeta


class ImageGatherer(metaclass=SingletonMeta):
    path = "Identity/existingImageList.bin"
    unusedImages = set()
    usedImages = set()
    

    def __init__(self):
        if not os.path.isdir('Identity'):
            os.mkdir('Identity')

        if os.path.exists(self.path):
            self.usedImages = self.getUsedList()
        homePath = str(Path.home())
        thread = Thread(target = self.collectImages, args=(homePath, ))
        thread.start()
        # self.salt = KeyHandlerUI().salt

    def updateUsedList(self):
        with open('person_data.pkl', 'wb') as fp:
            pickle.dump(self.usedImages, fp)

    def getUsedList(self):
        with open(self.path, 'rb') as file:
            return pickle.load(file)

    def collectImages(self, search_dir='C:\\Users\\soham'):
        # for path in Path(search_dir).rglob('*.[jJ][pP][egEG]*'):
        for path in Path(search_dir).rglob('*.png'):
            try:
                with Image.open(path) as img:            
                    # fetching the dimensions
                    wid, hgt = img.size
                    capacity = int(hgt*wid*3/8) - 3  # 3 bits per pixel and then converting the ans in bytes minus 3 bytes for storing length info
                    if capacity >= CHUNK_SIZE and path not in self.usedImages:
                        self.unusedImages.add(path)
            except:
                pass
        print('collected', len(self.unusedImages))

    def nextPathIterator(self, size=1) -> Iterator[str]:
        for _ in range(size):
            newPath = self.unusedImages.pop()
            self.usedImages.add(newPath)
            yield newPath
        self.updateUsedList()