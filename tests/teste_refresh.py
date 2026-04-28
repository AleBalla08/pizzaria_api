import requests

header = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc3OTgzMzM4fQ.dYiya5tZACdIjL9AvfOarjXjsMZJPyJNrWB-X1RF6to"
}

requisicao = requests.get("http://127.0.0.1:8000/auth/refresh", headers=header)
print(requisicao)
# print(requisicao.json())