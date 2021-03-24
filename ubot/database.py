import ujson
from peewee import (BooleanField, FloatField, IntegerField, Model,
                    SqliteDatabase, TextField)

DATABASE = SqliteDatabase("database.sqlite")


class BaseDB(Model):
    class Meta:
        database = DATABASE


class BlacklistedUser(BaseDB):
    user_id = IntegerField(unique=True, primary_key=True)


class SudoUser(BaseDB):
    user_id = IntegerField(unique=True, primary_key=True)


class Chat(BaseDB):
    chat_id = FloatField(unique=True, primary_key=True)
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

    # custom prefix functions
    def get_prefix(self, chat_id: int) -> str:
        return self.get_chat(chat_id).custom_prefix

    def set_prefix(self, chat_id: int, prefix: str):
        chat = self.get_chat(chat_id)
        chat.custom_prefix = prefix
        chat.save()

    # fun command functions
    def fun_enabled(self, chat_id: int) -> bool:
        return self.get_chat(chat_id).fun_enabled

    def set_fun(self, chat_id: int, enabled: bool):
        chat = self.get_chat(chat_id)
        chat.fun_enabled = enabled
        chat.save()

    # nsfw command functions
    def nsfw_enabled(self, chat_id: int) -> bool:
        return self.get_chat(chat_id).nsfw_enabled

    def set_nsfw(self, chat_id: int, enabled: bool):
        chat = self.get_chat(chat_id)
        chat.nsfw_enabled = enabled
        chat.save()

    # disable/enable command functions
    @staticmethod
    def _get_disabled_commands(chat: Chat) -> list:
        return ujson.loads(chat.disabled_commands)

    def disabled_commands(self, chat_id: int) -> list:
        return self._get_disabled_commands(self.get_chat(chat_id))

    def enable_command(self, chat_id: int, command: str):
        chat = self.get_chat(chat_id)
        disabled_commands = self._get_disabled_commands(chat)

        if command in disabled_commands:
            disabled_commands.remove(command)
            chat.disabled_commands = ujson.dumps(disabled_commands)
            chat.save()

    def disable_command(self, chat_id: int, command: str):
        chat = self.get_chat(chat_id)
        disabled_commands = self._get_disabled_commands(chat)

        if command not in disabled_commands:
            disabled_commands.append(command)
            chat.disabled_commands = ujson.dumps(disabled_commands)
            chat.save()

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
