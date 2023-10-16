import rapidjson
from peewee import (BigIntegerField, BooleanField, IntegrityError, Model,
                    SqliteDatabase, TextField)

CHAT_WRAPPER_CACHE_LIMIT = 200
DATABASE = SqliteDatabase("database.sqlite", pragmas={
    "journal_mode": "wal",
    "cache_size": -1024 * 16}
)


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
    spoiler_nsfw = BooleanField(default=False)
    disabled_commands = TextField(default="[]")
    custom_prefix = TextField(default="/")
    lang = TextField(default="en")
    modmode_enabled = BooleanField(default=False)


DATABASE.connect()
DATABASE.create_tables([
    Chat,
    BlacklistedUser,
    SudoUser
])


class ChatWrapper():
    def __init__(self, chat: Chat):
        self.disabled_commands: list = rapidjson.loads(chat.disabled_commands)
        self.chat = chat

    # custom prefix functions
    @property
    def prefix(self) -> str:
        return self.chat.custom_prefix

    @prefix.setter
    def prefix(self, prefix: str):
        self.chat.custom_prefix = prefix
        self.chat.save()

    # language functions
    @property
    def lang(self) -> str:
        return self.chat.lang

    @lang.setter
    def lang(self, lang: str):
        self.chat.lang = lang
        self.chat.save()

    # modmode command functions
    @property
    def modmode_enabled(self) -> bool:
        return self.chat.modmode_enabled

    @modmode_enabled.setter
    def modmode_enabled(self, enabled: bool):
        self.chat.modmode_enabled = enabled
        self.chat.save()

    # fun command functions
    @property
    def fun_enabled(self) -> bool:
        return self.chat.fun_enabled

    @fun_enabled.setter
    def fun_enabled(self, enabled: bool):
        self.chat.fun_enabled = enabled
        self.chat.save()

    # nsfw command functions
    @property
    def nsfw_enabled(self) -> bool:
        return self.chat.nsfw_enabled

    @nsfw_enabled.setter
    def nsfw_enabled(self, enabled: bool):
        self.chat.nsfw_enabled = enabled
        self.chat.save()

    @property
    def spoiler_nsfw(self) -> bool:
        return self.chat.spoiler_nsfw

    @spoiler_nsfw.setter
    def spoiler_nsfw(self, enabled: bool):
        self.chat.spoiler_nsfw = enabled
        self.chat.save()

    # disable/enable command functions
    def enable_command(self, command: str):
        if command in self.disabled_commands:
            self.disabled_commands.remove(command)
            self.chat.disabled_commands = rapidjson.dumps(self.disabled_commands)
            self.chat.save()

    def disable_command(self, command: str):
        if command not in self.disabled_commands:
            self.disabled_commands.append(command)
            self.chat.disabled_commands = rapidjson.dumps(self.disabled_commands)
            self.chat.save()


class Database():
    cached_chat_wrappers = {}
    chat_table = Chat
    blacklisted_user_table = BlacklistedUser
    sudo_user_table = SudoUser
    db = DATABASE

    try:
        blacklisted_users = [user.user_id for user in BlacklistedUser.select().execute()]
    except BlacklistedUser.DoesNotExist:
        blacklisted_users = []

    try:
        sudo_users = [user.user_id for user in SudoUser.select().execute()]
    except SudoUser.DoesNotExist:
        sudo_users = []

    # returns a ChatWrapper for a given chat ID
    def get_chat(self, chat_id: int) -> ChatWrapper:
        if chat_id in self.cached_chat_wrappers:
            # new events raise wrappers back to the top
            self.cached_chat_wrappers[chat_id] = self.cached_chat_wrappers.pop(chat_id)
            return self.cached_chat_wrappers[chat_id]

        try:
            chat = Chat.get_by_id(chat_id)
        except Chat.DoesNotExist:
            chat = Chat.create(chat_id=chat_id)
            chat.save()

        while len(self.cached_chat_wrappers) >= CHAT_WRAPPER_CACHE_LIMIT:
            self.cached_chat_wrappers.pop(next(iter(self.cached_chat_wrappers)))

        self.cached_chat_wrappers[chat_id] = (chat_db := ChatWrapper(chat))
        return chat_db

    # sudo functions
    def sudo_user(self, user_id: int):
        try:
            SudoUser.create(user_id=user_id)

            if user_id not in self.sudo_users:
                self.sudo_users.append(user_id)
        except IntegrityError:
            pass

    def unsudo_user(self, user_id: int):
        SudoUser.delete_by_id(user_id)

        if user_id in self.sudo_users:
            self.sudo_users.remove(user_id)

    # blacklist functions
    def blacklist_user(self, user_id: int):
        try:
            BlacklistedUser.create(user_id=user_id)

            if user_id not in self.blacklisted_users:
                self.blacklisted_users.append(user_id)
        except IntegrityError:
            pass

    def unblacklist_user(self, user_id: int):
        BlacklistedUser.delete_by_id(user_id)

        if user_id in self.blacklisted_users:
            self.blacklisted_users.remove(user_id)
