import requests
import json
from bs4 import BeautifulSoup
import subprocess
import argparse
from urllib.parse import urlparse
from urllib.parse import parse_qs


def fetch_episode_urns(url):
    parsed_url = urlparse(url)
    show_id = parse_qs(parsed_url.query)['id'][0]
    api_url = "https://www.srf.ch/play/v3/api/srf/production/videos-by-show-id?showId=$ID".replace("$ID", show_id)
    req = requests.get(api_url)
    episodes_json = json.loads(req.text)
    episode_data = episodes_json["data"]["data"]

    urns = []
    show_title = ""
    for episode in episode_data:
        # urn:srf:video:0e1bae7e-5a42-40af-84cc-3d97cc6c13be
        urns.append(episode["urn"])
        show_title = episode["show"]["title"]
    return (urns, show_title)


def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)

    return json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents))


def download(show_name, urn):
    try:
        base_show_url = "https://www.srf.ch/play/tv/abc/video/abc?urn="
        url = base_show_url + urn

        print(f"downloading {show_name} - {url}")
        data = get_ld_json(url)
        filename = f"{show_name}-{data['uploadDate'].split('T', 1)[0]}-{data['name'].strip()}".replace(":", ".") + ".mp4"
        print(f"filename: {filename}")
        command = ["wget", "--no-clobber", "-O", f"{args.destination}{filename}", data['contentUrl']]
        print(f"command: {command}")
        subprocess.Popen(command).communicate()
    except Exception as e:
        print(e)

def download_full_show(url):
    (urns, show_title) = fetch_episode_urns(url)
    for urn in urns:
        download(show_title, urn)

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
args = parser.parse_args() 
with open('logo.ansi.txt', 'r') as f:
    print(f.read())

if(args.show_url):
    download_full_show(args.show_url)
elif(args.url):
    download_single_episode(args.url)
else:
    print("No url or sitemap specified")
    parser.print_help()