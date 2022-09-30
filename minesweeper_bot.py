import nextcord as discord
from nextcord.ext import commands
from minesweeper_class import minesweeper
from connect4_class import connect4
from othello_class import othello
from mastermind_class import mastermind
from yahtzee_class import yahtzee
from battleship_class import battleship
from hangman_class import hangman
from uno_class import uno as uno_c
from wordle_class import wordle
from tzfe_class import tzfe as tzfe_c
from records import global_leaderboard, server_leaderboard, privacy_change, delete_record, theme_change, get_theme, member_count, change_stats, get_stats
from records import profile as uprofile
import asyncio
import os
import random as rd
import requests
import pandas as pd
import matplotlib.pyplot as plt
from nextcord.utils import get
import dbots
import statcord

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix = ";", intents = intents, help_command = None, case_insensitive = True)
token = os.getenv("DISCORD_TOKEN")
topgg_token = os.getenv("TOPGG_TOKEN")
discords_token = os.getenv("DISCORDS_TOKEN")
discordlabs_token = os.getenv("DISCORDLABS_TOKEN")
discordbots_token = os.getenv("DISCORDBOTS_TOKEN")
discordbotlist_token = os.getenv("DISCORDBOTLIST_TOKEN")
statcord_token = os.getenv("STATCORD_TOKEN")
dbots_client = dbots.ClientPoster(bot, "discord.py", api_keys = {"top.gg": topgg_token, "discords.com": discords_token, "discordlabs.org": discordlabs_token, "discord.bots.gg": discordbots_token, "discordbotlist.com": discordbotlist_token})
statcord_client = statcord.Client(bot, statcord_token)
statcord_client.start_loop()

in_game = []
live_battles = {}
tourney_channels = []
live_uno = {}

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Game(name = "Minesweeper | ;help"))
    print("Ready for takeoff!")
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("I'm in "+str(len(bot.guilds))+" servers!")
    bot_count = bot.get_channel(948144061305479198)
    await bot_count.edit(name = f"Servers: {len(bot.guilds)}")
    await dbots_client.post()
    dbots_client.start_loop()

@bot.event
async def on_guild_join(guild: discord.Guild):
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("New server: "+str(guild))
    new_server = discord.Embed(title = "Thanks for inviting me!", description = "Hey there! Thanks a lot for inviting me to your server! Here are a few commands and links you should check out first (the prefix for all commands is `;`):", colour = discord.Colour.blue())
    new_server.add_field(name = "Commands", value = '''
`;help`: Open the help page (probably the first thing you should do!)
`;ms`: Start a new 8x8 minesweeper game with 8 bombs
`;other`: View other games that can be played on the bot!
''')
    new_server.add_field(name = "Important links", value = '''
[Support Server](https://discord.gg/3jCG74D3RK): Get some help with any queries that you have!
[Invite](https://discord.com/oauth2/authorize?client_id=902498109270134794&permissions=274878188608&scope=bot%20applications.commands): Invite the bot to another server!
[Website](https://minesweeper-bot.carrd.co): Check out our website!
[Vote for Us!](https://top.gg/bot/902498109270134794/vote): Vote for us on `top.gg`!
''')
    channel = guild.system_channel
    if channel != None:
        try:
            await channel.send(embed = new_server)
        except discord.errors.Forbidden:
            pass
    bot_count = bot.get_channel(948144061305479198)
    await bot_count.edit(name = f"Servers: {len(bot.guilds)}")

@bot.event
async def on_guild_remove(guild: discord.Guild):
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("Removed from: "+str(guild))
    bot_count = bot.get_channel(948144061305479198)
    await bot_count.edit(name = f"Servers: {len(bot.guilds)}")

@bot.event
async def on_command_error(mess: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        logs = bot.get_channel(1018406288885039154)
        description = f"Normal command\n\nChannel: <#{mess.channel.id}>\nUser: <@!{mess.author.id}>\nServer: {mess.guild.name} ({mess.guild.id})\n\nError:\n```{error}```"
        if "Cannot send messages to this user" in str(error):
            await mess.channel.send("One of the players has not allowed DMs from the bot so the game has been cancelled")
        await logs.send(description)

@bot.event
async def on_application_command_error(mess: discord.Interaction, error):
    logs = bot.get_channel(1018406288885039154)
    description = f"Slash command\n\nChannel: <#{mess.channel.id}>\nUser: <@!{mess.user.id}>\nServer: {mess.guild.name} ({mess.guild.id})\n\nError:\n```{error}```"
    if "Cannot send messages to this user" in str(error):
        await mess.channel.send("One of the players has not allowed DMs from the bot so the game has been cancelled")
    await logs.send(description)

@bot.event
async def on_thread_join(thread: discord.Thread):
    await thread.join()

@bot.command(name = "ms", description = "Start an 8x8 minesweeper game with 8 bombs", aliases = ["minesweeper"])
async def ms(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("minesweeper")
    if msg == ";minesweeper" or msg == ";ms":
        author_id = mess.author.id
        if author_id not in in_game:
            play = minesweeper(8, 8, 8, author_id, "no", get_theme(author_id))
            game_init = discord.Embed(title=author+"'s minesweeper game", description='''
            You do not have to use ; while playing
            '''
            + play.str_row, color=discord.Color.blue())
            await mess.channel.send(embed=game_init)
            in_game.append(author_id)
            while play.game == 1:
                while True:
                    while True:
                        await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                        try:
                            pos_msg = await bot.wait_for("message", check=lambda m: m.author == mess.author and m.channel == mess.channel, timeout = 30.0)
                        except asyncio.TimeoutError:
                            play.end_msg = "You took too long to respond so the game has ended 😢"
                            message = "quit"
                            play.game = 0
                            break
                        try:
                            message = pos_msg.content
                            r, c = map(int, message.split())
                            if r <= 0 or r > play.num_rows:
                                await mess.channel.send("Row is out of range")
                            elif c <= 0 or c > play.num_cols:
                                await mess.channel.send("Column is out of range")
                            else:
                                break
                        except ValueError:
                            message = str(pos_msg.content).lower()
                            if message == "flag":
                                if play.flag_var == 0:
                                    await mess.channel.send("Flag mode on")
                                    play.flag_var = 1
                                else:
                                    await mess.channel.send("Flag mode off")
                                    play.flag_var = 0
                            elif message == "board":
                                if play.flag_var == 1:
                                    play.flag = "On"
                                else:
                                    play.flag = "Off"

                                game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag+
                                '''
                                '''
                                + play.str_row, color=discord.Color.blue())
                                await mess.channel.send(embed=game_real)
                            elif message == "quit":
                                play.game = 0
                                play.end_msg = "I'm sorry to see you leave 😢"
                                break
                            else:
                                await mess.channel.send("Invalid input")

                    if message == "quit":
                        break

                    try:
                        play.guess(r, c)
                    except UnboundLocalError:
                        await mess.channel.send("That position is already occupied")
                    else:
                        play.moves += 1
                        break
                if message != "quit":
                    if play.flag_var == 1:
                        play.flag = "On"
                    else:
                        play.flag = "Off"

                    game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag +
                    '''
                    '''
                    + play.str_row, color=discord.Color.blue())
                    await mess.channel.send(embed=game_real)
            await mess.channel.send(play.end_msg)
            in_game.remove(author_id)
        else:
            await mess.channel.send("You're already in a game!")
    
    else:
        if not(isinstance(mess.channel, discord.DMChannel)):
            valid_id = 0
            if msg.startswith(";minesweeper <@!") and msg.endswith(">"):
                opp_id_temp = msg.replace(";minesweeper <@!", "")
                opp_id = opp_id_temp.replace(">", "")
                try:
                    int(opp_id)
                    valid_id = 1
                except ValueError:
                    pass
            elif msg.startswith(";ms <@!") and msg.endswith(">"):
                opp_id_temp = msg.replace(";ms <@!", "")
                opp_id = opp_id_temp.replace(">", "")
                try:
                    int(opp_id)
                    valid_id = 1
                except ValueError:
                    pass
            elif msg.startswith(";minesweeper <@") and msg.endswith(">"):
                opp_id_temp = msg.replace(";minesweeper <@", "")
                opp_id = opp_id_temp.replace(">", "")
                try:
                    int(opp_id)
                    valid_id = 1
                except ValueError:
                    pass
            elif msg.startswith(";ms <@") and msg.endswith(">"):
                opp_id_temp = msg.replace(";ms <@", "")
                opp_id = opp_id_temp.replace(">", "")
                try:
                    int(opp_id)
                    valid_id = 1
                except ValueError:
                    pass
            if valid_id == 1:
                opp_id = int(opp_id)
                try:
                    a_id = mess.author.id
                    me = await bot.fetch_user(a_id)
                    opponent = await bot.fetch_user(opp_id)
                    server_id = mess.guild.id
                    guild = bot.get_guild(server_id)
                    members = []
                    for m in guild.members:
                        members.append(m)
                    if opponent in members and opponent != me and not(opponent.bot):
                        if a_id not in in_game and opp_id not in in_game:
                            want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of minesweeper! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                            want_play = await mess.channel.send(embed = want_play_embed)
                            await want_play.add_reaction("✅")
                            await want_play.add_reaction("❌")
                            in_game.append(a_id)
                            in_game.append(opp_id)
                            try:
                                reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                            except asyncio.TimeoutError:
                                await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                            else:
                                if str(reaction.emoji) == "✅":
                                    player_1 = minesweeper(8, 8, 8, a_id, "yes", get_theme(a_id))
                                    player_2 = minesweeper(8, 8, 8, opp_id, "yes", get_theme(opp_id))
                                    turn = 0
                                    while player_1.game == 1 and player_2.game == 1:
                                        if turn == 0:
                                            await mess.channel.send(f"<@!{a_id}> it's your turn")
                                            game_init_1 = discord.Embed(title=me.name+"'s minesweeper game", description='''
                                            You do not have to use ; while playing
                                            '''
                                            + player_1.str_row, color=discord.Color.blue())
                                            
                                            await mess.channel.send(embed=game_init_1)
                                            while True:
                                                while True:
                                                    await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                                                    try:
                                                        pos_msg = await bot.wait_for("message", check=lambda m: m.author.id == a_id and m.channel == mess.channel, timeout = 30.0)
                                                    except asyncio.TimeoutError:
                                                        player_1.end_msg = "You took too long to respond so the game has ended 😢"
                                                        message = "quit"
                                                        break
                                                    try:
                                                        message = pos_msg.content
                                                        r, c = map(int, message.split())
                                                        if r <= 0 or r > player_1.num_rows:
                                                            await mess.channel.send("Row is out of range")
                                                        elif c <= 0 or c > player_1.num_cols:
                                                            await mess.channel.send("Column is out of range")
                                                        else:
                                                            break
                                                    except ValueError:
                                                        message = str(pos_msg.content).lower()
                                                        if message == "flag":
                                                            if player_1.flag_var == 0:
                                                                await mess.channel.send("Flag mode on")
                                                                player_1.flag_var = 1
                                                            else:
                                                                await mess.channel.send("Flag mode off")
                                                                player_1.flag_var = 0
                                                        elif message == "board":
                                                            if player_1.flag_var == 1:
                                                                player_1.flag = "On"
                                                            else:
                                                                player_1.flag = "Off"

                                                            game_real = discord.Embed(title=me.name+"'s minesweeper game", description="Flag mode: "+player_1.flag+
                                                            '''
                                                            '''
                                                            + player_1.str_row, color=discord.Color.blue())
                                                            
                                                            await mess.channel.send(embed=game_real)
                                                        elif message == "quit":
                                                            player_1.game = 0
                                                            player_1.end_msg = "I'm sorry to see you leave 😢"
                                                            break
                                                        else:
                                                            await mess.channel.send("Invalid input")

                                                if message == "quit":
                                                    break

                                                try:
                                                    player_1.guess(r, c)
                                                    break
                                                except UnboundLocalError:
                                                    await mess.channel.send("That position is already occupied")
                                            if message != "quit":
                                                if player_1.flag_var == 1:
                                                    player_1.flag = "On"
                                                else:
                                                    player_1.flag = "Off"

                                                game_real = discord.Embed(title=me.name+"'s minesweeper game", description="Flag mode: "+player_1.flag +
                                                '''
                                                '''
                                                + player_1.str_row, color=discord.Color.blue())
                                                
                                                await mess.channel.send(embed=game_real)
                                            else:
                                                player_1.game = 0
                                                player_1.game_over = 1
                                            turn = 1

                                        else:
                                            await mess.channel.send(f"<@!{opp_id}> it's your turn")
                                            game_init_2 = discord.Embed(title=opponent.name+"'s minesweeper game", description='''
                                            You do not have to use ; while playing
                                            '''
                                            + player_2.str_row, color=discord.Color.blue())
                                            
                                            await mess.channel.send(embed=game_init_2)
                                            while True:
                                                while True:
                                                    await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                                                    try:
                                                        pos_msg = await bot.wait_for("message", check=lambda m: m.author.id == opp_id and m.channel == mess.channel, timeout = 30.0)
                                                    except asyncio.TimeoutError:
                                                        player_2.end_msg = "You took too long to respond so the game has ended 😢"
                                                        message = "quit"
                                                        break
                                                    try:
                                                        message = pos_msg.content
                                                        r, c = map(int, message.split())
                                                        if r <= 0 or r > player_2.num_rows:
                                                            await mess.channel.send("Row is out of range")
                                                        elif c <= 0 or c > player_2.num_cols:
                                                            await mess.channel.send("Column is out of range")
                                                        else:
                                                            break
                                                    except ValueError:
                                                        message = str(pos_msg.content).lower()
                                                        if message == "flag":
                                                            if player_2.flag_var == 0:
                                                                await mess.channel.send("Flag mode on")
                                                                player_2.flag_var = 1
                                                            else:
                                                                await mess.channel.send("Flag mode off")
                                                                player_2.flag_var = 0
                                                        elif message == "board":
                                                            if player_2.flag_var == 1:
                                                                player_2.flag = "On"
                                                            else:
                                                                player_2.flag = "Off"

                                                            game_real = discord.Embed(title=opponent.name+"'s minesweeper game", description="Flag mode: "+player_2.flag+
                                                            '''
                                                            '''
                                                            + player_2.str_row, color=discord.Color.blue())
                                                            
                                                            await mess.channel.send(embed=game_real)
                                                        elif message == "quit":
                                                            player_2.game = 0
                                                            player_2.end_msg = "I'm sorry to see you leave 😢"
                                                            break
                                                        else:
                                                            await mess.channel.send("Invalid input")

                                                if message == "quit":
                                                    break

                                                try:
                                                    player_2.guess(r, c)
                                                    break
                                                except UnboundLocalError:
                                                    await mess.channel.send("That position is already occupied")
                                            if message != "quit":
                                                if player_2.flag_var == 1:
                                                    player_2.flag = "On"
                                                else:
                                                    player_2.flag = "Off"

                                                game_real = discord.Embed(title=opponent.name+"'s minesweeper game", description="Flag mode: "+player_2.flag +
                                                '''
                                                '''
                                                + player_2.str_row, color=discord.Color.blue())
                                                
                                                await mess.channel.send(embed=game_real)
                                            else:
                                                player_2.game = 0
                                                player_2.game_over = 1
                                            turn = 0

                                    if player_1.game_over == 1:
                                        await mess.channel.send(player_1.end_msg)
                                        await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                                        
                                        
                                    elif player_2.game_over == 1:
                                        await mess.channel.send(player_2.end_msg)
                                        await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                                        
                                        
                                    elif player_1.game_won == 1:
                                        await mess.channel.send(player_1.end_msg)
                                        await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                                        
                                        
                                    elif player_2.game_won == 1:
                                        await mess.channel.send(player_2.end_msg)
                                        await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                                        
                                else:
                                    await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                            in_game.remove(a_id)
                            in_game.remove(opp_id)
                        else:
                            if a_id in in_game:
                                await mess.channel.send("You're already in a game!")
                            else:
                                await mess.channel.send("Your opponent is already in a game!")
                                
                                

                    else:
                        if opponent != me and not(opponent.bot):
                            dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                            await mess.channel.send(embed = dual_game)
                            
                            
                except discord.errors.NotFound:
                    dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                    await mess.channel.send(embed = dual_game)
                    
                    
            else:
                dual_game = discord.Embed(title = "Invalid syntax!", description = "The minesweeper syntax is invalid! The correct syntax is: ;minesweeper/;ms @user", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                
                
        else:
            await mess.channel.send("You can't play a match against someone in a DM!")

@bot.command(name = "mscustom", description = "Start a custom minesweeper game", aliases = ["minesweepercustom"])
async def mscustom(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("minesweeper_custom")
    author_id = mess.author.id
    if author_id not in in_game:
        in_game.append(author_id)
        while True:
            while True:
                await mess.channel.send("Enter the number of rows")
                num_rows_msg = await bot.wait_for("message", check=lambda m: m.author == mess.author and m.channel == mess.channel)
                try:
                    num_rows = int(num_rows_msg.content)
                    if num_rows <= 1:
                        await mess.channel.send("You have too less rows")
                    else:
                        break
                except ValueError:
                    await mess.channel.send("Invalid input")

            while True:
                await mess.channel.send("Enter the number of columns")
                num_cols_msg = await bot.wait_for("message", check=lambda m: m.author == mess.author and m.channel == mess.channel)
                try:
                    num_cols = int(num_cols_msg.content)
                    if num_cols <= 1:
                        await mess.channel.send("You have too less columns")
                    elif num_cols+len(str(num_rows))+1 > 27:
                        await mess.channel.send("You have too many columns")
                    else:
                        break
                except ValueError:
                    await mess.channel.send("Invalid input")

            while True:
                await mess.channel.send("Enter the number of bombs")
                num_bombs_msg = await bot.wait_for("message", check=lambda m: m.author == mess.author and m.channel == mess.channel)
                try:
                    num_bombs = int(num_bombs_msg.content)
                    if num_bombs >= (num_rows*num_cols):
                        await mess.channel.send("You have too many bombs")
                    elif num_bombs <= 0:
                        await mess.channel.send("You have too less bombs")
                    else:
                        break
                except ValueError:
                    await mess.channel.send("Invalid input")

            play = minesweeper(num_rows, num_cols, num_bombs, author_id, "no", get_theme(author_id))
            if play.items_tot+((((len(str(num_rows))+1)*num_rows))+((len(str(num_cols))+1)*num_cols)+((len(str(num_rows))+1)*(len(str(num_cols))+1))) > 198:
                await mess.channel.send("Your grid is too big (you can have only a max of 198 objects (row and column numbers included))")
            else:
                break
        game_init = discord.Embed(title=author+"'s minesweeper game", description='''
        You do not have to use ; while playing
        '''
        + play.str_row, color=discord.Color.blue())
        await mess.channel.send(embed=game_init)
        while play.game == 1:
            while True:
                while True:
                    await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                    try:
                        pos_msg = await bot.wait_for("message", check=lambda m: m.author == mess.author and m.channel == mess.channel, timeout = 30.0)
                    except asyncio.TimeoutError:
                        play.end_msg = "You took too long to respond so the game has ended 😢"
                        message = "quit"
                        play.game = 0
                        break
                    try:
                        message = pos_msg.content
                        r, c = map(int, message.split())
                        if r <= 0 or r > play.num_rows:
                            await mess.channel.send("Row is out of range")
                        elif c <= 0 or c > play.num_cols:
                            await mess.channel.send("Column is out of range")
                        else:
                            break
                    except ValueError:
                        message = str(pos_msg.content).lower()
                        if message == "flag":
                            if play.flag_var == 0:
                                await mess.channel.send("Flag mode on")
                                play.flag_var = 1
                            else:
                                await mess.channel.send("Flag mode off")
                                play.flag_var = 0
                        elif message == "board":
                            if play.flag_var == 1:
                                play.flag = "On"
                            else:
                                play.flag = "Off"

                            game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag+
                            '''
                            '''
                            + play.str_row, color=discord.Color.blue())
                            await mess.channel.send(embed=game_real)
                        elif message == "quit":
                            play.game = 0
                            play.end_msg = "I'm sorry to see you leave 😢"
                            break
                        else:
                            await mess.channel.send("Invalid input")

                if message == "quit":
                    break

                try:
                    play.guess(r, c)
                    break
                except UnboundLocalError:
                    await mess.channel.send("That position is already occupied")
            if message != "quit":
                if play.flag_var == 1:
                    play.flag = "On"
                else:
                    play.flag = "Off"

                game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag +
                '''
                '''
                + play.str_row, color=discord.Color.blue())
                await mess.channel.send(embed=game_real)
        await mess.channel.send(play.end_msg)
        in_game.remove(author_id)
    else:
        await mess.channel.send("You're already in a game!")

@bot.command(name = "tournament", description = "Starts a minesweeper tournament")
async def tournament(mess: commands.Context):
    global in_game, tourney_channels
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("tournament")
    if not(isinstance(mess.channel, discord.DMChannel)):
        host_id = mess.author.id
        if host_id not in in_game and mess.channel.id not in tourney_channels:
            tourney_channels.append(mess.channel.id)
            thumb = bot.get_emoji(935120796358152212)
            check = bot.get_emoji(935455988516028486)
            winner = bot.get_emoji(935794255543275541)
            yay = bot.get_emoji(951716865049247855)
            tourney_members = [host_id]
            tourney_init_embed = discord.Embed(title = "Tournament started!", description = f"<@!{host_id}> started a tournament! React with {thumb} below or type `;join` to join! Remove your reaction or type `;leave` to leave. <@!{host_id}> react with {check} or type `;start` to start the tournament!", colour = discord.Colour.blue())
            tourney_init = await mess.channel.send(embed = tourney_init_embed)
            await tourney_init.add_reaction(str(thumb))
            await tourney_init.add_reaction(str(check))
            in_game.append(host_id)
            while True:
                decisions = [asyncio.create_task(bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) in [str(thumb), str(check)] and p != bot.user and r.message.id == tourney_init.id, timeout = 60.0), name = "radd"), asyncio.create_task(bot.wait_for("reaction_remove", check = lambda r, p: str(r.emoji) == str(thumb) and p != bot.user and r.message.id == tourney_init.id, timeout = 60.0), name = "rrem"), asyncio.create_task(bot.wait_for("message", check = lambda m: m.channel == mess.channel, timeout = 60.0), name = "msgd")]

                completed, pending = await asyncio.wait(decisions, return_when = asyncio.FIRST_COMPLETED)
                
                finished_task: asyncio.Task = list(completed)[0]
                
                for unfinished in pending:
                    try:
                        unfinished.cancel()
                    except asyncio.CancelledError:
                        pass

                action = finished_task.get_name()
                try:
                    result = finished_task.result()
                except asyncio.TimeoutError:
                    break

                else:
                    if action == "radd":
                        reaction, user = result
                        reaction_e = str(reaction.emoji)
                        if reaction_e == str(thumb) and user.id != host_id and user.id not in tourney_members:
                            if user.id not in in_game:
                                await mess.channel.send(f"<@!{user.id}> has joined the tournament {yay}")
                                tourney_members.append(user.id)
                                in_game.append(user.id)
                            else:
                                await mess.channel.send(f"<@!{user.id}>, you're already in a game!")
                        elif reaction_e == str(check) and user.id == host_id:
                            break
                    elif action == "rrem":
                        reaction, user = result
                        reaction_e = str(reaction.emoji)
                        if reaction_e == str(thumb) and user.id != host_id and user.id in tourney_members:
                            await mess.channel.send(f"<@!{user.id}> has left the tournament 😢")
                            tourney_members.remove(user.id)
                            in_game.remove(user.id)
                    elif action == "msgd":
                        jl_msg = str(result.content)
                        user = result.author
                        if jl_msg == ";join" and user.id not in tourney_members and user.id != host_id:
                            if user.id not in in_game:
                                await mess.channel.send(f"<@!{user.id}> has joined the tournament {yay}")
                                tourney_members.append(user.id)
                                in_game.append(user.id)
                            else:
                                await mess.channel.send(f"<@!{user.id}>, you're already in a game!")
                        elif jl_msg == ";leave" and user.id in tourney_members and user.id != host_id:
                            await mess.channel.send(f"<@!{user.id}> has left the tournament 😢")
                            tourney_members.remove(user.id)
                            in_game.remove(user.id)
                        elif jl_msg == ";start" and user.id == host_id:
                            break
            tourney_members = list(set(tourney_members))
            mem_str = "Tournament participants:"
            for mem in tourney_members:
                mem_str += f'''
<@!{mem}>'''
            await mess.channel.send(mem_str)
            round = 1
            match = 1
            while len(tourney_members) > 1:
                pairings = []
                tourney_members_temp = list(tourney_members)
                while tourney_members_temp != []:
                    p1 = rd.choice(tourney_members_temp)
                    tourney_members_temp.remove(p1)
                    if tourney_members_temp != []:
                        p2 = rd.choice(tourney_members_temp)
                        tourney_members_temp.remove(p2)
                    else:
                        p2 = "Bye"
                    pairings.append((p1, p2))
                pairings_list_str = ""
                for pai in pairings:
                    if pai[1] != "Bye":
                        pairings_list_str += f'''<@!{pai[0]}> --------------------- <@!{pai[1]}>
'''
                    else:
                        pairings_list_str += f'''<@!{pai[0]}> --------------------- Bye
'''
                pairings_list = discord.Embed(title = f"Round {round} pairings", description = pairings_list_str, colour = discord.Colour.blue())
                await mess.channel.send(embed = pairings_list)
                for mat in range(len(pairings)):
                    if pairings[match-1][1] != "Bye":
                        match_init_embed = discord.Embed(title = f"Match {match}", description = f"<@!{pairings[match-1][0]}> VS <@!{pairings[match-1][1]}>", colour = discord.Color.blue())
                        await mess.channel.send(embed = match_init_embed)
                        me = await bot.fetch_user(pairings[match-1][0])
                        opponent = await bot.fetch_user(pairings[match-1][1])
                        a_id = me.id
                        opp_id = opponent.id
                        standby = await mess.channel.send(f"<@!{a_id}> and <@!{opp_id}> on standby! React with {thumb} to get ready!")
                        await standby.add_reaction(str(thumb))
                        p1_ready = False
                        p2_ready = False
                        pairing_temp = list(pairings[match-1])
                        while not (p1_ready and p2_ready):
                            try:
                                reaction, user = await bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) == str(thumb) and p.id in pairing_temp and r.message.id == standby.id, timeout = 60.0)
                            except asyncio.TimeoutError:
                                break
                            else:
                                if user.id == pairings[match-1][0]:
                                    p1_ready = True
                                    await mess.channel.send(f"<@!{pairings[match-1][0]}> is ready!")
                                    pairing_temp.remove(pairings[match-1][0])
                                elif user.id == pairings[match-1][1]:
                                    p2_ready = True
                                    await mess.channel.send(f"<@!{pairings[match-1][1]}> is ready!")
                                    pairing_temp.remove(pairings[match-1][1])
                        player_1 = minesweeper(8, 8, 8, a_id, "yes", get_theme(a_id))
                        player_2 = minesweeper(8, 8, 8, opp_id, "yes", get_theme(opp_id))
                        turn = 0
                        while player_1.game == 1 and player_2.game == 1:
                            if turn == 0:
                                await mess.channel.send(f"<@!{a_id}> it's your turn")
                                game_init_1 = discord.Embed(title=me.name+"'s minesweeper game", description='''
                                You do not have to use ; while playing
                                '''
                                + player_1.str_row, color=discord.Color.blue())
                                
                                await mess.channel.send(embed=game_init_1)
                                while True:
                                    while True:
                                        await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                                        try:
                                            pos_msg = await bot.wait_for("message", check=lambda m: m.author.id == a_id and m.channel == mess.channel, timeout = 60.0)
                                        except asyncio.TimeoutError:
                                            player_1.end_msg = "You took too long to respond so the game has ended 😢"
                                            message = "quit"
                                            break
                                        try:
                                            message = pos_msg.content
                                            r, c = map(int, message.split())
                                            if r <= 0 or r > player_1.num_rows:
                                                await mess.channel.send("Row is out of range")
                                            elif c <= 0 or c > player_1.num_cols:
                                                await mess.channel.send("Column is out of range")
                                            else:
                                                break
                                        except ValueError:
                                            message = str(pos_msg.content).lower()
                                            if message == "flag":
                                                if player_1.flag_var == 0:
                                                    await mess.channel.send("Flag mode on")
                                                    player_1.flag_var = 1
                                                else:
                                                    await mess.channel.send("Flag mode off")
                                                    player_1.flag_var = 0
                                            elif message == "board":
                                                if player_1.flag_var == 1:
                                                    player_1.flag = "On"
                                                else:
                                                    player_1.flag = "Off"

                                                game_real = discord.Embed(title=me.name+"'s minesweeper game", description="Flag mode: "+player_1.flag+
                                                '''
                                                '''
                                                + player_1.str_row, color=discord.Color.blue())
                                                
                                                await mess.channel.send(embed=game_real)
                                            elif message == "quit":
                                                player_1.game = 0
                                                player_1.end_msg = "I'm sorry to see you leave 😢"
                                                break
                                            else:
                                                await mess.channel.send("Invalid input")

                                    if message == "quit":
                                        break

                                    try:
                                        player_1.guess(r, c)
                                        break
                                    except UnboundLocalError:
                                        await mess.channel.send("That position is already occupied")
                                if message != "quit":
                                    if player_1.flag_var == 1:
                                        player_1.flag = "On"
                                    else:
                                        player_1.flag = "Off"

                                    game_real = discord.Embed(title=me.name+"'s minesweeper game", description="Flag mode: "+player_1.flag +
                                    '''
                                    '''
                                    + player_1.str_row, color=discord.Color.blue())
                                    
                                    await mess.channel.send(embed=game_real)
                                else:
                                    player_1.game = 0
                                    player_1.game_over = 1
                                turn = 1

                            else:
                                await mess.channel.send(f"<@!{opp_id}> it's your turn")
                                game_init_2 = discord.Embed(title=opponent.name+"'s minesweeper game", description='''
                                You do not have to use ; while playing
                                '''
                                + player_2.str_row, color=discord.Color.blue())
                                
                                await mess.channel.send(embed=game_init_2)
                                while True:
                                    while True:
                                        await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                                        try:
                                            pos_msg = await bot.wait_for("message", check=lambda m: m.author.id == opp_id and m.channel == mess.channel, timeout = 60.0)
                                        except asyncio.TimeoutError:
                                            player_2.end_msg = "You took too long to respond so the game has ended 😢"
                                            message = "quit"
                                            break
                                        try:
                                            message = pos_msg.content
                                            r, c = map(int, message.split())
                                            if r <= 0 or r > player_2.num_rows:
                                                await mess.channel.send("Row is out of range")
                                            elif c <= 0 or c > player_2.num_cols:
                                                await mess.channel.send("Column is out of range")
                                            else:
                                                break
                                        except ValueError:
                                            message = str(pos_msg.content).lower()
                                            if message == "flag":
                                                if player_2.flag_var == 0:
                                                    await mess.channel.send("Flag mode on")
                                                    player_2.flag_var = 1
                                                else:
                                                    await mess.channel.send("Flag mode off")
                                                    player_2.flag_var = 0
                                            elif message == "board":
                                                if player_2.flag_var == 1:
                                                    player_2.flag = "On"
                                                else:
                                                    player_2.flag = "Off"

                                                game_real = discord.Embed(title=opponent.name+"'s minesweeper game", description="Flag mode: "+player_2.flag+
                                                '''
                                                '''
                                                + player_2.str_row, color=discord.Color.blue())
                                                
                                                await mess.channel.send(embed=game_real)
                                            elif message == "quit":
                                                player_2.game = 0
                                                player_2.end_msg = "I'm sorry to see you leave 😢"
                                                break
                                            else:
                                                await mess.channel.send("Invalid input")

                                    if message == "quit":
                                        break

                                    try:
                                        player_2.guess(r, c)
                                        break
                                    except UnboundLocalError:
                                        await mess.channel.send("That position is already occupied")
                                if message != "quit":
                                    if player_2.flag_var == 1:
                                        player_2.flag = "On"
                                    else:
                                        player_2.flag = "Off"

                                    game_real = discord.Embed(title=opponent.name+"'s minesweeper game", description="Flag mode: "+player_2.flag +
                                    '''
                                    '''
                                    + player_2.str_row, color=discord.Color.blue())
                                    
                                    await mess.channel.send(embed=game_real)
                                else:
                                    player_2.game = 0
                                    player_2.game_over = 1
                                turn = 0

                        if player_1.game_over == 1:
                            await mess.channel.send(player_1.end_msg)
                            tourney_members.remove(a_id)
                            in_game.remove(a_id)
                            await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                        elif player_2.game_over == 1:
                            await mess.channel.send(player_2.end_msg)
                            tourney_members.remove(opp_id)
                            in_game.remove(opp_id)
                            await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                        elif player_1.game_won == 1:
                            await mess.channel.send(player_1.end_msg)
                            tourney_members.remove(opp_id)
                            in_game.remove(opp_id)
                            await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                        elif player_2.game_won == 1:
                            await mess.channel.send(player_2.end_msg)
                            tourney_members.remove(a_id)
                            in_game.remove(a_id)
                            await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                        match += 1
                        await asyncio.sleep(5)
                    
                    else:
                        match = 1
                        await asyncio.sleep(5)
                round += 1
                match = 1
            await mess.channel.send(f"<@!{tourney_members[0]}> is the winner of the tournament! {winner}")
            in_game.remove(tourney_members[0])
            tourney_channels.remove(mess.channel.id)
        else:
            if mess.channel.id not in tourney_channels:
                await mess.channel.send("You're already in a game!")
            else:
                await mess.channel.send("There is already a tournament going on in this channel!")
        
        

    else:
        await mess.channel.send("You can't start a tournament in a DM!")

