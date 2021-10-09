from discord import Embed
from volby_cz import get_chamber_of_deputies_election_results, ChamberOfDeputiesElectionEnum
from itertools import combinations
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from volby_cz.models import Ps
from datetime import datetime
from parties_tag import TAGS
from os.path import exists


DATA: Ps = None
LAST_UPDATE: datetime = None


def update():
    global DATA, LAST_UPDATE

    if LAST_UPDATE is None or (datetime.now() - LAST_UPDATE).total_seconds() > 60 * 3:
        print('loading data')
        DATA = get_chamber_of_deputies_election_results(ChamberOfDeputiesElectionEnum.year_2021)
        LAST_UPDATE = datetime.now()
    else:
        print('cooldown on update...', LAST_UPDATE)


def x_get_parties():
    update()

    return [
        {
            "value": f"{p.k_party}",
            "label": f"{p.party_name}",
        }
        for p in sorted(DATA.results.cr.parties, key=lambda x: x.party_result.vote_percent, reverse=True)
    ]


def x_get_regions():
    update()

    return [
        {
            "value": f"{r.region_number}",
            "label": f"{r.region_name}",
        }
        for r in DATA.results.regions
    ]


def voting_status() -> Embed:
    update()

    e = Embed()
    e.title = 'Stav sčítání'
    e.timestamp = LAST_UPDATE
    e.set_footer(text=f'Poslední aktualizace: {LAST_UPDATE.strftime("%H:%M:%S %d. %m. %Y") if LAST_UPDATE else "??"}; '
                      f'Data vygenerována: {DATA.generated.strftime("%H:%M:%S %d. %m. %Y") if LAST_UPDATE else "??"}')

    e.add_field(name='Počet registrovaných voličů',
                value=f'{DATA.results.cr.voter_turnout.registered_voters}', inline=True)
    e.add_field(name='Počet platných hlasů',
                value=f'{DATA.results.cr.voter_turnout.valid_vote_count} '
                      f'({DATA.results.cr.voter_turnout.valid_vote_percent}%)', inline=True)
    e.add_field(name='Volební účast', value=f'{DATA.results.cr.voter_turnout.voter_turnout_percent}%', inline=True)
    e.add_field(name='Sečtených okrsků', value=f'{DATA.results.cr.voter_turnout.election_district_done_percent}%')
    return e


def all_parties() -> Embed:
    update()

    e = Embed()
    e.title = 'Průběžné výsledky'
    e.timestamp = LAST_UPDATE
    e.set_footer(
        text=f'Poslední aktualizace: {LAST_UPDATE.strftime("%H:%M:%S %d. %m. %Y")};'
             f'Data vygenerována: {DATA.generated.strftime("%H:%M:%S %d. %m. %Y")}')

    for p in sorted(DATA.results.cr.parties, key=lambda x: x.party_result.vote_percent, reverse=True):
        e.add_field(name=TAGS[p.k_party], value=f'{p.party_result.vote_percent}%')
    return e


def by_regions() -> Embed:
    update()

    e = Embed()
    e.title = 'Přehled po krajích'
    e.timestamp = LAST_UPDATE
    e.set_footer(
        text=f'Poslední aktualizace: {LAST_UPDATE.strftime("%H:%M:%S %d. %m. %Y")};'
             f'Data vygenerována: {DATA.generated.strftime("%H:%M:%S %d. %m. %Y")}')

    for k in DATA.results.regions:
        k.parties.sort(key=lambda x: x.party_result.vote_percent, reverse=True)
        first_party = k.parties[0]
        e.add_field(name=k.region_name, value=f'{first_party.party_name}\n'
                                              f'{first_party.party_result.vote_percent}%', inline=True)
    return e


def party_detail(k_party) -> [Embed]:
    update()
    party = [p for p in DATA.results.cr.parties if int(k_party[0]) == p.k_party]
    if len(party) == 0:
        return [Embed(description='Žádné informace')]
    party = party[0]

    e1 = Embed()
    e1.title = f'Výsledky strany: {party.party_name}'
    e1.add_field(name='Počet hlasů', value=f'{party.party_result.vote_count}\n'
                                           f'{party.party_result.vote_percent}%')
    e1.add_field(name='Počet mandátů', value=f'{party.party_result.mandate_count}\n'
                                             f'{party.party_result.mandate_percent}%')

    # ---

    e2 = Embed()
    e2.title = 'Mandáty strany'

    for d in party.deputies:
        e2.add_field(name=f'{d.prefix} {d.surname} {d.name} {d.suffix}',
                     value=f'Prefrenční hlasy: {d.prefer_vote_count} ({d.prefer_vote_percent}%)\n'
                           f'Pořadí na kandidátce: {d.ordinal_number}')

    e2.timestamp = LAST_UPDATE
    e2.set_footer(
        text=f'Poslední aktualizace: {LAST_UPDATE.strftime("%H:%M:%S %d. %m. %Y")};'
             f'Data vygenerována: {DATA.generated.strftime("%H:%M:%S %d. %m. %Y")}')

    return [e1, e2]


