import asyncio
import string

import aiohttp
from aiohttp import web

PATH_TO_HN = "news.ycombinator.com"
WORD_BORDERS = string.whitespace + r"""!"#$%'()*+,-.:;<=>?@[\]^`{|}~"""


def _modify_body(original_body: str) -> str:
    new_body, len_counter = "", 0
    i = 0
    len_original_body = len(original_body)
    while i < len_original_body:
        symbol = original_body[i]
        new_body += symbol
        if symbol == ">":
            looking_for_6_length_words = True
            len_counter = 0
        if symbol == "<":
            looking_for_6_length_words = False
        if (
            looking_for_6_length_words
            and symbol in string.ascii_letters
            and (i == 0 or original_body[i - len_counter - 1] in WORD_BORDERS)
        ):
            len_counter += 1
        else:
            len_counter = 0
        if len_counter == 6 and (
            i + 1 == len_original_body or original_body[i + 1] in WORD_BORDERS
        ):
            new_body += "™"
            len_counter = 0
        i += 1
    return new_body


async def handler(request):
    async with aiohttp.ClientSession() as session:
        async with getattr(session, request.method.lower())(
            f"https://{PATH_TO_HN}{request.path_qs}", headers=request.headers
        ) as resp:
            content = await resp.content.read()
            if resp.content_type == "text/html":
                kwargs = {"text": _modify_body(content.decode())}
            else:
                kwargs = {"body": content}
            return web.Response(
                status=resp.status, content_type=resp.content_type, **kwargs
            )


async def main():
    server = web.Server(handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

    print("======= Serving on http://localhost:8080/ ======")

    async with site._server:
        await site._server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("======= Server has been stoped ======")
