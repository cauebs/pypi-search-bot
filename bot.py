from pip.commands import SearchCommand
from telegram import InlineQueryResultArticle as InlineResult
from telegram import InputTextMessageContent, ParseMode
from telegram.ext import Updater, InlineQueryHandler
import logging
import re


INLINE_RESULT_LIMIT = 50


def escape_markdown(text):
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def search(query, args=[]):
    command = SearchCommand()
    options, _ = command.parse_args(args)
    return command.search(query, options)


def inlinequery(bot, update):
    query = update.inline_query.query
    if not query:
        return

    search_results = search(query)[:INLINE_RESULT_LIMIT]

    results = []
    for i, result in enumerate(search_results):
        name = escape_markdown(result['name'])
        desc = escape_markdown(result['summary'])
        version = escape_markdown(result['version'])
        url = f'https://pypi.python.org/pypi/{name}'

        message = InputTextMessageContent(f'[{name} {version}]({url})\n{desc}',
                                          parse_mode=ParseMode.MARKDOWN,
                                          disable_web_page_preview=True)

        results.append(InlineResult(id=i, title=name, description=desc,
                                    input_message_content=message))

    update.inline_query.answer(results)


def error_callback(bot, update, error):
    logging.error(error)


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s')

    updater = Updater(TOKEN)
    updater.dispatcher.add_error_handler(error_callback)
    updater.dispatcher.add_handler(InlineQueryHandler(inlinequery))

    updater.start_polling()
    updater.idle()
