import asyncio

from discord import AuditLogAction, Embed
from discord.ext import commands as c

from module import db


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot=bot


    @c.command()
    @c.has_permissions(administrator=True)
    async def restore(self, ctx, ch_id=None):
        if ch_id and ch_id.isdigit():
            ch_id=int(ch_id)
            data = db.boss_status.get_st(ctx.channel.id)
            if data:
                await ctx.send(embed=Embed(title="復元作業失敗",description="新規チャンネルではないためこのチャンネルでの復元はできません"))
                return
            deleted_ch = None
            try:
                async for i in ctx.guild.audit_logs(limit=None,action=AuditLogAction.channel_delete):
                    if ch_id==i.target.id:
                        deleted_ch = i.target.id
                        break
            except:
                await ctx.send("削除履歴の取得に失敗しました")
                return
            if deleted_ch is None:
                await ctx.send("削除履歴の取得に失敗しました")
                return
            data = db.boss_status.get_st(deleted_ch)
            if not data:
                return
            msg = await ctx.send(embed=Embed(title="復元しますか？",description="ID:`{}`(Lv.{})".format(ch_id,data[0])).set_footer(text="10s"))
            await msg.add_reaction("\U0001f44d")
            await msg.add_reaction("\U0001f44e")
            try:
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["\U0001f44d","\U0001f44e"]
                reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
            except asyncio.TimeoutError:
                await msg.edit(embed=Embed(title="異常終了",description='時間切れです'))
            else:
                if str(reaction.emoji) == "\U0001f44d":
                    db.channel.restore(ch_id, ctx.channel.id)
                    await msg.edit(embed=Embed(title="復元完了",description="ID:`{}`(Lv.{})".format(ch_id,data[0])))
                else:
                    await msg.edit(embed=Embed(title="復元取り消し",description="チャンネルの復元をキャンセルしました。"))
        else:
            deleted_ch = tuple()
            try:
                async for i in ctx.guild.audit_logs(limit=None,action=AuditLogAction.channel_delete):
                    deleted_ch+=(i.target.id,)
            except:
                await ctx.send("削除履歴の取得に失敗しました")
                return
            else:
                data = db.boss_status.get_list(deleted_ch)
                await ctx.send(embed=Embed(title="{}件の復元可能なチャンネルデータがあります".format(len(data)),description="\n".join(["ID:`{}`(Lv.{})".format(*i[:10]) for i in data])))


def setup(bot):
    bot.add_cog(Cog(bot))
