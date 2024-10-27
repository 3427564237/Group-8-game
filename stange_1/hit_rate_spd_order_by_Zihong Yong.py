import random
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/Users/john/Downloads/Stage_1_Character_Attributions')))


import Stage_1_Character_Attributions as S1CA


print(S1CA.tanker().random_HP)

def calculate_hit_rate(dodge_rate):
    # Ensure the dodge_rate is between 0 and 1
    hit_rate = 1 - dodge_rate
    return hit_rate


# Example
dodge_rate = float(S1CA.tanker().EVD_Tanker)
hit_rate = calculate_hit_rate(dodge_rate)
hit_roll = random.random()
print(hit_roll,hit_rate)
if hit_roll < hit_rate :
    print ("hit success")
else:
    print("hit fail")
print(f"Hit Rate: {hit_rate:.2f}") 

# Define Character turn order
def determine_turn_order(characters):
    """Based on SPD """
    return sorted(characters, key=lambda x: x.spd, reverse=True)

# Turn order list
#characters = [player1, enemy1, player2, enemy2]
#turn_order = determine_turn_order(characters)

