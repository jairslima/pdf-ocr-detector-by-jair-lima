# Especificação Técnica: pdf-ocr-detector-by-jair-lima

Este documento descreve as diretrizes técnicas e operacionais do projeto pdf-ocr-detector-by-jair-lima. O utilitário foi desenhado para auxiliar no saneamento da biblioteca digital do usuário, localizando documentos em formato PDF que não possuem camada de texto pesquisável (passíveis de OCR) e facilitando a abertura sequencial no software Adobe Acrobat.

## Objetivo
Varrer recursivamente um diretório de arquivos PDF e identificar de forma automatizada quais deles contêm apenas imagens escaneadas, ou seja, que não possuem texto extraível. Uma vez identificados, o script auxilia o usuário abrindo-os em lotes de 9 por vez no Adobe Acrobat para que o processo de OCR manual seja efetuado.

## Escopo
* **Incluso:**
  * Varredura recursiva de diretórios.
  * Verificação de arquivos com extensão `.pdf`.
  * Extração de texto de todas as páginas do arquivo PDF para verificar se o mesmo está vazio.
  * Interface interativa via terminal (CLI) para controle de fluxo.
  * Abertura automatizada no visualizador padrão do sistema (Adobe Acrobat) em lotes de 9 arquivos.
* **Excluso:**
  * Execução automática de OCR (o processo é manual por parte do usuário no Adobe Acrobat).
  * Edição direta do conteúdo binário dos PDFs.

## Arquitetura
O utilitário é uma aplicação de linha de comando (CLI) escrita em Python 3.
A arquitetura baseia-se em três etapas lógicas:
1. **Varredura:** Uso de módulos nativos do Python para caminhar pela árvore de diretórios.
2. **Análise de Conteúdo:** Utilização da biblioteca `pypdf` para ler a estrutura de páginas e realizar a extração de caracteres.
3. **Orquestração e Interface:** Controle de fluxo em laço. No modo interativo (padrão), o script agrupa arquivos em lotes de até 9 itens, abre no leitor e aguarda input do usuário. No modo automático (`--auto`), o script abre no máximo 9 arquivos e encerra imediatamente.

## Dependências
* Python 3.x
* Biblioteca `pypdf` (instalada automaticamente se não estiver presente no ambiente)

## Decisões de Design
* **Interatividade via Lotes de 9:** Em vez de abrir todos de uma só vez ou apenas um por um, o script agrupa arquivos sem OCR em lotes de 9. Isso otimiza o tempo do usuário no Adobe Acrobat sem sobrecarregar a memória do sistema.
* **Critério de OCR pendente:** Um arquivo PDF é classificado como "sem OCR" se a extração de texto de todas as suas páginas retornar apenas strings vazias ou compostas exclusivamente por caracteres de espaçamento.
* **Abertura do Sistema:** Utilização de `os.startfile` no Windows para invocar a aplicação associada ao arquivo (Adobe Acrobat), garantindo compatibilidade sem necessidade de codificar o caminho absoluto do executável do leitor de PDF.
* **Intervalo de Abertura:** Um atraso curto (0.5 segundo) entre as aberturas de arquivos no mesmo lote ajuda a evitar conflitos no leitor de PDF do Windows.
* **Execução Automática e Encerramento Imediato:** O modo `--auto` foi desenhado para agendamentos. Ele abre até 9 arquivos sem OCR e finaliza o processo Python de imediato para não deixar instâncias travadas em segundo plano consumindo memória.

## Critérios de Aceite
* O script deve identificar corretamente um PDF contendo texto (como livros digitais nativos) e ignorá-lo.
* O script deve identificar corretamente um PDF contendo apenas imagens escaneadas e listá-lo.
* Ao detectar PDFs sem OCR, eles devem ser agrupados em lotes de no máximo 9 arquivos.
* Os arquivos do lote atual devem ser abertos com sucesso no leitor padrão.
* O script não deve prosseguir para o próximo lote até que o usuário responda à instrução no terminal (em modo interativo).
* O script deve permitir pular o lote atual ou sair da varredura a qualquer momento (em modo interativo).
* Em modo automático (`--auto`), o script deve abrir no máximo 9 arquivos e fechar o processo imediatamente, registrando a operação no arquivo `registro_auto.txt`.

## Instruções Operacionais
Para executar o utilitário em modo interativo, abra um terminal na pasta do projeto e execute:
```powershell
python ocr_detector.py
```

Para executar o utilitário em modo automático (para testes manuais):
```powershell
python ocr_detector.py --auto
```

Para configurar a tarefa mensal no Agendador de Tarefas do Windows para executar todo dia 1 do mês às 01:00 AM:
```powershell
powershell -ExecutionPolicy Bypass -File schedule_task.ps1
```

