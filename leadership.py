import discord
from discord.ext import commands
from database import Database
from config import RANKS
from typing import Optional


class LeadershipModule:

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def assign_advisor(self, member: discord.Member) -> tuple[bool, str]:
        user_id = str(member.id)
        guild_id = str(member.guild.id)

        current_advisors = Database.get_leadership_roles(guild_id, 'advisor')
        max_advisors = RANKS[6].get('max_slots', 4)

        if len(current_advisors) >= max_advisors:
            return False, f"Maximum number of Advisors ({max_advisors}) already reached."

        user_stats = Database.get_user_stats(user_id, guild_id)
        if not user_stats:
            return False, "User stats not found."

        if user_stats.get('rank', 1) < 5:
            return False, "User must be at least Elite rank to become an Advisor."

        success = Database.assign_leadership_role(user_id, guild_id, 'advisor')
        if not success:
            return False, "Failed to assign Advisor role in database."

        Database.update_user_stats(user_id, guild_id, {
            'rank': 6,
            'is_immune_to_decay': True
        })

        await self.update_leadership_discord_role(member, 6)

        return True, f"{member.display_name} has been assigned as an Advisor!"

    async def assign_ruler(self, member: discord.Member) -> tuple[bool, str]:
        user_id = str(member.id)
        guild_id = str(member.guild.id)

        current_rulers = Database.get_leadership_roles(guild_id, 'ruler')

        if len(current_rulers) >= 1:
            return False, "There can only be one Ruler. Remove the current Ruler first."

        user_stats = Database.get_user_stats(user_id, guild_id)
        if not user_stats:
            return False, "User stats not found."

        if user_stats.get('rank', 1) < 5:
            return False, "User must be at least Elite rank to become a Ruler."

        success = Database.assign_leadership_role(user_id, guild_id, 'ruler')
        if not success:
            return False, "Failed to assign Ruler role in database."

        Database.update_user_stats(user_id, guild_id, {
            'rank': 7,
            'is_immune_to_decay': True
        })

        await self.update_leadership_discord_role(member, 7)

        return True, f"{member.display_name} has been assigned as the Ruler!"

    async def remove_advisor(self, member: discord.Member) -> tuple[bool, str]:
        user_id = str(member.id)
        guild_id = str(member.guild.id)

        success = Database.remove_leadership_role(user_id, guild_id, 'advisor')
        if not success:
            return False, "Failed to remove Advisor role."

        Database.update_user_stats(user_id, guild_id, {
            'rank': 5
        })

        await self.update_leadership_discord_role(member, 5)

        return True, f"{member.display_name} has been removed from Advisor position."

    async def remove_ruler(self, member: discord.Member) -> tuple[bool, str]:
        user_id = str(member.id)
        guild_id = str(member.guild.id)

        success = Database.remove_leadership_role(user_id, guild_id, 'ruler')
        if not success:
            return False, "Failed to remove Ruler role."

        Database.update_user_stats(user_id, guild_id, {
            'rank': 5
        })

        await self.update_leadership_discord_role(member, 5)

        return True, f"{member.display_name} has been removed from Ruler position."

    async def update_leadership_discord_role(self, member: discord.Member, rank: int):
        for rank_level in [6, 7]:
            role = discord.utils.get(member.guild.roles, name=RANKS[rank_level]['name'])
            if not role:
                try:
                    role = await member.guild.create_role(
                        name=RANKS[rank_level]['name'],
                        color=discord.Color(RANKS[rank_level]['color']),
                        mentionable=True
                    )
                except discord.Forbidden:
                    print(f"Missing permissions to create role in {member.guild.name}")
                    continue

            if role:
                try:
                    if rank_level == rank:
                        if role not in member.roles:
                            await member.add_roles(role)
                    else:
                        if role in member.roles:
                            await member.remove_roles(role)
                except discord.Forbidden:
                    print(f"Missing permissions to update roles in {member.guild.name}")

    async def validate_promotion(self, validator: discord.Member, target: discord.Member) -> tuple[bool, str]:
        validator_id = str(validator.id)
        guild_id = str(validator.guild.id)

        if not Database.is_leader(validator_id, guild_id):
            return False, "Only Advisors and Rulers can validate promotions."

        target_id = str(target.id)
        success = Database.add_validation(target_id, guild_id)

        if not success:
            return False, "Failed to add validation."

        return True, f"Validation added for {target.display_name}!"

    def get_leadership_embed(self, guild: discord.Guild) -> discord.Embed:
        guild_id = str(guild.id)

        embed = discord.Embed(
            title="Leadership Structure",
            description=f"Current leadership in {guild.name}",
            color=RANKS[7]['color']
        )

        rulers = Database.get_leadership_roles(guild_id, 'ruler')
        if rulers:
            ruler_names = '\n'.join([f"<@{r['discord_user_id']}>" for r in rulers])
            embed.add_field(
                name=f"Ruler (1/{RANKS[7].get('max_slots', 1)})",
                value=ruler_names,
                inline=False
            )
        else:
            embed.add_field(
                name="Ruler",
                value="Position vacant",
                inline=False
            )

        advisors = Database.get_leadership_roles(guild_id, 'advisor')
        if advisors:
            advisor_names = '\n'.join([f"<@{a['discord_user_id']}>" for a in advisors])
            embed.add_field(
                name=f"Advisors ({len(advisors)}/{RANKS[6].get('max_slots', 4)})",
                value=advisor_names,
                inline=False
            )
        else:
            embed.add_field(
                name="Advisors",
                value="No advisors assigned",
                inline=False
            )

        return embed


def setup_leadership_commands(bot: commands.Bot, leadership: LeadershipModule):

    @bot.command(name='assign_advisor')
    @commands.has_permissions(administrator=True)
    async def assign_advisor(ctx, member: discord.Member):
        success, message = await leadership.assign_advisor(member)

        embed = discord.Embed(
            title="Advisor Assignment",
            description=message,
            color=discord.Color.green() if success else discord.Color.red()
        )

        await ctx.send(embed=embed)

    @bot.command(name='assign_ruler')
    @commands.has_permissions(administrator=True)
    async def assign_ruler(ctx, member: discord.Member):
        success, message = await leadership.assign_ruler(member)

        embed = discord.Embed(
            title="Ruler Assignment",
            description=message,
            color=discord.Color.green() if success else discord.Color.red()
        )

        await ctx.send(embed=embed)

    @bot.command(name='remove_advisor')
    @commands.has_permissions(administrator=True)
    async def remove_advisor(ctx, member: discord.Member):
        success, message = await leadership.remove_advisor(member)

        embed = discord.Embed(
            title="Advisor Removal",
            description=message,
            color=discord.Color.green() if success else discord.Color.red()
        )

        await ctx.send(embed=embed)

    @bot.command(name='remove_ruler')
    @commands.has_permissions(administrator=True)
    async def remove_ruler(ctx, member: discord.Member):
        success, message = await leadership.remove_ruler(member)

        embed = discord.Embed(
            title="Ruler Removal",
            description=message,
            color=discord.Color.green() if success else discord.Color.red()
        )

        await ctx.send(embed=embed)

    @bot.command(name='validate')
    async def validate(ctx, member: discord.Member):
        success, message = await leadership.validate_promotion(ctx.author, member)

        embed = discord.Embed(
            title="Promotion Validation",
            description=message,
            color=discord.Color.green() if success else discord.Color.red()
        )

        await ctx.send(embed=embed)

    @bot.command(name='leadership')
    async def leadership_info(ctx):
        embed = leadership.get_leadership_embed(ctx.guild)
        await ctx.send(embed=embed)
