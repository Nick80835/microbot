from types import FunctionType


class Command:
    def __init__(self, func: FunctionType, args: dict):
        self.module = func.__module__.split(".")[-1]
        self.function = func
        self.data = {}

        self.pattern = args.get("pattern")
        self.simple_pattern = args.get("simple_pattern", False)
        self.raw_pattern = args.get("raw_pattern", False)
        self.pattern_extra = args.get("pattern_extra", "")
        self.extra = args.get("extra", None)
        self.help = args.get("help", None)
        self.hide_help = args.get("hide_help", False)
        self.owner = args.get("owner", False)
        self.sudo = args.get("sudo", False)
        self.admin = args.get("admin", False)
        self.nsfw = args.get("nsfw", False)
        self.nsfw_warning = args.get("nsfw_warning", None)
        self.pass_nsfw = args.get("pass_nsfw", False)
        self.locking = args.get("locking", False)
        self.lock_reason = None
        self.user_locking = args.get("userlocking", False)
        self.locked_users = []
        self.chance = args.get("chance", None)
        self.fun = args.get("fun", False)
        self.not_disableable = args.get("no_disable", False) or self.owner or self.sudo or self.admin
        self.no_private = args.get("no_private", False)
        self.silent_bail = args.get("silent_bail", False)


class InlinePhotoCommand:
    def __init__(self, func: FunctionType, args: dict):
        self.module = func.__module__.split(".")[-1]
        self.function = func

        self.pattern = args.get("pattern")
        self.pattern_extra = args.get("pattern_extra", "")
        self.default = args.get("default", None)
        self.extra = args.get("extra", None)
        self.parse_mode = args.get("parse_mode", "md")


class InlineArticleCommand:
    def __init__(self, func: FunctionType, args: dict):
        self.module = func.__module__.split(".")[-1]
        self.function = func

        self.pattern = args.get("pattern")
        self.pattern_extra = args.get("pattern_extra", "")
        self.default = args.get("default", None)
        self.extra = args.get("extra", None)
        self.link_preview = args.get("link_preview", True)
        self.parse_mode = args.get("parse_mode", "md")


class CallbackQueryCommand:
    def __init__(self, func: FunctionType, args: dict):
        self.module = func.__module__.split(".")[-1]
        self.function = func
        self.data = {}

        self.data_id = args.get("data_id")
        self.extra = args.get("extra", None)
