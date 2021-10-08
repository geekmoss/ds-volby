from discord.ext import commands
from discord import Intents, Embed, Colour
from discord_slash import SlashCommand
import signal
from config import config
from Cogs import Debug, Volby


intents = Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='--' if not config.debug else 'd--', intents=intents)
slash = SlashCommand(bot)


def stop():
    bot.loop.close()
    bot.logout()
    pass


async def command_error(self, ctx: commands.Context, error):
    if self.error_log:
        print('[ERROR]', error)

    if isinstance(error, commands.MissingRequiredArgument):
        await self.send_cmd_help(ctx)
    pass


@bot.event
async def on_ready():
    print("I'm ready!")
    pass


@bot.event
async def on_command_error(context: commands.Context, exception):
    print(f"{context.command}:", exception)

    if isinstance(exception, commands.MissingRequiredArgument):
        await context.send(embed=Embed(
            title="Error",
            color=Colour.red(),
            description=f"Příkaz není napsaný správně, prosím zkontrolujte ho.\n\n"
                        f"```\n{context.command.help}\n```"
        ))
        pass
    pass


bot.loop.add_signal_handler(signal.SIGINT, stop)
bot.loop.add_signal_handler(signal.SIGTERM, stop)

bot.add_cog(Debug(bot, config.discord_owner_userid))
bot.add_cog(Volby(bot, config.discord_owner_userid, slash))

bot.run(config.discord_token if not config.debug else
        (config.discord_token_debug if config.discord_token_debug else config.discord_token))
