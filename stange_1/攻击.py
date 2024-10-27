import random
import tkinter as tk


class Character:
    def __init__(self, name, hp, atk, defense, speed, skills):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.speed = speed
        self.skills = skills  # 技能列表
        self.is_alive = True

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def basic_attack(self, other):
        # 计算基础伤害
        damage = self.atk - other.defense
        damage = max(damage, 0)  # 确保伤害不为负数

        # 判定是否发生暴击
        is_critical = random.random() < 0.2  # 20% chance to crit
        if is_critical:
            # 如果发生暴击，计算暴击伤害
            damage *= 2  # Double damage on crit

        # 应用伤害到防御者
        other.take_damage(damage)
        return damage, is_critical

    def use_skill(self, skill, other):
        # 技能使用逻辑
        if skill in self.skills:
            damage = skill['damage']
            other.take_damage(damage)
            return damage, False
        else:
            return 0, False


# 创建角色实例
team1 = [
    Character("Warrior", 100, 20, 10, 15, [{'name': 'Slash', 'damage': 30}]),
    Character("Mage", 80, 15, 5, 12, [{'name': 'Fireball', 'damage': 35}]),
    Character("Archer", 90, 18, 8, 20, [{'name': 'Arrow', 'damage': 25}])
]

team2 = [
    Character("Goblin", 60, 15, 5, 10, [{'name': 'Stab', 'damage': 20}]),
    Character("Orc", 120, 15, 15, 8, [{'name': 'Smash', 'damage': 25}]),
    Character("Troll", 100, 20, 10, 12, [{'name': 'Club', 'damage': 30}])
]


# 定义战斗逻辑
class Battle:
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2
        self.turn_order = []

    def determine_turn_order(self):
        self.turn_order = self.team1 + self.team2
        self.turn_order.sort(key=lambda x: x.speed, reverse=True)

    def perform_turn(self):
        for character in self.turn_order:
            if character.is_alive:
                # 随机选择攻击目标
                if character in self.team1:
                    target = random.choice(self.team2)
                else:
                    target = random.choice(self.team1)
                if target.is_alive:
                    damage, is_critical = character.basic_attack(target)
                    print(
                        f"{character.name} attacks {target.name} for {damage} damage. {'(Critical!)' if is_critical else ''}")
                    if not target.is_alive:
                        print(f"{target.name} has been defeated!")


# 创建战斗实例
battle = Battle(team1, team2)


# 定义UI类
class GameUI:
    def __init__(self, battle):
        self.battle = battle
        self.root = tk.Tk()
        self.root.title("3v3 Turn-Based Game")
        self.root.geometry("400x300")

        self.label = tk.Label(self.root, text="Battle Start!")
        self.label.pack()

        self.start_button = tk.Button(self.root, text="Start Battle", command=self.start_battle)
        self.start_button.pack()

        self.root.mainloop()

    def start_battle(self):
        self.battle.determine_turn_order()
        self.battle.perform_turn()
        self.label.config(text="Battle Over!")


# 创建UI实例
game_ui = GameUI(battle)