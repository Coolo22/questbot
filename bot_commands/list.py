import json, discord, random, asyncio
from discord.ext.commands import MemberConverter
from resources import var, questbot


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def command_list(bot, ctx, arg1, arg2, arg3):
    converter = MemberConverter()
    ctx.bot = bot

    accepted = ["golden", "shiny", "standard"]

    page = 1
    creatureType = None
    user = None

    if arg1 == None:
        user = arg1
    elif arg2 == None:
        try:
            user = await converter.convert(ctx, arg1)
        except:
            if arg1.lower() in accepted:
                creatureType = arg1.lower()
            else:
                page = arg1
    elif arg3 == None:
        if arg1.lower() in accepted:
            creatureType = arg1.lower()
            try:
                user = await converter.convert(ctx, arg2)
            except:
                page = arg2
        else:
            page = arg2
            try:
                user = await converter.convert(ctx, arg1)
            except:
                page = arg1
                user = await converter.convert(ctx, arg2)
    else:
        creatureType = arg1.lower()
        page = arg3
        try:
            user = await converter.convert(ctx, arg2)
        except:
            page = arg2
            user = await converter.convert(ctx, arg3)
    
    if not str(page).isnumeric():
        return await ctx.send(f"> Invalid argument order. `{var.prefix}list *[{'/'.join(accepted)}] *[user] *[page]`")
    
    if user == None:
        user = ctx.author
    
    user = questbot.User(user)
    user.zoo.getCreatures()
    user.zoo.getZoo()
    
    allData = {}

    if creatureType == "standard":
        allData.update(user.zoo.zoo.creaturesRaw["common"])
        allData.update(user.zoo.zoo.creaturesRaw["very_common"])
    elif creatureType == "shiny":
        allData.update(user.zoo.zoo.creaturesRaw["rare"])
    elif creatureType == "golden":
        allData.update(user.zoo.zoo.creaturesRaw["golden"])
    else:
        creatureType = None
        allData.update(user.zoo.zoo.creaturesRaw["golden"])
        allData.update(user.zoo.zoo.creaturesRaw["rare"])
        allData.update(user.zoo.zoo.creaturesRaw["common"])
        allData.update(user.zoo.zoo.creaturesRaw["very_common"])

    try:
        page = int(page)
    except:
        return await ctx.send(content=f"> Page must be a number. `{var.prefix}list *[{'/'.join(accepted)}] *[user] *[page]`")
    
    ownedUsr = user.zoo.creatures

    ownedUsr = list(sorted(ownedUsr, key=lambda item: ownedUsr.count(item), reverse=True))

    creaturesOld = []
    creatureCount = 0

    for creature in allData:
        if creature in ownedUsr:
            creatureCount += ownedUsr.count(creature)
            creaturesOld.append(f'{allData[creature]["emoji"]} {ownedUsr.count(creature)}x {creature.replace("_", " ").title()}\n')

    creatures = list(chunks(creaturesOld, 15))

    embedFail = discord.Embed(title="Uh Oh!", description=f"Could not find page `{page}` on {user.user}'s creature list. There are only `{len(creatures)}` pages on {user.user}'s' list.", color=0xFF0000)

    if len(creatures) == 0:
        return await ctx.send(f"> {user.user} has no creatures!")
    if page > len(creatures):
        try:
            return await ctx.send(embed=embedFail)
        except:
            return await ctx.send(embeds=[embedFail])

    embed = discord.Embed(title=f"{user.user}'s {creatureType + ' ' if creatureType else ''}creature list ({creatureCount}x)", description=["".join(creature_list) for creature_list in creatures][page-1], color=var.embed)

    embed.set_footer(text=f"Page {page}/{len(creatures)}" + (f"  -  Use \"{var.prefix}list {creatureType + ' ' if creatureType else ''}{page+1 if page != len(creatures) else 1}{f' {user.user.name}' if user.user != ctx.author else ''}\" to see the next page." if len(creatures) != 1 else ""))

    await ctx.send(embeds=[embed])