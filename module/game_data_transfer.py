import datetime
import random
import hashlib

from discord.errors import NotFound
from module import db
from discord.ext import commands as c
from asyncio import sleep
import os


class Account(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.group()
    async def token(self, ctx):
        # サブコマンドが指定されていない場合、メッセージを送信する。
        if ctx.invoked_subcommand is None:
            await ctx.send("トークンを再生成する場合は`token make`\n"
                           "トークンを使ってアカウントを復元する場合は`token set`です")

    @token.command(pass_context=True, description='ゲームアカウントの復元に必要なコードを送ります')
    async def get(self, ctx):
        account = db.account.load(ctx.message.author.id)
        if account:
            await ctx.message.author.send(f"TOKEN情報はここに生成されています", delete_after=30)
        else:
            await ctx.message.author.send(f"TOKEN情報は生成されていません\n`token make`で生成できます", delete_after=30)

    @token.command(pass_context=True, description='ゲームアカウントの復元に必要なコードを作成します', enabled=False)
    async def make(self, ctx):
        a = datetime.datetime.now()
        b = random.random()
        c = ctx.message.id
        d = f"[{a}][{b}][{c}]"
        e = hashlib.sha512(d.encode("utf-8")).hexdigest()
        if ctx.message.author.dm_channel is None:
            await ctx.message.author.create_dm()
        account = db.account.load(ctx.message.author.id)
        if account:
            msg = await ctx.message.author.fetch_message(account[2])
            await msg.edit(content=f"TOKEN:`{e}`\n再生成した時間:`{a}`")
            db.account.save(ctx.message.author.id, e, account[2])
            await ctx.message.author.send(f"TOKEN情報を再生成しました", delete_after=30)
        else:
            msg = await ctx.message.author.send(f"TOKEN:`{e}`\n生成した時間:`{a}`")
            db.account.save(ctx.message.author.id, e, msg.id)

    @token.command(pass_context=True, description='ゲームアカウントをコードで復元します', enabled=False)
    async def set(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Account(bot))
