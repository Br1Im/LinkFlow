from mulenpay import MulenPayClient

api_key = '2iMSrdpFuTgrWiHjJdHR8bEMBCS46VId8YLzhY4wbf38fc08'
secret_key = 'b48d74485fcf7b4a2cade546bdebcaf3692945ffeeb7ff98729a758f6322684c'

mp = MulenPayClient(api_key=api_key, secret_key=secret_key)
print("OK - MulenPayClient created successfully")
