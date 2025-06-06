# app/utils/validators.py

import re
from rapidfuzz import process

def limpar_cpf(cpf: str) -> str:
    """Remove tudo que não for dígito."""
    return re.sub(r'[^0-9]', '', cpf or '')

def validar_cpf(cpf: str) -> bool:
    """
    Retorna True se o CPF for válido, False caso contrário.
    Baseado no algoritmo oficial de cálculo dos dígitos verificadores.
    """
    cpf_limpo = limpar_cpf(cpf)

    # Deve ter exatamente 11 dígitos
    if len(cpf_limpo) != 11:
        return False

    # Não aceitar sequências iguais (ex: '00000000000', '11111111111', etc.)
    if cpf_limpo == cpf_limpo[0] * 11:
        return False

    # Converter para lista de inteiros
    nums = list(map(int, cpf_limpo))

    # Cálculo do primeiro dígito verificador (dígito 10)
    soma1 = sum((10 - i) * nums[i] for i in range(9))
    resto1 = soma1 % 11
    dig1 = 0 if resto1 < 2 else 11 - resto1

    # Cálculo do segundo dígito verificador (dígito 11)
    soma2 = sum((11 - i) * nums[i] for i in range(10))
    resto2 = soma2 % 11
    dig2 = 0 if resto2 < 2 else 11 - resto2

    # Verifica se os dígitos calculados conferem com os dois últimos dígitos
    return nums[9] == dig1 and nums[10] == dig2

def encontrar_melhor_correspondencia(texto_usuario: str, termos_oficiais: list, limite_similaridade: int = 80) -> str:
    """
    Usa RapidFuzz para encontrar, entre os termos_oficiais, a string mais similar a texto_usuario.
    Se não encontrar pontuação >= limite_similaridade, retorna None.
    """
    if not texto_usuario:
        return None

    # Convertendo tudo para maiúsculo para comparar de forma uniforme
    resultado = process.extractOne(
        texto_usuario.upper(),
        [termo.upper() for termo in termos_oficiais],
        score_cutoff=limite_similaridade
    )
    if resultado:
        termo_achado, pontuacao, indice = resultado
        # Retorna o termo oficial original (mantendo a forma de termos_oficiais)
        return termos_oficiais[indice]
    return None
