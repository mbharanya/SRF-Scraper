import requests
import json
from bs4 import BeautifulSoup
import subprocess
import argparse
from urllib.parse import urlparse
from urllib.parse import parse_qs


def fetch_episode_urns(url, urns, next):
    parsed_url = urlparse(url)
    show_id = parse_qs(parsed_url.query)['id'][0]
    api_url = "https://www.srf.ch/play/v3/api/srf/production/videos-by-show-id"

    req = requests.get(api_url, {"showId": show_id, "next": next})
    episodes_json = json.loads(req.text)
    episode_data = episodes_json["data"]["data"]

    show_title = ""
    for episode in episode_data:
        # urn:srf:video:0e1bae7e-5a42-40af-84cc-3d97cc6c13be
        urns.append(episode["urn"])
        show_title = episode["show"]["title"]
    if "next" in episodes_json["data"]:
        print("next found")
        print(episodes_json["data"]["next"])
        fetch_episode_urns(url, urns, episodes_json["data"]["next"])

    return (urns, show_title)



def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)

    return json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents))


def download(show_name, urn, year):
    try:
        year = int(year)
        base_show_url = "https://www.srf.ch/play/tv/abc/video/abc?urn="
        url = base_show_url + urn
        data = get_ld_json(url)

        def download_with_ld_info():
            print(f"downloading {show_name} - {url}")
            filename = f"{show_name}-{data['uploadDate'].split('T', 1)[0]}-{data['name'].strip()}".replace(":", ".").replace("?", ".") + ".mp4"
            print(f"filename: {filename}")
            command = ["youtube-dl", "-o", f"{args.destination}{filename}", url]
            print(f"command: {command}")
            subprocess.Popen(command).communicate()

        # format: 2022-07-13T21:33:12+02:00
        if (year >= 1900 and data["uploadDate"][0:4] == str(year)):
            print(f"Download downloading {show_name} - {url} as it was released in {year}")
            download_with_ld_info()
        elif (year <= 0):
            download_with_ld_info()
    except Exception as e:
        print(e)

def download_full_show(url, year):
    (urns, show_title) = fetch_episode_urns(url, [], None)
    for urn in urns:
        download(show_title, urn, year)

def download_single_episode(url):
    parsed_url = urlparse(url)
    urn = parse_qs(parsed_url.query)['urn'][0]
    # https://il.srgssr.ch/integrationlayer/2.0/mediaComposition/byUrn/urn:srf:video:0e1bae7e-5a42-40af-84cc-3d97cc6c13be.json
    req = requests.get("https://il.srgssr.ch/integrationlayer/2.0/mediaComposition/byUrn/"+ urn)
    info_json = json.loads(req.text)
    download(info_json["show"]["title"], urn)

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument(
    '--url', help='Direct episode to crawl e.g. https://www.srf.ch/play/tv/ding-dong/video/in-der-evangelischen-wg-und-beim-handorgel-sammler?urn=urn:srf:video:0e1bae7e-5a42-40af-84cc-3d97cc6c13be')

parser.add_argument(
    '--show-url', help='Show url to download e.g. "https://www.srf.ch/play/tv/sendung/ding-dong?id=b558ca46-e1ce-442c-932d-571e5a6ad323"'
)
parser.add_argument(
    '--destination', default="/output/", help='Destination to save to (default docker /output/)'
)
parser.add_argument(
    '--year', default=-1, help='Download only episodes from given year'
)
args = parser.parse_args() 

banner = """
\033[1m\033[38;5;15m\033[48;5;196m................................................................................\033[0m
\033[1m\033[38;5;15m\033[48;5;196m................................................................................\033[0m
\033[1m\033[38;5;15m\033[48;5;196m...........,:loddxxxxxddo:...'codddddddddoolc:,........,codddddddddddddoc,......\033[0m
\033[1m\033[38;5;15m\033[48;5;196m.........;d0NWMMMMMMMMMMNd'..;0WMMMMMMMMMMMWWX0d:......cKWMMMMMMMMMMMMMWKc......\033[0m
\033[1m\033[38;5;15m\033[48;5;196m........c0WMMMWXKKKKKKKKOc...:0MMMMWXKKKKKNWMMMWKc.....cXMMMMNXXXXXXXXXXk:......\033[0m
\033[1m\033[38;5;15m\033[48;5;196m.......,kWMMMXd;,,,,,,,,,....:0MMMM0:,,,,,:dXMMMWk,....cKMMMWk:;;;;;;;;;,.......\033[0m
\033[1m\033[38;5;15m\033[48;5;196m.......,kWMMMXo,.............:0MMMMO;......;0MMMW0;....cXMMMWx'.................\033[0m
\033[1m\033[38;5;15m\033[48;5;196m.......'lXMMMMN0kxol:,'......:0MMMWO;...',:xXMMMWx,....cXMMMW0ollllllll:'.......\033[0m
\033[1m\033[38;5;15m\033[48;5;196m........'l0NMMMMMMMWNKOd:'...:0WMMMO;.'lO0NWMMMNk;.....cXMMMMMWWWWWWWWWKc.......\033[0m
\033[1m\033[38;5;15m\033[48;5;196m..........,cdk0XNWWMMMMWXd,..:0WMMMO;.;0WWMMMNkc'......cXMMMMWNNNNNNNNN0:.......\033[0m
\033[1m\033[38;5;15m\033[48;5;196m..............',:cokXWMMMNo'.:0WMMMO;.,kNWMMMNk;.......cXMMMWOc::::::::;'.......\033[0m
\033[1m\033[38;5;15m\033[48;5;196m...................'dNMMMWx'.:0MMMMO;..;cxNMMMWO:......cXMMMWx'.................\033[0m
\033[1m\033[38;5;15m\033[48;5;196m........,:cc::::::co0WMMMXl..;0WMMMO;....,xNMMMW0l'....cXMMMWx'.................\033[0m
\033[1m\033[38;5;15m\033[48;5;196m.......,xNWWNNNNNNWWMMMWXo,..;0WMMMO;.....'oXWMMWXo'...cXMMMWx'.................\033[0m
\033[1m\033[38;5;15m\033[48;5;196m.......;ONWWWWMWWWWWNKOd;'...;ONWWWk,......'oKNWWWXo'..cKWWWXd'.................\033[0m
\033[1m\033[38;5;15m\033[48;5;196m.......';cllloooollc:,'.......;cccc;........';cclcc;'..':cccc,..................\033[0m
\033[1m\033[38;5;15m\033[48;5;196m................................................................................\033[0m
\033[1m\033[38;5;15m\033[48;5;196m................................................................................\033[0m
"""
print(banner)

if(args.show_url):
    download_full_show(args.show_url, args.year)
elif(args.url):
    download_single_episode(args.url)
else:
    print("No url or sitemap specified")
    parser.print_help()