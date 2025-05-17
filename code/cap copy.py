#!/usr/bin/env python3
import os
import json
import re
import requests
import time
import sys

def extract_meta_from_url(url):
    """
    Extract chapter_id and token from the URL or HTML content
    """
    try:
        # Try to fetch the page content first
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to access URL: {url}")
            return None, None
            
        content = response.text
        
        # Extract chapter_id and token using regex
        chapter_id_match = re.search(r'<meta chapter-id="(\d+)">', content)
        token_match = re.search(r'<meta token="([^"]+)">', content)
        
        if chapter_id_match and token_match:
            chapter_id = chapter_id_match.group(1)
            token = token_match.group(1)
            return chapter_id, token
        else:
            print("Could not find chapter_id and token in the page content")
            return None, None
            
    except Exception as e:
        print(f"Error accessing URL: {e}")
        return None, None

def get_chapter_info(chapter_id, token):
    """
    Get chapter information using the API
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
            print(f"Failed to get chapter info: Status code {response.status_code}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"Error getting chapter info: {e}")
        return None

def get_chapter_pages(chapter_id, token):
    """
    Get chapter pages using the API
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
            print(f"Failed to get chapter pages: Status code {response.status_code}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"Error getting chapter pages: {e}")
        return None

def download_images(image_urls, output_folder):
    """
    Download images from URLs and save them to the specified folder
    """
    pages_folder = os.path.join(output_folder, 'pages')
    if not os.path.exists(pages_folder):
        os.makedirs(pages_folder)
    
    base_url = 'https://sakuramangas.org'
    
    for img_url in image_urls:
        # Clean up the URL by removing '../' and ensuring it starts with '/'
        clean_url = img_url.replace('../', '')
        if not clean_url.startswith('/'):
            clean_url = '/' + clean_url
            
        full_url = base_url + clean_url
        
        # Extract the filename (e.g., '001.jpg')
        filename = os.path.basename(img_url)
        output_path = os.path.join(pages_folder, filename)
        
        print(f"Downloading {filename} from {full_url}")
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {filename}: Status code {response.status_code}")
                
            # Add a small delay to avoid overloading the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error downloading {filename}: {e}")

def download_chapter(url_or_chapter_id, token=None):
    """
    Download a manga chapter
    """
    # If a URL is provided, extract chapter_id and token
    if url_or_chapter_id.startswith('http'):
        print(f"Extracting metadata from URL: {url_or_chapter_id}")
        chapter_id, token = extract_meta_from_url(url_or_chapter_id)
        if not chapter_id or not token:
            print("Failed to extract chapter_id and token from URL")
            return False
    else:
        chapter_id = url_or_chapter_id
        if not token:
            print("Token is required when providing chapter_id directly")
            return False
    
    print(f"Using chapter_id: {chapter_id}, token: {token}")
    
    # Get chapter info
    chapter_info = get_chapter_info(chapter_id, token)
    if not chapter_info:
        print("Failed to get chapter info")
        return False
    
    # Get manga title and chapter number
    manga_title = chapter_info['manga']['titulo']
    chapter_number = chapter_info['capitulo']['numero']
    
    print(f"Manga: {manga_title}")
    print(f"Chapter: {chapter_number}")
    
    # Create folder structure
    mangas_folder = 'mangas'
    if not os.path.exists(mangas_folder):
        os.makedirs(mangas_folder)
    
    manga_folder = os.path.join(mangas_folder, manga_title)
    if not os.path.exists(manga_folder):
        os.makedirs(manga_folder)
    
    chapter_folder = os.path.join(manga_folder, str(chapter_number))
    if not os.path.exists(chapter_folder):
        os.makedirs(chapter_folder)
    
    # Save chapter info
    with open(os.path.join(chapter_folder, 'capitulo_info.json'), 'w', encoding='utf-8') as f:
        json.dump(chapter_info, f, ensure_ascii=False, indent=4)
    
    # Get chapter pages
    chapter_pages = get_chapter_pages(chapter_id, token)
    if not chapter_pages:
        print("Failed to get chapter pages")
        return False
    
    # Save chapter pages info
    with open(os.path.join(chapter_folder, 'capitulo_pages.json'), 'w', encoding='utf-8') as f:
        json.dump(chapter_pages, f, ensure_ascii=False, indent=4)
    
    # Download images
    print(f"Downloading {len(chapter_pages['imageUrls'])} images...")
    download_images(chapter_pages['imageUrls'], chapter_folder)
    
    print(f"Successfully downloaded Chapter {chapter_number} of {manga_title}")
    return True

def process_json_file(json_file_path):
    """
    Process a JSON file containing chapter links
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            chapters_data = json.load(f)
            
        # Process links in reverse order (from the bottom up)
        for chapter in reversed(chapters_data):
            link = chapter.get('link-capitulo')
            chapter_num = chapter.get('num-capitulo')
            chapter_title = chapter.get('cap-titulo')
            scan_name = chapter.get('scan-nome')
            
            if link:
                print(f"\nProcessing Chapter {chapter_num}: {chapter_title} (Scan: {scan_name})")
                download_chapter(link)
            else:
                print(f"Missing link for chapter {chapter_num}")
                
            # Add a small delay between chapters
            time.sleep(1)
            
        return True
    except Exception as e:
        print(f"Error processing JSON file {json_file_path}: {e}")
        return False

def main():
    # Check if any arguments were provided
    if len(sys.argv) < 2:
        print("Sakura Mangas Downloader")
        print("=" * 30)
        print("\nUsage:")
        print("  python cap.py link1,link2,link3")
        print("  python cap.py path/to/file1.json,path/to/file2.json")
        print("\nOr run interactively:")
        run_interactive()
        return
    
    # Process all arguments
    all_args = ','.join(sys.argv[1:])
    args_list = [arg.strip() for arg in all_args.split(',')]
    
    for arg in args_list:
        if arg.lower().endswith('.json'):
            print(f"\nProcessing JSON file: {arg}")
            process_json_file(arg)
        elif arg.startswith('http'):
            print(f"\nProcessing URL: {arg}")
            download_chapter(arg)
        else:
            print(f"Unrecognized argument: {arg}")

def run_interactive():
    """
    Run the script in interactive mode
    """
    while True:
        print("\nOptions:")
        print("1. Download using URL")
        print("2. Download using chapter_id and token")
        print("3. Process JSON file with chapter links")
        print("4. Exit")
        
        choice = input("Select an option (1-4): ")
        
        if choice == '1':
            url = input("Enter the chapter URL: ")
            download_chapter(url)
        elif choice == '2':
            chapter_id = input("Enter chapter_id: ")
            token = input("Enter token: ")
            download_chapter(chapter_id, token)
        elif choice == '3':
            json_path = input("Enter path to JSON file: ")
            process_json_file(json_path)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()