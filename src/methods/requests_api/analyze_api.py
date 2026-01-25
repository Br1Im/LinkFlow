#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ перехваченных HTTP-запросов
"""

import json
from urllib.parse import urlparse, parse_qs

def analyze_captured_requests(filename='captured_requests.json'):
    """
    Анализирует перехваченные запросы и выводит структуру API
    """
    print("🔍 Анализ перехваченных запросов...\n")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            requests = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден!")
        print("Сначала запусти capture_requests.py")
        return
    
    print(f"📊 Всего запросов: {len(requests)}\n")
    print("="*80)
    
    # Группируем по эндпоинтам
    endpoints = {}
    
    for req in requests:
        url = req['url']
        method = req['method']
        parsed = urlparse(url)
        path = parsed.path
        
        key = f"{method} {path}"
        
        if key not in endpoints:
            endpoints[key] = {
                'count': 0,
                'examples': [],
                'headers': req['headers'],
                'query_params': parse_qs(parsed.query) if parsed.query else {}
            }
        
        endpoints[key]['count'] += 1
        
        if len(endpoints[key]['examples']) < 3:  # Сохраняем до 3 примеров
            example = {
                'url': url,
                'postData': req.get('postData')
            }
            endpoints[key]['examples'].append(example)
    
    # Выводим результаты
    for endpoint, data in sorted(endpoints.items()):
        print(f"\n🔹 {endpoint}")
        print(f"   Вызовов: {data['count']}")
        
        if data['query_params']:
            print(f"   Query параметры: {list(data['query_params'].keys())}")
        
        # Показываем важные заголовки
        important_headers = ['content-type', 'authorization', 'x-api-key', 'x-csrf-token']
        headers_to_show = {k: v for k, v in data['headers'].items() 
                          if k.lower() in important_headers}
        if headers_to_show:
            print(f"   Важные заголовки:")
            for k, v in headers_to_show.items():
                print(f"      {k}: {v}")
        
        # Показываем примеры данных
        for i, example in enumerate(data['examples'], 1):
            if example['postData']:
                print(f"   Пример {i} данных:")
                try:
                    # Пытаемся распарсить JSON
                    post_data = json.loads(example['postData'])
                    print(f"      {json.dumps(post_data, indent=6, ensure_ascii=False)[:300]}...")
                except:
                    print(f"      {example['postData'][:200]}...")
        
        print("   " + "-"*76)
    
    print("\n" + "="*80)
    print("\n💡 Рекомендации:")
    print("1. Найди эндпоинт для создания платежа (обычно POST /api/...)")
    print("2. Проверь какие данные отправляются в postData")
    print("3. Проверь нужны ли специальные заголовки (токены, CSRF)")
    print("4. Реализуй метод в multitransfer_payment.py")


if __name__ == "__main__":
    print("="*80)
    print("🔍 Анализ API multitransfer.ru")
    print("="*80 + "\n")
    
    analyze_captured_requests()
