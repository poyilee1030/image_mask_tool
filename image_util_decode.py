import os
import cv2
import numpy as np


def revert4base2decimal(p1, p2, p3, p4=0, p5=0, p6=0, n=3):
    if n == 3:
        n1 = 16 * p1
        n2 = 4 * p2
        n3 = 1 * p3
        return n1 + n2 + n3
    elif n == 4:
        n1 = 64 * p1
        n2 = 16 * p2
        n3 = 4 * p3
        n4 = 1 * p4
        return n1 + n2 + n3 + n4
    elif n == 6:
        n1 = 1024 * p1
        n2 = 256 * p2
        n3 = 64 * p3
        n4 = 16 * p4
        n5 = 4 * p5
        n6 = 1 * p6
        return n1 + n2 + n3 + n4 + n5 + n6


class ImageUtilDecode:

    def __init__(self, image_path):
        par_dir = os.path.dirname(image_path)
        basename_ext = os.path.basename(image_path)
        basename, ext = os.path.splitext(basename_ext)

        self.np_img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        h, w, c = self.np_img.shape
        self.height = h
        self.width = w
        self.img_size = w * h
        self.cur_pos = 0
        self.r2d = self.np_img[:, :, 0]
        self.g2d = self.np_img[:, :, 1]
        self.b2d = self.np_img[:, :, 2]
        self.a2d = self.np_img[:, :, 3]
        self.r1d = self.r2d.flatten()
        self.g1d = self.g2d.flatten()
        self.b1d = self.b2d.flatten()
        self.a1d = self.a2d.flatten()

        self.count = -1
        self.sd_list = []
        self.sd_img_list = []

    def decode(self, dst_path):
        self.decode_count()

        for i in range(self.count):
            x1, y1, x2, y2 = self.decode_size()
            w = x2 - x1
            h = y2 - y1
            self.sd_list.append(["0", x1, y1, x2, y2])
            self.decode_content(w, h)

        for i in range(self.count):
            sd = self.sd_list[i]
            x1 = sd[1]
            y1 = sd[2]
            x2 = sd[3]
            y2 = sd[4]
            roi_img = self.sd_img_list[i]
            self.np_img[y1:y2, x1:x2] = roi_img

        cv2.imencode(".png", self.np_img)[1].tofile(dst_path)

    def decode_content(self, w, h):
        size = w * h
        roi_r1d = np.zeros([size], dtype=np.uint8)
        roi_g1d = np.zeros([size], dtype=np.uint8)
        roi_b1d = np.zeros([size], dtype=np.uint8)
        roi_a1d = np.zeros([size], dtype=np.uint8)
        roi_a1d.fill(255)
        for i in range(size):
            r1 = self.r1d[self.cur_pos] & 3
            g1 = self.g1d[self.cur_pos] & 3
            b1 = self.b1d[self.cur_pos] & 3
            a1 = self.a1d[self.cur_pos] & 3
            red = revert4base2decimal(r1, g1, b1, a1, 0, 0, 4)
            roi_r1d[i] = red
            self.cur_pos += 1
            r2 = self.r1d[self.cur_pos] & 3
            g2 = self.g1d[self.cur_pos] & 3
            b2 = self.b1d[self.cur_pos] & 3
            a2 = self.a1d[self.cur_pos] & 3
            green = revert4base2decimal(r2, g2, b2, a2, 0, 0, 4)
            roi_g1d[i] = green
            self.cur_pos += 1
            r3 = self.r1d[self.cur_pos] & 3
            g3 = self.g1d[self.cur_pos] & 3
            b3 = self.b1d[self.cur_pos] & 3
            a3 = self.a1d[self.cur_pos] & 3
            blue = revert4base2decimal(r3, g3, b3, a3, 0, 0, 4)
            roi_b1d[i] = blue
            self.cur_pos += 1

        r2d = roi_r1d.reshape([h, w])
        g2d = roi_g1d.reshape([h, w])
        b2d = roi_b1d.reshape([h, w])
        a2d = roi_a1d.reshape([h, w])
        new_r2d = r2d[..., np.newaxis]
        new_g2d = g2d[..., np.newaxis]
        new_b2d = b2d[..., np.newaxis]
        new_a2d = a2d[..., np.newaxis]
        roi_img = np.concatenate((new_r2d, new_g2d, new_b2d, new_a2d), axis=2)
        self.sd_img_list.append(roi_img)

    def decode_count(self):
        r = self.r1d[self.cur_pos] & 3
        g = self.g1d[self.cur_pos] & 3
        b = self.b1d[self.cur_pos] & 3
        self.cur_pos += 1
        self.count = revert4base2decimal(r, g, b, 0, 0, 0, 3)

    def decode_size(self):
        if self.cur_pos >= self.img_size:
            return

        r1 = self.r1d[self.cur_pos] & 3
        g1 = self.g1d[self.cur_pos] & 3
        b1 = self.b1d[self.cur_pos] & 3
        self.cur_pos += 1
        r2 = self.r1d[self.cur_pos] & 3
        g2 = self.g1d[self.cur_pos] & 3
        b2 = self.b1d[self.cur_pos] & 3
        self.cur_pos += 1
        x1 = revert4base2decimal(r1, g1, b1, r2, g2, b2, 6)

        r1 = self.r1d[self.cur_pos] & 3
        g1 = self.g1d[self.cur_pos] & 3
        b1 = self.b1d[self.cur_pos] & 3
        self.cur_pos += 1
        r2 = self.r1d[self.cur_pos] & 3
        g2 = self.g1d[self.cur_pos] & 3
        b2 = self.b1d[self.cur_pos] & 3
        self.cur_pos += 1
        y1 = revert4base2decimal(r1, g1, b1, r2, g2, b2, 6)

        r1 = self.r1d[self.cur_pos] & 3
        g1 = self.g1d[self.cur_pos] & 3
        b1 = self.b1d[self.cur_pos] & 3
        self.cur_pos += 1
        r2 = self.r1d[self.cur_pos] & 3
        g2 = self.g1d[self.cur_pos] & 3
        b2 = self.b1d[self.cur_pos] & 3
        self.cur_pos += 1
        x2 = revert4base2decimal(r1, g1, b1, r2, g2, b2, 6)

        r1 = self.r1d[self.cur_pos] & 3
        g1 = self.g1d[self.cur_pos] & 3
        b1 = self.b1d[self.cur_pos] & 3
        self.cur_pos += 1
        r2 = self.r1d[self.cur_pos] & 3
        g2 = self.g1d[self.cur_pos] & 3
        b2 = self.b1d[self.cur_pos] & 3
        self.cur_pos += 1
        y2 = revert4base2decimal(r1, g1, b1, r2, g2, b2, 6)
        return x1, y1, x2, y2
