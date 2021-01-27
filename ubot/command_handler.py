from re import escape, search
from traceback import print_exc

from telethon import events


class CommandHandler():
    pattern_template = "(?is)^({0})({1}){2}(?: |$)(.*)"
    simple_pattern_template = "(?is)^({0}){1}(?: |$|_)(.*)"
    raw_pattern_template = "(?is){0}"

    outgoing_commands = []

    def __init__(self, client, settings):
        self.settings = settings
        client.add_event_handler(self.handle_outgoing, events.NewMessage(outgoing=True, forwards=False, func=lambda e: not e.via_bot_id and e.raw_text))

    async def handle_outgoing(self, event):
        prefix = "|".join([escape(i) for i in (self.settings.get_list("cmd_prefix") or ['.'])])

        for command in self.outgoing_commands:
            if command.simple_pattern:
                pattern_match = search(self.simple_pattern_template.format(command.pattern, command.pattern_extra), event.raw_text)
            elif command.raw_pattern:
                pattern_match = search(self.raw_pattern_template.format(command.pattern + command.pattern_extra), event.raw_text)
            else:
                pattern_match = search(self.pattern_template.format(prefix, command.pattern, command.pattern_extra), event.raw_text)

            if pattern_match:
                if command.raw_pattern:
                    event.command = command.pattern
                else:
                    event.command = pattern_match.groups()[1]
                    event.args = pattern_match.groups()[-1].strip()

                    if command.simple_pattern:
                        event.other_args = pattern_match.groups()[1:-1]
                    else:
                        event.other_args = pattern_match.groups()[2:-1]

                event.pattern_match = pattern_match
                event.extra = command.extra
                event.object = command

                try:
                    await command.function(event)
                except Exception as exception:
                    await event.reply(f"`An error occurred in {command.function.__name__}: {exception}`")
                    print_exc()
