import asyncio
import traceback
import urllib.request
from asyncio import StreamReader, StreamWriter

# вынести в настройки

PATH_TO_HN = 'news.ycombinator.com'
# BUFFER_SIZE = 65536
BUFFER_SIZE = 100


async def _request_to_target(reader: StreamReader, writer: StreamWriter):
    while True:
        readed_data = await reader.read(BUFFER_SIZE)
        writer.write(readed_data)
        if len(readed_data) < BUFFER_SIZE:
            return

async def _request_to_client(reader: StreamReader, writer: StreamWriter):
    total_data = b""
    while True:
        readed_data = await reader.read(BUFFER_SIZE)
        writer.write(readed_data)
        total_data += readed_data
        if len(readed_data) < BUFFER_SIZE:
            break
    print(total_data)



async def proxy_handler(proxy_reader: StreamReader, proxy_writer: StreamWriter) -> None:
    try:
        try:
            hn_reader, hn_writer = await asyncio.open_connection(PATH_TO_HN, 443, ssl=True)
        except Exception as err:
            print(err)
        await asyncio.gather(
            _request_to_target(proxy_reader, hn_writer), _request_to_client(hn_reader, proxy_writer)
        )
        await asyncio.sleep(1)
        hn_writer.close()
        await hn_writer.wait_closed()
        proxy_writer.close()
        await proxy_writer.wait_closed()
    except Exception as err:
        print(err, "t2")
        traceback.print_exc()


async def start_server():
    server = await asyncio.start_server(
        proxy_handler, port=80)

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(start_server())
