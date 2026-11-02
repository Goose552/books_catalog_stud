import asyncio

from library_catalog.external.openlibrary.client import OpenLibraryClient  # поправьте путь под свой проект


async def test():
    client = OpenLibraryClient()
    try:
        data = await client.search_by_isbn("9780132350884")
        print(f"Found: {data}")

        data = await client.search_by_title_author("Clean Code", "Robert Martin")
        print(f"Found: {data}")
    finally:
        await client.close()   # закроется, даже если выше было исключение


asyncio.run(test())