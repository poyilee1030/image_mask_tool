import os
import glob
from image_util_decode import ImageUtilDecode


if __name__ == "__main__":
    src_path = os.getcwd() + "/output/demo.png"
    dst_path = os.getcwd() + "/reverse/demo.png"

    obj = ImageUtilDecode(src_path)
    obj.decode(dst_path)
