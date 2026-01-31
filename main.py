import argparse as cli
import requests as r
from pathlib import Path
from alive_progress import alive_bar

def download_image_url(from_url: str, to: Path):
    if to is None: to = Path('.')
    image_path = to / from_url.split('/')[-1]
    if image_path.exists():
        print(f"Image {image_path} exists, skipping...")
        return
    image_object = r.get(from_url,stream=True)
    if image_object.status_code == 200:
        with open(image_path, 'wb') as f:
            with alive_bar(len(image_object.request.body if image_object.request.body else [])) as bar:
                for chunk in image_object:
                    f.write(chunk)
                    bar()
        
def download_pictures(pictures, parser):
     for picture in pictures['data']:
        print(f"[Found] ID: {picture['id']} VIEWS: {picture['views']}\n")
        print("Downloading...")
        download_image_url(picture['path'],parser.output)

def search_by_name(name: str, parser, page = 1, quantity = 0):
    search = r.get("https://wallhaven.cc/api/v1/search",params={"q": name,"categories": "111", "purity": "100", "page": page})
    parsed = search.json()
    if (parser.max is not None and parser.max <= quantity + len(parsed['data'])):
        limit = True
        max_data = parser.max - quantity
        parsed['data'] = parsed['data'][:max_data]
    return parsed


def main():
    print("Hello from wallhaven-downloader!")
    parser = cli.ArgumentParser()
    parser.add_argument("topics",nargs="+")
    parser.add_argument('-m',"--max",type=int, required=False)
    parser.add_argument('-o',"--output",type=Path, required=False)
    
    parsed_args = parser.parse_args()
    quantity = 0
    for _, value in parsed_args._get_kwargs():
        page = 1
        if value is not None:
            while quantity < parsed_args.max:
                pictures = search_by_name(value,parsed_args,page,quantity)
                download_pictures(pictures,parsed_args)
                if page >= pictures['meta']['last_page']:
                    break
                page += 1
                quantity += len(pictures['data'])

if __name__ == "__main__":
    main()
