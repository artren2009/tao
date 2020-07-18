import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta

from .score import Score
from .utils import *


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def info(self, ctx, target: discord.Member = None):
        # embed target information
        if not target:
            target = ctx.author

        # title
        embed = discord.Embed(
            title="{}".format(target.name), description="", color=color_main
        )

        # author
        embed.set_author(name=target, icon_url=target.avatar_url)

        # avatar thumbnail
        embed.set_thumbnail(url=target.avatar_url)

        ##########################################

        # ID
        embed.add_field(name="ID", value=target.id, inline=False)

        # username
        embed.add_field(name="username", value=target, inline=True)

        # age
        current_date = datetime.now()

        user_created = target.created_at
        user_created_str = user_created.strftime("%y/%m/%d")
        embed.add_field(
            name="created", value="{}".format(user_created_str), inline=True
        )

        user_join = target.joined_at
        user_join_str = user_join.strftime("%y/%m/%d")
        embed.add_field(name="joined", value="{}".format(user_join_str), inline=True)

        embed.add_field(name="top role", value=target.top_role, inline=True)

        # account age
        embed.add_field(
            name="account age",
            value="{}".format(await Score.get_age_account(ctx, target)),
            inline=True,
        )

        # guild age
        embed.add_field(
            name="guild age",
            value="{}".format(await Score.get_age_guild(ctx, target)),
            inline=True,
        )

        ##########################################

        # footer
        embed.set_footer(text="requested by {}".format(ctx.author))

        await ctx.send(embed=embed)

    @commands.command(pass_context=False)
    @commands.has_permissions(administrator=True)
    async def run(
        self,
        ctx,
        command: str = "",
        target: discord.Member = None,
        args_first: str = "",
    ):
        guild = ctx.guild

        # update file
        with open("cogs/_guild.json", "r") as f:
            guilds = json.load(f)

        data_guild = guilds[str(guild.id)]
        data_ch = data_guild["chnl_notify"]

        with open("cogs/_guild.json", "w") as f:
            json.dump(guilds, f)

        channel = discord.utils.get(
            self.client.get_all_channels(), guild__name=guild.name, id=data_ch,
        )

        if command == "":
            embed_errr = discord.Embed(title="Error", description="", color=color_errr)
            embed_errr.add_field(
                name="Invalid argument",
                value="Available arguments: `-set_flag`, `-get_score`, `-sort`",
                inline=False,
            )
            await ctx.send(embed=embed_errr)
            return 0
        elif command == "-set_flag":
            if target is None:
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="`target` cannot be `None`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)
                return 1
            if args_first == "":
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="Available arguments: `-0`, `-1`, `-2`, `-3`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)
                return 2
            if args_first == "-0":  # notify
                await Score.flag_member(Score, 0, 0.30, channel, target)
            elif args_first == "-1":  # approval
                await Score.flag_member(Score, 1, 0.15, channel, target)
            elif args_first == "-2":  # ban
                await Score.flag_member(Score, 2, 0.05, channel, target)
            elif args_first == "-3":  # valid
                await Score.flag_member(Score, -1, 1.0, channel, target)
        elif command == "-get_score":
            scr_val = await Score.get_score(Score, target)
            acc_val = await Score.get_age_account(Score, target)
            gld_val = await Score.get_age_guild(Score, target)
            avt_val = await Score.get_avatar(Score, target)
            mbl_val = await Score.get_is_on_mobide(Score, target)
            # hsq_val = await Score.get_hypesquad(Score, target)
            ntr_val = await Score.get_premium(Score, target)
            embed_info = discord.Embed(title="Info", description="", color=color_done)
            embed_info.add_field(
                name="User score:", value=str(scr_val), inline=True,
            )
            age = await Score.get_age_account(Score, target)
            age_clamped = max(min(age, 100), 0)
            embed_info.add_field(
                name="Account age:",
                value=str(acc_val) + " : +" + str(age_clamped / 100),
                inline=True,
            )
            diff = await Score.get_date_diff(Score, target)
            diff_clamped = max(min(diff, 100), 0)
            embed_info.add_field(
                name="Join age:",
                value=str(gld_val) + " : +" + str(diff_clamped / 100),
                inline=True,
            )
            avt = 0
            if avt_val:
                avt = 0.250
            else:
                avt = 0
            embed_info.add_field(
                name="Custom avatar:",
                value=str(avt_val) + " : +" + str(avt),
                inline=True,
            )
            mbl = 0
            if mbl_val:
                mbl = 0.250
            else:
                mbl = 0
            embed_info.add_field(
                name="On mobile:", value=str(mbl_val) + " : +" + str(mbl), inline=True,
            )
            ntr = 0
            if ntr_val:
                ntr = 0.5
            else:
                ntr = 0
            embed_info.add_field(
                name="Nitro:", value=str(ntr_val) + " : +" + str(ntr), inline=True,
            )
            await ctx.send(embed=embed_info)
        elif command == "-sort":
            if target is None:
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="`target` cannot be `None`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)
                return 1
            else:
                await Score.sort_user_auto(Score, channel, target)
                scr_val = await Score.get_score(Score, target)
                acc_val = await Score.get_age_account(Score, target)
                gld_val = await Score.get_age_guild(Score, target)
                avt_val = await Score.get_avatar(Score, target)
                mbl_val = await Score.get_is_on_mobide(Score, target)
                # hsq_val = await Score.get_hypesquad(Score, target)
                ntr_val = await Score.get_premium(Score, target)
                embed_info = discord.Embed(
                    title="Info", description="", color=color_done
                )
                embed_info.add_field(
                    name="User score:", value=str(scr_val), inline=True,
                )
                age = await Score.get_age_account(Score, target)
                age_clamped = max(min(age, 100), 0)
                embed_info.add_field(
                    name="Account age:",
                    value=str(acc_val) + " : +" + str(age_clamped / 100),
                    inline=True,
                )
                diff = await Score.get_date_diff(Score, target)
                diff_clamped = max(min(diff, 100), 0)
                embed_info.add_field(
                    name="Join age:",
                    value=str(gld_val) + " : +" + str(diff_clamped / 100),
                    inline=True,
                )
                avt = 0
                if avt_val:
                    avt = 0.250
                else:
                    avt = 0
                embed_info.add_field(
                    name="Custom avatar:",
                    value=str(avt_val) + " : +" + str(avt),
                    inline=True,
                )
                mbl = 0
                if mbl_val:
                    mbl = 0.250
                else:
                    mbl = 0
                embed_info.add_field(
                    name="On mobile:",
                    value=str(mbl_val) + " : +" + str(mbl),
                    inline=True,
                )
                ntr = 0
                if ntr_val:
                    ntr = 0.5
                else:
                    ntr = 0
                embed_info.add_field(
                    name="Nitro:", value=str(ntr_val) + " : +" + str(ntr), inline=True,
                )
                embed_info.add_field(
                    name="Manual sorting", value="User manually sorted", inline=True,
                )
                await ctx.send(embed=embed_info)


def setup(client):
    client.add_cog(Misc(client))
