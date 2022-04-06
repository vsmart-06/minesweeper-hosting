import discord
import discord.ext.commands
from minesweeper_class import minesweeper
from connect4_class import connect4
from othello_class import othello
from mastermind_class import mastermind
from records import global_leaderboard, server_leaderboard, profile, privacy_change, delete_record, theme_change, get_theme
import os
import asyncio
import random as rd
from discord.utils import get
import topgg
import discordspy
import statcord

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = discord.Client(intents = intents)
token = os.getenv("DISCORD_TOKEN")
topgg_token = os.getenv("TOPGG_TOKEN")
discords_token = os.getenv("DISCORDS_TOKEN")
statcord_token = os.getenv("STATCORD_TOKEN")
topgg_client = topgg.DBLClient(bot, topgg_token, autopost = True)
discords_client = discordspy.Client(bot, discords_token, post = discordspy.Post.intervals(0, 30, 0))
statcord_client = statcord.Client(bot, statcord_token)
statcord_client.start_loop()

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Game(name = "Minesweeper | ;help"))
    print("Ready for takeoff!")
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("I'm in "+str(len(bot.guilds))+" servers!")
    bot_count = bot.get_channel(948144061305479198)
    await bot_count.edit(name = f"Servers: {len(bot.guilds)}")

@bot.event
async def on_guild_join(guild):
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("New server: "+str(guild))
    bot_count = bot.get_channel(948144061305479198)
    await bot_count.edit(name = f"Servers: {len(bot.guilds)}")

@bot.event
async def on_guild_remove(guild):
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("Removed from: "+str(guild))
    bot_count = bot.get_channel(948144061305479198)
    await bot_count.edit(name = f"Servers: {len(bot.guilds)}")

