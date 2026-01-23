#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Админ-панель для LinkFlow
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import threading

from src.multitransfer_payment import MultitransferPayment
from src.payment_manager import PaymentManager
from src.config import EXAMPLE_SENDER_DATA, EXAMPLE_RECIPIENT_DATA, MIN_AMOUNT, MAX_AMOUNT, PAYMENT_MODES

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Хранилище платежей (в продакшене использовать БД)
payments_storage = []
payment_lock = threading.Lock()


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', 
                         min_amount=MIN_AMOUNT, 
                         max_amount=MAX_AMOUNT,
                         payment_modes=PAYMENT_MODES,
                         default_card=EXAMPLE_RECIPIENT_DATA['card_number'],
                         default_owner=EXAMPLE_RECIPIENT_DATA['owner_name'])


@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    """API для создания платежа"""
    try:
        data = request.json
        
        # Валидация
        card_number = data.get('card_number', '').strip()
        owner_name = data.get('owner_name', '').strip()
        amount = int(data.get('amount', 0))
        payment_mode = data.get('payment_mode', 'standard')
        payment_system = data.get('payment_system', 'multitransfer')  # multitransfer или elecsnet
        
        if not card_number or not owner_name or not amount:
            return jsonify({'success': False, 'error': 'Все поля обязательны'}), 400
        
        # Получаем лимиты для выбранного режима
        mode_config = PAYMENT_MODES.get(payment_mode, PAYMENT_MODES['standard'])
        min_amount = mode_config['min_amount']
        max_amount = mode_config['max_amount']
        
        if amount < min_amount or amount > max_amount:
            return jsonify({
                'success': False, 
                'error': f'Для режима "{mode_config["name"]}" сумма должна быть от {min_amount} до {max_amount} RUB'
            }), 400
        
        # Данные отправителя (можно настроить через форму)
        sender_data = data.get('sender_data', EXAMPLE_SENDER_DATA)
        
        # Создание платежа в отдельном потоке
        payment_id = len(payments_storage) + 1
        
        with payment_lock:
            payments_storage.append({
                'id': payment_id,
                'card_number': card_number,
                'owner_name': owner_name,
                'amount': amount,
                'payment_mode': payment_mode,
                'payment_system': payment_system,
                'mode_name': mode_config['name'],
                'status': 'processing',
                'created_at': datetime.now().isoformat(),
                'result': None
            })
        
        # Запускаем создание платежа в фоне
        thread = threading.Thread(
            target=process_payment,
            args=(payment_id, card_number, owner_name, amount, sender_data, payment_system)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'payment_id': payment_id,
            'message': 'Платеж создается...'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def process_payment(payment_id, card_number, owner_name, amount, sender_data, payment_system='multitransfer'):
    """Обработка платежа в фоновом режиме"""
    try:
        # Создаем платеж через выбранную систему
        # skip_bank_selection=True для ускорения (банк уже выбран в URL)
        if payment_system == 'elecsnet':
            payment = PaymentManager(sender_data=sender_data, headless=True)
        else:
            payment = MultitransferPayment(sender_data=sender_data, headless=True, skip_bank_selection=True)
        
        payment.login()
        
        result = payment.create_payment(
            card_number=card_number,
            owner_name=owner_name,
            amount=amount
        )
        
        payment.close()
        
        # Обновляем статус
        with payment_lock:
            for p in payments_storage:
                if p['id'] == payment_id:
                    p['status'] = 'completed' if result.get('success') else 'failed'
                    p['result'] = result
                    p['completed_at'] = datetime.now().isoformat()
                    break
                    
    except Exception as e:
        with payment_lock:
            for p in payments_storage:
                if p['id'] == payment_id:
                    p['status'] = 'failed'
                    p['result'] = {'error': str(e), 'success': False}
                    p['completed_at'] = datetime.now().isoformat()
                    break


@app.route('/api/payment/<int:payment_id>')
def get_payment(payment_id):
    """Получить информацию о платеже"""
    with payment_lock:
        for payment in payments_storage:
            if payment['id'] == payment_id:
                return jsonify(payment)
    
    return jsonify({'error': 'Платеж не найден'}), 404


@app.route('/api/payments')
def get_payments():
    """Получить список всех платежей"""
    with payment_lock:
        return jsonify(payments_storage)


@app.route('/payments')
def payments_list():
    """Страница со списком платежей"""
    return render_template('payments.html')


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 LinkFlow Admin Panel")
    print("="*60)
    print(f"📍 URL: http://localhost:5000")
    print(f"📊 Лимиты: {MIN_AMOUNT}-{MAX_AMOUNT} RUB")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
