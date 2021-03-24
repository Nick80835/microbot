import ujson
from peewee import (BigIntegerField, BooleanField, Model, SqliteDatabase,
                    TextField)

DATABASE = SqliteDatabase("database.sqlite")


class BaseDB(Model):
    class Meta:
        database = DATABASE


class BlacklistedUser(BaseDB):
    user_id = BigIntegerField(unique=True, primary_key=True)


class SudoUser(BaseDB):
    user_id = BigIntegerField(unique=True, primary_key=True)


class Chat(BaseDB):
    chat_id = BigIntegerField(unique=True, primary_key=True)
    fun_enabled = BooleanField(default=True)
    nsfw_enabled = BooleanField(default=True)
    disabled_commands = TextField(default="[]")
    custom_prefix = TextField(default="/")


DATABASE.connect()
DATABASE.create_tables([
    Chat,
    BlacklistedUser,
    SudoUser
])


class ChatWrapper():
    def __init__(self, chat: Chat):
        self.chat = chat

    # custom prefix functions
    def get_prefix(self) -> str:
        return self.chat.custom_prefix

    def set_prefix(self, prefix: str):
        self.chat.custom_prefix = prefix
        self.chat.save()

    # fun command functions
    def fun_enabled(self) -> bool:
        return self.chat.fun_enabled

    def set_fun(self, enabled: bool):
        self.chat.fun_enabled = enabled
        self.chat.save()

    # nsfw command functions
    def nsfw_enabled(self) -> bool:
        return self.chat.nsfw_enabled

    def set_nsfw(self, enabled: bool):
        self.chat.nsfw_enabled = enabled
        self.chat.save()

    # disable/enable command functions
    @staticmethod
    def _get_disabled_commands(chat: Chat) -> list:
        return ujson.loads(chat.disabled_commands)

    def disabled_commands(self) -> list:
        return self._get_disabled_commands(self.chat)

    def enable_command(self, command: str):
        disabled_commands = self._get_disabled_commands(self.chat)

        if command in disabled_commands:
            disabled_commands.remove(command)
            self.chat.disabled_commands = ujson.dumps(disabled_commands)
            self.chat.save()

    def disable_command(self, command: str):
        disabled_commands = self._get_disabled_commands(self.chat)

        if command not in disabled_commands:
            disabled_commands.append(command)
            self.chat.disabled_commands = ujson.dumps(disabled_commands)
            self.chat.save()


class Database():
    db = DATABASE

    # returns a Chat row
    @staticmethod
    def get_chat(chat_id: int) -> Chat:
        try:
            return Chat.get_by_id(chat_id)
        except Chat.DoesNotExist:
            chat = Chat.create(chat_id=chat_id)
            chat.save()
            return chat

    # sudo functions
    @staticmethod
    def get_sudo_list() -> list:
        try:
            return [user.user_id for user in SudoUser.select().execute()]
        except SudoUser.DoesNotExist:
            return []

    @staticmethod
    def sudo_user(user_id: int):
        SudoUser.create(user_id=user_id)

    @staticmethod
    def unsudo_user(user_id: int):
        SudoUser.delete_by_id(user_id)

    #blacklist functions
    @staticmethod
    def get_blacklist_list() -> list:
        try:
            return [user.user_id for user in BlacklistedUser.select().execute()]
        except BlacklistedUser.DoesNotExist:
            return []

    @staticmethod
    def blacklist_user(user_id: int):
        BlacklistedUser.create(user_id=user_id)

    @staticmethod
    def unblacklist_user(user_id: int):
        BlacklistedUser.delete_by_id(user_id)
