import argparse
import asyncio
from collections.abc import Awaitable, Iterable
from pathlib import Path

from monster_siren import MonsterSiren


async def run_concurrent_tasks[T](
    tasks: Iterable[Awaitable[T]], n: int, return_exceptions: bool = False
) -> list:
    async def semaphore_wrapper(task: Awaitable[T]) -> T:
        async with semaphore:
            return await task

    semaphore = asyncio.Semaphore(n)
    return await asyncio.gather(
        *(semaphore_wrapper(task) for task in tasks),
        return_exceptions=return_exceptions,
    )


async def download_all(
    folder: Path = Path("Songs"),
    file_name_format: str = "{cid}_{song_name}{suffix}",
    skip_existing: bool = True,
    concurrent_tasks: int = 2,
) -> None:
    monster_siren = MonsterSiren()

    # albums = await monster_siren.albums()
    # album_data_tasks = [
    #     monster_siren.album_data(album["cid"])
    #     for album in albums["data"]
    # ]

    songs = await monster_siren.songs()
    song_data_tasks = [
        monster_siren.download_song_by_cid_and_save(
            song["cid"], folder, file_name_format, skip_existing
        )
        for song in songs["data"]["list"]
    ]
    await run_concurrent_tasks(song_data_tasks, concurrent_tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download songs from Monster Siren.")
    parser.add_argument(
        "-f",
        "--folder",
        type=Path,
        default=Path("Songs"),
        help="Folder to save the downloaded songs.",
    )
    parser.add_argument(
        "-n",
        "--name-format",
        type=str,
        default="{cid}_{song_name}{suffix}",
        help="File name format.",
    )
    parser.add_argument(
        "-s",
        "--overwrite-existing",
        action="store_true",
        help="Overwrite existing files (otherwise skip existing).",
    )
    parser.add_argument(
        "-c",
        "--concurrent-tasks",
        type=int,
        default=2,
        help="Number of concurrent tasks.",
    )
    args = parser.parse_args()
    folder = args.folder
    file_name_format = args.name_format
    skip_existing = not args.overwrite_existing
    concurrent_tasks = args.concurrent_tasks

    folder.mkdir(parents=True, exist_ok=True)
    asyncio.run(
        download_all(
            folder=folder,
            file_name_format=file_name_format,
            skip_existing=skip_existing,
            concurrent_tasks=concurrent_tasks,
        )
    )
