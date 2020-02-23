# Copyright (C) 2019 Nick Filmer (nick80835@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
