# PDF OCR Detector by Jair Lima

Varre uma pasta de PDFs e encontra os que **não têm texto extraível**, ou seja, os que são só imagens escaneadas. Em seguida abre esses arquivos no leitor padrão do Windows (por exemplo, o Adobe Acrobat), em lotes de 9, para você aplicar o OCR.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```bash
python ocr_detector.py --pasta "D:\\Biblioteca"          # modo interativo, lotes de 9
python ocr_detector.py --pasta "D:\\Biblioteca" --auto   # abre até 9 e encerra, sem interação
```

Sem `--pasta`, varre a pasta Documentos do usuário. O modo `--auto` grava um registro em `registro_auto.txt` ao lado do script.

## Como decide

Um PDF é considerado sem OCR quando a extração de texto de todas as páginas (com `pypdf`) devolve apenas texto vazio ou espaços. O programa não executa OCR: só localiza e abre os arquivos.

## Especificação

Veja [SPEC.md](SPEC.md).

## Licença

MIT, veja [LICENSE](LICENSE).
