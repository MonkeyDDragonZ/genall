import os
from supabase import create_client, Client
from datetime import datetime
from typing import Optional, Dict, Any, List

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class Database:

    @staticmethod
    def get_user_stats(discord_user_id: str, guild_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = supabase.table('user_stats').select('*').eq('discord_user_id', discord_user_id).eq('guild_id', guild_id).maybeSingle().execute()
            return result.data
        except Exception as e:
            print(f"Error fetching user stats: {e}")
            return None

    @staticmethod
    def create_user_stats(discord_user_id: str, username: str, guild_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = supabase.table('user_stats').insert({
                'discord_user_id': discord_user_id,
                'discord_username': username,
                'guild_id': guild_id,
                'rank': 1,
                'voice_time_seconds': 0,
                'message_count': 0,
                'invite_count': 0,
                'reaction_count': 0,
                'subject_posts': 0,
                'subject_reactions': 0,
                'voice_sessions_hosted': 0,
                'videos_shared': 0,
                'wants_to_contribute': False,
                'advisor_validations': 0,
                'last_activity': datetime.utcnow().isoformat(),
                'is_immune_to_decay': False
            }).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user stats: {e}")
            return None

    @staticmethod
    def update_user_stats(discord_user_id: str, guild_id: str, updates: Dict[str, Any]) -> bool:
        try:
            updates['last_activity'] = datetime.utcnow().isoformat()
            supabase.table('user_stats').update(updates).eq('discord_user_id', discord_user_id).eq('guild_id', guild_id).execute()
            return True
        except Exception as e:
            print(f"Error updating user stats: {e}")
            return False

    @staticmethod
    def increment_stat(discord_user_id: str, username: str, guild_id: str, stat_name: str, amount: int = 1) -> bool:
        try:
            user_stats = Database.get_user_stats(discord_user_id, guild_id)

            if not user_stats:
                user_stats = Database.create_user_stats(discord_user_id, username, guild_id)
                if not user_stats:
                    return False

            current_value = user_stats.get(stat_name, 0)
            updates = {
                stat_name: current_value + amount,
                'discord_username': username
            }

            return Database.update_user_stats(discord_user_id, guild_id, updates)
        except Exception as e:
            print(f"Error incrementing stat {stat_name}: {e}")
            return False

    @staticmethod
    def get_all_users_in_guild(guild_id: str) -> List[Dict[str, Any]]:
        try:
            result = supabase.table('user_stats').select('*').eq('guild_id', guild_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching all users: {e}")
            return []

    @staticmethod
    def get_users_by_rank(guild_id: str, rank: int) -> List[Dict[str, Any]]:
        try:
            result = supabase.table('user_stats').select('*').eq('guild_id', guild_id).eq('rank', rank).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching users by rank: {e}")
            return []

    @staticmethod
    def create_promotion_request(discord_user_id: str, guild_id: str, current_rank: int, target_rank: int, validations_needed: int) -> Optional[Dict[str, Any]]:
        try:
            result = supabase.table('promotion_requests').insert({
                'discord_user_id': discord_user_id,
                'guild_id': guild_id,
                'current_rank': current_rank,
                'target_rank': target_rank,
                'validations_received': 0,
                'validations_needed': validations_needed,
                'status': 'pending'
            }).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating promotion request: {e}")
            return None

    @staticmethod
    def get_pending_promotion_request(discord_user_id: str, guild_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = supabase.table('promotion_requests').select('*').eq('discord_user_id', discord_user_id).eq('guild_id', guild_id).eq('status', 'pending').maybeSingle().execute()
            return result.data
        except Exception as e:
            print(f"Error fetching promotion request: {e}")
            return None

    @staticmethod
    def update_promotion_request(request_id: str, updates: Dict[str, Any]) -> bool:
        try:
            supabase.table('promotion_requests').update(updates).eq('id', request_id).execute()
            return True
        except Exception as e:
            print(f"Error updating promotion request: {e}")
            return False

    @staticmethod
    def add_validation(discord_user_id: str, guild_id: str) -> bool:
        try:
            user_stats = Database.get_user_stats(discord_user_id, guild_id)
            if not user_stats:
                return False

            current_validations = user_stats.get('advisor_validations', 0)
            return Database.update_user_stats(discord_user_id, guild_id, {
                'advisor_validations': current_validations + 1
            })
        except Exception as e:
            print(f"Error adding validation: {e}")
            return False

    @staticmethod
    def get_leadership_roles(guild_id: str, role_type: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            query = supabase.table('leadership_roles').select('*').eq('guild_id', guild_id)
            if role_type:
                query = query.eq('role_type', role_type)
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching leadership roles: {e}")
            return []

    @staticmethod
    def assign_leadership_role(discord_user_id: str, guild_id: str, role_type: str) -> bool:
        try:
            supabase.table('leadership_roles').insert({
                'discord_user_id': discord_user_id,
                'guild_id': guild_id,
                'role_type': role_type
            }).execute()
            return True
        except Exception as e:
            print(f"Error assigning leadership role: {e}")
            return False

    @staticmethod
    def remove_leadership_role(discord_user_id: str, guild_id: str, role_type: str) -> bool:
        try:
            supabase.table('leadership_roles').delete().eq('discord_user_id', discord_user_id).eq('guild_id', guild_id).eq('role_type', role_type).execute()
            return True
        except Exception as e:
            print(f"Error removing leadership role: {e}")
            return False

    @staticmethod
    def is_leader(discord_user_id: str, guild_id: str) -> bool:
        try:
            result = supabase.table('leadership_roles').select('*').eq('discord_user_id', discord_user_id).eq('guild_id', guild_id).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"Error checking leadership status: {e}")
            return False

    @staticmethod
    def get_inactive_users(guild_id: str, days: int) -> List[Dict[str, Any]]:
        try:
            from datetime import timedelta
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            result = supabase.table('user_stats').select('*').eq('guild_id', guild_id).lt('last_activity', cutoff_date).eq('is_immune_to_decay', False).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching inactive users: {e}")
            return []
