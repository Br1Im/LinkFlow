#!/usr/bin/env python3
"""
Тест конвертации валюты RUB -> UZS через API multitransfer.ru
"""

import sys
import os

# Добавляем путь к payment_service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from currency_converter import CurrencyConverter


def test_conversion():
    """Тестирует конвертацию валюты"""
    
    print("=" * 60)
    print("🔄 Тест конвертации валюты RUB -> UZS")
    print("=" * 60)
    
    converter = CurrencyConverter()
    
    # Тестовые суммы
    test_amounts = [1000, 2500, 5000, 10000]
    
    for amount_rub in test_amounts:
        print(f"\n💰 Конвертирую {amount_rub} RUB...")
        
        result = converter.convert_rub_to_uzs(amount_rub)
        
        if result:
            print(f"✅ Успешно:")
            print(f"   {result['amount_rub']} RUB = {result['amount_uzs']} UZS")
            print(f"   Курс: {result['exchange_rate']}")
            
            if 'commission' in result:
                commission = result['commission']
                print(f"   Комиссия: {commission}")
        else:
            print(f"❌ Ошибка конвертации")
    
    print("\n" + "=" * 60)
    print("✅ Тест завершен")
    print("=" * 60)


if __name__ == "__main__":
    test_conversion()
