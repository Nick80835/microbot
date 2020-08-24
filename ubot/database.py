# SPDX-License-Identifier: GPL-2.0-or-later

import json
import sqlite3


class Database():
    db_conn = sqlite3.connect("database.sqlite")

    def __init__(self):
        cur = self.db_conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS chats (
                id integer PRIMARY KEY,
                disabled_commands text NOT NULL
            );"""
        )

    def ensure_chat_table(self, chat_id: int):
        cur = self.db_conn.cursor()
        cur.execute("INSERT OR IGNORE INTO chats (id, disabled_commands) VALUES (?, ?);", [str(chat_id), "[]"])
        self.db_conn.commit()

    def get_disabled_commands(self, chat_id: int) -> list:
        self.ensure_chat_table(chat_id)
        cur = self.db_conn.cursor()
        disabled_raw = cur.execute("SELECT disabled_commands FROM chats WHERE id = ?;", [str(chat_id)]).fetchone()
        return json.loads(disabled_raw[0] if disabled_raw else "[]")

    def disable_command(self, chat_id: int, command: str):
        disabled_commands = self.get_disabled_commands(chat_id)

        if command not in disabled_commands:
            disabled_commands.append(command)
            new_disabled_commands = json.dumps(disabled_commands)
            cur = self.db_conn.cursor()
            cur.execute("UPDATE chats SET disabled_commands = ? WHERE id = ?;", [new_disabled_commands, str(chat_id)])
            self.db_conn.commit()

    def enable_command(self, chat_id: int, command: str):
        disabled_commands = self.get_disabled_commands(chat_id)

        if command in disabled_commands:
            disabled_commands.remove(command)
            new_disabled_commands = json.dumps(disabled_commands)
            cur = self.db_conn.cursor()
            cur.execute("UPDATE chats SET disabled_commands = ? WHERE id = ?;", [new_disabled_commands, str(chat_id)])
            self.db_conn.commit()
