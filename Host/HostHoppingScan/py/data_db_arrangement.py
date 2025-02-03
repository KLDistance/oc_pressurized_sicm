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
CREATE TABLE data (
    pixel_name TEXT PRIMARY KEY,
    frame_idx INTEGER,
    x_idx INTEGER,
    y_idx INTEGER,
    x_pos REAL,
    y_pos REAL,
    z_height REAL,
    baseline_curr REAL,
    z_trace ARRAY,
    curr_trace ARRAY
)''')
            cursor.execute('''
CREATE TABLE frame (
    frame_idx INTEGER PRIMARY KEY,
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
    x_num INTEGER,
    y_num INTEGER,
    x_offset REAL,
    y_offset REAL,
    x_stepsize REAL,
    y_stepsize REAL,
    recording_threshold REAL,
    halting_threshold REAL,
    retract REAL,
    ff_apprate REAL,
    nf_apprate REAL,
    frame_num INTEGER,
    pressure REAL,
    extra_note TEXT
)''')
            connection.commit()
            cursor.close()
    
    def start_frame_timer(self):
        ct = datetime.datetime.now()
        self.start_frame_timestamp = ct.timestamp()
    
    def end_frame_timer(self, frame_idx, is_finished_naturally):
        ct = datetime.datetime.now()
        self.end_frame_timestamp = ct.timestamp()
        sqlite3.register_adapter(np.ndarray, adapt_array)
        with closing(sqlite3.connect(self.db_fp, detect_types=sqlite3.PARSE_DECLTYPES)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
INSERT INTO frame (
    frame_idx,
    start_frame_timestamp,
    end_frame_timestamp,
    is_finished_naturally
) VALUES(
    ?, ?, ?, ?
)
''', (frame_idx, self.start_frame_timestamp, self.end_frame_timestamp, int(is_finished_naturally)))
            connection.commit()
            cursor.close()

    def start_global_timer(self):
        ct = datetime.datetime.now()
        self.start_global_timestamp = ct.timestamp()

    def end_global_timer(self):
        ct = datetime.datetime.now()
        self.end_global_timestamp = ct.timestamp()
    
    def insert_data(self, frame_idx, xpos, ypos, xidx, yidx, zheight, baseline_curr,\
        ztrace, curr_trace):
        sqlite3.register_adapter(np.ndarray, adapt_array)
        with closing(sqlite3.connect(self.db_fp, detect_types=sqlite3.PARSE_DECLTYPES)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
INSERT INTO data (
    pixel_name,
    frame_idx,
    x_idx,
    y_idx,
    x_pos,
    y_pos,
    z_height,
    baseline_curr,
    z_trace,
    curr_trace
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)''', (f'px_{frame_idx}_{xidx}_{yidx}', frame_idx, xidx, yidx, xpos, ypos, zheight, baseline_curr, ztrace, curr_trace))
            connection.commit()
            cursor.close()
    
    def insert_info(self, param_iter, xnum, ynum, xstep, ystep, xoffset, yoffset,\
        recording_threshold, halting_threshold, retract, ff_apprate, nf_apprate, framenum, pressure, extra_note):
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
    retract,
    ff_apprate,
    nf_apprate,
    frame_num,
    pressure,
    extra_note
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)''', (f'param_iter_{param_iter}', 'um', 's', 'kPa', 'nA', self.start_global_timestamp, self.end_global_timestamp, \
            xnum, ynum, xoffset, yoffset, xstep, ystep, recording_threshold, halting_threshold, retract, ff_apprate, nf_apprate, framenum, pressure, extra_note))
            connection.commit()
            cursor.close()

def db_init(fp):
    db_manager = DB_Manager(fp)
    return db_manager

def db_start_global_timer(db_manager):
    db_manager.start_global_timer()

def db_end_global_timer(db_manager):
    db_manager.end_global_timer()

def db_start_frame_timer(db_manager):
    db_manager.start_frame_timer()

def db_end_frame_timer(db_manager, frame_idx, is_finished_naturally):
    db_manager.end_frame_timer(frame_idx, is_finished_naturally)

def db_insert_data(db_manager, frame_idx, xpos, ypos, xidx, yidx, zheight, baseline_curr,\
    ztrace, curr_trace):
    db_manager.insert_data(frame_idx, xpos, ypos, xidx, yidx, zheight, baseline_curr, np.array(ztrace), np.array(curr_trace))

def db_insert_info(db_manager, param_iter, xnum, ynum, xstep, ystep, xoffset, yoffset,\
    recording_threshold, halting_threshold, retract, ff_apprate, nf_apprate, framenum, pressure, extra_note):
    db_manager.insert_info(param_iter, xnum, ynum, xstep, ystep, xoffset, yoffset, recording_threshold, halting_threshold, retract, ff_apprate, nf_apprate, framenum, pressure, extra_note)