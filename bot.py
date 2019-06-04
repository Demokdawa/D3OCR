import discord
from discord.ext import commands
import sqlite3
from spellcheck import SpellCheck

# Command Checker #############################################################################

spell_check = SpellCheck('ref/ref_words.txt')

Era_file = 'ref/ref_era.txt'
Lith_file = 'ref/ref_lith.txt'
Meso_file = 'ref/ref_meso.txt'
Neo_file = 'ref/ref_neo.txt'
Axi_file = 'ref/ref_axi.txt'
Quality_file = 'ref/ref_quality.txt'


def parse_ref_files(file):
    ref_list = []
    with open(file, "r") as fileHandler:
        for line in fileHandler:
            ref_list.append(line.strip())
    return ref_list


ref_list_era = parse_ref_files(Era_file)
ref_list_lith = parse_ref_files(Lith_file)
ref_list_meso = parse_ref_files(Meso_file)
ref_list_neo = parse_ref_files(Neo_file)
ref_list_axi = parse_ref_files(Axi_file)
ref_list_quality = parse_ref_files(Quality_file)


def syntax_check_pass(arg1, arg2, arg3):
    # Check for Era
    if arg1 not in ref_list_era:
        return 'Cette ère de relique n\'existe pas ! (' + arg1 + ')'
    else:
        # Check for Name
        if arg1 == 'Lith':
            if arg2 not in ref_list_lith:
                return 'Cette relique n\'existe pas en Lith ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True
        if arg1 == 'Meso':
            if arg2 not in ref_list_meso:
                return 'Cette relique n\'existe pas en Meso ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True
        if arg1 == 'Neo':
            if arg2 not in ref_list_neo:
                return 'Cette relique n\'existe pas en Neo ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True
        if arg1 == 'Axi':
            if arg2 not in ref_list_axi:
                return 'Cette relique n\'existe pas en Axi ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True


def capit_arg(string):
    return string.capitalize()


def clean_disctag(name):
    sep = '#'
    rest = name.split(sep, 1)[0]
    return rest


def spell_correct(string):
    spell_check.check(string)
    return spell_check.correct().capitalize()


def number_check(a4):
    if a4 > 100:
        return False
    else:
        return True

###############################################################################################
# DB-Operations ###############################################################################


db = sqlite3.connect('relicdb')
print('Connexion a la db réussie !')


def check_relic_quantity(a1, a2, a3, owner):
    cursor = db.cursor()
    cursor.execute('''SELECT Quantity FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (a2, a1, a3, check_user_exist(owner),))
    result = cursor.fetchone()
    return result[0]


def check_user_exist(owner):
    cursor = db.cursor()
    cursor.execute('''SELECT IDUser FROM User WHERE Pseudo = ?''', (owner,))
    result = cursor.fetchone()
    if result:
        print('L\'utilisateur existe déja !')
        return result[0]
    else:
        print('L\'utilisateur n\'existe pas !')
        cursor.execute('''INSERT INTO User (Pseudo) VALUES (?)''', (owner,))
        db.commit()
        return cursor.lastrowid


# Ajoute une relique dans la BDD en INSERT/UPDATE (3-4 queries)
def add_relic_to_db(a1, a2, a3, a4, owner):
    cursor = db.cursor()
    relic_owner = check_user_exist(owner)
    cursor.execute('''SELECT IDRelic FROM Relic WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (a2, a1, a3, relic_owner,))
    result = cursor.fetchone()
    if result:
        print('La relique existe déja !')
        cursor.execute('''UPDATE Relic SET Quantity = Quantity + ? WHERE Name = ? AND Era = ? AND Quality = ? AND IDOwner = ?''', (a4, a2, a1, a3, relic_owner,))
    else:
        cursor.execute('''INSERT INTO Relic (Era, Name, Quality, Quantity, IDOwner) VALUES (?,?,?,?,?)''', (a1, a2, a3, a4, relic_owner))
    db.commit()

###############################################################################################
# Bot-commands ###############################################################################


prefix = "!"
bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_ready():
    print("Bot est dans la place !")
    await bot.change_presence(activity=discord.Game("JE TRAVAILLE OK"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "Hello":
        await message.channel.send("Yo !")
    if message.content == "Jour ?":
        await message.channel.send("Nuit")
    if message.content == "Clem ?":
        await message.channel.send("GRAKATA")
    if message.content == "Demokdawa":
        await message.channel.send("LE DIEU !")
    if message.content == "A Kadoc ?":
        await message.channel.send("Il dit que c'est a lui de jouer...")
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("FINIS LA COMMANDE BATAR")


@bot.command()
async def ping(ctx):
    latency = bot.latency
    print("le ping marche !")
    await ctx.send(latency)


@bot.command()
async def index(ctx):
    await ctx.send('https://docs.google.com/document/d/1zRJiGvXl1rY21ri0DuirK7BovAsBw1ikc0qCLChx7gw/edit?usp=sharing')


@bot.command()
async def relicadd(ctx, a1: spell_correct, a2: spell_correct, a3: spell_correct, a4: int):
    if number_check(a4) is True:
        if syntax_check_pass(a1, a2, a3) is True:
            add_relic_to_db(a1, a2, a3, a4, clean_disctag(str(ctx.message.author)))
            new_quantity = check_relic_quantity(a1, a2, a3, clean_disctag(str(ctx.message.author)))
            await ctx.send('Votre relique est une {} {} {}, que vous possedez dorénavant en {} exemplaire(s)'.format(a1, a2, a3, new_quantity))
        else:
            await ctx.send(syntax_check_pass(a1, a2, a3))
    else:
        await ctx.send('{} ? Ton mensonge ne trompe personne jeune Tenno !'.format(a4))

bot.run("NTg0NzYzODUyMzc0NDA5MjE5.XPUA6g.WC1uUgEvEIx8oEZP_g2Ry-7L6PE")

