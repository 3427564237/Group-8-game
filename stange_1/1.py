def gain_exp(self,damage_dealt,target_defence):
    if damage_dealt > 0:
       base_exp = damage_dealt + self.defence + self.ram_damage
       if damage_dealt >10:
           additional_exp = 0.2*damage_dealt
       else:
           additional_exp = 0.1*damage_dealt
       attacker_exp = base_exp + additional_exp
    else:
        attacker_exp = self.defence+0.05*self.defence
    target_exp = target_defence + (0.1*target_defence if damage_dealt >0 else 0.6*target_defence)
    self.exp += attacker_exp
    def level_up(self):
        exp_limit = 100+(self.rank*50)
        if self.exp >= exp_limit:
            self.rank += 1
            self.exp -=exp_limit#超过的经验转换为下级经验

def random_growth(self,character_type,attribute):
    growth_ranges = {
    'Tanker':{'hp':(5,15),
              'atk':(3,7),
              'def':(2,5),
              'ram_dmg':(1,3)
              },
    'Warrior':{'hp':(5,10),
               'atk':(4,8),
               'def':(1,4),
               'ram_dmg':(1,3)
               },
    'Ranger':{'hp':(3,8),
              'atk':(3,6),
              'def':(1,3),
              'ram_dmg':(1,4)}
    }
    return random.randint(*growth_ranges[character_type][attribute])