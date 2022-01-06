import discord
import discord.ext.commands
from minesweeper_class import minesweeper
from records import global_leaderboard, server_leaderboard, profile, privacy_change
import os

intents = discord.Intents.default()
intents.members = True
bot = discord.Client(intents = intents)
token = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = ";help"))
    print("Ready for takeoff!")


@bot.event
async def on_message(mess):
    msg = mess.content.lower()
    author = mess.author.name
    if mess.author == bot.user:
        return

    if msg == ";minesweeper" or msg == ";ms":
        author_id = mess.author.id
        play = minesweeper(8, 8, 8, author_id)
        game_init = discord.Embed(title=author+"'s minesweeper game", description='''
        You do not have to use ; while playing
        '''
        + play.str_row, color=discord.Color.blue())
        await mess.channel.send(embed=game_init)
        while play.game == 1:
            while True:
                while True:
                    await mess.channel.send("Enter the row (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                    r_msg = await bot.wait_for("message", check=lambda m: m.author == mess.author and m.channel == mess.channel)
                    try:
                        r = int(r_msg.content)
                        if r <= 0 or r > play.num_rows:
                            await mess.channel.send("Row is out of range")
                        else:
                            break
                    except ValueError:
                        r = str(r_msg.content).lower()
                        if r == "flag":
                            if play.flag_var == 0:
                                await mess.channel.send("Flag mode on")
                                play.flag_var = 1
                            else:
                                await mess.channel.send("Flag mode off")
                                play.flag_var = 0
                            break
                        elif r == "board":
                            if play.flag_var == 1:
                                play.flag = "On"
                            else:
                                play.flag = "Off"

                            game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag +
                            '''
                            '''
                            + play.str_row, color=discord.Color.blue())
                            await mess.channel.send(embed=game_real)
                        elif r == "quit":
                            play.game = 0
                            play.end_msg = "I'm sorry to see you leave 😢"
                            break
                        else:
                            await mess.channel.send("Invalid input")

                if r != "flag" and r != "quit":
                    while True:
                        await mess.channel.send("Enter the column")
                        c_msg = await bot.wait_for("message", check=lambda m: m.author == mess.author and m.channel == mess.channel)
                        try:
                            c = int(c_msg.content)
                            if c <= 0 or c > play.num_cols:
                                await mess.channel.send("Column is out of range")
                            else:
                                break
                        except ValueError:
                            await mess.channel.send("Invalid input")

                elif r == "quit":
                    break

                else:
                    continue

                try:
                    play.guess(r, c)
                    break
                except UnboundLocalError:
                    await mess.channel.send("That position is already occupied")
            if r != "quit":
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

    if msg == ";minesweeper custom" or msg == ";mscustom":
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
                    elif num_cols > 27:
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

            play = minesweeper(num_rows, num_cols, num_bombs, author_id)
            if play.items_tot > 198:
                await mess.channel.send("Your grid is too big")
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
                    await mess.channel.send("Enter the row (to toggle flag mode, type 'flag'; type 'board' to see your current game; type 'quit' to end the game)")
                    r_msg = await bot.wait_for("message", check=lambda m: m.author == mess.author and m.channel == mess.channel)
                    try:
                        r = int(r_msg.content)
                        if r <= 0 or r > play.num_rows:
                            await mess.channel.send("Row is out of range")
                        else:
                            break
                    except ValueError:
                        r = str(r_msg.content).lower()
                        if r == "flag":
                            if play.flag_var == 0:
                                await mess.channel.send("Flag mode on")
                                play.flag_var = 1
                            else:
                                await mess.channel.send("Flag mode off")
                                play.flag_var = 0
                            break
                        elif r == "board":
                            if play.flag_var == 1:
                                play.flag = "On"
                            else:
                                play.flag = "Off"

                            game_real = discord.Embed(title=author+"'s minesweeper game", description="Flag mode: "+play.flag+
                            '''
                            '''
                            + play.str_row, color=discord.Color.blue())
                            await mess.channel.send(embed=game_real)
                        elif r == "quit":
                            play.game = 0
                            play.end_msg = "I'm sorry to see you leave 😢"
                            break
                        else:
                            await mess.channel.send("Invalid input")

                if r != "flag" and r != "quit":
                    while True:
                        await mess.channel.send("Enter the column")
                        c_msg = await bot.wait_for("message", check=lambda m: m.author == mess.author and m.channel == mess.channel)
                        try:
                            c = int(c_msg.content)
                            if c <= 0 or c > play.num_cols:
                                await mess.channel.send("Column is out of range")
                            else:
                                break
                        except ValueError:
                            await mess.channel.send("Invalid input")

                elif r == "quit":
                    break

                else:
                    continue

                try:
                    play.guess(r, c)
                    break
                except UnboundLocalError:
                    await mess.channel.send("That position is already occupied")
            if r != "quit":
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
    
    if msg == ";leaderboard" or msg == ";lb":
        leaders = global_leaderboard()
        leaders_str = ""
        for user in leaders:
            if user[1] != None:
                time_mins = int(user[1]//60)
                time_secs = int(user[1]%60)
                leaders_str += "<@!"+str(user[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                leaders_str += '''
'''
        global_lb = discord.Embed(title="Global leaderboard", description = leaders_str, colour=discord.Color.blue())
        await mess.channel.send(embed=global_lb)

    if msg == ";server leaderboard" or msg == ";serverlb":
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
                sleaders_str += "<@!"+str(member[0])+"> : "+str(time_mins)+"m and "+str(time_secs)+"s"
                sleaders_str += '''
'''
        server_lb = discord.Embed(title="Server leaderboard", description = sleaders_str, colour=discord.Color.blue())
        await mess.channel.send(embed=server_lb)

    if msg.startswith(";profile"):
        valid_id = 0
        inv_setting = 0
        prof_author = mess.author.id
        if msg == ";profile":
            user_id = mess.author.id
            valid_id = 1
        elif msg.startswith(";profile settings"):
            if msg == ";profile settings public":
                user_id = mess.author.id
                priv = "public"
                privacy_change(user_id, priv)
            elif msg == ";profile settings private":
                user_id = mess.author.id
                priv = "private"
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
                        user_profile = discord.Embed(title = user_name+"'s profile", description = "All stats about this user on the minesweeper bot!", color = discord.Color.blue())
                        user_profile.add_field(name = "Discord handle:", value = user_handle, inline = True)
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

    if msg == ";invite":
        invite = discord.Embed(title = "Invite me to your server!", description = "Use this link to invite me: https://discord.com/api/oauth2/authorize?client_id=902498109270134794&permissions=274877910016&scope=bot", colour = discord.Colour.blue())
        await mess.channel.send(embed = invite)
    
    if msg == ";help":
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
`;minesweeper`: Start a new minesweeper game in an 8x8 grid with 8 bombs.
`;ms`: Alias of `;minesweeper`.
`;minesweeper custom`: Start a custom minesweeper game.
`;mscustom`: Alias of `;minesweeper custom`.
`;leaderboard`: View the global leaderboard.
`;lb`: Alias of `;leaderboard`.
`;server leaderboard`: View the server leaderboard.
`;serverlb`: Alias of `;server leaderboard`.
`;profile`: View your personal minesweeper bot profile. Tag someone else to view their profile as well!
`;profile settings private/public`: Control who can view your profile. By default it is set to public.
`;invite`: Get a link to invite this bot to a server.''')
        await mess.channel.send(embed = help)

bot.run(token)