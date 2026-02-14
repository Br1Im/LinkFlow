#!/usr/bin/env python3
"""
Конфигурация для сервисов получения реквизитов
"""

# Выбор активного сервиса: 'auto', 'h2h' или 'payzteam'
# 'auto' - Автоматический выбор (сначала H2H, потом PayzTeam если не получилось)
# 'h2h' - H2H API (Liberty) - только этот источник
# 'payzteam' - PayzTeam API - только этот источник
ACTIVE_REQUISITE_SERVICE = 'auto'

# Конфигурация H2H API (Liberty)
H2H_CONFIG = {
    'base_url': 'https://api.liberty.top',
    'access_token': 'dtpf8uupsbhumevz4pz2jebrqzqmv62o',
    'merchant_id': 'd5c17c6c-dc40-428a-80e5-2ca01af99f68',
    'currency': 'rub',
    'payment_detail_type': 'card'
}

# Конфигурация PayzTeam API (старый сервис)
PAYZTEAM_CONFIG = {
    'merchant_id': '747',
    'api_key': 'f046a50c7e398bc48124437b612ac7ab',
    'secret_key': 'aa7c2689-98f2-428f-9c03-93e3835c3b1d',
    'payment_method': 'abh_c2c'
}


def get_requisite_service():
    """Возвращает название активного сервиса"""
    return ACTIVE_REQUISITE_SERVICE


def set_requisite_service(service: str):
    """Устанавливает активный сервис"""
    global ACTIVE_REQUISITE_SERVICE
    if service in ['auto', 'h2h', 'payzteam']:
        ACTIVE_REQUISITE_SERVICE = service
    else:
        raise ValueError(f"Unknown service: {service}. Use 'auto', 'h2h' or 'payzteam'")


def get_merchant_config():
    """Возвращает конфигурацию Merchant API"""
    return MERCHANT_CONFIG.copy()


def get_h2h_config():
    """Возвращает конфигурацию H2H API"""
    return H2H_CONFIG.copy()


def get_payzteam_config():
    """Возвращает конфигурацию PayzTeam API"""
    return PAYZTEAM_CONFIG.copy()
