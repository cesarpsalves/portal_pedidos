# app/routes/solicitacoes.py (versão ajustada com proteção de acesso completa)

import os
import io
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    session, flash, send_from_directory, abort
)
from sqlalchemy.orm import joinedload

from app.utils.auth import login_required, ativo_required, perfil_requerido
from app.utils.validators import validar_cpf, encontrar_melhor_correspondencia

from app.extensions import db
from app.models.solicitacoes import Solicitacao, ItemSolicitacao
from app.models.unidades import Unidade
from app.models.empresas import Empresa

import pandas as pd

solicitacoes_bp = Blueprint("solicitacoes", __name__)

TERMOS_OFICIAIS_PRODUTOS = [
    "AIRFRYER FRITADEIRA ELÉTRICA",
    "ASPIRADOR ROBÔ",
    "CARRO DE MÃO PNEUMÁTICO ATÉ 350KG",
    "CHURRASQUEIRA ELÉTRICA PORTÁTIL TIPO GRILL",
    "IMPRESSORA DE ETIQUETA ELGIN",
    "IMPRESSORA DE ETIQUETA ZEBRA",
    "KIT JAQUETA PUFFER COM TOCA E LUVA",
    "LAVADORA DE ALTA PRESSÃO BOSCH",
    "MAQUINA TROCA DE ÁGUA ARREFECIMENTO",
    "NOBREAK",
    "PURIFICADOR DE ÁGUA",
    "SEGUNDA PELE TÉRMICA FLANELADO",
    "TABLET LENOVO TAB M9",
    "TABLET SAMSUNG TAB A9"
]


@solicitacoes_bp.route("/solicitacao/nova", methods=["GET", "POST"])
@login_required
@ativo_required
@perfil_requerido("solicitante", "administrador")
def nova_solicitacao():
    if request.method == "POST":
        usuario_id = session.get("usuario_id")
        empresa_id = request.form.get("empresa_solicitante_id")
        finalidade = (request.form.get("finalidade") or "").strip().upper()
        centro_custo = request.form.get("centro_custo")
        unidade_id = request.form.get("unidade_id")
        tipo_recebimento = (request.form.get("recebimento") or "").upper()

        # Campos de Retirada (caso RETIRADA)
        nome_retirada = (
            (request.form.get("nome_retirada") or "").strip().upper()
            if tipo_recebimento == "RETIRADA"
            else None
        )
        cpf_retirada = (
            request.form.get("cpf_retirada") if tipo_recebimento == "RETIRADA" else None
        )

        # 1) Validação de CPF no backend
        if tipo_recebimento == "RETIRADA":
            if not cpf_retirada or not validar_cpf(cpf_retirada):
                flash("CPF de quem irá retirar é inválido. Verifique e tente novamente.", "danger")
                # Recarrega o formulário com os dados básicos e a lista de termos para datalist
                empresas = Empresa.query.order_by(Empresa.nome).all()
                unidades = Unidade.query.order_by(Unidade.nome).all()
                hoje = datetime.utcnow().date().strftime("%Y-%m-%d")
                return render_template(
                    "solicitacoes/nova.html",
                    empresas=empresas,
                    unidades=unidades,
                    hoje=hoje,
                    dias_max=30,
                    termos_produto=TERMOS_OFICIAIS_PRODUTOS,
                )

        # 2) Converte string de data para objeto datetime (se preenchido)
        prazo_limite_str = request.form.get("prazo_limite")
        prazo_limite = (
            datetime.strptime(prazo_limite_str, "%Y-%m-%d")
            if prazo_limite_str
            else None
        )

        # 3) Cria a nova solicitação
        nova_solic = Solicitacao(
            usuario_id=usuario_id,
            empresa_solicitante_id=empresa_id,
            finalidade=finalidade,
            centro_custo=centro_custo,
            unidade_id=unidade_id,
            tipo_recebimento=tipo_recebimento,
            nome_retirada=nome_retirada,
            cpf_retirada=cpf_retirada,
            prazo_limite=prazo_limite,
            status="pendente",
        )
        db.session.add(nova_solic)
        db.session.flush()  # para obter nova_solic.id antes de adicionar itens

        # 4) Itens da solicitação + fuzzy matching no nome_produto
        nomes = request.form.getlist("nome_produto")
        tecnicos = request.form.getlist("nome_tecnico")
        quantidades = request.form.getlist("quantidade")
        voltagens = request.form.getlist("voltagem")
        especificacoes = request.form.getlist("especificacoes")
        links = request.form.getlist("link")

        for i in range(len(nomes)):
            nome_digitado = (nomes[i] or "").strip().upper()
            if not nome_digitado:
                continue  # pula itens vazios

            # Tenta encontrar correspondência em TERMOS_OFICIAIS_PRODUTOS
            correspondencia = encontrar_melhor_correspondencia(
                nome_digitado,
                TERMOS_OFICIAIS_PRODUTOS,
                limite_similaridade=80
            )
            if correspondencia:
                nome_produto_final = correspondencia
            else:
                nome_produto_final = nome_digitado

            item = ItemSolicitacao(
                solicitacao_id=nova_solic.id,
                nome_produto=nome_produto_final,
                nome_tecnico=(tecnicos[i] or "").strip().upper() if i < len(tecnicos) else "",
                quantidade=(
                    int(quantidades[i])
                    if i < len(quantidades) and quantidades[i].isdigit()
                    else 1
                ),
                voltagem=voltagens[i] if i < len(voltagens) else "",
                especificacoes=(especificacoes[i] or "").strip().upper() if i < len(especificacoes) else "",
                link=(links[i] or "").strip() if i < len(links) else "",
            )
            db.session.add(item)

        db.session.commit()
        flash("Solicitação criada com sucesso!", "success")
        return redirect(url_for("main.dashboard"))

    # Se GET, renderiza o formulário normalmente
    empresas = Empresa.query.order_by(Empresa.nome).all()
    unidades = Unidade.query.order_by(Unidade.nome).all()
    hoje = datetime.utcnow().date().strftime("%Y-%m-%d")
    dias_max = 30

    return render_template(
        "solicitacoes/nova.html",
        empresas=empresas,
        unidades=unidades,
        hoje=hoje,
        dias_max=dias_max,
        termos_produto=TERMOS_OFICIAIS_PRODUTOS,
    )


