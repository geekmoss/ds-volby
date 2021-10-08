from config import config


def is_owner(ctx):
    return ctx.author.id == config.discord_owner_userid
