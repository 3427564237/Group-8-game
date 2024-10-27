import pytest
from stage1 import Character  # 导入你要测试的模块

@pytest.fixture
def character():
    return Character(character_type='Tanker', name='TestTank')

@pytest.fixture
def target():
    return Character(character_type='Warrior', name='TestWar')

def test_attack(character, target):
    initial_target_hp = target.hp
    damage, crit, ram_dmg = character.attack(target)

    # 检查伤害是否合理
    assert damage >= 0
    assert target.hp < initial_target_hp

def test_gain_exp(character):
    initial_exp = character.exp
    character.gain_exp(50, True)

    # 检查经验是否增加
    assert character.exp == initial_exp + 50

def test_take_damage(character):
    initial_hp = character.hp
    character.take_damage(20)

    # 检查生命值是否减少
    assert character.hp == initial_hp - 20
