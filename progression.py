import discord
from discord.ext import commands
from database import Database
from config import RANKS, PROMOTION_REQUIREMENTS, SCORING
from typing import Optional, Dict, Any, List


class ProgressionModule:

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def calculate_user_score(self, user_stats: Dict[str, Any]) -> float:
        voice_hours = user_stats.get('voice_time_seconds', 0) / 3600
        messages = user_stats.get('message_count', 0)
        invites = user_stats.get('invite_count', 0)
        reactions = user_stats.get('reaction_count', 0)
        videos = user_stats.get('videos_shared', 0)
        subjects = user_stats.get('subject_posts', 0)
        sessions = user_stats.get('voice_sessions_hosted', 0)

        score = (
            voice_hours * SCORING['voice_per_hour'] +
            messages * SCORING['message_per_count'] +
            invites * SCORING['invite_per_count'] +
            reactions * SCORING['reaction_per_count'] +
            videos * SCORING['video_per_count'] +
            subjects * SCORING['subject_post_per_count'] +
            sessions * SCORING['voice_session_hosted']
        )

        return round(score, 2)

    def check_promotion_eligibility(self, user_stats: Dict[str, Any]) -> tuple[bool, int, Dict[str, Any]]:
        current_rank = user_stats.get('rank', 1)

        if current_rank >= 5:
            return False, current_rank, {}

        target_rank = current_rank + 1
        requirements = PROMOTION_REQUIREMENTS.get(target_rank)

        if not requirements:
            return False, current_rank, {}

        reqs = requirements['requirements']
        voice_hours = user_stats.get('voice_time_seconds', 0) / 3600

        checks = {
            'voice_time_hours': voice_hours >= reqs.get('voice_time_hours', 0),
            'message_count': user_stats.get('message_count', 0) >= reqs.get('message_count', 0),
            'invite_count': user_stats.get('invite_count', 0) >= reqs.get('invite_count', 0),
            'reaction_count': user_stats.get('reaction_count', 0) >= reqs.get('reaction_count', 0),
            'subject_posts': user_stats.get('subject_posts', 0) >= reqs.get('subject_posts', 0),
            'subject_reactions': user_stats.get('subject_reactions', 0) >= reqs.get('subject_reactions', 0),
            'voice_sessions_hosted': user_stats.get('voice_sessions_hosted', 0) >= reqs.get('voice_sessions_hosted', 0),
            'videos_shared': user_stats.get('videos_shared', 0) >= reqs.get('videos_shared', 0),
            'wants_to_contribute': user_stats.get('wants_to_contribute', False) if 'wants_to_contribute' in reqs else True,
            'advisor_validations': user_stats.get('advisor_validations', 0) >= reqs.get('advisor_validations', 0)
        }

        progress = {}
        for key, passed in checks.items():
            if key in reqs:
                required = reqs[key]
                if key == 'voice_time_hours':
                    current = voice_hours
                elif key == 'wants_to_contribute':
                    current = user_stats.get(key, False)
                else:
                    current = user_stats.get(key, 0)
                progress[key] = {'required': required, 'current': current, 'passed': passed}

        all_passed = all(checks.values())

        return all_passed, target_rank, progress

    async def promote_user(self, member: discord.Member, new_rank: int) -> bool:
        user_id = str(member.id)
        guild_id = str(member.guild.id)

        Database.update_user_stats(user_id, guild_id, {'rank': new_rank})

        if new_rank == 5:
            Database.update_user_stats(user_id, guild_id, {'is_immune_to_decay': True})

        await self.update_user_roles(member, new_rank)

        return True

    async def update_user_roles(self, member: discord.Member, new_rank: int):
        for rank_level in range(1, 8):
            role = discord.utils.get(member.guild.roles, name=RANKS[rank_level]['name'])
            if role:
                try:
                    if rank_level == new_rank:
                        if role not in member.roles:
                            await member.add_roles(role)
                    else:
                        if role in member.roles:
                            await member.remove_roles(role)
                except discord.Forbidden:
                    print(f"Missing permissions to update roles in {member.guild.name}")

    def get_progress_embed(self, user_stats: Dict[str, Any], member: discord.Member) -> discord.Embed:
        current_rank = user_stats.get('rank', 1)
        eligible, target_rank, progress = self.check_promotion_eligibility(user_stats)

        embed = discord.Embed(
            title=f"Progress for {member.display_name}",
            description=f"Current Rank: **{RANKS[current_rank]['name']}**",
            color=RANKS[current_rank]['color']
        )

        score = self.calculate_user_score(user_stats)
        embed.add_field(name="Overall Score", value=f"{score} points", inline=False)

        if current_rank >= 5:
            embed.add_field(
                name="Status",
                value=f"You have reached **{RANKS[current_rank]['name']}** rank!",
                inline=False
            )
            return embed

        requirements = PROMOTION_REQUIREMENTS.get(target_rank)
        if not requirements:
            return embed

        embed.add_field(
            name=f"Progress to {RANKS[target_rank]['name']}",
            value="",
            inline=False
        )

        for key, data in progress.items():
            status = "✅" if data['passed'] else "❌"
            field_name = key.replace('_', ' ').title()

            if key == 'voice_time_hours':
                value = f"{status} {data['current']:.1f}/{data['required']} hours"
            elif key == 'wants_to_contribute':
                value = f"{status} {'Yes' if data['current'] else 'No'}"
            else:
                value = f"{status} {data['current']}/{data['required']}"

            embed.add_field(name=field_name, value=value, inline=True)

        if eligible:
            embed.add_field(
                name="Ready for Promotion!",
                value=f"You can be promoted to **{RANKS[target_rank]['name']}**!",
                inline=False
            )

        return embed

    def get_leaderboard_embed(self, guild: discord.Guild, category: str = 'all') -> discord.Embed:
        guild_id = str(guild.id)
        users = Database.get_all_users_in_guild(guild_id)

        if not users:
            return discord.Embed(
                title="Leaderboard",
                description="No users found!",
                color=discord.Color.red()
            )

        if category == 'voice':
            users.sort(key=lambda x: x.get('voice_time_seconds', 0), reverse=True)
            title = "Voice Time Leaderboard"
            value_fn = lambda x: f"{x.get('voice_time_seconds', 0) / 3600:.1f}h"
        elif category == 'messages':
            users.sort(key=lambda x: x.get('message_count', 0), reverse=True)
            title = "Messages Leaderboard"
            value_fn = lambda x: f"{x.get('message_count', 0)} msgs"
        elif category == 'invites':
            users.sort(key=lambda x: x.get('invite_count', 0), reverse=True)
            title = "Invites Leaderboard"
            value_fn = lambda x: f"{x.get('invite_count', 0)} invites"
        else:
            for user in users:
                user['score'] = self.calculate_user_score(user)
            users.sort(key=lambda x: x.get('score', 0), reverse=True)
            title = "Overall Leaderboard"
            value_fn = lambda x: f"{x.get('score', 0):.1f} pts"

        embed = discord.Embed(
            title=title,
            color=discord.Color.gold()
        )

        for i, user in enumerate(users[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            rank_name = RANKS[user.get('rank', 1)]['name']
            embed.add_field(
                name=f"{medal} {user['discord_username']} ({rank_name})",
                value=value_fn(user),
                inline=False
            )

        return embed


def setup_progression_commands(bot: commands.Bot, progression: ProgressionModule):

    @bot.command(name='progress')
    async def progress(ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_stats = Database.get_user_stats(str(member.id), str(ctx.guild.id))

        if not user_stats:
            await ctx.send(f"No stats found for {member.display_name}")
            return

        embed = progression.get_progress_embed(user_stats, member)
        await ctx.send(embed=embed)

    @bot.command(name='leaderboard')
    async def leaderboard(ctx, category: str = 'all'):
        embed = progression.get_leaderboard_embed(ctx.guild, category)
        await ctx.send(embed=embed)

    @bot.command(name='promote')
    @commands.has_permissions(administrator=True)
    async def promote_command(ctx, member: discord.Member):
        user_stats = Database.get_user_stats(str(member.id), str(ctx.guild.id))

        if not user_stats:
            await ctx.send(f"No stats found for {member.display_name}")
            return

        eligible, target_rank, progress = progression.check_promotion_eligibility(user_stats)

        if not eligible:
            embed = discord.Embed(
                title="Promotion Not Available",
                description=f"{member.display_name} does not meet the requirements yet.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        success = await progression.promote_user(member, target_rank)

        if success:
            embed = discord.Embed(
                title="Promotion Successful!",
                description=f"{member.mention} has been promoted to **{RANKS[target_rank]['name']}**!",
                color=RANKS[target_rank]['color']
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to promote user.")
