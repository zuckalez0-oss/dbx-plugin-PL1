import os
import re
import math
import ezdxf
from ezdxf import bbox
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, ColorPolicy, BackgroundPolicy

from exportador_dxf import ExportadorDXF
from gerador_pdf import GeradorPDFLayout

class ProcessadorMaster:
    """Gerencia a leitura do arquivo DXF mestre, agrupamento e direcionamento para os módulos."""
    
    def __init__(self, pasta_entrada="./dxf_entrada", pasta_saida_pdf="./pdf_saida", pasta_saida_dxf="./dxf_saida"):
        self.pasta_entrada = pasta_entrada
        self.pasta_saida_pdf = pasta_saida_pdf
        self.pasta_saida_dxf = pasta_saida_dxf
        self.padrao_texto = re.compile(r"(\d+)_([A-Za-z0-9\-]+)_([\d\.]+)\s*\((\d+)x\)", re.IGNORECASE)
        self._inicializar_diretorios()

    def _inicializar_diretorios(self):
        for pasta in [self.pasta_entrada, self.pasta_saida_pdf, self.pasta_saida_dxf]:
            if not os.path.exists(pasta):
                os.makedirs(pasta)

    def processar_arquivo_master(self, nome_arquivo):
        caminho_dxf = os.path.join(self.pasta_entrada, nome_arquivo)
        doc = ezdxf.readfile(caminho_dxf)
        msp = doc.modelspace()

        # 1. Identificação das Âncoras de Texto
        textos_validos = []
        for texto in msp.query('TEXT MTEXT'):
            if hasattr(texto.dxf, 'layer') and texto.dxf.layer.upper() == 'TEXTO':
                match = self.padrao_texto.search(texto.dxf.text)
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
                            "forma": "Plani/Dobrada",
                            "dimensoes": "-",
                            "furacoes": "Sem furação"
                        }
                    })

        if not textos_validos:
            print(f"[{nome_arquivo}] Nenhuma peça estruturada mapeada na camada TEXTO.")
            return

        # 2. Agrupamento Espacial por Proximidade
        todas_entidades = msp.query('LINE ARC CIRCLE LWPOLYLINE POLYLINE DIMENSION LEADER MTEXT TEXT')
        layers_permitidas = ['CONTORNO', 'COTAS', 'COTA', 'DIM', 'DOBRAS', 'DOBRA']

        for ent in todas_entidades:
            layer_entidade = ent.dxf.layer.upper() if hasattr(ent.dxf, 'layer') else ''
            
            if layer_entidade in layers_permitidas or ent.dxftype() in ['DIMENSION', 'LEADER']:
                ext = bbox.extents([ent])
                if ext.has_data:
                    centro_x = (ext.extmax.x + ext.extmin.x) / 2
                    centro_y = (ext.extmax.y + ext.extmin.y) / 2

                    min_dist = float('inf')
                    value_texto = None

                    for t in textos_validos:
                        dist = math.hypot(centro_x - t['pt'].x, centro_y - t['pt'].y)
                        if dist < min_dist:
                            min_dist = dist
                            value_texto = t

                    if value_texto and min_dist < 5000:
                        value_texto['entidades_geometria'].append(ent)

        # 3. Exportação e Geração dos Entregáveis
        for t in textos_validos:
            if not t['entidades_geometria']:
                continue

            # Filtro exclusivo de contorno: Ignora cotas, textos e a vista da dobra
            entidades_contorno = [
                e for e in t['entidades_geometria'] 
                if e.dxftype() not in ['DIMENSION', 'LEADER', 'TEXT', 'MTEXT'] 
                and hasattr(e.dxf, 'layer') 
                and e.dxf.layer.upper() == 'CONTORNO'
            ]
            
            if entidades_contorno:
                ext_peca = bbox.extents(entidades_contorno)
                if ext_peca.has_data:
                    largura = abs(ext_peca.extmax.x - ext_peca.extmin.x)
                    altura = abs(ext_peca.extmax.y - ext_peca.extmin.y)
                    t['dados']['dimensoes'] = f"{largura:.1f} x {altura:.1f} mm"

                    qtd_furos = sum(1 for ent in entidades_contorno if ent.dxftype() == 'CIRCLE')
                    if qtd_furos > 0:
                        t['dados']['furacoes'] = f"Sim ({qtd_furos} furos)"

            base_nome = f"{t['dados']['projeto']}_{t['dados']['identificador']}_Esp_{t['dados']['espessura'].replace(' ', '')}"
            caminho_saida_dxf = os.path.join(self.pasta_saida_dxf, f"{base_nome}.dxf")
            caminho_saida_pdf = os.path.join(self.pasta_saida_pdf, f"{base_nome}.pdf")
            img_temporaria = os.path.join(self.pasta_saida_pdf, f"temp_{t['dados']['identificador']}.png")

            try:
                # PASSO A: Chamar Módulo DXF
                # ALTERAÇÃO AQUI: Enviando APENAS as `entidades_contorno` para o arquivo de máquina
                ExportadorDXF.criar_dxf_peca(doc, entidades_contorno, caminho_saida_dxf)
                
                # PASSO B: Renderização de Imagem para o PDF
                # Aqui continuamos enviando `t['entidades_geometria']` pois o PDF deve exibir tudo (cotas, dobras, etc)
                fig = plt.figure()
                ax = fig.add_axes([0, 0, 1, 1])
                ax.set_aspect('equal')
                ax.set_axis_off()

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

                # PASSO C: Chamar Módulo PDF Layout
                GeradorPDFLayout.gerar_pdf_padrao(caminho_saida_pdf, t['dados'], img_temporaria)
                print(f" -> Processado com Sucesso: {t['dados']['identificador']} [DXF Limpo + PDF Completo]")
                
            except Exception as e:
                print(f" -> Falha Crítica na peça {t['dados']['identificador']}: {e}")
            finally:
                if os.path.exists(img_temporaria):
                    os.remove(img_temporaria)

if __name__ == "__main__":
    processador = ProcessadorMaster()
    print("Iniciando Pipeline Avançado: Geração de DXF limpo para CAM e PDF detalhado...")
    
    for item in os.listdir(processador.pasta_entrada):
        if item.lower().endswith('.dxf'):
            print(f"\n[Master File Encontrado]: {item}")
            processador.processar_arquivo_master(item)