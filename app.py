
from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import io
from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

app = Flask(__name__)


def buscar_despesas_filtradas(cursor):
    """Monta e executa a consulta de despesas usando os filtros da URL (?pesquisa, ?categoria, ?data_inicio, ?data_fim, ?ordenar)."""

    pesquisa = request.args.get("pesquisa", "")
    categoria = request.args.get("categoria", "")
    data_inicio = request.args.get("data_inicio", "")
    data_fim = request.args.get("data_fim", "")
    ordenar = request.args.get("ordenar", "data_desc")

    sql = "SELECT * FROM despesas WHERE 1=1"
    parametros = []

    if pesquisa:
        sql += " AND nome LIKE ?"
        parametros.append('%' + pesquisa + '%')

    if categoria:
        sql += " AND categoria = ?"
        parametros.append(categoria)

    if data_inicio:
        sql += " AND data >= ?"
        parametros.append(data_inicio)

    if data_fim:
        sql += " AND data <= ?"
        parametros.append(data_fim)

    # Whitelist de ordenação: evita montar ORDER BY com valor vindo direto da URL
    colunas_ordenacao = {
        "data_desc": "data DESC",
        "data_asc": "data ASC",
        "valor_desc": "valor DESC",
        "valor_asc": "valor ASC",
        "nome_asc": "nome ASC",
        "nome_desc": "nome DESC",
    }

    sql += " ORDER BY " + colunas_ordenacao.get(ordenar, "data DESC")

    cursor.execute(sql, parametros)
    return cursor.fetchall()


@app.route("/")
def home():

    conexao = sqlite3.connect("despesas.db")
    cursor = conexao.cursor()

    despesas = buscar_despesas_filtradas(cursor)
    query_string = request.query_string.decode()

    pesquisa = request.args.get("pesquisa", "")
    categoria = request.args.get("categoria", "")
    data_inicio = request.args.get("data_inicio", "")
    data_fim = request.args.get("data_fim", "")
    ordenar = request.args.get("ordenar", "data_desc")

    # Total gasto
    cursor.execute("SELECT SUM(valor) FROM despesas")
    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    # Quantidade de despesas
    cursor.execute("SELECT COUNT(*) FROM despesas")
    quantidade = cursor.fetchone()[0]

    # Média das despesas
    if quantidade > 0:
        media = total / quantidade
    else:
        media = 0

    # Maior despesa
    cursor.execute("SELECT MAX(valor) FROM despesas")
    maior_despesa = cursor.fetchone()[0]

    if maior_despesa is None:
        maior_despesa = 0

    # Menor despesa
    cursor.execute("SELECT MIN(valor) FROM despesas")
    menor_despesa = cursor.fetchone()[0]

    if menor_despesa is None:
        menor_despesa = 0

    # Gasto do mês atual
    cursor.execute("""
        SELECT SUM(valor) FROM despesas
        WHERE strftime('%Y-%m', data) = strftime('%Y-%m', 'now')
    """)
    gasto_mes = cursor.fetchone()[0]

    if gasto_mes is None:
        gasto_mes = 0

    # Gasto do ano atual
    cursor.execute("""
        SELECT SUM(valor) FROM despesas
        WHERE strftime('%Y', data) = strftime('%Y', 'now')
    """)
    gasto_ano = cursor.fetchone()[0]

    if gasto_ano is None:
        gasto_ano = 0

    # Gráfico: despesas por categoria
    cursor.execute("SELECT categoria, SUM(valor) FROM despesas GROUP BY categoria")
    dados_categoria = cursor.fetchall()

    categoria_labels = [linha[0] for linha in dados_categoria]
    categoria_valores = [linha[1] for linha in dados_categoria]

    # Gráfico: despesas por mês
    cursor.execute("""
        SELECT strftime('%Y-%m', data), SUM(valor)
        FROM despesas
        GROUP BY strftime('%Y-%m', data)
        ORDER BY strftime('%Y-%m', data)
    """)
    dados_mensal = cursor.fetchall()

    mes_labels = [linha[0] for linha in dados_mensal]
    mes_valores = [linha[1] for linha in dados_mensal]

    # Gráfico: evolução acumulada dos gastos
    cursor.execute("SELECT data, valor FROM despesas ORDER BY data")
    dados_evolucao = cursor.fetchall()

    evolucao_labels = []
    evolucao_valores = []
    acumulado = 0

    for data_despesa, valor_despesa in dados_evolucao:
        acumulado += valor_despesa
        evolucao_labels.append(data_despesa)
        evolucao_valores.append(acumulado)

    conexao.close()

    return render_template(
        "index.html",
        despesas=despesas,
        total=total,
        quantidade=quantidade,
        media=media,
        maior_despesa=maior_despesa,
        menor_despesa=menor_despesa,
        gasto_mes=gasto_mes,
        gasto_ano=gasto_ano,
        pesquisa=pesquisa,
        categoria=categoria,
        data_inicio=data_inicio,
        data_fim=data_fim,
        ordenar=ordenar,
        categoria_labels=categoria_labels,
        categoria_valores=categoria_valores,
        mes_labels=mes_labels,
        mes_valores=mes_valores,
        evolucao_labels=evolucao_labels,
        evolucao_valores=evolucao_valores,
        query_string=query_string
    )


