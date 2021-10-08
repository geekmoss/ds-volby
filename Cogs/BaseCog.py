from discord.ext.commands import Bot, Cog, Context
from discord import Embed


class BaseCog(Cog):
    def __init__(self, bot: Bot, owner: int, slash=None, *args, **kwargs):
        self.bot: Bot = bot
        self.owner = owner
        self.args = args
        self.kwargs = kwargs
        self.slash = slash

    async def generic_error(self, ctx: Context, problem: str = ""):
        await ctx.send(embed=Embed(
            title="Error",
            color=0xff0000,
            description=f"Sorry {ctx.author.mention}, we have some problem: **{problem}**"
        ))
        pass

    async def on_command_error(self, ctx, error):
        print(ctx, error)

        await self.generic_error(ctx, error)
        pass
    pass
