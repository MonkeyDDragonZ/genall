import discord
from discord.ext import commands
from database import Database
from config import RANKS
from typing import Optional


class OnboardingModule:

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def welcome_member(self, member: discord.Member):
        user_stats = Database.get_user_stats(str(member.id), str(member.guild.id))

        if not user_stats:
            Database.create_user_stats(str(member.id), member.name, str(member.guild.id))

        await self.assign_viewer_role(member)

        welcome_channel = self.get_welcome_channel(member.guild)
        if welcome_channel:
            embed = discord.Embed(
                title=f"Welcome {member.name}!",
                description=f"You have been assigned the **{RANKS[1]['name']}** rank.\n\n"
                           f"{RANKS[1]['description']}\n\n"
                           f"Complete your onboarding and use `!contribute` when ready to become a Learner!",
                color=RANKS[1]['color']
            )
            await welcome_channel.send(embed=embed)

    async def assign_viewer_role(self, member: discord.Member):
        viewer_role = discord.utils.get(member.guild.roles, name=RANKS[1]['name'])

        if not viewer_role:
            viewer_role = await self.create_rank_role(member.guild, 1)

        if viewer_role and viewer_role not in member.roles:
            try:
                await member.add_roles(viewer_role)
            except discord.Forbidden:
                print(f"Missing permissions to assign role in {member.guild.name}")

    async def create_rank_role(self, guild: discord.Guild, rank: int) -> Optional[discord.Role]:
        rank_info = RANKS.get(rank)
        if not rank_info:
            return None

        try:
            role = await guild.create_role(
                name=rank_info['name'],
                color=discord.Color(rank_info['color']),
                mentionable=True
            )
            return role
        except discord.Forbidden:
            print(f"Missing permissions to create role in {guild.name}")
            return None

    def get_welcome_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        welcome_channels = ['welcome', 'general', 'lobby']

        for channel_name in welcome_channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                return channel

        if guild.text_channels:
            return guild.text_channels[0]

        return None

    async def handle_contribute_button(self, user_id: str, username: str, guild_id: str) -> tuple[bool, str]:
        user_stats = Database.get_user_stats(user_id, guild_id)

        if not user_stats:
            return False, "User stats not found. Please contact an admin."

        if user_stats['rank'] != 1:
            return False, f"You are already a {RANKS[user_stats['rank']]['name']}!"

        if user_stats.get('wants_to_contribute', False):
            return False, "You have already pressed the contribute button!"

        Database.update_user_stats(user_id, guild_id, {
            'wants_to_contribute': True
        })

        return True, "Thank you for wanting to contribute! An admin will review your request."

    async def promote_to_learner(self, member: discord.Member) -> bool:
        user_id = str(member.id)
        guild_id = str(member.guild.id)

        user_stats = Database.get_user_stats(user_id, guild_id)

        if not user_stats:
            return False

        if user_stats['rank'] != 1:
            return False

        if not user_stats.get('wants_to_contribute', False):
            return False

        Database.update_user_stats(user_id, guild_id, {
            'rank': 2
        })

        viewer_role = discord.utils.get(member.guild.roles, name=RANKS[1]['name'])
        learner_role = discord.utils.get(member.guild.roles, name=RANKS[2]['name'])

        if not learner_role:
            learner_role = await self.create_rank_role(member.guild, 2)

        try:
            if viewer_role and viewer_role in member.roles:
                await member.remove_roles(viewer_role)
            if learner_role:
                await member.add_roles(learner_role)
        except discord.Forbidden:
            print(f"Missing permissions to update roles in {member.guild.name}")

        return True


def setup_onboarding_commands(bot: commands.Bot, onboarding: OnboardingModule):

    @bot.command(name='contribute')
    async def contribute(ctx):
        success, message = await onboarding.handle_contribute_button(
            str(ctx.author.id),
            ctx.author.name,
            str(ctx.guild.id)
        )

        if success:
            embed = discord.Embed(
                title="Contribution Request Received",
                description=message,
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="Request Failed",
                description=message,
                color=discord.Color.red()
            )

        await ctx.send(embed=embed)

    @bot.command(name='approve_learner')
    @commands.has_permissions(administrator=True)
    async def approve_learner(ctx, member: discord.Member):
        success = await onboarding.promote_to_learner(member)

        if success:
            embed = discord.Embed(
                title="Promotion Successful",
                description=f"{member.mention} has been promoted to **{RANKS[2]['name']}**!",
                color=RANKS[2]['color']
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to promote user. Check if they are a Viewer and have requested to contribute.")
