import requests
import re
import os
import sys
import subprocess

from bs4 import BeautifulSoup

HOST = "https://github.com"
REPO = "AChep/keyguard-app"
RELEASE_URL = f"{HOST}/{REPO}/releases/latest"


def get_latest_release_tag():
    response = requests.get(RELEASE_URL)
    return re.match(r".*tag/([\w]+).*", response.url).group(1)


tag = get_latest_release_tag()
apk_filename = f"repo/Keyguard-{tag}.apk"

# If the file already exists, then there is no
# need to download the file. We assume that the
# files are immutable.
if os.path.exists(apk_filename):
    sys.exit(0)

#
# Download the latest .apk from GitHub
#

assets_url = f"{HOST}/{REPO}/releases/expanded_assets/{tag}"
assets_response = requests.get(assets_url)
assets_soup = BeautifulSoup(
    assets_response.content,
    features="html.parser"
)

assets_urls = [el['href'] for el in assets_soup.select('a[href]')]
assets_apk_url = next(
    filter(
        lambda url: url.endswith('/androidApp-none-release.apk'),
        assets_urls
    ),
    None
)
if not assets_apk_url:
    raise Exception("Failed to find a url to the latest .apk file!")
assets_apk_url = f"{HOST}{assets_apk_url}"

apk_response = requests.get(assets_apk_url)
with open(apk_filename, mode="wb") as file:
    file.write(apk_response.content)

#
# Update repository
#

subprocess.run(["fdroid", "update"], check=True)
