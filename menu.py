import os
import subprocess
import sys
import glob

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
    Sakura Mangas Downloader
    Criado por Etoshy
    https://github.com/etoshy/Sakura-Mangas-Downloader/
    """
    print(banner)

def download_chapters():
    clear_screen()
    print("=== Baixar Capítulos ===")
    print("Digite os links dos capítulos separados por vírgula (,)")
    print("Ou os caminhos dos arquivos links_caps.json")
    print("Exemplo: https://link1.com,https://link2.com")
    print("Ou: mangas/Shin Kirari/links_caps.json,mangas/Harukaze no Étranger/links_caps.json")
    print("\nDigite os links ou caminhos:")
    
    links = input("> ").strip()
    if not links:
        print("Nenhum link fornecido. Voltando ao menu...")
        input("Pressione Enter para continuar...")
        return
    
    # Limpar os links (remover espaços extras)
    links_list = [link.strip() for link in links.split(',')]
    processed_links = ",".join(links_list)
    
    # Executar o script cap.py
    command = f'python code/cap.py {processed_links}'
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script cap.py: {e}")
    finally:
        input("\nProcesso concluído. Pressione Enter para voltar ao menu...")

def download_complete_manga():
    clear_screen()
    print("=== Baixar Mangá Completo ===")
    print("Digite os links dos mangás separados por vírgula (,)")
    print("Exemplo: https://sakuramangas.org/obras/shin-kirari,https://sakuramangas.org/obras/harukaze-no-etranger")
    print("\nDigite os links:")
    
    links_input = input("> ").strip()
    if not links_input:
        print("Nenhum link fornecido. Voltando ao menu...")
        input("Pressione Enter para continuar...")
        return
    
    # Processar os links
    links = [link.strip() for link in links_input.split(',') if link.strip()]
    json_files = set()  # Usando set para evitar duplicatas
    
    for link in links:
        print(f"\nProcessando URL: {link}")
        try:
            command = f'python code/manga.py "{link}"'
            result = subprocess.run(command, shell=True, check=True)
            
            if result.returncode == 0:
                print(f"Processamento de {link} concluído com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o script manga.py para {link}: {e}")
        except Exception as e:
            print(f"Erro inesperado ao processar {link}: {e}")
    
    # Buscar todos os arquivos JSON após processar todos os links
    json_files.update(glob.glob('mangas/**/links_caps.json', recursive=True))
    
    # Se arquivos JSON foram gerados, oferecer para baixar os capítulos
    if json_files:
        print("\nArquivos links_caps.json gerados com sucesso:")
        for json_file in sorted(json_files):  # Ordenados alfabeticamente
            print(f"- {json_file}")
        
        print("\nDeseja baixar todos os capítulos agora? (S/N)")
        choice = input("> ").strip().lower()
        
        if choice == 's':
            json_paths = ",".join(sorted(json_files))  # Junta os paths sem duplicatas
            print(f"\nExecutando: python code/cap.py {json_paths}")
            try:
                subprocess.run(f'python code/cap.py "{json_paths}"', shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Erro ao executar o script cap.py: {e}")
    
    input("\nProcesso concluído. Pressione Enter para voltar ao menu...")

def main_menu():
    while True:
        clear_screen()
        print_banner()
        print("Menu Principal:")
        print("1 - Baixar Capítulo")
        print("2 - Baixar Mangá Completo")
        print("3 - Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            download_chapters()
        elif choice == '2':
            download_complete_manga()
        elif choice == '3':
            print("Saindo do Sakura Mangas Downloader...")
            break
        else:
            print("Opção inválida. Por favor, escolha 1, 2 ou 3.")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
        sys.exit(0)