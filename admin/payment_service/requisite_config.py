#!/usr/bin/env python3
"""
Конфигурация для сервисов получения реквизитов
"""

# Выбор активного сервиса: 'merchant', 'h2h' или 'payzteam'
# 'h2h' - H2H API (РАБОТАЕТ! Возвращает реквизиты напрямую)
# 'merchant' - Merchant API (тоже работает, возвращает реквизиты + платежную ссылку)
# 'payzteam' - старый сервис
ACTIVE_REQUISITE_SERVICE = 'h2h'

# Конфигурация Merchant API (РАБОТАЕТ)
MERCHANT_CONFIG = {
    'base_url': 'https://liberty.top',
    'access_token': 'dtpf8uupsbhumevz4pz2jebrqzqmv62o',
    'merchant_id': 'd5c17c6c-dc40-428a-80e5-2ca01af99f68',
    'currency': 'rub',
    'payment_detail_type': 'card'
}

# Конфигурация H2H API (РАБОТАЕТ!)
H2H_CONFIG = {
    'base_url': 'https://api.liberty.top',
    'access_token': 'dtpf8uupsbhumevz4pz2jebrqzqmv62o',
    'merchant_id': 'd5c17c6c-dc40-428a-80e5-2ca01af99f68',
    'currency': 'rub',
    'payment_detail_type': 'card'
}

# Конфигурация PayzTeam API (старый сервис, закомментирован)
PAYZTEAM_CONFIG = {
    'merchant_id': '747',
    'api_key': 'f046a50c7e398bc48124437b612ac7ab',
    'secret_key': 'aa7c2689-98f2-428f-9c03-93e3835c3b1d',
    'payment_method': 'abh_c2c'
}


def get_requisite_service():
    """Возвращает название активного сервиса"""
    return ACTIVE_REQUISITE_SERVICE


def get_merchant_config():
    """Возвращает конфигурацию Merchant API"""
    return MERCHANT_CONFIG.copy()


def get_h2h_config():
    """Возвращает конфигурацию H2H API"""
    return H2H_CONFIG.copy()


def get_payzteam_config():
    """Возвращает конфигурацию PayzTeam API"""
    return PAYZTEAM_CONFIG.copy()
