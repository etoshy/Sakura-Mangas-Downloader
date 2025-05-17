import os
import json
import re
import requests
import time
import sys

def extract_meta_from_url(url):
    """
    Extrai chapter_id e token da URL ou conteúdo HTML
    """
    try:
        # Tenta buscar o conteúdo da página primeiro
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Falha ao acessar URL: {url}")
            return None, None
            
        content = response.text
        
        # Extrai chapter_id e token usando regex
        chapter_id_match = re.search(r'<meta chapter-id="(\d+)">', content)
        token_match = re.search(r'<meta token="([^"]+)">', content)
        
        if chapter_id_match and token_match:
            chapter_id = chapter_id_match.group(1)
            token = token_match.group(1)
            return chapter_id, token
        else:
            print("Não foi possível encontrar chapter_id e token no conteúdo da página")
            return None, None
            
    except Exception as e:
        print(f"Erro ao acessar URL: {e}")
        return None, None

def get_chapter_info(chapter_id, token):
    """
    Obtém informações do capítulo usando a API
    """
    url = 'https://sakuramangas.org/dist/sakura/models/capitulo/capitulos_info.php'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = f'chapter_id={chapter_id}&token={token}'
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            print(f"Falha ao obter informações do capítulo: Código de status {response.status_code}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"Erro ao obter informações do capítulo: {e}")
        return None

def get_chapter_pages(chapter_id, token):
    """
    Obtém páginas do capítulo usando a API
    """
    url = 'https://sakuramangas.org/dist/sakura/models/capitulo/capitulos_read.php'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = f'chapter_id={chapter_id}&token={token}'
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            print(f"Falha ao obter páginas do capítulo: Código de status {response.status_code}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"Erro ao obter páginas do capítulo: {e}")
        return None

def download_images(image_urls, output_folder):
    """
    Faz download das imagens das URLs e salva na pasta especificada
    """
    pages_folder = os.path.join(output_folder, 'pages')
    if not os.path.exists(pages_folder):
        os.makedirs(pages_folder)
    
    base_url = 'https://sakuramangas.org'
    
    for img_url in image_urls:
        # Limpa a URL removendo '../' e garantindo que comece com '/'
        clean_url = img_url.replace('../', '')
        if not clean_url.startswith('/'):
            clean_url = '/' + clean_url
            
        full_url = base_url + clean_url
        
        # Extrai o nome do arquivo (ex: '001.jpg')
        filename = os.path.basename(img_url)
        output_path = os.path.join(pages_folder, filename)
        
        print(f"Fazendo download de {filename} de {full_url}")
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"Download concluído: {filename}")
            else:
                print(f"Falha ao baixar {filename}: Código de status {response.status_code}")
                
            # Adiciona um pequeno atraso para evitar sobrecarregar o servidor
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Erro ao baixar {filename}: {e}")

def download_chapter(url_or_chapter_id, token=None):
    """
    Faz download de um capítulo de mangá
    """
    # Se uma URL for fornecida, extrai chapter_id e token
    if url_or_chapter_id.startswith('http'):
        print(f"Extraindo metadados da URL: {url_or_chapter_id}")
        chapter_id, token = extract_meta_from_url(url_or_chapter_id)
        if not chapter_id or not token:
            print("Falha ao extrair chapter_id e token da URL")
            return False
    else:
        chapter_id = url_or_chapter_id
        if not token:
            print("Token é necessário quando fornecido chapter_id diretamente")
            return False
    
    print(f"Usando chapter_id: {chapter_id}, token: {token}")
    
    # Obtém informações do capítulo
    chapter_info = get_chapter_info(chapter_id, token)
    if not chapter_info:
        print("Falha ao obter informações do capítulo")
        return False
    
    # Obtém título do mangá e número do capítulo
    manga_title = chapter_info['manga']['titulo']
    chapter_number = chapter_info['capitulo']['numero']
    
    print(f"Mangá: {manga_title}")
    print(f"Capítulo: {chapter_number}")
    
    # Cria estrutura de pastas
    mangas_folder = 'mangas'
    if not os.path.exists(mangas_folder):
        os.makedirs(mangas_folder)
    
    manga_folder = os.path.join(mangas_folder, manga_title)
    if not os.path.exists(manga_folder):
        os.makedirs(manga_folder)
    
    chapter_folder = os.path.join(manga_folder, str(chapter_number))
    if not os.path.exists(chapter_folder):
        os.makedirs(chapter_folder)
    
    # Salva informações do capítulo
    with open(os.path.join(chapter_folder, 'capitulo_info.json'), 'w', encoding='utf-8') as f:
        json.dump(chapter_info, f, ensure_ascii=False, indent=4)
    
    # Obtém páginas do capítulo
    chapter_pages = get_chapter_pages(chapter_id, token)
    if not chapter_pages:
        print("Falha ao obter páginas do capítulo")
        return False
    
    # Salva informações das páginas do capítulo
    with open(os.path.join(chapter_folder, 'capitulo_pages.json'), 'w', encoding='utf-8') as f:
        json.dump(chapter_pages, f, ensure_ascii=False, indent=4)
    
    # Faz download das imagens
    print(f"Fazendo download de {len(chapter_pages['imageUrls'])} imagens...")
    download_images(chapter_pages['imageUrls'], chapter_folder)
    
    print(f"Capítulo {chapter_number} de {manga_title} baixado com sucesso")
    return True

def process_json_file(json_file_path):
    """
    Processa um arquivo JSON contendo links de capítulos
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            chapters_data = json.load(f)
            
        # Processa links em ordem reversa (de baixo para cima)
        for chapter in reversed(chapters_data):
            link = chapter.get('link-capitulo')
            chapter_num = chapter.get('num-capitulo')
            chapter_title = chapter.get('cap-titulo')
            scan_name = chapter.get('scan-nome')
            
            if link:
                print(f"\nProcessando Capítulo {chapter_num}: {chapter_title} (Scan: {scan_name})")
                download_chapter(link)
            else:
                print(f"Link faltando para o capítulo {chapter_num}")
                
            # Adiciona um pequeno atraso entre capítulos
            time.sleep(1)
            
        return True
    except Exception as e:
        print(f"Erro ao processar arquivo JSON {json_file_path}: {e}")
        return False

def main():
    # Verifica se algum argumento foi fornecido
    if len(sys.argv) < 2:
        print("Sakura Mangas Downloader")
        print("=" * 30)
        print("\nModo de uso:")
        print("  python cap.py link1,link2,link3")
        print("  python cap.py caminho/para/arquivo1.json,caminho/para/arquivo2.json")
        print("\nOu execute interativamente:")
        run_interactive()
        return
    
    # Processa todos os argumentos
    all_args = ','.join(sys.argv[1:])
    args_list = [arg.strip() for arg in all_args.split(',')]
    
    for arg in args_list:
        if arg.lower().endswith('.json'):
            print(f"\nProcessando arquivo JSON: {arg}")
            process_json_file(arg)
        elif arg.startswith('http'):
            print(f"\nProcessando URL: {arg}")
            download_chapter(arg)
        else:
            print(f"Argumento não reconhecido: {arg}")

def run_interactive():
    """
    Executa o script no modo interativo
    """
    while True:
        print("\nOpções:")
        print("1. Baixar usando URL")
        print("2. Baixar usando chapter_id e token")
        print("3. Processar arquivo JSON com links de capítulos")
        print("4. Sair")
        
        choice = input("Selecione uma opção (1-4): ")
        
        if choice == '1':
            url = input("Digite a URL do capítulo: ")
            download_chapter(url)
        elif choice == '2':
            chapter_id = input("Digite o chapter_id: ")
            token = input("Digite o token: ")
            download_chapter(chapter_id, token)
        elif choice == '3':
            json_path = input("Digite o caminho para o arquivo JSON: ")
            process_json_file(json_path)
        elif choice == '4':
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    main()