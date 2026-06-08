
import os
import re
import math
import ezdxf
from ezdxf import bbox
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
# Importando as configurações para forçar o Monocromático
from ezdxf.addons.drawing.config import Configuration, ColorPolicy, BackgroundPolicy

def gerar_pdf_padrao(caminho_pdf, dados_peca, caminho_img_peca):
    """Gera o PDF com o layout da LYPSYOS."""
    largura_a4, altura_a4 = A4
    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    
    margem = 20
    c.setLineWidth(2)
    c.setStrokeColor(colors.black)
    c.rect(margem, margem, largura_a4 - (margem * 2), altura_a4 - (margem * 2))
    
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(largura_a4 / 2.0, altura_a4 - 45, f"DESENHO DA PEÇA: {dados_peca['identificador']}")
    c.setLineWidth(1)
    c.line(margem, altura_a4 - 60, largura_a4 - margem, altura_a4 - 60)
    
    if os.path.exists(caminho_img_peca):
        largura_desenho = largura_a4 - 80
        altura_desenho = 450
        c.drawImage(ImageReader(caminho_img_peca), margem + 20, 160, 
                    width=largura_desenho, height=altura_desenho, preserveAspectRatio=True)
    
    topo_selo = 140
    c.line(margem, topo_selo, largura_a4 - margem, topo_selo)
    
    c.setFillColor(colors.HexColor("#e8e8e3"))
    c.rect(margem, topo_selo - 20, largura_a4 - (margem * 2), 20, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margem + 10, topo_selo - 14, "LYPSYOS - DBX V4")
    c.drawRightString(largura_a4 - margem - 10, topo_selo - 14, "DESENHO TÉCNICO DE PEÇA PARA CORTE")
    
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(margem + 5, topo_selo - 32, "NOME / IDENTIFICADOR")
    c.drawString(margem + 205, topo_selo - 32, "PROJETO")
    c.drawString(margem + 295, topo_selo - 32, "FORMA")
    c.drawString(margem + 405, topo_selo - 32, "ESPESSURA")
    c.drawString(margem + 485, topo_selo - 32, "QUANTIDADE")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(margem + 5, topo_selo - 46, dados_peca['identificador'])
    c.drawString(margem + 205, topo_selo - 46, dados_peca['projeto'])
    c.drawString(margem + 295, topo_selo - 46, dados_peca['forma'])
    c.drawString(margem + 405, topo_selo - 46, dados_peca['espessura'])
    c.drawString(margem + 485, topo_selo - 46, dados_peca['quantidade'])
    
    c.line(margem, topo_selo - 52, largura_a4 - margem, topo_selo - 52)
    
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(margem + 5, topo_selo - 64, "DIMENSÕES PRINCIPAIS")
    c.drawString(margem + 255, topo_selo - 64, "FURAÇÕES")
    c.drawString(margem + 405, topo_selo - 64, "OBSERVAÇÕES")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(margem + 5, topo_selo - 78, dados_peca['dimensoes'])
    c.drawString(margem + 255, topo_selo - 78, dados_peca['furacoes'])
    c.setFont("Helvetica", 8)
    c.drawString(margem + 405, topo_selo - 78, "Unidades em mm | Escala Automática")
    
    c.line(margem + 200, topo_selo - 20, margem + 200, topo_selo - 52)
    c.line(margem + 290, topo_selo - 20, margem + 290, topo_selo - 52)
    c.line(margem + 400, topo_selo - 20, margem + 400, topo_selo - 90)
    c.line(margem + 480, topo_selo - 20, margem + 480, topo_selo - 52)
    c.line(margem + 250, topo_selo - 52, margem + 250, topo_selo - 90)

    # --- NOVO: BLOCO DE TOLERÂNCIA (RODAPÉ DO SELO) ---
    c.line(margem, topo_selo - 90, largura_a4 - margem, topo_selo - 90) # Linha que fecha a parte de cima
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#444444")) # Cinza bem escuro para o texto não brigar com os dados principais
    # \u00B1 é o código para o símbolo de ± (Mais ou Menos)
    c.drawCentredString(largura_a4 / 2.0, topo_selo - 108, "NOTA DE FABRICAÇÃO: PODE HAVER VARIAÇÃO DIMENSIONAL DE \u00B1 2 mm")

    c.save()

