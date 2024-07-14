import cv2
import numpy as np


class ImageUtilEncode:

    def __init__(self, image_path, sd_list):
        self.np_img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        h, w, c = self.np_img.shape
        self.height = h
        self.width = w
        self.img_size = w * h
        self.cur_pos = 0
        self.r2d = None
        self.g2d = None
        self.b2d = None
        self.a2d = None
        self.r1d = None
        self.g1d = None
        self.b1d = None
        self.a1d = None
        self.sd_list = sd_list
        self.sd_img_list = []

    def encode(self, dst_path):
        self.copy_and_erase_img_in_sd_list()
        self.prepare_encode()
        self.encode_sd_list()
        self.save_result(dst_path)

    def copy_and_erase_img_in_sd_list(self):
        for sd in self.sd_list:
            sx = int(sd[1] * self.width)
            sy = int(sd[2] * self.height)
            ex = int(sd[3] * self.width)
            ey = int(sd[4] * self.height)
            sd_img = self.np_img[sy:ey, sx:ex].copy()
            self.sd_img_list.append(sd_img)
            self.np_img[sy:ey, sx:ex, :] = 255

    # def erase_img_in_sd_list(self):
    #     for sd in self.sd_list:
    #         sx = int(sd[1] * self.width)
    #         sy = int(sd[2] * self.height)
    #         ex = int(sd[3] * self.width)
    #         ey = int(sd[4] * self.height)
    #         self.np_img[sy:ey, sx:ex, :] = 255

    def prepare_encode(self):
        self.cur_pos = 0
        self.r2d = self.np_img[:, :, 0]
        self.g2d = self.np_img[:, :, 1]
        self.b2d = self.np_img[:, :, 2]
        self.a2d = np.zeros([self.height, self.width], dtype=np.uint8)
        self.a2d.fill(255)
        self.r1d = self.r2d.flatten()
        self.g1d = self.g2d.flatten()
        self.b1d = self.b2d.flatten()
        self.a1d = self.a2d.flatten()

    def encode_sd_list(self):
        count = len(self.sd_list)
        cnt = np.base_repr(count, 4).zfill(3)
        r = int(cnt[0])
        g = int(cnt[1])
        b = int(cnt[2])
        self.put_size_data_into(r, g, b)
        for idx, sd in enumerate(self.sd_list):
            self.encode_one_sd(idx, sd)

    def save_result(self, dst_path):
        self.r2d = self.r1d.reshape([self.height, self.width])
        self.g2d = self.g1d.reshape([self.height, self.width])
        self.b2d = self.b1d.reshape([self.height, self.width])
        self.a2d = self.a1d.reshape([self.height, self.width])
        new_r2d = self.r2d[..., np.newaxis]
        new_g2d = self.g2d[..., np.newaxis]
        new_b2d = self.b2d[..., np.newaxis]
        new_a2d = self.a2d[..., np.newaxis]
        result_img = np.concatenate((new_r2d, new_g2d, new_b2d, new_a2d), axis=2)
        cv2.imencode(".png", result_img)[1].tofile(dst_path)

    def encode_one_sd(self, idx, sd):
        sx = int(sd[1] * self.width)
        sy = int(sd[2] * self.height)
        ex = int(sd[3] * self.width)
        ey = int(sd[4] * self.height)

        print(sx, sy, ex, ey)

        # sx
        nsx = np.base_repr(sx, 4).zfill(6)
        nsx1 = nsx[:3]
        r = int(nsx1[0])
        g = int(nsx1[1])
        b = int(nsx1[2])
        self.put_size_data_into(r, g, b)
        nsx2 = nsx[3:]
        r = int(nsx2[0])
        g = int(nsx2[1])
        b = int(nsx2[2])
        self.put_size_data_into(r, g, b)

        # sy
        nsy = np.base_repr(sy, 4).zfill(6)
        nsy1 = nsy[:3]
        r = int(nsy1[0])
        g = int(nsy1[1])
        b = int(nsy1[2])
        self.put_size_data_into(r, g, b)
        nsy2 = nsy[3:]
        r = int(nsy2[0])
        g = int(nsy2[1])
        b = int(nsy2[2])
        self.put_size_data_into(r, g, b)

        # ex
        nex = np.base_repr(ex, 4).zfill(6)
        nex1 = nex[:3]
        r = int(nex1[0])
        g = int(nex1[1])
        b = int(nex1[2])
        self.put_size_data_into(r, g, b)
        nex2 = nex[3:]
        r = int(nex2[0])
        g = int(nex2[1])
        b = int(nex2[2])
        self.put_size_data_into(r, g, b)

        # ey
        ney = np.base_repr(ey, 4).zfill(6)
        ney1 = ney[:3]
        r = int(ney1[0])
        g = int(ney1[1])
        b = int(ney1[2])
        self.put_size_data_into(r, g, b)
        ney2 = ney[3:]
        r = int(ney2[0])
        g = int(ney2[1])
        b = int(ney2[2])
        self.put_size_data_into(r, g, b)

        roi_img = self.sd_img_list[idx]
        roi_r2d_img = roi_img[:, :, 0]
        roi_g2d_img = roi_img[:, :, 1]
        roi_b2d_img = roi_img[:, :, 2]
        roi_r1d_img = roi_r2d_img.flatten()
        roi_g1d_img = roi_g2d_img.flatten()
        roi_b1d_img = roi_b2d_img.flatten()
        size = (ex-sx) * (ey-sy)
        for i in range(size):
            r = roi_r1d_img[i]
            nr = np.base_repr(r, 4).zfill(4)
            p1 = int(nr[0])
            p2 = int(nr[1])
            p3 = int(nr[2])
            p4 = int(nr[3])
            self.put_value_data_into(p1, p2, p3, p4)

            g = roi_g1d_img[i]
            ng = np.base_repr(g, 4).zfill(4)
            p1 = int(ng[0])
            p2 = int(ng[1])
            p3 = int(ng[2])
            p4 = int(ng[3])
            self.put_value_data_into(p1, p2, p3, p4)

            b = roi_b1d_img[i]
            nb = np.base_repr(b, 4).zfill(4)
            p1 = int(nb[0])
            p2 = int(nb[1])
            p3 = int(nb[2])
            p4 = int(nb[3])
            self.put_value_data_into(p1, p2, p3, p4)

    def put_size_data_into(self, r, g, b):
        if self.cur_pos >= self.img_size:
            return

        tmp_r = self.r1d[self.cur_pos]
        self.r1d[self.cur_pos] = (tmp_r & 252) | r

        tmp_g = self.g1d[self.cur_pos]
        self.g1d[self.cur_pos] = (tmp_g & 252) | g

        tmp_b = self.b1d[self.cur_pos]
        self.b1d[self.cur_pos] = (tmp_b & 252) | b

        self.cur_pos += 1

    def put_value_data_into(self, r, g, b, a):
        if self.cur_pos >= self.img_size:
            return
        
        tmp_r = self.r1d[self.cur_pos]
        self.r1d[self.cur_pos] = (tmp_r & 252) | r

        tmp_g = self.g1d[self.cur_pos]
        self.g1d[self.cur_pos] = (tmp_g & 252) | g

        tmp_b = self.b1d[self.cur_pos]
        self.b1d[self.cur_pos] = (tmp_b & 252) | b

        tmp_a = self.a1d[self.cur_pos]
        self.a1d[self.cur_pos] = (tmp_a & 252) | a
        
        self.cur_pos += 1
