import os
import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta
import time

from .utils import *


class Data(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def update_data(self, guilds, guild: discord.Guild):
        id = str(guild.id)

        if not id in guilds:
            # if the guild is not saved create guild object
            guilds[id] = {}
            guilds[id]["scre_enable"] = True
            guilds[id]["chnl_notify"] = 0
            guilds[id]["chnl_approve"] = 0
            guilds[id]["chnl_approve_voice"] = 0
            guilds[id]["role_approve"] = 0
            guilds[id]["role_member"] = 0

    async def update_id_channel(
        self, guilds, guild, channel: discord.channel.TextChannel, type: str
    ):
        id = str(guild.id)

        guilds[id][type] = channel.id

    async def update_id_role(self, guilds, guild, role: discord.Role, type: str):
        id = str(guild.id)

        guilds[id][type] = role.id

    async def update_state_score(self, guilds, guild, state: bool):
        id = str(guild.id)

        guilds[id]["scre_enable"] = state

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def create_channel(self, ctx, name: str, cfg: str, type: str, embed):
        guild = ctx.message.guild

        # get existing channel
        channel_existing = discord.utils.get(
            self.client.get_all_channels(), guild__name=ctx.guild.name, name=name,
        )

        # if there is an existing channel
        if channel_existing is not None:
            # update file
            with open(data_file, "r") as f:
                guilds = json.load(f)

            await self.update_id_channel(guilds, guild, channel_existing, cfg)

            with open(data_file, "w") as f:
                json.dump(guilds, f)

            if embed is not None:
                embed.add_field(
                    name="Updated existing channel",
                    value="`" + name + "`",
                    inline=False,
                )
        else:
            # create channel
            if type == "text":
                await guild.create_text_channel(name)
            elif type == "voice":
                await guild.create_voice_channel(name)

            # get created channel
            channel = discord.utils.get(
                self.client.get_all_channels(), guild__name=ctx.guild.name, name=name,
            )

            # update file
            with open(data_file, "r") as f:
                guilds = json.load(f)

            await self.update_id_channel(guilds, guild, channel, cfg)

            with open(data_file, "w") as f:
                json.dump(guilds, f)

            if embed is not None:
                embed.add_field(
                    name="Created channel", value="`" + name + "`", inline=False
                )

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def create_role(self, ctx, name: str, cfg: str, color: discord.Color, embed):
        guild = ctx.message.guild

        # get existing role
        role_existing = discord.utils.get(guild.roles, name=name)

        # if the role exists
        if role_existing is not None:
            # update file
            with open(data_file, "r") as f:
                guilds = json.load(f)

            await self.update_id_role(guilds, guild, role_existing, cfg)

            with open(data_file, "w") as f:
                json.dump(guilds, f)

            if embed is not None:
                embed.add_field(
                    name="Updated existing role",
                    value=role_existing.mention,
                    inline=False,
                )
        else:
            # create role
            await guild.create_role(name=name, color=color)

            # get created role
            role = discord.utils.get(guild.roles, name=name)

            # update file
            with open(data_file, "r") as f:
                guilds = json.load(f)

            await self.update_id_role(guilds, guild, role, cfg)

            with open(data_file, "w") as f:
                json.dump(guilds, f)

            if embed is not None:
                embed.add_field(name="Created role", value=role.mention, inline=False)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def update_perms(self, ctx, guild: discord.Guild, embed: discord.Embed):
        approval_role = discord.utils.get(guild.roles, name="tao-approval")

        # update file
        with open(data_file, "r") as f:
            guilds = json.load(f)

        approve_id = guilds[str(guild.id)]["role_approve"]
        member_id = guilds[str(guild.id)]["role_member"]
        ch_approve_id = guilds[str(guild.id)]["chnl_approve"]
        ch_approve_voice_id = guilds[str(guild.id)]["chnl_approve_voice"]

        with open(data_file, "w") as f:
            json.dump(guilds, f)

        approve_role = discord.utils.get(guild.roles, id=approve_id)
        member_role = discord.utils.get(guild.roles, id=member_id)

        if approve_role == member_role:
            print("dbg")

        approve_channel = discord.utils.get(
            self.client.get_all_channels(), guild__name=guild.name, id=ch_approve_id,
        )
        approve_voice_channel = discord.utils.get(
            self.client.get_all_channels(),
            guild__name=guild.name,
            id=ch_approve_voice_id,
        )

        text_channel_list = []
        voice_channel_list = []

        for channel in guild.text_channels:
            text_channel_list.append(channel)
        for channel in guild.voice_channels:
            voice_channel_list.append(channel)

        for ch in text_channel_list:
            await ch.set_permissions(
                approval_role, read_messages=False, read_message_history=False
            )
            time.sleep(1)
            await ch.set_permissions(
                member_role, read_messages=True, read_message_history=True
            )

        for ch_v in voice_channel_list:
            await ch_v.set_permissions(approval_role, view_channel=False, speak=False)
            time.sleep(1)
            await ch_v.set_permissions(member_role, view_channel=True, speak=True)

        await approve_channel.set_permissions(
            approval_role, view_channel=True, read_message_history=True
        )
        time.sleep(1)
        await approve_channel.set_permissions(
            member_role, view_channel=False, read_message_history=False
        )

        await approve_voice_channel.set_permissions(
            approval_role, view_channel=True, speak=True
        )
        time.sleep(1)
        await approve_voice_channel.set_permissions(
            member_role, view_channel=False, speak=False
        )

        if embed is not None:
            embed.add_field(
                name="Set all permissions",
                value="Set permissions for manual approval channels",
                inline=False,
            )

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def set_role(self, ctx, name):
        guild = ctx.message.guild

        # update file
        with open(data_file, "r") as f:
            guilds = json.load(f)

        await self.update_data(guilds, guild)

        with open(data_file, "w") as f:
            json.dump(guilds, f)

        if name == "":
            # create embed
            embed = discord.Embed(title="Error", description="", color=color_errr)
            embed.add_field(name="Missing argument", value="`name`", inline=False)
            embed.add_field(
                name="Set it to @everyone?",
                value="Type `tao setup_role -yes` to proceed",
                inline=False,
            )
            await ctx.send(embed=embed)
            return

        # get existing role
        role_existing = discord.utils.get(guild.roles, name=name)

        role_everyone = guild.default_role

        if role_existing is not None or name == "-yes" or name == "-everyone":
            # create embed
            embed = discord.Embed(title="Done!", description="", color=color_done)

            # update file
            with open(data_file, "r") as f:
                guilds = json.load(f)

            if name != "-yes" and name != "-everyone":
                await self.update_id_role(guilds, guild, role_existing, "role_member")
            elif name == "-yes" or "-everyone":
                await self.update_id_role(guilds, guild, role_everyone, "role_member")

            with open(data_file, "w") as f:
                json.dump(guilds, f)

            if name != "-yes" and name != "-everyone":
                embed.add_field(
                    name="User role set as", value=role_existing.mention, inline=False
                )
            elif name == "-yes" or "-everyone":
                embed.add_field(
                    name="User role set as", value=role_everyone, inline=False
                )

            await ctx.send(embed=embed)
        else:
            # create embed
            embed = discord.Embed(title="Error", description="", color=color_errr)
            embed.add_field(name="Could not find role", value=name, inline=False)
            embed.add_field(
                name="Set it to @everyone?",
                value="Type `tao set_role -yes` to proceed",
                inline=False,
            )
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def init(self, ctx, name: str = ""):
        guild = ctx.message.guild

        # update file
        with open(data_file, "r") as f:
            guilds = json.load(f)

        await self.update_data(guilds, guild)
        user_id = guilds[str(guild.id)]["role_member"]

        with open(data_file, "w") as f:
            json.dump(guilds, f)

        # create embed
        embed_waiting = discord.Embed(title="Setup", description="", color=color_main)
        embed_waiting.add_field(
            name="Please wait", value="Processing request...", inline=False,
        )
        waiting_msg = await ctx.send(embed=embed_waiting)

        # create embed
        embed = discord.Embed(title="Setup", description="", color=color_done)

        # if user role is not set
        # if user_id == 0:
        #     # create embed
        #     embed_brk = discord.Embed(title="Error", description="", color=color_errr)
        #     embed_brk.add_field(
        #         name="No user role set",
        #         value="First, set your user role with `tao set_role [rolename] (-everyone)`",
        #         inline=False,
        #     )
        #     await waiting_msg.delete()
        #     await ctx.send(embed=embed_brk)
        #     return

        # set role
        self.set_role(name)

        # create role
        await self.create_role(ctx, "tao-approval", "role_approve", color_warn, embed)

        # create channels
        await self.create_channel(
            ctx, "tao-notifications", "chnl_notify", "text", embed
        )
        await self.create_channel(
            ctx, "tao-approve_manual", "chnl_approve", "text", embed
        )
        await self.create_channel(
            ctx, "tao-approve_voice", "chnl_approve_voice", "voice", embed
        )

        await self.update_perms(ctx, guild, embed)

        embed.add_field(name="User role set", value="Setup complete!", inline=False)

        embed.add_field(
            name="WARNING",
            value="User checks are `enabled` by default. Type `tao score -disable` to disable it.",
            inline=False,
        )

        await waiting_msg.delete()
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def score(self, ctx, args: str = ""):
        guild = ctx.guild

        if args == "":
            embed_errr = discord.Embed(title="Error", description="", color=color_errr)
            embed_errr.add_field(
                name="Invalid argument",
                value="Available arguments: `-enable`, `-disable`",
                inline=False,
            )
            await ctx.send(embed=embed_errr)

        # update file
        with open(data_file, "r") as f:
            guilds = json.load(f)

        await self.update_data(guilds, guild)
        state = guilds[str(guild.id)]["scre_enable"]

        with open(data_file, "w") as f:
            json.dump(guilds, f)

        if args == "-enable":
            if state == True:
                embed_warn = discord.Embed(
                    title="Info", description="", color=color_done
                )
                embed_warn.add_field(
                    name="Already enabled",
                    value="This function has already been enabled",
                    inline=False,
                )
                await ctx.send(embed=embed_warn)
            elif state == False:
                # update file
                with open(data_file, "r") as f:
                    guilds = json.load(f)

                await self.update_data(guilds, guild)
                await self.update_state_score(guilds, guild, True)

                with open(data_file, "w") as f:
                    json.dump(guilds, f)

                embed_done = discord.Embed(
                    title="Done!", description="", color=color_done
                )
                embed_done.add_field(
                    name="Enabled function",
                    value="Successfully enabled the function",
                    inline=False,
                )
                await ctx.send(embed=embed_done)
        elif args == "-disable":
            if state == False:
                embed_warn = discord.Embed(
                    title="Info", description="", color=color_done
                )
                embed_warn.add_field(
                    name="Already disabled",
                    value="This function has already been disabled",
                    inline=False,
                )
                await ctx.send(embed=embed_warn)
            elif state == True:
                # update file
                with open(data_file, "r") as f:
                    guilds = json.load(f)

                await self.update_data(guilds, guild)
                await self.update_state_score(guilds, guild, False)

                with open(data_file, "w") as f:
                    json.dump(guilds, f)

                embed_done = discord.Embed(
                    title="Done!", description="", color=color_done
                )
                embed_done.add_field(
                    name="Disabled function",
                    value="Successfully disabled the function",
                    inline=False,
                )
                await ctx.send(embed=embed_done)


def setup(client):
    client.add_cog(Data(client))