def processar_dxf_multiplas_pecas(caminho_dxf, pasta_destino):
    doc = ezdxf.readfile(caminho_dxf)
    msp = doc.modelspace()

    # 1. Mapear os textos (Âncoras)
    padrao = re.compile(r"(\d+)_([A-Za-z0-9\-]+)_([\d\.]+)\s*\((\d+)x\)", re.IGNORECASE)
    textos_validos = []

    for texto in msp.query('TEXT MTEXT'):
        if texto.dxf.layer.upper() == 'TEXTO':
            match = padrao.search(texto.dxf.text)
            if match:
                textos_validos.append({
                    'texto_bruto': texto.dxf.text,
                    'pt': texto.dxf.insert,
                    'entidades_geometria': [],
                    'dados': {
                        "projeto": match.group(1),
                        "identificador": match.group(2),
                        "espessura": match.group(3).replace('.', ',') + " mm",
                        "quantidade": match.group(4),
                        "forma": "Retangular",
                        "dimensoes": "-",
                        "furacoes": "Sem furação"
                    }
                })

    if not textos_validos:
        print(f"[{os.path.basename(caminho_dxf)}] Nenhum texto válido na layer TEXTO.")
        return

    # 2. Agrupar Geometrias E COTAS
    # Incluímos DIMENSION (Cota nativa) e LEADER (Setas) na busca
    todas_entidades = msp.query('LINE ARC CIRCLE LWPOLYLINE POLYLINE DIMENSION LEADER MTEXT TEXT')
    
    for ent in todas_entidades:
        layer_entidade = ent.dxf.layer.upper()
        
        # Filtro: Pega a entidade se ela for da layer CONTORNO ou se for uma entidade de COTA/TEXTO solta
        if layer_entidade in ['CONTORNO', 'COTAS', 'COTA', 'DIM'] or ent.dxftype() in ['DIMENSION', 'LEADER']:
            ext = bbox.extents([ent])
            if ext.has_data:
                centro_x = (ext.extmax.x + ext.extmin.x) / 2
                centro_y = (ext.extmax.y + ext.extmin.y) / 2

                min_dist = float('inf')
                texto_mais_proximo = None

                for t in textos_validos:
                    dist = math.hypot(centro_x - t['pt'].x, centro_y - t['pt'].y)
                    if dist < min_dist:
                        min_dist = dist
                        texto_mais_proximo = t

                if texto_mais_proximo and min_dist < 5000:
                    texto_mais_proximo['entidades_geometria'].append(ent)

    # 3. Gerar PDF
    for t in textos_validos:
        if not t['entidades_geometria']:
            continue

        # Calcula as dimensões filtrando APENAS as geometrias de contorno (ignora o tamanho da cota)
        entidades_contorno = [e for e in t['entidades_geometria'] if e.dxftype() not in ['DIMENSION', 'LEADER', 'TEXT', 'MTEXT']]
        if entidades_contorno:
            ext_peca = bbox.extents(entidades_contorno)
            if ext_peca.has_data:
                largura = abs(ext_peca.extmax.x - ext_peca.extmin.x)
                altura = abs(ext_peca.extmax.y - ext_peca.extmin.y)
                t['dados']['dimensoes'] = f"{largura:.1f} x {altura:.1f} mm"

                qtd_furos = sum(1 for ent in entidades_contorno if ent.dxftype() == 'CIRCLE')
                if qtd_furos > 0:
                    t['dados']['furacoes'] = f"Sim ({qtd_furos} furos)"

        img_temporaria = os.path.join(pasta_destino, f"temp_{t['dados']['identificador']}.png")
        try:
            fig = plt.figure()
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_aspect('equal')
            ax.set_axis_off()

            # Força o renderizador a desenhar TUDO em preto com fundo branco
            config_monocromatico = Configuration(
                background_policy=BackgroundPolicy.CUSTOM,
                custom_bg_color="#FFFFFF",
                color_policy=ColorPolicy.BLACK
            )

            ctx = RenderContext(doc)
            out = MatplotlibBackend(ax)
            frontend = Frontend(ctx, out, config=config_monocromatico)
            
            frontend.draw_entities(t['entidades_geometria'])
            ax.autoscale(enable=True, axis='both', tight=True)

            fig.savefig(img_temporaria, dpi=150, bbox_inches='tight', pad_inches=0.1, facecolor='#FFFFFF')
            plt.close(fig)

            nome_saida_pdf = f"{t['dados']['projeto']}_{t['dados']['identificador']}_Espessura_{t['dados']['espessura'].replace(' ', '')}.pdf"
            caminho_final_pdf = os.path.join(pasta_destino, nome_saida_pdf)
            
            gerar_pdf_padrao(caminho_final_pdf, t['dados'], img_temporaria)
            print(f" -> Sucesso: {nome_saida_pdf}")
            
        except Exception as e:
            print(f" -> Erro ao gerar peça {t['dados']['identificador']}: {e}")
        finally:
            if os.path.exists(img_temporaria):
                os.remove(img_temporaria)

if __name__ == "__main__":
    PASTA_ENTRADA = "./dxf_entrada"
    PASTA_SAIDA = "./pdf_saida"
    
    if not os.path.exists(PASTA_ENTRADA): os.makedirs(PASTA_ENTRADA)
    if not os.path.exists(PASTA_SAIDA): os.makedirs(PASTA_SAIDA)
    
    print("Iniciando extração com renderização Monocromática e Cotas...")
    for item in os.listdir(PASTA_ENTRADA):
        if item.lower().endswith('.dxf'):
            print(f"\nLendo arquivo master: {item}")
            caminho_completo = os.path.join(PASTA_ENTRADA, item)
            processar_dxf_multiplas_pecas(caminho_completo, PASTA_SAIDA)

