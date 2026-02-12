#!/usr/bin/env python3
"""Test MulenPay API directly"""
import asyncio
from mulenpay import MulenPayClient, CreatePayment

async def test():
    api_key = '2iMSrdpFuTgrWiHjJdHR8bEMBCS46VId8YLzhY4wbf38fc08'
    secret_key = 'b48d74485fcf7b4a2cade546bdebcaf3692945ffeeb7ff98729a758f6322684c'
    
    client = MulenPayClient(api_key=api_key, secret_key=secret_key)
    
    # Debug: print headers
    print("Headers being sent:")
    print(client._client.headers)
    print()
    
    payment_data = CreatePayment(
        currency="RUB",
        amount="3500",
        uuid="test_direct_3500",
        shopId=280,  # Using the same shopId as Nutrition bot
        description="Test payment 3500",
        language="ru"
    )
    
    try:
        result = await client.create_payment(payment_data)
        print("SUCCESS:")
        print(result)
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test())
