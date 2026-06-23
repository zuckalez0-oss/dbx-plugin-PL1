import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class GeradorPDFLayout:
    """Responsável pela geração do documento técnico final em PDF."""
    
    @staticmethod
    def gerar_pdf_padrao(caminho_pdf, dados_peca, caminho_img_peca):
        """Gera o PDF com o layout padrão da LYPSYOS."""
        largura_a4, altura_a4 = A4
        c = canvas.Canvas(caminho_pdf, pagesize=A4)
        
        # Borda externa do desenho
        margem = 20
        c.setLineWidth(2)
        c.setStrokeColor(colors.black)
        c.rect(margem, margem, largura_a4 - (margem * 2), altura_a4 - (margem * 2))
        
        # Cabeçalho dinâmico
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(largura_a4 / 2.0, altura_a4 - 45, f"DESENHO DA PEÇA: {dados_peca['identificador']}")
        c.setLineWidth(1)
        c.line(margem, altura_a4 - 60, largura_a4 - margem, altura_a4 - 60)
        
        # Área de plotagem da imagem
        if os.path.exists(caminho_img_peca):
            largura_desenho = largura_a4 - 80
            altura_desenho = 450
            c.drawImage(ImageReader(caminho_img_peca), margem + 20, 160, 
                        width=largura_desenho, height=altura_desenho, preserveAspectRatio=True)
        
        # Linhas estruturais do Selo Técnico
        topo_selo = 140
        c.line(margem, topo_selo, largura_a4 - margem, topo_selo)
        
        c.setFillColor(colors.HexColor("#e8e8e3"))
        c.rect(margem, topo_selo - 20, largura_a4 - (margem * 2), 20, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margem + 10, topo_selo - 14, "NOROACO- DBX V4")
        c.drawRightString(largura_a4 - margem - 10, topo_selo - 14, "DESENHO TÉCNICO DE PEÇA PARA CORTE")
        
        # Labels do Selo (Camada superior)
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(margem + 5, topo_selo - 32, "NOME / IDENTIFICADOR")
        c.drawString(margem + 205, topo_selo - 32, "PROJETO")
        c.drawString(margem + 295, topo_selo - 32, "FORMA")
        c.drawString(margem + 405, topo_selo - 32, "ESPESSURA")
        c.drawString(margem + 485, topo_selo - 32, "QUANTIDADE")
        
        # Dados da Peça (Camada inferior)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margem + 5, topo_selo - 46, dados_peca['identificador'])
        c.drawString(margem + 205, topo_selo - 46, dados_peca['projeto'])
        c.drawString(margem + 295, topo_selo - 46, dados_peca['forma'])
        c.drawString(margem + 405, topo_selo - 46, dados_peca['espessura'])
        c.drawString(margem + 485, topo_selo - 46, dados_peca['quantidade'])
        
        c.line(margem, topo_selo - 52, largura_a4 - margem, topo_selo - 52)
        
        # Subseções do Selo
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
        
        # Divisórias verticais do selo
        c.line(margem + 200, topo_selo - 20, margem + 200, topo_selo - 52)
        c.line(margem + 290, topo_selo - 20, margem + 290, topo_selo - 52)
        c.line(margem + 400, topo_selo - 20, margem + 400, topo_selo - 90)
        c.line(margem + 480, topo_selo - 20, margem + 480, topo_selo - 52)
        c.line(margem + 250, topo_selo - 52, margem + 250, topo_selo - 90)

        # Bloco de Tolerância e Rodapé Informativo
        c.line(margem, topo_selo - 90, largura_a4 - margem, topo_selo - 90)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawCentredString(largura_a4 / 2.0, topo_selo - 108, "NOTA DE FABRICAÇÃO: PODE HAVER VARIAÇÃO DIMENSIONAL DE \u00B1 2 mm")

        c.save()