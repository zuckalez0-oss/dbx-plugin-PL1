import ezdxf
from ezdxf import bbox
from ezdxf.addons import Importer

class ExportadorDXF:
    """Responsável por isolar geometrias e exportar arquivos DXF individuais para CAM."""
    
    @staticmethod
    def criar_dxf_peca(doc_origem, entidades_corte, caminho_saida):
        """
        Cria um novo arquivo DXF contendo APENAS a geometria de corte.
        Garante o alinhamento do contorno principal na origem (0,0) para o CAM.
        """
        # Cria um novo documento mantendo a versão do arquivo original
        doc_destino = ezdxf.new(dxfversion=doc_origem.dxfversion)
        msp_destino = doc_destino.modelspace()
        
        # Garante a criação prévia das camadas (Neste caso, apenas a layer CONTORNO existirá)
        layers_origem = {e.dxf.layer for e in entidades_corte if hasattr(e.dxf, 'layer')}
        for layer in layers_origem:
            if layer not in doc_destino.layers:
                doc_destino.layers.new(name=layer)
                
        # Importa apenas as entidades de corte limpas (sem cotas, sem dobras)
        importer = Importer(doc_origem, doc_destino)
        importer.import_entities(entidades_corte)
        importer.finalize()
        
        # Rotina de alinhamento no Zero Máquina (0,0) baseado no contorno limpo
        if entidades_corte:
            ext_peca = bbox.extents(entidades_corte)
            if ext_peca.has_data:
                dx = -ext_peca.extmin.x
                dy = -ext_peca.extmin.y
                
                # Move as entidades limpas para a origem
                for ent in msp_destino:
                    ent.translate(dx, dy, 0)
                    
        # Salva o arquivo individual pronto para a máquina
        doc_destino.saveas(caminho_saida)