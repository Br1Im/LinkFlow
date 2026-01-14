#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╨Ю╨Я╨в╨Ш╨Ь╨Ш╨Ч╨Ш╨а╨Ю╨Т╨Р╨Э╨Э╨Р╨п ╨░╨┤╨╝╨╕╨╜-╨┐╨░╨╜╨╡╨╗╤М ╤Б ╨┐╨░╤А╨░╨╗╨╗╨╡╨╗╤М╨╜╨╛╨╣ ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨╛╨╣
╨ж╨Х╨Ы╨м: ╨Я╨╛╨┤╨┤╨╡╤А╨╢╨║╨░ ╤З╨░╤Б╤В╤Л╤Е ╨╖╨░╨┐╤А╨╛╤Б╨╛╨▓ (1-3s ╨╕╨╜╤В╨╡╤А╨▓╨░╨╗) ╨╕ ╤Г╤Б╨║╨╛╤А╨╡╨╜╨╕╨╡ ╨┤╨╛ 8-12s
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import uuid
import time
import os
from datetime import datetime
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import sys

# ╨Ф╨╛╨▒╨░╨▓╨╗╤П╨╡╨╝ ╨┐╤Г╤В╤М ╨┤╨╗╤П ╨╕╨╝╨┐╨╛╤А╤В╨░ ╨╝╨╛╨┤╤Г╨╗╨╡╨╣
sys.path.append('/app/bot')

from payment_service_turbo import create_payment_fast as create_payment
from database import db

# ╨Э╨░╤Б╤В╤А╨╛╨╣╨║╨░ ╨╗╨╛╨│╨╕╤А╨╛╨▓╨░╨╜╨╕╤П
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

# ╨С╨░╨╖╨░ ╨┤╨░╨╜╨╜╤Л╤Е ╤Б╨╛╨╖╨┤╨░╨╜╨╜╤Л╤Е ╤Б╤Б╤Л╨╗╨╛╨║
payment_links = {}

# ╨Я╤Г╨╗ ╨┐╨╛╤В╨╛╨║╨╛╨▓ ╨┤╨╗╤П ╨┐╨░╤А╨░╨╗╨╗╨╡╨╗╤М╨╜╨╛╨╣ ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨╕
executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="payment_worker")

# ╨б╤В╨░╤В╨╕╤Б╤В╨╕╨║╨░
stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'concurrent_requests': 0,
    'avg_response_time': 0,
    'start_time': time.time()
}
stats_lock = threading.Lock()

def update_stats(success, response_time):
    """╨Ю╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╨╡ ╤Б╤В╨░╤В╨╕╤Б╤В╨╕╨║╨╕"""
    with stats_lock:
        stats['total_requests'] += 1
        if success:
            stats['successful_requests'] += 1
        else:
            stats['failed_requests'] += 1
        
        # ╨Ю╨▒╨╜╨╛╨▓╨╗╤П╨╡╨╝ ╤Б╤А╨╡╨┤╨╜╨╡╨╡ ╨▓╤А╨╡╨╝╤П ╨╛╤В╨▓╨╡╤В╨░
        if stats['total_requests'] > 1:
            stats['avg_response_time'] = (
                (stats['avg_response_time'] * (stats['total_requests'] - 1) + response_time) 
                / stats['total_requests']
            )
        else:
            stats['avg_response_time'] = response_time

