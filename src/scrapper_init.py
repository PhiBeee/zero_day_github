import pandas as pd
from scrapper import get_repo_details, make_safe_filename, download_file

def get_initial_downloads():
    df = pd.read_csv('../clustering/hac_clustering/hac_cluster_1.csv')

    repo_urls = df['repo_url']
    checked_urls = set({})
    
    for url in repo_urls:
        if url in checked_urls: continue
        checked_urls.add(url)

        # Turn the repo url into api url 
        url = url.replace('github', 'api.github', 1)
        url = url.replace('.com/', '.com/repos/')

        # Grab repo details 
        details = get_repo_details(url)

        content_url = url + '/contents/'
        
        files = recursively_get_files(content_url, ['.ts', '.js'])
        print(len(files))
        name_with_owner = details['full_name']

        for file, download_url in files:
            filename = make_safe_filename(f"{name_with_owner}-{file.split('/')[-1]}")
            download_file(download_url, filename)
            

def recursively_get_files(content_url, extensions):
    files = set({})
    # Get directory
    content = get_repo_details(content_url)
    for item in content:
        # Weird message response 
        if type(item) == str:
            continue
        filename = item['path']
        # Only grab the files we're interested in
        if filename[-3:] in extensions:
            print(f'{filename}, {item['download_url']}')
            files.add((filename, item['download_url']))
        elif item['type'] == 'dir':
            files |= recursively_get_files(f'{content_url}/{filename.split('/')[-1]}', extensions)
    return files

if __name__ == '__main__':
    get_initial_downloads()
