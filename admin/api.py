#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API для внешних запросов на создание платежей
Порт: 5001
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, request, jsonify
from datetime import datetime
import threading
import pickle

from src.multitransfer_payment import MultitransferPayment
from src.config import EXAMPLE_SENDER_DATA

app = Flask(__name__)

# Bearer токен для авторизации
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

# Путь к файлу хранилища (общий с admin panel)
STORAGE_FILE = '/tmp/linkflow_payments.pkl'

# Хранилище платежей (в продакшене использовать БД)
payments_storage = []
payment_lock = threading.Lock()

def load_payments():
    """Загрузить платежи из файла"""
    global payments_storage
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'rb') as f:
                payments_storage = pickle.load(f)
    except Exception as e:
        print(f"⚠️ Ошибка загрузки платежей: {e}")
        payments_storage = []

def save_payments():
    """Сохранить платежи в файл"""
    try:
        with open(STORAGE_FILE, 'wb') as f:
            pickle.dump(payments_storage, f)
    except Exception as e:
        print(f"⚠️ Ошибка сохранения платежей: {e}")

# Загружаем платежи при старте
load_payments()


def check_auth():
    """Проверка Bearer токена"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    
    try:
        scheme, token = auth_header.split(' ', 1)
        if scheme.lower() != 'bearer':
            return False
        return token == API_TOKEN
    except:
        return False


@app.route('/api/payment', methods=['POST'])
def create_payment():
    """API для создания платежа через внешний запрос"""
    
    # Проверка авторизации
    if not check_auth():
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 401
    
    try:
        # Получаем JSON данные
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON'
            }), 400
        
        print(f"📥 Получен запрос: {data}")
        
        # Валидация
        amount = data.get('amount')
        order_id = data.get('orderId')
        
        if not amount or not order_id:
            return jsonify({
                'success': False,
                'error': 'amount and orderId are required'
            }), 400
        
        amount = int(amount)
        
        if amount < 100 or amount > 120000:
            return jsonify({
                'success': False,
                'error': 'Amount must be between 100 and 120000 RUB'
            }), 400
        
        # Данные получателя (фиксированные)
        card_number = '9860080323894719'
        owner_name = 'Nodir Asadullayev'
        
        # Создание платежа СИНХРОННО (ждем завершения)
        load_payments()  # Загружаем актуальные данные
        payment_id = len(payments_storage) + 1
        
        with payment_lock:
            payments_storage.append({
                'id': payment_id,
                'order_id': order_id,
                'card_number': card_number,
                'owner_name': owner_name,
                'amount': amount,
                'status': 'processing',
                'created_at': datetime.now().isoformat(),
                'result': None
            })
            save_payments()
        
        print(f"🚀 Создаю платеж #{payment_id} синхронно...")
        
        # Создаем платеж СИНХРОННО (блокирующий вызов)
        try:
            payment = MultitransferPayment(sender_data=EXAMPLE_SENDER_DATA, headless=False)  # Визуализация
            payment.login()
            
            result = payment.create_payment(
                card_number=card_number,
                owner_name=owner_name,
                amount=amount
            )
            
            payment.close()
            
            # Обновляем статус
            with payment_lock:
                load_payments()
                for p in payments_storage:
                    if p['id'] == payment_id:
                        p['status'] = 'completed' if result.get('success') else 'failed'
                        p['result'] = result
                        p['completed_at'] = datetime.now().isoformat()
                        break
                save_payments()
            
            # Возвращаем результат с ссылкой и QR-кодом
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'payment_id': payment_id,
                    'order_id': order_id,
                    'amount': amount,
                    'status': 'completed',
                    'payment_link': result.get('payment_link'),
                    'qr_code': result.get('qr_code'),
                    'elapsed_time': result.get('elapsed_time'),
                    'message': 'Payment created successfully'
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'payment_id': payment_id,
                    'order_id': order_id,
                    'error': result.get('error', 'Payment creation failed')
                }), 500
                
        except Exception as e:
            # Обновляем статус при ошибке
            with payment_lock:
                load_payments()
                for p in payments_storage:
                    if p['id'] == payment_id:
                        p['status'] = 'failed'
                        p['result'] = {'error': str(e), 'success': False}
                        p['completed_at'] = datetime.now().isoformat()
                        break
                save_payments()
            
            return jsonify({
                'success': False,
                'payment_id': payment_id,
                'order_id': order_id,
                'error': str(e)
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/payment/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Получить статус платежа"""
    
    # Проверка авторизации
    if not check_auth():
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 401
    
    load_payments()  # Загружаем актуальные данные
    with payment_lock:
        for payment in payments_storage:
            if payment['id'] == payment_id:
                return jsonify({
                    'success': True,
                    'payment': payment
                })
    
    return jsonify({
        'success': False,
        'error': 'Payment not found'
    }), 404


@app.route('/api/payment/order/<order_id>', methods=['GET'])
def get_payment_by_order(order_id):
    """Получить статус платежа по orderId"""
    
    # Проверка авторизации
    if not check_auth():
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 401
    
    load_payments()  # Загружаем актуальные данные
    with payment_lock:
        for payment in payments_storage:
            if payment.get('order_id') == order_id:
                return jsonify({
                    'success': True,
                    'payment': payment
                })
    
    return jsonify({
        'success': False,
        'error': 'Payment not found'
    }), 404


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'LinkFlow API',
        'version': '1.0.0'
    })


def process_payment(payment_id, card_number, owner_name, amount, sender_data):
    """Обработка платежа в фоновом режиме"""
    try:
        payment = MultitransferPayment(sender_data=sender_data, headless=True)
        payment.login()
        
        result = payment.create_payment(
            card_number=card_number,
            owner_name=owner_name,
            amount=amount
        )
        
        payment.close()
        
        # Обновляем статус
        with payment_lock:
            load_payments()  # Загружаем актуальные данные
            for p in payments_storage:
                if p['id'] == payment_id:
                    p['status'] = 'completed' if result.get('success') else 'failed'
                    p['result'] = result
                    p['completed_at'] = datetime.now().isoformat()
                    break
            save_payments()
                    
    except Exception as e:
        with payment_lock:
            load_payments()  # Загружаем актуальные данные
            for p in payments_storage:
                if p['id'] == payment_id:
                    p['status'] = 'failed'
                    p['result'] = {'error': str(e), 'success': False}
                    p['completed_at'] = datetime.now().isoformat()
                    break
            save_payments()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 LinkFlow API Server")
    print("="*60)
    print(f"📍 URL: http://localhost:5001")
    print(f"🔑 Bearer Token: {API_TOKEN}")
    print(f"📊 Endpoints:")
    print(f"   POST   /api/payment")
    print(f"   GET    /api/payment/<payment_id>")
    print(f"   GET    /api/payment/order/<order_id>")
    print(f"   GET    /health")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
