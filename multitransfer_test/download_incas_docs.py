#!/usr/bin/env python3
"""
Скрипт для загрузки документации Incas API
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def download_incas_docs():
    """Загрузка документации с сайта Incas"""
    
    print("🚀 Запуск браузера...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080}
    )
    
    page = await context.new_page()
    
    print("📄 Загрузка страницы документации...")
    await page.goto('https://developer.incas.world/', wait_until='networkidle', timeout=60000)
    
    # Ждем загрузки контента
    await asyncio.sleep(5)
    
    print("📝 Извлечение текста документации...")
    
    # Получаем весь текст со страницы
    full_text = await page.evaluate("""
        () => {
            return document.body.innerText;
        }
    """)
    
    # Сохраняем в файл
    with open('INCAS_API_FULL.txt', 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"✅ Документация сохранена в INCAS_API_FULL.txt ({len(full_text)} символов)")
    
    # Пытаемся получить структурированные данные
    print("🔍 Извлечение структурированных данных...")
    
    api_data = await page.evaluate("""
        () => {
            const endpoints = [];
            
            // Ищем все эндпоинты на странице
            const operations = document.querySelectorAll('[data-section-id]');
            
            operations.forEach(op => {
                const title = op.querySelector('h2, h3, h4');
                const method = op.querySelector('[data-role="method"]');
                const path = op.querySelector('[data-role="path"]');
                const description = op.querySelector('[data-role="description"]');
                
                if (title) {
                    endpoints.push({
                        title: title.innerText,
                        method: method ? method.innerText : '',
                        path: path ? path.innerText : '',
                        description: description ? description.innerText : '',
                        html: op.innerHTML.substring(0, 500)
                    });
                }
            });
            
            return {
                endpoints: endpoints,
                fullHTML: document.body.innerHTML
            };
        }
    """)
    
    # Сохраняем HTML
    with open('INCAS_API.html', 'w', encoding='utf-8') as f:
        f.write(api_data['fullHTML'])
    
    print(f"✅ HTML сохранен в INCAS_API.html")
    print(f"📊 Найдено эндпоинтов: {len(api_data['endpoints'])}")
    
    # Сохраняем JSON
    with open('INCAS_API.json', 'w', encoding='utf-8') as f:
        json.dump(api_data['endpoints'], f, ensure_ascii=False, indent=2)
    
    print("✅ Структура сохранена в INCAS_API.json")
    
    # Скриншот
    await page.screenshot(path='incas_docs_screenshot.png', full_page=True)
    print("✅ Скриншот сохранен")
    
    print("\n⏸️  Браузер остается открытым 30 секунд для просмотра...")
    await asyncio.sleep(30)
    
    await browser.close()
    await playwright.stop()
    
    print("\n✅ Готово!")

if __name__ == "__main__":
    asyncio.run(download_incas_docs())
