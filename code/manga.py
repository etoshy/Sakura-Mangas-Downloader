import os
import re
import json
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def create_directory(path):
    """Cria diretório se não existir"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Diretório criado: {path}")

def extract_manga_info(url):
    """Extrai manga_id e token de uma URL de capítulo de mangá"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Extrai manga-id e token usando regex
            manga_id_match = re.search(r'<meta\s+manga-id="(\d+)">', response.text)
            token_match = re.search(r'<meta\s+token="([^"]+)">', response.text)
            
            if manga_id_match and token_match:
                manga_id = manga_id_match.group(1)
                token = token_match.group(1)
                return {"manga_id": manga_id, "token": token}
            else:
                # Método alternativo: tenta extrair da URL
                parsed_url = urlparse(url)
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) >= 2:
                    obra_name = path_parts[-2]
                    print(f"Não encontrou tags de metadados, mas encontrou nome da obra: {obra_name}")
                    # Você pode precisar implementar um jeito de obter manga_id do nome da obra
                
                print("Não foi possível extrair manga_id e token da página")
                return None
        else:
            print(f"Falha ao acessar URL: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao extrair informações do mangá: {e}")
        return None

def get_manga_details(manga_id, token):
    """Obtém detalhes do mangá da API"""
    url = 'https://sakuramangas.org/dist/sakura/models/manga/manga_info.php'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = {
        'manga_id': manga_id,
        'token': token,
        'dataType': 'json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Falha ao obter detalhes do mangá: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao obter detalhes do mangá: {e}")
        return None

def get_manga_chapters(manga_id, token, last_chapter):
    """Obtém todos os capítulos do mangá"""
    url = 'https://sakuramangas.org/dist/sakura/models/manga/manga_capitulos.php'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    all_chapters_html = ""
    all_chapters_data = []
    
    # Calcula quantas requisições precisamos fazer
    limit = 90
    requests_needed = (last_chapter // limit) + 1
    
    for i in range(requests_needed):
        offset = i * limit
        data = {
            'manga_id': manga_id,
            'token': token,
            'offset': offset,
            'order': 'desc',
            'limit': limit
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                chapters_html = response.text
                all_chapters_html += chapters_html
                
                # Analisa o HTML para extrair informações dos capítulos
                soup = BeautifulSoup(chapters_html, 'html.parser')
                chapter_items = soup.find_all('div', class_='capitulo-item')
                
                for chapter in chapter_items:
                    try:
                        chapter_num_span = chapter.find('span', class_='num-capitulo')
                        if not chapter_num_span:
                            continue
                            
                        chapter_num = chapter_num_span.get('data-chapter', '')
                        chapter_link_elem = chapter_num_span.find('a')
                        chapter_link = chapter_link_elem['href'] if chapter_link_elem else ''
                        chapter_title = chapter.find('span', class_='cap-titulo').text.strip() if chapter.find('span', class_='cap-titulo') else ''
                        scan_name = chapter.find('span', class_='scan-nome').text.strip() if chapter.find('span', class_='scan-nome') else ''
                        
                        chapter_data = {
                            "num-capitulo": chapter_num,
                            "cap-titulo": chapter_title,
                            "scan-nome": scan_name,
                            "link-capitulo": chapter_link
                        }
                        all_chapters_data.append(chapter_data)
                    except Exception as e:
                        print(f"Erro ao analisar capítulo: {e}")
                        continue
                
                # Se recebemos menos itens que o limite, podemos parar
                if len(chapter_items) < limit:
                    break
                    
            else:
                print(f"Falha ao obter capítulos no offset {offset}: {response.status_code}")
                break
        except Exception as e:
            print(f"Erro ao obter capítulos do mangá: {e}")
            break
    
    return all_chapters_html, all_chapters_data

def main():
    # Verifica se argumentos de linha de comando foram fornecidos
    if len(sys.argv) < 2:
        print("Uso: python manga.py {link} [{link} ...]")
        print("Exemplo: python manga.py https://sakuramangas.org/manga/one-piece/1 https://sakuramangas.org/manga/naruto/1")
        return
    
    # Obtém URLs de capítulos de mangá dos argumentos de linha de comando
    manga_urls = sys.argv[1:]
    
    for url in manga_urls:
        # Limpa URL (remove vírgulas ou espaços extras)
        url = url.strip().strip(',')
        if not url.startswith('http'):
            print(f"Pulando URL inválida: {url}")
            continue
            
        print(f"\nProcessando URL: {url}")
        
        # Extrai ID do mangá e token
        manga_info = extract_manga_info(url)
        if not manga_info:
            print(f"Pulando URL: {url}")
            continue
        
        manga_id = manga_info["manga_id"]
        token = manga_info["token"]
        
        # Obtém detalhes do mangá
        manga_details = get_manga_details(manga_id, token)
        if not manga_details:
            print(f"Não foi possível obter detalhes do mangá para {url}")
            continue
        
        # Cria estrutura de diretórios
        manga_title = manga_details.get("titulo", "Desconhecido")
        manga_dir = os.path.join("mangas", manga_title)
        create_directory("mangas")
        create_directory(manga_dir)
        
        # Salva informações do mangá
        manga_info_path = os.path.join(manga_dir, "manga_info.json")
        with open(manga_info_path, 'w', encoding='utf-8') as f:
            json.dump(manga_details, f, ensure_ascii=False, indent=4)
        print(f"Informações do mangá salvas em {manga_info_path}")
        
        # Obtém número do último capítulo
        last_chapter = int(manga_details.get("ultimo_capitulo", 1))
        
        # Obtém todos os capítulos
        chapters_html, chapters_data = get_manga_chapters(manga_id, token, last_chapter)
        
        # Salva HTML dos capítulos
        chapters_html_path = os.path.join(manga_dir, "manga_caps.html")
        with open(chapters_html_path, 'w', encoding='utf-8') as f:
            f.write(chapters_html)
        print(f"HTML dos capítulos salvo em {chapters_html_path}")
        
        # Salva JSON dos capítulos
        chapters_json_path = os.path.join(manga_dir, "links_caps.json")
        with open(chapters_json_path, 'w', encoding='utf-8') as f:
            json.dump(chapters_data, f, ensure_ascii=False, indent=4)
        print(f"JSON dos capítulos salvo em {chapters_json_path}")
        
        print(f"Processamento de {manga_title} concluído")

if __name__ == "__main__":
    main()