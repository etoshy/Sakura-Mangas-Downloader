import os
import re
import json
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def extract_manga_info(url):
    """Extract manga_id and token from a manga chapter URL"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Extract manga-id and token using regex
            manga_id_match = re.search(r'<meta\s+manga-id="(\d+)">', response.text)
            token_match = re.search(r'<meta\s+token="([^"]+)">', response.text)
            
            if manga_id_match and token_match:
                manga_id = manga_id_match.group(1)
                token = token_match.group(1)
                return {"manga_id": manga_id, "token": token}
            else:
                # Alternative method: try to extract from URL
                parsed_url = urlparse(url)
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) >= 2:
                    obra_name = path_parts[-2]
                    print(f"Couldn't find metadata tags, but found obra name: {obra_name}")
                    # You might need to implement a way to get manga_id from obra name
                
                print("Couldn't extract manga_id and token from the page")
                return None
        else:
            print(f"Failed to access URL: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error extracting manga info: {e}")
        return None

def get_manga_details(manga_id, token):
    """Get manga details from API"""
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
            print(f"Failed to get manga details: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting manga details: {e}")
        return None

def get_manga_chapters(manga_id, token, last_chapter):
    """Get all manga chapters"""
    url = 'https://sakuramangas.org/dist/sakura/models/manga/manga_capitulos.php'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    all_chapters_html = ""
    all_chapters_data = []
    
    # Calculate how many requests we need to make
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
                
                # Parse the HTML to extract chapter information
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
                        print(f"Error parsing chapter: {e}")
                        continue
                
                # If we got fewer items than the limit, we can stop
                if len(chapter_items) < limit:
                    break
                    
            else:
                print(f"Failed to get chapters at offset {offset}: {response.status_code}")
                break
        except Exception as e:
            print(f"Error getting manga chapters: {e}")
            break
    
    return all_chapters_html, all_chapters_data

def main():
    # Check if command line arguments were provided
    if len(sys.argv) < 2:
        print("Usage: python manga.py {link} [{link} ...]")
        print("Example: python manga.py https://sakuramangas.org/manga/one-piece/1 https://sakuramangas.org/manga/naruto/1")
        return
    
    # Get manga chapter URLs from command line arguments
    manga_urls = sys.argv[1:]
    
    for url in manga_urls:
        # Clean up URL (remove any extra commas or spaces)
        url = url.strip().strip(',')
        if not url.startswith('http'):
            print(f"Skipping invalid URL: {url}")
            continue
            
        print(f"\nProcessing URL: {url}")
        
        # Extract manga ID and token
        manga_info = extract_manga_info(url)
        if not manga_info:
            print(f"Skipping URL: {url}")
            continue
        
        manga_id = manga_info["manga_id"]
        token = manga_info["token"]
        
        # Get manga details
        manga_details = get_manga_details(manga_id, token)
        if not manga_details:
            print(f"Couldn't get manga details for {url}")
            continue
        
        # Create directory structure
        manga_title = manga_details.get("titulo", "Unknown")
        manga_dir = os.path.join("mangas", manga_title)
        create_directory("mangas")
        create_directory(manga_dir)
        
        # Save manga info
        manga_info_path = os.path.join(manga_dir, "manga_info.json")
        with open(manga_info_path, 'w', encoding='utf-8') as f:
            json.dump(manga_details, f, ensure_ascii=False, indent=4)
        print(f"Saved manga info to {manga_info_path}")
        
        # Get last chapter number
        last_chapter = int(manga_details.get("ultimo_capitulo", 1))
        
        # Get all chapters
        chapters_html, chapters_data = get_manga_chapters(manga_id, token, last_chapter)
        
        # Save chapters HTML
        chapters_html_path = os.path.join(manga_dir, "manga_caps.html")
        with open(chapters_html_path, 'w', encoding='utf-8') as f:
            f.write(chapters_html)
        print(f"Saved chapters HTML to {chapters_html_path}")
        
        # Save chapters JSON
        chapters_json_path = os.path.join(manga_dir, "links_caps.json")
        with open(chapters_json_path, 'w', encoding='utf-8') as f:
            json.dump(chapters_data, f, ensure_ascii=False, indent=4)
        print(f"Saved chapters JSON to {chapters_json_path}")
        
        print(f"Finished processing {manga_title}")

if __name__ == "__main__":
    main()