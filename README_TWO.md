# 🎮 Discord Ranking Bot

> 🚀 A powerful 7-tier ranking system for Discord communities!

## 🏆 Ranking Tiers

| Rank | Name | Description |
|------|------|-------------|
| 1️⃣ | **Viewer** | 👋 Entry-level member |
| 2️⃣ | **Learner** | 📚 Curious participant |
| 3️⃣ | **Member** | 💬 Active contributor |
| 4️⃣ | **Contributor** | 🗳️ Voting rights |
| 5️⃣ | **Elite** | ⭐ Immune to decay |
| 6️⃣ | **Advisor** | 👨‍🏫 Senior mentor (max 4) |
| 7️⃣ | **Ruler** | 👑 Server leader (max 1) |

## 📈 Promotion Path

### 1️⃣ → 2️⃣ Viewer → Learner
- ✅ Show respect
- 🔘 Press `!contribute`

### 2️⃣ → 3️⃣ Learner → Member
- 🎤 1 hour voice
- 💬 50 messages
- ❤️ 10 reactions
- 📨 5 invites
- 📝 1 subject post

### 3️⃣ → 4️⃣ Member → Contributor
- 🎤 2 hours voice
- 💬 150 messages
- ❤️ 20 reactions
- 📨 15 invites
- 📝 1 subject (5 reactions)
- 🎙️ Host 1 session
- 📹 5 videos
- ✅ 1 validation

### 4️⃣ → 5️⃣ Contributor → Elite
- 🎤 5 hours voice
- 💬 300 messages
- ❤️ 100 reactions
- 📨 25 invites
- 📹 25 videos
- ✅ 2 validations

## 💯 Scoring System

| Activity | Points |
|----------|--------|
| 🎤 Voice Time | 10 pts/hour |
| 💬 Message | 0.1 pts/msg |
| 📨 Invite | 20 pts/invite |
| ❤️ Reaction | 0.5 pts/reaction |
| 📹 Video | 2 pts/video |
| 📝 Subject Post | 5 pts/post |
| 🎙️ Voice Session | 10 pts/session |

## ⚡ Features

- 📊 **Real-time Tracking** - All activities monitored
- 🗃️ **Supabase Storage** - Persistent data
- 🏅 **Multiple Leaderboards** - Voice, messages, invites, overall
- ⏰ **Auto Decay** - 10% decay after 7 days inactive
- 🛡️ **Elite Immunity** - Ranks 5-7 immune to decay
- 🎯 **Progress Tracking** - Know your next goal
- 👥 **Leadership System** - Advisors & Ruler

## �� Elite Types

- 💎 **Solid** - Reliable member
- 🏛️ **Pillar** - Core support
- ⚡ **Team X** - Exceptional

## 🎮 Quick Commands

### 👤 User
- `!stats` - 📊 View your stats
- `!progress` - 📈 Check promotion progress
- `!contribute` - 🔘 Become Learner
- `!add_video` - 📹 Log video
- `!add_subject` - 📝 Log subject post
- `!add_session` - 🎙️ Log voice session

### 🏆 Leaderboards
- `!leaderboard` - 🥇 View rankings
- `!ranks` - 📋 All ranks info

### ⭐ Elite & Leadership
- `!elite_list` - ⭐ Elite members
- `!leadership` - 👑 Current leaders
- `!validate @user` - ✅ Validate promotion

### 🔄 Decay
- `!decay_info` - ℹ️ Decay system
- `!decay_status` - 📉 Check decay

### 🛠️ Admin
- `!approve_learner @user` - 2️⃣ Approve Learner
- `!promote @user` - ⬆️ Promote user
- `!elite_assign @user solid` - ⭐ Assign Elite type
- `!assign_advisor @user` - 👨‍🏫 Make Advisor
- `!assign_ruler @user` - 👑 Make Ruler
- `!help_bot` - 📖 All commands

## 🚀 Quick Setup

1. 📦 `pip install -r requirements.txt`
2. 🔑 Add `DISCORD_TOKEN` to `.env`
3. ▶️ `python bot.py`

## 📂 Modules

| File | Purpose |
|------|---------|
| 🤖 `bot.py` | Main bot |
| ⚙️ `config.py` | Settings |
| 💾 `database.py` | Database ops |
| 👋 `onboarding.py` | Welcome system |
| 📈 `progression.py` | Rank tracking |
| ⭐ `elite_system.py` | Elite management |
| ⏰ `decay.py` | Point decay |
| 👑 `leadership.py` | Advisors & Ruler |

## 🎯 Key Benefits

- ✅ Encourages active participation
- ✅ Clear progression path
- ✅ Reward loyal members
- ✅ Automated rank management
- ✅ Fair decay system
- ✅ Leadership structure

---

**Made with ❤️ for Discord communities** 🎉
