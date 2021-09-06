"""HTTP utilities."""
from typing import IO

import requests
from tqdm import tqdm


def download(url: str, description: str, handle: IO[bytes]) -> None:
    """Download a given URL to a given stream and show a progressbar.

    :param url: URL to download
    :param description: description to show in the progressbar
    :param handle: stream to write to
    """
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get("Content-Length", 0))
    block_size = 1024
    with tqdm(
        desc=description,
        total=total_size_in_bytes,
        unit="iB",
        unit_scale=True,
    ) as progress_bar:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            handle.write(data)
