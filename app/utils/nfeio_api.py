# app/utils/nfeio_api.py

import requests

API_KEY = "dNe9u46dnbZKsTklekIggIxByvBF9v8qxsm5gCTGSuWwp0SkyXhdnpDgYBtOBKUZTBx"
API_URL = "https://api.nfe.io/v1/companies/sub_6849d1b6747b621748b86bc4/nfes"

def consultar_nfe_nfeio(chave_acesso: str) -> dict:
    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json"
    }

    params = {
        "accessKey": chave_acesso
    }

    response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code == 200:
        resultado = response.json()
        if resultado.get("data"):
            return resultado["data"][0]
        raise ValueError("Nota não encontrada.")
    else:
        raise ValueError(f"Erro {response.status_code}: {response.text}")
