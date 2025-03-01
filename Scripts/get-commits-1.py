import requests
import json
import argparse
import time

# GitHub API token
token = "<Github_api_token_here>"

# Komut satırı argümanlarını alma
parser = argparse.ArgumentParser(description='Process GitHub commit URLs and extract Java file changes.')
parser.add_argument('url_file_path', type=str, help='Path to the file containing GitHub API URLs')
args = parser.parse_args()

# API isteği için gerekli headers
headers = {"Authorization": f"token {token}"}

# Sonuçları saklamak için liste
all_java_files = []

# URL'leri dosyadan oku
print(f"Reading URLs from {args.url_file_path}...")
with open(args.url_file_path, 'r') as url_file:
    urls = url_file.readlines()

# Her bir URL için işlem yap
for repo_url in urls:
    repo_url = repo_url.strip()
    if not repo_url:
        continue

    print(f"Processing URL: {repo_url}")
    
    response = requests.get(repo_url, headers=headers)
    if response.status_code == 403:
        print(f"API rate limit exceeded. Waiting for 60 minutes before retrying...")
        time.sleep(3600)  # 60 dakika bekle
        response = requests.get(repo_url, headers=headers)  # Tekrar dene
    if response.status_code != 200:
        print(f"Error fetching URL: {repo_url} (Status Code: {response.status_code})")
        continue

    commit_details = response.json()

    # Her bir dosya için işlem yapma
    for file in commit_details.get('files', []):
        filename = file['filename']
        
        # Sadece .java dosyalarını işle ve deletions değeri 0 olmayanları seç
        if filename.endswith('.java') and file['deletions'] > 0:
            print(f"Processing Java file: {filename}")

            patch = file.get('patch', '')
            
            # deleted_lines kısmını al
            deleted_lines = []
            lines = patch.split('\n')
            for line in lines:
                if line.startswith('-'):
                    deleted_lines.append(line[1:])  # - işaretini kaldırarak deleted_lines içerisine ekle
            
            # Dosya bilgilerini JSON formatında sakla
            java_file_info = {
                "filename": filename,
                "contents_url": file['contents_url'],
                "deleted_lines": deleted_lines,
                "status": file['status'],
                "additions": file['additions'],
                "deletions": file['deletions'],
                "changes": file['changes']
            }
            all_java_files.append(java_file_info)
        elif filename.endswith('.java'):
            print(f"No deletions in Java file: {filename}")

# Sonuçları JSON dosyasına kaydet
output_file = 'all_java_files.json'
print(f"Saving results to {output_file}...")
with open(output_file, 'w') as json_file:
    json.dump(all_java_files, json_file, indent=4)

print("Processing complete, results saved to 'all_java_files.json'.")
