import pandas as pd
import random

# extract data from Excel
df = pd.read_excel("game_config.xlsx")
print(df,"\n")

# all characters' data from Excel, just for backup
Tanker = df[df.iloc[:, 0] == "Tanker"]
Warrior = df[df.iloc[:, 0] == "Warrior"]
Ranger = df[df.iloc[:, 0] == "Ranger"]


# Tanker attributions
class Tanker():
    Tanker = df[df.iloc[:, 0] == "Tanker"]
    print(Tanker,"\n")

# each element of Tanker
    HP_Tanker = str(df.iloc[1,1])
    ATK_Tanker = str(df.iloc[1,2])
    DEF_Tanker = str(df.iloc[1,3])
    RAN_DMG_Tanker = str(df.iloc[1,4])
    CRT_Tanker = str(df.iloc[1,5])
    SPD_Tanker = str(df.iloc[1,6])
    EVD_Tanker = str(df.iloc[1,7])

# HP random
    start_HP, end_HP = map(int, HP_Tanker.split('~'))
    random_HP = round(random.uniform(start_HP, end_HP),1)
    print(random_HP)

# ATK random
    start_ATK, end_ATK = map(int, ATK_Tanker.split('~'))
    random_ATK = random.randint(start_ATK, end_ATK)
    print(random_ATK)

# DEF random
    start_DEF, end_DEF = map(int, DEF_Tanker.split('~'))
    random_DEF = random.randint(start_DEF, end_DEF)
    print(random_DEF)

# RAN_DMG random
    start_RAN_DMG, end_RAN_DMG = map(int, RAN_DMG_Tanker.split('~'))
    random_RAN_DMG = random.randint(start_RAN_DMG, end_RAN_DMG)
    print(random_RAN_DMG)

# CRT random
    start_CRT, end_CRT = map(float, CRT_Tanker.split('~'))
    random_CRT = round(random.uniform(start_CRT, end_CRT), 1)
    print(random_CRT)

# SPD random
    start_SPD, end_SPD = map(int, SPD_Tanker.split('~'))
    random_SPD = random.randint(start_SPD, end_SPD)
    print(random_SPD)

# EVD
    print(EVD_Tanker)



# Warrior attributions
class Warrior():
    Warrior = df[df.iloc[:, 0] == "Warrior"]
    print(Warrior, "\n")

# each element of Warrior
    HP_Warrior = str(df.iloc[2, 1])
    ATK_Warrior = str(df.iloc[2, 2])
    DEF_Warrior = str(df.iloc[2, 3])
    RAN_DMG_Warrior = str(df.iloc[2, 4])
    CRT_Warrior = str(df.iloc[2, 5])
    SPD_Warrior = str(df.iloc[2, 6])
    EVD_Warrior = str(df.iloc[2, 7])

 # HP random
    start_HP, end_HP = map(int, HP_Warrior.split('~'))
    random_HP = round(random.uniform(start_HP, end_HP), 1)
    print(random_HP)

# ATK random
    start_ATK, end_ATK = map(int, ATK_Warrior.split('~'))
    random_ATK = random.randint(start_ATK, end_ATK)
    print(random_ATK)

 # DEF random
    start_DEF, end_DEF = map(int, DEF_Warrior.split('~'))
    random_DEF = random.randint(start_DEF, end_DEF)
    print(random_DEF)

# RAN_DMG random
    start_RAN_DMG, end_RAN_DMG = map(int, RAN_DMG_Warrior.split('~'))
    random_RAN_DMG = random.randint(start_RAN_DMG, end_RAN_DMG)
    print(random_RAN_DMG)

# CRT random
    start_CRT, end_CRT = map(float, CRT_Warrior.split('~'))
    random_CRT = round(random.uniform(start_CRT, end_CRT), 1)
    print(random_CRT)

# SPD random
    start_SPD, end_SPD = map(int, SPD_Warrior.split('~'))
    random_SPD = random.randint(start_SPD, end_SPD)
    print(random_SPD)

# EVD
    print(EVD_Warrior)



# Ranger attributions
class Ranger():
    Ranger = df[df.iloc[:, 0] == "Ranger"]
    print(Ranger, "\n")

 # each element of Warrior
    HP_Ranger = str(df.iloc[3, 1])
    ATK_Ranger = str(df.iloc[3, 2])
    DEF_Ranger = str(df.iloc[3, 3])
    RAN_DMG_Ranger = str(df.iloc[3, 4])
    CRT_Ranger = str(df.iloc[3, 5])
    SPD_Ranger = str(df.iloc[3, 6])
    EVD_Ranger = str(df.iloc[3, 7])
    print(EVD_Ranger)

# HP random
    start_HP, end_HP = map(int, HP_Ranger.split('~'))
    random_HP = round(random.uniform(start_HP, end_HP), 1)
    print(random_HP)

# ATK random
    start_ATK, end_ATK = map(int, ATK_Ranger.split('~'))
    random_ATK = random.randint(start_ATK, end_ATK)
    print(random_ATK)

# DEF random
    start_DEF, end_DEF = map(int, DEF_Ranger.split('~'))
    random_DEF = random.randint(start_DEF, end_DEF)
    print(random_DEF)

# RAN_DMG random
    start_RAN_DMG, end_RAN_DMG = map(int, RAN_DMG_Ranger.split('~'))
    random_RAN_DMG = random.randint(start_RAN_DMG, end_RAN_DMG)
    print(random_RAN_DMG)

# CRT random
    start_CRT, end_CRT = map(float, CRT_Ranger.split('~'))
    random_CRT = round(random.uniform(start_CRT, end_CRT), 1)
    print(random_CRT)

# SPD random
    start_SPD, end_SPD = map(int, SPD_Ranger.split('~'))
    random_SPD = random.randint(start_SPD, end_SPD)
    print(random_SPD)

# EVD
    print(EVD_Ranger)
