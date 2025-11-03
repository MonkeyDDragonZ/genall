RANKS = {
    1: {
        'name': 'Viewer',
        'description': 'Entry-level; basic member after onboarding.',
        'color': 0x95a5a6
    },
    2: {
        'name': 'Learner',
        'description': 'Shows curiosity and initial participation.',
        'color': 0x3498db
    },
    3: {
        'name': 'Member',
        'description': 'Active participant in text and voice.',
        'color': 0x2ecc71
    },
    4: {
        'name': 'Contributor',
        'description': 'Gains right to vote.',
        'color': 0xf39c12
    },
    5: {
        'name': 'Elite',
        'description': 'Divided into Solid, Pillar, and Team X. Immune to point decay.',
        'color': 0xe74c3c,
        'subtypes': ['solid', 'pillar', 'team_x']
    },
    6: {
        'name': 'Advisor',
        'description': 'Senior mentors; max 4. Assist and advise.',
        'color': 0x9b59b6,
        'max_slots': 4
    },
    7: {
        'name': 'Ruler',
        'description': 'The single leader responsible for major decisions.',
        'color': 0xf1c40f,
        'max_slots': 1
    }
}

PROMOTION_REQUIREMENTS = {
    2: {
        'from_rank': 1,
        'to_rank': 2,
        'name': 'Viewer → Learner',
        'requirements': {
            'wants_to_contribute': True,
            'description': 'Show respect and work ethics + press button "I want to contribute"'
        }
    },
    3: {
        'from_rank': 2,
        'to_rank': 3,
        'name': 'Learner → Member',
        'requirements': {
            'voice_time_hours': 1,
            'message_count': 50,
            'reaction_count': 10,
            'invite_count': 5,
            'subject_posts': 1,
            'description': '1 hour talk + 50 messages + 10 reactions + 5 invites + 1 subject post'
        }
    },
    4: {
        'from_rank': 3,
        'to_rank': 4,
        'name': 'Member → Contributor',
        'requirements': {
            'voice_time_hours': 2,
            'invite_count': 15,
            'message_count': 150,
            'reaction_count': 20,
            'subject_posts': 1,
            'subject_reactions': 5,
            'voice_sessions_hosted': 1,
            'videos_shared': 5,
            'advisor_validations': 1,
            'description': '2 hours talk + 15 invites + 150 texts + 20 reactions + 1 subject (5 reactions) + host 1 voice + 5 videos + Advisor/Ruler validation'
        }
    },
    5: {
        'from_rank': 4,
        'to_rank': 5,
        'name': 'Contributor → Elite',
        'requirements': {
            'voice_time_hours': 5,
            'invite_count': 25,
            'message_count': 300,
            'reaction_count': 100,
            'videos_shared': 25,
            'advisor_validations': 2,
            'description': '5 hours talk + 25 invites + 300 texts + 100 reactions + 25 videos + 2 Advisor/Ruler validations'
        }
    }
}

SCORING = {
    'voice_per_hour': 10,
    'message_per_count': 0.1,
    'invite_per_count': 20,
    'reaction_per_count': 0.5,
    'video_per_count': 2,
    'subject_post_per_count': 5,
    'voice_session_hosted': 10
}

DECAY_SETTINGS = {
    'inactive_days': 7,
    'decay_percentage': 10,
    'check_interval_hours': 24,
    'immune_ranks': [5, 6, 7]
}

ELITE_TYPES = {
    'solid': {
        'name': 'Solid',
        'description': 'Reliable and consistent Elite member'
    },
    'pillar': {
        'name': 'Pillar',
        'description': 'Core support Elite member'
    },
    'team_x': {
        'name': 'Team X',
        'description': 'Exceptional Elite member'
    }
}
