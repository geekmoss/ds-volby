import environ


@environ.config(prefix='')
class Config:
    debug = environ.var(False, converter=bool)

    discord_token = environ.var()
    discord_token_debug = environ.var('')
    discord_owner_userid = environ.var(converter=int)
    pass


config: Config = environ.to_config(Config)
