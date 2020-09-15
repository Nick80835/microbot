# SPDX-License-Identifier: GPL-2.0-or-later

from types import FunctionType


class Command:
    def __init__(self, func: FunctionType, args: dict):
        self.function = func
        self.pattern = args.get("pattern")
        self.simple_pattern = args.get("simple_pattern", None)
        self.raw_pattern = args.get("raw_pattern", None)
        self.pattern_extra = args.get("pattern_extra", "")
        self.extra = args.get("extra", None)
