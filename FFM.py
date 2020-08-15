import os
from discord import AllowedMentions
from discord.ext import commands as c
from module.prefix import table
from module import db

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
        for p in cur.glob('module/*.py'):
            try:
                self.load_extension(f'module.{p.stem}')
                print(f'LOADING       :module.{p.stem}')
            except c.errors.ExtensionAlreadyLoaded:
                print(f'Already Loaded:module.{p.stem}')
            except c.errors.NoEntryPointError:
                print(f'NoEntryPoint  :module.{p.stem}')
        print('------')

    #async def on_guild_remove(self, guild):
    #    db.guild_remove(guild)


bot = MyBot(command_prefix=table,allowed_mentions=AllowedMentions(everyone=False, users=False, roles=False))

bot.run(os.environ.get("DISCORD_TOKEN_FFM"))
