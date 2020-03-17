# SPDX-License-Identifier: GPL-2.0-or-later

from databases import Database as db


class Database():
    def __init__(self, client):
        self.db = db("sqlite:///database.db")
        client.loop.run_until_complete(self.db.connect())

    async def ensure_table(self, table, columns):
        await self.db.execute(f"create table if not exists {table} ({' TEXT, '.join(columns) + ' TEXT'})")
        return ", ".join(columns)

    async def single_row_write(self, table, columns, row, value):
        column_string = await self.ensure_table(table, columns)
        await self.db.execute(f"delete from {table} where {columns[0]} = '{row}'")
        await self.db.execute(f"insert into {table}({column_string}) values ('{row}', '{value}')")

    async def single_row_delete(self, table, columns, row):
        await self.ensure_table(table, columns)
        await self.db.execute(f"delete from {table} where {columns[0]} = '{row}'")

    async def single_column_readall(self, table, columns, row):
        await self.ensure_table(table, columns)
        fetched_tuple = await self.db.fetch_all(f"select {row} from {table}")
        fetched_list = [item[0] for item in fetched_tuple]
        return fetched_list

    async def single_row_read(self, table, columns, row):
        await self.ensure_table(table, columns)
        content = await self.db.fetch_one(f"select {columns[1]} from {table} where {columns[0]} = '{row}'")

        if content:
            return content[0]
        else:
            return None
