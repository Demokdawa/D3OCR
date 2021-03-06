import discord
from discord.ext import tasks, commands
from discord.utils import get
import functools
from utils import *
from db_operations import *
from loadconfig import bot_token_prod


# Initialize ##################################################################################

prefix = "!"
bot = commands.Bot(command_prefix=prefix)
bot.remove_command('help')
print('[Init] Bot configuré !')


###############################################################################################
# Background Tasks ############################################################################


@tasks.loop(seconds=3600)
async def vault_update():
    await bot.wait_until_ready()
    thing = functools.partial(update_vault_list)
    await bot.loop.run_in_executor(None, thing)
    
    
###############################################################################################
# Custom Convertors ################################################################################

@bot.event
async def on_command_error(ctx, message):
    if isinstance(message, commands.UserInputError):
        await ctx.send(message)
    if isinstance(message, commands.MissingRequiredArgument):
        await ctx.send("J'ai pas pigé un broc de ce que vous bavez !")  
    else:
        print(message)


# Check if number is too high or not an absolute
class CheckNbr(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            if int(argument) > 100:
                raise commands.UserInputError('{} ? De qui te moques-tu, Tenno !?'.format(argument))
            else:
                return int(argument)
        else:
            raise commands.UserInputError('Vous ne pouvez entrer qu\'un nombre absolu !')
            
            
# def check_bot_channel():
#     def predicate(ctx):
#         if ctx.guild.id == 290252322028650497:
#             raise commands.UserInputError("C'est pas encore prêt :p")
#         else:
#             return True
#     return commands.check(predicate)

###############################################################################################
# Bot-commands ################################################################################


@bot.event
async def on_ready():
    print("[Init] Bot en ligne !")
    await bot.change_presence(activity=discord.Game("Ordis travaille, opérateur"))


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     if message.content == "Hello":
#         await message.channel.send("Yo !")
#     if message.content == "Jour ?":
#         await message.channel.send("Nuit")
#     if message.content == "Clem ?":
#         await message.channel.send("GRAKATA")
#     if message.content == "Demokdawa":
#         await message.channel.send("LE DIEU !")
#     if message.content == "A Kadoc ?":
#         await message.channel.send("Il dit que c'est a lui de jouer...")
#     await bot.process_commands(message)


# @bot.event
# async def on_raw_reaction_add(payload):
#     message_to_track = 678911976252112926
#
#     perrin_emoji = 678378425001443343
#     veil_emoji = 678378424925945856
#     meridian_emoji = 678378424976277564
#     loka_emoji = 678378424955306004
#     suda_emoji = 678378424967888906
#     hexis_emoji = 678378425073008695
#
#     guild = bot.get_guild(payload.guild_id)
#     member = guild.get_member(payload.user_id)
#
#     veil = get(guild.roles, id=677885546684743700)
#     meridian = get(guild.roles, id=677886858579017741)
#     suda = get(guild.roles, id=677887426332590080)
#     hexis = get(guild.roles, id=677885889774616607)
#     perrin = get(guild.roles, id=677886031642755073)
#     loka = get(guild.roles, id=677886156108595229)
#
#     if payload.message_id == message_to_track:
#         if payload.emoji.id == meridian_emoji:
#             await member.add_roles(meridian, reason=None, atomic=True)
#         elif payload.emoji.id == veil_emoji:
#             await member.add_roles(veil, reason=None, atomic=True)
#         elif payload.emoji.id == perrin_emoji:
#             await member.add_roles(perrin, reason=None, atomic=True)
#         elif payload.emoji.id == loka_emoji:
#             await member.add_roles(loka, reason=None, atomic=True)
#         elif payload.emoji.id == suda_emoji:
#             await member.add_roles(suda, reason=None, atomic=True)
#         elif payload.emoji.id == hexis_emoji:
#             await member.add_roles(hexis, reason=None, atomic=True)


# @bot.event
# async def on_raw_reaction_remove(payload):
#     message_to_track = 678911976252112926
#
#     perrin_emoji = 678378425001443343
#     veil_emoji = 678378424925945856
#     meridian_emoji = 678378424976277564
#     loka_emoji = 678378424955306004
#     suda_emoji = 678378424967888906
#     hexis_emoji = 678378425073008695
#
#     guild = bot.get_guild(payload.guild_id)
#     member = guild.get_member(payload.user_id)
#
#     veil = get(guild.roles, id=677885546684743700)
#     meridian = get(guild.roles, id=677886858579017741)
#     suda = get(guild.roles, id=677887426332590080)
#     hexis = get(guild.roles, id=677885889774616607)
#     perrin = get(guild.roles, id=677886031642755073)
#     loka = get(guild.roles, id=677886156108595229)
#
#     if payload.message_id == message_to_track:
#         if payload.emoji.id == meridian_emoji:
#             await member.remove_roles(meridian, reason=None, atomic=True)
#         elif payload.emoji.id == veil_emoji:
#             await member.remove_roles(veil, reason=None, atomic=True)
#         elif payload.emoji.id == perrin_emoji:
#             await member.remove_roles(perrin, reason=None, atomic=True)
#         elif payload.emoji.id == loka_emoji:
#             await member.remove_roles(loka, reason=None, atomic=True)
#         elif payload.emoji.id == suda_emoji:
#             await member.remove_roles(suda, reason=None, atomic=True)
#         elif payload.emoji.id == hexis_emoji:
#             await member.remove_roles(hexis, reason=None, atomic=True)


@bot.command()
async def ping(ctx):
    latency = bot.latency
    print("Bip Boup je suis la !")
    await ctx.send(latency)
    
    
# Index guide command
@bot.command()
async def doc(ctx):
    await ctx.send('https://docs.google.com/spreadsheets/d/1nvXMWn3Ep95QCp317le8EpDU2XgqLTdCcMJtipolz8k/edit?usp=sharing')


# Arg 1 = Era, Arg2 = Name, Arg3 = Quality, Arg4 = Quantity
@bot.command()
async def relicadd(ctx, a1: spell_correct, a2: spell_correct, a3: spell_correct, a4: CheckNbr):
    if syntax_check_pass(a1, a2, a3) is True:
        add_relic_to_db(a1, a2, a3, a4, clean_disctag(str(ctx.message.author)))
        new_quantity = check_relic_quantity(a1, a2, a3, clean_disctag(str(ctx.message.author)))
        relic_state = is_vaulted(a1, a2)
        await ctx.send('Votre relique est une {} {} {}, que vous possedez dorénavant en {} exemplaire(s) **({})**'.format(a1, a2, a3, new_quantity, relic_state))
    else:
        await ctx.send(syntax_check_pass(a1, a2, a3))


# Arg 1 = Era, Arg2 = Name, Arg3 = Quality, Arg4 = Quantity
@bot.command()
async def relicdel(ctx, a1: spell_correct, a2: spell_correct, a3: spell_correct, a4: CheckNbr):
    if syntax_check_pass(a1, a2, a3) is True:
        del_state = del_relic_on_db(a1, a2, a3, a4, clean_disctag(str(ctx.message.author)))
        if del_state is True:
            new_quantity = check_relic_quantity(a1, a2, a3, clean_disctag(str(ctx.message.author)))
            relic_state = is_vaulted(a1, a2)
            await ctx.send('Vous avez supprimé {} reliques {} {} {}, que vous possedez dorénavant en {} exemplaire(s) **({})**'.format(a4, a1, a2, a3, new_quantity, relic_state))
        else:
            await ctx.send(del_state)
    else:
        await ctx.send(syntax_check_pass(a1, a2, a3))


# Arg 1 = Era, Arg2 = Name, Arg3 = Quality, Arg4 = Quantity
@bot.command()
async def relicrefine(ctx, a1: spell_correct, a2: spell_correct, a3: spell_correct, a4: CheckNbr):
    if syntax_check_pass(a1, a2, a3) is True:
        refine_state = refine_relics(a1, a2, a3, a4, clean_disctag(str(ctx.message.author)))
        if refine_state is True:
            new_quantity = check_relic_quantity(a1, a2, a3, clean_disctag(str(ctx.message.author)))
            relic_state = is_vaulted(a1, a2)
            await ctx.send('Vous avez raffiné {} reliques {} {} en {}, que vous possedez dorénavant en {} exemplaires(s) **({})**'.format(a4, a1, a2, a3, new_quantity, relic_state))
        else:
            await ctx.send(refine_state)
    else:
        await ctx.send(syntax_check_pass(a1, a2, a3))


@bot.command()
async def ressourcedrop(ctx):
    await ctx.send('J\'ai pas encore fait la commande, oups !')


# OCR scan command 
@bot.command()
async def scanrelic(ctx, member: discord.Member=None):
    url = ctx.message.attachments[0].url
    if member is None:  # Default with no argument
        message = process_image(image_from_url(url), clean_disctag(str(ctx.message.author)))
    else:
        print(clean_disctag(str(member)))
        message = process_image(image_from_url(url), clean_disctag(str(member)))

    await ctx.send(message)
    

# OCR scan command - TEST
@bot.command()
# @check_bot_channel()
async def scanrelictest(ctx):
    url = ctx.message.attachments[0].url
    message = process_image(image_from_url(url), 'test')
    await ctx.send(message)


# Delete relics from the user
@bot.command()
# @check_bot_channel()
async def clearrelic(ctx):
    message = relic_owner_clear(clean_disctag(str(ctx.message.author)))
    await ctx.send(message)
    
    
# Delete relics from the user 'test'
@bot.command()
# @check_bot_channel()
async def clearrelictest(ctx):
    message = relic_owner_clear('test')
    await ctx.send(message)

    
# !halp command for help
@bot.command()
async def halp(ctx):
    embed = discord.Embed(title="Bienvenue sur le merveilleux 🤖 pour Warframe !",
                          description="Je suis la pour vous aider 😄", color=0xd5d500)
    embed.add_field(name="!clearrelic", value="Supprime toutes vos reliques. ⚠️", inline=True)
    embed.add_field(name="!scanrelic", value="Ajoute des reliques depuis un screen et écrase si déja existant.", inline=True)
    embed.add_field(name="!relicadd", value="Ajoute un montant d'une certaine relique. Ex : ***!relicadd Lith A2 Eclatante 3***", inline=True)
    embed.add_field(name="!relicdel", value="Supprime un montant d'une certaine relique. Ex : ***!relicdel Lith A2 Eclatante 4***", inline=True)
    embed.add_field(name="!relicrefine", value="Permet de raffiner une relique. Ex : ***!relicrefine Lith A2 Eclatante 2***", inline=True)
    embed.add_field(name="!ressourcedrop", value="Cette commande n'existe pas encore, désolay", inline=True)
    embed.add_field(name="!doc", value="Vous envoie le lien du doc.", inline=True)
    embed.set_footer(
        text="Pour les commandes !baserelic et !scanrelic il suffit d'attacher un screenshot de vos reliques en 1920x1080. \n "
        "Il faut un fullscreen pour que ca fonctionne. Supporte l'anglais et le francais. Les reliques sont visibles sur le site : \n"
        "relic.zenma-serv.net")
        
    await ctx.channel.send(embed=embed)

update_vault_list()
bot.run(bot_token_prod, bot=True, reconnect=True)  # Prod