@solicitacoes_bp.route("/solicitacoes")
@login_required
@ativo_required
def lista_solicitacoes():
    usuario_id = session.get("usuario_id")
    tipo_usuario = session.get("usuario_tipo")

    if tipo_usuario == "administrador":
        solicitacoes = (
            Solicitacao.query
            .options(joinedload(Solicitacao.itens))
            .order_by(Solicitacao.criado_em.desc())
            .all()
        )
    else:
        solicitacoes = (
            Solicitacao.query
            .options(joinedload(Solicitacao.itens))
            .filter_by(usuario_id=usuario_id)
            .order_by(Solicitacao.criado_em.desc())
            .all()
        )

    return render_template("solicitacoes/lista.html", solicitacoes=solicitacoes)


@solicitacoes_bp.route("/solicitacao/<int:id>")
@login_required
@ativo_required
def ver_solicitacao(id):
    solicitacao = Solicitacao.query.get_or_404(id)
    tipo_usuario = session.get("usuario_tipo")

    # Se não é admin e não for dono da solicitação, nega acesso
    if tipo_usuario != "administrador" and solicitacao.usuario_id != session.get("usuario_id"):
        flash("Acesso negado.", "danger")
        return redirect(url_for("solicitacoes.lista_solicitacoes"))

    itens = ItemSolicitacao.query.filter_by(solicitacao_id=solicitacao.id).all()
    anexos = solicitacao.anexos

    return render_template(
        "solicitacoes/ver.html",
        solicitacao=solicitacao,
        itens=itens,
        anexos=anexos
    )


@solicitacoes_bp.route("/solicitacao/download_template/<tipo>")
@login_required
@ativo_required
@perfil_requerido("solicitante", "administrador")
def download_template(tipo):
    """
    Retorna o arquivo modelo .xlsx para o usuário baixar.
    `tipo` deve ser 'retirada' ou 'entrega'.
    """
    pasta_templates = os.path.join(os.path.dirname(__file__), "..", "static", "templates_excel")
    if tipo == "retirada":
        nome_arquivo = "Template_Retirada.xlsx"
    elif tipo == "entrega":
        nome_arquivo = "Template_Entrega.xlsx"
    else:
        abort(404)

    caminho = os.path.join(pasta_templates, nome_arquivo)
    if not os.path.exists(caminho):
        abort(404)

    return send_from_directory(pasta_templates, nome_arquivo, as_attachment=True)


