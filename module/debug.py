from discord.ext import commands as c
import contextlib
import io
import json
import textwrap
import traceback
from contextlib import redirect_stdout

with open('../assets/USERs.json', encoding='utf-8') as f:
    USERs = json.load(f)

def cleanup_code(content):
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])
    return content.strip('` \n')

class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.is_owner()
    @c.command(name='eval', hidden=True)
    async def evals(self, ctx):
        """Evaluates a code"""

        if not all((x in USERs.get(str(ctx.author.id), [])) for x in ["Cheater", "Debugger"]):
            return
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        if ctx.message.attachments:
            body = (await ctx.message.attachments[0].read()).decode('utf-8')
        else:
            body = cleanup_code(ctx.message.content[6:].lstrip())
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')
