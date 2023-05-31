import io
from typing import IO, Union

from PIL import Image
from bitstring import BitArray, Bits
from typing import IO, Iterator, Union

from stegano.lsb.generators import identity



def setlsb(component: int, bit: str) -> int:
    """Set Least Significant Bit of a colour component."""
    return component & ~1 | int(bit)


def open_image(fname_or_instance: Union[str, IO[bytes]]):
    """Opens a Image and returns it.

    :param fname_or_instance: Can either be the location of the image as a
                              string or the Image.Image instance itself.
    """
    if isinstance(fname_or_instance, Image.Image):
        return fname_or_instance

    return Image.open(fname_or_instance)


class StegEncoder:
    def __init__(
        self,
        input_image: Union[str, IO[bytes]],
        message: bytes,
        auto_convert_rgb: bool = False,
    ):
        self._index = 0

        message_length = len(message)
        assert message_length != 0, "message length is zero"

        image = open_image(input_image)

        if image.mode not in ["RGB", "RGBA"]:
            if not auto_convert_rgb:
                print("The mode of the image is not RGB. Mode is {}".format(image.mode))
                answer = input("Convert the image to RGB ? [Y / n]\n") or "Y"
                if answer.lower() == "n":
                    raise Exception("Not a RGB image.")

            image = image.convert("RGB")

        self.encoded_image = image.copy()
        image.close()


        PAD_SIZE = (3 - ((message_length+3)*8 % 3)) % 3
        # print("PAD_SIZE", PAD_SIZE)
        # pad_size_bin = PAD_SIZE.to_bytes(length=1, byteorder='big')

        buffer = io.BytesIO()
        buffer.write(message_length.to_bytes(length=3, byteorder='big'))
        # buffer.write(pad_size_bin)
        buffer.write(message)

        self._message_bits = Bits(buffer).bin + '0'*PAD_SIZE
        # print("msgbits", self._message_bits, len(self._message_bits))
        width, height = self.encoded_image.size
        npixels = width * height
        self._len_message_bits = len(self._message_bits)

        if self._len_message_bits > npixels * 3:
            print(self._len_message_bits , npixels * 3 )
            raise Exception(
                "The message you want to hide is too long: {}".format(message_length)
            )

    def encode_another_pixel(self):
        return True if self._index + 3 <= self._len_message_bits else False

    def encode_pixel(self, coordinate: tuple):
        # Get the colour component.
        r, g, b, *a = self.encoded_image.getpixel(coordinate)
        r = setlsb(r, self._message_bits[self._index])
        g = setlsb(g, self._message_bits[self._index + 1])
        b = setlsb(b, self._message_bits[self._index + 2])

        # Save the new pixel
        if self.encoded_image.mode == "RGBA":
            self.encoded_image.putpixel(coordinate, (r, g, b, *a))
        else:
            self.encoded_image.putpixel(coordinate, (r, g, b))

        self._index += 3

    def encode(
        self,
        # image: Union[str, IO[bytes]],
        # message: str,
        generator: Union[None, Iterator[int]] = None,
        shift: int = 0,
        # auto_convert_rgb: bool = True,
    ):
        # hider = StegEncoder(image, message, auto_convert_rgb)
        width = self.encoded_image.width

        if not generator:
            generator = identity()

        while shift != 0:
            next(generator)
            shift -= 1

        while self.encode_another_pixel():
            generated_number = next(generator)

            col = generated_number % width
            row = int(generated_number / width)
            self.encode_pixel((col, row))
        del generator
        return self.encoded_image



class StegDecoder:
    def __init__(self, encoded_image: Union[str, IO[bytes]]):
        self.encoded_image : Image = open_image(encoded_image)
        self._buff, self._count = BitArray(), 0
        self.semib = ""
        self.secret_message : bytes = None
        self._MSG_LENGTH = 0
        self._length_find_flag = True

    def decode_pixel(self, coordinate: tuple):
        # pixel = [r, g, b] or [r,g,b,a]
        pixel = self.encoded_image.getpixel(coordinate)
        if self.encoded_image.mode == "RGBA":
            pixel = pixel[:3]  # ignore the alpha

        for color in pixel:
            self.semib += '1' if (color & 1) else '0'
            self._count += 1
            if self._count%8 == 0:
                self._buff.append(BitArray(bin=self.semib))
                self.semib = ""
            if not self._length_find_flag:
                if self._count == 8*self._MSG_LENGTH:
                    self.secret_message = self._buff.bytes
                    self.encoded_image.close()
                    return True
            else:
                if self._count == 3*8: # 3 bytes for the message length
                    msg_len_bin = self._buff.bytes
                    self._MSG_LENGTH = int.from_bytes(msg_len_bin, byteorder ='big')
                    # print("Message length", self._MSG_LENGTH, self._buff)
                    self._buff = BitArray()
                    self._length_find_flag = False
                    self._count = 0
        return False
    
    
    def decode(
        self,
        # encoded_image: Union[str, IO[bytes]],
        generator: Union[None, Iterator[int]] = None,
        shift: int = 0,
    ) -> bytes:
        # revealer = StegDecoder(encoded_image)
        width = self.encoded_image.width

        if not generator:
            generator = identity()

        while shift != 0:
            next(generator)
            shift -= 1

        while True:
            generated_number = next(generator)

            col = generated_number % width
            row = int(generated_number / width)

            if self.decode_pixel((col, row)):
                return self.secret_message