@bot.event
async def on_message(mess):
    msg = mess.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot:
        return

    if msg == ";minesweeper" or msg == ";ms":
        author_id = mess.author.id
        play = minesweeper(8, 8, 8, author_id, "no", get_theme(author_id))
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
        tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
        await mess.channel.send(embed = tournament_invite)

    elif msg == ";minesweeper custom" or msg == ";mscustom":
        author_id = mess.author.id
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
        tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
        await mess.channel.send(embed = tournament_invite)
    
    elif msg.startswith(";minesweeper") or msg.startswith(";ms"):
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
                    if opponent in members and opponent != me:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of minesweeper! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
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
                                    tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                    await mess.channel.send(embed = tournament_invite)
                                elif player_2.game_over == 1:
                                    await mess.channel.send(player_2.end_msg)
                                    await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                                    tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                    await mess.channel.send(embed = tournament_invite)
                                elif player_1.game_won == 1:
                                    await mess.channel.send(player_1.end_msg)
                                    await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                                    tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                    await mess.channel.send(embed = tournament_invite)
                                elif player_2.game_won == 1:
                                    await mess.channel.send(player_2.end_msg)
                                    await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                                    tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                    await mess.channel.send(embed = tournament_invite)

                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                await mess.channel.send(embed = tournament_invite)

                    else:
                        if opponent != me:
                            dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                            await mess.channel.send(embed = dual_game)
                            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                            await mess.channel.send(embed = tournament_invite)
                except discord.errors.NotFound:
                    dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                    await mess.channel.send(embed = dual_game)
                    tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                    await mess.channel.send(embed = tournament_invite)
            else:
                dual_game = discord.Embed(title = "Invalid syntax!", description = "The minesweeper syntax is invalid! The correct syntax is: ;minesweeper/;ms @user", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                await mess.channel.send(embed = tournament_invite)
        else:
            await mess.channel.send("You cant play a match against someone in a DM!")
            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)

    elif msg == ";tournament":
        if not(isinstance(mess.channel, discord.DMChannel)):
            host_id = mess.author.id
            thumb = bot.get_emoji(935120796358152212)
            check = bot.get_emoji(935455988516028486)
            winner = bot.get_emoji(935794255543275541)
            yay = bot.get_emoji(951716865049247855)
            tourney_members = [host_id]
            tourney_init_embed = discord.Embed(title = "Tournament started!", description = f"<@!{host_id}> started a tournament! React with {thumb} below or type `;join` to join! Remove your reaction or type `;leave` to leave. <@!{host_id}> react with {check} or type `;start` to start the tournament!", colour = discord.Colour.blue())
            tourney_init = await mess.channel.send(embed = tourney_init_embed)
            await tourney_init.add_reaction(str(thumb))
            await tourney_init.add_reaction(str(check))
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
                            await mess.channel.send(f"<@!{user.id}> has joined the tournament {yay}")
                            tourney_members.append(user.id)
                        elif reaction_e == str(check) and user.id == host_id:
                            break
                    elif action == "rrem":
                        reaction, user = result
                        reaction_e = str(reaction.emoji)
                        if reaction_e == str(thumb) and user.id != host_id and user.id in tourney_members:
                            await mess.channel.send(f"<@!{user.id}> has left the tournament 😢")
                            tourney_members.remove(user.id)
                    elif action == "msgd":
                        jl_msg = str(result.content)
                        user = result.author
                        if jl_msg == ";join" and user.id not in tourney_members and user.id != host_id:
                            await mess.channel.send(f"<@!{user.id}> has joined the tournament {yay}")
                            tourney_members.append(user.id)
                        elif jl_msg == ";leave" and user.id in tourney_members and user.id != host_id:
                            await mess.channel.send(f"<@!{user.id}> has left the tournament 😢")
                            tourney_members.remove(user.id)
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
                            await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                        elif player_2.game_over == 1:
                            await mess.channel.send(player_2.end_msg)
                            tourney_members.remove(opp_id)
                            await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                        elif player_1.game_won == 1:
                            await mess.channel.send(player_1.end_msg)
                            tourney_members.remove(opp_id)
                            await mess.channel.send("<@!"+str(a_id)+"> is the winner!")
                        elif player_2.game_won == 1:
                            await mess.channel.send(player_2.end_msg)
                            tourney_members.remove(a_id)
                            await mess.channel.send("<@!"+str(opp_id)+"> is the winner!")
                        match += 1
                        await asyncio.sleep(5)
                    
                    else:
                        match = 1
                        await asyncio.sleep(5)
                round += 1
                match = 1
            await mess.channel.send(f"<@!{tourney_members[0]}> is the winner of the tournament! {winner}")
            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)

        else:
            await mess.channel.send("You can't start a tournament in a DM!")
            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)

    elif msg == ";leaderboard" or msg == ";lb":
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

        tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
        await mess.channel.send(embed = tournament_invite)

    elif msg == ";server leaderboard" or msg == ";serverlb":
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

            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)
        else:
            await mess.channel.send("This is not a server!")
            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)

    elif msg.startswith(";profile"):
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
            prof = profile(int(user_id))
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
                        user_profile.set_thumbnail(url = u.avatar_url)
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
            user_profile = discord.Embed(title = "Profile settings changed!", description = "Your profile is now "+priv+"!", color = discord.Color.blue())
        else:
            user_profile = discord.Embed(title = "Invalid syntax!", description = "The profile syntax is invalid! The correct syntax is: ;profile @user", color = discord.Color.blue())
        await mess.channel.send(embed=user_profile)
        tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
        await mess.channel.send(embed = tournament_invite)

    elif msg == ";delete":
        aut_id = mess.author.id
        delete_data = await mess.channel.send("Are you sure you want to delete all of your data on this bot? React to confirm!")
        await delete_data.add_reaction("✅")
        await delete_data.add_reaction("❌")
        try:
            reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) in ["✅", "❌"] and p.id == aut_id and r.message.id == delete_data.id, timeout = 30.0)
        except asyncio.TimeoutError:
            record_d = discord.Embed(title = "Operation cancelled!", description = "You took too long to respond so the data deletion has been cancelled!", colour = discord.Colour.blue())
            await mess.channel.send(embed = record_d)
            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)
        else:
            if str(reaction.emoji) == "✅":
                delete_record(aut_id)
                record_d = discord.Embed(title = "Data deleted", description = "All of your stats with the bot have been deleted. Play again to create new stats.", colour = discord.Colour.blue())
            else:
                record_d = discord.Embed(title = "Operation cancelled!", description = "Data deletion has been cancelled!", colour = discord.Colour.blue())
            await mess.channel.send(embed = record_d)
            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)

    elif msg.startswith(";theme settings "):
        theme = msg.replace(";theme settings ", "")
        aut_id = mess.author.id
        if theme in ["light", "dark"]:
            theme_change(aut_id, theme)
            theme_settings = discord.Embed(title = "Theme changed successfully!", description = f"Your game theme has been successfully changed to {theme} mode!", color = discord.Color.blue())
        else:
            theme_settings = discord.Embed(title = "Invalid syntax!", description = "The theme settings syntax is invalid! The correct syntax is: ;theme settings light/dark", color = discord.Color.blue())
        await mess.channel.send(embed = theme_settings)

    elif msg.startswith(";connect4") or msg.startswith(";c4"):
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
                    if opponent in members and opponent != me:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of connect 4! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
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
                                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                await mess.channel.send(embed = tournament_invite)
                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                await mess.channel.send(embed = tournament_invite)

                    else:
                        if opponent != me:
                            dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                            await mess.channel.send(embed = dual_game)
                            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                            await mess.channel.send(embed = tournament_invite)
                except discord.errors.NotFound:
                    dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                    await mess.channel.send(embed = dual_game)
                    tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                    await mess.channel.send(embed = tournament_invite)
            else:
                dual_game = discord.Embed(title = "Invalid syntax!", description = "The connect 4 syntax is invalid! The correct syntax is: ;connect4/;c4 @user", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                await mess.channel.send(embed = tournament_invite)
        else:
            await mess.channel.send("You cant play a match against someone in a DM!")
            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)

    elif msg.startswith(";othello") or msg.startswith(";oto"):
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
                    if opponent in members and opponent != me:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of othello! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
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

                                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                await mess.channel.send(embed = tournament_invite)
                                
                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                await mess.channel.send(embed = tournament_invite)

                    else:
                        if opponent != me:
                            dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                            await mess.channel.send(embed = dual_game)
                            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                            await mess.channel.send(embed = tournament_invite)
                except discord.errors.NotFound:
                    dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                    await mess.channel.send(embed = dual_game)
                    tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                    await mess.channel.send(embed = tournament_invite)
            else:
                dual_game = discord.Embed(title = "Invalid syntax!", description = "The othello syntax is invalid! The correct syntax is: ;othello/;oto @user", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                await mess.channel.send(embed = tournament_invite)
        else:
            await mess.channel.send("You cant play a match against someone in a DM!")
            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)

    elif msg.startswith(";mastermind") or msg.startswith(";mm"):
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
                    if opponent in members and opponent != me:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of mastermind! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
                        try:
                            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 120.0)
                        except asyncio.TimeoutError:
                            await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                        else:
                            if str(reaction.emoji) == "✅":
                                p1_id = rd.choice([a_id, opp_id])
                                if p1_id == a_id:
                                    p2_id = opp_id
                                else:
                                    p2_id = a_id
                                await mess.channel.send(f"<@!{p1_id}> check your DMs for a message from me to enter your code!")
                                game = mastermind(p1_id, p2_id, get_theme(p2_id))
                                p1 = await bot.fetch_user(p1_id)
                                while True:
                                    await p1.send('''Enter the hidden code with the following numbers:
🔴 - 1
🟠 - 2
🟡 - 3
🟢 - 4
🔵 - 5
🟣 - 6
🟤 - 7
Ex: 1 2 3 4
''')
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
                                            await channel.send('''Enter your guess with the following numbers:
    🔴 - 1
    🟠 - 2
    🟡 - 3
    🟢 - 4
    🔵 - 5
    🟣 - 6
    🟤 - 7
    Ex: 1 2 3 4

    Type 'board' to view the current board; type 'quit' to quit the game
    ''')
                                            try:
                                                gcode_msg = await bot.wait_for("message", check = lambda m: m.author.id == p2_id and m.channel == channel, timeout = 120.0)
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
                                        game.guess(nums)
                                    if game.turns != None:
                                        game.string_rows()
                                        grid_embed = discord.Embed(title = "Mastermind!", description = game.grid, colour = discord.Colour.blue())
                                        await channel.send(embed = grid_embed)
                                        if game.turns == 8:
                                            game.winner = game.p1
                                        await channel.send(f"<@!{game.winner}> is the winner!")

                            else:
                                await mess.channel.send(f"<@!{a_id}> your challenge was rejected")
                                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                                await mess.channel.send(embed = tournament_invite)

                    else:
                        if opponent != me:
                            dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if they're not in the server!", color = discord.Color.blue())
                            await mess.channel.send(embed = dual_game)
                            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                            await mess.channel.send(embed = tournament_invite)
                except discord.errors.NotFound:
                    dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                    await mess.channel.send(embed = dual_game)
                    tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                    await mess.channel.send(embed = tournament_invite)
            else:
                dual_game = discord.Embed(title = "Invalid syntax!", description = "The mastermind syntax is invalid! The correct syntax is: ;mastermind/;mm @user", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
                tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
                await mess.channel.send(embed = tournament_invite)
        else:
            await mess.channel.send("You cant play a match against someone in a DM!")
            tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
            await mess.channel.send(embed = tournament_invite)

    elif msg == ";other":
        other_games = discord.Embed(title = "Other games on the bot!", description = "A list of all other games that can be played on the bot and their respective commands", colour = discord.Colour.blue())
        other_games.add_field(name = "Connect 4", value = '''
Connect 4 or Four-in-a-row is now here on the minesweeper bot! The main aim of this game is to get 4 of your tokens in a line: horizontally, vertically, or diagonally. Drop your tokens in the columns to place them!

**Commands and aliases**: `;connect4`, `;c4` 
''', inline = False)
        other_games.add_field(name = "Othello", value = '''
Othello is now here on the minesweeper bot! There are 2 players who play this game, and they are given one of two colours: black and white. Black goes first. The rules are as follows:
1. You can only place your coin in a position that 'outflanks' at least one of your opponent's coins. Outflanking means that the coin you place and another one of your placed coins must be at the two ends of your opponent's coins.
2. After placing the coin, any of the opponent's coins that are outflanked by the coin you placed and another one of your coins, is turned over.
3. If you cannot place a coin anywhere, the bot will automatically pass on the turn to the other player.
4. The game ends when the board is full, or nobody else can place a coin in a valid position. Whoever has more of their coins on the board at this point wins!

**Commands and aliases**: `;othello`, `;oto`
''', inline = False)
        other_games.add_field(name = "Mastermind", value = '''
Mastermind is now here on the minesweeper bot! 2 players play this game and they are give one of two roles - the code setter, or the code guesser. The code setter will make a code following a prompt from the bot in their DMs. The code will consist of 4 colours, which can be repeated. The code guesser will then have to guess the code in a maximum of 8 turns. Following each turn, the code guesser will see how close their guess is to the actual word. This will be seen at the side of the grid in the following form:
✅ - Correct colour in the correct position
☑️ - Correct colour in the wrong position
❌ - Wrong colour
These icons will be given for each of the 4 guessed colour positions, but these icons will be given at random - they will not correspond to any particular position. Deduce the correct code to win the game!

**Commands and aliases**: `;mastermind`, `;mm` 
''', inline = False)
        await mess.channel.send(embed = other_games)
        

    elif msg == ";register" and mess.channel.id == 936949262791606272:
        yay = bot.get_emoji(951716865049247855)
        t_mem_id = mess.author.id
        t_mem = mess.author
        await mess.channel.send(f"<@!{t_mem_id}> has joined the tournament {yay}")
        c_guild = bot.get_guild(915952924172091433)
        role = get(c_guild.roles, name="Tournament participants")
        await t_mem.add_roles(role)

    elif msg == ";invite":
        invite = discord.Embed(title = "Invite me to your server!", description = "Use this link to invite me: [https://discord.com/bot/minesweeper](https://discord.com/api/oauth2/authorize?client_id=902498109270134794&permissions=274878188608&scope=bot)", colour = discord.Colour.blue())
        await mess.channel.send(embed = invite)
        tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
        await mess.channel.send(embed = tournament_invite)
    
    elif msg == ";support":
        support = discord.Embed(title = "Join the official minesweeper bot support server!", description = "Use this link to join the server: [https://discord.gg/minesweeper](https://discord.gg/3jCG74D3RK)", colour = discord.Colour.blue())
        await mess.channel.send(embed = support)
        tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
        await mess.channel.send(embed = tournament_invite)
    
    elif msg == ";vote":
        vote = discord.Embed(title = "Vote for me!", description = '''Enjoyed using the bot?
Vote for us on `top.gg`: https://top.gg/bot/902498109270134794/vote
Vote for us on `discordbotlist.com`: https://discordbotlist.com/bots/minesweeper-bot/upvote
Vote for us on `discords.com`: https://discords.com/bots/bot/902498109270134794/vote
Vote for us on `bots.discordlabs.org`: https://bots.discordlabs.org/bot/902498109270134794?vote''', colour = discord.Colour.blue())
        await mess.channel.send(embed = vote)
        tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
        await mess.channel.send(embed = tournament_invite)
    
    elif msg == ";strength" and mess.author.id == 706855396828250153:
        await mess.channel.send(f"I'm in {len(bot.guilds)} servers!")
        bot_count = bot.get_channel(948144061305479198)
        await bot_count.edit(name = f"Servers: {len(bot.guilds)}")
        await mess.channel.send("Updated server count in <#948144061305479198>")
    
    elif msg == ";help":
        page = 1
        while True:
            if page == 1:
                help_embed = discord.Embed(title = "A complete guide on how to use the Minesweeper Bot!", description = "This bot allows you to play minesweeper on discord! The prefix for the bot is `;`.", colour = discord.Colour.blue())
                help_embed.add_field(name = "Rules: ", value = 
                '''The basic rules of minesweeper are:
1. Behind each circle is either a bomb, a number, or nothing.
2. If you hit a bomb you lose the game.
3. The number signifies how many bombs are there behind the circles adjacent to it (diagonals included).
4. If you know the location of a bomb, you can place a flag over there for reference.
5. Open up all the circles without the bombs to win the game!''', inline = False)
                help_embed.add_field(name = "The Nexus:", value = "[Invite Me](https://discord.com/api/oauth2/authorize?client_id=902498109270134794&permissions=274878188608&scope=bot) · [Support Server](https://discord.gg/3jCG74D3RK) · [Vote for Us!](https://top.gg/bot/902498109270134794/vote)", inline = False)
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
                help_embed = discord.Embed(title = "A complete guide on how to use the Minesweeper Bot!", description = "This bot allows you to play minesweeper on discord! The prefix for the bot is `;`.", colour = discord.Colour.blue())
                help_embed.add_field(name = "Commands: ", value = 
'''
`;help`: Open the guide.
`;minesweeper`/`;ms`: Start a new minesweeper game in an 8x8 grid with 8 bombs. Tag someone in your server to play a game against them!
`;minesweeper custom`/`;mscustom`: Start a custom minesweeper game.
`;tournament`: Start a minesweeper tournament in your server!
`;leaderboard`/`;lb`: View the global leaderboard.
`;server leaderboard`/`;serverlb`: View the server leaderboard.
`;profile`: View your personal minesweeper bot profile. Tag someone else to view their profile as well!
*`;profile settings private/public`: Control who can view your profile. By default it is set to public.
*`;theme settings light/dark`: Change the theme the bot uses for your games. By default it is set to dark.
*`;delete`: Delete all your data on the minesweeper bot.
`;other`: View other games that can be played on the bot!
`;invite`: Get a link to invite this bot to a server.
`;support`: Get a link to join the official minesweeper bot support server.
`;vote`: Vote for the bot!
''', inline = False)
                help_embed.add_field(name = "Note:", value = "*: These commands despite giving a confirmation message will not have any effect unless the user plays at least 1 game of normal minesweeper on the bot.", inline = False)
                help_embed.add_field(name = "The Nexus:", value = "[Invite Me](https://discord.com/api/oauth2/authorize?client_id=902498109270134794&permissions=274878188608&scope=bot) · [Support Server](https://discord.gg/3jCG74D3RK) · [Vote for Us!](https://top.gg/bot/902498109270134794/vote)", inline = False)
                help = await mess.channel.send(embed = help_embed)
                await help.add_reaction("◀")
                try:
                    reaction, user = await bot.wait_for("reaction_add", check=lambda r, p: str(r.emoji) == "◀" and p.id != bot.user.id and r.message.id == help.id, timeout = 30.0)
                except asyncio.TimeoutError:
                    break
                else:
                    page = 1
                    await help.delete()

        tournament_invite = discord.Embed(title = "REGISTRATIONS FOR THE MINESWEEPER SUPER LEAGUE HAVE BEGUN 🥳", description = '''
Huge prizes for the winners - top 3 players can avail amazing rewards:
🥇 1st place - 10M DMC (Dank Memer Coins)
🥈 2nd place - 7M DMC
🥉 3rd place - 3M DMC

Join our [support server](https://discord.gg/3jCG74D3RK) to register for the tournament and play the matches!''', colour = discord.Color.blue())
        await mess.channel.send(embed = tournament_invite)

bot.run(token)