def process_payment_async(request_id, amount, order_id):
    """╨Р╤Б╨╕╨╜╤Е╤А╨╛╨╜╨╜╨░╤П ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨░ ╨┐╨╗╨░╤В╨╡╨╢╨░"""
    start_time = time.time()
    
    with stats_lock:
        stats['concurrent_requests'] += 1
    
    try:
        logger.info(f"ЁЯЪА ╨Э╨░╤З╨╕╨╜╨░╤О ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╤Г ╨┐╨╗╨░╤В╨╡╨╢╨░ {request_id}: {amount} ╤Б╤Г╨╝")
        
        # ╨Я╤А╤П╨╝╨╛╨╣ ╨▓╤Л╨╖╨╛╨▓ ╨▒╨╡╨╖ ╨╛╤З╨╡╤А╨╡╨┤╨╕ ╨┤╨╗╤П ╨╝╨░╨║╤Б╨╕╨╝╨░╨╗╤М╨╜╨╛╨╣ ╤Б╨║╨╛╤А╨╛╤Б╤В╨╕
        result = create_payment(amount)
        
        elapsed = time.time() - start_time
        
        if result and result.get('success'):
            logger.info(f"тЬЕ ╨Я╨╗╨░╤В╨╡╨╢ {request_id} ╤Г╤Б╨┐╨╡╤И╨╡╨╜ ╨╖╨░ {elapsed:.1f}s")
            
            # ╨б╨╛╤Е╤А╨░╨╜╤П╨╡╨╝ ╤А╨╡╨╖╤Г╨╗╤М╤В╨░╤В
            payment_data = {
                'id': request_id,
                'amount': amount,
                'order_id': order_id,
                'payment_link': result.get('payment_link'),
                'qr_base64': result.get('qr_base64'),
                'created_at': datetime.now().isoformat(),
                'processing_time': elapsed,
                'status': 'completed'
            }
            
            payment_links[request_id] = payment_data
            update_stats(True, elapsed)
            
            return {
                'success': True,
                'request_id': request_id,
                'order_id': order_id,
                'payment_link': result.get('payment_link'),
                'qr_base64': result.get('qr_base64'),
                'processing_time': elapsed
            }
        else:
            error = result.get('error', '╨Э╨╡╨╕╨╖╨▓╨╡╤Б╤В╨╜╨░╤П ╨╛╤И╨╕╨▒╨║╨░') if result else '╨Э╨╡╤В ╤А╨╡╨╖╤Г╨╗╤М╤В╨░╤В╨░'
            logger.error(f"тЭМ ╨Я╨╗╨░╤В╨╡╨╢ {request_id} ╨╜╨╡╤Г╨┤╨░╤З╨╡╨╜ ╨╖╨░ {elapsed:.1f}s: {error}")
            
            update_stats(False, elapsed)
            
            return {
                'success': False,
                'request_id': request_id,
                'order_id': order_id,
                'error': error,
                'processing_time': elapsed
            }
            
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"ЁЯТе ╨Ш╤Б╨║╨╗╤О╤З╨╡╨╜╨╕╨╡ ╨▓ ╨┐╨╗╨░╤В╨╡╨╢╨╡ {request_id} ╨╖╨░ {elapsed:.1f}s: {e}")
        
        update_stats(False, elapsed)
        
        return {
            'success': False,
            'request_id': request_id,
            'order_id': order_id,
            'error': str(e),
            'processing_time': elapsed
        }
    finally:
        with stats_lock:
            stats['concurrent_requests'] -= 1

