import os
import sys
import subprocess
import argparse

# Configura a saída padrão do console para UTF-8 no Windows para evitar UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Garante a importação e instalação da biblioteca pypdf se necessário
try:
    import pypdf
except ImportError:
    print("Biblioteca 'pypdf' não encontrada. Instalando automaticamente via pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
        import pypdf
        print("Biblioteca 'pypdf' instalada e carregada com sucesso!\n")
    except Exception as e:
        print(f"Erro crítico ao tentar instalar a biblioteca 'pypdf': {e}")
        print("Por favor, instale manualmente executando: pip install pypdf")
        input("Pressione ENTER para fechar...")
        sys.exit(1)

def is_scanned_pdf(file_path):
    """
    Analisa se o PDF é apenas imagem (sem OCR).
    Retorna True se nenhuma página contiver texto extraível.
    """
    try:
        # Abre o arquivo PDF de forma segura
        reader = pypdf.PdfReader(file_path)
        if not reader.pages:
            return False
        
        # Analisa página por página
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                # Encontrou texto legível, portanto já possui OCR ou é nativo
                return False
                
        # Se nenhuma página retornou texto legível, é escaneado sem OCR
        return True
    except Exception as e:
        # Se ocorrer erro ao ler o PDF (arquivo corrompido, protegido, etc)
        # reportamos mas não travamos a execução.
        print(f"\n[Aviso] Não foi possível ler o arquivo: {file_path}")
        print(f"        Detalhe do erro: {e}")
        return False

def format_size(size_bytes):
    """Formata o tamanho do arquivo em formato legível."""
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def run_detector(auto=False, scan_dir=None):
    scan_dir = scan_dir or os.path.join(os.path.expanduser("~"), "Documents")
    BATCH_SIZE = 9
    
    print("======================================================================")
    print("             DETECTOR DE PDFS SEM OCR: BY JAIR LIMA")
    print("======================================================================")
    print(f"Diretório alvo: {scan_dir}")
    if auto:
        print(f"Modo: Execução Automática (Abertura de até {BATCH_SIZE} PDFs e encerramento)")
    else:
        print(f"Modo: Processamento em lotes de {BATCH_SIZE} arquivos")
    print("Iniciando varredura recursiva de arquivos. Por favor, aguarde...")
    print("----------------------------------------------------------------------")
    
    if not os.path.exists(scan_dir):
        print(f"[Erro] O diretório {scan_dir} não existe fisicamente no disco.")
        if not auto:
            input("\nPressione ENTER para sair...")
        return

    scanned_count = 0
    total_scanned_files = 0
    batch = []
    
    def process_batch(current_batch):
        nonlocal scanned_count
        if not current_batch:
            return True
            
        print("\n\n" + "="*70)
        print(f"[*] LOTE DE PDFs SEM OCR LOCALIZADOS ({len(current_batch)} arquivos)")
        print("="*70)
        
        for idx, (path, size) in enumerate(current_batch, 1):
            print(f" {idx}. Caminho: {path}")
            print(f"    Tamanho: {format_size(size)}")
            print("-" * 50)
            
        print("[Status] Abrindo lote no Adobe Acrobat...")
        
        import time
        for path, _ in current_batch:
            try:
                os.startfile(path)
                time.sleep(0.5) # pequeno intervalo para o Adobe processar sem engasgar
            except Exception as e:
                print(f"[Erro] Não foi possível abrir o arquivo {path}: {e}")
                
        if auto:
            try:
                from datetime import datetime
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro_auto.txt")
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Abertos {len(current_batch)} arquivos sem OCR no Adobe Acrobat.\n")
                    for path, _ in current_batch:
                        log_file.write(f"  - {path}\n")
            except Exception as e:
                print(f"[Aviso] Erro ao gravar registro de execução: {e}")
            print("\nModo automático: arquivos abertos no Adobe Acrobat. Encerrando execução.")
            return False
            
        print("\n[Instruções] Faça o OCR e salve no Adobe Acrobat para cada um dos arquivos.")
        print("             Em seguida, escolha uma opção abaixo:")
        print("  [ENTER] Ir para o próximo lote de PDFs sem OCR")
        print("  [s]     Pular este lote e continuar a busca")
        print("  [q]     Sair do programa e parar a busca")
        
        choice = input("\nEscolha uma opção: ").strip().lower()
        if choice in ['q', 'quit', 'exit']:
            return False
        return True

    # Executa a varredura recursiva na pasta e subpastas
    for root, dirs, files in os.walk(scan_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                total_scanned_files += 1
                file_path = os.path.join(root, file)
                
                # Exibe um indicador sutil de progresso no console
                sys.stdout.write(f"\rAnalisando arquivo #{total_scanned_files}... ")
                sys.stdout.flush()
                
                if is_scanned_pdf(file_path):
                    scanned_count += 1
                    file_size = os.path.getsize(file_path)
                    batch.append((file_path, file_size))
                    
                    if len(batch) == BATCH_SIZE:
                        if not process_batch(batch):
                            if not auto:
                                print("\nEncerrando a varredura a pedido do usuário.")
                                print(f"Total de PDFs sem OCR encontrados nesta sessão: {scanned_count}")
                                input("Pressione ENTER para fechar...")
                            return
                        batch = []
                        print(f"\nContinuando busca...")

    # Processa os arquivos restantes que não completaram um lote cheio
    if batch:
        if not process_batch(batch):
            if not auto:
                print("\nEncerrando a varredura a pedido do usuário.")
                print(f"Total de PDFs sem OCR encontrados nesta sessão: {scanned_count}")
                input("Pressione ENTER para fechar...")
            return

    if not auto:
        print("\n" + "-"*70)
        print("Varredura concluída!")
        print(f"Total de arquivos PDF verificados: {total_scanned_files}")
        print(f"Total de PDFs sem OCR encontrados: {scanned_count}")
        input("\nPressione ENTER para fechar...")
    else:
        if scanned_count == 0:
            try:
                from datetime import datetime
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro_auto.txt")
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Varredura concluída. Nenhum PDF sem OCR encontrado.\n")
            except Exception as e:
                print(f"[Aviso] Erro ao gravar registro de execução: {e}")
            print("\nVarredura automática concluída: nenhum PDF sem OCR localizado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detector de PDFs sem OCR - by Jair Lima")
    parser.add_argument("--pasta", default=None, help="Pasta a varrer (padrao: Documentos do usuario)")
    parser.add_argument("--auto", action="store_true", help="Executa de forma automatica, abre ate 9 PDFs no Adobe Acrobat e encerra sem interacao")
    args = parser.parse_args()
    
    try:
        run_detector(auto=args.auto, scan_dir=args.pasta)
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
        sys.exit(0)

