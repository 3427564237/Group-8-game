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
        """
        Initialize the GameDataStorage class.

        Parameters:
        json_file: Name of the JSON file to store game data.
        log_file: Name of the text file to record battle logs.
        """
        self.json_file = json_file # JSON file for storing game data
        self.log_file = log_file # # Text file for logging battle events
        self.data = {"game_state": {}, "battle_logs": []} # Initial game state and logs
        self.log_buffer = [] # Temporary buffer for logs
        self.load_data() # Load existing game data

    def load_data(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Data loaded from {self.json_file}")
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Data file error, creating a new one")
            self.save_data() # Create a new data file if load fails

    def save_data(self):
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            print(f"Data saved to {self.json_file}")
        except IOError as e:
            print(f"An error occurred while saving data: {e}")

    def log_event(self, event):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {event}"
        self.data['battle_logs'].append(log_entry) # Add log entry to data
        self.log_buffer.append(log_entry) # Add log entry to buffer
        if len(self.log_buffer) >= 10:
            self.flush_logs() # Write logs to file if buffer is full

    def flush_logs(self):
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.writelines([entry + "\n" for entry in self.log_buffer])
            self.log_buffer.clear() # Clear the buffer after writing
            print("Logs written to file")
        except IOError as e:
            print(f"An error occurred while writing logs: {e}")

    def update_game_state(self, key, value):
        self.data['game_state'][key] = value
        self.save_data() # Save the updated game state

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
        # Initialize character attributes based on type and random values
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
        try:
            attr_value = str(self.character_data[attribute])
            if '~' not in attr_value:
                return round(float(attr_value.strip('%')) / 100, 2) if decimal else int(attr_value)
            start, end = map(float, attr_value.replace('%', '').split('~'))
            return round(random.uniform(start, end), 2) if decimal else random.randint(int(start), int(end))
        except Exception as e:
            print(f"An error occurred while random value: {e}")
            return 0 # Return 0 if there is an error

    def parse_range(self, range_str):
        start, end = map(int, range_str.split("~"))
        return (start, end)

    def calculate_max_exp(self):
        """Calculate the maximum experience required for the next rank."""
        return 100 + (self.rank * 50)

    def gain_exp(self, exp_gained, caused_damage):
        """Increase character's experience and handle level-ups."""
        self.exp += exp_gained # Increase experience
        max_exp = self.calculate_max_exp() # Get max experience for current rank
        while self.exp >= max_exp:
            self.exp -= max_exp # Deduct max exp for level-up
            self.rank += 1 # Level up!!!
            self.update_attributes() # Update attributes after level-up
            max_exp = self.calculate_max_exp()  # Recalculate max exp for the new rank

        # Coins gain logic remains the same
        self.coins += 10 if caused_damage > 0 else 5
        print(f"{self.name} gains {exp_gained} EXP and now has {self.exp}/{max_exp}. Coins: {self.coins}")

    # Rest of the Character class remains unchanged
    TANKER_INCREMENT = {"HP": (5, 15), "ATK": (3, 7), "DEF": (2, 5)}
    WARRIOR_INCREMENT = {"HP": (5, 10), "ATK": (4, 8), "DEF": (1, 4)}
    RANGER_INCREMENT = {"HP": (3, 8), "ATK": (3, 6), "DEF": (1, 3)}

    def update_attributes(self):
        if self.character_data["type"] == "Tanker":
            self.hp += random.randint(*self.TANKER_INCREMENT["HP"])
            self.atk += random.randint(*self.TANKER_INCREMENT["ATK"])
            self.defense += random.randint(*self.TANKER_INCREMENT["DEF"])
        elif self.character_data["type"] == "Warrior":
            self.hp += random.randint(*self.WARRIOR_INCREMENT["HP"])
            self.atk += random.randint(*self.WARRIOR_INCREMENT["ATK"])
            self.defense += random.randint(*self.WARRIOR_INCREMENT["DEF"])
        elif self.character_data["type"] == "Ranger":
            self.hp += random.randint(*self.RANGER_INCREMENT["HP"])
            self.atk += random.randint(*self.RANGER_INCREMENT["ATK"])
            self.defense += random.randint(*self.RANGER_INCREMENT["DEF"])

    def get_random_ram_dmg(self):
        return random.randint(self.ram_dmg_range[0], self.ram_dmg_range[1])

    def get_c_dmg(self):
        c_dmg_value = str(self.character_data["C_DMG"])
        if '~' not in c_dmg_value:
            return float(c_dmg_value)
        start, end = map(float, c_dmg_value.split('~'))
        return round(random.uniform(start, end), 2)

    def attack(self, target):
        # check if dmg > 0
        if self.hp <= 0:
            print(f"{self.name} cannot attack because they are defeated.")
            return 0, False, 0  # cause 0 dmg

        # Check for dodge
        if random.random() < target.evd:
            print(f"{target.name} dodged the attack!")
            return 0, False, 0  # No damage dealt

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

        # check if the character is dead
        if self.hp <= 0:
            print(f"{self.name} has died.")

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
            self.df = pd.DataFrame()  # empty DataFrame

    def create_character(self, character_type, name="Unnamed"):
        character_type = character_type.capitalize()
        if character_type not in self.df.iloc[:, 0].values:
            raise ValueError(f"Character type '{character_type}' not found in the configuration.")
        return Character(character_type, name)


# Input/Output manager class
class IOManager:
    def __init__(self, game_data_storage):
        self.game_data_storage = game_data_storage

    def display_welcome(self):
        print("Welcome to the PVE Game!")

    def get_character_name(self):
        name = input("Enter your character's name: ")
        return name

    def get_character_type(self):
        print("Available character types: Tanker, Warrior, Ranger")
        while True:
            character_type = input("Choose your character type: ")
            if character_type in ["Tanker", "Warrior", "Ranger"]:
                return character_type
            print("Invalid type. Please try again.")

    def log_event(self, event):
        self.game_data_storage.log_event(event)


# Main game loop
class Game:
    def __init__(self):
        self.data_storage = GameDataStorage()
        self.io_manager = IOManager(self.data_storage)
        self.character_manager = CharacterManager("characters.xlsx")
        self.character = None

    def start(self):
        self.io_manager.display_welcome()
        name = self.io_manager.get_character_name()
        character_type = self.io_manager.get_character_type()
        self.character = self.character_manager.create_character(character_type, name)
        self.character.show_attributes()

    def run(self):
        self.start()


if __name__ == "__main__":
    game = Game()
    game.run()