def region_detail(region_number) -> [Embed]:
    update()
    region = [r for r in DATA.results.regions if int(region_number[0]) == r.region_number]
    if len(region) == 0:
        return [Embed(description='Žádné informace')]
    region = region[0]

    e1 = Embed()
    e1.title = f'Výsledky v {region.region_name}'
    region.parties.sort(key=lambda x: x.party_result.vote_percent, reverse=True)

    for p in region.parties:
        e1.add_field(name=TAGS[p.k_party], value=f'{p.party_result.vote_percent}%')
    # ---

    e2 = Embed()
    e2.title = 'Sčítání hlasů'

    e2.add_field(name='Počet registrovaných voličů',
                 value=f'{region.voter_turnout.registered_voters}', inline=True)
    e2.add_field(name='Počet platných hlasů',
                 value=f'{region.voter_turnout.valid_vote_count} '
                      f'({region.voter_turnout.valid_vote_percent}%)', inline=True)
    e2.add_field(name='Volební účast', value=f'{region.voter_turnout.voter_turnout_percent}%', inline=True)
    e2.add_field(name='Sečtených okrsků', value=f'{region.voter_turnout.election_district_done_percent}%')

    e2.timestamp = LAST_UPDATE
    e2.set_footer(
        text=f'Poslední aktualizace: {LAST_UPDATE.strftime("%H:%M:%S %d. %m. %Y")};'
             f'Data vygenerována: {DATA.generated.strftime("%H:%M:%S %d. %m. %Y")}')

    return [e1, e2]


def get_coalition() -> (str, Embed):
    update()

    parties = [p for p in DATA.results.cr.parties if p.party_result.mandate_count > 0]
    parties.sort(key=lambda x: x.party_result.mandate_count, reverse=True)

    # mandate_labels = [TAGS[p.k_party] for p in parties]
    mandate_labels = [p.party_name for p in parties]
    mandate_values = [p.party_result.mandate_count for p in parties]

    parties.sort(key=lambda x: x.party_result.vote_percent, reverse=True)
    # percent_labels = [TAGS[p.k_party] for p in parties]
    percent_labels = [p.party_name for p in parties]
    percent_values = [p.party_result.vote_percent for p in parties]

    # Pie Chart

    file = f'/tmp/{LAST_UPDATE.timestamp()}.png'
    if not exists(file):
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'pie'}]])
        fig.add_trace(go.Pie(title='Zisk hlasů', labels=percent_labels, values=percent_values, textposition='inside',
                   textinfo='percent'), row=1, col=1)
        fig.add_trace(go.Pie(title='Počet získáných mandátů', labels=mandate_labels, values=mandate_values, textposition='inside',
                   textinfo='value+percent'), row=1, col=2)
        fig.write_image(file)

    # Possible Coalition
    pairs = list(zip(mandate_labels, mandate_values))
    winner = pairs[0] if parties else ('', 0)
    coalition = []

    for size in (2, 3):
        for combo in combinations(pairs, size):
            total_mandate = sum([v for _, v in combo])
            if winner not in combo:
                continue

            if total_mandate < 101:
                continue

            coalition.append(combo)

    if len(coalition) == 0:
        for size in (4, 5):
            for combo in combinations(pairs, size):
                total_mandate = sum([v for _, v in combo])
                if winner not in combo:
                    continue

                if total_mandate < 101:
                    continue

                coalition.append(combo)

    coalition.sort(key=lambda x: (len(x), sum([v for _, v in x])))

    return file, Embed(
        title='Počet mandátů a možné složení většinové vlády',
        timestamp=LAST_UPDATE,
        description='\n\n'.join([
            f'{sum([v for _, v in c])} - ' + ', '.join([f'{n} ({v})' for n, v in c])
            for c in coalition
            if sum([v for _, v in c]) > 100]),
    )
