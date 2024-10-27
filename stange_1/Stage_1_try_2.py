import json
import pandas as pd
import random
from abc import ABC, abstractmethod
from datetime import datetime

# Extract data from Excel
df = pd.read_excel("characters.xlsx")

# Game data storage class
class GameDataStorage:
    def __init__(self, json_file='game_data.json', log_file='battle_log.txt'):
        self.json_file = json_file
        self.log_file = log_file
        self.data = {
            "game_state": {},
            "battle_logs": []
        }
        self.log_buffer = []
        self.load_data()

    # Load data
    def load_data(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Data loaded from {self.json_file}")
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"{self.json_file} not found or format error, creating a new data file")
            self.save_data()

    # Save data
    def save_data(self):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {self.json_file}")

    # Log battle events
    def log_event(self, event: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {event}"
        self.data['battle_logs'].append(log_entry)
        self.log_buffer.append(log_entry)
        self.save_data()

    def flush_logs(self):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.writelines([entry + "\n" for entry in self.log_buffer])
        self.log_buffer.clear()
        print("Logs written to file")

    def update_game_state(self, key: str, value):
        self.data['game_state'][key] = value
        print(f"Game state updated: {key} = {value}")
        self.save_data()


# Abstract character interface
class CharacterInterface(ABC):
    @abstractmethod
    def show_attributes(self):
        pass

    @abstractmethod
    def attack(self, target):
        pass

    @abstractmethod
    def take_damage(self, damage):
        pass


# Character class
class Character(CharacterInterface):
    def __init__(self, character_type, name="Unnamed"):
        self.character_data = df[df.iloc[:, 0] == character_type].iloc[0]
        self.name = name
        self.hp = self.random_value("HP")
        self.atk = self.random_value("ATK")
        self.defense = self.random_value("DEF")
        self.crt = self.random_value("CRT", decimal=True)
        self.c_dmg = self.get_c_dmg()
        self.spd = self.random_value("SPD")
        self.evd = self.character_data["EVD"]
        self.ram_dmg_range = self.parse_range(self.character_data["RAM_DMG"])
        self.exp = 0
        self.rank = 1
        self.coins = 0

    def random_value(self, attribute, decimal=False):
        attr_value = str(self.character_data[attribute])
        if '~' not in attr_value:
            return round(float(attr_value.strip('%')) / 100, 2) if decimal else int(attr_value)
        start, end = map(float, attr_value.replace('%', '').split('~'))
        return round(random.uniform(start, end), 2) if decimal else random.randint(int(start), int(end))

    def parse_range(self, range_str):
        start, end = map(int, range_str.split("~"))
        return (start, end)

    def gain_exp(self, exp_gained, caused_damage):
        self.exp += exp_gained
        max_exp = 100 + (self.rank * 50)
        while self.exp >= max_exp:
            self.exp -= max_exp
            self.rank += 1
            self.update_attributes()
            max_exp = 100 + (self.rank * 50)

        self.coins += 10 if caused_damage > 0 else 5
        print(f"{self.name} gains {exp_gained} EXP and now has {self.exp}/{max_exp}. Coins: {self.coins}")

    def update_attributes(self):
        if self.character_data["type"] == "Tanker":
            self.hp += random.randint(5, 15)
            self.atk += random.randint(3, 7)
            self.defense += random.randint(2, 5)
        elif self.character_data["type"] == "Warrior":
            self.hp += random.randint(5, 10)
            self.atk += random.randint(4, 8)
            self.defense += random.randint(1, 4)
        elif self.character_data["type"] == "Ranger":
            self.hp += random.randint(3, 8)
            self.atk += random.randint(3, 6)
            self.defense += random.randint(1, 3)

    def get_random_ram_dmg(self):
        return random.randint(self.ram_dmg_range[0], self.ram_dmg_range[1])

    def get_c_dmg(self):
        c_dmg_value = str(self.character_data["C_DMG"])
        if '~' not in c_dmg_value:
            return float(c_dmg_value)
        start, end = map(float, c_dmg_value.split('~'))
        return round(random.uniform(start, end), 2)

    def attack(self, target):
        # 检查攻击者的 HP 是否大于 0
        if self.hp <= 0:
            print(f"{self.name} cannot attack because they are defeated.")
            return 0, False, 0  # 返回 0 表示没有造成伤害

        crit_hit = random.random() < self.crt
        ram_dmg = self.get_random_ram_dmg()
        base_dmg = self.atk * self.c_dmg if crit_hit else self.atk
        damage = max(0, base_dmg - target.defense + ram_dmg)

        target.take_damage(damage)
        attack_type = "Critical" if crit_hit else "Normal"
        print(
            f"{self.name} {attack_type} attack deals {damage} damage to {target.name}. Target DEF blocked {target.defense}.")

        if target.hp <= 0:
            print(f"{target.name} has been defeated!")

        attacker_exp = damage + target.defense + ram_dmg
        if damage > 0:
            attacker_exp *= 1.2 if damage > 10 else 1.1
        else:
            attacker_exp *= 1.05

        self.gain_exp(int(attacker_exp), damage > 0)

        target_exp = target.defense
        if damage > 0:
            target_exp *= 1.1
        else:
            target_exp *= 1.5
        target.gain_exp(int(target_exp), False)
        print(f"Attacker EXP: {self.exp}, Target EXP: {target.exp}")

        return damage, crit_hit, ram_dmg

    def take_damage(self, damage):
        self.hp -= damage
        print(f"\n{self.name} takes {damage} damage. Remaining HP: {self.hp}")

    def show_attributes(self):
        print(f"Name: {self.name}, Type: {self.character_data['type']} | "
              f"HP: {self.hp}, ATK: {self.atk}, DEF: {self.defense}, "
              f"CRT: {self.crt}, C_DMG: {self.c_dmg}, SPD: {self.spd}, "
              f"EVD: {self.evd}, EXP: {self.exp}, RANK: {self.rank}")


# Character manager class
class CharacterManager:
    def __init__(self, config_file):
        try:
            self.df = pd.read_excel(config_file)
        except Exception as e:
            print(f"Error reading configuration file: {e}")
            self.df = pd.DataFrame()  # 赋值一个空的 DataFrame

    def create_character(self, character_type, name="Unnamed"):
        character_type = character_type.capitalize()
        if character_type not in self.df.iloc[:, 0].values:
            raise ValueError(f"Character type '{character_type}' not found in the configuration.")
        return Character(character_type, name)


# create player's team
def create_player_team(manager, existing_names):
    player_team = []
    for i in range(4):  # Assuming player team size is 3
        while True:
            try:
                character_type = input(f"Select role {i + 1} type (Tanker, Warrior, Ranger): ").capitalize()
                name = input("Enter character name: ").strip()  # Remove leading/trailing spaces
                if not name:  # Check if name is empty after stripping
                    print("Character name cannot be empty. Please choose another name.")
                    continue
                if name in existing_names:  # Check for duplicates
                    print("Character name already exists. Please choose another name.")
                    continue
                character = manager.create_character(character_type, name)
                player_team.append(character)
                existing_names.add(name)  # Add name to the set of existing names
                break
            except ValueError as e:
                print(e)
                # Allow re-entry if an error occurs
                if 'not found' in str(e):
                    print("Invalid character type. Please select Tanker, Warrior, or Ranger.")
    return player_team

# Create AI team
def create_ai_team(manager):
    ai_team = []
    existing_ai_names = set()  # Keep track of existing AI names
    for i in range(3):  # Assuming AI team size is 3
        while True:
            character_type = random.choice(["Tanker", "Warrior", "Ranger"])
            ai_name = f"AI{random.randint(10, 99)}"
            if ai_name not in existing_ai_names:  # Check for duplicates
                existing_ai_names.add(ai_name)
                character = manager.create_character(character_type, ai_name)
                ai_team.append(character)
                break
    return ai_team

# Display team details
def display_team_details(team, team_name):
    print(f"\n{team_name} Team:")
    for character in team:
        character.show_attributes()

# Battle system
def battle(player_team, ai_team, storage):
    all_characters = player_team + ai_team

    while any(char.hp > 0 for char in player_team) and any(char.hp > 0 for char in ai_team):
        # Sort characters based on SPD before each round
        all_characters.sort(key=lambda x: x.spd, reverse=True)

        for character in all_characters:
            if character.hp <= 0:
                continue

            if character in player_team:
                # Player character's turn
                print(f"\n{character.name}'s turn. Choose a target:")
                while True:
                    target_name = input(", ".join([t.name for t in ai_team if t.hp > 0]) + ": ")
                    target = next((t for t in ai_team if t.name == target_name and t.hp > 0), None)
                    if target:
                        damage, crit, ram_dmg = character.attack(target)
                        storage.log_event(f"{character.name} attacks {target.name} dealing {damage} damage. (Crit: {crit}, RAM Damage: {ram_dmg})")
                        break
                    else:
                        print("Target not found or already defeated. Please choose another target.")

            else:
                # AI character's turn
                target = random.choice([char for char in player_team if char.hp > 0])
                damage, crit, ram_dmg = character.attack(target)
                storage.log_event(f"{character.name} attacks {target.name} dealing {damage} damage. (Crit: {crit}, RAM Damage: {ram_dmg})")

# Main function
def main():
    storage = GameDataStorage()
    manager = CharacterManager("characters.xlsx")

    existing_names = set()  # Initialize an empty set for existing names

    print("Create your team:")
    player_team = create_player_team(manager, existing_names)

    # Display player team details
    display_team_details(player_team, "Player")

    print("\nAI team has been created:")
    ai_team = create_ai_team(manager)

    # Display AI team details
    display_team_details(ai_team, "AI")

    print("\nStarting battle:")
    battle(player_team, ai_team, storage)
    storage.flush_logs()


if __name__ == "__main__":
    main()
