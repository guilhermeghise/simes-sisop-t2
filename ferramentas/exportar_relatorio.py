"""Exporta RELATORIO.md e os gráficos oficiais para um PDF A4.

Requer reportlab: python3 -m pip install reportlab
Uso: python3 ferramentas/exportar_relatorio.py
"""
import re
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


def inline(texto):
    texto = escape(texto)
    texto = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                   r'<link href="\2" color="#205b82">\1</link>', texto)
    texto = re.sub(r"`([^`]+)`", r'<font name="SimESSans">\1</font>', texto)
    texto = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", texto)
    return texto


def exportar(raiz):
    fontes = Path(reportlab.__file__).parent / "fonts"
    for nome, arquivo in (("SimESSans", "Vera.ttf"), ("SimESSans-Bold", "VeraBd.ttf"),
                          ("SimESSans-Italic", "VeraIt.ttf"), ("SimESSans-BoldItalic", "VeraBI.ttf")):
        pdfmetrics.registerFont(TTFont(nome, str(fontes / arquivo)))
    pdfmetrics.registerFontFamily("SimESSans", normal="SimESSans", bold="SimESSans-Bold",
                                  italic="SimESSans-Italic", boldItalic="SimESSans-BoldItalic")
    destino = raiz / "output" / "pdf" / "relatorio-simes.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    estilos = getSampleStyleSheet()
    estilos["Normal"].fontName = "SimESSans"
    estilos["Normal"].fontSize = 9
    estilos["Normal"].leading = 13
    estilos["Normal"].spaceAfter = 7
    estilos["Normal"].splitLongWords = True
    estilos["Normal"].allowOrphans = 0
    estilos["Normal"].allowWidows = 0
    for nome, tamanho in (("Title", 19), ("Heading1", 14), ("Heading2", 11)):
        estilos[nome].fontName = "SimESSans-Bold"
        estilos[nome].fontSize = tamanho
        estilos[nome].leading = tamanho + 4
        estilos[nome].textColor = colors.HexColor("#183b56")
        estilos[nome].spaceBefore = 13
        estilos[nome].spaceAfter = 8
        estilos[nome].keepWithNext = True
    celula = ParagraphStyle("Celula", parent=estilos["Normal"], fontSize=7,
                            leading=9, spaceAfter=0, alignment=TA_LEFT)
    legenda = ParagraphStyle("Legenda", parent=estilos["Normal"], fontSize=8,
                             leading=11, textColor=colors.HexColor("#475569"))
    largura = A4[0] - 3.2 * cm
    doc = SimpleDocTemplate(str(destino), pagesize=A4,
                            leftMargin=1.6*cm, rightMargin=1.6*cm,
                            topMargin=1.8*cm, bottomMargin=1.7*cm,
                            title="SimES - Relatório final",
                            author="Eduardo Ferrari e Guilherme Ghise Rossoni")
    conteudo = []
    linhas = (raiz / "RELATORIO.md").read_text(encoding="utf-8").splitlines()
    i = 0
    experimento = None
    graficos = {
        "X1": ["X1_resposta_media_ms.png", "X1_espera_max_ms.png", "X1_deslocamento_total.png"],
        "X2": ["X2_cpu.png"], "X3": ["X3_tempo_por_operacao.png"],
        "X4": ["X4_open_por_profundidade.png"], "X5": ["X5_tabelas.png"],
        "X8": ["X8_cpu.png", "X8_buffering.png"],
    }
    while i < len(linhas):
        linha = linhas[i].strip()
        if not linha:
            i += 1
            continue
        if linha.startswith("<!--"):
            while i < len(linhas) and "-->" not in linhas[i]:
                i += 1
            i += 1
            continue
        if linha.startswith("|"):
            dados = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                campos = [s.strip() for s in linhas[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in campos):
                    dados.append(campos)
                i += 1
            n = len(dados[0])
            if n == 8:
                pesos = [1.0, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 0.85]
            else:
                pesos = [1] * n
            larguras = [largura * p / sum(pesos) for p in pesos]
            celulas = [[Paragraph(inline(c), celula) for c in r] for r in dados]
            tabela = Table(celulas, colWidths=larguras, repeatRows=1, hAlign="LEFT")
            tabela.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2edf4")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
                ("LINEBELOW", (0, 0), (-1, 0), .6, colors.HexColor("#8ba9bc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            conteudo.extend([tabela, Spacer(1, 9)])
            continue
        if linha.startswith("#"):
            nivel = len(linha) - len(linha.lstrip("#"))
            titulo = linha[nivel:].strip()
            estilo = {1: "Title", 2: "Heading1"}.get(nivel, "Heading2")
            conteudo.append(Paragraph(inline(titulo), estilos[estilo]))
            m = re.match(r"(X\d+) —", titulo)
            experimento = m.group(1) if m else None
            i += 1
            continue
        paragrafo = [linha]
        i += 1
        while (i < len(linhas) and linhas[i].strip()
               and not linhas[i].startswith(("#", "|", "- "))
               and not re.match(r"\d+\.\s", linhas[i])):
            paragrafo.append(linhas[i].strip())
            i += 1
        texto = " ".join(paragrafo)
        if texto.startswith("- "):
            texto = "• " + texto[2:]
        paragrafo_pdf = Paragraph(inline(texto), estilos["Normal"])
        if texto.startswith("**Resultados:**"):
            paragrafo_pdf.keepWithNext = True
        conteudo.append(paragrafo_pdf)
        if texto.startswith("**Veredito:**") and experimento:
            for nome in graficos.get(experimento, []):
                caminho = raiz / "graficos" / nome
                if not caminho.is_file():
                    raise FileNotFoundError(caminho)
                img = Image(str(caminho))
                img.drawHeight *= largura / img.drawWidth
                img.drawWidth = largura
                conteudo.append(KeepTogether([
                    Spacer(1, 7), img,
                    Paragraph("Fonte: graficos/" + nome + "; dados da simulação oficial.", legenda),
                    Spacer(1, 8),
                ]))

    def pagina(canvas, documento):
        canvas.saveState()
        canvas.setFont("SimESSans", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(1.6*cm, A4[1]-1.1*cm, "Sistemas Operacionais · PUCRS · 2026/2")
        canvas.drawRightString(A4[0]-1.6*cm, 0.95*cm, "SimES | %d" % documento.page)
        canvas.restoreState()

    doc.build(conteudo, onFirstPage=pagina, onLaterPages=pagina)
    return destino


if __name__ == "__main__":
    print(exportar(Path(__file__).resolve().parents[1]))
