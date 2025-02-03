import os, sys, io, shutil, datetime, sqlite3
from contextlib import closing
import numpy as np

def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

class DB_Manager:
    def __init__(self, db_fp):
        self.db_fp = db_fp
        self.start_global_timestamp = 0.0
        self.end_global_timestamp = 0.0
        self.start_frame_timestamp = 0.0
        self.end_frame_timestamp = 0.0
        sqlite3.register_adapter(np.ndarray, adapt_array)
        with closing(sqlite3.connect(self.db_fp, detect_types=sqlite3.PARSE_DECLTYPES)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
CREATE TABLE coordinate_calibration (
    calibration_name TEXT PRIMARY KEY,
    x_coord_calibration_begin REAL,
    y_coord_calibration_begin REAL,
    x_coord_calibration_end REAL,
    y_coord_calibration_end REAL,
    coord_calibration_threshold REAL,
    coord_calibration_retract REAL,
    coord_calibration_apprate REAL,
    coord_calibration_retrate REAL,
    tip_point_cropped_image ARRAY,
    target_isolated_coordinates ARRAY,
    transform_matrix ARRAY,
    is_coordinate_calibration_on INTEGER,
    is_auto_image_segmentation_on INTEGER
)''')
            cursor.execute('''
CREATE TABLE data (
    pixel_name TEXT PRIMARY KEY,
    region_idx INTEGER,
    frame_idx INTEGER,
    x_idx INTEGER,
    y_idx INTEGER,
    x_pos REAL,
    y_pos REAL,
    z_height_probe REAL,
    z_height REAL,
    baseline_curr REAL,
    circular_buffer_pointer_idx INTEGER,
    z_trace ARRAY,
    curr_trace ARRAY
)''')
            cursor.execute('''
CREATE TABLE frame (
    frame_name TEXT PRIMARY KEY,
    region_idx INTEGER,
    frame_idx INTEGER,
    start_frame_timestamp REAL,
    end_frame_timestamp REAL,
    is_finished_naturally INTEGER
)''')
            cursor.execute('''
CREATE TABLE param (
    param_name TEXT PRIMARY KEY,
    universal_length_unit TEXT,
    universal_time_unit TEXT,
    universal_pressure_unit TEXT,
    universal_current_unit TEXT,
    start_global_timestamp REAL,
    end_global_timestamp REAL,
    x_num ARRAY,
    y_num ARRAY,
    x_offset ARRAY,
    y_offset ARRAY,
    x_stepsize ARRAY,
    y_stepsize ARRAY,
    recording_threshold REAL,
    halting_threshold REAL,
    retract_flat REAL,
    retract_edge REAL,
    ff_apprate REAL,
    nf_apprate REAL,
    region_num INTEGER,
    frame_num INTEGER,
    pressure REAL,
    extra_note TEXT
)''')
            connection.commit()
            cursor.close()
    
    def start_frame_timer(self):
        ct = datetime.datetime.now()
        self.start_frame_timestamp = ct.timestamp()
    
    def end_frame_timer(self, region_idx, frame_idx, is_finished_naturally):
        ct = datetime.datetime.now()
        self.end_frame_timestamp = ct.timestamp()
        sqlite3.register_adapter(np.ndarray, adapt_array)
        with closing(sqlite3.connect(self.db_fp, detect_types=sqlite3.PARSE_DECLTYPES)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
INSERT INTO frame (
    frame_name,
    region_idx,
    frame_idx,
    start_frame_timestamp,
    end_frame_timestamp,
    is_finished_naturally
) VALUES(
    ?, ?, ?, ?, ?, ?
)
''', (f'r_{region_idx}_f_{frame_idx}', region_idx, frame_idx, self.start_frame_timestamp, self.end_frame_timestamp, int(is_finished_naturally)))
            connection.commit()
            cursor.close()

    def start_global_timer(self):
        ct = datetime.datetime.now()
        self.start_global_timestamp = ct.timestamp()

    def end_global_timer(self):
        ct = datetime.datetime.now()
        self.end_global_timestamp = ct.timestamp()
    
    def insert_coordinate_calibration(self, x_coord_cal_begin, y_coord_cal_begin, x_coord_cal_end, y_coord_cal_end, \
        coord_cal_threshold, coord_cal_retract, coord_cal_apprate, coord_cal_retrate, \
        tip_point_cropped_image, target_isolated_coordinates, transform_matrix, \
        is_coordinate_calibration_on, is_auto_image_segmentation_on):
        sqlite3.register_adapter(np.ndarray, adapt_array)
        with closing(sqlite3.connect(self.db_fp, detect_types=sqlite3.PARSE_DECLTYPES)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
INSERT INTO coordinate_calibration (
    calibration_name,
    x_coord_calibration_begin,
    y_coord_calibration_begin,
    x_coord_calibration_end,
    y_coord_calibration_end,
    coord_calibration_threshold,
    coord_calibration_retract,
    coord_calibration_apprate,
    coord_calibration_retrate,
    tip_point_cropped_image,
    target_isolated_coordinates,
    transform_matrix,
    is_coordinate_calibration_on,
    is_auto_image_segmentation_on
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)''', ('coordinate calibration', x_coord_cal_begin, y_coord_cal_begin, x_coord_cal_end, y_coord_cal_end, \
            coord_cal_threshold, coord_cal_retract, coord_cal_apprate, coord_cal_retrate, \
            np.array(tip_point_cropped_image), np.array(target_isolated_coordinates), np.array(transform_matrix), \
            is_coordinate_calibration_on, is_auto_image_segmentation_on))
            connection.commit()
            cursor.close()

    def insert_data(self, region_idx, frame_idx, xpos, ypos, xidx, yidx, zheight_probe, zheight, baseline_curr, circular_buffer_pointer_idx,\
        ztrace, curr_trace):
        sqlite3.register_adapter(np.ndarray, adapt_array)
        with closing(sqlite3.connect(self.db_fp, detect_types=sqlite3.PARSE_DECLTYPES)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
INSERT INTO data (
    pixel_name,
    region_idx,
    frame_idx,
    x_idx,
    y_idx,
    x_pos,
    y_pos,
    z_height_probe,
    z_height,
    baseline_curr,
    circular_buffer_pointer_idx,
    z_trace,
    curr_trace
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)''', (f'px_{region_idx}_{frame_idx}_{xidx}_{yidx}', region_idx, frame_idx, xidx, yidx, xpos, ypos, zheight_probe, zheight, baseline_curr, circular_buffer_pointer_idx, ztrace, curr_trace))
            connection.commit()
            cursor.close()
    
    def insert_info(self, param_iter, xnum, ynum, xstep, ystep, xoffset, yoffset,\
        recording_threshold, halting_threshold, retract_flat, retract_edge, ff_apprate,\
        nf_apprate, region_num, framenum, pressure, extra_note):
        sqlite3.register_adapter(np.ndarray, adapt_array)
        with closing(sqlite3.connect(self.db_fp, detect_types=sqlite3.PARSE_DECLTYPES)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
INSERT INTO param (
    param_name,
    universal_length_unit,
    universal_time_unit,
    universal_pressure_unit,
    universal_current_unit,
    start_global_timestamp,
    end_global_timestamp,
    x_num,
    y_num,
    x_offset,
    y_offset,
    x_stepsize,
    y_stepsize,
    recording_threshold,
    halting_threshold,
    retract_flat,
    retract_edge,
    ff_apprate,
    nf_apprate,
    region_num,
    frame_num,
    pressure,
    extra_note
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)''', (f'param_iter_{param_iter}', 'um', 's', 'kPa', 'nA', self.start_global_timestamp, self.end_global_timestamp, \
            np.array(xnum), np.array(ynum), np.array(xoffset), np.array(yoffset), np.array(xstep), np.array(ystep), \
            recording_threshold, halting_threshold, retract_flat, retract_edge, ff_apprate, nf_apprate, region_num,\
            framenum, pressure, extra_note))
            connection.commit()
            cursor.close()

def db_init(fp):
    db_manager = DB_Manager(fp)
    return db_manager

def db_insert_coordinate_calibration(db_manager, x_coord_cal_begin, y_coord_cal_begin, x_coord_cal_end, y_coord_cal_end, \
        coord_cal_threshold, coord_cal_retract, coord_cal_apprate, coord_cal_retrate, \
        tip_point_cropped_image, target_isolated_coordinates, transform_matrix, \
        is_coordinate_calibration_on, is_auto_image_segmentation_on):
    db_manager.insert_coordinate_calibration(x_coord_cal_begin, y_coord_cal_begin, x_coord_cal_end, y_coord_cal_end, \
        coord_cal_threshold, coord_cal_retract, coord_cal_apprate, coord_cal_retrate, \
        tip_point_cropped_image, target_isolated_coordinates, transform_matrix, \
        is_coordinate_calibration_on, is_auto_image_segmentation_on)

def db_start_global_timer(db_manager):
    db_manager.start_global_timer()

def db_end_global_timer(db_manager):
    db_manager.end_global_timer()

def db_start_frame_timer(db_manager):
    db_manager.start_frame_timer()

def db_end_frame_timer(db_manager, region_idx, frame_idx, is_finished_naturally):
    db_manager.end_frame_timer(region_idx, frame_idx, is_finished_naturally)

def db_insert_data(db_manager, region_idx, frame_idx, xpos, ypos, xidx, yidx, zheight_probe, zheight, baseline_curr, circular_buffer_pointer_idx,\
    ztrace, curr_trace):
    db_manager.insert_data(region_idx, frame_idx, xpos, ypos, xidx, yidx, zheight_probe, zheight, baseline_curr, circular_buffer_pointer_idx, np.array(ztrace), np.array(curr_trace))

def db_insert_info(db_manager, param_iter, xnum, ynum, xstep, ystep, xoffset, yoffset,\
    recording_threshold, halting_threshold, retract_flat, retract_edge, ff_apprate, nf_apprate, regionnum, framenum, pressure, extra_note):
    db_manager.insert_info(param_iter, xnum, ynum, xstep, ystep, xoffset, yoffset, recording_threshold, halting_threshold, retract_flat,\
    retract_edge, ff_apprate, nf_apprate, regionnum, framenum, pressure, extra_note)
