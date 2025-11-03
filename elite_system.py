import discord
from discord.ext import commands
from database import Database
from config import RANKS, ELITE_TYPES
from typing import Optional


class EliteSystemModule:

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def assign_elite_type(self, member: discord.Member, elite_type: str) -> bool:
        user_id = str(member.id)
        guild_id = str(member.guild.id)

        user_stats = Database.get_user_stats(user_id, guild_id)

        if not user_stats:
            return False

        if user_stats['rank'] != 5:
            return False

        if elite_type not in ELITE_TYPES:
            return False

        Database.update_user_stats(user_id, guild_id, {
            'elite_type': elite_type,
            'is_immune_to_decay': True
        })

        await self.update_elite_role(member, elite_type)

        return True

    async def update_elite_role(self, member: discord.Member, elite_type: str):
        elite_role_name = f"Elite - {ELITE_TYPES[elite_type]['name']}"
        elite_role = discord.utils.get(member.guild.roles, name=elite_role_name)

        if not elite_role:
            try:
                elite_role = await member.guild.create_role(
                    name=elite_role_name,
                    color=discord.Color(RANKS[5]['color']),
                    mentionable=True
                )
            except discord.Forbidden:
                print(f"Missing permissions to create elite role in {member.guild.name}")
                return

        for et in ELITE_TYPES.keys():
            old_role_name = f"Elite - {ELITE_TYPES[et]['name']}"
            old_role = discord.utils.get(member.guild.roles, name=old_role_name)
            if old_role and old_role in member.roles:
                try:
                    await member.remove_roles(old_role)
                except discord.Forbidden:
                    print(f"Missing permissions to remove role in {member.guild.name}")

        if elite_role and elite_role not in member.roles:
            try:
                await member.add_roles(elite_role)
            except discord.Forbidden:
                print(f"Missing permissions to add elite role in {member.guild.name}")

    def get_elite_members(self, guild_id: str) -> list:
        users = Database.get_users_by_rank(guild_id, 5)
        return users

    def get_elite_stats_embed(self, guild: discord.Guild) -> discord.Embed:
        guild_id = str(guild.id)
        elite_members = self.get_elite_members(guild_id)

        embed = discord.Embed(
            title="Elite Members",
            description=f"Total Elite Members: {len(elite_members)}",
            color=RANKS[5]['color']
        )

        if not elite_members:
            embed.add_field(
                name="No Elite Members",
                value="Be the first to reach Elite rank!",
                inline=False
            )
            return embed

        solid_members = [u for u in elite_members if u.get('elite_type') == 'solid']
        pillar_members = [u for u in elite_members if u.get('elite_type') == 'pillar']
        team_x_members = [u for u in elite_members if u.get('elite_type') == 'team_x']
        unassigned = [u for u in elite_members if not u.get('elite_type')]

        if solid_members:
            solid_names = '\n'.join([u['discord_username'] for u in solid_members])
            embed.add_field(name=f"Solid ({len(solid_members)})", value=solid_names, inline=True)

        if pillar_members:
            pillar_names = '\n'.join([u['discord_username'] for u in pillar_members])
            embed.add_field(name=f"Pillar ({len(pillar_members)})", value=pillar_names, inline=True)

        if team_x_members:
            team_x_names = '\n'.join([u['discord_username'] for u in team_x_members])
            embed.add_field(name=f"Team X ({len(team_x_members)})", value=team_x_names, inline=True)

        if unassigned:
            unassigned_names = '\n'.join([u['discord_username'] for u in unassigned])
            embed.add_field(name=f"Unassigned ({len(unassigned)})", value=unassigned_names, inline=True)

        return embed

    async def check_and_grant_immunity(self, user_id: str, guild_id: str):
        user_stats = Database.get_user_stats(user_id, guild_id)

        if not user_stats:
            return

        rank = user_stats.get('rank', 1)

        if rank >= 5 and not user_stats.get('is_immune_to_decay', False):
            Database.update_user_stats(user_id, guild_id, {
                'is_immune_to_decay': True
            })


def setup_elite_commands(bot: commands.Bot, elite_system: EliteSystemModule):

    @bot.command(name='elite_assign')
    @commands.has_permissions(administrator=True)
    async def elite_assign(ctx, member: discord.Member, elite_type: str):
        elite_type = elite_type.lower()

        if elite_type not in ELITE_TYPES:
            valid_types = ', '.join(ELITE_TYPES.keys())
            await ctx.send(f"Invalid elite type. Valid types: {valid_types}")
            return

        success = await elite_system.assign_elite_type(member, elite_type)

        if success:
            embed = discord.Embed(
                title="Elite Type Assigned",
                description=f"{member.mention} has been assigned as **{ELITE_TYPES[elite_type]['name']}**!",
                color=RANKS[5]['color']
            )
            embed.add_field(
                name="Description",
                value=ELITE_TYPES[elite_type]['description'],
                inline=False
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Failed to assign elite type. Make sure {member.display_name} is an Elite member.")

    @bot.command(name='elite_list')
    async def elite_list(ctx):
        embed = elite_system.get_elite_stats_embed(ctx.guild)
        await ctx.send(embed=embed)

    @bot.command(name='elite_info')
    async def elite_info(ctx):
        embed = discord.Embed(
            title="Elite System Information",
            description="Elite members are immune to point decay and are divided into three subtypes:",
            color=RANKS[5]['color']
        )

        for elite_type, info in ELITE_TYPES.items():
            embed.add_field(
                name=info['name'],
                value=info['description'],
                inline=False
            )

        await ctx.send(embed=embed)
