# app/utils/nfe_utils.py

import os
import re
import uuid
import logging
from PyPDF2 import PdfReader
import pdfplumber

TEMP_TXT_DIR = "/opt/portal_pedidos/uploads/notas_temp"
os.makedirs(TEMP_TXT_DIR, exist_ok=True)

def salvar_texto_temporario(texto: str) -> str:
    nome_arquivo = f"{uuid.uuid4().hex}.txt"
    caminho = os.path.join(TEMP_TXT_DIR, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    return caminho

def extrair_texto_pdf_pypdf2(caminho_pdf: str) -> str:
    reader = PdfReader(caminho_pdf)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def extrair_texto_pdf_plumber(caminho_pdf: str) -> str:
    with pdfplumber.open(caminho_pdf) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def extrair_chave_acesso(texto: str) -> str | None:
    # Remove todos os espaços, depois insere espaços a cada 4 dígitos para visualização posterior
    numeros = re.findall(r"\d{44,}", texto.replace(" ", ""))
    for numero in numeros:
        if len(numero) > 44:
            # tenta identificar uma sequência de 44 dígitos dentro da string maior
            for i in range(len(numero) - 43):
                sub = numero[i:i+44]
                if sub.isdigit():
                    return " ".join([sub[i:i+4] for i in range(0, 44, 4)])
        elif len(numero) == 44:
            return " ".join([numero[i:i+4] for i in range(0, 44, 4)])
    return None

def extrair_dados_pdf(caminho_pdf: str) -> dict:
    dados = {
        "chave_acesso": None,
    }

    texto = ""
    try:
        texto = extrair_texto_pdf_pypdf2(caminho_pdf)
        if not texto.strip():
            raise ValueError("Texto vazio via PyPDF2.")
    except Exception as e:
        logging.warning(f"Fallback para pdfplumber: {e}")
        try:
            texto = extrair_texto_pdf_plumber(caminho_pdf)
        except Exception as ee:
            logging.error(f"[EXTRAÇÃO FALHOU] {ee}")
            return dados

    salvar_texto_temporario(texto)

    chave = extrair_chave_acesso(texto)
    if chave:
        dados["chave_acesso"] = chave

    return dados