@solicitacoes_bp.route("/solicitacao/importar", methods=["GET", "POST"])
@login_required
@ativo_required
@perfil_requerido("solicitante", "administrador")
def importar_solicitacao():
    """
    Rota para importar solicitação via planilha Excel.
    Se for GET: apenas mostra o formulário (importar.html).
    Se for POST: processa o arquivo upload, valida cada linha e
    insere no banco se estiver tudo OK, ou retorna erros.
    """
    if request.method == "POST":
        tipo_importacao = request.form.get("tipo_importacao")  # 'retirada' ou 'entrega'
        arquivo = request.files.get("arquivo_excel")
        if not arquivo:
            flash("Nenhum arquivo enviado.", "danger")
            return redirect(url_for("solicitacoes.importar_solicitacao"))

        # Verifica extensão
        nome_arquivo = arquivo.filename.lower()
        if not nome_arquivo.endswith(".xlsx"):
            flash("Envie um arquivo .xlsx válido.", "danger")
            return redirect(url_for("solicitacoes.importar_solicitacao"))

        # Lê o conteúdo do Excel via pandas
        try:
            data = arquivo.read()
            excel_io = io.BytesIO(data)
            df = pd.read_excel(excel_io, sheet_name="Dados", dtype=str)
        except Exception as e:
            flash(f"Falha ao ler o Excel: {e}", "danger")
            return redirect(url_for("solicitacoes.importar_solicitacao"))

        erros = []         # lista de { linha: X, mensagem: "..." }
        linhas_validas = []  # vai acumular dicionários com dados válidos

        # Itera linha a linha (df.index é zero-based; linha real no Excel = idx+3)
        for idx, row in df.iterrows():
            numero_linha_excel = idx + 3  # 1=título, 2=cabeçalho, 3=primeira linha de dados

            # 1) Lê os campos comuns
            empresa_txt = (row.get("Empresa") or "").strip()
            finalidade_txt = (row.get("Finalidade") or "").strip()
            centro_custo_txt = (row.get("Centro de Custo") or "").strip()
            unidade_txt = (row.get("Unidade") or "").strip()

            # 2) Se for retirada, pega também nome_retirada e cpf_retirada
            nome_retirada_txt = None
            cpf_retirada_txt = None
            if tipo_importacao == "retirada":
                nome_retirada_txt = (row.get("Nome de quem irá retirar") or "").strip().upper()
                cpf_retirada_txt = (row.get("CPF de quem irá retirar") or "").strip()

            # 3) Prazo Limite (comum aos dois modelos)
            prazo_limite_txt = (row.get("Prazo Limite") or "").strip()

            # 4) Campos de item
            nome_produto_txt = (row.get("Nome do Produto") or "").strip().upper()
            nome_tecnico_txt = (row.get("Nome Técnico") or "").strip().upper()
            quantidade_txt = (row.get("Qtd") or "").strip()
            voltagem_txt = (row.get("Voltagem") or "").strip().upper()
            especificacoes_txt = (row.get("Especificações") or "").strip().upper()
            link_txt = (row.get("Link") or "").strip()

            # 5) Validações básicas

            # a) Empresa existe?
            empresa_obj = None
            if not empresa_txt:
                erros.append({ "linha": numero_linha_excel, "mensagem": "Coluna 'Empresa' vazia." })
                continue
            else:
                try:
                    if empresa_txt.isdigit():
                        empresa_obj = Empresa.query.get(int(empresa_txt))
                    else:
                        empresa_obj = Empresa.query.filter_by(nome=empresa_txt).first()
                except:
                    empresa_obj = None

                if not empresa_obj:
                    erros.append({
                        "linha": numero_linha_excel,
                        "mensagem": f"Empresa '{empresa_txt}' não encontrada."
                    })
                    continue

            # b) Finalidade obrigatória?
            if not finalidade_txt:
                erros.append({ "linha": numero_linha_excel, "mensagem": "Coluna 'Finalidade' vazia." })
                continue

            # c) Centro de Custo obrigatório?
            if not centro_custo_txt:
                erros.append({ "linha": numero_linha_excel, "mensagem": "Coluna 'Centro de Custo' vazia." })
                continue

            # d) Unidade existe?
            unidade_obj = None
            if not unidade_txt:
                erros.append({ "linha": numero_linha_excel, "mensagem": "Coluna 'Unidade' vazia." })
                continue
            else:
                try:
                    if unidade_txt.isdigit():
                        unidade_obj = Unidade.query.get(int(unidade_txt))
                    else:
                        unidade_obj = Unidade.query.filter_by(nome=unidade_txt).first()
                except:
                    unidade_obj = None

                if not unidade_obj:
                    erros.append({
                        "linha": numero_linha_excel,
                        "mensagem": f"Unidade '{unidade_txt}' não encontrada."
                    })
                    continue

            # e) Se for retirada: nome_retirada e cpf_retirada são obrigatórios
            if tipo_importacao == "retirada":
                if not nome_retirada_txt:
                    erros.append({
                        "linha": numero_linha_excel,
                        "mensagem": "Campo 'Nome de quem irá retirar' vazio (Retirada)."
                    })
                    continue
                if not cpf_retirada_txt:
                    erros.append({
                        "linha": numero_linha_excel,
                        "mensagem": "Campo 'CPF de quem irá retirar' vazio (Retirada)."
                    })
                    continue
                # Valida CPF
                if not validar_cpf(cpf_retirada_txt):
                    erros.append({
                        "linha": numero_linha_excel,
                        "mensagem": f"CPF inválido: '{cpf_retirada_txt}'."
                    })
                    continue

            # f) Prazo Limite (date no formato AAAA-MM-DD)
            try:
                if not prazo_limite_txt:
                    raise ValueError("Prazo Limite vazio.")
                prazo_obj = datetime.strptime(prazo_limite_txt, "%Y-%m-%d")
            except Exception:
                erros.append({
                    "linha": numero_linha_excel,
                    "mensagem": f"Data inválida em 'Prazo Limite': '{prazo_limite_txt}'."
                })
                continue

            # g) Nome do Produto obrigatório?
            if not nome_produto_txt:
                erros.append({
                    "linha": numero_linha_excel,
                    "mensagem": "Campo 'Nome do Produto' vazio."
                })
                continue

            # h) Tenta padronizar nome_produto via fuzzy
            correspondencia = encontrar_melhor_correspondencia(
                nome_produto_txt,
                TERMOS_OFICIAIS_PRODUTOS,
                limite_similaridade=80
            )
            if correspondencia:
                nome_produto_final = correspondencia
            else:
                nome_produto_final = nome_produto_txt

            # i) Quantidade deve ser inteiro ≥ 1
            qtd_int = 1
            if quantidade_txt:
                if quantidade_txt.isdigit() and int(quantidade_txt) >= 1:
                    qtd_int = int(quantidade_txt)
                else:
                    erros.append({
                        "linha": numero_linha_excel,
                        "mensagem": f"Quantidade inválida: '{quantidade_txt}'."
                    })
                    continue

            # j) Voltagem, se houver, só pode ser “110V” ou “220V”
            if voltagem_txt and voltagem_txt not in ["110V", "220V"]:
                erros.append({
                    "linha": numero_linha_excel,
                    "mensagem": f"Voltagem inválida: '{voltagem_txt}' (use 110V ou 220V)."
                })
                continue

            # 6) Se chegou aqui, a linha está OK. Montamos um dicionário de dados válidos
            linhas_validas.append({
                "empresa_id": empresa_obj.id,
                "finalidade": finalidade_txt.upper(),
                "centro_custo": centro_custo_txt,
                "unidade_id": unidade_obj.id,
                "tipo_recebimento": tipo_importacao.upper(),
                "nome_retirada": nome_retirada_txt if tipo_importacao == "retirada" else None,
                "cpf_retirada": cpf_retirada_txt if tipo_importacao == "retirada" else None,
                "prazo_limite": prazo_obj,
                "nome_produto": nome_produto_final,
                "nome_tecnico": nome_tecnico_txt,
                "quantidade": qtd_int,
                "voltagem": voltagem_txt,
                "especificacoes": especificacoes_txt,
                "link": link_txt
            })

        # 2. Se houver erros, interrompe e mostra relatório
        if erros:
            return render_template("solicitacoes/importar.html", errors=erros)

        # 3. Se nenhuma linha falhou, insere no banco:
        #    Todas as linhas_validas pertencem à MESMA solicitação, então criamos uma só Solicitacao
        primeira = linhas_validas[0]
        nova_solic = Solicitacao(
            usuario_id = session.get("usuario_id"),
            empresa_solicitante_id = primeira["empresa_id"],
            finalidade = primeira["finalidade"],
            centro_custo = primeira["centro_custo"],
            unidade_id = primeira["unidade_id"],
            tipo_recebimento = primeira["tipo_recebimento"],
            nome_retirada = primeira.get("nome_retirada"),
            cpf_retirada = primeira.get("cpf_retirada"),
            prazo_limite = primeira["prazo_limite"],
            status = "pendente"
        )
        db.session.add(nova_solic)
        db.session.flush()  # para obter nova_solic.id

        # Agora percorre todas as linhas válidas e cria um ItemSolicitacao para cada
        total_itens = 0
        for reg in linhas_validas:
            item = ItemSolicitacao(
                solicitacao_id = nova_solic.id,
                nome_produto = reg["nome_produto"],
                nome_tecnico = reg["nome_tecnico"],
                quantidade = reg["quantidade"],
                voltagem = reg["voltagem"],
                especificacoes = reg["especificacoes"],
                link = reg["link"]
            )
            db.session.add(item)
            total_itens += 1

        db.session.commit()
        flash(f"Importação concluída com sucesso: 1 solicitação e {total_itens} item(ns) gravado(s).", "success")
        return redirect(url_for("main.dashboard"))

    # Se for GET, renderiza o formulário de upload
    return render_template("solicitacoes/importar.html")