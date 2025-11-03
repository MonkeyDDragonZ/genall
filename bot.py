import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime

from database import Database
from config import RANKS, SCORING
from onboarding import OnboardingModule, setup_onboarding_commands
from progression import ProgressionModule, setup_progression_commands
from elite_system import EliteSystemModule, setup_elite_commands
from decay import DecayModule, setup_decay_commands
from leadership import LeadershipModule, setup_leadership_commands

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.invites = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

voice_sessions = {}
guild_invites = {}

onboarding = OnboardingModule(bot)
progression = ProgressionModule(bot)
elite_system = EliteSystemModule(bot)
decay = DecayModule(bot)
leadership = LeadershipModule(bot)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

    for guild in bot.guilds:
        try:
            guild_invites[guild.id] = await guild.invites()
        except discord.Forbidden:
            print(f"Cannot fetch invites for {guild.name} - missing permissions")
            guild_invites[guild.id] = []


@bot.event
async def on_member_join(member: discord.Member):
    await onboarding.welcome_member(member)

    guild = member.guild

    try:
        new_invites = await guild.invites()
        old_invites = guild_invites.get(guild.id, [])

        for new_invite in new_invites:
            for old_invite in old_invites:
                if new_invite.code == old_invite.code and new_invite.uses > old_invite.uses:
                    inviter = new_invite.inviter
                    if inviter and not inviter.bot:
                        Database.increment_stat(str(inviter.id), inviter.name, str(guild.id), 'invite_count')
                        print(f"{inviter.name} invited {member.name}")
                    break

        guild_invites[guild.id] = new_invites
    except discord.Forbidden:
        print(f"Cannot track invites for {guild.name} - missing permissions")


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    guild_id = str(member.guild.id)
    user_id = str(member.id)
    session_key = f"{guild_id}_{user_id}"

    if before.channel is None and after.channel is not None:
        voice_sessions[session_key] = datetime.utcnow()
        print(f"{member.name} joined voice channel")

    elif before.channel is not None and after.channel is None:
        if session_key in voice_sessions:
            join_time = voice_sessions[session_key]
            duration = (datetime.utcnow() - join_time).total_seconds()
            del voice_sessions[session_key]

            user_stats = Database.get_user_stats(user_id, guild_id)
            if user_stats:
                current_time = user_stats.get('voice_time_seconds', 0)
                Database.update_user_stats(user_id, guild_id, {
                    'voice_time_seconds': current_time + int(duration),
                    'discord_username': member.name
                })
            else:
                Database.create_user_stats(user_id, member.name, guild_id)
                Database.update_user_stats(user_id, guild_id, {
                    'voice_time_seconds': int(duration)
                })

            print(f"{member.name} left voice channel after {int(duration)} seconds")


@bot.event
async def on_message(message):
    if message.author.bot:
        await bot.process_commands(message)
        return

    if not message.guild:
        await bot.process_commands(message)
        return

    user_id = str(message.author.id)
    username = message.author.name
    guild_id = str(message.guild.id)

    Database.increment_stat(user_id, username, guild_id, 'message_count')

    await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if not reaction.message.guild:
        return

    user_id = str(user.id)
    guild_id = str(reaction.message.guild.id)

    Database.increment_stat(user_id, user.name, guild_id, 'reaction_count')


@bot.event
async def on_invite_create(invite):
    guild_invites[invite.guild.id] = await invite.guild.invites()


