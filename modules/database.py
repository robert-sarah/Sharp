"""Database utilities for Sharp"""
import sqlite3
import json

class Database:
    def __init__(self, filepath):
        self.filepath = filepath
        self.conn = None
    
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.filepath)
            return True
        except:
            return False
    
    def execute(self, query, params=None):
        try:
            if params:
                self.conn.execute(query, params)
            else:
                self.conn.execute(query)
            self.conn.commit()
            return True
        except:
            return False
    
    def query(self, query, params=None):
        try:
            if params:
                cursor = self.conn.execute(query, params)
            else:
                cursor = self.conn.execute(query)
            return cursor.fetchall()
        except:
            return []
    
    def close(self):
        if self.conn:
            self.conn.close()

def create_database(filepath):
    db = Database(filepath)
    db.connect()
    return db
