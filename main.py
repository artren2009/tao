import os
import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta, date
import asyncio

import logging

import os.path
from os import path

from cogs.moderation import Moderation
from cogs.score import Score
from cogs.data import Data
from cogs.utils import *

# initialize
TOKEN = open("tmp/token.txt", "r").read()

cogs = [
    "cogs.score",
    "cogs.data",
    "cogs.misc",
    "cogs.moderation",
    "cogs.eval",
    "cogs.error",
]

# setup intents
intents = discord.Intents()
intents.guilds = True
intents.members = True
intents.bans = True
intents.presences = True
intents.messages = True
intents.guild_messages = True
intents.reactions = True
intents.guild_reactions = True

# setup client object
client = commands.Bot(
    command_prefix="tao ",
    status=discord.Status.idle,
    activity=discord.Game(name="initializing"),
    intents=intents,
)

# remove the help command
# because we have our own command
client.remove_command("help")

""" ERROR HANDLING """

if not path.exists("cogs/_error.txt"):
    f = open("cogs/_error.txt", "w")
    f.close()

# Create a logging instance
logger = logging.getLogger("tao")
logger.setLevel(logging.ERROR)  # you can set this to be DEBUG, INFO, ERROR

# Assign a file-handler to that instance
fh = logging.FileHandler("cogs/_error.txt")
fh.setLevel(logging.INFO)  # again, you can set this differently

# Format your logs (optional)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)  # This will set the format to the file handler

# Add the handler to your logging instance
logger.addHandler(fh)

try:
    raise ValueError("an error occured")
except ValueError as e:
    logger.exception(e)  # Will send the errors to the file

""" ERROR HANDLING """


@client.event
async def on_ready():

    # print bot user and discrim on the console
    print("{0.user}".format(client))

    # get guild count
    guild_count = len(list(client.guilds))

    # change the presence to show
    # guild count
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(list(client.guilds))} guilds",
        ),
    )

    # create required files
    # if they dont exist
    if not path.exists(data_guild):
        f = open(data_guild, "w")
        f.write("{" + "}")
        f.close()
    if not path.exists(data_users):
        f = open(data_users, "w")
        f.write("{" + "}")
        f.close()


@client.event
async def on_guild_join(guild):

    # update file
    guilds = json_load(data_guild)

    # create json object for guild
    await Data.update_data(Data, guilds, guild)

    json_save(guilds, data_guild)

    # update guild count
    guild_count = len(list(client.guilds))
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(list(client.guilds))} guilds",
        ),
    )


@client.event
async def on_member_join(member):

    # update file
    guilds = json_load(data_guild)

    # get configuration
    alias = guilds[str(member.guild.id)]
    data_ch = alias["chnl_notify"]
    data_state = alias["scre_enable"]
    data_state_late = alias["late_enable"]

    json_save(guilds, data_guild)

    channel = client.get_channel(data_ch)

    # sort user
    if data_state == True and channel:
        await Score.sort_user_auto(Score, channel, member, False, False)


@client.event
async def on_message(message):

    # embed meta
    embed = discord.Embed(color=0xF5F5F5)

    source = "https://github.com/0x16c3/tao"
    avatar = client.user.avatar_url

    if message.content == "tao":
        embed.set_author(name="Tao", url=source, icon_url=avatar)
        embed.set_thumbnail(url=avatar)

        embed.add_field(name="source", value=source, inline=False)
        embed.set_footer(text="道")

        await message.channel.send(embed=embed)
    else:
        if not message.author.bot and isinstance(
            message.channel, discord.channel.TextChannel
        ):
            # update file
            members = json_load(data_users)

            # get if user is checked
            await Data.update_data_user(Data, members, message.author)
            checked = members[str(message.author.id)]["checked"]

            json_save(members, data_users)

            # update file
            guilds = json_load(data_guild)

            # get configuration
            await Data.update_data(Data, guilds, message.guild)
            late = await Data.get_state_config(
                Data, guilds, message.guild, "late_enable"
            )
            channel = guilds[str(message.guild.id)]["chnl_notify"]
            verbose = guilds[str(message.guild.id)]["verbose_enable"]
            setup_complete = guilds[str(message.guild.id)]["setup_complete"]

            # get notification channel
            channel_notify = discord.utils.get(
                client.get_all_channels(), guild__name=message.guild.name, id=channel,
            )

            json_save(guilds, data_guild)

            # send setup notification
            if not setup_complete and message.content != "tao init":
                try:
                    await Data.setup_notify(Data, message.channel)
                except:
                    pass

            # update if guild is notified
            if message.content == "tao init":
                # update file
                guilds = json_load(data_guild)

                guilds[str(message.guild.id)]["notified"] = True

                json_save(guilds, data_guild)

            # late scoring
            if late and not checked and channel_notify:

                await Score.sort_user_auto(Score, channel_notify, message.author, True)

                # update file
                members = json_load(data_users)

                await Data.update_data_user(Data, members, message.author)
                await Data.update_state_user(
                    Data, members, message.author, "checked", True
                )

                json_save(members, data_users)

    await client.process_commands(message)


