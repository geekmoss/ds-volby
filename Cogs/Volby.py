from discord.ext.commands import command, Context
from discord_slash.utils.manage_components import create_button, create_actionrow, ComponentContext, create_select, \
    create_select_option
from discord_slash.model import ButtonStyle
from discord_slash.cog_ext import cog_component
from Cogs.BaseCog import BaseCog
from volby import voting_status, all_parties, by_regions, x_get_parties, party_detail, x_get_regions, region_detail


class Volby(BaseCog):
    @command(name='volby')
    async def volby(self, ctx: Context):
        buttons = [
            create_button(style=ButtonStyle.green, label='Průběžná výsledky', custom_id='all_parties'),
            create_button(style=ButtonStyle.blue, label='Stav sčítání', custom_id='counting_status'),
            create_button(style=ButtonStyle.blue, label='Přehled po krajích', custom_id='regions'),
        ]

        select_party = create_select(options=[
            create_select_option(item['label'], value=item['value'])
            for item in x_get_parties()[:25]
        ],
            placeholder='Detail stran a jejich mandátry: vyberte kraj',
            min_values=1,
            max_values=1,
            custom_id='select_party',
        )

        select_region = create_select(options=[
            create_select_option(item['label'], value=item['value'])
            for item in x_get_regions()[:25]
        ],
            placeholder='Detail krajů: vyberte kraj',
            min_values=1,
            max_values=1,
            custom_id='select_region',
        )

        action_row_buttons = create_actionrow(*buttons)

        await ctx.send(
            components=[action_row_buttons, create_actionrow(select_party), create_actionrow(select_region)],
            content='Vyberte jednu z možností:'
        )

    @cog_component()
    async def counting_status(self, ctx: ComponentContext):
        await ctx.edit_origin(embed=voting_status())
        pass

    @cog_component()
    async def all_parties(self, ctx: ComponentContext):
        await ctx.edit_origin(embed=all_parties())
        pass

    @cog_component()
    async def regions(self, ctx: ComponentContext):
        await ctx.edit_origin(embed=by_regions())
        pass

    @cog_component()
    async def select_party(self, ctx: ComponentContext):
        await ctx.edit_origin(embeds=party_detail(ctx.selected_options))

    @cog_component()
    async def select_region(self, ctx: ComponentContext):
        await ctx.edit_origin(embeds=region_detail(ctx.selected_options))
