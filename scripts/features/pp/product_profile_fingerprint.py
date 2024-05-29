import errno
import hashlib
import math
import os
import sqlite3
from datetime import datetime

import pandas as pd

from scripts.logger import ScriptLogger

logger = ScriptLogger().logger


class ProductProfileFingerprint:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.create_connection()

    def create_connection(self):
        """创建一个SQLite数据库连接"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            # logger.info(f"连接到 SQLite 版本：{sqlite3.version}")
        except sqlite3.Error as e:
            logger.info(e)

    def create_table(self):
        """创建一个新表"""
        try:
            c = self.conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS product_profile_fingerprint (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            product_no TEXT NOT NULL,
                            fingerprint TEXT NOT NULL,
                            modify_time TEXT,
                            re_upload INTEGER DEFAULT 0,
                            process_card_url TEXT
                        );""")
            # 添加唯一性约束到 name 列
            c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_product_no ON product_profile_fingerprint (product_no);")
        except sqlite3.Error as e:
            logger.info(e)

    def insert_or_update_data(self, data, modify_time, re_upload, process_card_url):
        """按名称插入或更新数据"""
        sql = ''' INSERT OR REPLACE INTO product_profile_fingerprint(product_no, fingerprint, modify_time, re_upload, process_card_url)
                  VALUES(?,?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, (*data, modify_time, re_upload, process_card_url))
        self.conn.commit()
        return cur.lastrowid

    def get_by_product_no(self, product_no: str):
        """按product_no查询指纹数据"""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM product_profile_fingerprint WHERE product_no=?", (product_no,))
        rows = cur.fetchall()
        return rows

    def get_by_re_upload(self, re_upload: int):
        """按re_upload查询指纹数据,1: 已推送RPA下载，待上传绑定；2：已上传绑定"""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM product_profile_fingerprint WHERE re_upload=?", (re_upload,))
        rows = cur.fetchall()
        return rows

    def update_process_card_url(self, product_no, new_process_card_url):
        """根据产品编号更新工艺卡 URL"""
        sql = ''' UPDATE product_profile_fingerprint
                  SET process_card_url = ?, re_upload = 2
                  WHERE product_no = ? '''
        cur = self.conn.cursor()
        cur.execute(sql, (new_process_card_url, product_no))
        self.conn.commit()

    def get_or_insert_data(self, product_no: str):
        """按product_no查询指纹数据，不存在新增"""
        cur = self.conn.cursor()
        # 查询是否存在具有指定名称的记录
        cur.execute(f'SELECT id FROM product_profile_fingerprint WHERE product_no = ?', (product_no,))
        row = cur.fetchone()

        if row:
            # 如果记录存在，返回其No
            return row[0]
        else:
            # 如果记录不存在，插入新记录
            fingerprint = ''
            re_upload = 1
            process_card_url = ''
            modify_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = ''' INSERT INTO product_profile_fingerprint(product_no, fingerprint, modify_time, re_upload, process_card_url)
                              VALUES(?,?,?,?,?) '''
            cur.execute(sql, (product_no, fingerprint, modify_time, re_upload, process_card_url))
            self.conn.commit()
            return cur.lastrowid

    def close_connection(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


def create_database():
    # 获取当前脚本所在的文件夹路径
    script_folder = os.path.dirname(os.path.abspath(__file__))
    database = "product_profile_fingerprint.db"
    db_path = os.path.join(script_folder, 'sqlite', database)
    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(os.path.dirname(db_path)):
        try:
            os.makedirs(os.path.dirname(db_path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # 创建 Database 实例
    product_profile_fingerprint_db = ProductProfileFingerprint(db_path)

    # 创建 表
    product_profile_fingerprint_db.create_table()
    return product_profile_fingerprint_db


def save_fingerprint(fingerprints):
    """保存指纹"""
    # 统一更新时间
    modify_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 插入或更新数据
    process_card_url = ''
    db = create_database()

    try:
        for fingerprint in fingerprints:
            # 新增或修改
            re_upload = 1
            if fingerprint[0] and fingerprint[0].startswith("P"):
                re_upload = 2
            db.insert_or_update_data(fingerprint, modify_time, re_upload, process_card_url)
    except sqlite3.Error as e:
        logger.error("Error save_fingerprint record:", e)
    finally:
        db.close_connection()


def calculate_row_fingerprint(row):
    # 将行数据转换为字符串
    row_str = ','.join(map(str, row))

    # 计算哈希值作为指纹
    fingerprint = hashlib.sha256(row_str.encode()).hexdigest()
    return fingerprint


def compute_fingerprint(pp_export_file: str):
    """计算指纹"""
    # 读取Excel文件
    df = pd.read_excel(pp_export_file)
    df.fillna('')

    # 计算每一行的指纹
    df['Fingerprint'] = df.apply(calculate_row_fingerprint, axis=1)
    fingerprints = []
    for index, row in df.iterrows():
        product_no = row.iloc[5]
        if isinstance(product_no, float) and math.isnan(product_no):
            continue
        if product_no == '产品号' or product_no == '产品级编号':
            continue
        fingerprint = row['Fingerprint']
        logger.info(f"Fingerprint: {fingerprint}, ProductNo: {product_no}")
        fingerprints.append((product_no, fingerprint))
    return fingerprints


def filter_fingerprint(fingerprints):
    """查询指纹"""
    # 待重新同步及上传工艺卡
    pending_synchronization_products = []
    db = create_database()

    try:
        for fingerprint in fingerprints:
            # 产品编号
            product_no = fingerprint[0]
            # 数据指纹
            product_profile_fingerprint = fingerprint[1]
            # 查询数据
            fingerprint_data = db.get_by_product_no(product_no)
            if fingerprint_data:
                if fingerprint_data[0][2] != product_profile_fingerprint:
                    pending_synchronization_products.append(product_no)
                    # product_profile_fingerprint_db.insert_or_update_data(fingerprint, modify_time, 1, '')
            else:
                pending_synchronization_products.append(product_no)
                # product_profile_fingerprint_db.insert_or_update_data(fingerprint, modify_time, 0, '')
        return pending_synchronization_products
    except sqlite3.Error as e:
        logger.error("Error filter_fingerprint record:", e)
    finally:
        db.close_connection()


def load_fingerprints_by_upload_status(re_upload: int):
    """查询待上传工艺卡的产品档案"""
    product_nos = []
    db = create_database()

    try:
        for fingerprint in db.get_by_re_upload(re_upload):
            # 产品编号
            product_no = fingerprint[1]
            product_nos.append(product_no)
        return product_nos
    except sqlite3.Error as e:
        logger.error("Error load_fingerprints_by_upload_status record:", e)
    finally:
        db.close_connection()


def update_process_card_url_by_product_no(product_no: str, process_card_url: str):
    """更新工艺卡文件URL"""
    if not product_no:
        return

    db = create_database()
    try:
        db.update_process_card_url(product_no, process_card_url)
    except sqlite3.Error as e:
        logger.error("Error update_process_card_url_by_product_no record:", e)
    finally:
        db.close_connection()


def update_non_existent_product_no(product_no: str):
    """添加不存在的产品工艺卡"""
    if not product_no:
        return

    db = create_database()
    try:
        db.get_or_insert_data(product_no)
    except sqlite3.Error as e:
        logger.error("Error update_non_existent_product_no record:", e)
    finally:
        db.close_connection()