if __name__ == "__main__":
    for extension in cogs:
        try:
            client.load_extension(extension)
        except Exception as error:
            print(f"{extension} could not be activated. [{error}]")
    try:
        client.load_extension("cogs.topgg")
    except:
        pass

# timer for moderation commands
async def timer_secd():

    # wait if bot is not ready yet
    await client.wait_until_ready()

    while client.is_ready():
        # run loop once every second
        await asyncio.sleep(1)

        # get all guilds
        guilds = json_load(data_guild)

        for guild_i in guilds:

            guild = client.get_guild(int(guild_i))

            if guild:

                # update guild data
                await Data.update_data(Data, guilds, guild)

                json_save(guilds, data_guild)

                # get updated guild data
                guilds = json_load(data_guild)

                # get punished members in the guild database
                member_list = guilds[guild_i]["banned_members"]

                for member_i in member_list:

                    # get member object
                    member = await client.fetch_user(int(member_i))

                    # update timer
                    await Data.update_ban_timer(Data, guilds, guild, member)
                    curtime = await Data.get_ban_timer(Data, guilds, guild, member)

                    json_save(guilds, data_guild)

                    # if there is no time (expired)
                    if curtime <= 0:

                        guilds = json_load(data_guild)

                        # unban member
                        try:
                            await guild.unban(member)

                            embed = discord.Embed(
                                title="Info", description="", color=color_errr
                            )
                            embed.add_field(
                                name="You have been unbanned!",
                                value="Your ban from `"
                                + ctx.guild.name
                                + "` has expired!",
                                inline=False,
                            )
                            try:
                                await member.send(embed=embed)
                            except:
                                pass
                        except:
                            pass

                        # delete banned member json object
                        await Data.delete_banned_member(Data, guilds, guild, member)

                        json_save(guilds, data_guild)


# autoapprove function
async def run_autoapprove():

    # get users
    users = json_load(data_users)

    for member_i in users:

        # check for autoapprove flag
        approve_flag = users[member_i]["flag_approve"]

        if not approve_flag:
            continue

        # get member object
        member = await fetch_member(client, int(member_i))

        if member == None:
            continue

        # update member data
        await Data.update_data_user(Data, users, member)

        json_save(users, data_users)

        # get updated data
        users = json_load(data_users)

        # get current days
        approve_days = users[member_i]["approval"]["days"]
        approve_dval = users[member_i]["approval"]["start_date"]
        if approve_dval != 0:
            approve_date = datetime.strptime(str(approve_dval), "%Y-%m-%dT%H:%M:%S.%f")

        # check for users with approval days
        if approve_days > 0:
            status = member.status

            # check if they are online
            if status == discord.Status.online or status == discord.Status.dnd:
                users = json_load(data_users)

                # update the score
                await Data.update_state_user_approval(
                    Data,
                    users,
                    member,
                    "score",
                    users[member_i]["approval"]["score"] + 1,
                )
                await Data.update_state_user_approval(
                    Data,
                    users,
                    member,
                    "checks",
                    users[member_i]["approval"]["checks"] - 1,
                )

                json_save(users, data_users)

            today = datetime.now()
            # if its been a day since start_date
            if (today - approve_date).days >= 1:
                users = json_load(data_users)

                today_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                if today_str and type(today_str) == str:
                    # set date as today and subtract days
                    await Data.update_state_user_approval(
                        Data, users, member, "start_date", today_str
                    )

                await Data.update_state_user_approval(
                    Data,
                    users,
                    member,
                    "days",
                    users[member_i]["approval"]["days"] - 1,
                )

                json_save(users, data_users)

        elif approve_days == 0 and users[member_i]["approval"]["static"] != 0:
            users = json_load(data_users)

            # magical score calculation
            static = users[member_i]["approval"]["static"]
            days = static / 8

            final_score = users[member_i]["approval"]["score"] / static

            await Data.update_state_user_approval(
                Data, users, member, "score", final_score
            )

            await Data.update_state_user(Data, users, member, "flag_approve", False)
            await Data.update_state_user_approval(
                Data, users, member, "checks", 0
            )  # 8 checks per day
            await Data.update_state_user_approval(
                Data, users, member, "static", 0
            )  # store check count for calculation
            await Data.update_state_user_approval(Data, users, member, "start_date", "")

            json_save(users, data_users)


async def timer_hour(hours: int):
    await client.wait_until_ready()
    while client.is_ready():
        await run_autoapprove()
        await asyncio.sleep(3600 * hours)


try:
    client.loop.create_task(timer_secd())
    client.loop.create_task(timer_hour(3))
    client.run(TOKEN)
except KeyboardInterrupt:
    print("exit")
