
# DBX Plugin: Gerador de Peças a partir de Master DXF 🖨️🤖

**Ferramenta de automação que processa um arquivo DXF "master" contendo múltiplas peças, extraindo-as em arquivos DXF individuais para CAM e gerando PDFs técnicos detalhados para cada uma.**
## 📝 Sobre o Projeto
Este projeto otimiza o fluxo de trabalho de engenharia ao automatizar a tediosa tarefa de separar peças de um layout mestre. A partir de um único arquivo DXF, a ferramenta identifica cada peça, extrai suas informações e geometria, e gera os entregáveis necessários para a produção e documentação:

1.  **Arquivos DXF para CAM:** Um arquivo DXF limpo para cada peça, contendo apenas o contorno de corte, posicionado na origem (0,0) para fácil importação em software CAM.
2.  **Desenhos Técnicos em PDF:** Um PDF para cada peça, com um layout padronizado, incluindo uma imagem da peça (com cotas e dobras), e um selo técnico preenchido com dados como projeto, dimensões, espessura, etc.

O processo é finalizado com a limpeza automática do arquivo DXF master, que tem suas geometrias de corte e dobra removidas, deixando-o pronto para o próximo layout.

### ✨ Principais Funcionalidades
*   **Extração de Múltiplas Peças:** Processa um único arquivo DXF contendo o layout de várias peças.
*   **Agrupamento Inteligente:** Usa âncoras de texto para identificar e agrupar a geometria de cada peça (contornos, dobras, cotas).
*   **Geração de DXF para CAM:** Exporta um DXF individual por peça, contendo apenas as linhas de corte (`CONTORNO`), alinhado na origem (0,0).
*   **Geração de PDF Técnico:** Cria um PDF A4 para cada peça com um selo (title block) padrão, imagem da peça e informações detalhadas.
*   **Preenchimento Automático de Dados:** Extrai dados (projeto, identificador, espessura, quantidade) do texto âncora e calcula automaticamente as dimensões e a quantidade de furos.
*   **Limpeza do Arquivo Master:** Após a extração bem-sucedida, remove as entidades processadas do arquivo DXF master, preparando-o para novo uso.

---

## 🚀 Como Utilizar
### Pré-requisitos
*   Python 3.8 ou superior.
*   Bibliotecas Python: `ezdxf`, `matplotlib`, `reportlab`

### Instalação
1.  Clone ou baixe este repositório.
2.  Navegue até a pasta do projeto pelo terminal.
3.  Instale as dependências necessárias:
    ```bash
    pip install ezdxf matplotlib reportlab
    ```

### Passo 1: Preparar o Arquivo DXF Master

Para que o script funcione corretamente, seu arquivo DXF deve seguir algumas convenções:

1.  **Estrutura de Pastas:**
    *   `./dxf_entrada/`: Coloque seus arquivos DXF master aqui.
    *   `./dxf_saida/`: Os DXFs individuais para CAM serão salvos aqui.
    *   `./pdf_saida/`: Os PDFs técnicos serão salvos aqui.

2.  **Estrutura de Camadas (Layers) no DXF:**
    *   `TEXTO`: Camada para as âncoras de texto que identificam cada peça.
    *   `CONTORNO`: Camada para a geometria de corte da peça (linhas externas, furos).
    *   `DOBRAS` ou `DOBRA`: Camada para as linhas de dobra.
    *   `COTAS`, `COTA`, `DIM`: Camadas para as dimensões.

3.  **Formato da Âncora de Texto:**
    O texto na camada `TEXTO` deve seguir o padrão: `PROJETO_IDENTIFICADOR_ESPESSURA(QUANTIDADEx)`

    *   **Exemplo:** `1257_SUPORTE-MOTOR_3.17(4x)`
    *   **`1257`**: Código do projeto.
    *   **`SUPORTE-MOTOR`**: Identificador único da peça.
    *   **`3.17`**: Espessura do material (use ponto como separador decimal).
    *   **`4x`**: Quantidade de peças.

    Coloque este texto próximo à peça correspondente no desenho.

### Passo 2: Executar o Script

1.  Com os arquivos DXF master na pasta `dxf_entrada`, abra um terminal na raiz do projeto.
2.  Execute o processador principal:
    ```bash
    python processador_master.py
    ```
3.  O script irá varrer todos os arquivos `.dxf` na pasta de entrada, processar cada peça encontrada e gerar os arquivos de saída nas pastas `dxf_saida` e `pdf_saida`. O progresso será exibido no terminal.

---

## 🛠️ Ferramentas Auxiliares para AutoCAD

### Comando de Limpeza Rápida (LISP)

O script Python já limpa o arquivo master automaticamente após a exportação. Contudo, se você preferir realizar a limpeza manualmente de dentro do ambiente AutoCAD, pode criar um comando personalizado.

Isso é útil para limpar desenhos que não serão processados pelo script ou para verificar o estado do arquivo antes da automação.

**Como criar o botão de limpeza:**

> **Pré-requisito:** Você precisa ter uma rotina LISP que defina um comando `LIMPARPADRAO` para apagar as entidades das camadas de corte e dobra.

1.  No AutoCAD, abra a personalização da interface do usuário (comando `CUI`).
2.  Na lista de comandos, crie um novo comando.
3.  Na propriedade "Macro", digite:
    ```
    ^C^CLIMPARPADRAO;
    ```
4.  Arraste esse comando para a sua barra de ferramentas (Ribbon ou Toolbar) e escolha um ícone.

Pronto! Um clique no novo ícone e o comando de limpeza será executado