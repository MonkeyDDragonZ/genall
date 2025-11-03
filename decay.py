import discord
from discord.ext import commands, tasks
from database import Database
from config import DECAY_SETTINGS, RANKS
from datetime import datetime, timedelta


class DecayModule:

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.decay_task.start()

    def cog_unload(self):
        self.decay_task.cancel()

    @tasks.loop(hours=DECAY_SETTINGS['check_interval_hours'])
    async def decay_task(self):
        print(f"Running decay check at {datetime.utcnow()}")

        for guild in self.bot.guilds:
            await self.process_guild_decay(guild)

    @decay_task.before_loop
    async def before_decay_task(self):
        await self.bot.wait_until_ready()

    async def process_guild_decay(self, guild: discord.Guild):
        guild_id = str(guild.id)
        inactive_days = DECAY_SETTINGS['inactive_days']

        inactive_users = Database.get_inactive_users(guild_id, inactive_days)

        if not inactive_users:
            return

        decay_percentage = DECAY_SETTINGS['decay_percentage']

        for user in inactive_users:
            user_id = user['discord_user_id']

            if user.get('is_immune_to_decay', False):
                continue

            if user.get('rank', 1) in DECAY_SETTINGS['immune_ranks']:
                continue

            await self.apply_decay(user_id, guild_id, decay_percentage)

        print(f"Processed decay for {len(inactive_users)} users in {guild.name}")

    async def apply_decay(self, user_id: str, guild_id: str, decay_percentage: int):
        user_stats = Database.get_user_stats(user_id, guild_id)

        if not user_stats:
            return

        decay_factor = (100 - decay_percentage) / 100

        new_stats = {
            'voice_time_seconds': int(user_stats.get('voice_time_seconds', 0) * decay_factor),
            'message_count': int(user_stats.get('message_count', 0) * decay_factor),
            'reaction_count': int(user_stats.get('reaction_count', 0) * decay_factor),
            'videos_shared': int(user_stats.get('videos_shared', 0) * decay_factor),
        }

        Database.update_user_stats(user_id, guild_id, new_stats)

        print(f"Applied {decay_percentage}% decay to user {user_id}")

    async def check_demotion(self, user_id: str, guild_id: str):
        user_stats = Database.get_user_stats(user_id, guild_id)

        if not user_stats:
            return

        current_rank = user_stats.get('rank', 1)

        if current_rank <= 2:
            return

        if user_stats.get('is_immune_to_decay', False):
            return

        from progression import ProgressionModule
        progression = ProgressionModule(self.bot)

        eligible, _, _ = progression.check_promotion_eligibility(user_stats)

        voice_hours = user_stats.get('voice_time_seconds', 0) / 3600
        messages = user_stats.get('message_count', 0)

        if voice_hours < 0.5 and messages < 10 and current_rank > 2:
            new_rank = current_rank - 1
            Database.update_user_stats(user_id, guild_id, {'rank': new_rank})

            member = await self.get_member(user_id, guild_id)
            if member:
                await self.notify_demotion(member, new_rank)

    async def get_member(self, user_id: str, guild_id: str) -> discord.Member:
        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            return None

        try:
            member = await guild.fetch_member(int(user_id))
            return member
        except discord.NotFound:
            return None

    async def notify_demotion(self, member: discord.Member, new_rank: int):
        try:
            embed = discord.Embed(
                title="Rank Update",
                description=f"Due to inactivity, you have been demoted to **{RANKS[new_rank]['name']}**.\n\n"
                           f"Stay active to maintain and improve your rank!",
                color=discord.Color.orange()
            )
            await member.send(embed=embed)
        except discord.Forbidden:
            print(f"Cannot send DM to {member.name}")

    def get_decay_info_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Point Decay System",
            description="Inactive users will experience point decay to encourage consistent participation.",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Inactivity Period",
            value=f"{DECAY_SETTINGS['inactive_days']} days",
            inline=True
        )

        embed.add_field(
            name="Decay Rate",
            value=f"{DECAY_SETTINGS['decay_percentage']}% per check",
            inline=True
        )

        embed.add_field(
            name="Check Frequency",
            value=f"Every {DECAY_SETTINGS['check_interval_hours']} hours",
            inline=True
        )

        immune_ranks = ', '.join([RANKS[r]['name'] for r in DECAY_SETTINGS['immune_ranks']])
        embed.add_field(
            name="Immune Ranks",
            value=immune_ranks,
            inline=False
        )

        embed.add_field(
            name="How to Avoid Decay",
            value="Stay active! Send messages, join voice channels, and participate in the community.",
            inline=False
        )

        return embed


def setup_decay_commands(bot: commands.Bot, decay: DecayModule):

    @bot.command(name='decay_info')
    async def decay_info(ctx):
        embed = decay.get_decay_info_embed()
        await ctx.send(embed=embed)

    @bot.command(name='decay_status')
    async def decay_status(ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_stats = Database.get_user_stats(str(member.id), str(ctx.guild.id))

        if not user_stats:
            await ctx.send(f"No stats found for {member.display_name}")
            return

        is_immune = user_stats.get('is_immune_to_decay', False)
        last_activity = user_stats.get('last_activity')

        if last_activity:
            last_active = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            days_inactive = (datetime.utcnow().replace(tzinfo=last_active.tzinfo) - last_active).days
        else:
            days_inactive = 0

        embed = discord.Embed(
            title=f"Decay Status - {member.display_name}",
            color=discord.Color.green() if is_immune or days_inactive < DECAY_SETTINGS['inactive_days'] else discord.Color.red()
        )

        embed.add_field(
            name="Immunity Status",
            value="Immune" if is_immune else "Not Immune",
            inline=True
        )

        embed.add_field(
            name="Days Since Last Activity",
            value=f"{days_inactive} days",
            inline=True
        )

        if not is_immune and days_inactive >= DECAY_SETTINGS['inactive_days']:
            embed.add_field(
                name="Warning",
                value=f"You are inactive and will lose {DECAY_SETTINGS['decay_percentage']}% of your points!",
                inline=False
            )

        await ctx.send(embed=embed)

    @bot.command(name='force_decay')
    @commands.has_permissions(administrator=True)
    async def force_decay(ctx):
        await ctx.send("Starting manual decay check...")
        await decay.process_guild_decay(ctx.guild)
        await ctx.send("Decay check completed!")
