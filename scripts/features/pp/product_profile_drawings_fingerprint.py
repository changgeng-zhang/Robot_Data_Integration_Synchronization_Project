import errno
import os
import sqlite3
from datetime import datetime

from scripts.logger import ScriptLogger

logger = ScriptLogger().logger


class ProductProfileDrawingsFingerprint:
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
            c.execute("""CREATE TABLE IF NOT EXISTS product_profile_drawings_fingerprint (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            product_no TEXT NOT NULL,
                            file_path TEXT NOT NULL,
                            fingerprint TEXT NOT NULL,
                            modify_time TEXT,
                            drawings_url TEXT
                        );""")
            # 添加唯一性约束到 name 列
            c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_product_no_fingerprint ON product_profile_drawings_fingerprint (product_no, fingerprint);")
        except sqlite3.Error as e:
            logger.info(e)

    def insert_or_update_data(self, fingerprint, modify_time, drawings_url):
        """按名称插入或更新数据"""
        sql = ''' INSERT OR REPLACE INTO product_profile_drawings_fingerprint(product_no, file_path, fingerprint, modify_time, drawings_url)
                  VALUES(?,?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, (*fingerprint, modify_time, drawings_url))
        self.conn.commit()
        return cur.lastrowid

    def get_by_product_no(self, product_no: str):
        """按product_no查询指纹数据"""
        cur = self.conn.cursor()
        cur.execute("SELECT product_no, file_path, fingerprint FROM product_profile_drawings_fingerprint WHERE product_no=?", (product_no,))
        rows = cur.fetchall()
        return rows

    def del_by_product_no(self, product_no: str):
        """按product_no删除指纹数据"""
        sql = ''' DELETE FROM product_profile_drawings_fingerprint
                          WHERE product_no = ? '''
        cur = self.conn.cursor()
        cur.execute(sql, (product_no,))
        self.conn.commit()

    def close_connection(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


def create_database():
    # 获取当前脚本所在的文件夹路径
    script_folder = os.path.dirname(os.path.abspath(__file__))
    database = "product_profile_drawings_fingerprint.db"
    db_path = os.path.join(script_folder, 'sqlite', database)
    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(os.path.dirname(db_path)):
        try:
            os.makedirs(os.path.dirname(db_path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # 创建 Database 实例
    product_profile_drawings_fingerprint_db = ProductProfileDrawingsFingerprint(db_path)

    # 创建 表
    product_profile_drawings_fingerprint_db.create_table()
    return product_profile_drawings_fingerprint_db


def save_product_fingerprint(fingerprints):
    db = create_database()
    try:
        # 统一更新时间
        modify_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 插入或更新数据
        for fingerprint in fingerprints:
            db.insert_or_update_data(fingerprint, modify_time, '')

    except sqlite3.Error as e:
        print("Error save record:", e)
    finally:
        db.close_connection()


def find_by_product_no(product_no: str):
    """查询指纹"""
    db = create_database()
    try:
        rows = db.get_by_product_no(product_no)
        return rows
    except sqlite3.Error as e:
        print("Error find record:", e)
    finally:
        db.close_connection()


def del_by_product_no(product_no: str):
    """删除指纹"""
    db = create_database()
    try:
        db.del_by_product_no(product_no)
    except sqlite3.Error as e:
        print("Error deleting record:", e)
    finally:
        db.close_connection()
