# Discord Ranking Bot

A comprehensive Python Discord bot featuring a 7-tier ranking system that tracks user engagement across multiple dimensions.

## Ranking System

### Ranks
1. **Viewer** - Entry-level; basic member after onboarding
2. **Learner** - Shows curiosity and initial participation
3. **Member** - Active participant in text and voice
4. **Contributor** - Gains right to vote
5. **Elite** - Divided into Solid, Pillar, and Team X. Immune to point decay
6. **Advisor** - Senior mentors (max 4). Assist and advise
7. **Ruler** - Single leader responsible for major decisions (max 1)

### Promotion Requirements

**Viewer → Learner**
- Show respect and work ethics
- Press "I want to contribute" button (`!contribute`)

**Learner → Member**
- 1 hour voice time
- 50 messages
- 10 reactions
- 5 invites
- 1 subject post

**Member → Contributor**
- 2 hours voice time
- 150 messages
- 20 reactions
- 15 invites
- 1 subject post with 5 reactions
- Host 1 voice session
- Share 5 videos
- 1 Advisor/Ruler validation

**Contributor → Elite**
- 5 hours voice time
- 300 messages
- 100 reactions
- 25 invites
- 25 videos shared
- 2 Advisor/Ruler validations

## Features

### Activity Tracking
- Voice channel time
- Text messages
- Reactions given
- Server invites
- Videos shared
- Subject posts
- Voice sessions hosted

### Scoring System
- Voice: 10 points/hour
- Messages: 0.1 points/message
- Invites: 20 points/invite
- Reactions: 0.5 points/reaction
- Videos: 2 points/video
- Subject Posts: 5 points/post
- Voice Sessions Hosted: 10 points/session

### Point Decay System
- Inactive users (7+ days) lose 10% of points every 24 hours
- Elite, Advisor, and Ruler ranks are immune to decay
- Encourages consistent participation

### Elite System
Three Elite subtypes:
- **Solid** - Reliable and consistent Elite member
- **Pillar** - Core support Elite member
- **Team X** - Exceptional Elite member

### Leadership
- **Advisors** - Maximum 4 members, can validate promotions
- **Ruler** - Single leader, can validate promotions

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Enable these Privileged Gateway Intents:
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT
   - PRESENCE INTENT
5. Copy your bot token
6. Go to OAuth2 > URL Generator
7. Select scopes: `bot`
8. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Manage Server (for invite tracking)
   - Manage Roles
   - Read Message History
   - Add Reactions
   - Connect (voice)
   - Speak (voice)
9. Use the generated URL to invite the bot to your server

### 3. Configure Environment Variables

Edit the `.env` file and add your Discord bot token:

```
DISCORD_TOKEN=your_discord_bot_token_here
```

The Supabase credentials are already configured.

### 4. Run the Bot

```bash
python bot.py
```

## Commands

### User Commands
- `!stats [@user]` - View user statistics
- `!progress [@user]` - View promotion progress
- `!contribute` - Request to become a Learner
- `!add_video` - Log a shared video
- `!add_subject` - Log a subject post
- `!add_session` - Log a hosted voice session

### Leaderboards
- `!leaderboard [all|voice|messages|invites]` - View rankings
- `!ranks` - View all rank information

### Elite & Leadership
- `!elite_list` - View Elite members
- `!elite_info` - Elite system information
- `!leadership` - View current leaders
- `!validate @user` - Validate user for promotion (Advisor/Ruler only)

### Decay System
- `!decay_info` - View decay system information
- `!decay_status [@user]` - Check decay status

### Admin Commands
- `!approve_learner @user` - Approve Viewer → Learner
- `!promote @user` - Promote user to next rank
- `!elite_assign @user [solid|pillar|team_x]` - Assign Elite type
- `!assign_advisor @user` - Assign Advisor role
- `!assign_ruler @user` - Assign Ruler role
- `!remove_advisor @user` - Remove Advisor
- `!remove_ruler @user` - Remove Ruler
- `!force_decay` - Run decay check manually
- `!help_bot` - Display all commands

## Architecture

The bot is built with a modular architecture:

- **bot.py** - Main bot file and event handlers
- **config.py** - Ranks, requirements, and scoring configuration
- **database.py** - Database operations and queries
- **onboarding.py** - Welcome and Viewer/Learner management
- **progression.py** - Progression tracking and promotion logic
- **elite_system.py** - Elite member management
- **decay.py** - Automatic point decay for inactive users
- **leadership.py** - Advisor and Ruler management

## Database Schema

The bot uses Supabase with the following tables:

**user_stats**
- All user activity metrics
- Current rank and elite type
- Decay immunity status
- Last activity timestamp

**promotion_requests**
- Tracks promotion requests requiring validation

**leadership_roles**
- Manages Advisor and Ruler assignments

## Permissions Required

The bot needs these permissions:
- Read Messages
- Send Messages
- Manage Server (for invite tracking)
- Manage Roles
- Add Reactions
- Connect to Voice Channels
- View Voice Channel Members
