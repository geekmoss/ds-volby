import environ


@environ.config(prefix='')
class Config:
    debug = environ.bool_var(False)

    discord_token = environ.var()
    discord_token_debug = environ.var('')
    discord_owner_userid = environ.var(converter=int)
    pass


config: Config = environ.to_config(Config)