@bot.command(name='stats')
async def stats(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_id = str(member.id)
    guild_id = str(ctx.guild.id)

    user_stats = Database.get_user_stats(user_id, guild_id)

    if not user_stats:
        await ctx.send(f"No stats found for {member.display_name}")
        return

    voice_hours = user_stats.get('voice_time_seconds', 0) / 3600
    rank = user_stats.get('rank', 1)
    elite_type = user_stats.get('elite_type')

    rank_name = RANKS[rank]['name']
    if elite_type and rank == 5:
        from config import ELITE_TYPES
        rank_name += f" - {ELITE_TYPES[elite_type]['name']}"

    embed = discord.Embed(
        title=f"Stats for {member.display_name}",
        description=f"Rank: **{rank_name}**",
        color=RANKS[rank]['color']
    )

    score = progression.calculate_user_score(user_stats)
    embed.add_field(name="Overall Score", value=f"{score} pts", inline=False)

    embed.add_field(name="Voice Time", value=f"{voice_hours:.2f} hours", inline=True)
    embed.add_field(name="Messages", value=str(user_stats.get('message_count', 0)), inline=True)
    embed.add_field(name="Invites", value=str(user_stats.get('invite_count', 0)), inline=True)

    embed.add_field(name="Reactions", value=str(user_stats.get('reaction_count', 0)), inline=True)
    embed.add_field(name="Videos Shared", value=str(user_stats.get('videos_shared', 0)), inline=True)
    embed.add_field(name="Subject Posts", value=str(user_stats.get('subject_posts', 0)), inline=True)

    embed.add_field(name="Voice Sessions Hosted", value=str(user_stats.get('voice_sessions_hosted', 0)), inline=True)
    embed.add_field(name="Validations", value=str(user_stats.get('advisor_validations', 0)), inline=True)

    if user_stats.get('is_immune_to_decay', False):
        embed.add_field(name="Decay Immunity", value="✅ Immune", inline=True)

    await ctx.send(embed=embed)


@bot.command(name='add_video')
async def add_video(ctx):
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    Database.increment_stat(user_id, ctx.author.name, guild_id, 'videos_shared')

    await ctx.send(f"{ctx.author.mention} video recorded! (+{SCORING['video_per_count']} points)")


@bot.command(name='add_subject')
async def add_subject(ctx):
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    Database.increment_stat(user_id, ctx.author.name, guild_id, 'subject_posts')

    await ctx.send(f"{ctx.author.mention} subject post recorded! (+{SCORING['subject_post_per_count']} points)")


@bot.command(name='add_session')
async def add_session(ctx):
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    Database.increment_stat(user_id, ctx.author.name, guild_id, 'voice_sessions_hosted')

    await ctx.send(f"{ctx.author.mention} voice session recorded! (+{SCORING['voice_session_hosted']} points)")


@bot.command(name='ranks')
async def ranks_info(ctx):
    embed = discord.Embed(
        title="Ranking System",
        description="All available ranks in the server",
        color=discord.Color.blue()
    )

    for rank_level, rank_info in RANKS.items():
        embed.add_field(
            name=f"{rank_level}. {rank_info['name']}",
            value=rank_info['description'],
            inline=False
        )

    await ctx.send(embed=embed)


@bot.command(name='help_bot')
async def help_bot(ctx):
    embed = discord.Embed(
        title="Discord Ranking Bot - Commands",
        description="Complete command list organized by category",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="User Commands",
        value="`!stats [@user]` - View user statistics\n"
              "`!progress [@user]` - View promotion progress\n"
              "`!contribute` - Request to become a Learner\n"
              "`!add_video` - Log a shared video\n"
              "`!add_subject` - Log a subject post\n"
              "`!add_session` - Log a hosted voice session",
        inline=False
    )

    embed.add_field(
        name="Leaderboards",
        value="`!leaderboard [all|voice|messages|invites]` - View rankings\n"
              "`!ranks` - View all rank information",
        inline=False
    )

    embed.add_field(
        name="Elite & Leadership",
        value="`!elite_list` - View Elite members\n"
              "`!elite_info` - Elite system information\n"
              "`!leadership` - View current leaders\n"
              "`!validate @user` - Validate user for promotion (Advisor/Ruler only)",
        inline=False
    )

    embed.add_field(
        name="Decay System",
        value="`!decay_info` - View decay system information\n"
              "`!decay_status [@user]` - Check decay status",
        inline=False
    )

    embed.add_field(
        name="Admin Commands",
        value="`!approve_learner @user` - Approve Viewer → Learner\n"
              "`!promote @user` - Promote user to next rank\n"
              "`!elite_assign @user [solid|pillar|team_x]` - Assign Elite type\n"
              "`!assign_advisor @user` - Assign Advisor role\n"
              "`!assign_ruler @user` - Assign Ruler role\n"
              "`!remove_advisor @user` - Remove Advisor\n"
              "`!remove_ruler @user` - Remove Ruler\n"
              "`!force_decay` - Run decay check manually",
        inline=False
    )

    await ctx.send(embed=embed)


setup_onboarding_commands(bot, onboarding)
setup_progression_commands(bot, progression)
setup_elite_commands(bot, elite_system)
setup_decay_commands(bot, decay)
setup_leadership_commands(bot, leadership)


if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
