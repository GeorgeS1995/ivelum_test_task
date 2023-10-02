import asyncio
import string
import traceback
from asyncio import StreamReader, StreamWriter

# вынести в настройки

PATH_TO_HN = 'news.ycombinator.com'
BUFFER_SIZE = 65536
# BUFFER_SIZE = 100


async def _request_task(reader: StreamReader, writer: StreamWriter, modify_stream: bool = False) -> None:
    is_data_in_reader = True
    while is_data_in_reader:
        readed_data = await reader.read(BUFFER_SIZE)
        if modify_stream:
            try:
                looking_for_6_length_words, len_counter = False, 0
                data_to_sent = []
                for rune in readed_data:
                    symbol = chr(rune)
                    data_to_sent.append(rune)
                    if symbol == '>':
                        looking_for_6_length_words = True
                        len_counter = 0
                    if symbol == '<':
                        looking_for_6_length_words = False
                    if looking_for_6_length_words and symbol in string.ascii_letters:
                        len_counter += 1
                    if len_counter == 6:
                        data_to_sent.extend([r for r in '™'.encode()])
                        try:
                            print(bytes(data_to_sent[-7:-1]).decode(), [r for r in '™'.encode()], "suc")
                        except:
                            print(bytes(data_to_sent[-7:-1]), "err")
                        len_counter = 0
                data_to_sent = bytes(data_to_sent)
                print(data_to_sent, "full")
            except Exception as err:
                print(err, "t1")
        else:
            data_to_sent = readed_data
        print(data_to_sent)
        writer.write(data_to_sent)
        try:
            await writer.drain()
        except:
            print("1", data_to_sent, "1")
        if len(readed_data) < BUFFER_SIZE:
            is_data_in_reader = False


async def proxy_handler(proxy_reader: StreamReader, proxy_writer: StreamWriter) -> None:
    try:
        try:
            hn_reader, hn_writer = await asyncio.open_connection(PATH_TO_HN, 443, ssl=True)
        except Exception as err:
            print(err)
        await asyncio.gather(
            _request_task(proxy_reader, hn_writer), _request_task(hn_reader, proxy_writer, modify_stream=False)
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