@bot.command(name = "lb", description = "View the global leaderboard", aliases = ["leaderboard"])
async def lb(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("leaderboard")
    page = 1
    while True:
        if page == 1:
            leaders = global_leaderboard("best_time")
            leaders_str = ""
            for user in leaders:
                if user[1] != None:
                    time_mins = int(user[1]//60)
                    time_secs = int(user[1]%60)
                    if user == leaders[0]:
                        leaders_str += "🥇"
                    elif user == leaders[1]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        else:
                            leaders_str += "🥈"
                    elif user == leaders[2]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        else:
                            leaders_str += "🥉"
                    else:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        elif user[1] == leaders[2][1]:
                            leaders_str += "🥉"
                        else:
                            leaders_str += "👏"
                    leaders_str += "<@!"+str(user[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                    leaders_str += '''
'''
            global_lb = discord.Embed(title="Fastest times", description = leaders_str, colour=discord.Color.blue())
            global_lb.set_footer(text = "Global leaderboard 1/3")
            try:
                await lb.delete()
            except UnboundLocalError:
                pass
            lb = await mess.channel.send(embed=global_lb)
            await lb.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "▶" and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 2

        elif page == 2:
            leaders = global_leaderboard("avg_time")
            leaders_str = ""
            for user in leaders:
                if user[1] != None:
                    time_mins = int(user[1]//60)
                    time_secs = int(user[1]%60)
                    if user == leaders[0]:
                        leaders_str += "🥇"
                    elif user == leaders[1]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        else:
                            leaders_str += "🥈"
                    elif user == leaders[2]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        else:
                            leaders_str += "🥉"
                    else:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        elif user[1] == leaders[2][1]:
                            leaders_str += "🥉"
                        else:
                            leaders_str += "👏"
                    leaders_str += "<@!"+str(user[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                    leaders_str += '''
'''
            global_lb = discord.Embed(title="Best average times", description = leaders_str, colour=discord.Color.blue())
            global_lb.set_footer(text = "Global leaderboard 2/3")
            await lb.delete()
            lb = await mess.channel.send(embed=global_lb)
            await lb.add_reaction("◀")
            await lb.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                if str(reaction.emoji) == "◀":
                    page = 1
                else:
                    page = 3
        
        elif page == 3:
            leaders = global_leaderboard("max_streak")
            leaders_str = ""
            for user in leaders:
                if user[1] != None:
                    if user == leaders[0]:
                        leaders_str += "🥇"
                    elif user == leaders[1]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        else:
                            leaders_str += "🥈"
                    elif user == leaders[2]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        else:
                            leaders_str += "🥉"
                    else:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        elif user[1] == leaders[2][1]:
                            leaders_str += "🥉"
                        else:
                            leaders_str += "👏"
                    leaders_str += "<@!"+str(user[0])+"> : "+str(user[1])
                    leaders_str += '''
'''
            global_lb = discord.Embed(title="Highest streaks", description = leaders_str, colour=discord.Color.blue())
            global_lb.set_footer(text = "Global leaderboard 3/3")
            await lb.delete()
            lb = await mess.channel.send(embed=global_lb)
            await lb.add_reaction("◀")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "◀" and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 2

@bot.command(name = "serverlb", description = "View the server leaderboard", aliases = ["serverleaderboard"])
async def serverlb(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("server_leaderboard")
    if not(isinstance(mess.channel, discord.DMChannel)):
        server_id = mess.guild.id
        guild = bot.get_guild(server_id)
        members = []
        for m in guild.members:
            members.append(m.id)
        page = 1
        while True:
            if page == 1:
                server_leaders = server_leaderboard(members, "best_time")
                sleaders_str = ""
                for member in server_leaders:
                    if member[1] != None:
                        time_mins = int(member[1]//60)
                        time_secs = int(member[1]%60)
                        if member == server_leaders[0]:
                            sleaders_str += "🥇"
                        elif member == server_leaders[1]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            else:
                                sleaders_str += "🥈"
                        elif member == server_leaders[2]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            else:
                                sleaders_str += "🥉"
                        else:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            elif member[1] == server_leaders[2][1]:
                                sleaders_str += "🥉"
                            else:
                                sleaders_str += "👏"
                        sleaders_str += "<@!"+str(member[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                        sleaders_str += '''
'''
                server_lb = discord.Embed(title="Fastest times in the server", description = sleaders_str, colour=discord.Color.blue())
                server_lb.set_footer(text = "Server leaderboard 1/3")
                try:
                    await lb.delete()
                except UnboundLocalError:
                    pass
                lb = await mess.channel.send(embed=server_lb)
                await lb.add_reaction("▶")
                try:
                    reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "▶" and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
                except asyncio.TimeoutError:
                    break
                else:
                    page = 2

            elif page == 2:
                server_leaders = server_leaderboard(members, "avg_time")
                sleaders_str = ""
                for member in server_leaders:
                    if member[1] != None:
                        time_mins = int(member[1]//60)
                        time_secs = int(member[1]%60)
                        if member == server_leaders[0]:
                            sleaders_str += "🥇"
                        elif member == server_leaders[1]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            else:
                                sleaders_str += "🥈"
                        elif member == server_leaders[2]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            else:
                                sleaders_str += "🥉"
                        else:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            elif member[1] == server_leaders[2][1]:
                                sleaders_str += "🥉"
                            else:
                                sleaders_str += "👏"
                        sleaders_str += "<@!"+str(member[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                        sleaders_str += '''
'''
                server_lb = discord.Embed(title="Best average times in the server", description = sleaders_str, colour=discord.Color.blue())
                server_lb.set_footer(text = "Server leaderboard 2/3")
                await lb.delete()
                lb = await mess.channel.send(embed=server_lb)
                await lb.add_reaction("◀")
                await lb.add_reaction("▶")
                try:
                    reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
                except asyncio.TimeoutError:
                    break
                else:
                    if str(reaction.emoji) == "◀":
                        page = 1
                    else:
                        page = 3
            
            elif page == 3:
                server_leaders = server_leaderboard(members, "max_streak")
                sleaders_str = ""
                for member in server_leaders:
                    if member[1] != None:
                        if member == server_leaders[0]:
                            sleaders_str += "🥇"
                        elif member == server_leaders[1]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            else:
                                sleaders_str += "🥈"
                        elif member == server_leaders[2]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            else:
                                sleaders_str += "🥉"
                        else:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            elif member[1] == server_leaders[2][1]:
                                sleaders_str += "🥉"
                            else:
                                sleaders_str += "👏"
                        sleaders_str += "<@!"+str(member[0])+"> : "+str(member[1])
                        sleaders_str += '''
'''
                server_lb = discord.Embed(title="Highest streaks in the server", description = sleaders_str, colour=discord.Color.blue())
                server_lb.set_footer(text = "Server leaderboard 3/3")
                await lb.delete()
                lb = await mess.channel.send(embed=server_lb)
                await lb.add_reaction("◀")
                try:
                    reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "◀" and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
                except asyncio.TimeoutError:
                    break
                else:
                    page = 2

        
        
    else:
        await mess.channel.send("This is not a server!")

@bot.command(name = "profile", description = "View anyone's profile")
async def profile(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    valid_id = 0
    inv_setting = 1
    prof_author = mess.author.id
    if msg == ";profile":
        user_id = mess.author.id
        valid_id = 1
    elif msg.startswith(";profile settings"):
        if msg == ";profile settings public":
            user_id = mess.author.id
            priv = "public"
            inv_setting = 0
            privacy_change(user_id, priv)
        elif msg == ";profile settings private":
            user_id = mess.author.id
            priv = "private"
            inv_setting = 0
            privacy_change(user_id, priv)
        else:
            inv_setting = 1
    elif msg.startswith(";profile <@!") and msg.endswith(">"):
        user_id_temp = msg.replace(";profile <@!", "")
        user_id = user_id_temp.replace(">", "")
        try:
            int(user_id)
            valid_id = 1
        except ValueError:
            pass
    elif msg.startswith(";profile <@") and msg.endswith(">"):
        user_id_temp = msg.replace(";profile <@", "")
        user_id = user_id_temp.replace(">", "")
        try:
            int(user_id)
            valid_id = 1
        except ValueError:
            pass
    if valid_id == 1:
        change_stats("user_profile") 
        prof = uprofile(int(user_id))
        try:
            u = await bot.fetch_user(user_id)
            user_handle = str(u)
            user_name = u.name
            try:
                if prof[8] == "public" or prof_author == int(user_id):
                    if prof[1] != None:
                        time_mins = int(prof[1]//60)
                        time_secs = int(prof[1]%60)
                        avg_mins = int(prof[7]//60)
                        avg_secs = int(prof[7]%60)
                    if prof[9] == "yes":
                        initialsupporter = bot.get_emoji(932908272971841536)
                        p_title = user_name+"'s profile "+str(initialsupporter)
                    else:
                        p_title = user_name+"'s profile"
                    if prof[4] >= 100:
                        hun_club = bot.get_emoji(946733351195254814)
                        p_title += " "+str(hun_club)
                    user_profile = discord.Embed(title = p_title, description = "All stats about this user on the minesweeper bot!", color = discord.Color.blue())
                    user_profile.set_thumbnail(url = u.display_avatar)
                    user_profile.add_field(name = "Discord handle:", value = "||"+user_handle+"||", inline = True)
                    if prof[1] != None:
                        user_profile.add_field(name = "Best time:", value = str(time_mins)+"m "+str(time_secs)+"s", inline = True)
                        user_profile.add_field(name = "Average winning time:", value = str(avg_mins)+"m "+str(avg_secs)+"s", inline = True)
                    else:
                        user_profile.add_field(name = "Best time:", value = prof[1], inline = True)
                        user_profile.add_field(name = "Average winning time:", value = prof[7], inline = True)
                    user_profile.add_field(name = "Games won:", value = prof[2], inline = True)
                    user_profile.add_field(name = "Games lost:", value = prof[3], inline = True)
                    user_profile.add_field(name = "Total games played:", value = prof[4], inline = True)
                    user_profile.add_field(name = "Win percentage:", value = prof[5], inline = True)
                    user_profile.add_field(name = "Current win streak:", value = prof[10], inline = True)
                    user_profile.add_field(name = "Maximum win streak:", value = prof[11], inline = True)
                    user_profile.add_field(name = "Minimum moves:", value = prof[12], inline = True)
                    user_profile.add_field(name = "Average moves:", value = prof[14], inline = True)
                    user_profile.add_field(name = "Profile type:", value = prof[8].capitalize(), inline = True)
                else:
                    user_profile = discord.Embed(title = "Private profile!", description = "This profile is private so you cannot view it!", color = discord.Color.blue())
            except TypeError:
                user_profile = discord.Embed(title = "User not detected!", description = "This user hasn't used the bot yet!", color = discord.Color.blue())
        except discord.errors.NotFound:
            user_profile = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
    elif inv_setting == 0:
        change_stats("profile_settings")
        user_profile = discord.Embed(title = "Profile settings changed!", description = "Your profile is now "+priv+"!", color = discord.Color.blue())
    else:
        user_profile = discord.Embed(title = "Invalid syntax!", description = "The profile syntax is invalid! The correct syntax is: ;profile @user", color = discord.Color.blue())
    await mess.channel.send(embed=user_profile)

@bot.command(name = "delete", description = "Delete your stats on the bot")
async def delete(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("delete_stats")
    aut_id = mess.author.id
    delete_data = await mess.channel.send("Are you sure you want to delete all of your data on this bot? React to confirm!")
    await delete_data.add_reaction("✅")
    await delete_data.add_reaction("❌")
    try:
        reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["✅", "❌"] and p.id == aut_id and r.message.id == delete_data.id, timeout = 30.0)
    except asyncio.TimeoutError:
        record_d = discord.Embed(title = "Operation cancelled!", description = "You took too long to respond so the data deletion has been cancelled!", colour = discord.Colour.blue())
        await mess.channel.send(embed = record_d)
        
        
    else:
        if str(reaction.emoji) == "✅":
            delete_record(aut_id)
            record_d = discord.Embed(title = "Data deleted", description = "All of your stats with the bot have been deleted. Play again to create new stats.", colour = discord.Colour.blue())
        else:
            record_d = discord.Embed(title = "Operation cancelled!", description = "Data deletion has been cancelled!", colour = discord.Colour.blue())
        await mess.channel.send(embed = record_d)

@bot.command(name = "theme", description = "Change your game theme")
async def theme(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("theme")
    theme = msg.replace(";theme settings ", "")
    aut_id = mess.author.id
    if theme in ["light", "dark"]:
        theme_change(aut_id, theme)
        theme_settings = discord.Embed(title = "Theme changed successfully!", description = f"Your game theme has been successfully changed to {theme} mode!", color = discord.Color.blue())
    else:
        theme_settings = discord.Embed(title = "Invalid syntax!", description = "The theme settings syntax is invalid! The correct syntax is: ;theme settings light/dark", color = discord.Color.blue())
    await mess.channel.send(embed = theme_settings)

@bot.command(name = "c4", description = "Start a game of connect 4", aliases = ["connect4"])
async def c4(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("connect_four")
    if not(isinstance(mess.channel, discord.DMChannel)):
        valid_id = 0
        if msg.startswith(";connect4 <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";connect4 <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";c4 <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";c4 <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";connect4 <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";connect4 <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";c4 <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";c4 <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        if valid_id == 1:
            opp_id = int(opp_id)
            try:
                a_id = mess.author.id
                me = await bot.fetch_user(a_id)
                opponent = await bot.fetch_user(opp_id)
                server_id = mess.guild.id
                guild = bot.get_guild(server_id)
                members = []
                for m in guild.members:
                    members.append(m)
                if opponent in members and opponent != me and not(opponent.bot):
                    if a_id not in in_game and opp_id not in in_game:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of connect 4! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
                        in_game.append(a_id)
                        in_game.append(opp_id)
                        try:
                            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                        except asyncio.TimeoutError:
                            await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                        else:
                            if str(reaction.emoji) == "✅":
                                game = connect4(a_id, opp_id, get_theme(a_id), get_theme(opp_id))
                                while game.game_end == 0:
                                    if game.turn == 0:
                                        await mess.channel.send(f"<@!{a_id}> it's your turn")
                                        game.string_rows()
                                        c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                        
                                        await mess.channel.send(embed = c4_embed)
                                        while True:
                                            await mess.channel.send("Choose the column (1-7) in which you want to drop your coin! (Type 'board' to see your current game; type 'quit' to end the game)")
                                            try:
                                                pos_msg = await bot.wait_for("message", check = lambda m: m.author.id == a_id and m.channel == mess.channel, timeout = 120.0)
                                            except asyncio.TimeoutError:
                                                await mess.channel.send("You took too long to respond so the game has ended 😢")
                                                game.game_end = 1
                                                game.winner = opp_id
                                                await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                break
                                            pos = pos_msg.content
                                            try:
                                                pos = int(pos)
                                                if not(1 <= pos <= 7):
                                                    await mess.channel.send("Column is out of range")
                                                else:
                                                    game.columns[game.columns[pos-1].index("")]
                                                    break
                                            except ValueError:
                                                try:
                                                    pos = int(pos)
                                                    await mess.channel.send("Column is full")
                                                except ValueError:
                                                    pos = str(pos).lower()
                                                    if pos == "quit":
                                                        game.game_end = 1
                                                        game.winner = opp_id
                                                        await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                        break
                                                    elif pos == "board":
                                                        c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                                        
                                                        await mess.channel.send(embed = c4_embed)
                                                    else:
                                                        await mess.channel.send("Column number can only be an integer from 1 to 7")
                                        if game.game_end == 0:
                                            game.columns[pos-1][game.columns[pos-1].index("")] = "Red"
                                            game.string_rows()
                                            c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                            await mess.channel.send(embed = c4_embed)
                                            game.turn = 1
                                            game.left_pos -= 1
                                    else:
                                        await mess.channel.send(f"<@!{opp_id}> it's your turn")
                                        game.string_rows()
                                        c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                        await mess.channel.send(embed = c4_embed)
                                        while True:
                                            await mess.channel.send("Choose the column (1-7) in which you want to drop your coin! (Type 'board' to see your current game; type 'quit' to end the game)")
                                            try:
                                                pos_msg = await bot.wait_for("message", check = lambda m: m.author.id == opp_id and m.channel == mess.channel, timeout = 120.0)
                                            except asyncio.TimeoutError:
                                                await mess.channel.send("You took too long to respond so the game has ended 😢")
                                                game.game_end = 1
                                                game.winner = a_id
                                                await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                break
                                            pos = pos_msg.content
                                            try:
                                                pos = int(pos)
                                                if not(1 <= pos <= 7):
                                                    await mess.channel.send("Column is out of range")
                                                else:
                                                    game.columns[game.columns[pos-1].index("")]
                                                    break
                                            except ValueError:
                                                try:
                                                    pos = int(pos)
                                                    await mess.channel.send("Column is full")
                                                except ValueError:
                                                    pos = str(pos).lower()
                                                    if pos == "quit":
                                                        game.game_end = 1
                                                        game.winner = a_id
                                                        await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                        break
                                                    elif pos == "board":
                                                        c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                                        
                                                        await mess.channel.send(embed = c4_embed)
                                                    else:
                                                        await mess.channel.send("Column number can only be an integer from 1 to 7")
                                        if game.game_end == 0:
                                            game.columns[pos-1][game.columns[pos-1].index("")] = "Yellow"
                                            game.string_rows()
                                            c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                            await mess.channel.send(embed = c4_embed)
                                            game.turn = 0
                                            game.left_pos -= 1
                                    if game.game_end == 0:
                                        game.game_over()
                                        if game.game_end == 1:
                                            await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                        elif game.left_pos == 0:
                                            await mess.channel.send("It's a tie ¯\_(ツ)_/¯")
                                            game.game_end = 1
                                
                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                        in_game.remove(a_id)
                        in_game.remove(opp_id)
                    else:
                        if a_id in in_game:
                            await mess.channel.send("You're already in a game!")
                        else:
                            await mess.channel.send("Your opponent is already in a game!")
                            
                            

                else:
                    if opponent != me and not(opponent.bot):
                        dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                        await mess.channel.send(embed = dual_game)
                        
                        
            except discord.errors.NotFound:
                dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                
                
        else:
            dual_game = discord.Embed(title = "Invalid syntax!", description = "The connect 4 syntax is invalid! The correct syntax is: ;connect4/;c4 @user", color = discord.Color.blue())
            await mess.channel.send(embed = dual_game)
            
            
    else:
        await mess.channel.send("You can't play a match against someone in a DM!")

@bot.command(name = "oto", description = "Start a game of othello", aliases = ["othello"])
async def oto(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("othello")
    if not(isinstance(mess.channel, discord.DMChannel)):
        valid_id = 0
        if msg.startswith(";othello <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";othello <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";oto <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";oto <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";othello <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";othello <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";oto <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";oto <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        if valid_id == 1:
            opp_id = int(opp_id)
            try:
                a_id = mess.author.id
                me = await bot.fetch_user(a_id)
                opponent = await bot.fetch_user(opp_id)
                server_id = mess.guild.id
                guild = bot.get_guild(server_id)
                members = []
                for m in guild.members:
                    members.append(m)
                if opponent in members and opponent != me and not(opponent.bot):
                    if a_id not in in_game and opp_id not in in_game:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of othello! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
                        in_game.append(a_id)
                        in_game.append(opp_id)
                        try:
                            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                        except asyncio.TimeoutError:
                            await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                        else:
                            if str(reaction.emoji) == "✅":
                                game = othello(a_id, opp_id, get_theme(a_id), get_theme(opp_id))
                                while (game.any_valid("black") or game.any_valid("white")) and game.game_end == 0:
                                    if game.turn == 0:
                                        if game.any_valid("black"):
                                            await mess.channel.send(f"<@!{a_id}> it's your turn")
                                            game.string_rows()
                                            board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                            await mess.channel.send(embed = board)
                                            while True:
                                                await mess.channel.send("Enter the row and column where you would like to place your coin (ex: '3 4') (Type 'board' to see your current game; type 'quit' to end the game)")
                                                try:
                                                    rc_msg = await bot.wait_for("message", check = lambda m: m.author.id == a_id and m.channel == mess.channel, timeout = 120.0)
                                                except asyncio.TimeoutError:
                                                    await mess.channel.send("You took too long to respond so the game has ended 😢")
                                                    game.game_end = 1
                                                    game.winner = opp_id
                                                    await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                    break
                                                message = rc_msg.content
                                                try:
                                                    r, c = map(int, message.split())
                                                    if r <= 0 or r > 8:
                                                        await mess.channel.send("Row is out of range")
                                                    elif c <= 0 or c > 8:
                                                        await mess.channel.send("Column is out of range")
                                                    else:
                                                        if game.items[r-1][c-1] != "":
                                                            await mess.channel.send("That spot is already occupied")
                                                        elif not game.is_valid_move(r, c, "black"):
                                                            await mess.channel.send("Invalid move")
                                                        else:
                                                            break
                                                except ValueError:
                                                    if message == "board":
                                                        game.string_rows()
                                                        board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                                        await mess.channel.send(embed = board)
                                                    elif message == "quit":
                                                        game.game_end = 1
                                                        game.winner = opp_id
                                                        await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                        break
                                                    else:
                                                        await mess.channel.send("Invalid input")
                                            if game.game_end == 0:
                                                game.guess(r, c, "black")
                                                game.string_rows()
                                                board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                                await mess.channel.send(embed = board)
                                                game.turn = 1
                                        else:
                                            await mess.channel.send("Black has no moves left so it is white's turn")
                                            game.turn = 1
                                    else:
                                        if game.any_valid("white"):
                                            await mess.channel.send(f"<@!{opp_id}> it's your turn")
                                            game.string_rows()
                                            board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                            await mess.channel.send(embed = board)
                                            while True:
                                                await mess.channel.send("Enter the row and column where you would like to place your coin (ex: '3 4') (Type 'board' to see your current game; type 'quit' to end the game)")
                                                try:
                                                    rc_msg = await bot.wait_for("message", check = lambda m: m.author.id == opp_id and m.channel == mess.channel, timeout = 120.0)
                                                except asyncio.TimeoutError:
                                                    await mess.channel.send("You took too long to respond so the game has ended 😢")
                                                    game.game_end = 1
                                                    game.winner = a_id
                                                    await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                    break
                                                message = rc_msg.content
                                                try:
                                                    r, c = map(int, message.split())
                                                    if r <= 0 or r > 8:
                                                        await mess.channel.send("Row is out of range")
                                                    elif c <= 0 or c > 8:
                                                        await mess.channel.send("Column is out of range")
                                                    else:
                                                        if game.items[r-1][c-1] != "":
                                                            await mess.channel.send("That spot is already occupied")
                                                        elif not game.is_valid_move(r, c, "white"):
                                                            await mess.channel.send("Invalid move")
                                                        else:
                                                            break
                                                except ValueError:
                                                    message = message.lower()
                                                    if message == "board":
                                                        game.string_rows()
                                                        board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                                        await mess.channel.send(embed = board)
                                                    elif message == "quit":
                                                        game.game_end = 1
                                                        game.winner = a_id
                                                        await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                        break
                                                    else:
                                                        await mess.channel.send("Invalid input")
                                            if game.game_end == 0:
                                                game.guess(r, c, "white")
                                                game.string_rows()
                                                board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                                await mess.channel.send(embed = board)
                                                game.turn = 0
                                        else:
                                            await mess.channel.send("White has no moves left so it is black's turn")
                                            game.turn = 0
                                if game.game_end == 0:
                                    game.find_winner()
                                    if not game.tie:
                                        await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                    else:
                                        await mess.channel.send("It's a tie ¯\_(ツ)_/¯")

                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                        in_game.remove(a_id)
                        in_game.remove(opp_id)
                    else:
                        if a_id in in_game:
                            await mess.channel.send("You're already in a game!")
                        else:
                            await mess.channel.send("Your opponent is already in a game!")
                            
                            

                else:
                    if opponent != me and not(opponent.bot):
                        dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                        await mess.channel.send(embed = dual_game)
                        
                        
            except discord.errors.NotFound:
                dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                
                
        else:
            dual_game = discord.Embed(title = "Invalid syntax!", description = "The othello syntax is invalid! The correct syntax is: ;othello/;oto @user", color = discord.Color.blue())
            await mess.channel.send(embed = dual_game)
            
            
    else:
        await mess.channel.send("You can't play a match against someone in a DM!")

@bot.command(name = "mm", description = "Start a game of mastermind", aliases = ["mastermind"])
async def mm(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("mastermind")
    if not(isinstance(mess.channel, discord.DMChannel)):
        valid_id = 0
        channel_id = mess.channel.id
        if msg.startswith(";mastermind <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";mastermind <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";mm <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";mm <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";mastermind <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";mastermind <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";mm <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";mm <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        if valid_id == 1:
            opp_id = int(opp_id)
            try:
                a_id = mess.author.id
                me = await bot.fetch_user(a_id)
                opponent = await bot.fetch_user(opp_id)
                server_id = mess.guild.id
                guild = bot.get_guild(server_id)
                members = []
                for m in guild.members:
                    members.append(m)
                if opponent in members and opponent != me and not(opponent.bot):
                    if a_id not in in_game and opp_id not in in_game:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of mastermind! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
                        in_game.append(a_id)
                        in_game.append(opp_id)
                        try:
                            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                        except asyncio.TimeoutError:
                            await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                        else:
                            if str(reaction.emoji) == "✅":
                                red = str(bot.get_emoji(962686453157068880))
                                orange = str(bot.get_emoji(962686453320679454))
                                yellow = str(bot.get_emoji(962686452918009858))
                                green = str(bot.get_emoji(962686453123534858))
                                blue = str(bot.get_emoji(962686453123543050))
                                purple = str(bot.get_emoji(962686453438095360))
                                brown = str(bot.get_emoji(962686453157085275))
                                p1_id = rd.choice([a_id, opp_id])
                                if p1_id == a_id:
                                    p2_id = opp_id
                                else:
                                    p2_id = a_id
                                await mess.channel.send(f"<@!{p1_id}> check your DMs for a message from me to enter your code!")
                                game = mastermind(p1_id, p2_id, get_theme(p2_id), red, orange, yellow, green, blue, purple, brown)
                                p1 = await bot.fetch_user(p1_id)
                                while True:
                                    try:
                                        await p1.send(f'''Enter the hidden code with the following numbers:
{red}, {orange}, {yellow}, {green}, {blue}, {purple}, {brown}
Ex: 1 2 3 4
''')
                                    except discord.errors.Forbidden:
                                        in_game.remove(p1_id)
                                        in_game.remove(p2_id)
                                        raise Exception("Cannot send messages to this user")
                                    try:
                                        hcode_msg = await bot.wait_for("message", check = lambda m: m.author.id == p1_id and m.guild == None, timeout = 120.0)
                                    except asyncio.TimeoutError:
                                        await p1.send("You took too long to respond so the game has been cancelled")
                                        game.game = 1
                                        break
                                    else:
                                        hc = hcode_msg.content
                                        try:
                                            invalid = 0
                                            nums = list(map(int, hc.split()))
                                            if len(nums) != 4:
                                                await p1.send("You can only enter 4 numbers")
                                                invalid = 1
                                            else:
                                                for x in nums:
                                                    if not(1 <= x <= 7):
                                                        await p1.send("You can only enter numbers from 1-7")
                                                        invalid = 1
                                                        break
                                            if invalid == 0:
                                                break
                                        except ValueError:
                                            await p1.send("You can only enter numbers from 1-7")
                                if game.game == 0:
                                    game.colourify(nums, 1)
                                    hcode_str = ""
                                    for x in game.hcode:
                                        hcode_str += x
                                    await p1.send(f"You have chosen the code {hcode_str}. Head back to <#{channel_id}> to watch the match!")
                                    channel = await bot.fetch_channel(channel_id)
                                    await channel.send(f"<@!{p2_id}> the code has been chosen! Get ready!" )
                                    while game.game == 0 and game.turns < 8:
                                        game.string_rows()
                                        grid_embed = discord.Embed(title = "Mastermind!", description = game.grid, colour = discord.Colour.blue())
                                        await channel.send(embed = grid_embed)
                                        while True:
                                            await channel.send(f'''Enter your guess with the following numbers:
{red}, {orange}, {yellow}, {green}, {blue}, {purple}, {brown}
Ex: 1 2 3 4

Type 'board' to view the current board; type 'quit' to quit the game
''')
                                            try:
                                                gcode_msg = await bot.wait_for("message", check = lambda m: m.author.id == p2_id and m.channel == channel, timeout = 300.0)
                                            except asyncio.TimeoutError:
                                                await channel.send("You took too long to respond so the game has ended")
                                                game.winner = game.p1
                                                await channel.send(f"<@!{game.winner}> is the winner!")
                                                game.turns = None
                                                break
                                            else:
                                                gc = gcode_msg.content
                                                try:
                                                    invalid = 0
                                                    nums = list(map(int, gc.split()))
                                                    if len(nums) != 4:
                                                        await channel.send("You can only enter 4 numbers")
                                                        invalid = 1
                                                    else:
                                                        for x in nums:
                                                            if not(1 <= x <= 7):
                                                                await channel.send("You can only enter numbers from 1-7")
                                                                invalid = 1
                                                                break
                                                    if invalid == 0:
                                                        break
                                                except ValueError:
                                                    gc = gc.lower()
                                                    if gc == "quit":
                                                        game.turns = None
                                                        game.winner = game.p1
                                                        await channel.send(f"<@!{game.winner}> is the winner!")
                                                        break
                                                    elif gc == "board":
                                                        game.string_rows()
                                                        grid_embed = discord.Embed(title = "Mastermind!", description = game.grid, colour = discord.Colour.blue())
                                                        await channel.send(embed = grid_embed)
                                                    else:
                                                        await channel.send("You can only enter numbers from 1-7")
                                        if game.turns != None:
                                            game.guess(nums)
                                        else:
                                            break
                                    if game.turns != None:
                                        game.string_rows()
                                        grid_embed = discord.Embed(title = "Mastermind!", description = game.grid, colour = discord.Colour.blue())
                                        await channel.send(embed = grid_embed)
                                        if game.turns == 8:
                                            game.winner = game.p1
                                        await channel.send(f"<@!{game.winner}> is the winner!")

                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                        in_game.remove(a_id)
                        in_game.remove(opp_id)
                    else:
                        if a_id in in_game:
                            await mess.channel.send("You're already in a game!")
                        else:
                            await mess.channel.send("Your opponent is already in a game!")
                            
                            

                else:
                    if opponent != me and not(opponent.bot):
                        dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                        await mess.channel.send(embed = dual_game)
                        
                        
            except discord.errors.NotFound:
                dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                
                
        else:
            dual_game = discord.Embed(title = "Invalid syntax!", description = "The mastermind syntax is invalid! The correct syntax is: ;mastermind/;mm @user", color = discord.Color.blue())
            await mess.channel.send(embed = dual_game)
            
            
    else:
        await mess.channel.send("You can't play a match against someone in a DM!")
    
@bot.command(name = "yz", description = "Start a game of yahtzee", aliases = ["yahtzee"])
async def yz(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("yahtzee")
    if not(isinstance(mess.channel, discord.DMChannel)):
        valid_id = 0
        channel_id = mess.channel.id
        if msg.startswith(";yahtzee <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";yahtzee <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";yz <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";yz <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";yahtzee <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";yahtzee <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";yz <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";yz <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        if valid_id == 1:
            opp_id = int(opp_id)
            try:
                a_id = mess.author.id
                me = await bot.fetch_user(a_id)
                opponent = await bot.fetch_user(opp_id)
                server_id = mess.guild.id
                guild = bot.get_guild(server_id)
                members = []
                for m in guild.members:
                    members.append(m)
                if opponent in members and opponent != me and not(opponent.bot):
                    if a_id not in in_game and opp_id not in in_game:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of yahtzee! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
                        in_game.append(a_id)
                        in_game.append(opp_id)
                        try:
                            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                        except asyncio.TimeoutError:
                            await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                        else:
                            if str(reaction.emoji) == "✅":
                                d1 = str(bot.get_emoji(963012018066055188))
                                d2 = str(bot.get_emoji(963012017558540309))
                                d3 = str(bot.get_emoji(963012018045063248))
                                d4 = str(bot.get_emoji(963012017982173254))
                                d5 = str(bot.get_emoji(963012017894084638))
                                d6 = str(bot.get_emoji(963012017671774259))
                                p1_game = yahtzee(a_id, d1, d2, d3, d4, d5, d6)
                                p2_game = yahtzee(opp_id, d1, d2, d3, d4, d5, d6)
                                turn = 0
                                while (p1_game.game == 0 or p2_game.game == 0) and p1_game.quit == 0 and p2_game.quit == 0:
                                    if turn == 0:
                                        if p1_game.empty_pos > 0:
                                            await mess.channel.send(f"<@!{p1_game.user_id}> it's your turn")
                                            p1_game.string_rows()
                                            p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                            p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                            p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                            p1_card.add_field(name = "Scores", value = p1_game.right)
                                            await mess.channel.send(embed = p1_card)
                                            inp = ""
                                            while p1_game.rolls > 0 and inp != "stop" and p1_game.quit == 0:
                                                p1_game.roll()
                                                p1_game.string_dice()
                                                dice_string = ""
                                                for x in p1_game.sdice:
                                                    dice_string += x+" "
                                                roll = discord.Embed(title = f"Roll {3-p1_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                await mess.channel.send(embed = roll)
                                                if p1_game.rolls > 0:
                                                    while True:
                                                        await mess.channel.send("Enter the numbers of the dice you would like to hold separated by spaces. Ex: 1 2 3 (Enter 0 to hold none of the dice; enter 'stop' to not roll again; enter 'dice' to view the current roll; enter 'card' to view the card; enter 'quit' to quit the game)")
                                                        try:
                                                            inp = await bot.wait_for("message", check = lambda m: m.author.id == p1_game.user_id and m.channel == mess.channel, timeout = 120.0)
                                                        except asyncio.TimeoutError:
                                                            await mess.channel.send("You took too long to respond so the game has ended")
                                                            p1_game.quit = 1
                                                            await mess.channel.send(f"<@!{p2_game.user_id}> is the winner!")
                                                            break
                                                        else:
                                                            inp = inp.content
                                                            inp = inp.lower()
                                                            if inp != "stop":
                                                                try:
                                                                    invalid = 0
                                                                    nums = list(map(int, inp.split()))
                                                                    if len(nums) > 5:
                                                                        await mess.channel.send("You can't hold more than 5 dice")
                                                                        invalid = 1
                                                                    elif len(nums) == 1 and nums[0] == 0:
                                                                        nums = []
                                                                    else:
                                                                        for x in nums:
                                                                            if not(1 <= x <= 6):
                                                                                await mess.channel.send("You can only hold dice with numbers from 1-6")
                                                                                invalid = 1
                                                                                break
                                                                            elif x not in p1_game.dice or nums.count(x) > p1_game.counts[x]:
                                                                                await mess.channel.send("You can only hold dice that have been rolled")
                                                                                invalid = 1
                                                                                break
                                                                    if invalid == 0:
                                                                        break
                                                                except ValueError:
                                                                    if inp == "quit":
                                                                        p1_game.quit = 1
                                                                        await mess.channel.send(f"<@!{p2_game.user_id}> is the winner!")
                                                                        break
                                                                    elif inp == "dice":
                                                                        p1_game.string_dice()
                                                                        dice_string = ""
                                                                        for x in p1_game.sdice:
                                                                            dice_string += x+" "
                                                                        roll = discord.Embed(title = f"Roll {3-p1_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                                        await mess.channel.send(embed = roll)
                                                                    elif inp == "card":
                                                                        p1_game.string_rows()
                                                                        p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                                                        p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                                                        p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                                                        p1_card.add_field(name = "Scores", value = p1_game.right)
                                                                        await mess.channel.send(embed = p1_card)
                                                                        p1_game.string_dice()
                                                                        dice_string = ""
                                                                        for x in p1_game.sdice:
                                                                            dice_string += x+" "
                                                                        roll = discord.Embed(title = f"Roll {3-p1_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                                        await mess.channel.send(embed = roll)
                                                                    else:
                                                                        await mess.channel.send("You can only enter integral values")
                                                            else:
                                                                break
                                                    if inp != "stop" and p1_game.quit == 0:
                                                        p1_game.store(nums)
                                            if p1_game.quit == 0:
                                                p1_game.string_rows()
                                                p1_game.string_dice()
                                                dice_string = ""
                                                for x in p1_game.sdice:
                                                    dice_string += x+" "
                                                p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                                p1_card.add_field(name = "Final dice", value = dice_string, inline = False)
                                                p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                                p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                                p1_card.add_field(name = "Scores", value = p1_game.right)
                                                await mess.channel.send(embed = p1_card)
                                                while True:
                                                    await mess.channel.send("Which field would you like to place your roll in. Ex: L1 (Enter 'card' to view the card)")
                                                    try:
                                                        loc = await bot.wait_for("message", check = lambda m: m.author.id == p1_game.user_id and m.channel == mess.channel, timeout = 120.0)
                                                    except asyncio.TimeoutError:
                                                        await mess.channel.send("You took too long to repond so the game has ended")
                                                        p1_game.quit = 1
                                                        await mess.channel.send(f"<@!{p2_game.user_id}> is the winner!")
                                                        break
                                                    else:
                                                        loc = loc.content
                                                        loc = str(loc).upper()
                                                        if loc[0] in ["U", "L"]:
                                                            try:
                                                                invalid = 0
                                                                if len(loc) != 2:
                                                                    await mess.channel.send("Invalid input")
                                                                    invalid = 1
                                                                elif loc[0] == "U":
                                                                    if not(1 <= int(loc[1:]) <= 6):
                                                                        await mess.channel.send("Invalid field")
                                                                        invalid = 1
                                                                else:
                                                                    if not(1 <= int(loc[1:]) <= 7):
                                                                        await mess.channel.send("Invalid field")
                                                                        invalid = 1
                                                                if invalid == 0:
                                                                    p1_game.points(loc)
                                                                    if p1_game.invalid == 0:
                                                                        break
                                                                    else:
                                                                        await mess.channel.send("That field is already occupied")
                                                            except ValueError:
                                                                await mess.channel.send("Invalid input")
                                                        else:
                                                            if loc == "CARD":
                                                                p1_game.string_rows()
                                                                p1_game.string_dice()
                                                                dice_string = ""
                                                                for x in p1_game.sdice:
                                                                    dice_string += x+" "
                                                                p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                                                p1_card.add_field(name = "Final dice", value = dice_string, inline = False)
                                                                p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                                                p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                                                p1_card.add_field(name = "Scores", value = p1_game.right)
                                                                await mess.channel.send(embed = p1_card)
                                                            else:
                                                                await mess.channel.send("Invalid input")
                                                if p1_game.quit == 0:
                                                    p1_game.string_rows()
                                                    p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                                    p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                                    p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                                    p1_card.add_field(name = "Scores", value = p1_game.right)
                                                    await mess.channel.send(embed = p1_card)
                                        else:
                                            p1_game.game = 1
                                        turn = 1
                                    else:
                                        if p2_game.empty_pos > 0:
                                            await mess.channel.send(f"<@!{p2_game.user_id}> it's your turn")
                                            p2_game.string_rows()
                                            p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                            p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                            p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                            p2_card.add_field(name = "Scores", value = p2_game.right)
                                            await mess.channel.send(embed = p2_card)
                                            inp = ""
                                            while p2_game.rolls > 0 and inp != "stop" and p2_game.quit == 0:
                                                p2_game.roll()
                                                p2_game.string_dice()
                                                dice_string = ""
                                                for x in p2_game.sdice:
                                                    dice_string += x+" "
                                                roll = discord.Embed(title = f"Roll {3-p2_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                await mess.channel.send(embed = roll)
                                                if p2_game.rolls > 0:
                                                    while True:
                                                        await mess.channel.send("Enter the numbers of the dice you would like to hold separated by spaces. Ex: 1 2 3 (Enter 0 to hold none of the dice; enter 'stop' to not roll again; enter 'dice' to view the current roll; enter 'card' to view the card; enter 'quit' to quit the game)")
                                                        try:
                                                            inp = await bot.wait_for("message", check = lambda m: m.author.id == p2_game.user_id and m.channel == mess.channel, timeout = 120.0)
                                                        except asyncio.TimeoutError:
                                                            await mess.channel.send("You took too long to respond so the game has ended")
                                                            p2_game.quit = 1
                                                            await mess.channel.send(f"<@!{p1_game.user_id}> is the winner!")
                                                            break
                                                        else:
                                                            inp = inp.content
                                                            inp = inp.lower()
                                                            if inp != "stop":
                                                                try:
                                                                    invalid = 0
                                                                    nums = list(map(int, inp.split()))
                                                                    if len(nums) > 5:
                                                                        await mess.channel.send("You can't hold more than 5 dice")
                                                                        invalid = 1
                                                                    elif len(nums) == 1 and nums[0] == 0:
                                                                        nums = []
                                                                    else:
                                                                        for x in nums:
                                                                            if not(1 <= x <= 6):
                                                                                await mess.channel.send("You can only hold dice with numbers from 1-6")
                                                                                invalid = 1
                                                                                break
                                                                            elif x not in p2_game.dice or nums.count(x) > p2_game.counts[x]:
                                                                                await mess.channel.send("You can only hold dice that have been rolled")
                                                                                invalid = 1
                                                                                break
                                                                    if invalid == 0:
                                                                        break
                                                                except ValueError:
                                                                    if inp == "quit":
                                                                        p2_game.quit = 1
                                                                        await mess.channel.send(f"<@!{p1_game.user_id}> is the winner!")
                                                                        break
                                                                    elif inp == "dice":
                                                                        p2_game.string_dice()
                                                                        dice_string = ""
                                                                        for x in p2_game.sdice:
                                                                            dice_string += x+" "
                                                                        roll = discord.Embed(title = f"Roll {3-p2_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                                        await mess.channel.send(embed = roll)
                                                                    elif inp == "card":
                                                                        p2_game.string_rows()
                                                                        p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                                                        p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                                                        p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                                                        p2_card.add_field(name = "Scores", value = p2_game.right)
                                                                        await mess.channel.send(embed = p2_card)
                                                                        p2_game.string_dice()
                                                                        dice_string = ""
                                                                        for x in p2_game.sdice:
                                                                            dice_string += x+" "
                                                                        roll = discord.Embed(title = f"Roll {3-p2_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                                        await mess.channel.send(embed = roll)
                                                                    else:
                                                                        await mess.channel.send("You can only enter integral values")
                                                            else:
                                                                break
                                                    if inp != "stop" and p2_game.quit == 0:
                                                        p2_game.store(nums)
                                            if p2_game.quit == 0:
                                                p2_game.string_rows()
                                                p2_game.string_dice()
                                                dice_string = ""
                                                for x in p2_game.sdice:
                                                    dice_string += x+" "
                                                p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                                p2_card.add_field(name = "Final dice", value = dice_string, inline = False)
                                                p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                                p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                                p2_card.add_field(name = "Scores", value = p2_game.right)
                                                await mess.channel.send(embed = p2_card)
                                                while True:
                                                    await mess.channel.send("Which field would you like to place your roll in. Ex: L1 (Enter 'card' to view the card)")
                                                    try:
                                                        loc = await bot.wait_for("message", check = lambda m: m.author.id == p2_game.user_id and m.channel == mess.channel, timeout = 120.0)
                                                    except asyncio.TimeoutError:
                                                        await mess.channel.send("You took too long to repond so the game has ended")
                                                        p2_game.quit = 1
                                                        await mess.channel.send(f"<@!{p1_game.user_id}> is the winner!")
                                                        break
                                                    else:
                                                        loc = loc.content
                                                        loc = str(loc).upper()
                                                        if loc[0] in ["U", "L"]:
                                                            try:
                                                                invalid = 0
                                                                if len(loc) != 2:
                                                                    await mess.channel.send("Invalid input")
                                                                    invalid = 1
                                                                elif loc[0] == "U":
                                                                    if not(1 <= int(loc[1:]) <= 6):
                                                                        await mess.channel.send("Invalid field")
                                                                        invalid = 1
                                                                else:
                                                                    if not(1 <= int(loc[1:]) <= 7):
                                                                        await mess.channel.send("Invalid field")
                                                                        invalid = 1
                                                                if invalid == 0:
                                                                    p2_game.points(loc)
                                                                    if p2_game.invalid == 0:
                                                                        break
                                                                    else:
                                                                        await mess.channel.send("That field is already occupied")
                                                            except ValueError:
                                                                await mess.channel.send("Invalid input")
                                                        else:
                                                            if loc == "CARD":
                                                                p2_game.string_rows()
                                                                p2_game.string_dice()
                                                                dice_string = ""
                                                                for x in p2_game.sdice:
                                                                    dice_string += x+" "
                                                                p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                                                p2_card.add_field(name = "Final dice", value = dice_string, inline = False)
                                                                p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                                                p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                                                p2_card.add_field(name = "Scores", value = p2_game.right)
                                                                await mess.channel.send(embed = p2_card)
                                                            else:
                                                                await mess.channel.send("Invalid input")
                                                if p2_game.quit == 0:
                                                    p2_game.string_rows()
                                                    p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                                    p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                                    p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                                    p2_card.add_field(name = "Scores", value = p2_game.right)
                                                    await mess.channel.send(embed = p2_card)
                                        else:
                                            p2_game.game = 1
                                        turn = 0
                                if p1_game.quit == 0 and p2_game.quit == 0:
                                    await mess.channel.send(f'''
{me.name}'s total: {p1_game.total}
{opponent.name}'s total: {p2_game.total}
''')
                                    if p1_game.total > p2_game.total:
                                        await mess.channel.send(f"<@!{p1_game.user_id}> is the winner!")
                                    elif p2_game.total > p1_game.total:
                                        await mess.channel.send(f"<@!{p2_game.user_id}> is the winner!")
                                    else:
                                        await mess.channel.send("It's a tie ¯\_(ツ)_/¯")

                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                        in_game.remove(a_id)
                        in_game.remove(opp_id)
                    else:
                        if a_id in in_game:
                            await mess.channel.send("You're already in a game!")
                        else:
                            await mess.channel.send("Your opponent is already in a game!")
                            
                            

                else:
                    if opponent != me and not(opponent.bot):
                        dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                        await mess.channel.send(embed = dual_game)
                        
                        
            except discord.errors.NotFound:
                dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                
                
        else:
            dual_game = discord.Embed(title = "Invalid syntax!", description = "The yahtzee syntax is invalid! The correct syntax is: ;yahtzee/;yz @user", color = discord.Color.blue())
            await mess.channel.send(embed = dual_game)
            
            
    else:
        await mess.channel.send("You can't play a match against someone in a DM!")

@bot.command(name = "bs", description = "Start a game of battleship", aliases = ["battleship"])
async def bs(mess: commands.Context):
    global in_game, live_battles
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("battleship")
    if not(isinstance(mess.channel, discord.DMChannel)):
        valid_id = 0
        channel_id = mess.channel.id
        if msg.startswith(";battleship <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";battleship <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";bs <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";bs <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";battleship <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";battleship <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";bs <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";bs <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        if valid_id == 1:
            opp_id = int(opp_id)
            try:
                a_id = mess.author.id
                me = await bot.fetch_user(a_id)
                opponent = await bot.fetch_user(opp_id)
                server_id = mess.guild.id
                guild = bot.get_guild(server_id)
                members = []
                channel = mess.channel
                for m in guild.members:
                    members.append(m)
                if opponent in members and opponent != me and not(opponent.bot):
                    if a_id not in in_game and opp_id not in in_game and channel.id not in live_battles.keys():
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of battleship! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
                        in_game.append(a_id)
                        in_game.append(opp_id)
                        try:
                            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                        except asyncio.TimeoutError:
                            await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                        else:
                            if str(reaction.emoji) == "✅":
                                live_battles[channel.id] = (0, 0)
                                await mess.channel.send("Hop into your DMs and start playing!")
                                p1_game = battleship(get_theme(a_id), get_theme(opp_id))
                                p2_game = battleship(get_theme(opp_id), get_theme(a_id))
                                async def get_pos(id, o_id):
                                    timeout = 0
                                    p0 = await bot.fetch_user(id)
                                    p0_game = battleship(get_theme(id), get_theme(o_id))
                                    ships = [("carrier", 5), ("battleship", 4), ("cruiser", 3), ("submarine", 3), ("destroyer", 2)]
                                    for ship in ships:
                                        if timeout == 0:
                                            while True:
                                                invalid = 0
                                                p0_game.string_grid()
                                                grid = discord.Embed(title = "Your grid", description = p0_game.grid_string, colour = discord.Colour.blue())
                                                try:
                                                    await p0.send(embed = grid)
                                                except discord.errors.Forbidden:
                                                    in_game.remove(id)
                                                    in_game.remove(o_id)
                                                    del live_battles[channel.id]
                                                    raise Exception("Cannot send messages to this user")
                                                await p0.send(f"Where would you like to place your {ship[0]} ({ship[1]} holes)? (Enter the start and end coordinates separated by spaces. Ex: 1 1 1 5)")
                                                try:
                                                    ship_loc = await bot.wait_for("message", check = lambda m: m.author.id == id and m.guild == None, timeout = 60.0)
                                                except asyncio.TimeoutError:
                                                    await p0.send("You took too long to respond so the game has ended")
                                                    timeout = 1
                                                    break
                                                else:
                                                    try:
                                                        coords = list(map(int, ship_loc.content.split()))
                                                        if len(coords) != 4:
                                                            await p0.send("You have to enter 2 sets of coordinates with 4 values")
                                                            invalid = 1
                                                        else:
                                                            for coord in coords:
                                                                if not(1 <= coord <= 10):
                                                                    await p0.send("You can only enter numbers from 1 to 10")
                                                                    invalid = 1
                                                                    break
                                                    except ValueError:
                                                        await p0.send("Invalid input")
                                                        invalid = 1
                                                    if invalid == 0:
                                                        locs = ((coords[0], coords[1]), (coords[2], coords[3]))
                                                        result = p0_game.valid_ship(locs, ship[1])
                                                        if result[0] == 1:
                                                            error = result[1]
                                                            if error == "row":
                                                                await p0.send("You can only place the ship in a single row or column")
                                                            elif error == "length":
                                                                await p0.send(f"Your ship must be {ship[1]} units long")
                                                            elif error == "overlap":
                                                                await p0.send("Your entered ship is overlapping another one of your ships")

                                                        else:
                                                            p0_game.place_ship(locs, ship[1])
                                                            break
                                        else:
                                            break
                                    if timeout == 0:
                                        p0_game.string_grid()
                                        grid = discord.Embed(title = "Your final grid", description = p0_game.grid_string, colour = discord.Colour.blue())
                                        await p0.send(embed = grid)
                                        await p0.send("Please wait for some time while your opponent finishes arranging their ships")
                                        return p0_game
                                    else:
                                        return timeout
                                tasks = []
                                tasks.append(asyncio.create_task(get_pos(a_id, opp_id)))
                                tasks.append(asyncio.create_task(get_pos(opp_id, a_id)))
                                await asyncio.gather(*tasks)
                                p1_game = tasks[0].result()
                                p2_game = tasks[1].result()
                                p1 = me
                                p2 = opponent
                                if not(p1_game == 1 or p2_game == 1):
                                    turn = 0
                                    channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", colour = discord.Colour.blue())
                                    p1_game.channel_grid()
                                    p2_game.channel_grid()
                                    channel_game_embed.add_field(name = f"{p1.name}'s grid", value = p1_game.guess_string, inline = True)
                                    channel_game_embed.add_field(name = f"{p2.name}'s grid", value = p2_game.guess_string, inline = True)
                                    channel_game = await channel.send(embed = channel_game_embed)
                                    live_battles[channel.id] = (channel.guild.id, channel_game.id)
                                    await p1.send("Get ready to begin!")
                                    await p2.send("Get ready to begin!")
                                    quit = 0
                                    while p1_game.alive_ships > 0 and p2_game.alive_ships > 0 and quit == 0:
                                        if turn == 0:
                                            await p2.send(f"It is <@!{p1.id}>'s turn")
                                            while True:
                                                p1_game.string_grid()
                                                p2_game.string_guess()
                                                p1_comp = discord.Embed(title = "Battleship!", description = f'''**Opponent ships**: {p2_game.ship_names}
**Your ships**: {p1_game.ship_names}''', colour = discord.Colour.blue())
                                                p1_comp.add_field(name = "Your target grid", value = p2_game.guess_string, inline = True)
                                                p1_comp.add_field(name = "Your grid", value = p1_game.grid_string, inline = True)
                                                await p1.send(embed = p1_comp)
                                                await p1.send("Enter the coordinates where you would like to shoot separated by a space (Ex: 5 4) (Enter 'quit' if you wish to quit the game)")
                                                try:
                                                    loc_msg = await bot.wait_for("message", check = lambda m: m.author.id == p1.id and m.guild == None, timeout = 120.0)
                                                except asyncio.TimeoutError:
                                                    await p1.send("You took too long to respond so the game has ended")
                                                    await channel.send(f"<@!{p2.id}>, <@!{p1.id}> took too long to respond so the game has ended")
                                                    quit = 1
                                                    break
                                                else:
                                                    try:
                                                        loc = tuple(map(int, loc_msg.content.split()))
                                                        if len(loc) != 2:
                                                            await p1.send("You can only enter 2 integral coordinates")
                                                        elif not(1 <= loc[0] <= 10) or not(1 <= loc[1] <= 10):
                                                            await p1.send("You can only enter integers from 1 to 10")
                                                        else:
                                                            shot = p2_game.shoot(loc)
                                                            if shot[0] == 1:
                                                                await p1.send("You have already shot over there")
                                                            else:
                                                                if shot[1] == 0:
                                                                    await p1.send("That was a miss!")
                                                                    await p2.send(f"<@!{p1.id}> shot at {loc} and missed!")
                                                                    channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p1.id}> shot at {loc} and missed!", colour = discord.Colour.blue())
                                                                    
                                                                else:
                                                                    if shot[2] == 1:
                                                                        await p1.send(f"{shot[3].upper()} SUNK!")
                                                                        await p2.send(f"<@!{p1.id}> shot at {loc} and sunk your {shot[3]}!")
                                                                        channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p1.id}> shot at {loc} and sunk the {shot[3]}!", colour = discord.Colour.blue())
                                                                        
                                                                    else:
                                                                        await p1.send(f"YOU HIT THE {shot[3].upper()}!")
                                                                        await p2.send(f"<@!{p1.id}> shot at {loc} and hit your {shot[3]}!")
                                                                        channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p1.id}> shot at {loc} and hit the {shot[3]}!", colour = discord.Colour.blue())

                                                                break
                                                    except ValueError:
                                                        text = loc_msg.content.lower()
                                                        if text == "quit":
                                                            await channel.send(f"<@!{p2.id}>, <@!{p1.id}> quit the game so you are the winner!")
                                                            quit = 1
                                                            break
                                                        else:
                                                            await p1.send("You can only enter integers")
                                            if quit == 0:
                                                p1_game.string_grid()
                                                p2_game.string_guess()
                                                p1_comp = discord.Embed(title = "Battleship!", description = f'''**Opponent ships**: {p2_game.ship_names}
**Your ships**: {p1_game.ship_names}''', colour = discord.Colour.blue())
                                                p1_comp.add_field(name = "Your target grid", value = p2_game.guess_string, inline = True)
                                                p1_comp.add_field(name = "Your grid", value = p1_game.grid_string, inline = True)
                                                await p1.send(embed = p1_comp)
                                                p1_game.channel_grid()
                                                p2_game.channel_grid()
                                                channel_game_embed.add_field(name = f"{p1.name}'s grid", value = p1_game.guess_string, inline = True)
                                                channel_game_embed.add_field(name = f"{p2.name}'s grid", value = p2_game.guess_string, inline = True)
                                                await channel_game.edit(embed = channel_game_embed)
                                                turn = 1
                                        else:
                                            await p1.send(f"It is <@!{p2.id}>'s turn")
                                            while True:
                                                p2_game.string_grid()
                                                p1_game.string_guess()
                                                p2_comp = discord.Embed(title = "Battleship!", description = f'''**Opponent ships**: {p1_game.ship_names}
**Your ships**: {p2_game.ship_names}''', colour = discord.Colour.blue())
                                                p2_comp.add_field(name = "Your target grid", value = p1_game.guess_string, inline = True)
                                                p2_comp.add_field(name = "Your grid", value = p2_game.grid_string, inline = True)
                                                await p2.send(embed = p2_comp)
                                                await p2.send("Enter the coordinates where you would like to shoot separated by a space (Ex: 5 4) (Enter 'quit' if you wish to quit the game)")
                                                try:
                                                    loc_msg = await bot.wait_for("message", check = lambda m: m.author.id == p2.id and m.guild == None, timeout = 120.0)
                                                except asyncio.TimeoutError:
                                                    await p2.send("You took too long to respond so the game has ended")
                                                    await channel.send(f"<@!{p1.id}>, <@!{p2.id}> took too long to respond so the game has ended")
                                                    quit = 1
                                                    break
                                                else:
                                                    try:
                                                        loc = tuple(map(int, loc_msg.content.split()))
                                                        if len(loc) != 2:
                                                            await p2.send("You can only enter 2 integral coordinates")
                                                        elif not(1 <= loc[0] <= 10) or not(1 <= loc[1] <= 10):
                                                            await p2.send("You can only enter integers from 1 to 10")
                                                        else:
                                                            shot = p1_game.shoot(loc)
                                                            if shot[0] == 1:
                                                                await p2.send("You have already shot over there")
                                                            else:
                                                                if shot[1] == 0:
                                                                    await p2.send("That was a miss!")
                                                                    await p1.send(f"<@!{p2.id}> shot at {loc} and missed!")
                                                                    channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p2.id}> shot at {loc} and missed!", colour = discord.Colour.blue())
                                                                else:
                                                                    if shot[2] == 1:
                                                                        await p2.send(f"{shot[3].upper()} SUNK!")
                                                                        await p1.send(f"<@!{p2.id}> shot at {loc} and sunk your {shot[3]}!")
                                                                        channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p2.id}> shot at {loc} and sunk the {shot[3]}!", colour = discord.Colour.blue())
                                                                        
                                                                    else:
                                                                        await p2.send(f"YOU HIT THE {shot[3].upper()}!")
                                                                        await p1.send(f"<@!{p2.id}> shot at {loc} and hit your {shot[3]}!")
                                                                        channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p2.id}> shot at {loc} and hit the {shot[3]}!", colour = discord.Colour.blue())
                                                                        
                                                                break
                                                    except ValueError:
                                                        text = loc_msg.content.lower()
                                                        if text == "quit":
                                                            await channel.send(f"<@!{p1.id}>, <@!{p2.id}> quit the game so you are the winner!")
                                                            quit = 1
                                                            break
                                                        else:
                                                            await p2.send("You can only enter integers")
                                            if quit == 0:
                                                p2_game.string_grid()
                                                p1_game.string_guess()
                                                p2_comp = discord.Embed(title = "Battleship!", description = f'''**Opponent ships**: {p1_game.ship_names}
**Your ships**: {p2_game.ship_names}''', colour = discord.Colour.blue())
                                                p2_comp.add_field(name = "Your target grid", value = p1_game.guess_string, inline = True)
                                                p2_comp.add_field(name = "Your grid", value = p2_game.grid_string, inline = True)
                                                await p2.send(embed = p2_comp)
                                                p1_game.channel_grid()
                                                p2_game.channel_grid()
                                                channel_game_embed.add_field(name = f"{p1.name}'s grid", value = p1_game.guess_string, inline = True)
                                                channel_game_embed.add_field(name = f"{p2.name}'s grid", value = p2_game.guess_string, inline = True)
                                                await channel_game.edit(embed = channel_game_embed)
                                                turn = 0
                                    if quit == 0:
                                        if p1_game.alive_ships == 0:
                                            await p1.send("You lost 😢")
                                            await p2.send("You won! 🥳")
                                            winner = p2
                                        else:
                                            await p2.send("You lost 😢")
                                            await p1.send("You won! 🥳")
                                            winner = p1
                                        p1_game.final_grid()
                                        p2_game.final_grid()
                                        p1_final = discord.Embed(title = "Your opponent's final grid", description = f"Ships alive: {p2_game.alive_ships}", colour = discord.Colour.blue())
                                        p1_final.add_field(name = "Your guesses on the grid", value = p2_game.grid_string)
                                        p2_final = discord.Embed(title = "Your opponent's final grid", description = f"Ships alive: {p1_game.alive_ships}", colour = discord.Colour.blue())
                                        p2_final.add_field(name = "Your guesses on the grid", value = p1_game.grid_string)
                                        await p1.send(embed = p1_final)
                                        await p2.send(embed = p2_final)
                                        await channel.send(f"<@!{winner.id}> is the winner!")
                                        p1_game.channel_final()
                                        p2_game.channel_final()
                                        channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{winner.id}> is the winner!", colour = discord.Colour.blue())
                                        channel_game_embed.add_field(name = f"{p1.name}'s revealed grid", value = p1_game.grid_string, inline = True)
                                        channel_game_embed.add_field(name = f"{p2.name}'s revealed grid", value = p2_game.grid_string, inline = True)
                                        await channel_game.edit(embed = channel_game_embed)
                                else:
                                    if p1_game == 1:
                                        await channel.send(f"<@!{p2.id}>, <@!{p1.id}> took too long to respond so the game has ended")
                                    else:
                                        await channel.send(f"<@!{p1.id}>, <@!{p2.id}> took too long to respond so the game has ended")
                                del live_battles[channel.id]
                                
                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                        in_game.remove(a_id)
                        in_game.remove(opp_id)
                    else:
                        if channel.id not in live_battles.keys():
                            if a_id in in_game:
                                await mess.channel.send("You're already in a game!")
                            else:
                                await mess.channel.send("Your opponent is already in a game!")
                        else:
                            await mess.channel.send("There is already a battleship game going on over here!")
                            
                else:
                    if opponent != me and not(opponent.bot):
                        dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                        await mess.channel.send(embed = dual_game)
                        
                        
            except discord.errors.NotFound:
                dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                
                
        else:
            dual_game = discord.Embed(title = "Invalid syntax!", description = "The battleship syntax is invalid! The correct syntax is: ;battleship/;bs @user", color = discord.Color.blue())
            await mess.channel.send(embed = dual_game)
            
            
    else:
        await mess.channel.send("You can't play a match against someone in a DM!")

@bot.command(name = "live", description = "Send the links for current battleship and uno games")
async def live(mess: commands.Context):
    global in_game, live_battles, live_uno
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("live")
    if not(isinstance(mess.channel, discord.DMChannel)):
        channel_id = mess.channel.id
        if channel_id in live_battles.keys():
            if live_battles[channel_id] != (0, 0):
                await mess.channel.send(f"**Battleship**: https://discord.com/channels/{live_battles[channel_id][0]}/{channel_id}/{live_battles[channel_id][1]}")
            else:
                await mess.channel.send("**Battleship**: The players are placing their ships so the game is yet to begin")
        if channel_id in live_uno.keys():
            if live_uno[channel_id] != (0, 0):
                await mess.channel.send(f"**Uno**: https://discord.com/channels/{live_uno[channel_id][0]}/{channel_id}/{live_uno[channel_id][1]}")
            else:
                await mess.channel.send("**Uno**: People are still joining the uno game!")
        if channel_id not in live_battles.keys() and channel_id not in live_uno.keys():
            await mess.channel.send("There are no battleship or uno games going on in this channel at the moment")
    else:
        await mess.channel.send("This is not a DM command!")

@bot.command(name = "hm", description = "Start a game of hangman", aliases = ["hangman"])
async def hm(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("hangman")
    if not(isinstance(mess.channel, discord.DMChannel)):
        valid_id = 0
        channel_id = mess.channel.id
        if msg.startswith(";hangman <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";hangman <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";hm <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";hm <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";hangman <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";hangman <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";hm <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";hm <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        if valid_id == 1:
            opp_id = int(opp_id)
            try:
                a_id = mess.author.id
                me = await bot.fetch_user(a_id)
                opponent = await bot.fetch_user(opp_id)
                server_id = mess.guild.id
                guild = bot.get_guild(server_id)
                channel = mess.channel
                members = []
                for m in guild.members:
                    members.append(m)
                if opponent in members and opponent != me and not(opponent.bot):
                    if a_id not in in_game and opp_id not in in_game:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of hangman! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
                        in_game.append(a_id)
                        in_game.append(opp_id)
                        try:
                            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                        except asyncio.TimeoutError:
                            await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                        else:
                            if str(reaction.emoji) == "✅":
                                game = hangman()
                                l = [me, opponent]
                                p1 = rd.choice(l)
                                l.remove(p1)
                                p2 = l[0]
                                await mess.channel.send(f"<@!{p1.id}> check your DMs for a message from me to enter your word/phrase!")
                                timeout = 0
                                while True:
                                    try:
                                        await p1.send("Enter the hidden word/phrase; it must be at least 3 characters in length and must consist of only letters and spaces")
                                    except discord.errors.Forbidden:
                                        in_game.remove(p1.id)
                                        in_game.remove(p2.id)
                                        raise Exception("Cannot send messages to this user")
                                    try:
                                        hmsg = await bot.wait_for("message", check = lambda m: m.author.id == p1.id and m.guild == None, timeout = 120.0)
                                    except asyncio.TimeoutError:
                                        await p1.send("You took too long to respond so the game has ended")
                                        await channel.send(f"<@!{p2.id}>, <@!{p1.id}> took too long to respond so the game has ended")
                                        timeout = 1
                                        break
                                    else:
                                        word = hmsg.content
                                        word = str(word).lower()
                                        if len(word) >= 3:
                                            is_alpha = True
                                            for x in word:
                                                if not(x.isalpha() or x == " "):
                                                    is_alpha = False
                                                    break
                                            if is_alpha:
                                                has_cons = False
                                                for x in word:
                                                    if x not in "aeiou":
                                                        has_cons = True
                                                        break
                                                if not has_cons:
                                                    await p1.send("You need to have at least one consonant in your word/phrase as all the vowels will be revealed at the start of the game")
                                                else:
                                                    break
                                            else:
                                                await p1.send("You can only enter characters and spaces")
                                        else:
                                            await p1.send("Your word/phrase has to be at least 3 characters long")
                                if timeout == 0:
                                    game.sto_word(word)
                                    await p1.send(f"You have chosen the phrase `{word}`. Head back to <#{channel.id}> to watch the match!")
                                    await channel.send(f"<@!{p2.id}> the word has been chosen! Get ready! (All the vowels have already been filled in)")
                                    while game.game == 0 and game.misses < 6 and timeout == 0:
                                        if game.misses == 0:
                                            photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030062973829160/hangman_1.png"
                                        elif game.misses == 1:
                                            photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030062692823080/hangman_2.png"
                                        elif game.misses == 2:
                                            photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030062436941825/hangman_3.png"
                                        elif game.misses == 3:
                                            photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030062197891122/hangman_4.png"
                                        elif game.misses == 4:
                                            photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030061904269362/hangman_5.png"
                                        elif game.misses == 5:
                                            photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030061631668324/hangman_6.png"
                                        else:
                                            photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030061346422794/hangman_7.png"
                                        man = discord.Embed(title = "Hangman!", colour = discord.Colour.blue())
                                        man.set_image(url = photo)
                                        game.string_letters()
                                        await channel.send(embed = man)
                                        await channel.send(f'''**Word**: {game.gword.upper()}

**Letters**:
{game.letters_string}''')
                                        while True:
                                            await channel.send("Enter a letter to guess (Enter 'quit' to leave the game; Enter 'board' to see the current board)")
                                            try:
                                                letter_msg = await bot.wait_for("message", check = lambda m: m.author.id == p2.id and m.channel == mess.channel, timeout = 120.0)
                                            except asyncio.TimeoutError:
                                                await channel.send("You took too long to respond so the game has ended")
                                                await channel.send(f"<@!{p1.id}> is the winner!")
                                                timeout = 1
                                                break
                                            else:
                                                letter = letter_msg.content
                                                letter = str(letter).lower()
                                                if len(letter) == 1:
                                                    if letter.isalpha():
                                                        result = game.guess(letter)
                                                        if result[1] == 0:
                                                            if result[0]:
                                                                await channel.send(f"{letter.upper()} was in the word/phrase!")
                                                            else:
                                                                await channel.send(f"{letter.upper()} was not in the word/phrase!")
                                                            break 
                                                        else:
                                                            if letter not in "aeiou":
                                                                await channel.send("You have already guessed that letter!")
                                                            else:
                                                                await channel.send("All the vowels have already been displayed!")
                                                    else:
                                                        await channel.send("You can only enter a single letter")
                                                else:
                                                    if letter == "quit":
                                                        await channel.send(f"<@!{p1.id}> is the winner!")
                                                        timeout = 1
                                                        break
                                                    elif letter == "board":
                                                        man = discord.Embed(title = "Hangman!", colour = discord.Colour.blue())
                                                        man.set_image(url = photo)
                                                        game.string_letters()
                                                        await channel.send(embed = man)
                                                        await channel.send(f'''**Word**: {game.gword.upper()}

**Letters**:
{game.letters_string}''')
                                                    else:
                                                        await channel.send("You can only enter a single letter")
                                    if timeout == 0:
                                        man = discord.Embed(title = "Hangman!", colour = discord.Colour.blue())
                                        if game.misses == 6:
                                            photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030061346422794/hangman_7.png"
                                        man.set_image(url = photo)
                                        game.string_letters()
                                        await channel.send(embed = man)
                                        await channel.send(f'''**Word**: {game.gword.upper()}

**Letters**:
{game.letters_string}''')
                                        if game.game == 0:
                                            await channel.send(f"<@!{p2.id}>, you could not guess the phrase correctly; it was `{game.hword}`")
                                            await channel.send(f"<@!{p1.id}> is the winner!")
                                        else:
                                            await channel.send(f"<@!{p2.id}>, you guessed the phrase correctly! It was `{game.hword}`")
                                            await channel.send(f"<@!{p2.id}> is the winner!")
                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")

                        in_game.remove(a_id)
                        in_game.remove(opp_id)
                    else:
                        if a_id in in_game:
                            await mess.channel.send("You're already in a game!")
                        else:
                            await mess.channel.send("Your opponent is already in a game!")     

                else:
                    if opponent != me and not(opponent.bot):
                        dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                        await mess.channel.send(embed = dual_game)
                        
                        
            except discord.errors.NotFound:
                dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                
                
        else:
            dual_game = discord.Embed(title = "Invalid syntax!", description = "The hangman syntax is invalid! The correct syntax is: ;hangman/;hm @user", color = discord.Color.blue())
            await mess.channel.send(embed = dual_game)
    else:
        await mess.channel.send("You can't play a match against someone in a DM!")

@bot.command(name = "uno", description = "Start a game of uno")
async def uno(mess: commands.Context):
    global in_game, live_uno
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("uno")
    if not(isinstance(mess.channel, discord.DMChannel)):
        host_id = mess.author.id
        if host_id not in in_game and mess.channel.id not in live_uno.keys():
            channel = mess.channel
            live_uno[mess.channel.id] = (0, 0)
            thumb = bot.get_emoji(935120796358152212)
            check = bot.get_emoji(935455988516028486)
            uno_members = [host_id]
            uno_init_embed = discord.Embed(title = "Uno game started!", description = f"<@!{host_id}> started a game of uno! React with {thumb} below or type `;join` to join! Remove your reaction or type `;leave` to leave. <@!{host_id}> react with {check} or type `;start` to start the game!", colour = discord.Colour.blue())
            uno_init = await mess.channel.send(embed = uno_init_embed)
            await uno_init.add_reaction(str(thumb))
            await uno_init.add_reaction(str(check))
            in_game.append(host_id)
            while True:
                decisions = [asyncio.create_task(bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) in [str(thumb), str(check)] and p != bot.user and r.message.id == uno_init.id, timeout = 60.0), name = "radd"), asyncio.create_task(bot.wait_for("reaction_remove", check = lambda r, p: str(r.emoji) == str(thumb) and p != bot.user and r.message.id == uno_init.id, timeout = 60.0), name = "rrem"), asyncio.create_task(bot.wait_for("message", check = lambda m: m.channel == mess.channel, timeout = 60.0), name = "msgd")]

                completed, pending = await asyncio.wait(decisions, return_when = asyncio.FIRST_COMPLETED)
                
                finished_task: asyncio.Task = list(completed)[0]
                
                for unfinished in pending:
                    try:
                        unfinished.cancel()
                    except asyncio.CancelledError:
                        pass

                action = finished_task.get_name()
                try:
                    result = finished_task.result()
                except asyncio.TimeoutError:
                    break

                else:
                    if action == "radd":
                        reaction, user = result
                        reaction_e = str(reaction.emoji)
                        if reaction_e == str(thumb) and user.id != host_id and user.id not in uno_members:
                            if user.id not in in_game:
                                await mess.channel.send(f"<@!{user.id}> has joined the game!")
                                uno_members.append(user.id)
                                in_game.append(user.id)
                            else:
                                await mess.channel.send("You're already in a game!")
                        elif reaction_e == str(check) and user.id == host_id:
                            break
                    elif action == "rrem":
                        reaction, user = result
                        reaction_e = str(reaction.emoji)
                        if reaction_e == str(thumb) and user.id != host_id and user.id in uno_members:
                            await mess.channel.send(f"<@!{user.id}> has left the game")
                            uno_members.remove(user.id)
                            in_game.remove(user.id)
                    elif action == "msgd":
                        jl_msg = str(result.content)
                        user = result.author
                        if jl_msg == ";join" and user.id not in uno_members and user.id != host_id:
                            if user.id not in in_game:
                                await mess.channel.send(f"<@!{user.id}> has joined the game!")
                                uno_members.append(user.id)
                                in_game.append(user.id)
                            else:
                                await mess.channel.send("You're already in a game!")
                        elif jl_msg == ";leave" and user.id in uno_members and user.id != host_id:
                            await mess.channel.send(f"<@!{user.id}> has left the game")
                            uno_members.remove(user.id)
                            in_game.remove(user.id)
                        elif jl_msg == ";start" and user.id == host_id:
                            break
            uno_members = list(set(uno_members))
            rd.shuffle(uno_members)
            if len(uno_members) > 1:
                uno_cards = [bot.get_emoji(982179451150430249), bot.get_emoji(982179449711759400), bot.get_emoji(982179450668089404), bot.get_emoji(982179833826115634), bot.get_emoji(982179450433200168), bot.get_emoji(982179450781327370), bot.get_emoji(982179449590132746), bot.get_emoji(982179450819059722), bot.get_emoji(982179451154595860), bot.get_emoji(982179450223493131), bot.get_emoji(982179449313316864), bot.get_emoji(982199615753437204), bot.get_emoji(982179450865193000), bot.get_emoji(982179450479325224), bot.get_emoji(982179450269630544), bot.get_emoji(982179450315739196), bot.get_emoji(982179450684842005), bot.get_emoji(982179449661435935), bot.get_emoji(982179449518837760), bot.get_emoji(982179450441588786), bot.get_emoji(982179450630328330), bot.get_emoji(982179450449965088), bot.get_emoji(982179449183281153), bot.get_emoji(982199640248156210), bot.get_emoji(982179451062337546), bot.get_emoji(982179450940702730), bot.get_emoji(982179449447546940), bot.get_emoji(982179451129450496), bot.get_emoji(982179450932322314), bot.get_emoji(982179449950830603), bot.get_emoji(982179449019699261), bot.get_emoji(982179449929875496), bot.get_emoji(982199575458754641), bot.get_emoji(982179449984397312), bot.get_emoji(982179449485266945), bot.get_emoji(982179450462568448), bot.get_emoji(982179450420609034), bot.get_emoji(982179450072477766), bot.get_emoji(982179449959247932), bot.get_emoji(982179450311540736), bot.get_emoji(982179450621931530), bot.get_emoji(982179449845985310), bot.get_emoji(982179449212641300), bot.get_emoji(982179449464303637), bot.get_emoji(982182124071301140), bot.get_emoji(982179448927445033), bot.get_emoji(982179448952610836), bot.get_emoji(982179450173128724), bot.get_emoji(982182206732664892), bot.get_emoji(982179449313308693), bot.get_emoji(982179449141346345), bot.get_emoji(982179450668064768), bot.get_emoji(982181991573241886), bot.get_emoji(982182052629741568)]
                uno_games = []
                p0_game = uno_c(uno_cards = uno_cards)
                mem_str = "Uno players:"
                for mem in uno_members:
                    player = await bot.fetch_user(mem)
                    uno_games.append((player, uno_c(get_theme(mem), uno_cards)))
                    mem_str += f'''
<@!{mem}>'''
                await mess.channel.send(mem_str)
                game = 0
                winner = None
                for x in uno_games:
                    x[1].string_rows()
                    your_cards_1 = "**Your uno cards:**"
                    your_cards_2 = x[1].cards_string
                    try:
                        await x[0].send(your_cards_1)
                    except discord.errors.Forbidden:
                        for id in uno_members:
                            in_game.remove(id)
                        del live_uno[channel.id]
                        raise Exception("Cannot send messages to this user")
                    await x[0].send(your_cards_2)
                init_number = rd.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
                init_colour = rd.choice(["red", "green", "blue", "yellow"])
                top_card = (init_number, init_colour)
                await channel.send("Hop into your DMs and start playing!")
                num_cards = f"It is <@!{uno_games[0][0].id}>'s turn"
                num_cards += '''

'''
                for x in uno_games:
                    num_cards += f"<@!{x[0].id}>'s cards: **{len(x[1].cards)}**"
                    if uno_games.index(x) == 0:
                        num_cards += "*"
                    num_cards += '''
'''
                channel_commentary_embed = discord.Embed(title = "Uno!", description = num_cards, colour = discord.Colour.blue())
                channel_commentary_embed.set_footer(text = "The current player is denoted by *")
                channel_game_2 = "**Top card:**"
                channel_game_3 = p0_game.colour_card(top_card)
                channel_commentary = await channel.send(embed = channel_commentary_embed)
                channel_msg_2 = await channel.send(channel_game_2)
                channel_msg_3 = await channel.send(channel_game_3)
                live_uno[channel.id] = (channel.guild.id, channel_msg_3.id)
                turn = 0
                flag = 0
                while game == 0 and len(uno_games) > 1:
                    await asyncio.sleep(2)
                    p0 = uno_games[turn][0]
                    p0_game = uno_games[turn][1]
                    uno_said = None
                    if top_card[0] not in ["skip", "reverse", "+2", "+4"] or flag == 0:
                        await p0.send("It is your turn")
                        channel_description = ""
                        if p0_game.available_card(top_card):
                            while True:
                                p0_game.string_rows()
                                cur_turn_1 = "**Top card:**"
                                cur_turn_2 = p0_game.colour_card(top_card)
                                cur_turn_3 = "**Your cards:**"
                                cur_turn_4 = p0_game.cards_string
                                await p0.send(cur_turn_1)
                                await p0.send(cur_turn_2)
                                await p0.send(cur_turn_3)
                                await p0.send(cur_turn_4)
                                await p0.send("Choose the position of your card to play it; Enter 'quit' to leave the game")
                                try:
                                    pos_msg = await bot.wait_for("message", check = lambda m: m.author.id == p0.id and m.guild == None, timeout = 120.0)
                                except asyncio.TimeoutError:
                                    await p0.send("You took too long to respond so you have been removed from the game")
                                    await channel.send(f"<@!{p0.id}> took too long to respond so they have been removed from the game")
                                    channel_description = f"<@!{p0.id}> has been removed from the game as they took too long to respond"
                                    uno_games.pop(turn)
                                    uno_members.pop(turn)
                                    in_game.remove(p0.id)
                                    turn -= 1
                                    break
                                else:
                                    pos = pos_msg.content.lower()
                                    try:
                                        pos = int(pos)
                                    except ValueError:
                                        pos = pos.lower()
                                        if pos == "quit":
                                            uno_games.pop(turn)
                                            uno_members.pop(turn)
                                            in_game.remove(p0.id)
                                            await p0.send("We're sorry to see you leave 😢")
                                            await channel.send(f"<@!{p0.id}> has left the game 😢")
                                            channel_description = f"<@!{p0.id}> has left the game"
                                            turn -= 1
                                            break
                                        elif pos == "uno" and len(p0_game.cards) == 2 and uno_said != True:
                                            await channel.send(f"<@!{p0.id}> said **UNO**!")
                                            uno_said = True
                                        elif len(p0_game.cards) == 2 and uno_said != True:
                                            uno_said = False
                                            await p0.send("You can only enter integral values")
                                        else:
                                            await p0.send("You can only enter integral values")
                                    else:
                                        if len(p0_game.cards) == 2 and uno_said != True:
                                            uno_said = False
                                        if not (1 <= pos <= len(p0_game.cards)):
                                            await p0.send(f"You can only enter integers from 1 to {len(p0_game.cards)}")
                                        else:
                                            result = p0_game.choose_card(top_card, pos)
                                            if result[0]:
                                                top_card = result[1]
                                                chosen_card = p0_game.colour_card(result[1])
                                                await p0.send("You have chosen the card:")
                                                await p0.send(chosen_card)
                                                
                                                if result[1][0] in ["skip", "reverse", "+2", "+4"]:
                                                    flag = 1
                                                if result[1][1] == "colourful":
                                                    colour_msg = await p0.send("Choose a colour")
                                                    await colour_msg.add_reaction("🔴")
                                                    await colour_msg.add_reaction("🟢")
                                                    await colour_msg.add_reaction("🔵")
                                                    await colour_msg.add_reaction("🟡")
                                                    reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == p0.id and r.message == colour_msg and str(r.emoji) in ["🔴", "🟢", "🔵", "🟡"])
                                                    if str(reaction.emoji) == "🔴":
                                                        colour = "red"
                                                    elif str(reaction.emoji) == "🟢":
                                                        colour = "green"
                                                    elif str(reaction.emoji) == "🔵":
                                                        colour = "blue"
                                                    else:
                                                        colour = "yellow"
                                                    await p0.send(f"You chose the colour {colour}")
                                                if result[1][1] == "colourful":
                                                    top_card = list(top_card)
                                                    top_card[1] = colour
                                                    top_card = tuple(top_card)
                                                    channel_description = f"<@!{p0.id}> played a **{result[1][0]}** and chose the colour **{colour}**"
                                                else:
                                                    channel_description = f"<@!{p0.id}> played a **{result[1][1]} {result[1][0]}**"
                                                if result[2]:
                                                    await p0.send("You are the winner!")
                                                    game = 1
                                                    winner = p0.id
                                                else:
                                                    p0_game.string_rows()
                                                    cur_turn_3 = "**Your cards:**"
                                                    cur_turn_4 = p0_game.cards_string
                                                    await p0.send(cur_turn_3)
                                                    await p0.send(cur_turn_4)
                                                break
                                            else:
                                                await p0.send("That is not a valid card")
                        else:
                            p0_game.string_rows()
                            cur_turn_1 = "**Top card:**"
                            cur_turn_2 = p0_game.colour_card(top_card)
                            cur_turn_3 = "**Your cards:**"
                            cur_turn_4 = p0_game.cards_string
                            await p0.send(cur_turn_1)
                            await p0.send(cur_turn_2)
                            await p0.send(cur_turn_3)
                            await p0.send(cur_turn_4)
                            await asyncio.sleep(5)
                            p0_game.draw(1)
                            await p0.send("You have drawn a card because you do not have a valid card to play")
                            channel_description = f"<@!{p0.id}> did not have any valid card so they drew one"
                            while True:
                                p0_game.string_rows()
                                cur_turn_1 = "**Top card:**"
                                cur_turn_2 = p0_game.colour_card(top_card)
                                cur_turn_3 = "**Your cards:**"
                                cur_turn_4 = p0_game.cards_string
                                await p0.send(cur_turn_1)
                                await p0.send(cur_turn_2)
                                await p0.send(cur_turn_3)
                                await p0.send(cur_turn_4)
                                if p0_game.available_card(top_card):
                                    await p0.send("Choose the position of your card to play it; Enter 'quit' to leave the game")
                                    try:
                                        pos_msg = await bot.wait_for("message", check = lambda m: m.author.id == p0.id and m.guild == None, timeout = 120.0)
                                    except asyncio.TimeoutError:
                                        await p0.send("You took too long to respond so you have been removed from the game")
                                        await channel.send(f"<@!{p0.id}> took too long to respond so they have been removed from the game")
                                        channel_description = f"<@!{p0.id}> has been removed from the game as they took too long to respond"
                                        uno_games.pop(turn)
                                        uno_members.pop(turn)
                                        in_game.remove(p0.id)
                                        turn -= 1
                                        break
                                    else:
                                        pos = pos_msg.content.lower()
                                        try:
                                            pos = int(pos)
                                        except ValueError:
                                            pos = pos.lower()
                                            if pos == "quit":
                                                uno_games.pop(turn)
                                                uno_members.pop(turn)
                                                in_game.remove(p0.id)
                                                await p0.send("We're sorry to see you leave 😢")
                                                await channel.send(f"<@!{p0.id}> has left the game 😢")
                                                channel_description = f"<@!{p0.id}> has left the game"
                                                turn -= 1
                                                break
                                            elif pos == "uno" and len(p0_game.cards) == 2 and uno_said != True:
                                                await channel.send(f"<@!{p0.id}> said **UNO**!")
                                                uno_said = True
                                            elif len(p0_game.cards) == 2 and uno_said != True:
                                                uno_said = False
                                                await p0.send("You can only enter integral values")
                                            else:
                                                await p0.send("You can only enter integral values")
                                        else:
                                            if len(p0_game.cards) == 2 and uno_said != True:
                                                uno_said = False
                                            if not (1 <= pos <= len(p0_game.cards)):
                                                await p0.send(f"You can only enter integers from 1 to {len(p0_game.cards)}")
                                            else:
                                                result = p0_game.choose_card(top_card, pos)
                                                if result[0]:
                                                    top_card = result[1]
                                                    chosen_card = p0_game.colour_card(result[1])
                                                    await p0.send("You have chosen the card:")
                                                    await p0.send(chosen_card)
                                                    if result[1][0] in ["skip", "reverse", "+2", "+4"]:
                                                        flag = 1
                                                    if result[1][1] == "colourful":
                                                        colour_msg = await p0.send("Choose a colour")
                                                        await colour_msg.add_reaction("🔴")
                                                        await colour_msg.add_reaction("🟢")
                                                        await colour_msg.add_reaction("🔵")
                                                        await colour_msg.add_reaction("🟡")
                                                        reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == p0.id and r.message == colour_msg and str(r.emoji) in ["🔴", "🟢", "🔵", "🟡"])
                                                        if str(reaction.emoji) == "🔴":
                                                            colour = "red"
                                                        elif str(reaction.emoji) == "🟢":
                                                            colour = "green"
                                                        elif str(reaction.emoji) == "🔵":
                                                            colour = "blue"
                                                        else:
                                                            colour = "yellow"
                                                        await p0.send(f"You chose the colour {colour}")
                                                    if result[1][1] == "colourful":
                                                        top_card = list(top_card)
                                                        top_card[1] = colour
                                                        top_card = tuple(top_card)
                                                        channel_description = f"<@!{p0.id}> drew a card and played a **{result[1][0]}** and chose the colour **{colour}**"
                                                    else:
                                                        channel_description = f"<@!{p0.id}> drew a card and played a **{result[1][1]} {result[1][0]}**"
                                                    if result[2]:
                                                        await p0.send("You are the winner!")
                                                        game = 1
                                                        winner = p0.id
                                                    else:
                                                        p0_game.string_rows()
                                                        cur_turn_3 = "**Your cards:**"
                                                        cur_turn_4 = p0_game.cards_string
                                                        await p0.send(cur_turn_3)
                                                        await p0.send(cur_turn_4)
                                                    break
                                                else:
                                                    await p0.send("That is not a valid card")
                                                
                                else:
                                    await p0.send("Your turn has ended")
                                    channel_description = f"<@!{p0.id}> could not play any card so their turn has passed on"
                                    break
                        channel_description += '''

'''
                        for x in uno_games:
                            channel_description += f"<@!{x[0].id}>'s cards: **{len(x[1].cards)}**"
                            if uno_games.index(x) == turn+1 or (uno_games.index(x) == 0 and turn+1 == len(uno_games)):
                                channel_description += "*"
                            channel_description += '''
'''
                        coloured_card = p0_game.colour_card(top_card)
                        channel_commentary_embed = discord.Embed(title = "Uno!", description = channel_description, colour = discord.Colour.blue())
                        channel_commentary_embed.set_footer(text = "The current player is denoted by *")
                        await channel_commentary.edit(embed = channel_commentary_embed)
                        await channel_msg_3.edit(content = coloured_card)
                    else:
                        p0_game.string_rows()
                        cur_turn_1 = "**Top card:**"
                        cur_turn_2 = p0_game.colour_card(top_card)
                        cur_turn_3 = "**Your cards:**"
                        cur_turn_4 = p0_game.cards_string
                        await p0.send(cur_turn_1)
                        await p0.send(cur_turn_2)
                        await p0.send(cur_turn_3)
                        await p0.send(cur_turn_4)
                        if top_card[0] == "skip":
                            await p0.send(f"You have been skipped by <@!{uno_games[turn-1][0].id}>")
                            channel_description = f"<@!{p0.id}> was skipped"
                        elif top_card[0] == "reverse":
                            await p0.send("The order has been reversed so it is not your turn now")
                            if len(uno_games) > 2:
                                player_b4 = uno_games[turn-2]
                            else:
                                player_b4 = uno_games[turn-1]
                            uno_games.reverse()
                            turn = uno_games.index(player_b4)-1
                            channel_description = "The order has been reversed"
                        elif top_card[0] == "+2":
                            await p0.send("You have to draw 2 cards now")
                            p0_game.draw(2)
                            p0_game.string_rows()
                            cur_turn_1 = "**Top card:**"
                            cur_turn_2 = p0_game.colour_card(top_card)
                            cur_turn_3 = "**Your cards:**"
                            cur_turn_4 = p0_game.cards_string
                            await p0.send(cur_turn_1)
                            await p0.send(cur_turn_2)
                            await p0.send(cur_turn_3)
                            await p0.send(cur_turn_4)
                            channel_description = f"<@!{p0.id}> drew 2 cards"
                        elif top_card[0] == "+4":
                            await p0.send("You have to draw 4 cards now")
                            p0_game.draw(4)
                            p0_game.string_rows()
                            cur_turn_1 = "**Top card:**"
                            cur_turn_2 = p0_game.colour_card(top_card)
                            cur_turn_3 = "**Your cards:**"
                            cur_turn_4 = p0_game.cards_string
                            await p0.send(cur_turn_1)
                            await p0.send(cur_turn_2)
                            await p0.send(cur_turn_3)
                            await p0.send(cur_turn_4)
                            channel_description = f"<@!{p0.id}> drew 4 cards"
                        channel_description += '''

'''
                        for x in uno_games:
                            channel_description += f"<@!{x[0].id}>'s cards: **{len(x[1].cards)}**"
                            if uno_games.index(x) == turn+1 or (uno_games.index(x) == 0 and turn+1 == len(uno_games)):
                                channel_description += "*"
                            channel_description += '''
'''
                        coloured_card = p0_game.colour_card(top_card)
                        channel_commentary_embed = discord.Embed(title = "Uno!", description = channel_description, colour = discord.Colour.blue())
                        channel_commentary_embed.set_footer(text = "The current player is denoted by *")
                        await channel_commentary.edit(embed = channel_commentary_embed)
                        await channel_msg_3.edit(content = coloured_card)
                        flag = 0

                    if uno_said == False:
                        while True:
                            uno_tasks = [asyncio.create_task(bot.wait_for("message", check = lambda m: m.channel.id == channel.id and m.author.id != p0.id and m.author.id in uno_members and str(m.content).lower() == "caught", timeout = 10.0), name = "caught"), asyncio.create_task(bot.wait_for("message", check = lambda m: m.guild == None and m.author.id == p0.id and str(m.content).lower() == "uno", timeout = 10.0), name = "uno")]

                            completed, pending = await asyncio.wait(uno_tasks, return_when = asyncio.FIRST_COMPLETED)
                            
                            finished_task: asyncio.Task = list(completed)[0]
                            
                            for unfinished in pending:
                                try:
                                    unfinished.cancel()
                                except asyncio.CancelledError:
                                    pass

                            action = finished_task.get_name()
                            try:
                                result = finished_task.result()
                            except asyncio.TimeoutError:
                                await channel.send(f"<@!{p0.id}> did not say uno and none of the other players caught them within the 10s time limit so they are not subject to the four card penalty! The next player's turn will start in a few seconds")
                                break

                            else:
                                if action == "caught":
                                    await channel.send(f"You have caught <@!{p0.id}> as they did not say uno! They now have to draw 4 cards")

                                    channel_description = f'''<@!{p0.id}> did not say uno and was caught by <@!{result.author.id}>

'''
                                    p0_game.draw(4)
                                    for x in uno_games:
                                        channel_description += f"<@!{x[0].id}>'s cards: **{len(x[1].cards)}**"
                                        if uno_games.index(x) == turn+1 or (uno_games.index(x) == 0 and turn+1 == len(uno_games)):
                                            channel_description += "*"
                                        channel_description += '''
'''
                                    coloured_card = p0_game.colour_card(top_card)
                                    channel_commentary_embed = discord.Embed(title = "Uno!", description = channel_description, colour = discord.Colour.blue())
                                    channel_commentary_embed.set_footer(text = "The current player is denoted by *")
                                    await channel_commentary.edit(embed = channel_commentary_embed)
                                    await p0.send(f"You did not say uno and <@!{result.author.id}> caught you so you have to draw 4 cards now")
                                    p0_game.string_rows()
                                    cur_turn_3 = "**Your cards:**"
                                    cur_turn_4 = p0_game.cards_string
                                    await p0.send(cur_turn_3)
                                    await p0.send(cur_turn_4)
                                    break
                                elif action == "uno":
                                    await channel.send(f"<@!{p0.id}> said uno before they were caught and does not have to draw any cards now!")
                                    break
                            
                    turn += 1
                    if turn == len(uno_games):
                        turn = 0
                    
                if game == 0:
                    await channel.send(f"<@!{uno_games[0][0].id}> is the winner!")
                    in_game.remove(uno_games[0][0].id)
                else:
                    await channel.send(f"<@!{winner}> is the winner!")
                    for x in uno_games:
                        in_game.remove(x[0].id)
                del live_uno[channel.id]
                
            else:
                await mess.channel.send("You need at least 2 players to play uno, so the game has been cancelled")
                in_game.remove(host_id)
                del live_uno[channel.id]
        else:
            if mess.channel.id not in live_uno.keys():
                await mess.channel.send("You're already in a game!")
            else:
                await mess.channel.send("There is already an uno game going on in this channel!")
    else:
        await mess.channel.send("This is not a DM command!")

@bot.command(name = "wd", description = "Start a game of wordle", aliases = ["wordle"])
async def wd(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("wordle")
    if not(isinstance(mess.channel, discord.DMChannel)):
        valid_id = 0
        channel_id = mess.channel.id
        if msg.startswith(";wordle <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";wordle <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";wd <@!") and msg.endswith(">"):
            opp_id_temp = msg.replace(";wd <@!", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";wordle <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";wordle <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        elif msg.startswith(";wd <@") and msg.endswith(">"):
            opp_id_temp = msg.replace(";wd <@", "")
            opp_id = opp_id_temp.replace(">", "")
            try:
                int(opp_id)
                valid_id = 1
            except ValueError:
                pass
        if valid_id == 1:
            opp_id = int(opp_id)
            try:
                a_id = mess.author.id
                me = await bot.fetch_user(a_id)
                opponent = await bot.fetch_user(opp_id)
                server_id = mess.guild.id
                guild = bot.get_guild(server_id)
                channel = mess.channel
                members = []
                for m in guild.members:
                    members.append(m)
                if opponent in members and opponent != me and not(opponent.bot):
                    if a_id not in in_game and opp_id not in in_game:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of wordle! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
                        in_game.append(a_id)
                        in_game.append(opp_id)
                        try:
                            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                        except asyncio.TimeoutError:
                            await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                        else:
                            if str(reaction.emoji) == "✅":
                                all_words = open("five_letter_words.txt", "r").read().splitlines()
                                p1_id = rd.choice([a_id, opp_id])
                                if p1_id == a_id:
                                    p2_id = opp_id
                                else:
                                    p2_id = a_id
                                await mess.channel.send(f"<@!{p1_id}> check your DMs for a message from me to enter your 5 letter word!")
                                game = wordle(p1_id, p2_id, get_theme(p2_id))
                                p1 = await bot.fetch_user(p1_id)
                                while True:
                                    await p1.send("Enter your hidden word; it must consist of only 5 letters")
                                    try:
                                        word_msg = await bot.wait_for("message", check = lambda m: m.author.id == p1_id and m.guild == None, timeout = 120.0)
                                    except asyncio.TimeoutError:
                                        await p1.send("You took too long to respond so the game has ended")
                                        await channel.send(f"<@!{p2_id}>, <@!{p1_id}> took too long to respond so the game has ended")
                                        game.game = 1
                                        break
                                    else:
                                        word = str(word_msg.content).lower()
                                        valid = 1
                                        if len(word) == 5:
                                            for x in word:
                                                if not(x.isalpha()):
                                                    await p1.send("Your word can only consist of letters")
                                                    valid = 0
                                                    break
                                            if valid == 1:
                                                if word not in all_words:
                                                    await p1.send("This is not a valid word")
                                                    valid = 0
                                        else:
                                            await p1.send("You can only enter a 5 letter word")
                                            valid = 0
                                        if valid == 1:
                                            break
                                if game.game == 0:
                                    game.colourify(word, 1)
                                    hword_str = ""
                                    for x in game.hword:
                                        hword_str += x
                                    await p1.send(f"You have chosen the word {hword_str}. Head back to <#{channel.id}> to watch the match!")
                                    await channel.send(f"<@!{p2_id}> the word has been chosen! Get ready!")
                                    timeout = 0
                                    while game.game == 0 and game.turns < 6 and timeout == 0:
                                        game.string_rows()
                                        game_grid = discord.Embed(title = "Wordle!", description = game.grid, colour = discord.Colour.blue())
                                        game_grid.add_field(name = "Keyboard", value = game.keyboard_string)
                                        await channel.send(embed = game_grid)
                                        while True:
                                            await channel.send("Guess a 5 letter word (Enter 'quit' to leave the game; Enter 'grid' to view the current board)")
                                            try:
                                                guess_msg = await bot.wait_for("message", check = lambda m: m.author.id == p2_id and m.channel.id == channel.id, timeout = 120.0)
                                            except asyncio.TimeoutError:
                                                await channel.send("You took too long to respond so the game has ended")
                                                timeout = 1
                                                break
                                            else:
                                                word = str(guess_msg.content).lower()
                                                valid = 1
                                                if len(word) == 5:
                                                    for x in word:
                                                        if not(x.isalpha()):
                                                            await channel.send("Your word can only consist of letters")
                                                            valid = 0
                                                            break
                                                    if valid == 1:
                                                        if word not in all_words:
                                                            await channel.send("This is not a valid word")
                                                            valid = 0
                                                else:
                                                    if word == "quit":
                                                        await channel.send("We're sorry to see you leave 😢")
                                                        timeout = 1
                                                        break
                                                    elif word == "grid":
                                                        game.string_rows()
                                                        game_grid = discord.Embed(title = "Wordle!", description = game.grid, colour = discord.Colour.blue())
                                                        game_grid.add_field(name = "Keyboard", value = game.keyboard_string)
                                                        await channel.send(embed = game_grid)
                                                    else:
                                                        await channel.send("You can only enter a 5 letter word")
                                                    valid = 0
                                                if valid == 1:
                                                    game.guess(word)
                                                    break
                                    if game.turns == 6:
                                        game.winner = p1_id
                                    if timeout == 0:
                                        game.string_rows()
                                        game_grid = discord.Embed(title = "Wordle!", description = game.grid, colour = discord.Colour.blue())
                                        game_grid.add_field(name = "Keyboard", value = game.keyboard_string)
                                        await channel.send(embed = game_grid)
                                        await channel.send(f"<@!{game.winner}> is the winner!")


                        in_game.remove(a_id)
                        in_game.remove(opp_id)
                    else:
                        if a_id in in_game:
                            await mess.channel.send("You're already in a game!")
                        else:
                            await mess.channel.send("Your opponent is already in a game!")     

                else:
                    if opponent != me and not(opponent.bot):
                        dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                        await mess.channel.send(embed = dual_game)
                        
                        
            except discord.errors.NotFound:
                dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                
                
        else:
            dual_game = discord.Embed(title = "Invalid syntax!", description = "The wordle syntax is invalid! The correct syntax is: ;wordle/;wd @user", color = discord.Color.blue())
            await mess.channel.send(embed = dual_game)
    else:
        await mess.channel.send("You can't play a match against someone in a DM!")

@bot.command(name = "tzfe", description = "Start a game of 2048", aliases = ["2048"])
async def tzfe(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("tzfe")
    author_id = mess.author.id
    if author_id not in in_game:
        in_game.append(author_id)
        p0 = mess.author
        a = bot.get_emoji(1006186622322212914)
        b = bot.get_emoji(1006186619822419970)
        c = bot.get_emoji(1006186617746239558)
        d = bot.get_emoji(1006186615300968458)
        e = bot.get_emoji(1006186612826321007)
        f = bot.get_emoji(1006186610456539296)
        g = bot.get_emoji(1006186607793156139)
        h = bot.get_emoji(1006186605469515897)
        i = bot.get_emoji(1006186602567041074)
        j = bot.get_emoji(1006186600197275678)
        k = bot.get_emoji(1006186597529698364)
        dirs = {"w": "up", "a": "left", "d": "right", "s": "down"}
        game = tzfe_c(a, b, c, d, e, f, g, h, i, j, k, get_theme(author_id))
        game.string_rows()
        game_embed = discord.Embed(title = "2048!", description = f"Player: <@!{author_id}>\nScore: {game.score}", colour = discord.Colour.blue())
        await mess.channel.send(embed = game_embed)
        await mess.channel.send(game.game_board)
        while game.game == 1:
            while True:
                await mess.channel.send("Enter the direction in which you would like to swipe ('w' for up, 's' for down, 'a' for left, 'd' for right); Enter 'quit' to quit the game, Enter 'board' to see the current board")
                try:
                    reaction_msg = await bot.wait_for("message", check = lambda m: m.author.id == author_id and m.channel.id == mess.channel.id, timeout = 120.0)
                except asyncio.TimeoutError:
                    await mess.channel.send(f"<@!{author_id}> you took too long to respond to the game has ended")
                    game.game = 0
                    in_game.remove(author_id)
                    break
                else:
                    dir = str(reaction_msg.content).lower()
                    if dir not in dirs.keys():
                        if dir == "quit":
                            await mess.channel.send("We're sorry to see you leave 😢")
                            game.game = 0
                            in_game.remove(author_id)
                            break
                        elif dir == "board":
                            game.string_rows()
                            game_embed = discord.Embed(title = "2048!", description = f"Player: <@!{author_id}>\nScore: {game.score}", colour = discord.Colour.blue())
                            await mess.channel.send(embed = game_embed)
                            await mess.channel.send(game.game_board)
                        else:
                            await mess.channel.send("Invalid direction")
                    else:
                        dir = dirs[dir]
                        break
            if game.game == 1:
                game.swipe(dir)
                game.string_rows()
                game_embed = discord.Embed(title = "2048!", description = f"Player: <@!{author_id}>\nScore: {game.score}", colour = discord.Colour.blue())
                await mess.channel.send(embed = game_embed)
                await mess.channel.send(game.game_board)
                if game.game == 0:
                    await mess.channel.send(f"<@!{author_id}> you won! Your final score is {game.score}")
                    in_game.remove(author_id)
                    break
                game.game_over()
                if game.game == 0:
                    await mess.channel.send(f"<@!{author_id}> the game is over! Your final score is {game.score}")
                    in_game.remove(author_id)
                    break
       
    else:
        await mess.channel.send("You're already in a game!")

@bot.command(name = "trivia", description = "Get a random multiple choice trivia question", aliases = ["quiz"])
async def trivia(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("trivia")
    author_id = mess.author.id
    if author_id not in in_game:
        if msg == ";trivia" or msg == ";quiz":
            question_data = requests.get("https://the-trivia-api.com/api/questions?limit=1").json()[0]
        else:
            if msg.startswith(";trivia "):
                t = msg.replace(";trivia ", "")
            elif msg.startswith(";quiz "):
                t = msg.replace(";quiz ", "")
            if t not in ["easy", "medium", "hard"]:
                await mess.channel.send("Invalid difficulty")
                return
            else:
                question_data = requests.get(f"https://the-trivia-api.com/api/questions?limit=1&difficulty={t}").json()[0]
        question = question_data["question"]
        options = question_data["incorrectAnswers"]
        options.append(question_data["correctAnswer"])
        rd.shuffle(options)
        question_embed = discord.Embed(title = "Trivia!", description = f"*Difficulty*: **{question_data['difficulty'].capitalize()}**", colour = discord.Colour.blue())
        question_embed.add_field(name = "Question", value = f"**{question}**", inline = False)
        question_embed.add_field(name = "Options", value = f'''1️⃣ *{str(options[0]).capitalize()}*
2️⃣ *{str(options[1]).capitalize()}*
3️⃣ *{str(options[2]).capitalize()}*
4️⃣ *{str(options[3]).capitalize()}*
''', inline = False)
        question_final = await mess.channel.send(embed = question_embed)
        await question_final.add_reaction("1️⃣")
        await question_final.add_reaction("2️⃣")
        await question_final.add_reaction("3️⃣")
        await question_final.add_reaction("4️⃣")
        try:
            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"] and r.message.id == question_final.id and p.id == author_id, timeout = 120.0)
        except asyncio.TimeoutError:
            await question_final.reply(f"<@!{author_id}> you took too long to respond so the question has been cancelled")
        else:
            t = {"1️⃣": 0, "2️⃣": 1, "3️⃣": 2, "4️⃣": 3}
            if options[t[str(reaction.emoji)]] == question_data["correctAnswer"]:
                await question_final.reply(f"<@!{author_id}> you chose the option `{options[t[str(reaction.emoji)]].capitalize()}` and that is the correct answer!", mention_author = False)
            else:
                await question_final.reply(f"<@!{author_id}> you chose the option `{options[t[str(reaction.emoji)]].capitalize()}` and that is incorrect! The correct answer is `{question_data['correctAnswer'].capitalize()}`", mention_author = False)
    else:
        await mess.channel.send("You're already in a game!")

@bot.command(name = "flags", description = "Get a random flag and guess the country")
async def flags(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("flags")
    author_id = mess.author.id
    if author_id not in in_game:
        df = pd.read_csv("flag_codes.txt", delimiter = "\t")
        flag_codes = df.to_numpy().tolist()
        real_flag = rd.choice(flag_codes)
        flag_codes.remove(real_flag)
        options = [real_flag]
        for t in range(3):
            option_flag = rd.choice(flag_codes)
            options.append(option_flag)
            flag_codes.remove(option_flag)
        rd.shuffle(options)
        flag_id = str(real_flag[1])
        if len(flag_id) != 3:
            flag_id = "0"*(3-(len(flag_id)))+flag_id
        flag_image = f"https://countryflagsapi.com/png/{flag_id}"
        question_embed = discord.Embed(title = "Flags!", description = "**Which country's flag is shown below?**", colour = discord.Colour.blue())
        question_embed.add_field(name = "Options", value = f'''1️⃣ *{options[0][0]}*
2️⃣ *{options[1][0]}*
3️⃣ *{options[2][0]}*
4️⃣ *{options[3][0]}*
''', inline = False)
        question_embed.set_image(url = flag_image)
        question_final = await mess.channel.send(embed = question_embed)
        await question_final.add_reaction("1️⃣")
        await question_final.add_reaction("2️⃣")
        await question_final.add_reaction("3️⃣")
        await question_final.add_reaction("4️⃣")
        try:
            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"] and r.message.id == question_final.id and p.id == author_id, timeout = 120.0)
        except asyncio.TimeoutError:
            await question_final.reply(f"<@!{author_id}> you took too long to respond so the question has been cancelled")
        else:
            t = {"1️⃣": 0, "2️⃣": 1, "3️⃣": 2, "4️⃣": 3}
            if options[t[str(reaction.emoji)]][0] == real_flag[0]:
                await question_final.reply(f"<@!{author_id}> you chose the option `{options[t[str(reaction.emoji)]][0]}` and that is the correct answer!", mention_author = False)
            else:
                await question_final.reply(f"<@!{author_id}> you chose the option `{options[t[str(reaction.emoji)]][0]}` and that is incorrect! The correct answer is `{real_flag[0]}`", mention_author = False)

    else:
        await mess.channel.send("You're already in a game!")

@bot.command(name = "other", description = "List all the other games on the bot")
async def other(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("other")
    page = 1
    while True:
        if page == 1:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 1/5")
            other_games.add_field(name = "Connect 4", value = '''
Connect 4 or Four-in-a-row is now here on the minesweeper bot! The main aim of this game is to get 4 of your tokens in a line: horizontally, vertically, or diagonally. Drop your tokens in the columns to place them!

**Complete rules**: https://www.ultraboardgames.com/connect4/game-rules.php
**Commands and aliases**: `;connect4`, `;c4` 
''', inline = False)
            other_games.add_field(name = "Othello", value = '''
Othello is now here on the minesweeper bot! There are 2 players who play this game, and they are given one of two colours: black and white. Black goes first. The rules are as follows:
1. You can only place your coin in a position that 'outflanks' at least one of your opponent's coins. Outflanking means that the coin you place and another one of your placed coins must be at the two ends of your opponent's coins.
2. After placing the coin, any of the opponent's coins that are outflanked by the coin you placed and another one of your coins, is turned over.
3. If you cannot place a coin anywhere, the bot will automatically pass on the turn to the other player.
4. The game ends when the board is full, or nobody else can place a coin in a valid position. Whoever has more of their coins on the board at this point wins!

**Complete rules**: https://www.ultraboardgames.com/othello/game-rules.php
**Commands and aliases**: `;othello`, `;oto`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "▶" and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 2
                await o_games.delete()

        elif page == 2:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 2/5")
            other_games.add_field(name = "Mastermind", value = '''
Mastermind is now here on the minesweeper bot! 2 players play this game and they are give one of two roles - the code setter, or the code guesser. The code setter will make a code following a prompt from the bot in their DMs. The code will consist of 4 colours, which can be repeated. The code guesser will then have to guess the code in a maximum of 8 turns. Following each turn, the code guesser will see how close their guess is to the actual word. This will be seen at the side of the grid in the following form:
✅ - Correct colour in the correct position
☑️ - Correct colour in the wrong position
❌ - Wrong colour
These icons will be given for each of the 4 guessed colour positions, but these icons will be given at random - they will not correspond to any particular position. Deduce the correct code to win the game!

**Complete rules**: https://www.ultraboardgames.com/mastermind/game-rules.php
**Commands and aliases**: `;mastermind`, `;mm` 
''', inline = False)
            other_games.add_field(name = "Yahtzee", value = '''
Yahtzee is now here on the minesweeper bot! This game is played with 2 players who play completely indivual games. The game requires the players to roll 5 dice in a total of 3 rolls. After each roll, the players can choose to hold a few of the dice to prevent them from being rolled the next time. This is essential in completing the cards that the players have. The cards have different fields that have to be filled: *Aces, Twos, Threes, Fours, Fives, and Sixes* in the Upper section, and *3 of a kind, 4 of a kind, Full house, Small straight, Large straight, Yahtzee, and Chance* in the Lower section. Each of these fields have specific criteria that have to be met to place your points in the fields. These criteria can be found in the link given below. Complete your cards to obtain a final score. The player with the highest final score wins the game!

**Complete rules**: https://www.ultraboardgames.com/yahtzee/game-rules.php
**Commands and aliases**: `;yahtzee`, `;yz`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("◀")
            await o_games.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                if str(reaction.emoji) == "◀":
                    page = 1
                else:
                    page = 3
                await o_games.delete()
        
        elif page == 3:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 3/5")
            other_games.add_field(name = "Battleship", value = '''
Battleship is now here on the minesweeper bot! An intense two-player game, battleship requires players to destroy each others ships fastest. Based on the theme of naval warfare, the players will first have to place their ships in strategic positions to avoid getting blasted by the other player's cannons. Turn by turn, the players will then enter coordinates as they try to locate and destroy each of the opponent's 5 ships. The first person to destroy all of the other person's ships wins! Other people can follow the game by using the `;live` command in the channel the game was started in!

**Complete rules**: https://www.ultraboardgames.com/battleship/game-rules.php
**Commands and aliases**: `;battleship`, `;bs`, `;live`
''', inline = False)
            other_games.add_field(name = "Hangman", value = '''
Hangman is now here on the minesweeper bot! An old classic, hangman is a game where one person decides on a word or phrase and then draws blanks corresponding to each letter of the word/phrase. The vowels may or may not be revealed, but in this version we will reveal the vowels beforehand. The other player must then guess individual letters to fill in the blanks. For every incorrect guess, a body part of the man will be revealed. If the player successfully guesses all the letters before the man is completely hanged, he will win the game!

**Complete rules**: https://www.ultraboardgames.com/hangman/game-rules.php
**Commands and aliases**: `;hangman`, `;hm`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("◀")
            await o_games.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                if str(reaction.emoji) == "◀":
                    page = 2
                else:
                    page = 4
                await o_games.delete()
    
        elif page == 4:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 4/5")
            other_games.add_field(name = "Uno", value = '''
Uno is now here on the minesweeper bot! Players play cards that match the top card by face value or by colour. You can also play special cards to hamper the progress of the other players! Before you play your second last card, you must say `uno` in the DM and then play the card. If you play the card without saying `uno`, someone else can say `caught` in the game channel within 10 seconds and then you will have to draw 4 cards. However, even after playing your second last card, you can say `uno` before someone else catches you and then you would not be subject to the 4 card penalty. If neither `uno` nor `caught` is said within 10 seconds, the 4 card penalty will not be applicable. Whoever finishes all their cards first wins the game! Everyone plays uno with different rules so it is recommended that you check out the rules in the link below as those are the rules used with this bot.

**Complete rules**: https://www.ultraboardgames.com/uno/game-rules.php
**Commands and aliases**: `;uno`, `;live`
''', inline = False)
            other_games.add_field(name = "Wordle", value = '''
Wordle is now here on the minesweeper bot! Given a hidden 5 letter word, the player must try to guess the word by making their own valid word guesses. The following colours indicate the status of a letter in the guessed word:
🟩 - Correct letter in the correct position
🟨 - Correct letter in the wrong position
🟥 - Wrong letter
These colours will be in order, so you will know exactly which letter corresponds to which colour. Using these colours, deduce the hidden word to win the game! Wordle on the minesweeper comes with a little twist - it's a two player game! One player will give a word that the other player has to guess!

**Complete rules**: https://www.nytimes.com/games/wordle/index.html
**Commands and aliases**: `;wordle`, `;wd`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("◀")
            await o_games.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                if str(reaction.emoji) == "◀":
                    page = 3
                else:
                    page = 5
                await o_games.delete()

        elif page == 5:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 5/5")
            other_games.add_field(name = "2048", value = '''
2048 is now here on the minesweeper bot! A highly addictive and fun game, 2048 is based on moving tiles and when tiles having the same number on them bump into each other, they will add up. If you manage to add up to 2048, you win the game! To slide the tiles, you will have to use the WASD keys as arrow keys. With every swipe, all tiles on the board move in that direction. You can also look at an incremental score counter that comes along with the board!

**Commands and aliases**: `;2048`, `;tzfe`
''', inline = False)
            other_games.add_field(name = "Trivia", value = '''
Trivia is now here on the minesweeper bot! In the mood for some fun trivia? Use the trivia command to get a random multiple choice trivia question for you to answer! Try out as many questions as you want - there are no limits! If you want to personalize the question furthur, you can also choose the difficulty for the question that you receive. Are you a flag enthusiast? We also have a flag quiz with the bot! Try to guess as many flags as you can!

**Commands and aliases**: `;trivia`, `;quiz`, `;flags`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("◀")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "◀" and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 4
                await o_games.delete()

@bot.command(name = "invite", description = "Send an invite link for the bot")
async def invite(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("invite")
    invite = discord.Embed(title = "Invite me to your server!", description = "Use this link to invite me: https://dsc.gg/minesweeper-bot", colour = discord.Colour.blue())
    await mess.channel.send(embed = invite)

@bot.command(name = "support", description = "Send an invite link for the support server")
async def support(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("support")
    support = discord.Embed(title = "Join the official minesweeper bot support server!", description = "Use this link to join the server: https://dsc.gg/minesweeper", colour = discord.Colour.blue())
    await mess.channel.send(embed = support)

@bot.command(name = "vote", description = "Send all the voting links for the bot")
async def vote(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("vote")
    vote = discord.Embed(title = "Vote for me!", description = '''Enjoyed using the bot?
Vote for us on `top.gg`: https://top.gg/bot/902498109270134794/vote
Vote for us on `discordbotlist.com`: https://discordbotlist.com/bots/minesweeper-bot/upvote
Vote for us on `discords.com`: https://discords.com/bots/bot/902498109270134794/vote
Vote for us on `bots.discordlabs.org`: https://bots.discordlabs.org/bot/902498109270134794?vote''', colour = discord.Colour.blue())
    await mess.channel.send(embed = vote)

@bot.command(name = "website", description = "Send the link for the website")
async def website(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("website")
    website = discord.Embed(title = "Visit our website!", description = "Use this link to view our website: https://minesweeper-bot.carrd.co", colour = discord.Colour.blue())
    await mess.channel.send(embed = website)

@bot.command(name = "strength", description = "A private command to view the number of servers the bot is in")
async def strength(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)) or not(mess.author.id == 706855396828250153):
        return

    await mess.channel.send(f"I'm in {len(bot.guilds)} servers!")
    bot_count = bot.get_channel(948144061305479198)
    await bot_count.edit(name = f"Servers: {len(bot.guilds)}")
    await mess.channel.send("Updated server count in <#948144061305479198>")

@bot.command(name = "count", description = "A private command to view the number of minesweeper users")
async def count(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)) or not(mess.author.id == 706855396828250153):
        return
    
    await mess.channel.send(f"We have {member_count()} users!")

@bot.command(name = "stats", description = "A private command to view the command statistics of the bot")
async def stats(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)) or not(mess.author.id == 706855396828250153):
        return

    commands_data = get_stats()
    commands = list(commands_data.keys())
    values = list(commands_data.values())

    fig = plt.figure(figsize = (16, 9))
    plt.barh(commands, values, color = "blue")
    plt.ylabel("Commands")
    plt.xlabel("Number of calls")
    plt.title("Commands data")
    plt.savefig("commands_graph.png")
    await mess.channel.send("Commands graph", file = discord.File("commands_graph.png"))

@bot.command(name = "help", description = "View the help page of the bot")
async def help(mess: commands.Context):
    global in_game
    msg = mess.message.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("help")
    page = 1
    while True:
        if page == 1:
            help_embed = discord.Embed(title = "A complete guide on how to use the Minesweeper Bot!", description = "This bot allows you to play a collection of some extremely entertaining games on discord! The prefix for the bot is `;`.", colour = discord.Colour.blue())
            help_embed.set_footer(text = "Help Page 1/2")
            help_embed.add_field(name = "Rules: ", value = 
            '''The basic rules of minesweeper are:
1. Behind each circle is either a bomb, a number, or nothing.
2. If you hit a bomb you lose the game.
3. The number signifies how many bombs are there behind the circles adjacent to it (diagonals included).
4. If you know the location of a bomb, you can place a flag over there for reference.
5. Open up all the circles without the bombs to win the game!''', inline = False)
            help_embed.add_field(name = "The Nexus:", value = "[Invite Me](https://discord.com/oauth2/authorize?client_id=902498109270134794&permissions=274878188608&scope=bot%20applications.commands) · [Support Server](https://discord.gg/3jCG74D3RK) · [Vote for Us!](https://top.gg/bot/902498109270134794/vote) · [GitHub](https://github.com/vsmart-06/minesweeper-hosting) · [Privacy Policy](https://gist.github.com/vsmart-06/cc24bd805d50c519853c43adafb993d7) · [Terms of Service](https://gist.github.com/vsmart-06/f68961c5515cb50025db1a34f4e2a1a4) · [Website](https://minesweeper-bot.carrd.co)", inline = False)
            help = await mess.channel.send(embed = help_embed)
            await help.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "▶" and p.id != bot.user.id and r.message.id == help.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 2
                await help.delete()

        elif page == 2:
            help_embed = discord.Embed(title = "A complete guide on how to use the Minesweeper Bot!", description = "This bot allows you to play a collection of some extremely entertaining games on discord! The prefix for the bot is `;`.", colour = discord.Colour.blue())
            help_embed.set_footer(text = "Help Page 2/2")
            help_embed.add_field(name = "Commands: ", value = 
'''
`;help`: Open the guide.
`;minesweeper`/`;ms`: Start a new minesweeper game in an 8x8 grid with 8 bombs. Tag someone else to play a game against them!
`;minesweepercustom`/`;mscustom`: Start a custom minesweeper game.
`;tournament`: Start a minesweeper tournament in your server!
`;leaderboard`/`;lb`: View the global leaderboard.
`;serverleaderboard`/`;serverlb`: View the server leaderboard.
`;profile`: View your personal minesweeper bot profile. Tag someone else to view their profile as well!
*`;profile settings private/public`: Control who can view your profile. By default it is set to public.
*`;theme settings light/dark`: Change the theme the bot uses for your games. By default it is set to dark.
*`;delete`: Delete all your data on the minesweeper bot.
`;other`: **View other games that can be played on the bot!**
`;invite`: Get a link to invite this bot to a server.
`;support`: Get a link to join the official minesweeper bot support server.
`;website`: Get a link to our website.
`;vote`: Vote for the bot!
''', inline = False)
            help_embed.add_field(name = "Note:", value = "*: These commands, despite giving a confirmation message, will not have any effect unless the user plays at least 1 game of normal minesweeper on the bot.", inline = False)
            help_embed.add_field(name = "Slash Commands", value = "Slash commands are also available with the minesweeper bot! Type `/` and click on the minesweeper bot's icon to view all of its slash commands! If you cannot see them, you may have to re-invite the bot to your server.")
            help_embed.add_field(name = "The Nexus:", value = "[Invite Me](https://discord.com/oauth2/authorize?client_id=902498109270134794&permissions=274878188608&scope=bot%20applications.commands) · [Support Server](https://discord.gg/3jCG74D3RK) · [Vote for Us!](https://top.gg/bot/902498109270134794/vote) · [GitHub](https://github.com/vsmart-06/minesweeper-hosting) · [Privacy Policy](https://gist.github.com/vsmart-06/cc24bd805d50c519853c43adafb993d7) · [Terms of Service](https://gist.github.com/vsmart-06/f68961c5515cb50025db1a34f4e2a1a4) · [Website](https://minesweeper-bot.carrd.co)", inline = False)
            help = await mess.channel.send(embed = help_embed)
            await help.add_reaction("◀")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "◀" and p.id != bot.user.id and r.message.id == help.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 1
                await help.delete()

@bot.slash_command(name = "minesweeper", description = "Start an 8x8 minesweeper game with 8 bombs")
async def ms(mess: discord.Interaction, user: discord.Member = discord.SlashOption(name = "opponent", description = "The opponent you wish to play against", required = False)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("minesweeper")
    if user is None:
        author_id = mess.user.id
        if author_id not in in_game:
            await mess.send("Done!", ephemeral = True)
            play = minesweeper(8, 8, 8, author_id, "no", get_theme(author_id))
            game_init = discord.Embed(title=author+"'s minesweeper game", description='''
            You do not have to use ; while playing
            '''
            + play.str_row, color=discord.Color.blue())
            await mess.channel.send(embed=game_init)
            in_game.append(author_id)
            while play.game == 1:
                while True:
                    while True:
                        await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                        try:
                            pos_msg = await bot.wait_for("message", check=lambda m: m.author == mess.user and m.channel == mess.channel, timeout = 30.0)
                        except asyncio.TimeoutError:
                            play.end_msg = "You took too long to respond so the game has ended 😢"
                            message = "quit"
                            play.game = 0
                            break
                        try:
                            message = pos_msg.content
                            r, c = map(int, message.split())
                            if r <= 0 or r > play.num_rows:
                                await mess.channel.send("Row is out of range")
                            elif c <= 0 or c > play.num_cols:
                                await mess.channel.send("Column is out of range")
                            else:
                                break
                        except ValueError:
                            message = str(pos_msg.content).lower()
                            if message == "flag":
                                if play.flag_var == 0:
                                    await mess.channel.send("Flag mode on")
                                    play.flag_var = 1
                                else:
                                    await mess.channel.send("Flag mode off")
                                    play.flag_var = 0
                            elif message == "board":
                                if play.flag_var == 1:
                                    play.flag = "On"
                                else:
                                    play.flag = "Off"

                                game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag+
                                '''
                                '''
                                + play.str_row, color=discord.Color.blue())
                                await mess.channel.send(embed=game_real)
                            elif message == "quit":
                                play.game = 0
                                play.end_msg = "I'm sorry to see you leave 😢"
                                break
                            else:
                                await mess.channel.send("Invalid input")

                    if message == "quit":
                        break

                    try:
                        play.guess(r, c)
                    except UnboundLocalError:
                        await mess.channel.send("That position is already occupied")
                    else:
                        play.moves += 1
                        break
                if message != "quit":
                    if play.flag_var == 1:
                        play.flag = "On"
                    else:
                        play.flag = "Off"

                    game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag +
                    '''
                    '''
                    + play.str_row, color=discord.Color.blue())
                    await mess.channel.send(embed=game_real)
            await mess.channel.send(play.end_msg)
            in_game.remove(author_id)
        else:
            await mess.send("You're already in a game!", ephemeral = True)
    
    else:
        if not(isinstance(mess.channel, discord.DMChannel)):
            opp_id = user.id
            opp_id = int(opp_id)
            a_id = mess.user.id
            me = await bot.fetch_user(a_id)
            opponent = await bot.fetch_user(opp_id)
            server_id = mess.guild.id
            guild = bot.get_guild(server_id)
            if opponent != me and not(opponent.bot):
                if a_id not in in_game and opp_id not in in_game:
                    await mess.send("Done!", ephemeral = True)
                    await mess.channel.send(f"<@!{opp_id}>")
                    want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of minesweeper! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                    want_play = await mess.channel.send(embed = want_play_embed)
                    await want_play.add_reaction("✅")
                    await want_play.add_reaction("❌")
                    in_game.append(a_id)
                    in_game.append(opp_id)
                    try:
                        reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                    except asyncio.TimeoutError:
                        await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                    else:
                        if str(reaction.emoji) == "✅":
                            player_1 = minesweeper(8, 8, 8, a_id, "yes", get_theme(a_id))
                            player_2 = minesweeper(8, 8, 8, opp_id, "yes", get_theme(opp_id))
                            turn = 0
                            while player_1.game == 1 and player_2.game == 1:
                                if turn == 0:
                                    await mess.channel.send(f"<@!{a_id}> it's your turn")
                                    game_init_1 = discord.Embed(title=me.name+"'s minesweeper game", description='''
                                    You do not have to use ; while playing
                                    '''
                                    + player_1.str_row, color=discord.Color.blue())
                                    
                                    await mess.channel.send(embed=game_init_1)
                                    while True:
                                        while True:
                                            await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                                            try:
                                                pos_msg = await bot.wait_for("message", check=lambda m: m.author.id == a_id and m.channel == mess.channel, timeout = 30.0)
                                            except asyncio.TimeoutError:
                                                player_1.end_msg = "You took too long to respond so the game has ended 😢"
                                                message = "quit"
                                                break
                                            try:
                                                message = pos_msg.content
                                                r, c = map(int, message.split())
                                                if r <= 0 or r > player_1.num_rows:
                                                    await mess.channel.send("Row is out of range")
                                                elif c <= 0 or c > player_1.num_cols:
                                                    await mess.channel.send("Column is out of range")
                                                else:
                                                    break
                                            except ValueError:
                                                message = str(pos_msg.content).lower()
                                                if message == "flag":
                                                    if player_1.flag_var == 0:
                                                        await mess.channel.send("Flag mode on")
                                                        player_1.flag_var = 1
                                                    else:
                                                        await mess.channel.send("Flag mode off")
                                                        player_1.flag_var = 0
                                                elif message == "board":
                                                    if player_1.flag_var == 1:
                                                        player_1.flag = "On"
                                                    else:
                                                        player_1.flag = "Off"

                                                    game_real = discord.Embed(title=me.name+"'s minesweeper game", description="Flag mode: "+player_1.flag+
                                                    '''
                                                    '''
                                                    + player_1.str_row, color=discord.Color.blue())
                                                    
                                                    await mess.channel.send(embed=game_real)
                                                elif message == "quit":
                                                    player_1.game = 0
                                                    player_1.end_msg = "I'm sorry to see you leave 😢"
                                                    break
                                                else:
                                                    await mess.channel.send("Invalid input")

                                        if message == "quit":
                                            break

                                        try:
                                            player_1.guess(r, c)
                                            break
                                        except UnboundLocalError:
                                            await mess.channel.send("That position is already occupied")
                                    if message != "quit":
                                        if player_1.flag_var == 1:
                                            player_1.flag = "On"
                                        else:
                                            player_1.flag = "Off"

                                        game_real = discord.Embed(title=me.name+"'s minesweeper game", description="Flag mode: "+player_1.flag +
                                        '''
                                        '''
                                        + player_1.str_row, color=discord.Color.blue())
                                        
                                        await mess.channel.send(embed=game_real)
                                    else:
                                        player_1.game = 0
                                        player_1.game_over = 1
                                    turn = 1

                                else:
                                    await mess.channel.send(f"<@!{opp_id}> it's your turn")
                                    game_init_2 = discord.Embed(title=opponent.name+"'s minesweeper game", description='''
                                    You do not have to use ; while playing
                                    '''
                                    + player_2.str_row, color=discord.Color.blue())
                                    
                                    await mess.channel.send(embed=game_init_2)
                                    while True:
                                        while True:
                                            await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                                            try:
                                                pos_msg = await bot.wait_for("message", check=lambda m: m.author.id == opp_id and m.channel == mess.channel, timeout = 30.0)
                                            except asyncio.TimeoutError:
                                                player_2.end_msg = "You took too long to respond so the game has ended 😢"
                                                message = "quit"
                                                break
                                            try:
                                                message = pos_msg.content
                                                r, c = map(int, message.split())
                                                if r <= 0 or r > player_2.num_rows:
                                                    await mess.channel.send("Row is out of range")
                                                elif c <= 0 or c > player_2.num_cols:
                                                    await mess.channel.send("Column is out of range")
                                                else:
                                                    break
                                            except ValueError:
                                                message = str(pos_msg.content).lower()
                                                if message == "flag":
                                                    if player_2.flag_var == 0:
                                                        await mess.channel.send("Flag mode on")
                                                        player_2.flag_var = 1
                                                    else:
                                                        await mess.channel.send("Flag mode off")
                                                        player_2.flag_var = 0
                                                elif message == "board":
                                                    if player_2.flag_var == 1:
                                                        player_2.flag = "On"
                                                    else:
                                                        player_2.flag = "Off"

                                                    game_real = discord.Embed(title=opponent.name+"'s minesweeper game", description="Flag mode: "+player_2.flag+
                                                    '''
                                                    '''
                                                    + player_2.str_row, color=discord.Color.blue())
                                                    
                                                    await mess.channel.send(embed=game_real)
                                                elif message == "quit":
                                                    player_2.game = 0
                                                    player_2.end_msg = "I'm sorry to see you leave 😢"
                                                    break
                                                else:
                                                    await mess.channel.send("Invalid input")

                                        if message == "quit":
                                            break

                                        try:
                                            player_2.guess(r, c)
                                            break
                                        except UnboundLocalError:
                                            await mess.channel.send("That position is already occupied")
                                    if message != "quit":
                                        if player_2.flag_var == 1:
                                            player_2.flag = "On"
                                        else:
                                            player_2.flag = "Off"

                                        game_real = discord.Embed(title=opponent.name+"'s minesweeper game", description="Flag mode: "+player_2.flag +
                                        '''
                                        '''
                                        + player_2.str_row, color=discord.Color.blue())
                                        
                                        await mess.channel.send(embed=game_real)
                                    else:
                                        player_2.game = 0
                                        player_2.game_over = 1
                                    turn = 0

                            if player_1.game_over == 1:
                                await mess.channel.send(player_1.end_msg)
                                await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                                
                                
                            elif player_2.game_over == 1:
                                await mess.channel.send(player_2.end_msg)
                                await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                                
                                
                            elif player_1.game_won == 1:
                                await mess.channel.send(player_1.end_msg)
                                await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                                
                                
                            elif player_2.game_won == 1:
                                await mess.channel.send(player_2.end_msg)
                                await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                                
                        else:
                            await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                    in_game.remove(a_id)
                    in_game.remove(opp_id)
                else:
                    if a_id in in_game:
                        await mess.send("You're already in a game!", ephemeral = True)
                    else:
                        await mess.send("Your opponent is already in a game!", ephemeral = True)
        else:
            await mess.send("You can't play a match against someone in a DM!", ephemeral = True)

@bot.slash_command(name = "minesweeper-custom", description = "Start a custom minesweeper game")
async def mscustom(mess: discord.Interaction, rows: int = discord.SlashOption(name = "rows", description = "The number of rows for your grid", required = True), columns: int = discord.SlashOption(name = "columns", description = "The number of columns for your grid", required = True), bombs: int = discord.SlashOption(name = "bombs", description = "The number of bombs for your grid", required = True)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("minesweeper_custom")
    author_id = mess.user.id
    if author_id not in in_game:
        if rows <= 1:
            await mess.send("You have too less rows", ephemeral = True)
            return
        elif columns <= 1:
            await mess.send("You have too less columns", ephemeral = True)
            return
        elif columns + len(str(rows)) + 1 > 27:
            await mess.send("You have too many columns", ephemeral = True)
            return
        elif bombs >= (rows*columns):
            await mess.send("You have too many bombs", ephemeral = True)
            return
        elif bombs <= 0:
            await mess.send("You have too less bombs", ephemeral = True)
            return

        num_rows = rows
        num_cols = columns
        num_bombs = bombs

        play = minesweeper(num_rows, num_cols, num_bombs, author_id, "no", get_theme(author_id))
        if play.items_tot+((((len(str(num_rows))+1)*num_rows))+((len(str(num_cols))+1)*num_cols)+((len(str(num_rows))+1)*(len(str(num_cols))+1))) > 198:
            await mess.send("Your grid is too big (you can have only a max of 198 objects (row and column numbers included))", ephemeral = True)
            return
        await mess.send("Done!", ephemeral = True)
        game_init = discord.Embed(title=author+"'s minesweeper game", description='''
        You do not have to use ; while playing
        '''
        + play.str_row, color=discord.Color.blue())
        await mess.channel.send(embed=game_init)
        in_game.append(author_id)
        while play.game == 1:
            while True:
                while True:
                    await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                    try:
                        pos_msg = await bot.wait_for("message", check=lambda m: m.author == mess.user and m.channel == mess.channel, timeout = 30.0)
                    except asyncio.TimeoutError:
                        play.end_msg = "You took too long to respond so the game has ended 😢"
                        message = "quit"
                        play.game = 0
                        break
                    try:
                        message = pos_msg.content
                        r, c = map(int, message.split())
                        if r <= 0 or r > play.num_rows:
                            await mess.channel.send("Row is out of range")
                        elif c <= 0 or c > play.num_cols:
                            await mess.channel.send("Column is out of range")
                        else:
                            break
                    except ValueError:
                        message = str(pos_msg.content).lower()
                        if message == "flag":
                            if play.flag_var == 0:
                                await mess.channel.send("Flag mode on")
                                play.flag_var = 1
                            else:
                                await mess.channel.send("Flag mode off")
                                play.flag_var = 0
                        elif message == "board":
                            if play.flag_var == 1:
                                play.flag = "On"
                            else:
                                play.flag = "Off"

                            game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag+
                            '''
                            '''
                            + play.str_row, color=discord.Color.blue())
                            await mess.channel.send(embed=game_real)
                        elif message == "quit":
                            play.game = 0
                            play.end_msg = "I'm sorry to see you leave 😢"
                            break
                        else:
                            await mess.channel.send("Invalid input")

                if message == "quit":
                    break

                try:
                    play.guess(r, c)
                    break
                except UnboundLocalError:
                    await mess.channel.send("That position is already occupied")
            if message != "quit":
                if play.flag_var == 1:
                    play.flag = "On"
                else:
                    play.flag = "Off"

                game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag +
                '''
                '''
                + play.str_row, color=discord.Color.blue())
                await mess.channel.send(embed=game_real)
        await mess.channel.send(play.end_msg)
        in_game.remove(author_id)
    else:
        await mess.send("You're already in a game!", ephemeral = True)

@bot.slash_command(name = "tournament", description = "Starts a minesweeper tournament")
async def tournament(mess: discord.Interaction):
    global in_game, tourney_channels
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("tournament")
    if not(isinstance(mess.channel, discord.DMChannel)):
        host_id = mess.user.id
        if host_id not in in_game and mess.channel.id not in tourney_channels:
            await mess.send("Done!", ephemeral = True)
            tourney_channels.append(mess.channel.id)
            thumb = bot.get_emoji(935120796358152212)
            check = bot.get_emoji(935455988516028486)
            winner = bot.get_emoji(935794255543275541)
            yay = bot.get_emoji(951716865049247855)
            tourney_members = [host_id]
            tourney_init_embed = discord.Embed(title = "Tournament started!", description = f"<@!{host_id}> started a tournament! React with {thumb} below or type `;join` to join! Remove your reaction or type `;leave` to leave. <@!{host_id}> react with {check} or type `;start` to start the tournament!", colour = discord.Colour.blue())
            tourney_init = await mess.channel.send(embed = tourney_init_embed)
            await tourney_init.add_reaction(str(thumb))
            await tourney_init.add_reaction(str(check))
            in_game.append(host_id)
            while True:
                decisions = [asyncio.create_task(bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) in [str(thumb), str(check)] and p != bot.user and r.message.id == tourney_init.id, timeout = 60.0), name = "radd"), asyncio.create_task(bot.wait_for("reaction_remove", check = lambda r, p: str(r.emoji) == str(thumb) and p != bot.user and r.message.id == tourney_init.id, timeout = 60.0), name = "rrem"), asyncio.create_task(bot.wait_for("message", check = lambda m: m.channel == mess.channel, timeout = 60.0), name = "msgd")]

                completed, pending = await asyncio.wait(decisions, return_when = asyncio.FIRST_COMPLETED)
                
                finished_task: asyncio.Task = list(completed)[0]
                
                for unfinished in pending:
                    try:
                        unfinished.cancel()
                    except asyncio.CancelledError:
                        pass

                action = finished_task.get_name()
                try:
                    result = finished_task.result()
                except asyncio.TimeoutError:
                    break

                else:
                    if action == "radd":
                        reaction, user = result
                        reaction_e = str(reaction.emoji)
                        if reaction_e == str(thumb) and user.id != host_id and user.id not in tourney_members:
                            if user.id not in in_game:
                                await mess.channel.send(f"<@!{user.id}> has joined the tournament {yay}")
                                tourney_members.append(user.id)
                                in_game.append(user.id)
                            else:
                                await mess.channel.send(f"<@!{user.id}>, you're already in a game!")
                        elif reaction_e == str(check) and user.id == host_id:
                            break
                    elif action == "rrem":
                        reaction, user = result
                        reaction_e = str(reaction.emoji)
                        if reaction_e == str(thumb) and user.id != host_id and user.id in tourney_members:
                            await mess.channel.send(f"<@!{user.id}> has left the tournament 😢")
                            tourney_members.remove(user.id)
                            in_game.remove(user.id)
                    elif action == "msgd":
                        jl_msg = str(result.content)
                        user = result.author
                        if jl_msg == ";join" and user.id not in tourney_members and user.id != host_id:
                            if user.id not in in_game:
                                await mess.channel.send(f"<@!{user.id}> has joined the tournament {yay}")
                                tourney_members.append(user.id)
                                in_game.append(user.id)
                            else:
                                await mess.channel.send(f"<@!{user.id}>, you're already in a game!")
                        elif jl_msg == ";leave" and user.id in tourney_members and user.id != host_id:
                            await mess.channel.send(f"<@!{user.id}> has left the tournament 😢")
                            tourney_members.remove(user.id)
                            in_game.remove(user.id)
                        elif jl_msg == ";start" and user.id == host_id:
                            break
            tourney_members = list(set(tourney_members))
            mem_str = "Tournament participants:"
            for mem in tourney_members:
                mem_str += f'''
<@!{mem}>'''
            await mess.channel.send(mem_str)
            round = 1
            match = 1
            while len(tourney_members) > 1:
                pairings = []
                tourney_members_temp = list(tourney_members)
                while tourney_members_temp != []:
                    p1 = rd.choice(tourney_members_temp)
                    tourney_members_temp.remove(p1)
                    if tourney_members_temp != []:
                        p2 = rd.choice(tourney_members_temp)
                        tourney_members_temp.remove(p2)
                    else:
                        p2 = "Bye"
                    pairings.append((p1, p2))
                pairings_list_str = ""
                for pai in pairings:
                    if pai[1] != "Bye":
                        pairings_list_str += f'''<@!{pai[0]}> --------------------- <@!{pai[1]}>
'''
                    else:
                        pairings_list_str += f'''<@!{pai[0]}> --------------------- Bye
'''
                pairings_list = discord.Embed(title = f"Round {round} pairings", description = pairings_list_str, colour = discord.Colour.blue())
                await mess.channel.send(embed = pairings_list)
                for mat in range(len(pairings)):
                    if pairings[match-1][1] != "Bye":
                        match_init_embed = discord.Embed(title = f"Match {match}", description = f"<@!{pairings[match-1][0]}> VS <@!{pairings[match-1][1]}>", colour = discord.Color.blue())
                        await mess.channel.send(embed = match_init_embed)
                        me = await bot.fetch_user(pairings[match-1][0])
                        opponent = await bot.fetch_user(pairings[match-1][1])
                        a_id = me.id
                        opp_id = opponent.id
                        standby = await mess.channel.send(f"<@!{a_id}> and <@!{opp_id}> on standby! React with {thumb} to get ready!")
                        await standby.add_reaction(str(thumb))
                        p1_ready = False
                        p2_ready = False
                        pairing_temp = list(pairings[match-1])
                        while not (p1_ready and p2_ready):
                            try:
                                reaction, user = await bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) == str(thumb) and p.id in pairing_temp and r.message.id == standby.id, timeout = 60.0)
                            except asyncio.TimeoutError:
                                break
                            else:
                                if user.id == pairings[match-1][0]:
                                    p1_ready = True
                                    await mess.channel.send(f"<@!{pairings[match-1][0]}> is ready!")
                                    pairing_temp.remove(pairings[match-1][0])
                                elif user.id == pairings[match-1][1]:
                                    p2_ready = True
                                    await mess.channel.send(f"<@!{pairings[match-1][1]}> is ready!")
                                    pairing_temp.remove(pairings[match-1][1])
                        player_1 = minesweeper(8, 8, 8, a_id, "yes", get_theme(a_id))
                        player_2 = minesweeper(8, 8, 8, opp_id, "yes", get_theme(opp_id))
                        turn = 0
                        while player_1.game == 1 and player_2.game == 1:
                            if turn == 0:
                                await mess.channel.send(f"<@!{a_id}> it's your turn")
                                game_init_1 = discord.Embed(title=me.name+"'s minesweeper game", description='''
                                You do not have to use ; while playing
                                '''
                                + player_1.str_row, color=discord.Color.blue())
                                
                                await mess.channel.send(embed=game_init_1)
                                while True:
                                    while True:
                                        await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                                        try:
                                            pos_msg = await bot.wait_for("message", check=lambda m: m.author.id == a_id and m.channel == mess.channel, timeout = 60.0)
                                        except asyncio.TimeoutError:
                                            player_1.end_msg = "You took too long to respond so the game has ended 😢"
                                            message = "quit"
                                            break
                                        try:
                                            message = pos_msg.content
                                            r, c = map(int, message.split())
                                            if r <= 0 or r > player_1.num_rows:
                                                await mess.channel.send("Row is out of range")
                                            elif c <= 0 or c > player_1.num_cols:
                                                await mess.channel.send("Column is out of range")
                                            else:
                                                break
                                        except ValueError:
                                            message = str(pos_msg.content).lower()
                                            if message == "flag":
                                                if player_1.flag_var == 0:
                                                    await mess.channel.send("Flag mode on")
                                                    player_1.flag_var = 1
                                                else:
                                                    await mess.channel.send("Flag mode off")
                                                    player_1.flag_var = 0
                                            elif message == "board":
                                                if player_1.flag_var == 1:
                                                    player_1.flag = "On"
                                                else:
                                                    player_1.flag = "Off"

                                                game_real = discord.Embed(title=me.name+"'s minesweeper game", description="Flag mode: "+player_1.flag+
                                                '''
                                                '''
                                                + player_1.str_row, color=discord.Color.blue())
                                                
                                                await mess.channel.send(embed=game_real)
                                            elif message == "quit":
                                                player_1.game = 0
                                                player_1.end_msg = "I'm sorry to see you leave 😢"
                                                break
                                            else:
                                                await mess.channel.send("Invalid input")

                                    if message == "quit":
                                        break

                                    try:
                                        player_1.guess(r, c)
                                        break
                                    except UnboundLocalError:
                                        await mess.channel.send("That position is already occupied")
                                if message != "quit":
                                    if player_1.flag_var == 1:
                                        player_1.flag = "On"
                                    else:
                                        player_1.flag = "Off"

                                    game_real = discord.Embed(title=me.name+"'s minesweeper game", description="Flag mode: "+player_1.flag +
                                    '''
                                    '''
                                    + player_1.str_row, color=discord.Color.blue())
                                    
                                    await mess.channel.send(embed=game_real)
                                else:
                                    player_1.game = 0
                                    player_1.game_over = 1
                                turn = 1

                            else:
                                await mess.channel.send(f"<@!{opp_id}> it's your turn")
                                game_init_2 = discord.Embed(title=opponent.name+"'s minesweeper game", description='''
                                You do not have to use ; while playing
                                '''
                                + player_2.str_row, color=discord.Color.blue())
                                
                                await mess.channel.send(embed=game_init_2)
                                while True:
                                    while True:
                                        await mess.channel.send("Enter the row and column (ex: '3 4') (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                                        try:
                                            pos_msg = await bot.wait_for("message", check=lambda m: m.author.id == opp_id and m.channel == mess.channel, timeout = 60.0)
                                        except asyncio.TimeoutError:
                                            player_2.end_msg = "You took too long to respond so the game has ended 😢"
                                            message = "quit"
                                            break
                                        try:
                                            message = pos_msg.content
                                            r, c = map(int, message.split())
                                            if r <= 0 or r > player_2.num_rows:
                                                await mess.channel.send("Row is out of range")
                                            elif c <= 0 or c > player_2.num_cols:
                                                await mess.channel.send("Column is out of range")
                                            else:
                                                break
                                        except ValueError:
                                            message = str(pos_msg.content).lower()
                                            if message == "flag":
                                                if player_2.flag_var == 0:
                                                    await mess.channel.send("Flag mode on")
                                                    player_2.flag_var = 1
                                                else:
                                                    await mess.channel.send("Flag mode off")
                                                    player_2.flag_var = 0
                                            elif message == "board":
                                                if player_2.flag_var == 1:
                                                    player_2.flag = "On"
                                                else:
                                                    player_2.flag = "Off"

                                                game_real = discord.Embed(title=opponent.name+"'s minesweeper game", description="Flag mode: "+player_2.flag+
                                                '''
                                                '''
                                                + player_2.str_row, color=discord.Color.blue())
                                                
                                                await mess.channel.send(embed=game_real)
                                            elif message == "quit":
                                                player_2.game = 0
                                                player_2.end_msg = "I'm sorry to see you leave 😢"
                                                break
                                            else:
                                                await mess.channel.send("Invalid input")

                                    if message == "quit":
                                        break

                                    try:
                                        player_2.guess(r, c)
                                        break
                                    except UnboundLocalError:
                                        await mess.channel.send("That position is already occupied")
                                if message != "quit":
                                    if player_2.flag_var == 1:
                                        player_2.flag = "On"
                                    else:
                                        player_2.flag = "Off"

                                    game_real = discord.Embed(title=opponent.name+"'s minesweeper game", description="Flag mode: "+player_2.flag +
                                    '''
                                    '''
                                    + player_2.str_row, color=discord.Color.blue())
                                    
                                    await mess.channel.send(embed=game_real)
                                else:
                                    player_2.game = 0
                                    player_2.game_over = 1
                                turn = 0

                        if player_1.game_over == 1:
                            await mess.channel.send(player_1.end_msg)
                            tourney_members.remove(a_id)
                            in_game.remove(a_id)
                            await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                        elif player_2.game_over == 1:
                            await mess.channel.send(player_2.end_msg)
                            tourney_members.remove(opp_id)
                            in_game.remove(opp_id)
                            await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                        elif player_1.game_won == 1:
                            await mess.channel.send(player_1.end_msg)
                            tourney_members.remove(opp_id)
                            in_game.remove(opp_id)
                            await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                        elif player_2.game_won == 1:
                            await mess.channel.send(player_2.end_msg)
                            tourney_members.remove(a_id)
                            in_game.remove(a_id)
                            await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                        match += 1
                        await asyncio.sleep(5)
                    
                    else:
                        match = 1
                        await asyncio.sleep(5)
                round += 1
                match = 1
            await mess.channel.send(f"<@!{tourney_members[0]}> is the winner of the tournament! {winner}")
            in_game.remove(tourney_members[0])
            tourney_channels.remove(mess.channel.id)
        else:
            if mess.channel.id not in tourney_channels:
                await mess.send("You're already in a game!", ephemeral = True)
            else:
                await mess.send("There is already a tournament going on in this channel!", ephemeral = True)
        
    else:
        await mess.send("You can't start a tournament in a DM!", ephemeral = True)

@bot.slash_command(name = "leaderboard", description = "View the global leaderboard")
async def lb(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    await mess.send("Done!", ephemeral = True)
    change_stats("leaderboard")
    page = 1
    while True:
        if page == 1:
            leaders = global_leaderboard("best_time")
            leaders_str = ""
            for user in leaders:
                if user[1] != None:
                    time_mins = int(user[1]//60)
                    time_secs = int(user[1]%60)
                    if user == leaders[0]:
                        leaders_str += "🥇"
                    elif user == leaders[1]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        else:
                            leaders_str += "🥈"
                    elif user == leaders[2]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        else:
                            leaders_str += "🥉"
                    else:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        elif user[1] == leaders[2][1]:
                            leaders_str += "🥉"
                        else:
                            leaders_str += "👏"
                    leaders_str += "<@!"+str(user[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                    leaders_str += '''
'''
            global_lb = discord.Embed(title="Fastest times", description = leaders_str, colour=discord.Color.blue())
            global_lb.set_footer(text = "Global leaderboard 1/3")
            try:
                await lb.delete()
            except UnboundLocalError:
                pass
            lb = await mess.channel.send(embed=global_lb)
            await lb.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "▶" and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 2

        elif page == 2:
            leaders = global_leaderboard("avg_time")
            leaders_str = ""
            for user in leaders:
                if user[1] != None:
                    time_mins = int(user[1]//60)
                    time_secs = int(user[1]%60)
                    if user == leaders[0]:
                        leaders_str += "🥇"
                    elif user == leaders[1]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        else:
                            leaders_str += "🥈"
                    elif user == leaders[2]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        else:
                            leaders_str += "🥉"
                    else:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        elif user[1] == leaders[2][1]:
                            leaders_str += "🥉"
                        else:
                            leaders_str += "👏"
                    leaders_str += "<@!"+str(user[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                    leaders_str += '''
'''
            global_lb = discord.Embed(title="Best average times", description = leaders_str, colour=discord.Color.blue())
            global_lb.set_footer(text = "Global leaderboard 2/3")
            await lb.delete()
            lb = await mess.channel.send(embed=global_lb)
            await lb.add_reaction("◀")
            await lb.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                if str(reaction.emoji) == "◀":
                    page = 1
                else:
                    page = 3
        
        elif page == 3:
            leaders = global_leaderboard("max_streak")
            leaders_str = ""
            for user in leaders:
                if user[1] != None:
                    if user == leaders[0]:
                        leaders_str += "🥇"
                    elif user == leaders[1]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        else:
                            leaders_str += "🥈"
                    elif user == leaders[2]:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        else:
                            leaders_str += "🥉"
                    else:
                        if user[1] == leaders[0][1]:
                            leaders_str += "🥇"
                        elif user[1] == leaders[1][1]:
                            leaders_str += "🥈"
                        elif user[1] == leaders[2][1]:
                            leaders_str += "🥉"
                        else:
                            leaders_str += "👏"
                    leaders_str += "<@!"+str(user[0])+"> : "+str(user[1])
                    leaders_str += '''
'''
            global_lb = discord.Embed(title="Highest streaks", description = leaders_str, colour=discord.Color.blue())
            global_lb.set_footer(text = "Global leaderboard 3/3")
            await lb.delete()
            lb = await mess.channel.send(embed=global_lb)
            await lb.add_reaction("◀")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "◀" and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 2

@bot.slash_command(name = "server-leaderboard", description = "View the server leaderboard")
async def serverlb(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("server_leaderboard")
    if not(isinstance(mess.channel, discord.DMChannel)):
        await mess.send("Done!", ephemeral = True)
        server_id = mess.guild.id
        guild = bot.get_guild(server_id)
        members = []
        for m in guild.members:
            members.append(m.id)
        page = 1
        while True:
            if page == 1:
                server_leaders = server_leaderboard(members, "best_time")
                sleaders_str = ""
                for member in server_leaders:
                    if member[1] != None:
                        time_mins = int(member[1]//60)
                        time_secs = int(member[1]%60)
                        if member == server_leaders[0]:
                            sleaders_str += "🥇"
                        elif member == server_leaders[1]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            else:
                                sleaders_str += "🥈"
                        elif member == server_leaders[2]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            else:
                                sleaders_str += "🥉"
                        else:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            elif member[1] == server_leaders[2][1]:
                                sleaders_str += "🥉"
                            else:
                                sleaders_str += "👏"
                        sleaders_str += "<@!"+str(member[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                        sleaders_str += '''
'''
                server_lb = discord.Embed(title="Fastest times in the server", description = sleaders_str, colour=discord.Color.blue())
                server_lb.set_footer(text = "Server leaderboard 1/3")
                try:
                    await lb.delete()
                except UnboundLocalError:
                    pass
                lb = await mess.channel.send(embed=server_lb)
                await lb.add_reaction("▶")
                try:
                    reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "▶" and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
                except asyncio.TimeoutError:
                    break
                else:
                    page = 2

            elif page == 2:
                server_leaders = server_leaderboard(members, "avg_time")
                sleaders_str = ""
                for member in server_leaders:
                    if member[1] != None:
                        time_mins = int(member[1]//60)
                        time_secs = int(member[1]%60)
                        if member == server_leaders[0]:
                            sleaders_str += "🥇"
                        elif member == server_leaders[1]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            else:
                                sleaders_str += "🥈"
                        elif member == server_leaders[2]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            else:
                                sleaders_str += "🥉"
                        else:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            elif member[1] == server_leaders[2][1]:
                                sleaders_str += "🥉"
                            else:
                                sleaders_str += "👏"
                        sleaders_str += "<@!"+str(member[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                        sleaders_str += '''
'''
                server_lb = discord.Embed(title="Best average times in the server", description = sleaders_str, colour=discord.Color.blue())
                server_lb.set_footer(text = "Server leaderboard 2/3")
                await lb.delete()
                lb = await mess.channel.send(embed=server_lb)
                await lb.add_reaction("◀")
                await lb.add_reaction("▶")
                try:
                    reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
                except asyncio.TimeoutError:
                    break
                else:
                    if str(reaction.emoji) == "◀":
                        page = 1
                    else:
                        page = 3
            
            elif page == 3:
                server_leaders = server_leaderboard(members, "max_streak")
                sleaders_str = ""
                for member in server_leaders:
                    if member[1] != None:
                        if member == server_leaders[0]:
                            sleaders_str += "🥇"
                        elif member == server_leaders[1]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            else:
                                sleaders_str += "🥈"
                        elif member == server_leaders[2]:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            else:
                                sleaders_str += "🥉"
                        else:
                            if member[1] == server_leaders[0][1]:
                                sleaders_str += "🥇"
                            elif member[1] == server_leaders[1][1]:
                                sleaders_str += "🥈"
                            elif member[1] == server_leaders[2][1]:
                                sleaders_str += "🥉"
                            else:
                                sleaders_str += "👏"
                        sleaders_str += "<@!"+str(member[0])+"> : "+str(member[1])
                        sleaders_str += '''
'''
                server_lb = discord.Embed(title="Highest streaks in the server", description = sleaders_str, colour=discord.Color.blue())
                server_lb.set_footer(text = "Server leaderboard 3/3")
                await lb.delete()
                lb = await mess.channel.send(embed=server_lb)
                await lb.add_reaction("◀")
                try:
                    reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "◀" and p.id != bot.user.id and r.message.id == lb.id, timeout = 30.0)
                except asyncio.TimeoutError:
                    break
                else:
                    page = 2
  
    else:
        await mess.send("This is not a server!", ephemeral = True)

@bot.slash_command(name = "profile", description = "View anyone's profile")
async def profile(mess: discord.Interaction, user: discord.Member = discord.SlashOption(name = "user", description = "The user who's profile you would like to view", required = False)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    prof_author = mess.user.id
    change_stats("user_profile")
    if user is None:
        user_id = mess.user.id
        prof = uprofile(int(user_id))
        u = await bot.fetch_user(user_id)
        user_handle = str(u)
        user_name = u.name
        try:
            if prof[1] != None:
                time_mins = int(prof[1]//60)
                time_secs = int(prof[1]%60)
                avg_mins = int(prof[7]//60)
                avg_secs = int(prof[7]%60)
            if prof[9] == "yes":
                initialsupporter = bot.get_emoji(932908272971841536)
                p_title = user_name+"'s profile "+str(initialsupporter)
            else:
                p_title = user_name+"'s profile"
            if prof[4] >= 100:
                hun_club = bot.get_emoji(946733351195254814)
                p_title += " "+str(hun_club)
            user_profile = discord.Embed(title = p_title, description = "All stats about this user on the minesweeper bot!", color = discord.Color.blue())
            user_profile.set_thumbnail(url = u.display_avatar)
            user_profile.add_field(name = "Discord handle:", value = "||"+user_handle+"||", inline = True)
            if prof[1] != None:
                user_profile.add_field(name = "Best time:", value = str(time_mins)+"m "+str(time_secs)+"s", inline = True)
                user_profile.add_field(name = "Average winning time:", value = str(avg_mins)+"m "+str(avg_secs)+"s", inline = True)
            else:
                user_profile.add_field(name = "Best time:", value = prof[1], inline = True)
                user_profile.add_field(name = "Average winning time:", value = prof[7], inline = True)
            user_profile.add_field(name = "Games won:", value = prof[2], inline = True)
            user_profile.add_field(name = "Games lost:", value = prof[3], inline = True)
            user_profile.add_field(name = "Total games played:", value = prof[4], inline = True)
            user_profile.add_field(name = "Win percentage:", value = prof[5], inline = True)
            user_profile.add_field(name = "Current win streak:", value = prof[10], inline = True)
            user_profile.add_field(name = "Maximum win streak:", value = prof[11], inline = True)
            user_profile.add_field(name = "Minimum moves:", value = prof[12], inline = True)
            user_profile.add_field(name = "Average moves:", value = prof[14], inline = True)
            user_profile.add_field(name = "Profile type:", value = prof[8].capitalize(), inline = True)
        except TypeError:
            user_profile = discord.Embed(title = "User not detected!", description = "This user hasn't used the bot yet!", color = discord.Color.blue())
    else:
        user_id = user.id
        prof = uprofile(int(user_id))
        u = await bot.fetch_user(user_id)
        user_handle = str(u)
        user_name = u.name
        try:
            if prof[8] == "public" or prof_author == int(user_id):
                if prof[1] != None:
                    time_mins = int(prof[1]//60)
                    time_secs = int(prof[1]%60)
                    avg_mins = int(prof[7]//60)
                    avg_secs = int(prof[7]%60)
                if prof[9] == "yes":
                    initialsupporter = bot.get_emoji(932908272971841536)
                    p_title = user_name+"'s profile "+str(initialsupporter)
                else:
                    p_title = user_name+"'s profile"
                if prof[4] >= 100:
                    hun_club = bot.get_emoji(946733351195254814)
                    p_title += " "+str(hun_club)
                user_profile = discord.Embed(title = p_title, description = "All stats about this user on the minesweeper bot!", color = discord.Color.blue())
                user_profile.set_thumbnail(url = u.display_avatar)
                user_profile.add_field(name = "Discord handle:", value = "||"+user_handle+"||", inline = True)
                if prof[1] != None:
                    user_profile.add_field(name = "Best time:", value = str(time_mins)+"m "+str(time_secs)+"s", inline = True)
                    user_profile.add_field(name = "Average winning time:", value = str(avg_mins)+"m "+str(avg_secs)+"s", inline = True)
                else:
                    user_profile.add_field(name = "Best time:", value = prof[1], inline = True)
                    user_profile.add_field(name = "Average winning time:", value = prof[7], inline = True)
                user_profile.add_field(name = "Games won:", value = prof[2], inline = True)
                user_profile.add_field(name = "Games lost:", value = prof[3], inline = True)
                user_profile.add_field(name = "Total games played:", value = prof[4], inline = True)
                user_profile.add_field(name = "Win percentage:", value = prof[5], inline = True)
                user_profile.add_field(name = "Current win streak:", value = prof[10], inline = True)
                user_profile.add_field(name = "Maximum win streak:", value = prof[11], inline = True)
                user_profile.add_field(name = "Minimum moves:", value = prof[12], inline = True)
                user_profile.add_field(name = "Average moves:", value = prof[14], inline = True)
                user_profile.add_field(name = "Profile type:", value = prof[8].capitalize(), inline = True)
            else:
                user_profile = discord.Embed(title = "Private profile!", description = "This profile is private so you cannot view it!", color = discord.Color.blue())
        except TypeError:
            user_profile = discord.Embed(title = "User not detected!", description = "This user hasn't used the bot yet!", color = discord.Color.blue())
    await mess.send(embed=user_profile)

@bot.slash_command(name = "profile-settings", description = "Change your profile settings")
async def settings(mess: discord.Interaction, privacy: str = discord.SlashOption(name = "privacy", description = "Your privacy option", choices = ["public", "private"], required = True)):
    user_id = mess.user.id
    change_stats("profile_settings")
    privacy_change(user_id, privacy)
    profile_privacy = discord.Embed(title = "Profile settings changed!", description = f"Your profile is now {privacy}!", color = discord.Color.blue())
    await mess.send(embed = profile_privacy)

@bot.slash_command(name = "delete", description = "Delete your stats on the bot")
async def delete(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    await mess.send("Done!", ephemeral = True)
    change_stats("delete_stats")
    aut_id = mess.user.id
    delete_data = await mess.channel.send("Are you sure you want to delete all of your data on this bot? React to confirm!")
    await delete_data.add_reaction("✅")
    await delete_data.add_reaction("❌")
    try:
        reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["✅", "❌"] and p.id == aut_id and r.message.id == delete_data.id, timeout = 30.0)
    except asyncio.TimeoutError:
        record_d = discord.Embed(title = "Operation cancelled!", description = "You took too long to respond so the data deletion has been cancelled!", colour = discord.Colour.blue())
        await mess.channel.send(embed = record_d)
        
        
    else:
        if str(reaction.emoji) == "✅":
            delete_record(aut_id)
            record_d = discord.Embed(title = "Data deleted", description = "All of your stats with the bot have been deleted. Play again to create new stats.", colour = discord.Colour.blue())
        else:
            record_d = discord.Embed(title = "Operation cancelled!", description = "Data deletion has been cancelled!", colour = discord.Colour.blue())
        await mess.channel.send(embed = record_d)

@bot.slash_command(name = "theme-settings", description = "Change your game theme")
async def theme(mess: discord.Interaction, theme: str = discord.SlashOption(name = "theme", description = "Your preferred theme", choices = ["light", "dark"], required = True)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("theme")
    aut_id = mess.user.id
    theme_change(aut_id, theme)
    theme_settings = discord.Embed(title = "Theme changed successfully!", description = f"Your game theme has been successfully changed to {theme} mode!", color = discord.Color.blue())
    await mess.send(embed = theme_settings)

@bot.slash_command(name = "connect4", description = "Start a game of connect 4")
async def c4(mess: discord.Interaction, user: discord.Member = discord.SlashOption(name = "opponent", description = "The opponent you wish to play against", required = True)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("connect_four")
    if not(isinstance(mess.channel, discord.DMChannel)):
        opp_id = user.id
        a_id = mess.user.id
        me = await bot.fetch_user(a_id)
        opponent = await bot.fetch_user(opp_id)
        server_id = mess.guild.id
        guild = bot.get_guild(server_id)
        if opponent != me and not(opponent.bot):
            if a_id not in in_game and opp_id not in in_game:
                await mess.send("Done!", ephemeral = True)
                await mess.channel.send(f"<@!{opp_id}>")
                want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of connect 4! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                want_play = await mess.channel.send(embed = want_play_embed)
                await want_play.add_reaction("✅")
                await want_play.add_reaction("❌")
                in_game.append(a_id)
                in_game.append(opp_id)
                try:
                    reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                except asyncio.TimeoutError:
                    await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                else:
                    if str(reaction.emoji) == "✅":
                        game = connect4(a_id, opp_id, get_theme(a_id), get_theme(opp_id))
                        while game.game_end == 0:
                            if game.turn == 0:
                                await mess.channel.send(f"<@!{a_id}> it's your turn")
                                game.string_rows()
                                c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                
                                await mess.channel.send(embed = c4_embed)
                                while True:
                                    await mess.channel.send("Choose the column (1-7) in which you want to drop your coin! (Type 'board' to see your current game; type 'quit' to end the game)")
                                    try:
                                        pos_msg = await bot.wait_for("message", check = lambda m: m.author.id == a_id and m.channel == mess.channel, timeout = 120.0)
                                    except asyncio.TimeoutError:
                                        await mess.channel.send("You took too long to respond so the game has ended 😢")
                                        game.game_end = 1
                                        game.winner = opp_id
                                        await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                        break
                                    pos = pos_msg.content
                                    try:
                                        pos = int(pos)
                                        if not(1 <= pos <= 7):
                                            await mess.channel.send("Column is out of range")
                                        else:
                                            game.columns[game.columns[pos-1].index("")]
                                            break
                                    except ValueError:
                                        try:
                                            pos = int(pos)
                                            await mess.channel.send("Column is full")
                                        except ValueError:
                                            pos = str(pos).lower()
                                            if pos == "quit":
                                                game.game_end = 1
                                                game.winner = opp_id
                                                await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                break
                                            elif pos == "board":
                                                c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                                
                                                await mess.channel.send(embed = c4_embed)
                                            else:
                                                await mess.channel.send("Column number can only be an integer from 1 to 7")
                                if game.game_end == 0:
                                    game.columns[pos-1][game.columns[pos-1].index("")] = "Red"
                                    game.string_rows()
                                    c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                    await mess.channel.send(embed = c4_embed)
                                    game.turn = 1
                                    game.left_pos -= 1
                            else:
                                await mess.channel.send(f"<@!{opp_id}> it's your turn")
                                game.string_rows()
                                c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                await mess.channel.send(embed = c4_embed)
                                while True:
                                    await mess.channel.send("Choose the column (1-7) in which you want to drop your coin! (Type 'board' to see your current game; type 'quit' to end the game)")
                                    try:
                                        pos_msg = await bot.wait_for("message", check = lambda m: m.author.id == opp_id and m.channel == mess.channel, timeout = 120.0)
                                    except asyncio.TimeoutError:
                                        await mess.channel.send("You took too long to respond so the game has ended 😢")
                                        game.game_end = 1
                                        game.winner = a_id
                                        await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                        break
                                    pos = pos_msg.content
                                    try:
                                        pos = int(pos)
                                        if not(1 <= pos <= 7):
                                            await mess.channel.send("Column is out of range")
                                        else:
                                            game.columns[game.columns[pos-1].index("")]
                                            break
                                    except ValueError:
                                        try:
                                            pos = int(pos)
                                            await mess.channel.send("Column is full")
                                        except ValueError:
                                            pos = str(pos).lower()
                                            if pos == "quit":
                                                game.game_end = 1
                                                game.winner = a_id
                                                await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                break
                                            elif pos == "board":
                                                c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                                
                                                await mess.channel.send(embed = c4_embed)
                                            else:
                                                await mess.channel.send("Column number can only be an integer from 1 to 7")
                                if game.game_end == 0:
                                    game.columns[pos-1][game.columns[pos-1].index("")] = "Yellow"
                                    game.string_rows()
                                    c4_embed = discord.Embed(title = "Connect 4!", description = game.string_items, colour = discord.Colour.blue())
                                    await mess.channel.send(embed = c4_embed)
                                    game.turn = 0
                                    game.left_pos -= 1
                            if game.game_end == 0:
                                game.game_over()
                                if game.game_end == 1:
                                    await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                elif game.left_pos == 0:
                                    await mess.channel.send("It's a tie ¯\_(ツ)_/¯")
                                    game.game_end = 1
                        
                    else:
                        await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                in_game.remove(a_id)
                in_game.remove(opp_id)
            else:
                if a_id in in_game:
                    await mess.send("You're already in a game!", ephemeral = True)
                else:
                    await mess.send("Your opponent is already in a game!", ephemeral = True)      
    else:
        await mess.send("You can't play a match against someone in a DM!", ephemeral = True)

@bot.slash_command(name = "othello", description = "Start a game of othello")
async def oto(mess: discord.Interaction, user: discord.Member = discord.SlashOption(name = "opponent", description = "The opponent you wish to play against", required = True)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("othello")
    if not(isinstance(mess.channel, discord.DMChannel)):
        opp_id = user.id
        a_id = mess.user.id
        me = await bot.fetch_user(a_id)
        opponent = await bot.fetch_user(opp_id)
        server_id = mess.guild.id
        guild = bot.get_guild(server_id)
        if opponent != me and not(opponent.bot):
            if a_id not in in_game and opp_id not in in_game:
                await mess.send("Done!", ephemeral = True)
                await mess.channel.send(f"<@!{opp_id}>")
                want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of othello! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                want_play = await mess.channel.send(embed = want_play_embed)
                await want_play.add_reaction("✅")
                await want_play.add_reaction("❌")
                in_game.append(a_id)
                in_game.append(opp_id)
                try:
                    reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                except asyncio.TimeoutError:
                    await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                else:
                    if str(reaction.emoji) == "✅":
                        game = othello(a_id, opp_id, get_theme(a_id), get_theme(opp_id))
                        while (game.any_valid("black") or game.any_valid("white")) and game.game_end == 0:
                            if game.turn == 0:
                                if game.any_valid("black"):
                                    await mess.channel.send(f"<@!{a_id}> it's your turn")
                                    game.string_rows()
                                    board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                    await mess.channel.send(embed = board)
                                    while True:
                                        await mess.channel.send("Enter the row and column where you would like to place your coin (ex: '3 4') (Type 'board' to see your current game; type 'quit' to end the game)")
                                        try:
                                            rc_msg = await bot.wait_for("message", check = lambda m: m.author.id == a_id and m.channel == mess.channel, timeout = 120.0)
                                        except asyncio.TimeoutError:
                                            await mess.channel.send("You took too long to respond so the game has ended 😢")
                                            game.game_end = 1
                                            game.winner = opp_id
                                            await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                            break
                                        message = rc_msg.content
                                        try:
                                            r, c = map(int, message.split())
                                            if r <= 0 or r > 8:
                                                await mess.channel.send("Row is out of range")
                                            elif c <= 0 or c > 8:
                                                await mess.channel.send("Column is out of range")
                                            else:
                                                if game.items[r-1][c-1] != "":
                                                    await mess.channel.send("That spot is already occupied")
                                                elif not game.is_valid_move(r, c, "black"):
                                                    await mess.channel.send("Invalid move")
                                                else:
                                                    break
                                        except ValueError:
                                            if message == "board":
                                                game.string_rows()
                                                board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                                await mess.channel.send(embed = board)
                                            elif message == "quit":
                                                game.game_end = 1
                                                game.winner = opp_id
                                                await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                break
                                            else:
                                                await mess.channel.send("Invalid input")
                                    if game.game_end == 0:
                                        game.guess(r, c, "black")
                                        game.string_rows()
                                        board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                        await mess.channel.send(embed = board)
                                        game.turn = 1
                                else:
                                    await mess.channel.send("Black has no moves left so it is white's turn")
                                    game.turn = 1
                            else:
                                if game.any_valid("white"):
                                    await mess.channel.send(f"<@!{opp_id}> it's your turn")
                                    game.string_rows()
                                    board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                    await mess.channel.send(embed = board)
                                    while True:
                                        await mess.channel.send("Enter the row and column where you would like to place your coin (ex: '3 4') (Type 'board' to see your current game; type 'quit' to end the game)")
                                        try:
                                            rc_msg = await bot.wait_for("message", check = lambda m: m.author.id == opp_id and m.channel == mess.channel, timeout = 120.0)
                                        except asyncio.TimeoutError:
                                            await mess.channel.send("You took too long to respond so the game has ended 😢")
                                            game.game_end = 1
                                            game.winner = a_id
                                            await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                            break
                                        message = rc_msg.content
                                        try:
                                            r, c = map(int, message.split())
                                            if r <= 0 or r > 8:
                                                await mess.channel.send("Row is out of range")
                                            elif c <= 0 or c > 8:
                                                await mess.channel.send("Column is out of range")
                                            else:
                                                if game.items[r-1][c-1] != "":
                                                    await mess.channel.send("That spot is already occupied")
                                                elif not game.is_valid_move(r, c, "white"):
                                                    await mess.channel.send("Invalid move")
                                                else:
                                                    break
                                        except ValueError:
                                            message = message.lower()
                                            if message == "board":
                                                game.string_rows()
                                                board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                                await mess.channel.send(embed = board)
                                            elif message == "quit":
                                                game.game_end = 1
                                                game.winner = a_id
                                                await mess.channel.send(f"<@!{game.winner}> is the winner!")
                                                break
                                            else:
                                                await mess.channel.send("Invalid input")
                                    if game.game_end == 0:
                                        game.guess(r, c, "white")
                                        game.string_rows()
                                        board = discord.Embed(title = "Othello!", description = game.board, colour = discord.Colour.blue())
                                        await mess.channel.send(embed = board)
                                        game.turn = 0
                                else:
                                    await mess.channel.send("White has no moves left so it is black's turn")
                                    game.turn = 0
                        if game.game_end == 0:
                            game.find_winner()
                            if not game.tie:
                                await mess.channel.send(f"<@!{game.winner}> is the winner!")
                            else:
                                await mess.channel.send("It's a tie ¯\_(ツ)_/¯")

                    else:
                        await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                in_game.remove(a_id)
                in_game.remove(opp_id)
            else:
                if a_id in in_game:
                    await mess.send("You're already in a game!", ephemeral = True)
                else:
                    await mess.send("Your opponent is already in a game!", ephemeral = True)
            
    else:
        await mess.send("You can't play a match against someone in a DM!", ephemeral = True)

@bot.slash_command(name = "mastermind", description = "Start a game of mastermind")
async def mm(mess: discord.Interaction, user: discord.Member = discord.SlashOption(name = "opponent", description = "The opponent you wish to play against", required = True)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("mastermind")
    if not(isinstance(mess.channel, discord.DMChannel)):
        channel_id = mess.channel.id
        opp_id = user.id
        a_id = mess.user.id
        me = await bot.fetch_user(a_id)
        opponent = await bot.fetch_user(opp_id)
        server_id = mess.guild.id
        guild = bot.get_guild(server_id)
        if opponent != me and not(opponent.bot):
            if a_id not in in_game and opp_id not in in_game:
                await mess.send("Done!", ephemeral = True)
                await mess.channel.send(f"<@!{opp_id}>")
                want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of mastermind! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                want_play = await mess.channel.send(embed = want_play_embed)
                await want_play.add_reaction("✅")
                await want_play.add_reaction("❌")
                in_game.append(a_id)
                in_game.append(opp_id)
                try:
                    reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                except asyncio.TimeoutError:
                    await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                else:
                    if str(reaction.emoji) == "✅":
                        red = str(bot.get_emoji(962686453157068880))
                        orange = str(bot.get_emoji(962686453320679454))
                        yellow = str(bot.get_emoji(962686452918009858))
                        green = str(bot.get_emoji(962686453123534858))
                        blue = str(bot.get_emoji(962686453123543050))
                        purple = str(bot.get_emoji(962686453438095360))
                        brown = str(bot.get_emoji(962686453157085275))
                        p1_id = rd.choice([a_id, opp_id])
                        if p1_id == a_id:
                            p2_id = opp_id
                        else:
                            p2_id = a_id
                        await mess.channel.send(f"<@!{p1_id}> check your DMs for a message from me to enter your code!")
                        game = mastermind(p1_id, p2_id, get_theme(p2_id), red, orange, yellow, green, blue, purple, brown)
                        p1 = await bot.fetch_user(p1_id)
                        while True:
                            try:
                                await p1.send(f'''Enter the hidden code with the following numbers:
{red}, {orange}, {yellow}, {green}, {blue}, {purple}, {brown}
Ex: 1 2 3 4
''')
                            except discord.errors.Forbidden:
                                in_game.remove(p1_id)
                                in_game.remove(p2_id)
                                raise Exception("Cannot send messages to this user")
                            try:
                                hcode_msg = await bot.wait_for("message", check = lambda m: m.author.id == p1_id and m.guild == None, timeout = 120.0)
                            except asyncio.TimeoutError:
                                await p1.send("You took too long to respond so the game has been cancelled")
                                game.game = 1
                                break
                            else:
                                hc = hcode_msg.content
                                try:
                                    invalid = 0
                                    nums = list(map(int, hc.split()))
                                    if len(nums) != 4:
                                        await p1.send("You can only enter 4 numbers")
                                        invalid = 1
                                    else:
                                        for x in nums:
                                            if not(1 <= x <= 7):
                                                await p1.send("You can only enter numbers from 1-7")
                                                invalid = 1
                                                break
                                    if invalid == 0:
                                        break
                                except ValueError:
                                    await p1.send("You can only enter numbers from 1-7")
                        if game.game == 0:
                            game.colourify(nums, 1)
                            hcode_str = ""
                            for x in game.hcode:
                                hcode_str += x
                            await p1.send(f"You have chosen the code {hcode_str}. Head back to <#{channel_id}> to watch the match!")
                            channel = await bot.fetch_channel(channel_id)
                            await channel.send(f"<@!{p2_id}> the code has been chosen! Get ready!" )
                            while game.game == 0 and game.turns < 8:
                                game.string_rows()
                                grid_embed = discord.Embed(title = "Mastermind!", description = game.grid, colour = discord.Colour.blue())
                                await channel.send(embed = grid_embed)
                                while True:
                                    await channel.send(f'''Enter your guess with the following numbers:
{red}, {orange}, {yellow}, {green}, {blue}, {purple}, {brown}
Ex: 1 2 3 4

Type 'board' to view the current board; type 'quit' to quit the game
''')
                                    try:
                                        gcode_msg = await bot.wait_for("message", check = lambda m: m.author.id == p2_id and m.channel == channel, timeout = 300.0)
                                    except asyncio.TimeoutError:
                                        await channel.send("You took too long to respond so the game has ended")
                                        game.winner = game.p1
                                        await channel.send(f"<@!{game.winner}> is the winner!")
                                        game.turns = None
                                        break
                                    else:
                                        gc = gcode_msg.content
                                        try:
                                            invalid = 0
                                            nums = list(map(int, gc.split()))
                                            if len(nums) != 4:
                                                await channel.send("You can only enter 4 numbers")
                                                invalid = 1
                                            else:
                                                for x in nums:
                                                    if not(1 <= x <= 7):
                                                        await channel.send("You can only enter numbers from 1-7")
                                                        invalid = 1
                                                        break
                                            if invalid == 0:
                                                break
                                        except ValueError:
                                            gc = gc.lower()
                                            if gc == "quit":
                                                game.turns = None
                                                game.winner = game.p1
                                                await channel.send(f"<@!{game.winner}> is the winner!")
                                                break
                                            elif gc == "board":
                                                game.string_rows()
                                                grid_embed = discord.Embed(title = "Mastermind!", description = game.grid, colour = discord.Colour.blue())
                                                await channel.send(embed = grid_embed)
                                            else:
                                                await channel.send("You can only enter numbers from 1-7")
                                if game.turns != None:
                                    game.guess(nums)
                                else:
                                    break
                            if game.turns != None:
                                game.string_rows()
                                grid_embed = discord.Embed(title = "Mastermind!", description = game.grid, colour = discord.Colour.blue())
                                await channel.send(embed = grid_embed)
                                if game.turns == 8:
                                    game.winner = game.p1
                                await channel.send(f"<@!{game.winner}> is the winner!")

                    else:
                        await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                in_game.remove(a_id)
                in_game.remove(opp_id)
            else:
                if a_id in in_game:
                    await mess.send("You're already in a game!", ephemeral = True)
                else:
                    await mess.send("Your opponent is already in a game!", ephemeral = True)

    else:
        await mess.send("You can't play a match against someone in a DM!", ephemeral = True)

@bot.slash_command(name = "yahtzee", description = "Start a game of yahtzee")
async def yz(mess: discord.Interaction, user: discord.Member = discord.SlashOption(name = "opponent", description = "The opponent you wish to play against", required = True)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("yahtzee")
    if not(isinstance(mess.channel, discord.DMChannel)):
        channel_id = mess.channel.id
        opp_id = user.id
        a_id = mess.user.id
        me = await bot.fetch_user(a_id)
        opponent = await bot.fetch_user(opp_id)
        server_id = mess.guild.id
        guild = bot.get_guild(server_id)
        if opponent != me and not(opponent.bot):
            if a_id not in in_game and opp_id not in in_game:
                await mess.send("Done!", ephemeral = True)
                await mess.channel.send(f"<@!{opp_id}>")
                want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of yahtzee! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                want_play = await mess.channel.send(embed = want_play_embed)
                await want_play.add_reaction("✅")
                await want_play.add_reaction("❌")
                in_game.append(a_id)
                in_game.append(opp_id)
                try:
                    reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                except asyncio.TimeoutError:
                    await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                else:
                    if str(reaction.emoji) == "✅":
                        d1 = str(bot.get_emoji(963012018066055188))
                        d2 = str(bot.get_emoji(963012017558540309))
                        d3 = str(bot.get_emoji(963012018045063248))
                        d4 = str(bot.get_emoji(963012017982173254))
                        d5 = str(bot.get_emoji(963012017894084638))
                        d6 = str(bot.get_emoji(963012017671774259))
                        p1_game = yahtzee(a_id, d1, d2, d3, d4, d5, d6)
                        p2_game = yahtzee(opp_id, d1, d2, d3, d4, d5, d6)
                        turn = 0
                        while (p1_game.game == 0 or p2_game.game == 0) and p1_game.quit == 0 and p2_game.quit == 0:
                            if turn == 0:
                                if p1_game.empty_pos > 0:
                                    await mess.channel.send(f"<@!{p1_game.user_id}> it's your turn")
                                    p1_game.string_rows()
                                    p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                    p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                    p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                    p1_card.add_field(name = "Scores", value = p1_game.right)
                                    await mess.channel.send(embed = p1_card)
                                    inp = ""
                                    while p1_game.rolls > 0 and inp != "stop" and p1_game.quit == 0:
                                        p1_game.roll()
                                        p1_game.string_dice()
                                        dice_string = ""
                                        for x in p1_game.sdice:
                                            dice_string += x+" "
                                        roll = discord.Embed(title = f"Roll {3-p1_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                        await mess.channel.send(embed = roll)
                                        if p1_game.rolls > 0:
                                            while True:
                                                await mess.channel.send("Enter the numbers of the dice you would like to hold separated by spaces. Ex: 1 2 3 (Enter 0 to hold none of the dice; enter 'stop' to not roll again; enter 'dice' to view the current roll; enter 'card' to view the card; enter 'quit' to quit the game)")
                                                try:
                                                    inp = await bot.wait_for("message", check = lambda m: m.author.id == p1_game.user_id and m.channel == mess.channel, timeout = 120.0)
                                                except asyncio.TimeoutError:
                                                    await mess.channel.send("You took too long to respond so the game has ended")
                                                    p1_game.quit = 1
                                                    await mess.channel.send(f"<@!{p2_game.user_id}> is the winner!")
                                                    break
                                                else:
                                                    inp = inp.content
                                                    inp = inp.lower()
                                                    if inp != "stop":
                                                        try:
                                                            invalid = 0
                                                            nums = list(map(int, inp.split()))
                                                            if len(nums) > 5:
                                                                await mess.channel.send("You can't hold more than 5 dice")
                                                                invalid = 1
                                                            elif len(nums) == 1 and nums[0] == 0:
                                                                nums = []
                                                            else:
                                                                for x in nums:
                                                                    if not(1 <= x <= 6):
                                                                        await mess.channel.send("You can only hold dice with numbers from 1-6")
                                                                        invalid = 1
                                                                        break
                                                                    elif x not in p1_game.dice or nums.count(x) > p1_game.counts[x]:
                                                                        await mess.channel.send("You can only hold dice that have been rolled")
                                                                        invalid = 1
                                                                        break
                                                            if invalid == 0:
                                                                break
                                                        except ValueError:
                                                            if inp == "quit":
                                                                p1_game.quit = 1
                                                                await mess.channel.send(f"<@!{p2_game.user_id}> is the winner!")
                                                                break
                                                            elif inp == "dice":
                                                                p1_game.string_dice()
                                                                dice_string = ""
                                                                for x in p1_game.sdice:
                                                                    dice_string += x+" "
                                                                roll = discord.Embed(title = f"Roll {3-p1_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                                await mess.channel.send(embed = roll)
                                                            elif inp == "card":
                                                                p1_game.string_rows()
                                                                p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                                                p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                                                p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                                                p1_card.add_field(name = "Scores", value = p1_game.right)
                                                                await mess.channel.send(embed = p1_card)
                                                                p1_game.string_dice()
                                                                dice_string = ""
                                                                for x in p1_game.sdice:
                                                                    dice_string += x+" "
                                                                roll = discord.Embed(title = f"Roll {3-p1_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                                await mess.channel.send(embed = roll)
                                                            else:
                                                                await mess.channel.send("You can only enter integral values")
                                                    else:
                                                        break
                                            if inp != "stop" and p1_game.quit == 0:
                                                p1_game.store(nums)
                                    if p1_game.quit == 0:
                                        p1_game.string_rows()
                                        p1_game.string_dice()
                                        dice_string = ""
                                        for x in p1_game.sdice:
                                            dice_string += x+" "
                                        p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                        p1_card.add_field(name = "Final dice", value = dice_string, inline = False)
                                        p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                        p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                        p1_card.add_field(name = "Scores", value = p1_game.right)
                                        await mess.channel.send(embed = p1_card)
                                        while True:
                                            await mess.channel.send("Which field would you like to place your roll in. Ex: L1 (Enter 'card' to view the card)")
                                            try:
                                                loc = await bot.wait_for("message", check = lambda m: m.author.id == p1_game.user_id and m.channel == mess.channel, timeout = 120.0)
                                            except asyncio.TimeoutError:
                                                await mess.channel.send("You took too long to repond so the game has ended")
                                                p1_game.quit = 1
                                                await mess.channel.send(f"<@!{p2_game.user_id}> is the winner!")
                                                break
                                            else:
                                                loc = loc.content
                                                loc = str(loc).upper()
                                                if loc[0] in ["U", "L"]:
                                                    try:
                                                        invalid = 0
                                                        if len(loc) != 2:
                                                            await mess.channel.send("Invalid input")
                                                            invalid = 1
                                                        elif loc[0] == "U":
                                                            if not(1 <= int(loc[1:]) <= 6):
                                                                await mess.channel.send("Invalid field")
                                                                invalid = 1
                                                        else:
                                                            if not(1 <= int(loc[1:]) <= 7):
                                                                await mess.channel.send("Invalid field")
                                                                invalid = 1
                                                        if invalid == 0:
                                                            p1_game.points(loc)
                                                            if p1_game.invalid == 0:
                                                                break
                                                            else:
                                                                await mess.channel.send("That field is already occupied")
                                                    except ValueError:
                                                        await mess.channel.send("Invalid input")
                                                else:
                                                    if loc == "CARD":
                                                        p1_game.string_rows()
                                                        p1_game.string_dice()
                                                        dice_string = ""
                                                        for x in p1_game.sdice:
                                                            dice_string += x+" "
                                                        p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                                        p1_card.add_field(name = "Final dice", value = dice_string, inline = False)
                                                        p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                                        p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                                        p1_card.add_field(name = "Scores", value = p1_game.right)
                                                        await mess.channel.send(embed = p1_card)
                                                    else:
                                                        await mess.channel.send("Invalid input")
                                        if p1_game.quit == 0:
                                            p1_game.string_rows()
                                            p1_card = discord.Embed(title = "Yahtzee!", description = f"{me.name}'s yahtzee card", colour = discord.Colour.blue())
                                            p1_card.add_field(name = "Upper", value = p1_game.left, inline = True)
                                            p1_card.add_field(name = "Lower", value = p1_game.middle, inline = True)
                                            p1_card.add_field(name = "Scores", value = p1_game.right)
                                            await mess.channel.send(embed = p1_card)
                                else:
                                    p1_game.game = 1
                                turn = 1
                            else:
                                if p2_game.empty_pos > 0:
                                    await mess.channel.send(f"<@!{p2_game.user_id}> it's your turn")
                                    p2_game.string_rows()
                                    p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                    p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                    p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                    p2_card.add_field(name = "Scores", value = p2_game.right)
                                    await mess.channel.send(embed = p2_card)
                                    inp = ""
                                    while p2_game.rolls > 0 and inp != "stop" and p2_game.quit == 0:
                                        p2_game.roll()
                                        p2_game.string_dice()
                                        dice_string = ""
                                        for x in p2_game.sdice:
                                            dice_string += x+" "
                                        roll = discord.Embed(title = f"Roll {3-p2_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                        await mess.channel.send(embed = roll)
                                        if p2_game.rolls > 0:
                                            while True:
                                                await mess.channel.send("Enter the numbers of the dice you would like to hold separated by spaces. Ex: 1 2 3 (Enter 0 to hold none of the dice; enter 'stop' to not roll again; enter 'dice' to view the current roll; enter 'card' to view the card; enter 'quit' to quit the game)")
                                                try:
                                                    inp = await bot.wait_for("message", check = lambda m: m.author.id == p2_game.user_id and m.channel == mess.channel, timeout = 120.0)
                                                except asyncio.TimeoutError:
                                                    await mess.channel.send("You took too long to respond so the game has ended")
                                                    p2_game.quit = 1
                                                    await mess.channel.send(f"<@!{p1_game.user_id}> is the winner!")
                                                    break
                                                else:
                                                    inp = inp.content
                                                    inp = inp.lower()
                                                    if inp != "stop":
                                                        try:
                                                            invalid = 0
                                                            nums = list(map(int, inp.split()))
                                                            if len(nums) > 5:
                                                                await mess.channel.send("You can't hold more than 5 dice")
                                                                invalid = 1
                                                            elif len(nums) == 1 and nums[0] == 0:
                                                                nums = []
                                                            else:
                                                                for x in nums:
                                                                    if not(1 <= x <= 6):
                                                                        await mess.channel.send("You can only hold dice with numbers from 1-6")
                                                                        invalid = 1
                                                                        break
                                                                    elif x not in p2_game.dice or nums.count(x) > p2_game.counts[x]:
                                                                        await mess.channel.send("You can only hold dice that have been rolled")
                                                                        invalid = 1
                                                                        break
                                                            if invalid == 0:
                                                                break
                                                        except ValueError:
                                                            if inp == "quit":
                                                                p2_game.quit = 1
                                                                await mess.channel.send(f"<@!{p1_game.user_id}> is the winner!")
                                                                break
                                                            elif inp == "dice":
                                                                p2_game.string_dice()
                                                                dice_string = ""
                                                                for x in p2_game.sdice:
                                                                    dice_string += x+" "
                                                                roll = discord.Embed(title = f"Roll {3-p2_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                                await mess.channel.send(embed = roll)
                                                            elif inp == "card":
                                                                p2_game.string_rows()
                                                                p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                                                p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                                                p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                                                p2_card.add_field(name = "Scores", value = p2_game.right)
                                                                await mess.channel.send(embed = p2_card)
                                                                p2_game.string_dice()
                                                                dice_string = ""
                                                                for x in p2_game.sdice:
                                                                    dice_string += x+" "
                                                                roll = discord.Embed(title = f"Roll {3-p2_game.rolls}", description = dice_string, colour = discord.Colour.blue())
                                                                await mess.channel.send(embed = roll)
                                                            else:
                                                                await mess.channel.send("You can only enter integral values")
                                                    else:
                                                        break
                                            if inp != "stop" and p2_game.quit == 0:
                                                p2_game.store(nums)
                                    if p2_game.quit == 0:
                                        p2_game.string_rows()
                                        p2_game.string_dice()
                                        dice_string = ""
                                        for x in p2_game.sdice:
                                            dice_string += x+" "
                                        p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                        p2_card.add_field(name = "Final dice", value = dice_string, inline = False)
                                        p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                        p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                        p2_card.add_field(name = "Scores", value = p2_game.right)
                                        await mess.channel.send(embed = p2_card)
                                        while True:
                                            await mess.channel.send("Which field would you like to place your roll in. Ex: L1 (Enter 'card' to view the card)")
                                            try:
                                                loc = await bot.wait_for("message", check = lambda m: m.author.id == p2_game.user_id and m.channel == mess.channel, timeout = 120.0)
                                            except asyncio.TimeoutError:
                                                await mess.channel.send("You took too long to repond so the game has ended")
                                                p2_game.quit = 1
                                                await mess.channel.send(f"<@!{p1_game.user_id}> is the winner!")
                                                break
                                            else:
                                                loc = loc.content
                                                loc = str(loc).upper()
                                                if loc[0] in ["U", "L"]:
                                                    try:
                                                        invalid = 0
                                                        if len(loc) != 2:
                                                            await mess.channel.send("Invalid input")
                                                            invalid = 1
                                                        elif loc[0] == "U":
                                                            if not(1 <= int(loc[1:]) <= 6):
                                                                await mess.channel.send("Invalid field")
                                                                invalid = 1
                                                        else:
                                                            if not(1 <= int(loc[1:]) <= 7):
                                                                await mess.channel.send("Invalid field")
                                                                invalid = 1
                                                        if invalid == 0:
                                                            p2_game.points(loc)
                                                            if p2_game.invalid == 0:
                                                                break
                                                            else:
                                                                await mess.channel.send("That field is already occupied")
                                                    except ValueError:
                                                        await mess.channel.send("Invalid input")
                                                else:
                                                    if loc == "CARD":
                                                        p2_game.string_rows()
                                                        p2_game.string_dice()
                                                        dice_string = ""
                                                        for x in p2_game.sdice:
                                                            dice_string += x+" "
                                                        p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                                        p2_card.add_field(name = "Final dice", value = dice_string, inline = False)
                                                        p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                                        p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                                        p2_card.add_field(name = "Scores", value = p2_game.right)
                                                        await mess.channel.send(embed = p2_card)
                                                    else:
                                                        await mess.channel.send("Invalid input")
                                        if p2_game.quit == 0:
                                            p2_game.string_rows()
                                            p2_card = discord.Embed(title = "Yahtzee!", description = f"{opponent.name}'s yahtzee card", colour = discord.Colour.blue())
                                            p2_card.add_field(name = "Upper", value = p2_game.left, inline = True)
                                            p2_card.add_field(name = "Lower", value = p2_game.middle, inline = True)
                                            p2_card.add_field(name = "Scores", value = p2_game.right)
                                            await mess.channel.send(embed = p2_card)
                                else:
                                    p2_game.game = 1
                                turn = 0
                        if p1_game.quit == 0 and p2_game.quit == 0:
                            await mess.channel.send(f'''
{me.name}'s total: {p1_game.total}
{opponent.name}'s total: {p2_game.total}
''')
                            if p1_game.total > p2_game.total:
                                await mess.channel.send(f"<@!{p1_game.user_id}> is the winner!")
                            elif p2_game.total > p1_game.total:
                                await mess.channel.send(f"<@!{p2_game.user_id}> is the winner!")
                            else:
                                await mess.channel.send("It's a tie ¯\_(ツ)_/¯")

                    else:
                        await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                in_game.remove(a_id)
                in_game.remove(opp_id)
            else:
                if a_id in in_game:
                    await mess.send("You're already in a game!", ephemeral = True)
                else:
                    await mess.send("Your opponent is already in a game!", ephemeral = True)
            
    else:
        await mess.send("You can't play a match against someone in a DM!", ephemeral = True)

@bot.slash_command(name = "battleship", description = "Start a game of battleship")
async def bs(mess: discord.Interaction, user: discord.Member = discord.SlashOption(name = "opponent", description = "The opponent you wish to play against", required = True)):
    global in_game, live_battles
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("battleship")
    if not(isinstance(mess.channel, discord.DMChannel)):
        channel_id = mess.channel.id
        opp_id = user.id
        a_id = mess.user.id
        me = await bot.fetch_user(a_id)
        opponent = await bot.fetch_user(opp_id)
        server_id = mess.guild.id
        guild = bot.get_guild(server_id)
        channel = mess.channel
        if opponent != me and not(opponent.bot):
            if a_id not in in_game and opp_id not in in_game and channel.id not in live_battles.keys():
                await mess.send("Done!", ephemeral = True)
                await mess.channel.send(f"<@!{opp_id}>")
                want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of battleship! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                want_play = await mess.channel.send(embed = want_play_embed)
                await want_play.add_reaction("✅")
                await want_play.add_reaction("❌")
                in_game.append(a_id)
                in_game.append(opp_id)
                try:
                    reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                except asyncio.TimeoutError:
                    await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                else:
                    if str(reaction.emoji) == "✅":
                        live_battles[channel.id] = (0, 0)
                        await mess.channel.send("Hop into your DMs and start playing!")
                        p1_game = battleship(get_theme(a_id), get_theme(opp_id))
                        p2_game = battleship(get_theme(opp_id), get_theme(a_id))
                        async def get_pos(id, o_id):
                            timeout = 0
                            p0 = await bot.fetch_user(id)
                            p0_game = battleship(get_theme(id), get_theme(o_id))
                            ships = [("carrier", 5), ("battleship", 4), ("cruiser", 3), ("submarine", 3), ("destroyer", 2)]
                            for ship in ships:
                                if timeout == 0:
                                    while True:
                                        invalid = 0
                                        p0_game.string_grid()
                                        grid = discord.Embed(title = "Your grid", description = p0_game.grid_string, colour = discord.Colour.blue())
                                        try:
                                            await p0.send(embed = grid)
                                        except discord.errors.Forbidden:
                                            in_game.remove(id)
                                            in_game.remove(o_id)
                                            del live_battles[channel.id]
                                            raise Exception("Cannot send messages to this user")
                                        await p0.send(f"Where would you like to place your {ship[0]} ({ship[1]} holes)? (Enter the start and end coordinates separated by spaces. Ex: 1 1 1 5)")
                                        try:
                                            ship_loc = await bot.wait_for("message", check = lambda m: m.author.id == id and m.guild == None, timeout = 60.0)
                                        except asyncio.TimeoutError:
                                            await p0.send("You took too long to respond so the game has ended")
                                            timeout = 1
                                            break
                                        else:
                                            try:
                                                coords = list(map(int, ship_loc.content.split()))
                                                if len(coords) != 4:
                                                    await p0.send("You have to enter 2 sets of coordinates with 4 values")
                                                    invalid = 1
                                                else:
                                                    for coord in coords:
                                                        if not(1 <= coord <= 10):
                                                            await p0.send("You can only enter numbers from 1 to 10")
                                                            invalid = 1
                                                            break
                                            except ValueError:
                                                await p0.send("Invalid input")
                                                invalid = 1
                                            if invalid == 0:
                                                locs = ((coords[0], coords[1]), (coords[2], coords[3]))
                                                result = p0_game.valid_ship(locs, ship[1])
                                                if result[0] == 1:
                                                    error = result[1]
                                                    if error == "row":
                                                        await p0.send("You can only place the ship in a single row or column")
                                                    elif error == "length":
                                                        await p0.send(f"Your ship must be {ship[1]} units long")
                                                    elif error == "overlap":
                                                        await p0.send("Your entered ship is overlapping another one of your ships")

                                                else:
                                                    p0_game.place_ship(locs, ship[1])
                                                    break
                                else:
                                    break
                            if timeout == 0:
                                p0_game.string_grid()
                                grid = discord.Embed(title = "Your final grid", description = p0_game.grid_string, colour = discord.Colour.blue())
                                await p0.send(embed = grid)
                                await p0.send("Please wait for some time while your opponent finishes arranging their ships")
                                return p0_game
                            else:
                                return timeout
                        tasks = []
                        tasks.append(asyncio.create_task(get_pos(a_id, opp_id)))
                        tasks.append(asyncio.create_task(get_pos(opp_id, a_id)))
                        await asyncio.gather(*tasks)
                        p1_game = tasks[0].result()
                        p2_game = tasks[1].result()
                        p1 = me
                        p2 = opponent
                        if not(p1_game == 1 or p2_game == 1):
                            turn = 0
                            channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", colour = discord.Colour.blue())
                            p1_game.channel_grid()
                            p2_game.channel_grid()
                            channel_game_embed.add_field(name = f"{p1.name}'s grid", value = p1_game.guess_string, inline = True)
                            channel_game_embed.add_field(name = f"{p2.name}'s grid", value = p2_game.guess_string, inline = True)
                            channel_game = await channel.send(embed = channel_game_embed)
                            live_battles[channel.id] = (channel.guild.id, channel_game.id)
                            await p1.send("Get ready to begin!")
                            await p2.send("Get ready to begin!")
                            quit = 0
                            while p1_game.alive_ships > 0 and p2_game.alive_ships > 0 and quit == 0:
                                if turn == 0:
                                    await p2.send(f"It is <@!{p1.id}>'s turn")
                                    while True:
                                        p1_game.string_grid()
                                        p2_game.string_guess()
                                        p1_comp = discord.Embed(title = "Battleship!", description = f'''**Opponent ships**: {p2_game.ship_names}
**Your ships**: {p1_game.ship_names}''', colour = discord.Colour.blue())
                                        p1_comp.add_field(name = "Your target grid", value = p2_game.guess_string, inline = True)
                                        p1_comp.add_field(name = "Your grid", value = p1_game.grid_string, inline = True)
                                        await p1.send(embed = p1_comp)
                                        await p1.send("Enter the coordinates where you would like to shoot separated by a space (Ex: 5 4) (Enter 'quit' if you wish to quit the game)")
                                        try:
                                            loc_msg = await bot.wait_for("message", check = lambda m: m.author.id == p1.id and m.guild == None, timeout = 120.0)
                                        except asyncio.TimeoutError:
                                            await p1.send("You took too long to respond so the game has ended")
                                            await channel.send(f"<@!{p2.id}>, <@!{p1.id}> took too long to respond so the game has ended")
                                            quit = 1
                                            break
                                        else:
                                            try:
                                                loc = tuple(map(int, loc_msg.content.split()))
                                                if len(loc) != 2:
                                                    await p1.send("You can only enter 2 integral coordinates")
                                                elif not(1 <= loc[0] <= 10) or not(1 <= loc[1] <= 10):
                                                    await p1.send("You can only enter integers from 1 to 10")
                                                else:
                                                    shot = p2_game.shoot(loc)
                                                    if shot[0] == 1:
                                                        await p1.send("You have already shot over there")
                                                    else:
                                                        if shot[1] == 0:
                                                            await p1.send("That was a miss!")
                                                            await p2.send(f"<@!{p1.id}> shot at {loc} and missed!")
                                                            channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p1.id}> shot at {loc} and missed!", colour = discord.Colour.blue())
                                                            
                                                        else:
                                                            if shot[2] == 1:
                                                                await p1.send(f"{shot[3].upper()} SUNK!")
                                                                await p2.send(f"<@!{p1.id}> shot at {loc} and sunk your {shot[3]}!")
                                                                channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p1.id}> shot at {loc} and sunk the {shot[3]}!", colour = discord.Colour.blue())
                                                                
                                                            else:
                                                                await p1.send(f"YOU HIT THE {shot[3].upper()}!")
                                                                await p2.send(f"<@!{p1.id}> shot at {loc} and hit your {shot[3]}!")
                                                                channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p1.id}> shot at {loc} and hit the {shot[3]}!", colour = discord.Colour.blue())

                                                        break
                                            except ValueError:
                                                text = loc_msg.content.lower()
                                                if text == "quit":
                                                    await channel.send(f"<@!{p2.id}>, <@!{p1.id}> quit the game so you are the winner!")
                                                    quit = 1
                                                    break
                                                else:
                                                    await p1.send("You can only enter integers")
                                    if quit == 0:
                                        p1_game.string_grid()
                                        p2_game.string_guess()
                                        p1_comp = discord.Embed(title = "Battleship!", description = f'''**Opponent ships**: {p2_game.ship_names}
**Your ships**: {p1_game.ship_names}''', colour = discord.Colour.blue())
                                        p1_comp.add_field(name = "Your target grid", value = p2_game.guess_string, inline = True)
                                        p1_comp.add_field(name = "Your grid", value = p1_game.grid_string, inline = True)
                                        await p1.send(embed = p1_comp)
                                        p1_game.channel_grid()
                                        p2_game.channel_grid()
                                        channel_game_embed.add_field(name = f"{p1.name}'s grid", value = p1_game.guess_string, inline = True)
                                        channel_game_embed.add_field(name = f"{p2.name}'s grid", value = p2_game.guess_string, inline = True)
                                        await channel_game.edit(embed = channel_game_embed)
                                        turn = 1
                                else:
                                    await p1.send(f"It is <@!{p2.id}>'s turn")
                                    while True:
                                        p2_game.string_grid()
                                        p1_game.string_guess()
                                        p2_comp = discord.Embed(title = "Battleship!", description = f'''**Opponent ships**: {p1_game.ship_names}
**Your ships**: {p2_game.ship_names}''', colour = discord.Colour.blue())
                                        p2_comp.add_field(name = "Your target grid", value = p1_game.guess_string, inline = True)
                                        p2_comp.add_field(name = "Your grid", value = p2_game.grid_string, inline = True)
                                        await p2.send(embed = p2_comp)
                                        await p2.send("Enter the coordinates where you would like to shoot separated by a space (Ex: 5 4) (Enter 'quit' if you wish to quit the game)")
                                        try:
                                            loc_msg = await bot.wait_for("message", check = lambda m: m.author.id == p2.id and m.guild == None, timeout = 120.0)
                                        except asyncio.TimeoutError:
                                            await p2.send("You took too long to respond so the game has ended")
                                            await channel.send(f"<@!{p1.id}>, <@!{p2.id}> took too long to respond so the game has ended")
                                            quit = 1
                                            break
                                        else:
                                            try:
                                                loc = tuple(map(int, loc_msg.content.split()))
                                                if len(loc) != 2:
                                                    await p2.send("You can only enter 2 integral coordinates")
                                                elif not(1 <= loc[0] <= 10) or not(1 <= loc[1] <= 10):
                                                    await p2.send("You can only enter integers from 1 to 10")
                                                else:
                                                    shot = p1_game.shoot(loc)
                                                    if shot[0] == 1:
                                                        await p2.send("You have already shot over there")
                                                    else:
                                                        if shot[1] == 0:
                                                            await p2.send("That was a miss!")
                                                            await p1.send(f"<@!{p2.id}> shot at {loc} and missed!")
                                                            channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p2.id}> shot at {loc} and missed!", colour = discord.Colour.blue())
                                                        else:
                                                            if shot[2] == 1:
                                                                await p2.send(f"{shot[3].upper()} SUNK!")
                                                                await p1.send(f"<@!{p2.id}> shot at {loc} and sunk your {shot[3]}!")
                                                                channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p2.id}> shot at {loc} and sunk the {shot[3]}!", colour = discord.Colour.blue())
                                                                
                                                            else:
                                                                await p2.send(f"YOU HIT THE {shot[3].upper()}!")
                                                                await p1.send(f"<@!{p2.id}> shot at {loc} and hit your {shot[3]}!")
                                                                channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{p2.id}> shot at {loc} and hit the {shot[3]}!", colour = discord.Colour.blue())
                                                                
                                                        break
                                            except ValueError:
                                                text = loc_msg.content.lower()
                                                if text == "quit":
                                                    await channel.send(f"<@!{p1.id}>, <@!{p2.id}> quit the game so you are the winner!")
                                                    quit = 1
                                                    break
                                                else:
                                                    await p2.send("You can only enter integers")
                                    if quit == 0:
                                        p2_game.string_grid()
                                        p1_game.string_guess()
                                        p2_comp = discord.Embed(title = "Battleship!", description = f'''**Opponent ships**: {p1_game.ship_names}
**Your ships**: {p2_game.ship_names}''', colour = discord.Colour.blue())
                                        p2_comp.add_field(name = "Your target grid", value = p1_game.guess_string, inline = True)
                                        p2_comp.add_field(name = "Your grid", value = p2_game.grid_string, inline = True)
                                        await p2.send(embed = p2_comp)
                                        p1_game.channel_grid()
                                        p2_game.channel_grid()
                                        channel_game_embed.add_field(name = f"{p1.name}'s grid", value = p1_game.guess_string, inline = True)
                                        channel_game_embed.add_field(name = f"{p2.name}'s grid", value = p2_game.guess_string, inline = True)
                                        await channel_game.edit(embed = channel_game_embed)
                                        turn = 0
                            if quit == 0:
                                if p1_game.alive_ships == 0:
                                    await p1.send("You lost 😢")
                                    await p2.send("You won! 🥳")
                                    winner = p2
                                else:
                                    await p2.send("You lost 😢")
                                    await p1.send("You won! 🥳")
                                    winner = p1
                                p1_game.final_grid()
                                p2_game.final_grid()
                                p1_final = discord.Embed(title = "Your opponent's final grid", description = f"Ships alive: {p2_game.alive_ships}", colour = discord.Colour.blue())
                                p1_final.add_field(name = "Your guesses on the grid", value = p2_game.grid_string)
                                p2_final = discord.Embed(title = "Your opponent's final grid", description = f"Ships alive: {p1_game.alive_ships}", colour = discord.Colour.blue())
                                p2_final.add_field(name = "Your guesses on the grid", value = p1_game.grid_string)
                                await p1.send(embed = p1_final)
                                await p2.send(embed = p2_final)
                                await channel.send(f"<@!{winner.id}> is the winner!")
                                p1_game.channel_final()
                                p2_game.channel_final()
                                channel_game_embed = discord.Embed(title = f"Battleship | {p1.name} VS {p2.name}", description = f"<@!{winner.id}> is the winner!", colour = discord.Colour.blue())
                                channel_game_embed.add_field(name = f"{p1.name}'s revealed grid", value = p1_game.grid_string, inline = True)
                                channel_game_embed.add_field(name = f"{p2.name}'s revealed grid", value = p2_game.grid_string, inline = True)
                                await channel_game.edit(embed = channel_game_embed)
                        else:
                            if p1_game == 1:
                                await channel.send(f"<@!{p2.id}>, <@!{p1.id}> took too long to respond so the game has ended")
                            else:
                                await channel.send(f"<@!{p1.id}>, <@!{p2.id}> took too long to respond so the game has ended")
                        del live_battles[channel.id]
                        
                    else:
                        await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                in_game.remove(a_id)
                in_game.remove(opp_id)
            else:
                if channel.id not in live_battles.keys():
                    if a_id in in_game:
                        await mess.send("You're already in a game!", ephemeral = True)
                    else:
                        await mess.send("Your opponent is already in a game!", ephemeral = True)
                else:
                    await mess.send("There is already a battleship game going on over here!", ephemeral = True)
                                    
    else:
        await mess.send("You can't play a match against someone in a DM!", ephemeral = True)

@bot.slash_command(name = "live", description = "Send the links for current battleship and uno games")
async def live(mess: discord.Interaction):
    global in_game, live_battles, live_uno
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("live")
    if not(isinstance(mess.channel, discord.DMChannel)):
        channel_id = mess.channel.id
        live_msg = ""
        if channel_id in live_battles.keys():
            if live_battles[channel_id] != (0, 0):
                live_msg += f"**Battleship**: https://discord.com/channels/{live_battles[channel_id][0]}/{channel_id}/{live_battles[channel_id][1]}"
            else:
                live_msg += "**Battleship**: The players are placing their ships so the game is yet to begin"
        if channel_id in live_uno.keys():
            if live_uno[channel_id] != (0, 0):
                live_msg += f"\n**Uno**: https://discord.com/channels/{live_uno[channel_id][0]}/{channel_id}/{live_uno[channel_id][1]}"
            else:
                live_msg += "\n**Uno**: People are still joining the uno game!"
        if channel_id not in live_battles.keys() and channel_id not in live_uno.keys():
            live_msg += "There are no battleship or uno games going on in this channel at the moment"
        await mess.send(live_msg)
    else:
        await mess.send("This is not a DM command!", ephemeral = True)

@bot.slash_command(name = "hangman", description = "Start a game of hangman")
async def hm(mess: discord.Interaction, user: discord.Member = discord.SlashOption(name = "opponent", description = "The opponent you wish to play against", required = True)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("hangman")
    if not(isinstance(mess.channel, discord.DMChannel)):
        channel_id = mess.channel.id
        opp_id = user.id
        a_id = mess.user.id
        me = await bot.fetch_user(a_id)
        opponent = await bot.fetch_user(opp_id)
        server_id = mess.guild.id
        guild = bot.get_guild(server_id)
        channel = mess.channel
        members = []
        for m in guild.members:
            members.append(m)
        if opponent in members and opponent != me and not(opponent.bot):
            if a_id not in in_game and opp_id not in in_game:
                await mess.send("Done!", ephemeral = True)
                await mess.channel.send(f"<@!{opp_id}>")
                want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of hangman! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                want_play = await mess.channel.send(embed = want_play_embed)
                await want_play.add_reaction("✅")
                await want_play.add_reaction("❌")
                in_game.append(a_id)
                in_game.append(opp_id)
                try:
                    reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                except asyncio.TimeoutError:
                    await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                else:
                    if str(reaction.emoji) == "✅":
                        game = hangman()
                        l = [me, opponent]
                        p1 = rd.choice(l)
                        l.remove(p1)
                        p2 = l[0]
                        await mess.channel.send(f"<@!{p1.id}> check your DMs for a message from me to enter your word/phrase!")
                        timeout = 0
                        while True:
                            try:
                                await p1.send("Enter the hidden word/phrase; it must be at least 3 characters in length and must consist of only letters and spaces")
                            except discord.errors.Forbidden:
                                in_game.remove(p1.id)
                                in_game.remove(p2.id)
                                raise Exception("Cannot send messages to this user")
                            try:
                                hmsg = await bot.wait_for("message", check = lambda m: m.author.id == p1.id and m.guild == None, timeout = 120.0)
                            except asyncio.TimeoutError:
                                await p1.send("You took too long to respond so the game has ended")
                                await channel.send(f"<@!{p2.id}>, <@!{p1.id}> took too long to respond so the game has ended")
                                timeout = 1
                                break
                            else:
                                word = hmsg.content
                                word = str(word).lower()
                                if len(word) >= 3:
                                    is_alpha = True
                                    for x in word:
                                        if not(x.isalpha() or x == " "):
                                            is_alpha = False
                                            break
                                    if is_alpha:
                                        has_cons = False
                                        for x in word:
                                            if x not in "aeiou":
                                                has_cons = True
                                                break
                                        if not has_cons:
                                            await p1.send("You need to have at least one consonant in your word/phrase as all the vowels will be revealed at the start of the game")
                                        else:
                                            break
                                    else:
                                        await p1.send("You can only enter characters and spaces")
                                else:
                                    await p1.send("Your word/phrase has to be at least 3 characters long")
                        if timeout == 0:
                            game.sto_word(word)
                            await p1.send(f"You have chosen the phrase `{word}`. Head back to <#{channel.id}> to watch the match!")
                            await channel.send(f"<@!{p2.id}> the word has been chosen! Get ready! (All the vowels have already been filled in)")
                            while game.game == 0 and game.misses < 6 and timeout == 0:
                                if game.misses == 0:
                                    photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030062973829160/hangman_1.png"
                                elif game.misses == 1:
                                    photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030062692823080/hangman_2.png"
                                elif game.misses == 2:
                                    photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030062436941825/hangman_3.png"
                                elif game.misses == 3:
                                    photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030062197891122/hangman_4.png"
                                elif game.misses == 4:
                                    photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030061904269362/hangman_5.png"
                                elif game.misses == 5:
                                    photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030061631668324/hangman_6.png"
                                else:
                                    photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030061346422794/hangman_7.png"
                                man = discord.Embed(title = "Hangman!", colour = discord.Colour.blue())
                                man.set_image(url = photo)
                                game.string_letters()
                                await channel.send(embed = man)
                                await channel.send(f'''**Word**: {game.gword.upper()}

**Letters**:
{game.letters_string}''')
                                while True:
                                    await channel.send("Enter a letter to guess (Enter 'quit' to leave the game; Enter 'board' to see the current board)")
                                    try:
                                        letter_msg = await bot.wait_for("message", check = lambda m: m.author.id == p2.id and m.channel == mess.channel, timeout = 120.0)
                                    except asyncio.TimeoutError:
                                        await channel.send("You took too long to respond so the game has ended")
                                        await channel.send(f"<@!{p1.id}> is the winner!")
                                        timeout = 1
                                        break
                                    else:
                                        letter = letter_msg.content
                                        letter = str(letter).lower()
                                        if len(letter) == 1:
                                            if letter.isalpha():
                                                result = game.guess(letter)
                                                if result[1] == 0:
                                                    if result[0]:
                                                        await channel.send(f"{letter.upper()} was in the word/phrase!")
                                                    else:
                                                        await channel.send(f"{letter.upper()} was not in the word/phrase!")
                                                    break 
                                                else:
                                                    if letter not in "aeiou":
                                                        await channel.send("You have already guessed that letter!")
                                                    else:
                                                        await channel.send("All the vowels have already been displayed!")
                                            else:
                                                await channel.send("You can only enter a single letter")
                                        else:
                                            if letter == "quit":
                                                await channel.send(f"<@!{p1.id}> is the winner!")
                                                timeout = 1
                                                break
                                            elif letter == "board":
                                                man = discord.Embed(title = "Hangman!", colour = discord.Colour.blue())
                                                man.set_image(url = photo)
                                                game.string_letters()
                                                await channel.send(embed = man)
                                                await channel.send(f'''**Word**: {game.gword.upper()}

**Letters**:
{game.letters_string}''')
                                            else:
                                                await channel.send("You can only enter a single letter")
                            if timeout == 0:
                                man = discord.Embed(title = "Hangman!", colour = discord.Colour.blue())
                                if game.misses == 6:
                                    photo = "https://cdn.discordapp.com/attachments/879559947380211723/980030061346422794/hangman_7.png"
                                man.set_image(url = photo)
                                game.string_letters()
                                await channel.send(embed = man)
                                await channel.send(f'''**Word**: {game.gword.upper()}

**Letters**:
{game.letters_string}''')
                                if game.game == 0:
                                    await channel.send(f"<@!{p2.id}>, you could not guess the phrase correctly; it was `{game.hword}`")
                                    await channel.send(f"<@!{p1.id}> is the winner!")
                                else:
                                    await channel.send(f"<@!{p2.id}>, you guessed the phrase correctly! It was `{game.hword}`")
                                    await channel.send(f"<@!{p2.id}> is the winner!")
                    else:
                        await mess.channel.send(f"<@!{a_id}> your challenge was rejected")

                in_game.remove(a_id)
                in_game.remove(opp_id)
            else:
                if a_id in in_game:
                    await mess.send("You're already in a game!", ephemeral = True)
                else:
                    await mess.send("Your opponent is already in a game!", ephemeral = True)     

    else:
        await mess.send("You can't play a match against someone in a DM!", ephemeral = True)

@bot.slash_command(name = "uno", description = "Start a game of uno")
async def uno(mess: discord.Interaction):
    global in_game, live_uno
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("uno")
    if not(isinstance(mess.channel, discord.DMChannel)):
        host_id = mess.user.id
        if host_id not in in_game and mess.channel.id not in live_uno.keys():
            await mess.send("Done!", ephemeral = True)
            channel = mess.channel
            live_uno[mess.channel.id] = (0, 0)
            thumb = bot.get_emoji(935120796358152212)
            check = bot.get_emoji(935455988516028486)
            uno_members = [host_id]
            uno_init_embed = discord.Embed(title = "Uno game started!", description = f"<@!{host_id}> started a game of uno! React with {thumb} below or type `;join` to join! Remove your reaction or type `;leave` to leave. <@!{host_id}> react with {check} or type `;start` to start the game!", colour = discord.Colour.blue())
            uno_init = await mess.channel.send(embed = uno_init_embed)
            await uno_init.add_reaction(str(thumb))
            await uno_init.add_reaction(str(check))
            in_game.append(host_id)
            while True:
                decisions = [asyncio.create_task(bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) in [str(thumb), str(check)] and p != bot.user and r.message.id == uno_init.id, timeout = 60.0), name = "radd"), asyncio.create_task(bot.wait_for("reaction_remove", check = lambda r, p: str(r.emoji) == str(thumb) and p != bot.user and r.message.id == uno_init.id, timeout = 60.0), name = "rrem"), asyncio.create_task(bot.wait_for("message", check = lambda m: m.channel == mess.channel, timeout = 60.0), name = "msgd")]

                completed, pending = await asyncio.wait(decisions, return_when = asyncio.FIRST_COMPLETED)
                
                finished_task: asyncio.Task = list(completed)[0]
                
                for unfinished in pending:
                    try:
                        unfinished.cancel()
                    except asyncio.CancelledError:
                        pass

                action = finished_task.get_name()
                try:
                    result = finished_task.result()
                except asyncio.TimeoutError:
                    break

                else:
                    if action == "radd":
                        reaction, user = result
                        reaction_e = str(reaction.emoji)
                        if reaction_e == str(thumb) and user.id != host_id and user.id not in uno_members:
                            if user.id not in in_game:
                                await mess.channel.send(f"<@!{user.id}> has joined the game!")
                                uno_members.append(user.id)
                                in_game.append(user.id)
                            else:
                                await mess.channel.send("You're already in a game!")
                        elif reaction_e == str(check) and user.id == host_id:
                            break
                    elif action == "rrem":
                        reaction, user = result
                        reaction_e = str(reaction.emoji)
                        if reaction_e == str(thumb) and user.id != host_id and user.id in uno_members:
                            await mess.channel.send(f"<@!{user.id}> has left the game")
                            uno_members.remove(user.id)
                            in_game.remove(user.id)
                    elif action == "msgd":
                        jl_msg = str(result.content)
                        user = result.author
                        if jl_msg == ";join" and user.id not in uno_members and user.id != host_id:
                            if user.id not in in_game:
                                await mess.channel.send(f"<@!{user.id}> has joined the game!")
                                uno_members.append(user.id)
                                in_game.append(user.id)
                            else:
                                await mess.channel.send("You're already in a game!")
                        elif jl_msg == ";leave" and user.id in uno_members and user.id != host_id:
                            await mess.channel.send(f"<@!{user.id}> has left the game")
                            uno_members.remove(user.id)
                            in_game.remove(user.id)
                        elif jl_msg == ";start" and user.id == host_id:
                            break
            uno_members = list(set(uno_members))
            rd.shuffle(uno_members)
            if len(uno_members) > 1:
                uno_cards = [bot.get_emoji(982179451150430249), bot.get_emoji(982179449711759400), bot.get_emoji(982179450668089404), bot.get_emoji(982179833826115634), bot.get_emoji(982179450433200168), bot.get_emoji(982179450781327370), bot.get_emoji(982179449590132746), bot.get_emoji(982179450819059722), bot.get_emoji(982179451154595860), bot.get_emoji(982179450223493131), bot.get_emoji(982179449313316864), bot.get_emoji(982199615753437204), bot.get_emoji(982179450865193000), bot.get_emoji(982179450479325224), bot.get_emoji(982179450269630544), bot.get_emoji(982179450315739196), bot.get_emoji(982179450684842005), bot.get_emoji(982179449661435935), bot.get_emoji(982179449518837760), bot.get_emoji(982179450441588786), bot.get_emoji(982179450630328330), bot.get_emoji(982179450449965088), bot.get_emoji(982179449183281153), bot.get_emoji(982199640248156210), bot.get_emoji(982179451062337546), bot.get_emoji(982179450940702730), bot.get_emoji(982179449447546940), bot.get_emoji(982179451129450496), bot.get_emoji(982179450932322314), bot.get_emoji(982179449950830603), bot.get_emoji(982179449019699261), bot.get_emoji(982179449929875496), bot.get_emoji(982199575458754641), bot.get_emoji(982179449984397312), bot.get_emoji(982179449485266945), bot.get_emoji(982179450462568448), bot.get_emoji(982179450420609034), bot.get_emoji(982179450072477766), bot.get_emoji(982179449959247932), bot.get_emoji(982179450311540736), bot.get_emoji(982179450621931530), bot.get_emoji(982179449845985310), bot.get_emoji(982179449212641300), bot.get_emoji(982179449464303637), bot.get_emoji(982182124071301140), bot.get_emoji(982179448927445033), bot.get_emoji(982179448952610836), bot.get_emoji(982179450173128724), bot.get_emoji(982182206732664892), bot.get_emoji(982179449313308693), bot.get_emoji(982179449141346345), bot.get_emoji(982179450668064768), bot.get_emoji(982181991573241886), bot.get_emoji(982182052629741568)]
                uno_games = []
                p0_game = uno_c(uno_cards = uno_cards)
                mem_str = "Uno players:"
                for mem in uno_members:
                    player = await bot.fetch_user(mem)
                    uno_games.append((player, uno_c(get_theme(mem), uno_cards)))
                    mem_str += f'''
<@!{mem}>'''
                await mess.channel.send(mem_str)
                game = 0
                winner = None
                for x in uno_games:
                    x[1].string_rows()
                    your_cards_1 = "**Your uno cards:**"
                    your_cards_2 = x[1].cards_string
                    try:
                        await x[0].send(your_cards_1)
                    except discord.errors.Forbidden:
                        for id in uno_members:
                            in_game.remove(id)
                        del live_uno[channel.id]
                        raise Exception("Cannot send messages to this user")
                    await x[0].send(your_cards_2)
                init_number = rd.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
                init_colour = rd.choice(["red", "green", "blue", "yellow"])
                top_card = (init_number, init_colour)
                await channel.send("Hop into your DMs and start playing!")
                num_cards = f"It is <@!{uno_games[0][0].id}>'s turn"
                num_cards += '''

'''
                for x in uno_games:
                    num_cards += f"<@!{x[0].id}>'s cards: **{len(x[1].cards)}**"
                    if uno_games.index(x) == 0:
                        num_cards += "*"
                    num_cards += '''
'''
                channel_commentary_embed = discord.Embed(title = "Uno!", description = num_cards, colour = discord.Colour.blue())
                channel_commentary_embed.set_footer(text = "The current player is denoted by *")
                channel_game_2 = "**Top card:**"
                channel_game_3 = p0_game.colour_card(top_card)
                channel_commentary = await channel.send(embed = channel_commentary_embed)
                channel_msg_2 = await channel.send(channel_game_2)
                channel_msg_3 = await channel.send(channel_game_3)
                live_uno[channel.id] = (channel.guild.id, channel_msg_3.id)
                turn = 0
                flag = 0
                while game == 0 and len(uno_games) > 1:
                    await asyncio.sleep(2)
                    p0 = uno_games[turn][0]
                    p0_game = uno_games[turn][1]
                    uno_said = None
                    if top_card[0] not in ["skip", "reverse", "+2", "+4"] or flag == 0:
                        await p0.send("It is your turn")
                        channel_description = ""
                        if p0_game.available_card(top_card):
                            while True:
                                p0_game.string_rows()
                                cur_turn_1 = "**Top card:**"
                                cur_turn_2 = p0_game.colour_card(top_card)
                                cur_turn_3 = "**Your cards:**"
                                cur_turn_4 = p0_game.cards_string
                                await p0.send(cur_turn_1)
                                await p0.send(cur_turn_2)
                                await p0.send(cur_turn_3)
                                await p0.send(cur_turn_4)
                                await p0.send("Choose the position of your card to play it; Enter 'quit' to leave the game")
                                try:
                                    pos_msg = await bot.wait_for("message", check = lambda m: m.author.id == p0.id and m.guild == None, timeout = 120.0)
                                except asyncio.TimeoutError:
                                    await p0.send("You took too long to respond so you have been removed from the game")
                                    await channel.send(f"<@!{p0.id}> took too long to respond so they have been removed from the game")
                                    channel_description = f"<@!{p0.id}> has been removed from the game as they took too long to respond"
                                    uno_games.pop(turn)
                                    uno_members.pop(turn)
                                    in_game.remove(p0.id)
                                    turn -= 1
                                    break
                                else:
                                    pos = pos_msg.content.lower()
                                    try:
                                        pos = int(pos)
                                    except ValueError:
                                        pos = pos.lower()
                                        if pos == "quit":
                                            uno_games.pop(turn)
                                            uno_members.pop(turn)
                                            in_game.remove(p0.id)
                                            await p0.send("We're sorry to see you leave 😢")
                                            await channel.send(f"<@!{p0.id}> has left the game 😢")
                                            channel_description = f"<@!{p0.id}> has left the game"
                                            turn -= 1
                                            break
                                        elif pos == "uno" and len(p0_game.cards) == 2 and uno_said != True:
                                            await channel.send(f"<@!{p0.id}> said **UNO**!")
                                            uno_said = True
                                        elif len(p0_game.cards) == 2 and uno_said != True:
                                            uno_said = False
                                            await p0.send("You can only enter integral values")
                                        else:
                                            await p0.send("You can only enter integral values")
                                    else:
                                        if len(p0_game.cards) == 2 and uno_said != True:
                                            uno_said = False
                                        if not (1 <= pos <= len(p0_game.cards)):
                                            await p0.send(f"You can only enter integers from 1 to {len(p0_game.cards)}")
                                        else:
                                            result = p0_game.choose_card(top_card, pos)
                                            if result[0]:
                                                top_card = result[1]
                                                chosen_card = p0_game.colour_card(result[1])
                                                await p0.send("You have chosen the card:")
                                                await p0.send(chosen_card)
                                                
                                                if result[1][0] in ["skip", "reverse", "+2", "+4"]:
                                                    flag = 1
                                                if result[1][1] == "colourful":
                                                    colour_msg = await p0.send("Choose a colour")
                                                    await colour_msg.add_reaction("🔴")
                                                    await colour_msg.add_reaction("🟢")
                                                    await colour_msg.add_reaction("🔵")
                                                    await colour_msg.add_reaction("🟡")
                                                    reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == p0.id and r.message == colour_msg and str(r.emoji) in ["🔴", "🟢", "🔵", "🟡"])
                                                    if str(reaction.emoji) == "🔴":
                                                        colour = "red"
                                                    elif str(reaction.emoji) == "🟢":
                                                        colour = "green"
                                                    elif str(reaction.emoji) == "🔵":
                                                        colour = "blue"
                                                    else:
                                                        colour = "yellow"
                                                    await p0.send(f"You chose the colour {colour}")
                                                if result[1][1] == "colourful":
                                                    top_card = list(top_card)
                                                    top_card[1] = colour
                                                    top_card = tuple(top_card)
                                                    channel_description = f"<@!{p0.id}> played a **{result[1][0]}** and chose the colour **{colour}**"
                                                else:
                                                    channel_description = f"<@!{p0.id}> played a **{result[1][1]} {result[1][0]}**"
                                                if result[2]:
                                                    await p0.send("You are the winner!")
                                                    game = 1
                                                    winner = p0.id
                                                else:
                                                    p0_game.string_rows()
                                                    cur_turn_3 = "**Your cards:**"
                                                    cur_turn_4 = p0_game.cards_string
                                                    await p0.send(cur_turn_3)
                                                    await p0.send(cur_turn_4)
                                                break
                                            else:
                                                await p0.send("That is not a valid card")
                        else:
                            p0_game.string_rows()
                            cur_turn_1 = "**Top card:**"
                            cur_turn_2 = p0_game.colour_card(top_card)
                            cur_turn_3 = "**Your cards:**"
                            cur_turn_4 = p0_game.cards_string
                            await p0.send(cur_turn_1)
                            await p0.send(cur_turn_2)
                            await p0.send(cur_turn_3)
                            await p0.send(cur_turn_4)
                            await asyncio.sleep(5)
                            p0_game.draw(1)
                            await p0.send("You have drawn a card because you do not have a valid card to play")
                            channel_description = f"<@!{p0.id}> did not have any valid card so they drew one"
                            while True:
                                p0_game.string_rows()
                                cur_turn_1 = "**Top card:**"
                                cur_turn_2 = p0_game.colour_card(top_card)
                                cur_turn_3 = "**Your cards:**"
                                cur_turn_4 = p0_game.cards_string
                                await p0.send(cur_turn_1)
                                await p0.send(cur_turn_2)
                                await p0.send(cur_turn_3)
                                await p0.send(cur_turn_4)
                                if p0_game.available_card(top_card):
                                    await p0.send("Choose the position of your card to play it; Enter 'quit' to leave the game")
                                    try:
                                        pos_msg = await bot.wait_for("message", check = lambda m: m.author.id == p0.id and m.guild == None, timeout = 120.0)
                                    except asyncio.TimeoutError:
                                        await p0.send("You took too long to respond so you have been removed from the game")
                                        await channel.send(f"<@!{p0.id}> took too long to respond so they have been removed from the game")
                                        channel_description = f"<@!{p0.id}> has been removed from the game as they took too long to respond"
                                        uno_games.pop(turn)
                                        uno_members.pop(turn)
                                        in_game.remove(p0.id)
                                        turn -= 1
                                        break
                                    else:
                                        pos = pos_msg.content.lower()
                                        try:
                                            pos = int(pos)
                                        except ValueError:
                                            pos = pos.lower()
                                            if pos == "quit":
                                                uno_games.pop(turn)
                                                uno_members.pop(turn)
                                                in_game.remove(p0.id)
                                                await p0.send("We're sorry to see you leave 😢")
                                                await channel.send(f"<@!{p0.id}> has left the game 😢")
                                                channel_description = f"<@!{p0.id}> has left the game"
                                                turn -= 1
                                                break
                                            elif pos == "uno" and len(p0_game.cards) == 2 and uno_said != True:
                                                await channel.send(f"<@!{p0.id}> said **UNO**!")
                                                uno_said = True
                                            elif len(p0_game.cards) == 2 and uno_said != True:
                                                uno_said = False
                                                await p0.send("You can only enter integral values")
                                            else:
                                                await p0.send("You can only enter integral values")
                                        else:
                                            if len(p0_game.cards) == 2 and uno_said != True:
                                                uno_said = False
                                            if not (1 <= pos <= len(p0_game.cards)):
                                                await p0.send(f"You can only enter integers from 1 to {len(p0_game.cards)}")
                                            else:
                                                result = p0_game.choose_card(top_card, pos)
                                                if result[0]:
                                                    top_card = result[1]
                                                    chosen_card = p0_game.colour_card(result[1])
                                                    await p0.send("You have chosen the card:")
                                                    await p0.send(chosen_card)
                                                    if result[1][0] in ["skip", "reverse", "+2", "+4"]:
                                                        flag = 1
                                                    if result[1][1] == "colourful":
                                                        colour_msg = await p0.send("Choose a colour")
                                                        await colour_msg.add_reaction("🔴")
                                                        await colour_msg.add_reaction("🟢")
                                                        await colour_msg.add_reaction("🔵")
                                                        await colour_msg.add_reaction("🟡")
                                                        reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == p0.id and r.message == colour_msg and str(r.emoji) in ["🔴", "🟢", "🔵", "🟡"])
                                                        if str(reaction.emoji) == "🔴":
                                                            colour = "red"
                                                        elif str(reaction.emoji) == "🟢":
                                                            colour = "green"
                                                        elif str(reaction.emoji) == "🔵":
                                                            colour = "blue"
                                                        else:
                                                            colour = "yellow"
                                                        await p0.send(f"You chose the colour {colour}")
                                                    if result[1][1] == "colourful":
                                                        top_card = list(top_card)
                                                        top_card[1] = colour
                                                        top_card = tuple(top_card)
                                                        channel_description = f"<@!{p0.id}> drew a card and played a **{result[1][0]}** and chose the colour **{colour}**"
                                                    else:
                                                        channel_description = f"<@!{p0.id}> drew a card and played a **{result[1][1]} {result[1][0]}**"
                                                    if result[2]:
                                                        await p0.send("You are the winner!")
                                                        game = 1
                                                        winner = p0.id
                                                    else:
                                                        p0_game.string_rows()
                                                        cur_turn_3 = "**Your cards:**"
                                                        cur_turn_4 = p0_game.cards_string
                                                        await p0.send(cur_turn_3)
                                                        await p0.send(cur_turn_4)
                                                    break
                                                else:
                                                    await p0.send("That is not a valid card")
                                                
                                else:
                                    await p0.send("Your turn has ended")
                                    channel_description = f"<@!{p0.id}> could not play any card so their turn has passed on"
                                    break
                        channel_description += '''

'''
                        for x in uno_games:
                            channel_description += f"<@!{x[0].id}>'s cards: **{len(x[1].cards)}**"
                            if uno_games.index(x) == turn+1 or (uno_games.index(x) == 0 and turn+1 == len(uno_games)):
                                channel_description += "*"
                            channel_description += '''
'''
                        coloured_card = p0_game.colour_card(top_card)
                        channel_commentary_embed = discord.Embed(title = "Uno!", description = channel_description, colour = discord.Colour.blue())
                        channel_commentary_embed.set_footer(text = "The current player is denoted by *")
                        await channel_commentary.edit(embed = channel_commentary_embed)
                        await channel_msg_3.edit(content = coloured_card)
                    else:
                        p0_game.string_rows()
                        cur_turn_1 = "**Top card:**"
                        cur_turn_2 = p0_game.colour_card(top_card)
                        cur_turn_3 = "**Your cards:**"
                        cur_turn_4 = p0_game.cards_string
                        await p0.send(cur_turn_1)
                        await p0.send(cur_turn_2)
                        await p0.send(cur_turn_3)
                        await p0.send(cur_turn_4)
                        if top_card[0] == "skip":
                            await p0.send(f"You have been skipped by <@!{uno_games[turn-1][0].id}>")
                            channel_description = f"<@!{p0.id}> was skipped"
                        elif top_card[0] == "reverse":
                            await p0.send("The order has been reversed so it is not your turn now")
                            if len(uno_games) > 2:
                                player_b4 = uno_games[turn-2]
                            else:
                                player_b4 = uno_games[turn-1]
                            uno_games.reverse()
                            turn = uno_games.index(player_b4)-1
                            channel_description = "The order has been reversed"
                        elif top_card[0] == "+2":
                            await p0.send("You have to draw 2 cards now")
                            p0_game.draw(2)
                            p0_game.string_rows()
                            cur_turn_1 = "**Top card:**"
                            cur_turn_2 = p0_game.colour_card(top_card)
                            cur_turn_3 = "**Your cards:**"
                            cur_turn_4 = p0_game.cards_string
                            await p0.send(cur_turn_1)
                            await p0.send(cur_turn_2)
                            await p0.send(cur_turn_3)
                            await p0.send(cur_turn_4)
                            channel_description = f"<@!{p0.id}> drew 2 cards"
                        elif top_card[0] == "+4":
                            await p0.send("You have to draw 4 cards now")
                            p0_game.draw(4)
                            p0_game.string_rows()
                            cur_turn_1 = "**Top card:**"
                            cur_turn_2 = p0_game.colour_card(top_card)
                            cur_turn_3 = "**Your cards:**"
                            cur_turn_4 = p0_game.cards_string
                            await p0.send(cur_turn_1)
                            await p0.send(cur_turn_2)
                            await p0.send(cur_turn_3)
                            await p0.send(cur_turn_4)
                            channel_description = f"<@!{p0.id}> drew 4 cards"
                        channel_description += '''

'''
                        for x in uno_games:
                            channel_description += f"<@!{x[0].id}>'s cards: **{len(x[1].cards)}**"
                            if uno_games.index(x) == turn+1 or (uno_games.index(x) == 0 and turn+1 == len(uno_games)):
                                channel_description += "*"
                            channel_description += '''
'''
                        coloured_card = p0_game.colour_card(top_card)
                        channel_commentary_embed = discord.Embed(title = "Uno!", description = channel_description, colour = discord.Colour.blue())
                        channel_commentary_embed.set_footer(text = "The current player is denoted by *")
                        await channel_commentary.edit(embed = channel_commentary_embed)
                        await channel_msg_3.edit(content = coloured_card)
                        flag = 0

                    if uno_said == False:
                        while True:
                            uno_tasks = [asyncio.create_task(bot.wait_for("message", check = lambda m: m.channel.id == channel.id and m.author.id != p0.id and m.author.id in uno_members and str(m.content).lower() == "caught", timeout = 10.0), name = "caught"), asyncio.create_task(bot.wait_for("message", check = lambda m: m.guild == None and m.author.id == p0.id and str(m.content).lower() == "uno", timeout = 10.0), name = "uno")]

                            completed, pending = await asyncio.wait(uno_tasks, return_when = asyncio.FIRST_COMPLETED)
                            
                            finished_task: asyncio.Task = list(completed)[0]
                            
                            for unfinished in pending:
                                try:
                                    unfinished.cancel()
                                except asyncio.CancelledError:
                                    pass

                            action = finished_task.get_name()
                            try:
                                result = finished_task.result()
                            except asyncio.TimeoutError:
                                await channel.send(f"<@!{p0.id}> did not say uno and none of the other players caught them within the 10s time limit so they are not subject to the four card penalty! The next player's turn will start in a few seconds")
                                break

                            else:
                                if action == "caught":
                                    await channel.send(f"You have caught <@!{p0.id}> as they did not say uno! They now have to draw 4 cards")

                                    channel_description = f'''<@!{p0.id}> did not say uno and was caught by <@!{result.author.id}>

'''
                                    p0_game.draw(4)
                                    for x in uno_games:
                                        channel_description += f"<@!{x[0].id}>'s cards: **{len(x[1].cards)}**"
                                        if uno_games.index(x) == turn+1 or (uno_games.index(x) == 0 and turn+1 == len(uno_games)):
                                            channel_description += "*"
                                        channel_description += '''
'''
                                    coloured_card = p0_game.colour_card(top_card)
                                    channel_commentary_embed = discord.Embed(title = "Uno!", description = channel_description, colour = discord.Colour.blue())
                                    channel_commentary_embed.set_footer(text = "The current player is denoted by *")
                                    await channel_commentary.edit(embed = channel_commentary_embed)
                                    await p0.send(f"You did not say uno and <@!{result.author.id}> caught you so you have to draw 4 cards now")
                                    p0_game.string_rows()
                                    cur_turn_3 = "**Your cards:**"
                                    cur_turn_4 = p0_game.cards_string
                                    await p0.send(cur_turn_3)
                                    await p0.send(cur_turn_4)
                                    break
                                elif action == "uno":
                                    await channel.send(f"<@!{p0.id}> said uno before they were caught and does not have to draw any cards now!")
                                    break
                            
                    turn += 1
                    if turn == len(uno_games):
                        turn = 0
                    
                if game == 0:
                    await channel.send(f"<@!{uno_games[0][0].id}> is the winner!")
                    in_game.remove(uno_games[0][0].id)
                else:
                    await channel.send(f"<@!{winner}> is the winner!")
                    for x in uno_games:
                        in_game.remove(x[0].id)
                del live_uno[channel.id]
                
            else:
                await mess.channel.send("You need at least 2 players to play uno, so the game has been cancelled")
                in_game.remove(host_id)
                del live_uno[channel.id]
        else:
            if mess.channel.id not in live_uno.keys():
                await mess.send("You're already in a game!", ephemeral = True)
            else:
                await mess.send("There is already an uno game going on in this channel!", ephemeral = True)
    else:
        await mess.send("This is not a DM command!", ephemeral = True)

@bot.slash_command(name = "wordle", description = "Start a game of wordle")
async def wd(mess: discord.Interaction, user: discord.Member = discord.SlashOption(name = "opponent", description = "The opponent you wish to play against", required = True)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("wordle")
    if not(isinstance(mess.channel, discord.DMChannel)):
        channel_id = mess.channel.id
        opp_id = user.id
        a_id = mess.user.id
        me = await bot.fetch_user(a_id)
        opponent = await bot.fetch_user(opp_id)
        server_id = mess.guild.id
        guild = bot.get_guild(server_id)
        channel = mess.channel
        if opponent != me and not(opponent.bot):
            if a_id not in in_game and opp_id not in in_game:
                await mess.send("Done!", ephemeral = True)
                await mess.channel.send(f"<@!{opp_id}>")
                want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of wordle! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                want_play = await mess.channel.send(embed = want_play_embed)
                await want_play.add_reaction("✅")
                await want_play.add_reaction("❌")
                in_game.append(a_id)
                in_game.append(opp_id)
                try:
                    reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                except asyncio.TimeoutError:
                    await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                else:
                    if str(reaction.emoji) == "✅":
                        all_words = open("five_letter_words.txt", "r").read().splitlines()
                        p1_id = rd.choice([a_id, opp_id])
                        if p1_id == a_id:
                            p2_id = opp_id
                        else:
                            p2_id = a_id
                        await mess.channel.send(f"<@!{p1_id}> check your DMs for a message from me to enter your 5 letter word!")
                        game = wordle(p1_id, p2_id, get_theme(p2_id))
                        p1 = await bot.fetch_user(p1_id)
                        while True:
                            await p1.send("Enter your hidden word; it must consist of only 5 letters")
                            try:
                                word_msg = await bot.wait_for("message", check = lambda m: m.author.id == p1_id and m.guild == None, timeout = 120.0)
                            except asyncio.TimeoutError:
                                await p1.send("You took too long to respond so the game has ended")
                                await channel.send(f"<@!{p2_id}>, <@!{p1_id}> took too long to respond so the game has ended")
                                game.game = 1
                                break
                            else:
                                word = str(word_msg.content).lower()
                                valid = 1
                                if len(word) == 5:
                                    for x in word:
                                        if not(x.isalpha()):
                                            await p1.send("Your word can only consist of letters")
                                            valid = 0
                                            break
                                    if valid == 1:
                                        if word not in all_words:
                                            await p1.send("This is not a valid word")
                                            valid = 0
                                else:
                                    await p1.send("You can only enter a 5 letter word")
                                    valid = 0
                                if valid == 1:
                                    break
                        if game.game == 0:
                            game.colourify(word, 1)
                            hword_str = ""
                            for x in game.hword:
                                hword_str += x
                            await p1.send(f"You have chosen the word {hword_str}. Head back to <#{channel.id}> to watch the match!")
                            await channel.send(f"<@!{p2_id}> the word has been chosen! Get ready!")
                            timeout = 0
                            while game.game == 0 and game.turns < 6 and timeout == 0:
                                game.string_rows()
                                game_grid = discord.Embed(title = "Wordle!", description = game.grid, colour = discord.Colour.blue())
                                game_grid.add_field(name = "Keyboard", value = game.keyboard_string)
                                await channel.send(embed = game_grid)
                                while True:
                                    await channel.send("Guess a 5 letter word (Enter 'quit' to leave the game; Enter 'grid' to view the current board)")
                                    try:
                                        guess_msg = await bot.wait_for("message", check = lambda m: m.author.id == p2_id and m.channel.id == channel.id, timeout = 120.0)
                                    except asyncio.TimeoutError:
                                        await channel.send("You took too long to respond so the game has ended")
                                        timeout = 1
                                        break
                                    else:
                                        word = str(guess_msg.content).lower()
                                        valid = 1
                                        if len(word) == 5:
                                            for x in word:
                                                if not(x.isalpha()):
                                                    await channel.send("Your word can only consist of letters")
                                                    valid = 0
                                                    break
                                            if valid == 1:
                                                if word not in all_words:
                                                    await channel.send("This is not a valid word")
                                                    valid = 0
                                        else:
                                            if word == "quit":
                                                await channel.send("We're sorry to see you leave 😢")
                                                timeout = 1
                                                break
                                            elif word == "grid":
                                                game.string_rows()
                                                game_grid = discord.Embed(title = "Wordle!", description = game.grid, colour = discord.Colour.blue())
                                                game_grid.add_field(name = "Keyboard", value = game.keyboard_string)
                                                await channel.send(embed = game_grid)
                                            else:
                                                await channel.send("You can only enter a 5 letter word")
                                            valid = 0
                                        if valid == 1:
                                            game.guess(word)
                                            break
                            if game.turns == 6:
                                game.winner = p1_id
                            if timeout == 0:
                                game.string_rows()
                                game_grid = discord.Embed(title = "Wordle!", description = game.grid, colour = discord.Colour.blue())
                                game_grid.add_field(name = "Keyboard", value = game.keyboard_string)
                                await channel.send(embed = game_grid)
                                await channel.send(f"<@!{game.winner}> is the winner!")


                in_game.remove(a_id)
                in_game.remove(opp_id)
            else:
                if a_id in in_game:
                    await mess.send("You're already in a game!", ephemeral = True)
                else:
                    await mess.send("Your opponent is already in a game!", ephemeral = True)     

    else:
        await mess.send("You can't play a match against someone in a DM!", ephemeral = True)

@bot.slash_command(name = "2048", description = "Start a game of 2048")
async def tzfe(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("tzfe")
    author_id = mess.user.id
    if author_id not in in_game:
        await mess.send("Done!", ephemeral = True)
        in_game.append(author_id)
        p0 = mess.user
        a = bot.get_emoji(1006186622322212914)
        b = bot.get_emoji(1006186619822419970)
        c = bot.get_emoji(1006186617746239558)
        d = bot.get_emoji(1006186615300968458)
        e = bot.get_emoji(1006186612826321007)
        f = bot.get_emoji(1006186610456539296)
        g = bot.get_emoji(1006186607793156139)
        h = bot.get_emoji(1006186605469515897)
        i = bot.get_emoji(1006186602567041074)
        j = bot.get_emoji(1006186600197275678)
        k = bot.get_emoji(1006186597529698364)
        dirs = {"w": "up", "a": "left", "d": "right", "s": "down"}
        game = tzfe_c(a, b, c, d, e, f, g, h, i, j, k, get_theme(author_id))
        game.string_rows()
        game_embed = discord.Embed(title = "2048!", description = f"Player: <@!{author_id}>\nScore: {game.score}", colour = discord.Colour.blue())
        await mess.channel.send(embed = game_embed)
        await mess.channel.send(game.game_board)
        while game.game == 1:
            while True:
                await mess.channel.send("Enter the direction in which you would like to swipe ('w' for up, 's' for down, 'a' for left, 'd' for right); Enter 'quit' to quit the game, Enter 'board' to see the current board")
                try:
                    reaction_msg = await bot.wait_for("message", check = lambda m: m.author.id == author_id and m.channel.id == mess.channel.id, timeout = 120.0)
                except asyncio.TimeoutError:
                    await mess.channel.send(f"<@!{author_id}> you took too long to respond to the game has ended")
                    game.game = 0
                    in_game.remove(author_id)
                    break
                else:
                    dir = str(reaction_msg.content).lower()
                    if dir not in dirs.keys():
                        if dir == "quit":
                            await mess.channel.send("We're sorry to see you leave 😢")
                            game.game = 0
                            in_game.remove(author_id)
                            break
                        elif dir == "board":
                            game.string_rows()
                            game_embed = discord.Embed(title = "2048!", description = f"Player: <@!{author_id}>\nScore: {game.score}", colour = discord.Colour.blue())
                            await mess.channel.send(embed = game_embed)
                            await mess.channel.send(game.game_board)
                        else:
                            await mess.channel.send("Invalid direction")
                    else:
                        dir = dirs[dir]
                        break
            if game.game == 1:
                game.swipe(dir)
                game.string_rows()
                game_embed = discord.Embed(title = "2048!", description = f"Player: <@!{author_id}>\nScore: {game.score}", colour = discord.Colour.blue())
                await mess.channel.send(embed = game_embed)
                await mess.channel.send(game.game_board)
                if game.game == 0:
                    await mess.channel.send(f"<@!{author_id}> you won! Your final score is {game.score}")
                    in_game.remove(author_id)
                    break
                game.game_over()
                if game.game == 0:
                    await mess.channel.send(f"<@!{author_id}> the game is over! Your final score is {game.score}")
                    in_game.remove(author_id)
                    break
       
    else:
        await mess.send("You're already in a game!", ephemeral = True)

@bot.slash_command(name = "trivia", description = "Get a random multiple choice trivia question")
async def trivia(mess: discord.Interaction, difficulty: str = discord.SlashOption(name = "difficulty", description = "The difficulty of the question that you will attempt", choices = ["easy", "medium", "hard"], required = False)):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("trivia")
    author_id = mess.user.id
    if author_id not in in_game:
        await mess.send("Done!", ephemeral = True)
        if difficulty is None:
            question_data = requests.get("https://the-trivia-api.com/api/questions?limit=1").json()[0]
        else:
            question_data = requests.get(f"https://the-trivia-api.com/api/questions?limit=1&difficulty={difficulty}").json()[0]
        question = question_data["question"]
        options = question_data["incorrectAnswers"]
        options.append(question_data["correctAnswer"])
        rd.shuffle(options)
        question_embed = discord.Embed(title = "Trivia!", description = f"*Difficulty*: **{question_data['difficulty'].capitalize()}**", colour = discord.Colour.blue())
        question_embed.add_field(name = "Question", value = f"**{question}**", inline = False)
        question_embed.add_field(name = "Options", value = f'''1️⃣ *{str(options[0]).capitalize()}*
2️⃣ *{str(options[1]).capitalize()}*
3️⃣ *{str(options[2]).capitalize()}*
4️⃣ *{str(options[3]).capitalize()}*
''', inline = False)
        question_final = await mess.channel.send(embed = question_embed)
        await question_final.add_reaction("1️⃣")
        await question_final.add_reaction("2️⃣")
        await question_final.add_reaction("3️⃣")
        await question_final.add_reaction("4️⃣")
        try:
            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"] and r.message.id == question_final.id and p.id == author_id, timeout = 120.0)
        except asyncio.TimeoutError:
            await question_final.reply(f"<@!{author_id}> you took too long to respond so the question has been cancelled")
        else:
            t = {"1️⃣": 0, "2️⃣": 1, "3️⃣": 2, "4️⃣": 3}
            if options[t[str(reaction.emoji)]] == question_data["correctAnswer"]:
                await question_final.reply(f"<@!{author_id}> you chose the option `{options[t[str(reaction.emoji)]].capitalize()}` and that is the correct answer!", mention_author = False)
            else:
                await question_final.reply(f"<@!{author_id}> you chose the option `{options[t[str(reaction.emoji)]].capitalize()}` and that is incorrect! The correct answer is `{question_data['correctAnswer'].capitalize()}`", mention_author = False)
    else:
        await mess.send("You're already in a game!", ephemeral = True)

@bot.slash_command(name = "flags", description = "Get a random flag and guess the country")
async def flags(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("flags")
    author_id = mess.user.id
    if author_id not in in_game:
        await mess.send("Done!", ephemeral = True)
        df = pd.read_csv("flag_codes.txt", delimiter = "\t")
        flag_codes = df.to_numpy().tolist()
        real_flag = rd.choice(flag_codes)
        flag_codes.remove(real_flag)
        options = [real_flag]
        for t in range(3):
            option_flag = rd.choice(flag_codes)
            options.append(option_flag)
            flag_codes.remove(option_flag)
        rd.shuffle(options)
        flag_id = str(real_flag[1])
        if len(flag_id) != 3:
            flag_id = "0"*(3-(len(flag_id)))+flag_id
        flag_image = f"https://countryflagsapi.com/png/{flag_id}"
        question_embed = discord.Embed(title = "Flags!", description = "**Which country's flag is shown below?**", colour = discord.Colour.blue())
        question_embed.add_field(name = "Options", value = f'''1️⃣ *{options[0][0]}*
2️⃣ *{options[1][0]}*
3️⃣ *{options[2][0]}*
4️⃣ *{options[3][0]}*
''', inline = False)
        question_embed.set_image(url = flag_image)
        question_final = await mess.channel.send(embed = question_embed)
        await question_final.add_reaction("1️⃣")
        await question_final.add_reaction("2️⃣")
        await question_final.add_reaction("3️⃣")
        await question_final.add_reaction("4️⃣")
        try:
            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"] and r.message.id == question_final.id and p.id == author_id, timeout = 120.0)
        except asyncio.TimeoutError:
            await question_final.reply(f"<@!{author_id}> you took too long to respond so the question has been cancelled")
        else:
            t = {"1️⃣": 0, "2️⃣": 1, "3️⃣": 2, "4️⃣": 3}
            if options[t[str(reaction.emoji)]][0] == real_flag[0]:
                await question_final.reply(f"<@!{author_id}> you chose the option `{options[t[str(reaction.emoji)]][0]}` and that is the correct answer!", mention_author = False)
            else:
                await question_final.reply(f"<@!{author_id}> you chose the option `{options[t[str(reaction.emoji)]][0]}` and that is incorrect! The correct answer is `{real_flag[0]}`", mention_author = False)

    else:
        await mess.send("You're already in a game!", ephemeral = True)

@bot.slash_command(name = "other", description = "List all the other games on the bot")
async def other(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    await mess.send("Done!", ephemeral = True)

    change_stats("other")
    page = 1
    while True:
        if page == 1:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 1/5")
            other_games.add_field(name = "Connect 4", value = '''
Connect 4 or Four-in-a-row is now here on the minesweeper bot! The main aim of this game is to get 4 of your tokens in a line: horizontally, vertically, or diagonally. Drop your tokens in the columns to place them!

**Complete rules**: https://www.ultraboardgames.com/connect4/game-rules.php
**Commands and aliases**: `;connect4`, `;c4` 
''', inline = False)
            other_games.add_field(name = "Othello", value = '''
Othello is now here on the minesweeper bot! There are 2 players who play this game, and they are given one of two colours: black and white. Black goes first. The rules are as follows:
1. You can only place your coin in a position that 'outflanks' at least one of your opponent's coins. Outflanking means that the coin you place and another one of your placed coins must be at the two ends of your opponent's coins.
2. After placing the coin, any of the opponent's coins that are outflanked by the coin you placed and another one of your coins, is turned over.
3. If you cannot place a coin anywhere, the bot will automatically pass on the turn to the other player.
4. The game ends when the board is full, or nobody else can place a coin in a valid position. Whoever has more of their coins on the board at this point wins!

**Complete rules**: https://www.ultraboardgames.com/othello/game-rules.php
**Commands and aliases**: `;othello`, `;oto`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "▶" and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 2
                await o_games.delete()

        elif page == 2:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 2/5")
            other_games.add_field(name = "Mastermind", value = '''
Mastermind is now here on the minesweeper bot! 2 players play this game and they are give one of two roles - the code setter, or the code guesser. The code setter will make a code following a prompt from the bot in their DMs. The code will consist of 4 colours, which can be repeated. The code guesser will then have to guess the code in a maximum of 8 turns. Following each turn, the code guesser will see how close their guess is to the actual word. This will be seen at the side of the grid in the following form:
✅ - Correct colour in the correct position
☑️ - Correct colour in the wrong position
❌ - Wrong colour
These icons will be given for each of the 4 guessed colour positions, but these icons will be given at random - they will not correspond to any particular position. Deduce the correct code to win the game!

**Complete rules**: https://www.ultraboardgames.com/mastermind/game-rules.php
**Commands and aliases**: `;mastermind`, `;mm` 
''', inline = False)
            other_games.add_field(name = "Yahtzee", value = '''
Yahtzee is now here on the minesweeper bot! This game is played with 2 players who play completely indivual games. The game requires the players to roll 5 dice in a total of 3 rolls. After each roll, the players can choose to hold a few of the dice to prevent them from being rolled the next time. This is essential in completing the cards that the players have. The cards have different fields that have to be filled: *Aces, Twos, Threes, Fours, Fives, and Sixes* in the Upper section, and *3 of a kind, 4 of a kind, Full house, Small straight, Large straight, Yahtzee, and Chance* in the Lower section. Each of these fields have specific criteria that have to be met to place your points in the fields. These criteria can be found in the link given below. Complete your cards to obtain a final score. The player with the highest final score wins the game!

**Complete rules**: https://www.ultraboardgames.com/yahtzee/game-rules.php
**Commands and aliases**: `;yahtzee`, `;yz`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("◀")
            await o_games.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                if str(reaction.emoji) == "◀":
                    page = 1
                else:
                    page = 3
                await o_games.delete()
        
        elif page == 3:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 3/5")
            other_games.add_field(name = "Battleship", value = '''
Battleship is now here on the minesweeper bot! An intense two-player game, battleship requires players to destroy each others ships fastest. Based on the theme of naval warfare, the players will first have to place their ships in strategic positions to avoid getting blasted by the other player's cannons. Turn by turn, the players will then enter coordinates as they try to locate and destroy each of the opponent's 5 ships. The first person to destroy all of the other person's ships wins! Other people can follow the game by using the `;live` command in the channel the game was started in!

**Complete rules**: https://www.ultraboardgames.com/battleship/game-rules.php
**Commands and aliases**: `;battleship`, `;bs`, `;live`
''', inline = False)
            other_games.add_field(name = "Hangman", value = '''
Hangman is now here on the minesweeper bot! An old classic, hangman is a game where one person decides on a word or phrase and then draws blanks corresponding to each letter of the word/phrase. The vowels may or may not be revealed, but in this version we will reveal the vowels beforehand. The other player must then guess individual letters to fill in the blanks. For every incorrect guess, a body part of the man will be revealed. If the player successfully guesses all the letters before the man is completely hanged, he will win the game!

**Complete rules**: https://www.ultraboardgames.com/hangman/game-rules.php
**Commands and aliases**: `;hangman`, `;hm`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("◀")
            await o_games.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                if str(reaction.emoji) == "◀":
                    page = 2
                else:
                    page = 4
                await o_games.delete()
    
        elif page == 4:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 4/5")
            other_games.add_field(name = "Uno", value = '''
Uno is now here on the minesweeper bot! Players play cards that match the top card by face value or by colour. You can also play special cards to hamper the progress of the other players! Before you play your second last card, you must say `uno` in the DM and then play the card. If you play the card without saying `uno`, someone else can say `caught` in the game channel within 10 seconds and then you will have to draw 4 cards. However, even after playing your second last card, you can say `uno` before someone else catches you and then you would not be subject to the 4 card penalty. If neither `uno` nor `caught` is said within 10 seconds, the 4 card penalty will not be applicable. Whoever finishes all their cards first wins the game! Everyone plays uno with different rules so it is recommended that you check out the rules in the link below as those are the rules used with this bot.

**Complete rules**: https://www.ultraboardgames.com/uno/game-rules.php
**Commands and aliases**: `;uno`, `;live`
''', inline = False)
            other_games.add_field(name = "Wordle", value = '''
Wordle is now here on the minesweeper bot! Given a hidden 5 letter word, the player must try to guess the word by making their own valid word guesses. The following colours indicate the status of a letter in the guessed word:
🟩 - Correct letter in the correct position
🟨 - Correct letter in the wrong position
🟥 - Wrong letter
These colours will be in order, so you will know exactly which letter corresponds to which colour. Using these colours, deduce the hidden word to win the game! Wordle on the minesweeper comes with a little twist - it's a two player game! One player will give a word that the other player has to guess!

**Complete rules**: https://www.nytimes.com/games/wordle/index.html
**Commands and aliases**: `;wordle`, `;wd`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("◀")
            await o_games.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["◀", "▶"] and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                if str(reaction.emoji) == "◀":
                    page = 3
                else:
                    page = 5
                await o_games.delete()

        elif page == 5:
            other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
            other_games.set_footer(text = "Other Games Page 5/5")
            other_games.add_field(name = "2048", value = '''
2048 is now here on the minesweeper bot! A highly addictive and fun game, 2048 is based on moving tiles and when tiles having the same number on them bump into each other, they will add up. If you manage to add up to 2048, you win the game! To slide the tiles, you will have to use the WASD keys as arrow keys. With every swipe, all tiles on the board move in that direction. You can also look at an incremental score counter that comes along with the board!

**Commands and aliases**: `;2048`, `;tzfe`
''', inline = False)
            other_games.add_field(name = "Trivia", value = '''
Trivia is now here on the minesweeper bot! In the mood for some fun trivia? Use the trivia command to get a random multiple choice trivia question for you to answer! Try out as many questions as you want - there are no limits! If you want to personalize the question furthur, you can also choose the difficulty for the question that you receive. Are you a flag enthusiast? We also have a flag quiz with the bot! Try to guess as many flags as you can!

**Commands and aliases**: `;trivia`, `;quiz`, `;flags`
''', inline = False)
            o_games = await mess.channel.send(embed = other_games)
            await o_games.add_reaction("◀")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "◀" and p.id != bot.user.id and r.message.id == o_games.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 4
                await o_games.delete()

@bot.slash_command(name = "invite", description = "Send an invite link for the bot")
async def invite(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("invite")
    invite = discord.Embed(title = "Invite me to your server!", description = "Use this link to invite me: https://dsc.gg/minesweeper-bot", colour = discord.Colour.blue())
    await mess.send(embed = invite)

@bot.slash_command(name = "support", description = "Send an invite link for the support server")
async def support(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("support")
    support = discord.Embed(title = "Join the official minesweeper bot support server!", description = "Use this link to join the server: https://dsc.gg/minesweeper", colour = discord.Colour.blue())
    await mess.send(embed = support)

@bot.slash_command(name = "vote", description = "Send all the voting links for the bot")
async def vote(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    change_stats("vote")
    vote = discord.Embed(title = "Vote for me!", description = '''Enjoyed using the bot?
Vote for us on `top.gg`: https://top.gg/bot/902498109270134794/vote
Vote for us on `discordbotlist.com`: https://discordbotlist.com/bots/minesweeper-bot/upvote
Vote for us on `discords.com`: https://discords.com/bots/bot/902498109270134794/vote
Vote for us on `bots.discordlabs.org`: https://bots.discordlabs.org/bot/902498109270134794?vote''', colour = discord.Colour.blue())
    await mess.send(embed = vote)

@bot.slash_command(name = "website", description = "Send the link for the website")
async def website(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return
    
    change_stats("website")
    website = discord.Embed(title = "Visit our website!", description = "Use this link to view our website: https://minesweeper-bot.carrd.co", colour = discord.Colour.blue())
    await mess.send(embed = website)

@bot.slash_command(name = "strength", description = "A private command to view the number of servers the bot is in", guild_ids = [852578295967121438])
async def strength(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)) or not(mess.user.id == 706855396828250153):
        return

    await mess.send(f"I'm in {len(bot.guilds)} servers!")
    bot_count = bot.get_channel(948144061305479198)
    await bot_count.edit(name = f"Servers: {len(bot.guilds)}")
    await mess.send("Updated server count in <#948144061305479198>", mention_author = False)

@bot.slash_command(name = "count", description = "A private command to view the number of minesweeper users", guild_ids = [852578295967121438])
async def count(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)) or not(mess.user.id == 706855396828250153):
        return
    
    await mess.send(f"We have {member_count()} users!")

@bot.slash_command(name = "statistics", description = "A private command to view the command statistics of the bot", guild_ids = [852578295967121438])
async def stats(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)) or not(mess.user.id == 706855396828250153):
        return

    commands_data = get_stats()
    commands = list(commands_data.keys())
    values = list(commands_data.values())

    fig = plt.figure(figsize = (16, 9))
    plt.barh(commands, values, color = "blue")
    plt.ylabel("Commands")
    plt.xlabel("Number of calls")
    plt.title("Commands data")
    plt.savefig("commands_graph.png")
    await mess.send("Commands graph", file = discord.File("commands_graph.png"))

@bot.slash_command(name = "help", description = "View the help page of the bot")
async def help(mess: discord.Interaction):
    global in_game
    author = mess.user.name
    if mess.user == bot.user or mess.user.bot or not(isinstance(mess.channel, discord.TextChannel) or isinstance(mess.channel, discord.DMChannel) or isinstance(mess.channel, discord.Thread)):
        return

    await mess.send("Done!", ephemeral = True)
    
    change_stats("help")
    page = 1
    while True:
        if page == 1:
            help_embed = discord.Embed(title = "A complete guide on how to use the Minesweeper Bot!", description = "This bot allows you to play a collection of some extremely entertaining games on discord! The prefix for the bot is `;`.", colour = discord.Colour.blue())
            help_embed.set_footer(text = "Help Page 1/2")
            help_embed.add_field(name = "Rules: ", value = 
            '''The basic rules of minesweeper are:
1. Behind each circle is either a bomb, a number, or nothing.
2. If you hit a bomb you lose the game.
3. The number signifies how many bombs are there behind the circles adjacent to it (diagonals included).
4. If you know the location of a bomb, you can place a flag over there for reference.
5. Open up all the circles without the bombs to win the game!''', inline = False)
            help_embed.add_field(name = "The Nexus:", value = "[Invite Me](https://discord.com/oauth2/authorize?client_id=902498109270134794&permissions=274878188608&scope=bot%20applications.commands) · [Support Server](https://discord.gg/3jCG74D3RK) · [Vote for Us!](https://top.gg/bot/902498109270134794/vote) · [GitHub](https://github.com/vsmart-06/minesweeper-hosting) · [Privacy Policy](https://gist.github.com/vsmart-06/cc24bd805d50c519853c43adafb993d7) · [Terms of Service](https://gist.github.com/vsmart-06/f68961c5515cb50025db1a34f4e2a1a4) · [Website](https://minesweeper-bot.carrd.co)", inline = False)
            help = await mess.channel.send(embed = help_embed)
            await help.add_reaction("▶")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "▶" and p.id != bot.user.id and r.message.id == help.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 2
                await help.delete()

        elif page == 2:
            help_embed = discord.Embed(title = "A complete guide on how to use the Minesweeper Bot!", description = "This bot allows you to play a collection of some extremely entertaining games on discord! The prefix for the bot is `;`.", colour = discord.Colour.blue())
            help_embed.set_footer(text = "Help Page 2/2")
            help_embed.add_field(name = "Commands: ", value = 
'''
`;help`: Open the guide.
`;minesweeper`/`;ms`: Start a new minesweeper game in an 8x8 grid with 8 bombs. Tag someone else to play a game against them!
`;minesweepercustom`/`;mscustom`: Start a custom minesweeper game.
`;tournament`: Start a minesweeper tournament in your server!
`;leaderboard`/`;lb`: View the global leaderboard.
`;serverleaderboard`/`;serverlb`: View the server leaderboard.
`;profile`: View your personal minesweeper bot profile. Tag someone else to view their profile as well!
*`;profile settings private/public`: Control who can view your profile. By default it is set to public.
*`;theme settings light/dark`: Change the theme the bot uses for your games. By default it is set to dark.
*`;delete`: Delete all your data on the minesweeper bot.
`;other`: **View other games that can be played on the bot!**
`;invite`: Get a link to invite this bot to a server.
`;support`: Get a link to join the official minesweeper bot support server.
`;website`: Get a link to our website.
`;vote`: Vote for the bot!
''', inline = False)
            help_embed.add_field(name = "Note:", value = "*: These commands, despite giving a confirmation message, will not have any effect unless the user plays at least 1 game of normal minesweeper on the bot.", inline = False)
            help_embed.add_field(name = "Slash Commands", value = "Slash commands are also available with the minesweeper bot! Type `/` and click on the minesweeper bot's icon to view all of its slash commands! If you cannot see them, you may have to re-invite the bot to your server.")
            help_embed.add_field(name = "The Nexus:", value = "[Invite Me](https://discord.com/oauth2/authorize?client_id=902498109270134794&permissions=274878188608&scope=bot%20applications.commands) · [Support Server](https://discord.gg/3jCG74D3RK) · [Vote for Us!](https://top.gg/bot/902498109270134794/vote) · [GitHub](https://github.com/vsmart-06/minesweeper-hosting) · [Privacy Policy](https://gist.github.com/vsmart-06/cc24bd805d50c519853c43adafb993d7) · [Terms of Service](https://gist.github.com/vsmart-06/f68961c5515cb50025db1a34f4e2a1a4) · [Website](https://minesweeper-bot.carrd.co)", inline = False)
            help = await mess.channel.send(embed = help_embed)
            await help.add_reaction("◀")
            try:
                reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "◀" and p.id != bot.user.id and r.message.id == help.id, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                page = 1
                await help.delete()

bot.run(token)