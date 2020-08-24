# SPDX-License-Identifier: GPL-2.0-or-later

import json

from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine


class Database():
    engine = create_engine('sqlite:///database.sqlite')
    metadata = MetaData()

    chats = Table(
        "chats",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("disabled_commands", String, nullable=False)
    )

    metadata.create_all(engine)
    conn = engine.connect()

    def ensure_disabled_commands_table(self, chat_id: int):
        self.conn.execute(f"INSERT OR IGNORE INTO chats (id, disabled_commands) VALUES (?, ?);", (chat_id, "[]"))

    def get_disabled_commands(self, chat_id: int) -> list:
        self.ensure_disabled_commands_table(chat_id)
        disabled_raw = self.conn.execute(f"SELECT disabled_commands FROM chats WHERE id = ?;", (chat_id, )).fetchone()
        return json.loads(disabled_raw[0] if disabled_raw else "[]")

    def disable_command(self, chat_id: int, command: str):
        disabled_commands = self.get_disabled_commands(chat_id)

        if command not in disabled_commands:
            disabled_commands.append(command)
            new_disabled_commands = json.dumps(disabled_commands)
            self.conn.execute("UPDATE chats SET disabled_commands = ? WHERE id = ?;", (new_disabled_commands, chat_id))

    def enable_command(self, chat_id: int, command: str):
        disabled_commands = self.get_disabled_commands(chat_id)

        if command in disabled_commands:
            disabled_commands.remove(command)
            new_disabled_commands = json.dumps(disabled_commands)
            self.conn.execute(f"UPDATE chats SET disabled_commands = ? WHERE id = ?;", (new_disabled_commands, chat_id))