# API TOKEN ╨┤╨╗╤П ╨░╨▓╤В╨╛╤А╨╕╨╖╨░╤Ж╨╕╨╕
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def verify_token():
    """╨Я╤А╨╛╨▓╨╡╤А╨║╨░ Bearer ╤В╨╛╨║╨╡╨╜╨░"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    return token == API_TOKEN

@app.route('/api/payment', methods=['POST'])
def create_payment_api_optimized():
    """╨Ю╨Я╨в╨Ш╨Ь╨Ш╨Ч╨Ш╨а╨Ю╨Т╨Р╨Э╨Э╨л╨Щ API ╨┤╨╗╤П ╤Б╨╛╨╖╨┤╨░╨╜╨╕╤П ╨┐╨╗╨░╤В╨╡╨╢╨░ ╤Б ╨┐╨░╤А╨░╨╗╨╗╨╡╨╗╤М╨╜╨╛╨╣ ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨╛╨╣"""
    
    # ╨Я╤А╨╛╨▓╨╡╤А╨║╨░ ╨░╨▓╤В╨╛╤А╨╕╨╖╨░╤Ж╨╕╨╕
    if not verify_token():
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Invalid or missing Bearer token"
        }), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON"
            }), 400
        
        # ╨Т╨░╨╗╨╕╨┤╨░╤Ж╨╕╤П ╨┤╨░╨╜╨╜╤Л╤Е
        amount = data.get('amount')
        order_id = data.get('orderId')
        
        if not amount:
            return jsonify({
                "success": False,
                "error": "Missing required field: amount"
            }), 400
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({
                "success": False,
                "error": "Invalid amount: must be positive number"
            }), 400
        
        if not order_id:
            return jsonify({
                "success": False,
                "error": "Missing required field: orderId"
            }), 400
        
        # ╨Я╤А╨╛╨▓╨╡╤А╨║╨░ ╨╜╨░ ╨┤╤Г╨▒╨╗╨╕╤А╨╛╨▓╨░╨╜╨╕╨╡ orderId
        for existing_payment in payment_links.values():
            if existing_payment.get('order_id') == order_id:
                return jsonify({
                    "success": False,
                    "error": f"Duplicate orderId: {order_id}",
                    "existing_payment": {
                        "request_id": existing_payment['id'],
                        "payment_link": existing_payment.get('payment_link'),
                        "created_at": existing_payment.get('created_at')
                    }
                }), 409
        
        # ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╨╝ ╤Г╨╜╨╕╨║╨░╨╗╤М╨╜╤Л╨╣ ID ╨╖╨░╨┐╤А╨╛╤Б╨░
        request_id = str(uuid.uuid4())
        
        logger.info(f"ЁЯУе ╨Э╨╛╨▓╤Л╨╣ ╨╖╨░╨┐╤А╨╛╤Б {request_id}: amount={amount}, orderId={order_id}")
        
        # ╨Я╨Р╨а╨Р╨Ы╨Ы╨Х╨Ы╨м╨Э╨Р╨п ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨░ - ╨╜╨╡ ╨╢╨┤╨╡╨╝ ╤А╨╡╨╖╤Г╨╗╤М╤В╨░╤В╨░
        future = executor.submit(process_payment_async, request_id, amount, order_id)
        
        # ╨Ц╨┤╨╡╨╝ ╤А╨╡╨╖╤Г╨╗╤М╤В╨░╤В ╤Б ╤В╨░╨╣╨╝╨░╤Г╤В╨╛╨╝ (╨┤╨╗╤П ╨▓╨╜╨╡╤И╨╜╨╕╤Е ╨║╨╗╨╕╨╡╨╜╤В╨╛╨▓)
        try:
            result = future.result(timeout=60)  # ╨г╨▓╨╡╨╗╨╕╤З╨╡╨╜ ╨┤╨╛ 60 ╤Б╨╡╨║╤Г╨╜╨┤ ╨┤╨╗╤П ╤Б╤В╨░╨▒╨╕╨╗╤М╨╜╨╛╨╣ ╤А╨░╨▒╨╛╤В╤Л
            
            if result['success']:
                return jsonify({
                    "success": True,
                    "request_id": result['request_id'],
                    "order_id": result['order_id'],
                    "payment_link": result['payment_link'],
                    "qr_base64": result['qr_base64'],
                    "processing_time": result['processing_time'],
                    "message": "Payment created successfully"
                }), 201
            else:
                return jsonify({
                    "success": False,
                    "request_id": result['request_id'],
                    "order_id": result['order_id'],
                    "error": result['error'],
                    "processing_time": result['processing_time']
                }), 500
                
        except TimeoutError:
            # ╨Х╤Б╨╗╨╕ ╨┐╤А╨╡╨▓╤Л╤И╨╡╨╜ ╤В╨░╨╣╨╝╨░╤Г╤В, ╨▓╨╛╨╖╨▓╤А╨░╤Й╨░╨╡╨╝ ╤Б╤В╨░╤В╤Г╤Б "╨▓ ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨╡"
            return jsonify({
                "success": False,
                "request_id": request_id,
                "order_id": order_id,
                "error": "Processing timeout",
                "message": "Payment processing took longer than 60 seconds",
                "processing_time": 60
            }), 408
            
    except Exception as e:
        logger.error(f"ЁЯТе ╨Ъ╤А╨╕╤В╨╕╤З╨╡╤Б╨║╨░╤П ╨╛╤И╨╕╨▒╨║╨░ API: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Internal server error"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """╨Я╨╛╨╗╤Г╤З╨╡╨╜╨╕╨╡ ╤Б╤В╨░╤В╨╕╤Б╤В╨╕╨║╨╕ ╤Б╨╕╤Б╤В╨╡╨╝╤Л"""
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401
    
    with stats_lock:
        uptime = time.time() - stats['start_time']
        current_stats = stats.copy()
        current_stats['uptime_seconds'] = uptime
        current_stats['uptime_formatted'] = f"{uptime/3600:.1f} hours"
        current_stats['success_rate'] = (
            (current_stats['successful_requests'] / current_stats['total_requests'] * 100)
            if current_stats['total_requests'] > 0 else 0
        )
    
    return jsonify(current_stats)

@app.route('/api/health', methods=['GET'])
def health_check_optimized():
    """╨Ю╨┐╤В╨╕╨╝╨╕╨╖╨╕╤А╨╛╨▓╨░╨╜╨╜╨░╤П ╨┐╤А╨╛╨▓╨╡╤А╨║╨░ ╨╖╨┤╨╛╤А╨╛╨▓╤М╤П ╤Б╨╕╤Б╤В╨╡╨╝╤Л"""
    try:
        # ╨С╤Л╤Б╤В╤А╨░╤П ╨┐╤А╨╛╨▓╨╡╤А╨║╨░ ╨║╨╛╨╝╨┐╨╛╨╜╨╡╨╜╤В╨╛╨▓
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": "healthy",
                "browser_manager": "healthy",
                "thread_pool": "healthy"
            },
            "stats": {
                "concurrent_requests": stats['concurrent_requests'],
                "total_requests": stats['total_requests'],
                "avg_response_time": f"{stats['avg_response_time']:.1f}s"
            }
        }
        
        # ╨Я╤А╨╛╨▓╨╡╤А╨║╨░ ╨▒╨░╨╖╤Л ╨┤╨░╨╜╨╜╤Л╤Е
        try:
            accounts = db.get_accounts()
            cards = db.get_requisites()
            if not accounts or not cards:
                health_status["components"]["database"] = "warning"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["database"] = "unhealthy"
            health_status["status"] = "unhealthy"
        
        # ╨Я╤А╨╛╨▓╨╡╤А╨║╨░ ╨┐╤Г╨╗╨░ ╨┐╨╛╤В╨╛╨║╨╛╨▓
        if executor._threads and len(executor._threads) > 0:
            health_status["components"]["thread_pool"] = "healthy"
        else:
            health_status["components"]["thread_pool"] = "warning"
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/api/payment/<request_id>', methods=['GET'])
def get_payment_status(request_id):
    """╨Я╨╛╨╗╤Г╤З╨╡╨╜╨╕╨╡ ╤Б╤В╨░╤В╤Г╤Б╨░ ╨║╨╛╨╜╨║╤А╨╡╤В╨╜╨╛╨│╨╛ ╨┐╨╗╨░╤В╨╡╨╢╨░"""
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401
    
    if request_id in payment_links:
        return jsonify(payment_links[request_id])
    else:
        return jsonify({
            "success": False,
            "error": "Payment not found",
            "request_id": request_id
        }), 404

# ╨Ю╤Б╤В╨░╨╗╤М╨╜╤Л╨╡ endpoints (accounts, cards, etc.) ╨╛╤Б╤В╨░╤О╤В╤Б╤П ╨▒╨╡╨╖ ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╨╣
@app.route('/api/accounts')
def get_accounts():
    """╨Я╨╛╨╗╤Г╤З╨╡╨╜╨╕╨╡ ╨▓╤Б╨╡╤Е ╨░╨║╨║╨░╤Г╨╜╤В╨╛╨▓"""
    accounts = db.get_accounts()
    return jsonify(accounts)

@app.route('/api/cards')
def get_cards():
    """╨Я╨╛╨╗╤Г╤З╨╡╨╜╨╕╨╡ ╨▓╤Б╨╡╤Е ╨║╨░╤А╤В"""
    cards = db.get_requisites()
    return jsonify(cards)

@app.route('/')
def admin_panel():
    """╨У╨╗╨░╨▓╨╜╨░╤П ╤Б╤В╤А╨░╨╜╨╕╤Ж╨░ ╨░╨┤╨╝╨╕╨╜-╨┐╨░╨╜╨╡╨╗╨╕"""
    return jsonify({
        "message": "Optimized Payment System API",
        "version": "2.0",
        "features": [
            "Parallel processing",
            "Fast response (8-12s target)",
            "High frequency support (1-3s intervals)",
            "Thread pool execution",
            "Real-time statistics"
        ],
        "endpoints": {
            "POST /api/payment": "Create payment (optimized)",
            "GET /api/stats": "System statistics",
            "GET /api/health": "Health check",
            "GET /api/payment/<id>": "Payment status"
        }
    })

if __name__ == '__main__':
    logger.info("ЁЯЪА ╨Ч╨░╨┐╤Г╤Б╨║ ╨Ю╨Я╨в╨Ш╨Ь╨Ш╨Ч╨Ш╨а╨Ю╨Т╨Р╨Э╨Э╨Ю╨Щ ╤Б╨╕╤Б╤В╨╡╨╝╤Л ╨┐╨╗╨░╤В╨╡╨╢╨╡╨╣")
    logger.info("тЪб ╨Я╨╛╨┤╨┤╨╡╤А╨╢╨║╨░ ╨┐╨░╤А╨░╨╗╨╗╨╡╨╗╤М╨╜╨╛╨╣ ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨╕")
    logger.info("ЁЯОп ╨ж╨╡╨╗╤М: 8-12 ╤Б╨╡╨║╤Г╨╜╨┤ ╨╜╨░ ╨┐╨╗╨░╤В╨╡╨╢")
    logger.info("ЁЯФе ╨Я╨╛╨┤╨┤╨╡╤А╨╢╨║╨░ ╤З╨░╤Б╤В╤Л╤Е ╨╖╨░╨┐╤А╨╛╤Б╨╛╨▓ (1-3s)")
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
