class EvolutionSystem:
    """进阶系统 / Evolution System"""
    def __init__(self):
        self.evolution_paths = {
            "tanker": {
                "knight": {
                    "required_level": 10,
                    "stat_multipliers": {
                        "hp": 1.5,
                        "def": 1.3,
                        "atk": 1.2
                    },
                    "new_skills": ["shield_wall", "holy_protection"]
                }
            },
            "warrior": {
                "samurai": {
                    "required_level": 10,
                    "stat_multipliers": {
                        "atk": 1.4,
                        "spd": 1.3,
                        "crt": 1.2
                    },
                    "new_skills": ["blade_storm", "swift_strike"]
                }
            },
            "ranger": {
                "leaf_ranger": {
                    "required_level": 10,
                    "stat_multipliers": {
                        "atk": 1.3,
                        "spd": 1.4,
                        "evd": 1.3
                    },
                    "new_skills": ["precise_shot", "nature_call"]
                }
            }
        } 