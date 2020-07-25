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
            guilds[id]["setup_complete"] = False
            guilds[id]["notified"] = False
            guilds[id]["scre_enable"] = True
            guilds[id]["verbose_enable"] = False
            guilds[id]["late_enable"] = False
            guilds[id]["chnl_notify"] = 0
            guilds[id]["chnl_approve"] = 0
            guilds[id]["chnl_approve_voice"] = 0
            guilds[id]["role_approve"] = 0
            guilds[id]["role_member"] = 0
            guilds[id]["banned_members"] = {}
            return

        if not "setup_complete" in guilds[id]:
            guilds[id]["setup_complete"] = False
        if not "notified" in guilds[id]:
            guilds[id]["notified"] = False
        if not "scre_enable" in guilds[id]:
            guilds[id]["scre_enable"] = False
        if not "verbose_enable" in guilds[id]:
            guilds[id]["verbose_enable"] = False
        if not "late_enable" in guilds[id]:
            guilds[id]["late_enable"] = False
        if not "chnl_notify" in guilds[id]:
            guilds[id]["chnl_notify"] = 0
        if not "chnl_approve" in guilds[id]:
            guilds[id]["chnl_approve"] = 0
        if not "chnl_approve_voice" in guilds[id]:
            guilds[id]["chnl_approve_voice"] = 0
        if not "role_approve" in guilds[id]:
            guilds[id]["role_approve"] = 0
        if not "role_member" in guilds[id]:
            guilds[id]["role_member"] = 0
        if not "banned_members" in guilds[id]:
            guilds[id]["banned_members"] = {}

    async def update_banned_member(self, guilds, guild, member: discord.User, time: int = 0):
        id = str(guild.id)

        if not str(member.id) in guilds[id]["banned_members"]:
            guilds[id]["banned_members"][str(member.id)] = {}

        guilds[id]["banned_members"][str(member.id)]["time"] = time

    async def update_ban_timer(self, guilds, guild, member: discord.User):
        id = str(guild.id)

        guilds[id]["banned_members"][str(member.id)]["time"] -= 1

    async def get_ban_timer(self, guilds, guild, member: discord.User):
        id = str(guild.id)

        return guilds[id]["banned_members"][str(member.id)]["time"]


    async def delete_banned_member(self, guilds, guild, member: discord.User):
        id = str(guild.id)

        del guilds[id]["banned_members"][str(member.id)]

    async def update_id_channel(
        self, guilds, guild, channel: discord.channel.TextChannel, type: str
    ):
        id = str(guild.id)

        if id in guilds:
            guilds[id][type] = channel.id

    async def update_id_role(self, guilds, guild, role: discord.Role, type: str):
        id = str(guild.id)

        if id in guilds:
            guilds[id][type] = role.id

    async def update_state_config(self, guilds, guild, cfg: str, state: bool):
        id = str(guild.id)

        if id in guilds:
            guilds[id][cfg] = state

    async def get_state_config(self, guilds, guild, cfg: str):
        id = str(guild.id)

        if id in guilds:
            return guilds[id][cfg]

    async def update_data_user(self, members, member: discord.Member):
        id = str(member.id)

        if not id in members:
            # if the guild is not saved create guild object
            members[id] = {}
            members[id]["checked"] = False

    async def update_state_user(self, members, member, state: bool):
        id = str(member.id)

        members[id]["checked"] = state

    async def update_state_user_guild(self, members, member, guild, cfg, state):
        id = str(member.id)
        guild_id = str(guild.id)

        members[id][guild_id][cfg] = state

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
            return
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
            return

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
            return
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
            return

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def update_perms(self, ctx, guild: discord.Guild, embed: discord.Embed):
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
            if ch.overwrites_for(approve_role).read_messages != False:
                await ch.set_permissions(
                    approve_role, read_messages=False, read_message_history=False
                )
            time.sleep(1)
            if ch.overwrites_for(member_role).read_messages != False:
                await ch.set_permissions(
                    member_role, read_messages=True, read_message_history=True
                )

        for ch_v in voice_channel_list:
            if ch_v.overwrites_for(approve_role).view_channel != False:
                await ch_v.set_permissions(
                    approve_role, view_channel=False, speak=False
                )
            time.sleep(1)
            if ch_v.overwrites_for(member_role).view_channel != False:
                await ch_v.set_permissions(member_role, view_channel=True, speak=True)

        await approve_channel.set_permissions(
            approve_role, view_channel=True, read_message_history=True
        )
        time.sleep(1)
        if approve_channel.overwrites_for(member_role).view_channel != False:
            await approve_channel.set_permissions(
                member_role, view_channel=False, read_message_history=False
            )

        await approve_voice_channel.set_permissions(
            approve_role, view_channel=True, speak=True, stream=True
        )
        time.sleep(1)
        if approve_voice_channel.overwrites_for(member_role).view_channel != False:
            await approve_voice_channel.set_permissions(
                member_role, view_channel=False, speak=False
            )

        if embed is not None:
            embed.add_field(
                name="Set all permissions",
                value="Set permissions for manual approval channels",
                inline=False,
            )
        return

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def init(self, ctx, args: str = ""):
        guild = ctx.message.guild
        role_set = False

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
        waiting_msg = None

        # create embed
        embed = discord.Embed(title="Setup", description="", color=color_done)

        def check(author):
            def inner_check(message):
                return message.author == author

            return inner_check

        # if user role is not set
        if user_id == 0:
            # create embed
            embed_brk = discord.Embed(title="Info", description="", color=color_done)
            embed_brk.add_field(
                name="No user role set",
                value="Reply to this message with your role name to set it as a user role",
                inline=False,
            )
            await ctx.send(embed=embed_brk)

            reply = await self.client.wait_for(
                "message", check=check(ctx.author), timeout=30
            )

            if reply is not None:
                content = reply.content

                # get existing role
                role_existing = discord.utils.get(guild.roles, name=content)

                role_everyone = guild.default_role

                if role_existing is not None or content == "everyone":
                    # create embed
                    embed = discord.Embed(
                        title="Done!", description="", color=color_done
                    )

                    # update file
                    with open(data_file, "r") as f:
                        guilds = json.load(f)

                    if content != "everyone":
                        await self.update_id_role(
                            guilds, guild, role_existing, "role_member"
                        )
                    elif content == "everyone":
                        await self.update_id_role(
                            guilds, guild, role_everyone, "role_member"
                        )

                    with open(data_file, "w") as f:
                        json.dump(guilds, f)

                    if content != "everyone":
                        embed.add_field(
                            name="User role set as",
                            value=role_existing.mention,
                            inline=False,
                        )
                    elif content == "everyone":
                        embed.add_field(
                            name="User role set as", value=role_everyone, inline=False
                        )

                    role_done = await ctx.send(embed=embed)
                    role_set = True
                    time.sleep(2)
                    await role_done.delete()
                    waiting_msg = await ctx.send(embed=embed_waiting)
                else:
                    # create embed
                    embed = discord.Embed(
                        title="Error", description="", color=color_errr
                    )
                    embed.add_field(
                        name="Could not find role", value=content, inline=False
                    )
                    await ctx.send(embed=embed)
                    return

        if role_set:
            # create role
            await self.create_role(
                ctx, "tao-approval", "role_approve", color_warn, embed
            )

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

            # update file
            with open(data_file, "r") as f:
                guilds = json.load(f)

            await self.update_data(guilds, guild)
            await self.update_state_config(guilds, guild, "setup_complete", True)

            with open(data_file, "w") as f:
                json.dump(guilds, f)

            await ctx.send(embed=embed)
            return
        elif not role_set and user_id != 0 and args == "-reset":
            # create role
            await self.create_role(
                ctx, "tao-approval", "role_approve", color_warn, embed
            )

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

            embed.add_field(name="Reset", value="Reset complete!", inline=False)

            await waiting_msg.delete()
            await ctx.send(embed=embed)
            return

    async def set_config(self, ctx, cfg: str = "", args: str = "", cfg_state: bool = False):
        guild = ctx.guild

        if args == "":
            embed_errr = discord.Embed(title="Error", description="", color=color_errr)
            embed_errr.add_field(
                name="Invalid argument",
                value="Available arguments: `-enable`, `-disable`",
                inline=False,
            )
            if cfg_state:
                embed_errr.add_field(
                    name="Current value",
                    value="`enabled`",
                    inline=False,
                )
            else:
                embed_errr.add_field(
                    name="Current value",
                    value="`disabled`",
                    inline=False,
                )
            await ctx.send(embed=embed_errr)
        if args == "-enable":
            if cfg_state == True:
                embed_warn = discord.Embed(
                    title="Info", description="", color=color_done
                )
                embed_warn.add_field(
                    name="Already enabled",
                    value="This function has already been enabled",
                    inline=False,
                )
                await ctx.send(embed=embed_warn)
            elif cfg_state == False:
                # update file
                with open(data_file, "r") as f:
                    guilds = json.load(f)

                await self.update_data(self, guilds, guild)
                if cfg == "-score":
                    await self.update_state_config(self, guilds, guild, "scre_enable", True)
                elif cfg == "-verbose":
                    await self.update_state_config(self, guilds, guild, "verbose_enable", True)
                elif cfg == "-late":
                    await self.update_state_config(self, guilds, guild, "late_enable", True)

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
            if cfg_state == False:
                embed_warn = discord.Embed(
                    title="Info", description="", color=color_done
                )
                embed_warn.add_field(
                    name="Already disabled",
                    value="This function has already been disabled",
                    inline=False,
                )
                await ctx.send(embed=embed_warn)
            elif cfg_state == True:
                # update file
                with open(data_file, "r") as f:
                    guilds = json.load(f)

                await self.update_data(self, guilds, guild)
                if cfg == "-score":
                    await self.update_state_config(self, guilds, guild, "scre_enable", False)
                elif cfg == "-verbose":
                    await self.update_state_config(self, guilds, guild, "verbose_enable", False)
                elif cfg == "-late":
                    await self.update_state_config(self, guilds, guild, "late_enable", False)

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


    @commands.command(pass_context=True)
    async def setup_notify(self, channel: discord.TextChannel):
        guild = channel.guild

        # update file
        with open("cogs/_guild.json", "r") as f:
            guilds = json.load(f)

        await self.update_data(self, guilds, guild)
        dont_send = guilds[str(guild.id)]["notified"]
        setup_complete = guilds[str(guild.id)]["setup_complete"]

        with open("cogs/_guild.json", "w") as f:
            json.dump(guilds, f)

        if not dont_send and not setup_complete:
            embed_errr = discord.Embed(title="WARNING!", description="", color=color_errr)
            embed_errr.add_field(
                name="Tao has not been set up yet!",
                value="Set Tao up using the command: `tao init`",
                inline=False,
            )
            await channel.send(embed=embed_errr)

            # update file
            with open("cogs/_guild.json", "r") as f:
                guilds = json.load(f)

            await self.update_data(self, guilds, guild)
            await self.update_state_config(self, guilds, guild, "notified", True)

            with open("cogs/_guild.json", "w") as f:
                json.dump(guilds, f)
        elif setup_complete:
            # update file
            with open("cogs/_guild.json", "r") as f:
                guilds = json.load(f)

            await self.update_data(self, guilds, guild)
            await self.update_state_config(self, guilds, guild, "notified", True)

            with open("cogs/_guild.json", "w") as f:
                json.dump(guilds, f)




def setup(client):
    client.add_cog(Data(client))
