#!/usr/bin/env python3
"""
Простой скрипт для создания множества платежей подряд
Перезапускает браузер после каждого платежа для 100% стабильности
"""

import asyncio
import sys
from payment_service import PaymentService, log

# Данные для платежей
PAYMENTS = [
    {"amount": 110, "card": "9860080323894719", "owner": "Nodir Asadullayev"},
    {"amount": 110, "card": "9860080323894719", "owner": "Nodir Asadullayev"},
    {"amount": 110, "card": "9860080323894719", "owner": "Nodir Asadullayev"},
]


async def create_single_payment(payment_data: dict, index: int) -> dict:
    """Создает один платеж с полным перезапуском браузера"""
    log("=" * 70, "INFO")
    log(f"ПЛАТЕЖ #{index + 1}", "INFO")
    log("=" * 70, "INFO")
    
    service = PaymentService()
    
    try:
        # Запускаем браузер
        await service.start(headless=True)
        
        # Создаем платеж
        result = await service.create_payment_link(
            amount=payment_data["amount"],
            card_number=payment_data["card"],
            owner_name=payment_data["owner"]
        )
        
        # Останавливаем браузер
        await service.stop()
        
        return result
        
    except Exception as e:
        log(f"Критическая ошибка: {e}", "ERROR")
        try:
            await service.stop()
        except:
            pass
        return {
            'success': False,
            'qr_link': None,
            'time': 0,
            'step1_time': 0,
            'step2_time': 0,
            'error': str(e)
        }


async def main():
    """Создает множество платежей подряд"""
    log("🚀 ЗАПУСК МАССОВОГО СОЗДАНИЯ ПЛАТЕЖЕЙ", "INFO")
    log(f"Количество платежей: {len(PAYMENTS)}", "INFO")
    log("=" * 70, "INFO")
    
    results = []
    
    for i, payment_data in enumerate(PAYMENTS):
        result = await create_single_payment(payment_data, i)
        results.append(result)
        
        if result['success']:
            log(f"✅ Платеж #{i + 1}: Успех!", "SUCCESS")
            log(f"   Этап 1: {result['step1_time']:.2f}s", "INFO")
            log(f"   Этап 2: {result['step2_time']:.2f}s", "INFO")
            log(f"   Общее время: {result['time']:.2f}s", "INFO")
            if result['qr_link']:
                log(f"   QR: {result['qr_link'][:60]}...", "SUCCESS")
        else:
            log(f"❌ Платеж #{i + 1}: Ошибка - {result['error']}", "ERROR")
        
        # Пауза между платежами
        if i < len(PAYMENTS) - 1:
            log("Пауза 2 секунды...", "INFO")
            await asyncio.sleep(2)
    
    # Итоговая статистика
    log("=" * 70, "INFO")
    log("ИТОГОВАЯ СТАТИСТИКА", "INFO")
    log("=" * 70, "INFO")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    log(f"Всего платежей: {len(results)}", "INFO")
    log(f"Успешных: {len(successful)}", "SUCCESS")
    log(f"Провалено: {len(failed)}", "ERROR")
    log(f"Успешность: {len(successful)/len(results)*100:.1f}%", "INFO")
    
    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        avg_step1 = sum(r['step1_time'] for r in successful) / len(successful)
        avg_step2 = sum(r['step2_time'] for r in successful) / len(successful)
        log(f"Среднее время: {avg_time:.2f}s", "INFO")
        log(f"Средний этап 1: {avg_step1:.2f}s", "INFO")
        log(f"Средний этап 2: {avg_step2:.2f}s", "INFO")
    
    # Выводим QR ссылки
    if successful:
        log("=" * 70, "INFO")
        log("QR ССЫЛКИ", "INFO")
        log("=" * 70, "INFO")
        for i, result in enumerate(results):
            if result['success'] and result['qr_link']:
                log(f"Платеж #{i + 1}: {result['qr_link']}", "SUCCESS")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Прервано пользователем", "WARNING")
        sys.exit(0)
