import requests
from bs4 import BeautifulSoup
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from textwrap import wrap

def salvar_em_pdf(nome_arquivo, conteudo, titulo, data):
    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    width, height = A4
    margem_esq = 2 * cm
    margem_topo = height - 2 * cm
    largura_texto = width - 4 * cm

    y = margem_topo

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, titulo)
    y -= 20

    # Data
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y, f"Data da consulta: {data}")
    y -= 30

    # Conteúdo
    c.setFont("Helvetica", 11)
    for linha in conteudo.split('\n'):
        if not linha.strip():
            y -= 10
            continue
        linhas_quebradas = wrap(linha, width=100)
        for l in linhas_quebradas:
            c.drawString(margem_esq, y, l)
            y -= 15
            if y < 2 * cm:
                c.showPage()
                y = margem_topo
                c.setFont("Helvetica", 11)

    c.save()

# Configurações
url = "https://sei.cade.gov.br/sei/publicacoes/controlador_publicacoes.php?acao=publicacao_pesquisar&id_orgao_publicacao=0"
data_hoje = datetime.today()
data_hoje_formatada = data_hoje.strftime("%d/%m/%Y")  # e.g., "10/04/2025"
data_arquivo = data_hoje.strftime("%d-%m-%Y")          # e.g., "10-04-2025"
titulo_pdf = "Relatório de Publicações do CADE"

tipos_documento = {
    "319": "Despacho SG Arquivamento IA",
    "321": "Despacho SG Encerramento PA - Arquivamento",
    "323": "Despacho SG Encerramento PA - Condenação",
    "324": "Despacho SG Instauração IA",
    "320": "Despacho SG Instauração PA"
}

resultado_texto = ""

for tipo_valor, tipo_nome in tipos_documento.items():
    # Updated payload with explicit date range for today
    payload = {
        "acao": "publicacao_pesquisar",
        "selSerie": tipo_valor,
        "optPeriodo": "personalizado",  # Switch to "custom" period
        "txtDataInicio": data_hoje_formatada,  # Start date: today
        "txtDataFim": data_hoje_formatada,    # End date: today
        "hdnInfraTipoPagina": "20",
        "hdnInfraUrl": "/sei/publicacoes/controlador_publicacoes.php"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Check for HTTP errors
        response.encoding = 'ISO-8859-1'
        soup = BeautifulSoup(response.text, 'html.parser')

        publicacoes = soup.find_all('tr', class_='infraTrClara') + soup.find_all('tr', class_='infraTrEscura')

        resultado_texto += f"📄 Tipo de Documento: {tipo_nome}\n"

        if not publicacoes:
            resultado_texto += "• Nenhuma publicação encontrada.\n\n"
        else:
            for pub in publicacoes:
                dados = [td.get_text(strip=True) for td in pub.find_all('td')]
                # Optional: Filter by date in case the server doesn't
                if len(dados) > 0 and dados[0] == data_hoje_formatada:  # Assuming first column is date
                    resultado_texto += "• " + " | ".join(dados) + "\n"
            resultado_texto += "\n"

    except requests.RequestException as e:
        resultado_texto += f"Erro ao buscar {tipo_nome}: {str(e)}\n\n"

nome_arquivo = f"resultado_{data_arquivo}.pdf"
salvar_em_pdf(nome_arquivo, resultado_texto, titulo_pdf, data_hoje_formatada)

print(f"✅ PDF gerado com sucesso: {nome_arquivo}")