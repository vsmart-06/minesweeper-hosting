import discord
import discord.ext.commands
from minesweeper_class import minesweeper
from records import global_leaderboard, server_leaderboard, profile, privacy_change, delete_record
import os
import asyncio
import random as rd
from discord.utils import get

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = discord.Client(intents = intents)
token = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = ";help"))
    print("Ready for takeoff!")
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("I'm in "+str(len(bot.guilds))+" servers!")

@bot.event
async def on_guild_join(guild):
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("New server: "+str(guild))

@bot.event
async def on_message(mess):
    msg = mess.content.lower()
    author = mess.author.name
    if mess.author == bot.user or mess.author.bot:
        return

    if msg == ";minesweeper" or msg == ";ms":
        author_id = mess.author.id
        play = minesweeper(8, 8, 8, author_id, "no")
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

            play = minesweeper(num_rows, num_cols, num_bombs, author_id, "no")
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
                    if opponent in members:
                        want_play_embed = discord.Embed(title = "React to play!", description = f"<@!{opp_id}>, <@!{a_id}> has challenged you to a game of minesweeper! React with the emojis below to accept or decline", colour = discord.Colour.blue())
                        want_play = await mess.channel.send(embed = want_play_embed)
                        await want_play.add_reaction("✅")
                        await want_play.add_reaction("❌")
                        try:
                            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == opp_id and str(r.emoji) in ["✅", "❌"] and r.message.id == want_play.id, timeout = 30.0)
                        except asyncio.TimeoutError:
                            await mess.channel.send(f"<@!{a_id}> your challenge has not been accepted")
                        else:
                            if str(reaction.emoji) == "✅":
                                player_1 = minesweeper(8, 8, 8, a_id, "yes")
                                player_2 = minesweeper(8, 8, 8, opp_id, "yes")
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

                    else:
                        dual_game = discord.Embed(title = "User not in server!", description = "You cannot play against this user if he's not in the server!", color = discord.Color.blue())
                        await mess.channel.send(embed = dual_game)
                except discord.errors.NotFound:
                    dual_game = discord.Embed(title = "Invalid user!", description = "The ID entered does not exist!", color = discord.Color.blue())
                    await mess.channel.send(embed = dual_game)
            else:
                dual_game = discord.Embed(title = "Invalid syntax!", description = "The minesweeper syntax is invalid!", color = discord.Color.blue())
                await mess.channel.send(embed = dual_game)
        else:
            await mess.channel.send("You cant play a match against someone in a DM!")

    elif msg == ";tournament":
        if not(isinstance(mess.channel, discord.DMChannel)):
            host_id = mess.author.id
            thumb = bot.get_emoji(935120796358152212)
            check = bot.get_emoji(935455988516028486)
            winner = bot.get_emoji(935794255543275541)
            bye = bot.get_emoji(935868215169540146)
            tourney_members = [host_id]
            tourney_init_embed = discord.Embed(title = "Tournament started!", description = f"<@!{host_id}> started a tournament! React with {thumb} below to join! React with {bye} to leave. React again to join/leave! <@!{host_id}> react with {check} to start the tournament!", colour = discord.Colour.blue())
            tourney_init = await mess.channel.send(embed = tourney_init_embed)
            await tourney_init.add_reaction(str(thumb))
            await tourney_init.add_reaction(str(bye))
            await tourney_init.add_reaction(str(check))
            while True:
                try:
                    reaction, user = await bot.wait_for("reaction_add", check = lambda r, p: str(r.emoji) in [str(thumb), str(bye), str(check)] and p != bot.user and r.message.id == tourney_init.id, timeout = 60.0)
                except asyncio.TimeoutError:
                    break
                else:
                    reaction_e = str(reaction.emoji)
                    if reaction_e == str(thumb) and user.id != host_id and user.id not in tourney_members:
                        await mess.channel.send(f"<@!{user.id}> has joined the tournament 🎉")
                        tourney_members.append(user.id)
                    elif reaction_e == str(bye) and user.id != host_id and user.id in tourney_members:
                        await mess.channel.send(f"<@!{user.id}> has left the tournament 😢")
                        tourney_members.remove(user.id)
                    elif reaction_e == str(check) and user.id == host_id:
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
                        player_1 = minesweeper(8, 8, 8, a_id, "yes")
                        player_2 = minesweeper(8, 8, 8, opp_id, "yes")
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

        else:
            await mess.channel.send("You can't start a tournament in a DM!")

    elif msg == ";leaderboard" or msg == ";lb":
        leaders = global_leaderboard()
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
        global_lb = discord.Embed(title="Global leaderboard", description = leaders_str, colour=discord.Color.blue())
        await mess.channel.send(embed=global_lb)

    elif msg == ";server leaderboard" or msg == ";serverlb":
        if not(isinstance(mess.channel, discord.DMChannel)):
            server_id = mess.guild.id
            guild = bot.get_guild(server_id)
            members = []
            for m in guild.members:
                members.append(m.id)
            server_leaders = server_leaderboard(members)
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
            server_lb = discord.Embed(title="Server leaderboard", description = sleaders_str, colour=discord.Color.blue())
            await mess.channel.send(embed=server_lb)
        else:
            await mess.channel.send("This is not a server!")

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
                        user_profile.add_field(name = "Win streak:", value = prof[10], inline = True)
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
            user_profile = discord.Embed(title = "Invalid syntax!", description = "The profile syntax is invalid!", color = discord.Color.blue())
        await mess.channel.send(embed=user_profile)

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
        else:
            if str(reaction.emoji) == "✅":
                delete_record(aut_id)
                record_d = discord.Embed(title = "Data deleted", description = "All of your stats with the bot have been deleted. Play again to create new stats.", colour = discord.Colour.blue())
            else:
                record_d = discord.Embed(title = "Operation cancelled!", description = "Data deletion has been cancelled!", colour = discord.Colour.blue())
            await mess.channel.send(embed = record_d)

    elif msg == ";register" and mess.channel.id == 936949262791606272:
        t_mem_id = mess.author.id
        t_mem = mess.author
        await mess.channel.send(f"<@!{t_mem_id}> has joined the tournament 🎉")
        c_guild = bot.get_guild(915952924172091433)
        role = get(c_guild.roles, name="Tournament participants")
        await t_mem.add_roles(role)

    elif msg == ";invite":
        invite = discord.Embed(title = "Invite me to your server!", description = "Use this link to invite me: https://discord.com/api/oauth2/authorize?client_id=902498109270134794&permissions=274878172224&scope=bot", colour = discord.Colour.blue())
        await mess.channel.send(embed = invite)
    
    elif msg == ";support":
        support = discord.Embed(title = "Join the official minesweeper bot support server!", description = "Use this link to join the server: https://discord.gg/3jCG74D3RK", colour = discord.Colour.blue())
        await mess.channel.send(embed = support)
    
    elif msg == ";vote":
        vote = discord.Embed(title = "Vote for me!", description = '''Enjoyed using the bot?
Vote for us on top.gg: https://top.gg/bot/902498109270134794/vote
Vote for us on discordbotlist: https://discordbotlist.com/bots/minesweeper-bot/upvote''', colour = discord.Colour.blue())
        await mess.channel.send(embed = vote)
    
    elif msg == ";strength" and mess.author.id == 706855396828250153:
        await mess.channel.send("I'm in "+str(len(bot.guilds))+" servers!")

    elif msg == ";help":
        help = discord.Embed(title = "A complete guide on how to use the Minesweeper Bot!", description = "This bot allows you to play minesweeper on discord! The prefix for the bot is `;`.", colour = discord.Colour.blue())
        help.add_field(name = "Rules: ", value = 
        '''The basic rules of the game are:
1. Behind each circle is either a bomb, a number, or nothing.
2. If you hit a bomb you lose the game.
3. The number signifies how many bombs are there behind the circles adjacent to it (diagonals included).
4. If you know the location of a bomb, you can place a flag over there for reference.
5. Open up all the circles without the bombs to win the game!'''
        , inline = False)
        help.add_field(name = "Commands: ", value = 
        '''
`;help`: Open the guide.
`;minesweeper`: Start a new minesweeper game in an 8x8 grid with 8 bombs. Tag someone in your server to play a game against them!
`;ms`: Alias of `;minesweeper`.
`;minesweeper custom`: Start a custom minesweeper game.
`;mscustom`: Alias of `;minesweeper custom`.
`;tournament`: Start a minesweeper tournament in your server!
`;leaderboard`: View the global leaderboard.
`;lb`: Alias of `;leaderboard`.
`;server leaderboard`: View the server leaderboard.
`;serverlb`: Alias of `;server leaderboard`.
`;profile`: View your personal minesweeper bot profile. Tag someone else to view their profile as well!
`;profile settings private/public`: Control who can view your profile. By default it is set to public.
`;delete`: Delete all your data on the minesweeper bot.
`;invite`: Get a link to invite this bot to a server.
`;support`: Get a link to join the official minesweeper bot support server.
`;vote`: Vote for the bot!''')
        help.add_field(name = "The Nexus:", value = "[Invite Me](https://discord.com/api/oauth2/authorize?client_id=902498109270134794&permissions=274878172224&scope=bot) · [Support Server](https://discord.gg/3jCG74D3RK) · [Vote for Us!](https://top.gg/bot/902498109270134794/vote)", inline = False)
        await mess.channel.send(embed = help)

bot.run(token)