@app.route("/exportar/excel")
def exportar_excel():

    conexao = sqlite3.connect("despesas.db")
    cursor = conexao.cursor()

    despesas = buscar_despesas_filtradas(cursor)
    conexao.close()

    planilha = Workbook()
    aba = planilha.active
    aba.title = "Despesas"

    cabecalho = ["ID", "Nome", "Descrição", "Categoria", "Valor (R$)", "Data"]
    aba.append(cabecalho)

    for celula in aba[1]:
        celula.font = Font(bold=True)

    for despesa in despesas:
        aba.append(list(despesa))

    for coluna in aba.columns:
        maior_texto = max(len(str(celula.value)) for celula in coluna)
        aba.column_dimensions[coluna[0].column_letter].width = maior_texto + 4

    buffer = io.BytesIO()
    planilha.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="despesas.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/exportar/pdf")
def exportar_pdf():

    conexao = sqlite3.connect("despesas.db")
    cursor = conexao.cursor()

    despesas = buscar_despesas_filtradas(cursor)
    conexao.close()

    buffer = io.BytesIO()
    documento = SimpleDocTemplate(buffer, pagesize=A4)
    estilos = getSampleStyleSheet()

    dados_tabela = [["ID", "Nome", "Descrição", "Categoria", "Valor (R$)", "Data"]]

    for despesa in despesas:
        linha = list(despesa)
        linha[4] = "R$ {:.2f}".format(linha[4])
        dados_tabela.append(linha)

    tabela = Table(dados_tabela, repeatRows=1)

    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#198754")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fff5")]),
    ]))

    elementos = [
        Paragraph("Relatório de Despesas", estilos["Title"]),
        Spacer(1, 12),
        tabela
    ]

    documento.build(elementos)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="despesas.pdf",
        mimetype="application/pdf"
    )


@app.route("/salvar", methods=["POST"])
def salvar():

    nome = request.form.get("nome")
    descricao = request.form.get("descricao")
    categoria = request.form.get("categoria")
    valor = request.form.get("valor")

    conexao = sqlite3.connect("despesas.db")
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO despesas (nome, descricao, categoria, valor, data)
        VALUES (?, ?, ?, ?, date('now'))
        """,
        (nome, descricao, categoria, valor)
    )

    conexao.commit()
    conexao.close()

    return redirect("/?sucesso=cadastrado")


@app.route("/excluir/<int:id>")
def excluir(id):

    conexao = sqlite3.connect("despesas.db")
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM despesas WHERE id = ?", (id,))

    conexao.commit()
    conexao.close()

    return redirect("/?sucesso=excluido")


@app.route("/editar/<int:id>")
def editar(id):

    conexao = sqlite3.connect("despesas.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM despesas WHERE id = ?", (id,))
    despesa = cursor.fetchone()

    conexao.close()

    return render_template("editar.html", despesa=despesa)


@app.route("/atualizar", methods=["POST"])
def atualizar():

    id = request.form.get("id")
    nome = request.form.get("nome")
    descricao = request.form.get("descricao")
    categoria = request.form.get("categoria")
    valor = request.form.get("valor")

    conexao = sqlite3.connect("despesas.db")
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE despesas
        SET nome = ?, descricao = ?, categoria = ?, valor = ?
        WHERE id = ?
        """,
        (nome, descricao, categoria, valor, id)
    )

    conexao.commit()
    conexao.close()

    return redirect("/?sucesso=atualizado")


if __name__ == "__main__":
    app.run(debug=True)