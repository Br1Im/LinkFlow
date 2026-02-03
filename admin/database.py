#!/usr/bin/env python3
"""
Database module for LinkFlow Admin Panel
SQLite database with all tables and operations
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = 'linkflow.db'


@contextmanager
def get_db():
    """Context manager for database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Initialize database with all tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                success BOOLEAN NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                qr_link TEXT,
                payment_time REAL,
                card TEXT,
                owner TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_timestamp ON payments(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_success ON payments(success)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC)')
        
        print("✅ Database initialized successfully")


# ============= PAYMENTS =============

def add_payment(payment_data):
    """Add new payment to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (id, order_id, amount, success, status, timestamp, qr_link, payment_time, card, owner)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment_data['id'],
            payment_data['order_id'],
            payment_data['amount'],
            payment_data['success'],
            payment_data['status'],
            payment_data['timestamp'],
            payment_data.get('qr_link'),
            payment_data.get('payment_time'),
            payment_data.get('card'),
            payment_data.get('owner')
        ))
        return payment_data['id']


def get_payments(status='all', search='', page=1, per_page=20):
    """Get payments with filtering and pagination"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Build query
        query = 'SELECT * FROM payments WHERE 1=1'
        params = []
        
        if status == 'success':
            query += ' AND success = 1'
        elif status == 'failed':
            query += ' AND success = 0'
        
        if search:
            query += ' AND (order_id LIKE ? OR id LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])
        
        # Count total
        count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Get paginated results
        query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        payments = []
        for row in rows:
            payments.append({
                'id': row['id'],
                'order_id': row['order_id'],
                'amount': row['amount'],
                'success': bool(row['success']),
                'status': row['status'],
                'timestamp': row['timestamp'],
                'qr_link': row['qr_link'],
                'payment_time': row['payment_time'],
                'card': row['card'],
                'owner': row['owner']
            })
        
        return {
            'payments': payments,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }


def get_payment_by_id(payment_id):
    """Get single payment by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            'id': row['id'],
            'order_id': row['order_id'],
            'amount': row['amount'],
            'success': bool(row['success']),
            'status': row['status'],
            'timestamp': row['timestamp'],
            'qr_link': row['qr_link'],
            'payment_time': row['payment_time'],
            'card': row['card'],
            'owner': row['owner']
        }


def get_all_payments():
    """Get all payments (for export)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        
        payments = []
        for row in rows:
            payments.append({
                'id': row['id'],
                'order_id': row['order_id'],
                'amount': row['amount'],
                'success': bool(row['success']),
                'status': row['status'],
                'timestamp': row['timestamp'],
                'qr_link': row['qr_link'],
                'payment_time': row['payment_time'],
                'card': row['card'],
                'owner': row['owner']
            })
        
        return payments


def get_payments_by_period(start_date):
    """Get payments from specific date"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM payments WHERE timestamp >= ? ORDER BY timestamp DESC',
            (start_date.isoformat(),)
        )
        rows = cursor.fetchall()
        
        payments = []
        for row in rows:
            payments.append({
                'id': row['id'],
                'order_id': row['order_id'],
                'amount': row['amount'],
                'success': bool(row['success']),
                'status': row['status'],
                'timestamp': row['timestamp'],
                'qr_link': row['qr_link'],
                'payment_time': row['payment_time'],
                'card': row['card'],
                'owner': row['owner']
            })
        
        return payments


# ============= LOGS =============

def add_log(level, message):
    """Add log entry"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (timestamp, level, message)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), level, message))
        
        # Keep only last 1000 logs
        cursor.execute('''
            DELETE FROM logs WHERE id NOT IN (
                SELECT id FROM logs ORDER BY timestamp DESC LIMIT 1000
            )
        ''')


def get_logs(limit=50):
    """Get recent logs"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            logs.append({
                'timestamp': row['timestamp'],
                'level': row['level'],
                'message': row['message']
            })
        
        return logs


# ============= SETTINGS =============

def get_setting(key, default=None):
    """Get single setting"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        if not row:
            return default
        
        try:
            return json.loads(row['value'])
        except:
            return row['value']


def set_setting(key, value):
    """Set single setting"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Convert to JSON if not string
        if not isinstance(value, str):
            value = json.dumps(value)
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))


def get_all_settings():
    """Get all settings as dict"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        
        settings = {}
        for row in rows:
            try:
                settings[row['key']] = json.loads(row['value'])
            except:
                settings[row['key']] = row['value']
        
        return settings


def update_settings(settings_dict):
    """Update multiple settings"""
    for key, value in settings_dict.items():
        set_setting(key, value)


# ============= STATISTICS =============

def get_stats_summary():
    """Get summary statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Today
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN success = 1 THEN amount ELSE 0 END) as amount
            FROM payments
            WHERE DATE(timestamp) = DATE('now')
        ''')
        today = cursor.fetchone()
        
        # This week
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN success = 1 THEN amount ELSE 0 END) as amount
            FROM payments
            WHERE DATE(timestamp) >= DATE('now', 'weekday 0', '-7 days')
        ''')
        week = cursor.fetchone()
        
        # This month
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN success = 1 THEN amount ELSE 0 END) as amount
            FROM payments
            WHERE DATE(timestamp) >= DATE('now', 'start of month')
        ''')
        month = cursor.fetchone()
        
        # All time
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN success = 1 THEN amount ELSE 0 END) as amount
            FROM payments
        ''')
        all_time = cursor.fetchone()
        
        return {
            'today': {
                'total': today['total'],
                'success': today['success'] or 0,
                'amount': today['amount'] or 0
            },
            'week': {
                'total': week['total'],
                'success': week['success'] or 0,
                'amount': week['amount'] or 0
            },
            'month': {
                'total': month['total'],
                'success': month['success'] or 0,
                'amount': month['amount'] or 0
            },
            'all_time': {
                'total': all_time['total'],
                'success': all_time['success'] or 0,
                'amount': all_time['amount'] or 0
            }
        }


if __name__ == '__main__':
    # Initialize database when run directly
    init_database()
    print("Database module ready!")
