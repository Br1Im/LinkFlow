#!/usr/bin/env python3
"""
Отладка: что админка отправляет на API
Запускаем прокси между админкой и API сервером
"""

from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/api/create-payment', methods=['POST'])
def proxy_create_payment():
    """Прокси запрос с логированием"""
    
    print("\n" + "="*60)
    print("ПЕРЕХВАЧЕН ЗАПРОС ОТ АДМИНКИ")
    print("="*60)
    
    # Логируем всё что пришло
    print(f"\nHeaders:")
    for key, value in request.headers:
        print(f"  {key}: {value}")
    
    print(f"\nContent-Type: {request.content_type}")
    print(f"Is JSON: {request.is_json}")
    
    try:
        data = request.get_json()
        print(f"\nJSON Payload:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n❌ Ошибка парсинга JSON: {e}")
        print(f"Raw data: {request.data}")
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    
    # Проверяем наличие requisite_api
    if 'requisite_api' in data:
        print(f"\n✅ requisite_api присутствует: {data['requisite_api']}")
    else:
        print(f"\n⚠️ requisite_api ОТСУТСТВУЕТ! Будет использовано значение по умолчанию")
    
    # Пересылаем на реальный API
    print(f"\nПересылаю на http://localhost:5001/api/create-payment...")
    
    try:
        response = requests.post(
            "http://localhost:5001/api/create-payment",
            json=data,
            timeout=120
        )
        
        print(f"\nОтвет от API:")
        print(f"Status: {response.status_code}")
        
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return jsonify(result), response.status_code
        
    except Exception as e:
        print(f"\n❌ Ошибка при обращении к API: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("="*60)
    print("ПРОКСИ-СЕРВЕР ДЛЯ ОТЛАДКИ")
    print("="*60)
    print("\nЗапускаю прокси на порту 5002...")
    print("Измените в admin_panel_db.py:")
    print("  API_URL = 'http://localhost:5002'")
    print("\nИли в настройках админки укажите:")
    print("  http://localhost:5002")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5002, debug=False)
