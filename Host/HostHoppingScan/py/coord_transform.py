import os, sys, shutil, pickle
import numpy as np
import scipy
from scipy import signal
from scipy.ndimage import gaussian_filter
import skimage, cv2

class CoordTransform:
    def __init__(self, coord_data_fp):
        self.coord_data_fp = coord_data_fp
    def _tip_point(self, img_diff_mat):
        #img_avg = np.mean(img_diff_mat)
        #img_std = np.std(img_diff_mat)
        img_max = np.amax(img_diff_mat)
        img_min = np.amin(img_diff_mat)
        img_diff = img_max - img_min
        y_tip_pts, x_tip_pts = np.where(img_diff_mat >= img_min + img_diff*0.95)
        x_tip_mean = np.mean(x_tip_pts)
        y_tip_mean = np.mean(y_tip_pts)
        return (x_tip_mean, y_tip_mean)
    def _search_t3pts(self):
        img_list_len = len(self.imgs_ret_list)
        x_img_vec = np.zeros((img_list_len))
        y_img_vec = np.zeros((img_list_len))
        x_tip_vec = np.zeros((img_list_len))
        y_tip_vec = np.zeros((img_list_len))
        for iter in range(img_list_len):
            img_retract_mat = np.array(self.imgs_ret_list[iter]).astype(float)
            img_extend_mat = np.array(self.imgs_ext_list[iter]).astype(float)
            img_diff_mat = img_retract_mat - img_extend_mat
            (x_tip_mean, y_tip_mean) = self._tip_point(img_diff_mat)
            x_img_vec[iter] = x_tip_mean
            y_img_vec[iter] = y_tip_mean
            x_tip_vec[iter] = self.x_tip_pos_list[iter]
            y_tip_vec[iter] = self.y_tip_pos_list[iter]
        return (x_img_vec, y_img_vec, x_tip_vec, y_tip_vec)
    def _edge_padding(self, img_mat):
        (rows, cols) = img_mat.shape
        pad_buf = np.zeros((rows*3, cols*3))
        # copies of original image into padding buffer with a specific pattern
        pad_buf[rows:rows*2, 0:cols] = img_mat[:, ::-1]
        pad_buf[rows:rows*2, cols*2:cols*3] = img_mat[:, ::-1]
        pad_buf[rows*2:rows*3, cols:cols*2] = img_mat[::-1, :]
        pad_buf[0:rows, cols:cols*2] = img_mat[::-1, :]
        pad_buf[rows*2:rows*3, 0:cols] = img_mat[::-1, ::-1]
        pad_buf[rows*2:rows*3, cols*2:cols*3] = img_mat[::-1, ::-1]
        pad_buf[0:rows, cols*2:cols*3] = img_mat[::-1, ::-1]
        pad_buf[0:rows, 0:cols] = img_mat[::-1, ::-1]
        return pad_buf
    def coord_img_segmentation(self, input_coord):
        # parsing
        #img_mat = tip_point_img[self.crop_y_idx_min:self.crop_y_idx_max+1, self.crop_x_idx_min:self.crop_x_idx_max+1]
        img_mat = np.array(input_coord).astype(float)
        (rows, cols) = img_mat.shape
        # padding
        padded_img_mat = self._edge_padding(img_mat)
        # filters
        gauss_img_mat = gaussian_filter(padded_img_mat, sigma=1.2)
        med_img_mat = signal.medfilt2d(gauss_img_mat, kernel_size=[5, 5])
        filtered_mat = med_img_mat[rows:rows*2, cols:cols*2]
        # normalize and thresholding
        markers = np.zeros_like(img_mat).astype(int)
        px_max = np.amax(filtered_mat)
        px_min = np.amin(filtered_mat)
        top_lim = (px_max-px_min)*0.67 + px_min
        bottom_lim = (px_max-px_min) * 0.33 + px_min
        markers[filtered_mat < bottom_lim] = 1
        markers[filtered_mat > top_lim] = 2
        # edge detection and segmentation
        elevation_map = skimage.filters.sobel(filtered_mat)
        segmentation = skimage.segmentation.watershed(elevation_map, markers)
        segmentation_refined = scipy.ndimage.binary_fill_holes(segmentation - 1)
        labels, _ = scipy.ndimage.label(segmentation_refined)
        labels = np.reshape(labels, (rows, cols)).astype(float)
        # dilate label map
        labels_dilated = cv2.dilate(labels, np.ones((7, 7)), iterations=1)
        # re-formalize label
        labels_dilated[labels_dilated > 0] = 1.0
        return labels_dilated
    def coord_fit(self, imgs_ret_list, imgs_ext_list, x_tip_pos_list, y_tip_pos_list):
        # reserve img and tip position list for future use
        self.imgs_ret_list = imgs_ret_list
        self.imgs_ext_list = imgs_ext_list
        self.x_tip_pos_list = x_tip_pos_list
        self.y_tip_pos_list = y_tip_pos_list
        # compuite directional vector
        (x_img_vec, y_img_vec, x_tip_vec, y_tip_vec) = self._search_t3pts()
        # keep img tip point state
        self.x_img_tip_point_vec = np.around(x_img_vec).astype(int)
        self.y_img_tip_point_vec = np.around(y_img_vec).astype(int)
        # construct img vectors
        xvec_img = np.array([x_img_vec[0], x_img_vec[1], x_img_vec[2]])
        yvec_img = np.array([y_img_vec[0], y_img_vec[1], y_img_vec[2]])
        zvec_img = np.array([1.0, 1.0, 1.0])
        #xvec_img = np.array([y_img_vec[1] - y_img_vec[0], x_img_vec[1] - x_img_vec[0]])
        #yvec_img = np.array([y_img_vec[2] - y_img_vec[1], x_img_vec[2] - x_img_vec[1]])
        img_vec = np.stack((xvec_img, yvec_img, zvec_img))
        # construct tip vectors
        xvec_tip = np.array([x_tip_vec[0], x_tip_vec[1], x_tip_vec[2]])
        yvec_tip = np.array([y_tip_vec[0], y_tip_vec[1], y_tip_vec[2]])
        zvec_tip = np.array([1.0, 1.0, 1.0])
        #xvec_tip = np.array([y_tip_vec[1] - y_tip_vec[0], x_tip_vec[1] - x_tip_vec[0]])
        #yvec_tip = np.array([y_tip_vec[2] - y_tip_vec[1], x_tip_vec[2] - x_tip_vec[1]])
        tip_vec = np.stack((xvec_tip, yvec_tip, zvec_tip))
        # affine transformation
        self.titransf_mat = np.matmul(tip_vec, np.linalg.inv(img_vec))
        # reserve img coordinate origin
        self.x_img_coord_origin = x_img_vec[0]
        self.y_img_coord_origin = y_img_vec[0]
        return self.titransf_mat
    def crop_tip_point_img(self):
        tip_point_img = np.array(self.imgs_ret_list[0])
        self.crop_x_idx_min = np.amin(self.x_img_tip_point_vec)
        self.crop_x_idx_max = np.amax(self.x_img_tip_point_vec)
        self.crop_y_idx_min = np.amin(self.y_img_tip_point_vec)
        self.crop_y_idx_max = np.amax(self.y_img_tip_point_vec)
        cropped_img = tip_point_img[self.crop_y_idx_min:self.crop_y_idx_max+1, self.crop_x_idx_min:self.crop_x_idx_max+1].tolist()
        return cropped_img
    def coord_eval(self, input_coord):
        input_coord_mat = np.array(input_coord).T
        # location restore and transform
        input_coord_mat[0, :] += self.crop_y_idx_min
        input_coord_mat[1, :] += self.crop_x_idx_min
        try:
            x_vec = np.asarray(input_coord_mat[1, :])
            y_vec = np.asarray(input_coord_mat[0, :])
            z_vec = np.ones((len(x_vec))).astype(float)
            refined_coord_mat = np.stack((x_vec, y_vec, z_vec))
            transformed_coord_mat = np.matmul(self.titransf_mat, refined_coord_mat)
        except Exception as e:
            error_msg = f"\nmatrix: \n{self.titransf_mat}\nx_vec:\n{x_vec}\ny_vec:\n{y_vec}\nz_vec:\n{z_vec}\nrefined:\n{refined_coord_mat}\n"
            raise Exception(error_msg)
        return transformed_coord_mat
    def save_transform_state(self):
        if os.path.exists(self.coord_data_fp):
            os.remove(self.coord_data_fp)
        # save as pickle
        with open(self.coord_data_fp + '.pickle', 'wb') as pickle_fh:
            data_dict = {}
            data_dict['imgs_ret_list'] = self.imgs_ret_list
            data_dict['imgs_ext_list'] = self.imgs_ext_list
            data_dict['x_img_tip_pos_vec'] = self.x_img_tip_point_vec
            data_dict['y_img_tip_pos_vec'] = self.y_img_tip_point_vec
            data_dict['x_tip_pos_list'] = self.x_tip_pos_list
            data_dict['y_tip_pos_list'] = self.y_tip_pos_list
            data_dict['transform_matrix'] = self.titransf_mat
            pickle.dump(data_dict, pickle_fh)
            pickle_fh.close()
    def load_transform_state(self):
        # check if tmp file exists
        if not os.path.isfile(self.coord_data_fp + '.pickle'):
            return False
        # load state from pickle
        with open(self.coord_data_fp + '.pickle', 'rb') as pickle_fh:
            data_dict = pickle.load(pickle_fh)
            pickle_fh.close()
        self.imgs_ret_list = data_dict['imgs_ret_list']
        self.imgs_ext_list = data_dict['imgs_ext_list']
        self.x_img_tip_point_vec = data_dict['x_img_tip_pos_vec']
        self.y_img_tip_point_vec = data_dict['y_img_tip_pos_vec']
        self.x_tip_pos_list = data_dict['x_tip_pos_list']
        self.y_tip_pos_list = data_dict['y_tip_pos_list']
        self.titransf_mat = data_dict['transform_matrix']
        return True
    def get_existing_transf_matrix(self):
        return self.titransf_mat.tolist()

def coord_init(coord_data_fp):
    coord_transform_obj = CoordTransform(coord_data_fp)
    return coord_transform_obj

def coord_load(coord_transform_obj):
    return coord_transform_obj.load_transform_state()

def coord_fit(coord_transform_obj, imgs_ret_list, imgs_ext_list, x_tip_pos_list, y_tip_pos_list, save_coord_stat):
    transform_matrix = coord_transform_obj.coord_fit(imgs_ret_list, imgs_ext_list, x_tip_pos_list, y_tip_pos_list)
    if save_coord_stat:
        coord_transform_obj.save_transform_state()
    return transform_matrix

def coord_get_crop_img(coord_transform_obj):
    return coord_transform_obj.crop_tip_point_img()

def coord_eval(coord_transform_obj, input_coord):
    return coord_transform_obj.coord_eval(input_coord).tolist()

def coord_img_segmentation(coord_transform_obj, input_img):
    return coord_transform_obj.coord_img_segmentation(input_img)

def coord_get_existing_transf_matrix(coord_transform_obj):
    return coord_transform_obj.get_existing_transf_matrix()