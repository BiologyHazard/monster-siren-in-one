import re
import reprlib
import urllib.parse
from typing import BinaryIO
from pathlib import Path
from typing import Any

from httpx import AsyncClient

from log import logger

base_url = "https://monster-siren.hypergryph.com"
albums_url = f"{base_url}/api/albums"  # 专辑列表
songs_url = f"{base_url}/api/songs"  # 乐曲列表
album_url = f"{base_url}/api/album"  # 专辑详情，例如 https://monster-siren.hypergryph.com/api/album/7766/data
song_url = f"{base_url}/api/song"  # 乐曲详情，例如 https://monster-siren.hypergryph.com/api/song/048794


def make_valid_filename(s: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', '_', s)


class MonsterSiren:
    def __init__(self) -> None:
        self.client = AsyncClient()

    async def _request(self,
                       method: str,
                       url: str,
                       **kwargs) -> dict[str, Any]:
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        obj = response.json()
        logger.debug(f'{method.upper()} {url} returned {reprlib.repr(obj)}')

        return obj

    async def download_file(self, url: str, f: BinaryIO) -> None:
        async with self.client.stream("GET", url) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                f.write(chunk)

    async def albums(self) -> dict[str, Any]:
        return await self._request("GET", albums_url)

    async def songs(self) -> dict[str, Any]:
        return await self._request("GET", songs_url)

    async def album_data(self, album_id: str) -> dict[str, Any]:
        url = f"{album_url}/{album_id}/data"
        return await self._request("GET", url)

    async def song_data(self, song_id: str) -> dict[str, Any]:
        url = f"{song_url}/{song_id}"
        return await self._request("GET", url)

    async def download_song_by_cid_and_save(
        self,
        song_id: str,
        folder: Path,
        file_name_format: str,
        skip_existing: bool,
    ) -> None:
        song_data = await self.song_data(song_id)
        cid = song_data["data"]["cid"]
        song_name = song_data["data"]["name"]
        source_url = song_data["data"]["sourceUrl"]
        lyric_url = song_data["data"]["lyricUrl"]
        mv_url = song_data["data"]["mvUrl"]
        mv_cover_url = song_data["data"]["mvCoverUrl"]
        assert mv_url is None and mv_cover_url is None

        parsed_url = urllib.parse.urlparse(source_url)
        suffix = Path(parsed_url.path).suffix
        original_file_name = Path(parsed_url.path).name
        file_name = file_name_format.format(
            cid=cid,
            song_name=song_name,
            suffix=suffix,
            original_file_name=original_file_name,
        )
        file_name = make_valid_filename(file_name)
        path = folder / file_name

        if skip_existing and path.exists():
            logger.info(f"File {path} already exists, SKIPPING.")
            return

        with open(path, "wb") as f:
            await self.download_file(source_url, f)
        logger.info(f"Downloaded {song_name} ({cid}) to {path} successfully.")
