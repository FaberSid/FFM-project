import os
from discord.ext import commands as c
from module.prefix import table
from module import db
import colorama
from colorama import Fore, Back, Style
colorama.init()
db.init()

class MyBot(c.Bot):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print("------")
        print(f"導入サーバー数：{len(self.guilds)}")
        print(f"合計ユーザー数：{len({a.id for a in self.users if not a.bot})}")
        print(f"合計ボット数：{len({a.id for a in self.users if a.bot})}")
        print('------')
        import pathlib
        cur = pathlib.Path('.')
        print(f'import')
        for p in cur.glob('module/*.py'):
            try:
                self.load_extension(f'module.{p.stem}')
                print(f'module.{p.stem}')
            except c.errors.NoEntryPointError:
                print(f'{Fore.RED}module.{p.stem}{Style.RESET_ALL}')

    async def on_guild_remove(guild):
        db.guild_remove(guild)

bot = MyBot(command_prefix=table)

bot.run(os.environ.get("DISCORD_TOKEN_FFM"))