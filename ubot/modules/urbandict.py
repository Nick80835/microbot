import io
from re import findall
from urllib.parse import quote_plus

from ubot import ldr

UD_QUERY_URL = 'http://api.urbandictionary.com/v0/define'
UD_RANDOM_URL = 'http://api.urbandictionary.com/v0/random'
UD_TERM_URL = 'https://www.urbandictionary.com/define.php?term={0}'
UD_AUTHOR_URL = 'https://www.urbandictionary.com/author.php?author={0}'


@ldr.add("ud", help="Fetches words from Urban Dictionary, takes an optional word as an argument.")
async def urban_dict(event):
    udquery = event.args

    if udquery:
        params = {'term': udquery}
        url = UD_QUERY_URL
    else:
        params = None
        url = UD_RANDOM_URL

    async with ldr.aioclient.get(url, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    if response['list']:
        response_word = response['list'][0]
    else:
        await event.reply(f"No results for query: **{udquery}**")
        return

    word = response_word['word']
    author = response_word['author']
    definition = response_word['definition']
    example = response_word['example']

    for match in findall(r'\[(.*?)\]', definition):
        definition = definition.replace(f"[{match}]", f'<a href="{UD_TERM_URL.format(quote_plus(match))}">{match}</a>')

    if example:
        for match in findall(r'\[(.*?)\]', example):
            example = example.replace(f"[{match}]", f'<a href="{UD_TERM_URL.format(quote_plus(match))}">{match}</a>')

        full_definition = f'<b>{word}</b> by <a href="{UD_AUTHOR_URL.format(quote_plus(author))}">{author}</a>: <i>{definition}</i>\n\n<b>Example</b>: <i>{example}</i>'
    else:
        full_definition = f'<b>{word}</b> by <a href="{UD_AUTHOR_URL.format(quote_plus(author))}">{author}</a>: <i>{definition}</i>'

    if len(full_definition) >= 4096:
        if example:
            bare_definition = f"{word}: {definition}\n\nExample: {example}"
        else:
            bare_definition = f"{word}: {definition}"

        file_io = io.BytesIO()
        file_io.write(bytes(bare_definition.replace("[", "").replace("]", "").encode('utf-8')))
        file_io.name = f"definition of {word}.txt"
        await event.reply("`Output was too large, sent it as a file.`", file=file_io)
        return

    await event.reply(full_definition, parse_mode="html", link_preview=False)


@ldr.add_inline_article("ud", default="ud", parse_mode="html", link_preview=False)
async def urban_dict_inline(event):
    udquery = event.args

    if udquery:
        params = {'term': udquery}
        url = UD_QUERY_URL
    else:
        params = None
        url = UD_RANDOM_URL

    async with ldr.aioclient.get(url, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            return

    if response['list']:
        response_words = response['list'][:10]
    else:
        return

    definition_list = []

    for response_word in response_words:
        word = response_word['word']
        author = response_word['author']
        definition = response_word['definition']
        clean_definition = definition.replace("[", "").replace("]", "")
        example = response_word['example']

        for match in findall(r'\[(.*?)\]', definition):
            definition = definition.replace(f"[{match}]", f'<a href="{UD_TERM_URL.format(quote_plus(match))}">{match}</a>')

        if example:
            for match in findall(r'\[(.*?)\]', example):
                example = example.replace(f"[{match}]", f'<a href="{UD_TERM_URL.format(quote_plus(match))}">{match}</a>')

            full_definition = f'<b>{word}</b> by <a href="{UD_AUTHOR_URL.format(quote_plus(author))}">{author}</a>: <i>{definition}</i>\n\n<b>Example</b>: <i>{example}</i>'
        else:
            full_definition = f'<b>{word}</b> by <a href="{UD_AUTHOR_URL.format(quote_plus(author))}">{author}</a>: <i>{definition}</i>'

        this_definition = {"title": word, "description": clean_definition, "text": full_definition}

        definition_list.append(this_definition)

    return definition_list
