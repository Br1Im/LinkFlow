# -*- coding: utf-8 -*-
"""
Система управления режимами создания платежей
- HYBRID: Быстрый режим (API + Selenium для авторизации) ~1-2 сек
- SELENIUM: Надежный режим (только Selenium) ~3-5 сек
"""

import json
import os
from enum import Enum

class PaymentMode(Enum):
    HYBRID = "hybrid"      # Быстрый режим (по умолчанию)
    SELENIUM = "selenium"  # Надежный режим

class PaymentModeManager:
    """Менеджер режимов создания платежей"""
    
    CONFIG_FILE = "payment_mode_config.json"
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        """Загрузка конфигурации"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        "mode": PaymentMode(data.get("mode", "selenium")),  # Default to selenium
                        "hybrid_failures": data.get("hybrid_failures", 0),
                        "auto_fallback": data.get("auto_fallback", True)
                    }
            except:
                pass
        
        # Конфигурация по умолчанию
        return {
            "mode": PaymentMode.SELENIUM,  # SELENIUM по умолчанию (надежнее)
            "hybrid_failures": 0,
            "auto_fallback": True  # Автоматическое переключение при ошибках
        }
    
    def _save_config(self):
        """Сохранение конфигурации"""
        try:
            data = {
                "mode": self.config["mode"].value,
                "hybrid_failures": self.config["hybrid_failures"],
                "auto_fallback": self.config["auto_fallback"]
            }
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Не удалось сохранить конфигурацию: {e}")
    
    def get_mode(self) -> PaymentMode:
        """Получить текущий режим"""
        return self.config["mode"]
    
    def set_mode(self, mode: PaymentMode):
        """Установить режим вручную"""
        self.config["mode"] = mode
        self.config["hybrid_failures"] = 0  # Сброс счетчика ошибок
        self._save_config()
        print(f"✅ Режим изменен на: {mode.value.upper()}")
    
    def report_hybrid_failure(self):
        """Сообщить об ошибке гибридного режима"""
        self.config["hybrid_failures"] += 1
        self._save_config()
        
        # Автоматическое переключение после 3 ошибок подряд
        if self.config["auto_fallback"] and self.config["hybrid_failures"] >= 3:
            print(f"⚠️ Гибридный режим: {self.config['hybrid_failures']} ошибок подряд")
            print(f"🔄 Автоматическое переключение на SELENIUM режим")
            self.config["mode"] = PaymentMode.SELENIUM
            self._save_config()
            return True
        
        return False
    
    def report_hybrid_success(self):
        """Сообщить об успехе гибридного режима"""
        if self.config["hybrid_failures"] > 0:
            self.config["hybrid_failures"] = 0
            self._save_config()
    
    def get_status(self) -> str:
        """Получить статус режимов"""
        mode = self.config["mode"]
        failures = self.config["hybrid_failures"]
        auto_fallback = self.config["auto_fallback"]
        
        status = f"🔧 РЕЖИМ СОЗДАНИЯ ПЛАТЕЖЕЙ\n\n"
        
        if mode == PaymentMode.SELENIUM:
            status += "✅ Текущий режим: SELENIUM (Надежный)\n"
            status += "   Скорость: ~3-5 секунд\n"
            status += "   Метод: Только Selenium\n"
        else:
            status += "⚠️ Текущий режим: HYBRID (Экспериментальный)\n"
            status += "   Скорость: ~1-2 секунды (цель)\n"
            status += "   Метод: API + Selenium\n"
            status += "   Статус: В РАЗРАБОТКЕ\n"
        
        status += f"\n📊 Статистика:\n"
        status += f"   Ошибок гибридного режима: {failures}\n"
        status += f"   Авто-переключение: {'Включено' if auto_fallback else 'Выключено'}\n"
        
        if auto_fallback:
            status += f"\n💡 При 3 ошибках подряд автоматически переключится на SELENIUM"
        
        return status
    
    def toggle_auto_fallback(self):
        """Переключить автоматическое переключение"""
        self.config["auto_fallback"] = not self.config["auto_fallback"]
        self._save_config()
        
        if self.config["auto_fallback"]:
            print("✅ Автоматическое переключение ВКЛЮЧЕНО")
        else:
            print("⚠️ Автоматическое переключение ВЫКЛЮЧЕНО")


# Глобальный экземпляр
mode_manager = PaymentModeManager()
