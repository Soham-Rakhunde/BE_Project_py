from smop.libsmop import *
from scipy.signal import wiener
import utils
from PIL import Image
import PIL
import math
import simplejpeg

def meshgrid(x: int):
    # col2d = np.array([[col for col in range(x)] for _ in range(x)])
    # row2d = np.array([[row for _ in range(x)] for row in range(x)])
    return np.meshgrid(np.arange(0,x), np.arange(0,x))

def extract_quantization_table(im: Image):
    return np.resize(im.quantization[0],(8,8))

image_path = 'C:\\Users\\soham\\OneDrive\\Desktop\\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\\data\\ALASKA_50774_QF75.jpg'
im = Image.open('C:\\Users\\soham\\OneDrive\\Desktop\\341a4625-cec0-45df-9753-7f9e16f8832c_v4.0\\data\\ALASKA_50774_QF75.jpg')
# print(np.resize(im.quantization[0],(8,8)))

with open(image_path, 'rb') as fp:
    # print(fp.read(2))
    sim = simplejpeg.decode_jpeg(fp.read())
    print(np.sum(sim))
    sdr = simplejpeg.decode_jpeg_header(fp.read())
    print(sdr)
    # print(sim)

print(np.sum(np.asarray(im)))
# print(np.asarray(im))
print(np.sum(np.asarray(im)) - 512*512*128)
# cc, rr = meshgrid(x=8)
# 144
# T = dot(sqrt(2 / 8), np.cos(multiply(dot(math.pi, (dot(2, cc) + 1)), rr) / (dot(2, 8))))
# T[0, :] = T[0, :] / sqrt(2)
# print(np.zeros((2,2)))

# arr=np.arange(16)
# arr_2d=arr.reshape(4,4)    #Reshapes 1d array in to 2d, containing 10 rows and 5 columns.
# print(arr_2d.T)

# dct64_mtx = np.zeros((64, 64))
# for i in range(64):
#     dcttmp = np.zeros((8,8))
#     # 150
#     dcttmp[i%8, int(i/8)] = 1
#     # 150
#     TTMP = dot(dot(T, dcttmp), T.T)
#     # 150
#     dct64_mtx[:, i] = np.ravel(TTMP)

# print(dct64_mtx)