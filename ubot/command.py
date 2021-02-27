from types import FunctionType


class Command:
    def __init__(self, func: FunctionType, args: dict):
        self.module = func.__module__.split(".")[-1]
        self.function = func
        self.data = None

        self.pattern = args.get("pattern")
        self.simple_pattern = args.get("simple_pattern", False)
        self.raw_pattern = args.get("raw_pattern", False)
        self.pattern_extra = args.get("pattern_extra", "")
        self.extra = args.get("extra", None)
        self.help = args.get('help', None)
        self.prep_func = args.get("prep_func", None)

    async def prep(self, force=False):
        if (not self.data or force) and self.prep_func:
            self.data = await self.prep_func()
