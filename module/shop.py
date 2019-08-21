import asyncio
from discord.ext import commands as c
from module import db, item

items = item.items


class Shop(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.group()
    async def shop(self, ctx):
        # サブコマンドが指定されていない場合、メッセージを送信する。
        if ctx.invoked_subcommand is None:
            await ctx.send("いらっしゃいませ！どうかなさいましたか？\n"
                           "相場を知りたい場合は`shop rate`\n"
                           "売る場合は`shop sell アイテム名 個数`\n"
                           "買う場合は`shop buy アイテム名 個数`です")

    @shop.command()
    async def rate(self, ctx):
        item_list = "\n".join("{} : {}{}{}".format(i["name"], f"売{i['sell']}FG" * (i['sell'] is not None),
                                                   "、" * (not (i["buy"] is None and i["sell"] is None)),
                                                   f"買{i['buy']}FG" * (i['buy'] is not None))
                              for i in items.values() if not (i["sell"] is None and i["buy"] is None))
        return await ctx.send("""販売中のアイテム：\n{}""".format(item_list))

    @shop.command()
    async def sell(self, ctx, item_name: str = None, cnt: int = 1):
        if item_name is None:
            return await ctx.send("アイテム名を指定してください")
        if cnt <= 0:
            return await ctx.send("数は1以上を指定してください")
        item_id = get_key_from_value(items, item_name)
        s_items = [item_id, items[str(item_id)]["name"], items[str(item_id)]["sell"]]
        item_cnt = db.player.item.get_cnt(ctx.message.author.id, s_items[0])
        if not item_cnt:
            return await ctx.send(f"<@{ctx.message.author.id}>は{s_items[1]}を持っていない")
        elif item_cnt < cnt:
            return await ctx.send(f"所持数が足りない")
        msg = await ctx.send(f"{s_items[1]} {cnt}個を{s_items[2] * cnt}FGで売却しますか？")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            _ = (user == ctx.message.author)
            _ &= (reaction.emoji in '✅❌')
            return _

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("またのお越しをお待ちしております")
        if reaction.emoji == '✅':
            money = db.player.money.get(ctx.message.author.id)
            db.player.item.update_cnt(ctx.message.author.id, s_items[0], item_cnt - cnt)
            db.player.money.add(ctx.message.author.id, s_items[2] * cnt)
            await ctx.send(f"{s_items[1]} {cnt}個を{s_items[2] * cnt}FGで売却しました。\nまたのお越しをお待ちしております")
        else:
            await ctx.send("またのお越しをお待ちしております")

    @shop.command()
    async def buy(self, ctx, item_name: str = None, cnt: int = 1):
        if item_name is None:
            return await ctx.send("アイテム名を指定してください")
        if cnt <= 0:
            return await ctx.send("数は1以上を指定してください")
        item_id = get_key_from_value(items, item_name)
        s_items = [item_id, items[str(item_id)]["name"], items[str(item_id)]["buy"]]
        money = db.player.money.get(ctx.message.author.id)
        if money < s_items[1] * cnt:
            return await ctx.send(f"お金が足りない")
        item = items[s_items[0]]
        msg = await ctx.send(f"{s_items[1]} {cnt}個を{s_items[2] * cnt}FGで買いますか？")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            _ = (user == ctx.message.author)
            _ &= (reaction.emoji in '✅❌')
            return _

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("またのお越しをお待ちしております")
        if reaction.emoji == '✅':
            item_cnt = db.player.item.get_cnt(ctx.message.author.id, s_items[0])
            db.player.money.pay(ctx.message.author.id, s_items[2] * cnt)
            db.player.item.update_cnt(ctx.message.author.id, s_items[0], item_cnt + cnt)
            await ctx.send(f"{s_items[1]} {cnt}個を{s_items[2] * cnt}FGで買いました。\nまたのお越しをお待ちしております")
        else:
            await ctx.send("またのお越しをお待ちしております")


def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if val == v["name"]]
    if keys:
        return keys[0]
    return None


def setup(bot):
    bot.add_cog(Shop(bot))
