############################################################################################################
# File: Jaegergembot3
# Author: Linus Hägg
# Date: 2019-12-15
############################################################################################################

############################################################################################################
############################################################################################################
############################################################################################################


#   IMPORTS


############################################################################################################
############################################################################################################
############################################################################################################
import discord
from discord.ext import commands
from discord.ext.commands import bot
from discord.utils import get

import numpy as np
import random
import time
import operator
from operator import add
from operator import mul
import copy
import asyncio
import math

import pickle
import sys
import os
############################################################################################################
############################################################################################################
############################################################################################################


#   CLASSES


############################################################################################################
############################################################################################################
############################################################################################################
class Gemma:
    def __init__(self):
        self.name = '-'
        self.type1 = -1
        self.type2 = -1
        self.ctype = ''
        self.power = 1      
        self.attack = -1
        self.defence = -1
        self.hp = 2         #Hearts/Health
        self.maxhp = 2      #Max hearts/Health
        self.speed = -1
        self.ability = [-1, 1, -1, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        self.alive = False
        self.typescore = -1
        self.personality = -1
        self.mood = 0
        self.AP = 0
        self.id = 'NULL'
        self.passive = [-1, 0] #num, counter
        self.exp = 0
        self.level = 1
        self.levelup = 0 #Says if you have options to pick for your levelup:
                         #0: No option
                         #1: Lv3 pick
                         #2: Lv7 pick
                         #3: Lv3 and Lv7 pick
                         #4: Lv10 pick
                         #5: Lv7 and Lv10 pick
                         #6: Lv3, Lv7, and Lv10 pick
        self.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        self.maxguard = 2 #Guard maximum
        self.check = 0 #Check for if you have recieved XP for various things
                       #0: base
                       #1: survived an attack
                       #2: used an ability (make sure it goes off)
                       #3: survived an attack and used an ability
        #self.temp = 0

class Duelist:
    def __init__(self):
        self.userid = -1
        self.user = -1
        self.discname = '-1'
        self.duelistname = '-1'
        self.g1 = Gemma()
        self.g2 = Gemma()
        self.g3 = Gemma()
        self.opponent = '-1'
        self.tradepartner = '-1'
        self.tradeuser = '-1'
        self.tradeslot = -1
        self.dueltag = -1
        self.gotrigger = False
        self.PC = [] #Fill with Gemma objects
        self.wincount = 0
        self.losecount = 0
        self.star = 1
        self.tokens = 1
        self.badge = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.basic = [[], [], [], [], [], [], [], [], [], [], [], [], [], []] #Stores wins for basic badges with a list of enemy userid
        self.elite = [[], [], [], [], [], [], [], [], [], [], [], [], [], []] #Stores wins for elite badges with a list of enemy userid
        self.temp = 0
        self.rotblock = False
        self.bot = False

class Duelmem:
    def __init__(self):
        self.phase = -1
        self.dueltag = -1
        self.caliber = -1 #0 for regular attacks, 1 for heavy attacks
        self.atkpower = 0
        self.atkroll = 0
        self.defroll = 0
        self.spdroll = 0
        self.espdroll = 0
        self.atkbonus = 0
        self.defbonus = 0
        self.spdbonus = 0
        self.espdbonus = 0
        self.typemod = 0
        self.abilityList = []
        self.duelists = [Duelist(), Duelist()]
        self.turn = -1
        self.passiveList = []
        self.channel = -1

class AItask:
    def __init__(self):
        self.task = -1
        self.channel = -1
        self.dueltag = -1

############################################################################################################
############################################################################################################
############################################################################################################


#   DEFINITIONS


############################################################################################################
############################################################################################################
############################################################################################################

#BOT DEFINITIONS
#______________________________________________
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
global runcheck_task


@bot.event
async def on_ready(): #This happens when it connects to discord
    print('Jaegergem bot is ready')
    print('My name is: ' + str(bot.user.name))
    print('My ID is: ' + str(bot.user.id))
    
    print('Starting to count at: ' + str(time.clock()))
    
    loadlist()
    with open('runcheck.pickle', 'wb') as f:
        pickle.dump(str(time.clock()), f, protocol=pickle.HIGHEST_PROTOCOL)
    global TagList
    TagList = []
    global runcheck_task
    runcheck_task = bot.loop.create_task(runcheck())

#This task runs every 5 seconds and checks if the bot is down. If it is it will remove the file runcheck.pickle
#The side script runchecker.py will then attempt to restart the bot
async def runcheck():
    await bot.wait_until_ready()
    while not bot.is_closed:
        await asyncio.sleep(10)
        print('Still running, time: ' + str(int(time.clock())))
        print('I have ', len(DuelmemList), ' duels in the duel memory. I have ', len(AItaskList), ' NPC bots active.' )
        if bot.is_closed:
            print('Going down')
            try:
                os.remove('runcheck.pickle')
            except FileNotFoundError:
                print('No runcheck to remove')
            savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
            sys.exit()
    print('Going down')
    try:
        os.remove('runcheck.pickle')
    except FileNotFoundError:
        print('No runcheck to remove')
    savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
    sys.exit()

#LISTS
#______________________________________________
TimeList = []       #Time list for keeping track of affection timers    #TimeList = [['Duelist name', Gemma ID, time stamp]]
DuelmemList = []    #Where duel memory objects are stored during duels
AdminList = ['125697188432052224'] #Hardcoded me as Admin
TeamList = []       #List of Duelist objects
TagList = []        #A user is stored in the tag list when they are locked in a command
AItaskList = []     #Stores tasks for AI duelist, one for each ongoing duel
E4 = [[],[],[],[],[],[]] #Stores the id's of those who have beaten the Elite Four and the champion. The last slot counts how many times you've beaten the league

#GLOBAL VARIABLES
#______________________________________________
maxGID = 0          #Gemma unique identifier number
gamepause = False       #Pauses user commands when True

############################################################################################################
############################################################################################################
############################################################################################################


#   TABLES AND DICTIONARIES


############################################################################################################
############################################################################################################
############################################################################################################

#DICE
#______________________________________________

#The dice size. The stat is stored as the index number. So an attack dice of d2 is stored as value 0
DiceList = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
            31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]

#TYPES
#______________________________________________
TypeList = ['Beast','Myth','Construct','Organism','Phasma','Sapien','Order','Chaos','Light','Dark','Wind','Earth','Aqua', 'Flame']

ColorDict = {0: 'Walnut', 1: 'Gold', 2: 'Iron', 3: 'Lime', 4: 'Plum', 5: 'Cinnamon', 6: 'Cobalt', 7: 'Indigo',
            8: 'Pearl', 9: 'Ebony', 10: 'Mint', 11: 'Chestnut', 12: 'Azure', 13: 'Scarlet'}

TypeChart = np.array([
    (0,0,-1,1,0,-1,1,0,0,1,0,-1,0,0), #Beast
    (1,0,1,0,0,1,0,0,-2,0,0,0,0,0), #Myth
    (0,0,0,1,-1,0,0,-1,0,0,0,1,0,0), #Construct
    (-1,0,-1,0,0,0,0,0,1,0,0,2,2,0), #Organism
    (-1,0,-1,0,2,1,0,0,1,-1,0,0,0,0), #Phasma
    (1,1,0,0,-2,0,0,1,0,-1,0,-1,0,0), #Sapien
    (0,-1,0,0,0,0,-1,2,0,0,1,0,1,1), #Order
    (0,0,0,0,0,0,2,-1,0,0,-1,1,0,-1), #Chaos
    (0,1,0,-1,2,0,0,0,-1,2,0,0,0,0), #Light
    (0,0,0,1,-1,1,0,0,2,-1,0,0,0,0), #Dark
    (0,0,0,2,0,0,0,-1,0,0,0,-1,0,-1), #Wind
    (0,-1,2,-1,0,0,1,0,0,0,-2,0,0,1), #Earth
    (0,-1,1,-1,0,0,0,0,1,0,0,1,-1,2), #Aqua
    (1,0,0,2,1,0,0,0,0,1,0,-1,-1,-1) #Flame
    ])

CompChart = np.array([
    ('','Dragon','','Bug','','','Dog','Cat','','Monstrosity','Bird','','Fish',''),
    ('Dragon','','Golem','Slime','Spirit','Fairy','Angel','Demon','','','Sylph','Dryad','Sea Serpent','Phoenix'),
    ('','Golem','','','Puppet','','','','Digital','','','Titan','',''),
    ('Bug','Slime','','','','','','','','Plague','','Plant','',''),
    ('','Spirit','Puppet','','','Ghost','','Dream','','','Elemental','Elemental','Elemental','Elemental'),
    ('','Fairy','','','Ghost','','','','','Shadow','','','Merfolk',''),
    ('Dog','Angel','','','','','','Mystic','Trillium','','','Crystal','Ice',''),
    ('Cat','Demon','','','Dream','','Mystic','','Celestial','','Storm','','',''),
    ('','','Digital','','','','Trillium','Celestial','','','Song','','','Holy'),
    ('Monstrosity','','','Plague','','Shadow','','','','','','Undead','','Infernal'),
    ('Bird','Sylph','','','Elemental','','','Storm','Song','','','','','Explosion'),
    ('','Dryad','Titan','Plant','Elemental','','Crystal','','','Undead','','','',''),
    ('Fish','Sea Serpent','','','Elemental','Merfolk','Ice','','','','','','','Cloud'),
    ('','Phoenix','','','Elemental','','','','Holy','Infernal','Explosion','','Cloud','')])

CompDict = {'Dragon': 0,
                'Golem': 1,
                'Bug': 2,
                'Slime': 3,
                'Spirit': 4,
                'Puppet': 5,
                'Fairy': 6,
                'Ghost': 7,
                'Dog': 8,
                'Angel': 9,
                'Cat': 10,
                'Demon': 11,
                'Mystic': 12,
                'Song': 13,
                'Digital': 14,
                'Trillium': 15,
                'Celestial': 16,
                'Plague': 17,
                'Shadow': 18,
                'Bird': 19,
                'Elemental': 20,
                'Dream': 21,
                'Crystal': 22,
                'Fish': 23,
                'Sea Serpent': 24,
                'Merfolk': 25,
                'Ice': 26,
                'Storm': 27,
                'Plant': 28,
                'Phoenix': 29,
                'Holy': 30,
                'Infernal': 31,
                'Cloud': 32,
                'Explosion': 33,
                'Titan': 34,
                'Sylph': 35,
                'Dryad': 36,
                'Undead': 37,
                'Monstrosity': 38} 

#Stat distribution for leveling
#______________________________________________
StatDistribution = [                                                                       #                ATK DEF SPD
        [[1,0,1], [2,0,0], [0,1,1], [1,1,0], [1,0,1], [1,1,0], [0,1,1], [1,0,1], [1,1,0]], #Brave   OK      8   5   5        
        [[0,1,1], [1,0,1], [0,1,1], [0,0,2], [1,0,1], [0,1,1], [0,1,1], [1,0,1], [0,1,1]], #Timid   OK      3   5   10   
        [[1,0,1], [0,0,2], [1,1,0], [0,1,1], [1,0,1], [0,1,1], [1,1,0], [1,0,1], [0,1,1]], #Jolly   OK      5   5   8            
        [[0,1,1], [0,2,0], [1,0,1], [1,1,0], [0,1,1], [1,1,0], [0,1,1], [1,0,1], [1,1,0]], #Calm    OK      5   8   5              
        [[0,1,1], [1,1,0], [0,1,1], [0,2,0], [1,1,0], [0,1,1], [0,1,1], [1,1,0], [0,1,1]], #Sassy   OK      3   10  5              
        [[1,0,1], [1,1,0], [1,0,1], [2,0,0], [1,1,0], [1,0,1], [1,0,1], [1,1,0], [1,0,1]], #Quirky  OK      10  3   5                  
        [[1,1,0], [1,0,1], [1,1,0], [2,0,0], [1,0,1], [1,1,0], [1,1,0], [1,0,1], [1,1,0]], #Hardy   OK      10  5   3                  
        [[1,1,0], [0,1,1], [1,1,0], [0,2,0], [0,1,1], [1,1,0], [1,1,0], [0,1,1], [1,1,0]], #Docile  OK      5   10  3                  
        [[1,0,1], [0,1,1], [1,0,1], [0,0,2], [0,1,1], [1,0,1], [1,0,1], [0,1,1], [1,0,1]]] #Skitterish  OK  5   3   10              

#AFFECTION
#______________________________________________

PetList = [['Brave', [' growls at you.', ' refuses to be pet by you.', ' lets you pet them carefully.'],
            [' growls softly.', ' reluctantly allows you to pet them.', ' doesn\'t seem to mind you petting them.'],
            [' seems agitated.', ' has a stoic expression.', ' rubs against your hand lovingly.']],
        ['Timid', [' does not come out of its gem.', ' shies away from you.', ' seems content to just be near you.'],
            [' comes out of its gem for a short while.', ' timidly allows you to pet them.', ' seems to appreciate the petting.'],
            [' just stays near you.', ' hugs you back.', ' hugs you and doesn\'t let go for a long while.']],
        ['Jolly', [' doesn\'t seem interested.', ' looks at you with curiosity.', ' seems quite happy to be petted.'],
            [' seems a bit down.', ' seems very happy.', ' rolls around on the floor.'],
            [' seems very tired.', ' jumps up and down happily.', ' runs in circles around you.']],
        ['Calm', [' ignores you.', ' allows you to pet them for a while.', ' seems quite pleased.'],
            [' doesn\'t seem to care', ' seems content as you pet them.', ' rubs against your hand as you pet them.'],
            [' has a somber expression.', ' seems very pleased.', ' happily cuddles with you.']],
        ['Sassy', [' just glares at you.', ' evades your attempt to pet them.', ' stays near you, but just outside of petting distance.'],
            [' turns away from you.', ' toys with your hand playfully.', ' makes a cheerful cry.'],
            [' is sulking.', ' jumps into your arms.', ' gleefully plays with you.']],
        ['Quirky', [' whimhpers.', ' nibbles on your hand.', ' looks excited.'],
            [' wanders around aimlessly.', ' seems confused but happy.', ' gives you a playful nudge.'],
            [' seems uneasy.', ' nuzzles your hand.', ' rests in your lap, delighted.']],
        ['Hardy', [' bats away your hand.', ' lets you rest their hand on them.', ' leans against you.'],
            [' looks at you disapprovingly.', ' lets you pet them for a short while.', ' seems content.'],
            [' lets you pet them in silence.', ' purrs with contentment.', ' pets you back.']],
        ['Docile', [' has a vacant expression.', ' does not react.', ' smiles at you.'],
            [' seems a bit tired.', ' seems to enjoy the petting.', ' dozes off as you pet them.'],
            [' seems a bit downtrodden.', ' curls up next to you.', ' falls asleep in your arms.']],
        ['Skitterish', [' hides from you.', ' jumps back, startled.', ' eyes you warily.'],
            [' seems scared.', ' shakes with excitement.', ' does not sit still as you pet them.'],
            [' twitches as you pet them.', ' calms down as you pet them.', ' shakes with excitement.']]]

#[Attack, ability, death, pet, deposit]
APImpact = [[2, 1, 0, 1, 0], #Brave
        [2, 2, 0, 1, -1], #Timid
        [1, 2, -1, 2, 0], #Jolly
        [1, 1, 0, 1, 1], #Calm
        [1, 2, 0, 1, 0], #Sassy
        [2, 1, 0, 2, -1], #Quirky
        [2, 0, 1, 1, 0], #Hardy
        [1, 1, 0, 2, 0], #Docile
        [2, 2, -1, 1, 0]] #Skitterish

#[Attack, ability, death, pet, deposit]
#Mood can be between -5 and 5
MoodImpact = [[2, 1, -3, 1, -1], #Brave
        [0, 2, -3, 3, -1], #Timid
        [1, 2, -4, 3, -1], #Jolly
        [1, 1, -3, 2, 0], #Calm
        [2, 1, -4, 3, -1], #Sassy
        [1, 1, -5, 4, -1], #Quirky
        [1, 1, -2, 1, 0], #Hardy
        [0, 1, -3, 3, 0], #Docile
        [1, 2, -3, 2, -1]] #Skitterish

#GANGS AND BADGES
#______________________________________________

RoleList = [
    '647191232258375680', #Aqua Wind          Dancers
    '647191267930931220', #Earth Flame        Evokers
    '647191334192414739', #Light Order        Knights
    '647191352509202442', #Dark Chaos         Outlaws
    '647191383509172255', #Sapien Construct   Paragons
    '647191401142026251', #Beast Myth         Rangers
    '647191416472338462'] #Organism Phasma    Shamans
    
BadgeDict = {
    0: ':dancer:',
    1: ':fire:',
    2: ':crossed_swords:',
    3: ':spy:',
    4: ':robot:',
    5: ':boar:',
    6: ':herb:'}

EbadgeDict = {
    0: ':thunder_cloud_rain:',
    1: ':volcano:',
    2: ':scales:',
    3: ':coffin:',
    4: ':cityscape:',
    5: ':dragon:',
    6: ':ghost:'}


TotalExp = [60, 180, 450, 900, 1500, 2250, 3200, 4300, 5500, -1]

GuardBreakMod = [2, 2, 3, 3, 4, 4, 5, 5, 6, 6] #The flat defence decrease when guard your guard breaks

#How ability and passive bonuses scale with level
BonusLevelScaling = [0.5, 0.5, 0.5, 1, 1, 1, 1.5, 1.5, 2, 2] #This is multiplied with dice bonuses and type modifiers

TypemodLevelScaling = [1, 1, 1, 1.5, 1.5, 1.5, 2, 2, 2.5, 2.5] #This is multiplied with dice bonuses and type modifiers

#How dice upgrades and downgrades scale with level
UpgradeLevelScaling = [-1, -1, -1, 0, 0, 0, 1, 1, 2, 2] #This is added to dice upgrades

############################################################################################################
############################################################################################################
############################################################################################################


#   PASSIVES AND ABILITIES - dictionaries


############################################################################################################
############################################################################################################
############################################################################################################

def passiveDict(num, level):
    a = BonusLevelScaling[level-1]
    b = UpgradeLevelScaling[level-1]
    PassiveDict = {0: 'Dragon: **+' + str(2*a) + '** to attack rolls when you have full hp.',
                1: 'Golem: +1 maximum guard.',
                2: 'Bug: **+' + str(3*a) + '** to your first defence roll.',
                3: 'Slime: +1 maximum hp, -1 maximum guard.',
                4: 'Spirit: When defeated, downgrade your opponent\'s attack dice by **' + str(3+b) + '** tiers.',
                5: 'Puppet: When defeated, turn the opposing Gemma into a [Puppet] Gemma.',#
                6: 'Fairy: **+' + str(1*a) + '** to defence rolls against heavy attacks.',
                7: 'Ghost: The opposing Gemma cannot rotate out if you have taken damage.',
                8: 'Dog: **+' + str(1*a) + '** to attack and defence rolls if there is a living Sapien type in your team.',
                9: 'Angel: +1 to power when your guard is broken.',
                10: 'Cat: **+' + str(1*a) + '** to attack and speed rolls if there is a living Sapien type in your team.',#
                11: 'Demon: Restore 1 hp after defeating an opposing Gemma.',
                12: 'Mystic: You may use one of your abilities twice, instead of using both once.',#
                13: 'Song: When defeated, upgrade your next Gemma\'s attack dice by **' + str(3+b) + '** tiers.',
                14: 'Digital: Lock-on to the first opponent you see, **+' + str(2*a) + '** to attack rolls against that opponent.',
                15: 'Trillium: Ignore the type modifier during your opponent\'s attacks.',#
                16: 'Celestial: **+' + str(2*a) + '** to attack rolls against composite type Gemma.',
                17: 'Plague: When defeated, after 2 turns your opponent takes 2 damage.',
                18: 'Shadow: Copy the attack dice of your opponent (once per duel).',#
                19: 'Bird: **+' + str(3*a) + '** to your first speed roll.',#
                20: 'Elemental: Double the type modifier for attack and defence rolls.',#
                21: 'Dream: Trade one of your abilities with your opponent (chosen randomly, once per duel).',#
                22: 'Crystal: **+' + str(1*a) + '** to attack rolls for every living Light type in your team.',
                23: 'Fish: **+' + str(1*a) + '** to speed rolls for every other living Aqua type in your team.',
                24: 'Sea Serpent: **+' + str(2*a) + '** to defense rolls when you have full hp.',#
                25: 'Merfolk: **+' + str(2*a) + '** to attack rolls if there is a [Sea Serpent] or [Fish] Gemma in your team.',#
                26: 'Ice: **+' + str(2*a) + '** to attack rolls against Aqua and Organism types, **-' + str(3*a) + '** to defense rolls against Fire types.',#      
                27: 'Storm: **+' + str(1*a) + '** to attack rolls for every other living Wind type in your team.',
                28: 'Plant: Refresh your abilities after making 3 attacks (once per duel).',
                29: 'Phoenix: When defeated, revive with 1 hp after 6 turns (once per duel).',
                30: 'Holy: **+' + str(2*a) + '** to attack rolls if there is a [Celestial] or [Angel] Gemma in your team.',
                31: 'Infernal: **+' + str(1*a) + '** to attack rolls for every other living Dark type in your team.',                                                     
                32: 'Cloud: **' + str(1*a) + '** to defence rolls for every other living Wind type in your team.',
                33: 'Explosion: Double all speed, attack and defence rolls.',#
                34: 'Titan: Your heavy attacks remove 1 guard regardless of the outcome.',
                35: 'Sylph: **+' + str(1*a) + '** to attack rolls for regular attacks.',
                36: 'Dryad: Reset all stat changes to attack, defence and speed in your team (once per duel).',
                37: 'Undead: **+' + str(1*a) + '** to defence rolls for every fainted Gemma in your team.',
                38: 'Monstrosity: **+' + str(1*a) + '** to attack rolls for every fainted Gemma in your team.'}
    return PassiveDict[num]


def abilityDict(num, level):
    a = BonusLevelScaling[level-1]
    b = UpgradeLevelScaling[level-1]
    AbilityDict = {0: '[-] Null Aura: Nullify your opponent\'s next ability activation.',
                1: '[I] Sprint: Add **+' + str(3*a) + '** to your speed roll',#
                2: '[I] Feather Weight: Reroll your speed roll',#
                3: '[I] Slime Trail: Reroll your opponent\'s speed roll',#
                4: '[I] Shadow shroud: Rotate your Gemma',#
                5: '[I] Tentacles: Rotate your opponent\'s Gemma',#
                6: '[I] Hallucination field: Rotate both your and your opponent\'s Gemma',#
                7: '[I] Cheap shot: Reduce your opponent\'s guard by 1',
                8: '[I] Overclocked: Add **+' + str(3*a) + '** to your speed roll',#
                9: '[I] Graceful Step: Reroll your speed roll',#
                10: '[I] Balance Disruptor: Reroll your opponent\'s speed roll',#
                11: '[I] Translocator: Rotate your Gemma',#
                12: '[I] Roundhouse Kick: Rotate your opponent\'s Gemma',#
                13: '[I] Ion Storm: Rotate both your and your opponent\'s Gemma' ,#
                14: '[B] Thermal Vision: Add **+' + str(3*a) + '** to your attack roll',#
                15: '[B] Hard Shell: Add **+' + str(3*a) + '** to your defence roll',#
                16: '[B] Many Limbs: Reroll your attack roll',#
                17: '[B] Heavy Weight: Reroll your defence roll',#
                18: '[B] Slippery Scales: Reroll your opponent\'s attack roll',#
                19: '[B] Corrosive Touch: Reroll your opponent\'s defence roll',#
                20: '[B] Elemental Affinity: Double the type modifier for this attack',
                21: '[B] Withdraw: Add **+' + str(2*a) + '** to your defence roll for each guard you have.',
                22: '[B] Shell bash: Add **+' + str(2*a) + '** to your attack roll for each guard you have.',
                23: '[B] Vacuum Aura: Ignore the type modifier for this attack',
                24: '[B] Prickly Thorns: By the end of this attack, if you defend successfully your opponent takes 1 damage.',#
                25: '[B] Heroic Grit: If this is your last Gemma, add **+' + str(5*a) + '** to your defence roll',#
                26: '[B] Lone Wolf: If this is your last Gemma, add **+' + str(5*a) + '** to your attack roll',#
                27: '[B] Power Surge: Add **+' + str(3*a) + '** to your attack roll',#
                28: '[B] Mental Shroud: Add **+' + str(3*a) + '** to your defence roll',#
                29: '[B] Tail Whip: Reroll your attack roll',#
                30: '[B] Outer Shell: Reroll your defence roll',#
                31: '[B] Mirage: Reroll your opponent\'s attack roll',#
                32: '[B] Armor Piercer: Reroll your opponent\'s defence roll',#
                33: '[B] Giant Slayer: If your opponent has a total attack of 10 or more, they take 2 damage after the attack',#
                34: '[B] Bunker Buster: If your opponent has a total defence of 10 or more, they take 2 damage after the attack',#
                35: '[B] Predatory Reflexes: If your opponent has a total attack of 1 or less, they take 2 damage after the attack',#
                36: '[B] Swift Strike: Reroll your attack roll with your speed dice',#
                37: '[B] Body Slam: Reroll your attack roll with your defence dice',#
                38: '[B] Forceful Parry: Reroll your defence roll with your attack dice',#
                39: '[B] Combat Roll: Reroll your defence roll with your speed dice',#
                40: '[B] Nightmare Visage: Reduce your opponent\'s total attack by **' + str(3*a) + '**',#
                41: '[B] Reckless lunge: Add **+' + str(5*a) + '** to your next attack roll, reduce your guard by 1',
                42: '[-] Soul Link: The next damage you take is transferred to your next living Gemma',#
                43: '[-] Rejuvinate: Restore 1 hp to the next living Gemma in your team',
                44: '[-] Disable: Downgrade your opponent\'s attack dice by **' + str(2+b) + '** tiers',#
                45: '[-] Pressure Point: Downgrade your opponent\'s defence dice by **' + str(2+b) + '** tiers',#
                46: '[-] Impair: Downgrade your opponent\'s speed dice by **' + str(2+b) + '** tiers',#
                47: '[-] Optimize Bloodlust: Upgrade your attack dice by **' + str(4+b) + '** tiers, downgrade your defence and speed dice by **' + str(2+b) + '** tier(s)',#
                48: '[-] Optimize Instincts: Upgrade your defence dice by **' + str(4+b) + '** tiers, downgrade your speed and attack dice by **' + str(2+b) + '** tier(s)',#
                49: '[-] Optimize Reflexes: Upgrade your speed dice by **' + str(4+b) + '** tiers, downgrade your attack and defence dice by **' + str(2+b) + '** tier(s)',#
                50: '[-] Berserk: Upgrade your attack dice by **' + str(3+b) + '** tiers, downgrade your defence dice by **' + str(2+b) + '** tiers',#
                51: '[-] Compose: Upgrade your attack dice by **' + str(3+b) + '** tiers, downgrade your speed dice by **' + str(2+b) + '** tiers',#
                52: '[-] Fortify: Upgrade your defence dice by **' + str(3+b) + '** tiers, downgrade your attack dice by **' + str(2+b) + '** tiers',#
                53: '[-] Entrench: Upgrade your defence dice by **' + str(3+b) + '** tiers, downgrade your speed dice by **' + str(2+b) + '** tiers',#
                54: '[-] Accelerate: Upgrade your speed dice by **' + str(3+b) + '** tiers, downgrade your attack dice by **' + str(2+b) + '** tiers',#
                55: '[-] Shed Skin: Upgrade your speed dice by **' + str(3+b) + '** tiers, downgrade your defence dice by **' + str(2+b) + '** tiers',#
                56: '[-] Munch: Upgrade your attack, defence and speed dice by **' + str(3+b) + '** tiers, your next Gemma faints',#
                57: '[-] Martial Exchange: Switch attack and defence dice with your next Gemma',#
                58: '[-] Feral Exchange: Switch speed and attack dice with your next Gemma',#
                59: '[-] Conscious Exchange: Switch defence and speed dice with your next Gemma',#
                60: '[-] Regenerate: Restore 1 hp and 1 guard',#
                61: '[I] Crystal Membrane: Downgrade your defence dice by **' + str(4+b) + '** tiers, increase your current and maximum hp by 2',#
                62: '[B] Life rite: Sacrifice 1 hp (and surviving), restore 2 hp to the next living Gemma in your team',#
                63: '[A] Necrotic wave: Sacrifice 1 hp, deal 1 hp to your opponent',#
                64: '[I] Taunting demeanour: The opposing Gemma cannot rotate out until you are defeated or rotate out',#
                65: '[-] Refocus: Fully restore your guard',
                66: '[-] Pulsar wave: Reduce your opponent\'s power by 1 for their next attack',
                67: '[I] Close combat: Reduce your and your opponent\'s guard by 2',
                68: '[I] Unstable flare: Add +1 power to your next attack, reduce your guard by 1',
                69: '[-] Shuffle: Switch the team order of your 2nd and 3rd Gemma',
                70: '[-] Disorganize: Switch the team order of the opposing team\'s 2nd and 3rd Gemma',
                71: '[B] Life sap: Restore 2 hp, sacrifice 1 hp from the next Gemma in your team'}                
    return AbilityDict[num]


############################################################################################################
############################################################################################################
############################################################################################################


#   PASSIVES AND ABILITIES


############################################################################################################
############################################################################################################
############################################################################################################


#Use playerIndex and enemyIndex to tell who has the turn, player has the turn, and who has the player speed memory slot
#owner is the index number for the duelist whos Gemma uses the ability
#owner should be recorded in the abilityList, when someone activates an ability it is equal to owner. But for triggers it should
#... come from the abilityList

#abIndex tells us if they used ability1 or ability2

#abilityListIndex is only used for trigger checks

#The trigger check rolls trough AbilityList and activates this function just like an !ab1 or !ab2 would do.

def ability(num, abIndex, DM, playerIndex, enemyIndex, owner, abilityListIndex, abilityListElement):
    w = '-1' #We should never return this, if it does happen something is wrong
    
    #These are only used when damage is dealt and something triggers
    slink1 = '-1'
    slink2 = '-1'
    pas1 = '-1'
    pas2 = '-1'

    if owner == 0:
        notowner = 1
    else:
        notowner = 0

    #Accessing the Gemma objects
    gowner = DM.duelists[owner].g1
    gnotowner = DM.duelists[notowner].g1
    gplayer = DM.duelists[playerIndex].g1
    genemy = DM.duelists[enemyIndex].g1

    if num == 0:
        if abilityListIndex == -1: #This should not trigger normally ever 
            #'[-] Null Aura: Nullify your opponent\'s next ability activation.'
            w = '**>>** ' + gowner.name + ' activates *Null Aura*, their opponent\'s next ability activation will be nullified!'
            DM.abilityList.append([num, owner, 0])
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)

    elif num == 1:
        #'[I] Sprint: Add +3 to your speed roll'
        if DM.phase == 1: #Phase 3 and not your turn, i.e. you are the defender.
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            if playerIndex == owner:
                DM.spdbonus += 3*a
            else:
                DM.espdbonus += 3*a
            w = '**>>** ' + gowner.name + ' activates *Sprint*, adding **+' + str(3*a) + '** to its speed roll!'    
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 2:
        #'[I] Feather Weight: Reroll your speed roll'
        if DM.phase == 1:
            if playerIndex == owner:
                speed = gplayer.speed 
                speedroll = random.randint(1, DiceList[speed])
                DM.spdroll = speedroll
                w = '**>>** ' + gowner.name + ' activates *Feather Weight* and rerolls **' + str(speedroll) + '** for speed!'
            
                if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                    DM.spdroll = DM.spdroll * 2 
            else:
                espeed = genemy.speed 
                espeedroll = random.randint(1, DiceList[espeed])
                DM.espdroll = espeedroll
                w = '**>>** ' + gowner.name + ' activates *Feather Weight* and rerolls **' + str(espeedroll) + '** for speed!'

                if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                    DM.espdroll = DM.espdroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else: 
            w = 'You cannot use this ability right now.'

    elif num == 3:
        #'[I] Slime Trail: Reroll your opponent\'s speed roll'
        if DM.phase == 1:
            if playerIndex != owner:
                speed = gplayer.speed 
                speedroll = random.randint(1, DiceList[speed])
                DM.spdroll = speedroll
                w = '**>>** ' + gowner.name + ' activates *Slime Trail* and rerolls **' + str(speedroll) + '** for ' + \
                gplayer.name + '\'s speed!'

                if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                    DM.spdroll = DM.spdroll * 2
            else:
                espeed = genemy.speed
                espeedroll = random.randint(1, DiceList[espeed])
                DM.espdroll = espeedroll
                w = '**>>** ' + gowner.name + ' activates *Slime Trail* and rerolls **' + str(espeedroll) + '** for ' + \
                genemy.name + '\'s speed!'

                if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                    DM.espdroll = DM.espdroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else: 
            w = 'You cannot use this ability right now.'

    elif num == 4:
        #'[I] Shadow shroud: Rotate your Gemma'
        if DM.phase == 1:
            w = '**>>** ' + gowner.name + ' activates *Shadow shroud*, attempting to rotate out their Gemma.'
            if (DM.duelists[owner].g2.alive or DM.duelists[owner].g3.alive):
                if not DM.duelists[owner].rotblock: #You are not blocked.
                    w += '\n' + rotateTeam_ab(DM, owner)
                    w += '\n\nAdvance with ``!go``'
                    DM.duelists[owner].rotblock = False
                    DM.duelists[notowner].rotblock = False
                    DM.phase = 0
                    DM.spdbonus = 0
                    DM.espdbonus = 0                    
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 5:
        #'[I] Tentacles: Rotate your opponent\'s Gemma'
        if DM.phase == 1:
            w = '**>>** ' + gowner.name + ' activates *Tentacles*, attempting to rotate out their opponent\'s Gemma.'
            if (DM.duelists[notowner].g2.alive or DM.duelists[notowner].g3.alive):
                if not DM.duelists[notowner].rotblock: #They are not blocked.
                    w += '\n' + rotateTeam_ab(DM, notowner)
                    w += '\n\nAdvance with ``!go``'
                    DM.duelists[owner].rotblock = False
                    DM.duelists[notowner].rotblock = False
                    DM.phase = 0
                    DM.spdbonus = 0
                    DM.espdbonus = 0
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 6:
        #'[I] Hallucination field: Rotate both your and your opponent\'s Gemma'
        if DM.phase == 1:
            w = '**>>** ' + gowner.name + ' activates *Hallucination Field*, attempting to rotate out both Gemma.'
            if (DM.duelists[owner].g2.alive or DM.duelists[owner].g3.alive):
                if not DM.duelists[owner].rotblock: #You are not blocked.
                    w += '\n' + rotateTeam_ab(DM, owner)
                    DM.duelists[owner].rotblock = False
                    DM.duelists[notowner].rotblock = False
                    DM.phase = 0
                    DM.spdbonus = 0
                    DM.espdbonus = 0
            if (DM.duelists[notowner].g2.alive or DM.duelists[notowner].g3.alive):
                if not DM.duelists[notowner].rotblock: #They are not blocked.
                    w += '\n\n' + rotateTeam_ab(DM, notowner)
                    DM.duelists[owner].rotblock = False
                    DM.duelists[notowner].rotblock = False
                    DM.phase = 0
                    DM.spdbonus = 0
                    DM.espdbonus = 0
            w += '\n\nAdvance with ``!go``'
            
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 7:
        #'[I] Cheap shot: Reduce your opponent\'s guard by 1'
        print('>>> Starting Cheap shot')
        if DM.phase == 1 and gnotowner.guard > 0:  
            print('>>> gnotowner.guard is ', gnotowner.guard)  
            gnotowner.guard -= 1
            print('>>> Reduced that to ', gnotowner.guard)
            if gnotowner.guard <= 0:
                gnotowner.guard = 0
                print('>>> Guard break, set it to zero')
                w = '**>>** ' + gowner.name + ' activates *Cheap shot*, reducing ' + gnotowner.name + '\'s guard by 1.'
                w += '\n:diamond_shape_with_a_dot_inside: **Guard Break** :diamond_shape_with_a_dot_inside:'
            else:
                w = '**>>** ' + gowner.name + ' activates *Cheap shot*, reducing ' + gnotowner.name + '\'s guard by 1.'

            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 8:
        #'[I] Overclocked: Add +3 to your speed roll'
        if DM.phase == 1: #Phase 3 and not your turn, i.e. you are the defender.
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            if playerIndex == owner:
                DM.spdbonus += 3*a
            else:
                DM.espdbonus += 3*a
            w = '**>>** ' + gowner.name + ' activates *Overclocked*, adding **+' + str(3*a) + '** to its speed roll!'    
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 9:
        #'[I] Graceful Step: Reroll your speed roll'
        if DM.phase == 1:
            if playerIndex == owner:
                speed = gplayer.speed
                speedroll = random.randint(1, DiceList[speed])
                DM.spdroll = speedroll
                w = '**>>** ' + gowner.name + ' activates *Graceful Step* and rerolls **' + str(speedroll) + '** for speed!'

                if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                    DM.spdroll = DM.spdroll * 2
            else:
                espeed = genemy.speed 
                espeedroll = random.randint(1, DiceList[espeed])
                DM.espdroll = espeedroll
                w = '**>>** ' + gowner.name + ' activates *Graceful Step* and rerolls **' + str(espeedroll) + '** for speed!'

                if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                    DM.espdroll = DM.espdroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else: 
            w = 'You cannot use this ability right now.'

    elif num == 10:
        #'[I] Balance Disruptor: Reroll your opponent\'s speed roll'
        if DM.phase == 1:
            if playerIndex != owner:
                speed = gplayer.speed 
                speedroll = random.randint(1, DiceList[speed])
                DM.spdroll = speedroll
                w = '**>>** ' + gowner.name + ' activates *Balance Disruptor* and rerolls **' + str(speedroll) + '** for ' + \
                gplayer.name + '\'s speed!'

                if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                    DM.spdroll = DM.spdroll * 2
            else:
                espeed = genemy.speed 
                espeedroll = random.randint(1, DiceList[espeed])
                DM.espdroll = espeedroll
                w = '**>>** ' + gowner.name + ' activates *Balance Disruptor* and rerolls **' + str(espeedroll) + '** for ' + \
                genemy.name + '\'s speed!'

                if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                    DM.espdroll = DM.espdroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else: 
            w = 'You cannot use this ability right now.'

    elif num == 11:
        #'[I] Translocator: Rotate your Gemma'
        if DM.phase == 1:
            w = '**>>** ' + gowner.name + ' activates *Translocator*, attempting to rotate out their Gemma!'
            if (DM.duelists[owner].g2.alive or DM.duelists[owner].g3.alive):
                if not DM.duelists[owner].rotblock: #You are not blocked.
                    w += '\n' + rotateTeam_ab(DM, owner)
                    w += '\n\nAdvance with ``!go``'
                    DM.duelists[owner].rotblock = False
                    DM.duelists[notowner].rotblock = False
                    DM.phase = 0
                    DM.spdbonus = 0
                    DM.espdbonus = 0
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 12:
        #'[I] Roundhouse Kick: Rotate your opponent\'s Gemma'
        if DM.phase == 1:
            w = '**>>** ' + gowner.name + ' activates *Roundhouse Kick*, attempting to rotate out their opponent\'s Gemma!'
            if (DM.duelists[notowner].g2.alive or DM.duelists[notowner].g3.alive):
                if not DM.duelists[notowner].rotblock: #They are not blocked.
                    w += '\n' + rotateTeam_ab(DM, notowner)
                    w += '\n\nAdvance with ``!go``'
                    DM.duelists[owner].rotblock = False
                    DM.duelists[notowner].rotblock = False
                    DM.phase = 0
                    DM.spdbonus = 0
                    DM.espdbonus = 0
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 13:
        #'[I] Ion Storm: Rotate both your and your opponent\'s Gemma'
        if DM.phase == 1:
            w = '**>>** ' + gowner.name + ' activates *Ion Storm*, attempting to rotate out both Gemma!'
            if (DM.duelists[owner].g2.alive or DM.duelists[owner].g3.alive):
                if not DM.duelists[owner].rotblock: #You are not blocked.
                    w += '\n' + rotateTeam_ab(DM, owner)
                    DM.duelists[owner].rotblock = False
                    DM.duelists[notowner].rotblock = False
                    DM.phase = 0
                    DM.spdbonus = 0
                    DM.espdbonus = 0
            if (DM.duelists[notowner].g2.alive or DM.duelists[notowner].g3.alive):
                if not DM.duelists[notowner].rotblock: #They are not blocked.
                    w += '\n' + rotateTeam_ab(DM, notowner)
                    DM.duelists[owner].rotblock = False
                    DM.duelists[notowner].rotblock = False
                    DM.phase = 0
                    DM.spdbonus = 0
                    DM.espdbonus = 0
            w += '\n\nAdvance with ``!go``'

            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 14:
        #'[B] Thermal Vision: Add +3 to your attack roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            w = '**>>** ' + gowner.name + ' activates *Thermal Vision*, adding **+' + str(3*a) + '** to its attack roll!'
            DM.atkbonus += 3*a
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 15:
        #'[B] Hard Shell: Add +3 to your defence roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            w = '**>>** ' + gowner.name + ' activates *Hard Shell*, adding **+' + str(3*a) + '** to its defence roll!'
            DM.defbonus += 3*a
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 16:
        #'[B] Many Limbs: Reroll your attack roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            attack = gplayer.attack 
            atkroll = random.randint(1, DiceList[attack])
            
            #Still disadvantage on heavy attacks
            if DM.caliber == 1:
                temp = random.randint(1, DiceList[attack])
                if temp < atkroll: atkroll = temp

            DM.atkroll = atkroll
            w = '**>>** ' + gowner.name + ' activates *Many Limbs* and rerolls **' + str(atkroll) + '** for attack!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.atkroll = DM.atkroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 17:
        #'[B] Heavy Weight: Reroll your defence roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            defence = genemy.defence 
            defroll = random.randint(1, DiceList[defence])
            DM.defroll = defroll
            w = '**>>** ' + gowner.name + ' activates *Heavy Weight* and rerolls **' + str(defroll) + '** for defence!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.defroll = DM.defroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 18:
        #'[B] Slippery Scales: Reroll your opponent\'s attack roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            attack = gplayer.attack
            atkroll = random.randint(1, DiceList[attack])
            DM.atkroll = atkroll
            w = '**>>** ' + gowner.name + ' activates *Slippery Scales* and rerolls **' + str(atkroll) + '** for ' + \
            gnotowner.name + '\'s attack!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.atkroll = DM.atkroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 19:
        #'[B] Corrosive Touch: Reroll your opponent\'s defence roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            defence = genemy.defence
            defroll = random.randint(1, DiceList[defence])
            DM.defroll = defroll
            w = '**>>** ' + gowner.name + ' activates *Corrosive Touch* and rerolls **' + str(defroll) + '** for ' + \
            gnotowner.name + '\'s defence!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.defroll = DM.defroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 20:
        #'[B] Elemental Affinity: Double the type modifier for this attack'
        if DM.phase == 3:
            DM.typemod = DM.typemod * 2
            w = '**>** ' + gowner.name + ' activates *Elemental Affinity*, doubling the type modifier to a total of '
            if DM.typemod < 0:
                w += '**' + str(-DM.typemod) + '** for defence!'
            else:
                w += '**' + str(DM.typemod) + '** for attack!'
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 21:
        #[B] Withdraw: Add +2 to your defence roll for each guard you have
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            w = '**>>** ' + gowner.name + ' activates *Withdraw*, adding **+' + str(2*a*gowner.guard) + '** to its defence roll!'
            DM.defbonus += 2*a*gowner.guard
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'
        
    elif num == 22:
        #[B] Shell bash: Add +2 to your attack roll for each guard you have
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            w = '**>>** ' + gowner.name + ' activates *Shell bash*, adding **+' + str(2*a*gowner.guard) + '** to its attack roll!'
            DM.atkbonus += 2*a*gowner.guard
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'
        
    elif num == 23:
        #'[B] Vacuum Aura: Ignore the type modifier for this attack'
        if DM.phase == 3:
            DM.typemod = 0
            w = '**>** ' + gowner.name + ' activates *Vacuum Aura*, setting the type modifier to 0!'
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'


    elif num == 24:
        #'[B] Prickly Thorns: By the end of this attack, if you defend successfully your opponent takes 1 damage.'
        if DM.phase == 3 and enemyIndex == owner and abilityListIndex == -1:
            w = '**>>** ' + gowner.name + ' activates *Prickly Thorns*, if they defend successfully the attacker takes 1 damage!'
            DM.abilityList.append([num, gowner.id, 0])
            gowner.ability[abIndex+1] -= 1

        elif DM.phase == 4 and abilityListIndex != -1:
            DM.abilityList.remove(abilityListElement)

            defboon = DM.defbonus 
            if DM.typemod < 0:
                defboon -= DM.typemod

            if (DM.defroll + defboon) >= (DM.atkroll + 
                DM.atkbonus):
                
                gplayer.hp -= 1 
                if gplayer.hp <= 0: 
                    gplayer.alive = False
                    DM.duelists[playerIndex].rotblock = False #You should always be able to rotate out when dead
                    w = '**>>** *Prickly Thorns* triggers and ' + gplayer.name + ' takes 1 damage! ' + gplayer.name + ' :skull: **faints!**'  #gplayer is the attacker
                else:
                    w = '**>>** *Prickly Thorns* triggers and ' + gplayer.name + ' takes 1 damage!' #gplayer is the attacker

                slink1 = soulink_check(DM, gplayer.id, 1)

                ###PASSIVE TRIGGER
                if DM.duelists[0].g1.ctype != '':
                    pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
                if DM.duelists[1].g1.ctype != '':
                    pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
                ###END OF PASSIVE TRIGGER

                awardAP(DM, enemyIndex, 2) #When we defend the enemy has the turn, so the user is the enemy
                #Award XP, check marker 2 for an ability
                awardXP(DM, owner, 2, genemy.level, gplayer.level)
            else:
                w = '-1' #Do not say anything
        else:
            if abilityListIndex == -1:
                w = 'You cannot use this ability right now.'
            else:
                w = '-1'

    elif num == 25:
        #'[B] Heroic Grit: If this is your last Gemma, add +5 to your defence roll.'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            if (not DM.duelists[owner].g2.alive and not DM.duelists[owner].g3.alive):
                a = BonusLevelScaling[gowner.level-1] #Level scaling
                w = '**>>** ' + gowner.name + ' activates *Heroic Grit*, adding **+' + str(5*a) + '** to its defence roll!'
                DM.defbonus += 5*a
                gowner.ability[abIndex+1] -= 1
                #Award affection points!
                awardAP(DM, owner, 1)
                #Award XP, check marker 2 for an ability
                awardXP(DM, owner, 2, gowner.level, gnotowner.level)
            else:
                w = 'You cannot use this ability right now.'
        else:
            w = 'You cannot use this ability right now.'

    elif num == 26:
        #'[B] Lone Wolf: If this is your last Gemma, add +5 to your attack roll.'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            if (not DM.duelists[owner].g2.alive and not DM.duelists[owner].g3.alive):
                a = BonusLevelScaling[gowner.level-1] #Level scaling
                w = '**>>** ' + gowner.name + ' activates *Lone Wolf*, adding **+' + str(5*a) + '** to its attack roll!'
                DM.atkbonus += 5*a
                gowner.ability[abIndex+1] -= 1
                #Award affection points!
                awardAP(DM, owner, 1)
                #Award XP, check marker 2 for an ability
                awardXP(DM, owner, 2, gowner.level, gnotowner.level)
            else:
                w = 'You cannot use this ability right now.'
        else:
            w = 'You cannot use this ability right now.'

    elif num == 27:
        #'[B] Power Surge: Add +3 to your attack roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            w = '**>>** ' + gowner.name + ' activates *Power Surge*, adding **+' + str(3*a) + '** to its attack roll!'
            DM.atkbonus += 3*a
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 28:
        #'[B] Mental Shroud: Add +3 to your defence roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            w = '**>>** ' + gowner.name + ' activates *Mental Shroud*, adding **+' + str(3*a) + '** to its defence roll!'
            DM.defbonus += 3*a
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 29:
        #'[B] Tail Whip: Reroll your attack roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            attack = gplayer.attack 
            atkroll = random.randint(1, DiceList[attack])
            
            #Still disadvantage on heavy attacks
            if DM.caliber == 1:
                temp = random.randint(1, DiceList[attack])
                if temp < atkroll: atkroll = temp
            
            DM.atkroll = atkroll
            w = '**>>** ' + gowner.name + ' activates *Tail Whip* and rerolls **' + str(atkroll) + '** for attack!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.atkroll = DM.atkroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 30:
        #'[B] Outer Shell: Reroll your defence roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            defence = genemy.defence 
            defroll = random.randint(1, DiceList[defence])
            DM.defroll = defroll
            w = '**>>** ' + gowner.name + ' activates *Outer Shell* and rerolls **' + str(defroll) + '** for defence!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.defroll = DM.defroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 31:
        #'[B] Mirage: Reroll your opponent\'s attack roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            attack = gplayer.attack
            atkroll = random.randint(1, DiceList[attack])
            DM.atkroll = atkroll
            w = '**>>** ' + gowner.name + ' activates *Mirage* and rerolls **' + str(atkroll) + '** for ' + gnotowner.name + '\'s attack!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.atkroll = DM.atkroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 32:
        #'[B] Armor Piercer: Reroll your opponent\'s defence roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            defence = genemy.defence
            defroll = random.randint(1, DiceList[defence])
            DM.defroll = defroll
            w = '**>>** ' + gowner.name + ' activates *Armor Piercer* and rerolls **' + str(defroll) + '** for ' + \
            gnotowner.name + '\'s defence!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.defroll = DM.defroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    
    elif num == 33:
        #'[B] Giant Slayer: If your opponent has a total attack of 10 or more, they take 2 damage after the attack'
        if DM.phase == 3 and enemyIndex == owner and abilityListIndex == -1:
            w = '**>>** ' + gowner.name + ' activates *Giant Slayer*, if ' + gnotowner.name + '\'s total attack ends ' + \
            'as 10 or higher, they take 2 damage!'
            DM.abilityList.append([num, gowner.id, 0])
            gowner.ability[abIndex+1] -= 1

        elif DM.phase == 4 and abilityListIndex != -1:
            DM.abilityList.remove(abilityListElement)
            atkboon = DM.atkbonus
            if DM.typemod > 0:
                atkboon += DM.typemod

            if (DM.atkroll + atkboon) >= 10:
                
                gplayer.hp -= 2 
                if gplayer.hp <= 0: 
                    gplayer.alive = False
                    DM.duelists[playerIndex].rotblock = False #You should always be able to rotate out when dead
                    w = '**>>** ' + '*Giant Slayer* triggers and ' + gplayer.name + ' takes 2 damage! ' + gplayer.name + ' :skull: **faints!**' #gplayer is the attacker
                else:
                    w = '**>>** ' + '*Giant Slayer* triggers and ' + gplayer.name + ' takes 2 damage!' #gplayer is the attacker
                
                slink1 = soulink_check(DM, gplayer.id, 1)

                ###PASSIVE TRIGGER
                if DM.duelists[0].g1.ctype != '':
                    pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
                if DM.duelists[1].g1.ctype != '':
                    pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
                ###END OF PASSIVE TRIGGER

                awardAP(DM, enemyIndex, 2) #The other Gemma is attacking, they have the turn, we are the enemy
                #Award XP, check marker 2 for an ability
                awardXP(DM, owner, 2, genemy.level, gplayer.level)

            else:
                w = '-1' #Do not say anything
        else:
            if abilityListIndex == -1:
                w = 'You cannot use this ability right now.'
            else:
                w = '-1'

    elif num == 34:
        #'[B] Bunker Buster: If your opponent has a total defence of 10 or more, they take 2 damage after the attack.
        if DM.phase == 3 and playerIndex == owner and abilityListIndex == -1:
            w = '**>>** ' + gowner.name + ' activates *Bunker Buster*, if ' + gnotowner.name + '\'s total defence ends ' + \
            'as 10 or higher, they take 2 damage!'
            DM.abilityList.append([num, gowner.id, 0]) 
            gowner.ability[abIndex+1] -= 1

        elif DM.phase == 4 and abilityListIndex != -1:
            DM.abilityList.remove(abilityListElement)            
            defboon = DM.defbonus
            if DM.typemod < 0:
                defboon -= DM.typemod

            if (DM.defroll + defboon) >= 10:
                
                genemy.hp -= 2
                if genemy.hp <= 0: 
                    genemy.alive = False
                    DM.duelists[enemyIndex].rotblock = False #You should always be able to rotate out when dead
                    w = '**>>** ' + '*Bunker Buster* triggers and ' + genemy.name + ' takes 2 damage! ' + genemy.name + ' :skull: **faints!**' #gplayer is the attacker
                else:
                    w = '**>>** ' + '*Bunker Buster* triggers and ' + genemy.name + ' takes 2 damage!' #gplayer is the attacker
                
                slink1 = soulink_check(DM, genemy.id, 1)

                ###PASSIVE TRIGGER
                if DM.duelists[0].g1.ctype != '':
                    pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
                if DM.duelists[1].g1.ctype != '':
                    pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
                ###END OF PASSIVE TRIGGER

                awardAP(DM, playerIndex, 2) #They are defending, we have the turn, we are the player
                #Award XP, check marker 2 for an ability
                awardXP(DM, owner, 2, gplayer.level, genemy.level)

            else:
                w = '-1' #Do not say anything
        else:
            if abilityListIndex == -1:
                w = 'You cannot use this ability right now.'
            else:
                w = '-1'

    elif num == 35:
        #'[B] Predatory Reflexes: If your opponent has a total attack of 1 or less, they take 2 damage after the attack'
        if DM.phase == 3 and enemyIndex == owner and abilityListIndex == -1:
            w = '**>>** ' + gowner.name + ' activates *Predatory Reflexes*, if ' + gnotowner.name + '\'s total attack ends ' + \
            'as 1 or lower, they take 2 damage!'
            DM.abilityList.append([num, gowner.id, 0]) 
            gowner.ability[abIndex+1] -= 1
        elif DM.phase == 4 and abilityListIndex != -1:
            DM.abilityList.remove(abilityListElement)
        
            atkboon = DM.atkbonus
            if DM.typemod > 0:
                atkboon += DM.typemod

            if (DM.atkroll + atkboon) <= 1:
                
                gplayer.hp -= 2 
                if gplayer.hp <= 0: 
                    gplayer.alive = False
                    DM.duelists[playerIndex].rotblock = False #You should always be able to rotate out when dead
                    w = '**>>** ' + '*Predatory Reflexes* triggers and ' + gplayer.name + ' takes 2 damage! ' + gplayer.name + ' :skull: **faints!**' #gplayer is the attacker
                else:
                    w = '**>>** ' + '*Predatory Reflexes* triggers and ' + gplayer.name + ' takes 2 damage!' #gplayer is the attacker

                slink1 = soulink_check(DM, gplayer.id, 1)

                ###PASSIVE TRIGGER
                if DM.duelists[0].g1.ctype != '':
                    pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
                if DM.duelists[1].g1.ctype != '':
                    pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
                ###END OF PASSIVE TRIGGER

                awardAP(DM, enemyIndex, 2) #They are attacking, we are defending, we are the enemy
                #Award XP, check marker 2 for an ability
                awardXP(DM, owner, 2, genemy.level, gplayer.level)
            else:
                w = '-1' #Do not say anything
        else:
            if abilityListIndex == -1:
                w = 'You cannot use this ability right now.'
            else:
                w = '-1'

    elif num == 36:
        #'[B] Swift Strike: Reroll your attack roll with your speed dice'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            attack = gplayer.speed
            atkroll = random.randint(1, DiceList[attack])
            
            #Still disadvantage on heavy attacks
            if DM.caliber == 1:
                temp = random.randint(1, DiceList[attack])
                if temp < atkroll: atkroll = temp
            
            DM.atkroll = atkroll
            w = '**>>** ' + gowner.name + ' activates *Swift Strike* and rerolls **' + str(atkroll) + '** for attack!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.atkroll = DM.atkroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 37:
        #'[B] Body Slam: Reroll your attack roll with your defence dice'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            attack = gplayer.defence
            atkroll = random.randint(1, DiceList[attack])
            
            #Still disadvantage on heavy attacks
            if DM.caliber == 1:
                temp = random.randint(1, DiceList[attack])
                if temp < atkroll: atkroll = temp

            DM.atkroll = atkroll
            w = '**>>** ' + gowner.name + ' activates *Body Slam* and rerolls **' + str(atkroll) + '** for attack!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.atkroll = DM.atkroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 38:
        #'[B] Forceful Parry: Reroll your defence roll with your attack dice'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            defence = gplayer.attack
            defroll = random.randint(1, DiceList[defence])
            DM.defroll = defroll
            w = '**>>** ' + gowner.name + ' activates *Forceful Parry* and rerolls **' + str(defroll) + '** for defence!'
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.defroll = DM.defroll * 2
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'
    
    elif num == 39:
        #'[B] Combat Roll: Reroll your defence roll with your speed dice'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            defence = gplayer.speed
            defroll = random.randint(1, DiceList[defence])
            DM.defroll = defroll
            w = '**>>** ' + gowner.name + ' activates *Combat Roll* and rerolls **' + str(defroll) + '** for defence!'
            gowner.ability[abIndex+1] -= 1
            if gowner.ctype == 'Explosion' or gnotowner.ctype == 'Explosion':
                DM.defroll = DM.defroll * 2
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 40:
        #'[B] Nightmare Visage: Reduce your opponent\'s total attack by 3'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            w = '**>>** ' + gowner.name + ' activates *Nightmare Visage*, reducing their opponent\'s attack by **' + str(3*a) + '**!'
            DM.atkbonus -= 3*a
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 41:
        #'[B] Reckless lunge: Add +5 to your attack roll, reduce your guard by 1'
        if DM.phase == 3 and playerIndex == owner and gowner.guard > 0:
            a = BonusLevelScaling[gowner.level-1] #Level scaling
            w = '**>>** ' + gowner.name + ' activates *Reckless lunge*, reducing its armor by 1 and adding **+' + str(5*a) + '** to its attack roll!'
            DM.atkbonus += 5*a
            gowner.guard -= 1
            if gowner.guard <= 0:
                gowner.guard = 0
                w += '\n:diamond_shape_with_a_dot_inside: **Guard Break** :diamond_shape_with_a_dot_inside:'
            
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 42:
        #'[-] Soul link: The next damage you take is transferred to your next living Gemma.'
        if DM.duelists[owner].g2.alive or DM.duelists[owner].g3.alive:
            if abilityListIndex == -1:
                w = '**>>** ' + gowner.name + ' activates *Soul Link*, the next damage taken will be transferred to another Gemma.'
                DM.abilityList.append([num, gowner.id, 0])
                gowner.ability[abIndex+1] -= 1
                #Award affection points!
                awardAP(DM, owner, 1)
                #Award XP, check marker 2 for an ability
                awardXP(DM, owner, 2, gowner.level, gnotowner.level)         
        else:
            w = 'You cannot use this ability right now.'

    elif num == 43:
        #'[-] Rejuvinate: Restore 1 hp to the next living Gemma in your team'        
        if DM.duelists[owner].g2.alive and \
                DM.duelists[owner].g2.hp < DM.duelists[owner].g2.maxhp:
            DM.duelists[owner].g2.hp += 1
            w = '**>>** ' + gowner.name + ' activates *Rejuvinate*, restoring 1 hp to ' + DM.duelists[owner].g2.name
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)        
        elif DM.duelists[owner].g3.alive and \
                DM.duelists[owner].g2.hp < DM.duelists[owner].g2.maxhp:
            DM.duelists[owner].g3.hp += 1
            w = '**>>** ' + gowner.name + ' activates *Rejuvinate*, restoring 1 hp to ' + DM.duelists[owner].g3.name
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'
        
    elif num == 44:
        #'[-] Disable: Downgrade your opponent\'s attack dice by 2 tiers'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Disable*, downgrading ' + gnotowner.name + '\'s attack dice by **' + str(2+b) + '** tiers!'
        gnotowner.attack -= 2+b
        if gnotowner.attack < 0:
            gnotowner.attack = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)
    
    elif num == 45:
        #'[-] Pressure Point: Downgrade your opponent\'s defence dice by 2 tiers.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Pressure Point*, downgrading ' + gnotowner.name + '\'s defence dice by **' + str(2+b) + '** tiers!'
        gnotowner.defence -= 2+b
        if gnotowner.defence < 0:
            gnotowner.defence = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        
    elif num == 46:
        #'[-] Impair: Downgrade your opponent\'s speed dice by 2 tiers.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Impair*, downgrading ' + gnotowner.name + '\'s speed dice by **' + str(2+b) + '** tiers!'
        gnotowner.speed -= 2+b
        if gnotowner.speed < 0:
            gnotowner.speed = 0

        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 47:
        #'[-] Optimize Bloodlust: Upgrade your attack dice by 4 tiers, downgrade your defence and speed dice by 2 tier.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Optimize Bloodlust*, upgrading its attack by **' + str(4+b) + '** tiers while also downgrading its ' + \
        'defence and speed dice by **' + str(2+b) + '** tier.'
        gowner.attack += 4+b
        gowner.defence -= 2+b
        gowner.speed -= 2+b

        if gowner.defence < 0:
            gowner.defence = 0
        if gowner.speed < 0:
            gowner.speed = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 48:
        #'[-] Optimize Instincts: Upgrade your defence dice by 4 tiers, downgrade your speed and attack dice by 2 tiers.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Optimize Instincts*, upgrading its defence by **' + str(4+b) + '** tiers while also downgrading its ' + \
        'speed and attack dice by **' + str(2+b) + '** tier.'
        gowner.defence += 4+b
        gowner.speed -= 2+b
        gowner.attack -= 2+b
        if gowner.attack < 0:
            gowner.attack = 0
        if gowner.speed < 0:
            gowner.speed = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 49:
        #'[-] Optimize Reflexes: Upgrade your speed dice by 4 tiers, downgrade your attack and defence dice by 2 tier.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Optimize Reflexes*, upgrading its speed by **' + str(4+b) + '** tiers while also downgrading its ' + \
        'attack and defence dice by **' + str(2+b) + '** tier.'
        gowner.speed += 4+b
        gowner.defence -= 2+b
        gowner.attack -= 2+b

        if gowner.defence < 0:
            gowner.defence = 0
        if gowner.attack < 0:
            gowner.attack = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)
    
    elif num == 50:
        #'[-] Berserk: Upgrade your attack dice by 3 tiers, downgrade your defence dice by 2 tiers.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Berserk*, upgrading its attack by **' + str(3+b) + '** tiers while also downgrading its ' + \
        'defence dice by **' + str(2+b) +'** tiers.'
        gowner.attack += 3+b
        gowner.defence -= 2+b
        if gowner.defence < 0:
            gowner.defence = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 51:
        #'[-] Compose: Upgrade your attack dice by 3 tiers, downgrade your speed dice by 2 tiers.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Compose*, upgrading its attack by **' + str(3+b) + '** tiers while also downgrading its ' + \
        'speed dice by **' + str(2+b) + '** tiers.'
        gowner.attack += 3+b
        gowner.speed -= 2+b
        if gowner.speed < 0:
            gowner.speed = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 52:
        #'[-] Fortify: Upgrade your defence dice by 3 tiers, downgrade your attack dice by 2 tiers.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Fortify*, upgrading its defence by **' + str(3+b) + '** tiers while also downgrading its ' + \
        'attack dice by **' + str(2+b) + '** tiers.'
        gowner.defence += 3+b
        gowner.attack -= 2+b
        if gowner.attack < 0:
            gowner.attack = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 53:
        #'[-] Entrench: Upgrade your defence dice by 3 tiers, downgrade your speed dice by 2 tiers.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Entrench*, upgrading its defence by **' + str(3+b) + '** tiers while also downgrading its ' + \
        'speed dice by **' + str(2+b) + '** tiers.'
        gowner.defence += 3+b
        gowner.speed -= 2+b

        if gowner.speed < 0:
            gowner.speed = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 54:
        #'[-] Accelerate: Upgrade your speed dice by 3 tiers, downgrade your attack dice by 2 tiers.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Accelerate*, upgrading its speed by **' + str(3+b) + '** tiers while also downgrading its ' + \
        'attack dice by **' + str(2+b) + '** tiers.'
        gowner.speed += 3+b
        gowner.attack -= 2+b

        if gowner.attack < 0:
            gowner.attack = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 55:
        #'[-] Shed Skin: Upgrade your speed dice by 3 tiers, downgrade your defence dice by 2 tiers.'
        b = UpgradeLevelScaling[gowner.level-1]
        w = '**>>** ' + gowner.name + ' activates *Shed Skin*, upgrading its speed by **' + str(3+b) + '** tiers while also downgrading its ' + \
        'defence dice by **' + str(2+b) + '** tiers.'
        gowner.speed += 3+b
        gowner.defence -= 2+b

        if gowner.defence < 0:
            gowner.defence = 0
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 56:
        #'[-] Munch: Upgrade your attack, defence and speed dice by 3 tiers, your next Gemma faints'
        ok = False
        if DM.duelists[owner].g2.alive:
            b = UpgradeLevelScaling[gowner.level-1]
            w = '**>>** ' + gowner.name + ' activates *Munch*, consuming ' + DM.duelists[owner].g2.name + \
            ' to upgrade its attack, defence and speed by **' + str(3+b) + '** tiers!'

            DM.duelists[owner].g2.hp -= DM.duelists[owner].g2.maxhp
            DM.duelists[owner].g2.alive = False
            ok = True
            slink1 = soulink_check(DM, DM.duelists[owner].g2.id, DM.duelists[owner].g2.maxhp)

            ###PASSIVE TRIGGER
            if DM.duelists[0].g1.ctype != '':
                pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
            if DM.duelists[1].g1.ctype != '':
                pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
            ###END OF PASSIVE TRIGGER

        elif DM.duelists[owner].g3.alive:
            b = UpgradeLevelScaling[gowner.level-1]
            w = '**>>** ' + gowner.name + ' activates *Munch*, consuming ' + DM.duelists[owner].g3.name + \
            ' to upgrade its attack, defence and speed by **' + str(3+b) + '** tiers!'
            DM.duelists[owner].g3.hp -= DM.duelists[owner].g3.maxhp
            DM.duelists[owner].g3.alive = False
            ok = True

            slink1 = soulink_check(DM, DM.duelists[owner].g3.id, DM.duelists[owner].g3.maxhp)
            
            ###PASSIVE TRIGGER
            if DM.duelists[0].g1.ctype != '':
                pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
            if DM.duelists[1].g1.ctype != '':
                pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
            ###END OF PASSIVE TRIGGER

        else:
            w = 'You cannot use this ability right now.'
        if ok:
            gowner.attack += 3+b
            gowner.defence += 3+b
            gowner.speed += 3+b
        
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)

    elif num == 57:
        #'[-] Martial Exchange: Switch attack and defence dice with your next Gemma'
        if DM.duelists[owner].g2.id != 'NULL':
            w = '**>>** ' + gowner.name + ' activates *Martial Exchange*, switching attack and defence dice with ' + DM.duelists[owner].g2.name
            attack = gowner.attack
            defence = gowner.defence
            gowner.attack = DM.duelists[owner].g2.attack
            gowner.defence = DM.duelists[owner].g2.defence
            DM.duelists[owner].g2.attack = attack
            DM.duelists[owner].g2.defence = defence
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        elif DM.duelists[owner].g3.id != 'NULL':
            w = '**>>** ' + gowner.name + ' activates *Martial Exchange*, switching attack and defence dice with ' + DM.duelists[owner].g3.name
            attack = gowner.attack
            defence = gowner.defence
            gowner.attack = DM.duelists[owner].g3.attack
            gowner.defence = DM.duelists[owner].g3.defence
            DM.duelists[owner].g3.attack = attack
            DM.duelists[owner].g3.defence = defence
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'
        
    elif num == 58:
        #'[-] Feral Exchange: Switch speed and attack dice with your next Gemma'
        if DM.duelists[owner].g2.id != 'NULL':
            w = '**>>** ' + gowner.name + ' activates *Feral Exchange*, switching speed and attack dice with ' + DM.duelists[owner].g2.name
            attack = gowner.attack
            speed = gowner.speed
            gowner.attack = DM.duelists[owner].g2.attack
            gowner.speed = DM.duelists[owner].g2.speed
            DM.duelists[owner].g2.attack = attack
            DM.duelists[owner].g2.speed = speed
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        elif DM.duelists[owner].g3.id != 'NULL':
            w = '**>>** ' + gowner.name + ' activates *Feral Exchange*, switching speed and attack dice with ' + DM.duelists[owner].g3.name
            attack = gowner.attack
            speed = gowner.speed
            gowner.attack = DM.duelists[owner].g3.attack
            gowner.speed = DM.duelists[owner].g3.speed
            DM.duelists[owner].g3.attack = attack
            DM.duelists[owner].g3.speed = speed
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 59:
        #'[-] Conscious Exchange: Switch defence and speed dice with your next Gemma'
        if DM.duelists[owner].g2.id != 'NULL':
            w = '**>>** ' + gowner.name + ' activates *Conscious Exchange*, switching defence and speed dice with ' + DM.duelists[owner].g2.name
            defence = gowner.defence
            speed = gowner.speed
            gowner.defence = DM.duelists[owner].g2.defence
            gowner.speed = DM.duelists[owner].g2.speed
            DM.duelists[owner].g2.defence = defence
            DM.duelists[owner].g2.speed = speed
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)

        elif DM.duelists[owner].g3.id != 'NULL':
            w = '**>>** ' + gowner.name + ' activates *Conscious Exchange*, switching defence and speed dice with ' + DM.duelists[owner].g3.name
            defence = gowner.defence
            speed = gowner.speed
            gowner.defence = DM.duelists[owner].g3.defence
            gowner.speed = DM.duelists[owner].g3.speed
            DM.duelists[owner].g3.defence = defence
            DM.duelists[owner].g3.speed = speed
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        
        else:
            w = 'You cannot use this ability right now.'
    
    elif num == 60:
        #[-] Regenerate: Restore 1 hp and 1 guard'
        if gowner.hp < gowner.maxhp or gowner.guard < gowner.maxguard:
            w = '**>>** ' + gowner.name + ' activates *Regenerate*, restoring 1 hp and 1 guard.'
            if gowner.hp < gowner.maxhp: gowner.hp += 1
            if gowner.guard < gowner.maxguard: gowner.guard += 1

            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 61:
        #'[I] Crystal Membrane: Downgrade your defence dice by 4 tiers, increase your current and maximum hp by 2'
        if DM.phase == 1:
            b = UpgradeLevelScaling[gowner.level-1]
            w = '**>>** ' + gowner.name + ' activates *Crystal Membrane*, downgrading its defence dice by **' + str(4+b) + '** tiers but increasing their current and max hp by 2!'
            gowner.defence -= 6+b
            if gowner.defence < 0:
                gowner.defence = 0
            gowner.ability[abIndex+1] -= 1
            gowner.maxhp += 2
            gowner.hp += 2
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 62:
        #[B] Life rite: Sacrifice 1 hp (and surviving), restore 2 hp to the next living Gemma in your team
        if DM.phase == 3 and DM.duelists[owner].g2.alive and DM.duelists[owner].g2.hp < DM.duelists[owner].g2.maxhp \
                and gowner.hp > 1:
            DM.duelists[owner].g2.hp += 2    
            gowner.hp -= 1
            if gowner.hp <= 0:
                gowner.hp = 0
                gowner.alive = False
                DM.duelists[owner].rotblock = False #You should always be able to rotate out when dead
                w = '**>>** ' + gowner.name + ' activates *Life rite*, damaging themselves and restoring 2 hp to ' \
                + DM.duelists[owner].g2.name + '. ' + gowner.name + ' :skull: **faints!**'
            else:
                w = '**>>** ' + gowner.name + ' activates *Life rite*, damaging themselves and restoring 2 hp to ' \
                + DM.duelists[owner].g2.name
            
            slink1 = soulink_check(DM, gowner.id, 1)

            ###PASSIVE TRIGGER
            if DM.duelists[0].g1.ctype != '':
                pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
            if DM.duelists[1].g1.ctype != '':
                pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
            ###END OF PASSIVE TRIGGER

            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level) 

        elif DM.phase == 3 and DM.duelists[owner].g3.alive and DM.duelists[owner].g3.hp < DM.duelists[owner].g3.maxhp \
                and gowner.hp > 1:
            DM.duelists[owner].g3.hp += 2
            gowner.hp -= 1
            if gowner.hp <= 0:
                gowner.hp = 0
                gowner.alive = False
                DM.duelists[owner].rotblock = False #You should always be able to rotate out when dead
                w = '**>>** ' + gowner.name + ' activates *Rejuvinate*, damaging themselves and restoring 2 hp to ' \
                + DM.duelists[owner].g3.name + '. ' + gowner.name + ' :skull: **faints!**'
            else:
                w = '**>>** ' + gowner.name + ' activates *Rejuvinate*, damaging themselves and restoring 2 hp to ' \
                + DM.duelists[owner].g3.name
            
            slink1 = soulink_check(DM, gowner.id, 1)

            ###PASSIVE TRIGGER
            if DM.duelists[0].g1.ctype != '':
                pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
            if DM.duelists[1].g1.ctype != '':
                pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
            ###END OF PASSIVE TRIGGER
            
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'
    
    elif num == 63:
        #[A] Necrotic wave: Sacrifice 1 hp, deal 1 hp to your opponent
        if DM.phase == 4 and gowner.alive:
            gnotowner.hp -= 1
            gowner.hp -= 1
            w = '**>>** ' + gowner.name + ' activates *Necrotic wave*, damaging themselves and their opponent!'
            if gowner.hp <= 0:
                gowner.hp = 0
                gowner.alive = False
                DM.duelists[owner].rotblock = False #You should always be able to rotate out when dead
                w += '\n' + gowner.name + ' :skull: **faints!**'
            if gnotowner.hp <= 0:
                gnotowner.hp = 0
                gnotowner.alive = False
                DM.duelists[notowner].rotblock = False #You should always be able to rotate out when dead
                w += '\n' + gnotowner.name + ' :skull: **faints!**'

            slink1 = soulink_check(DM, gowner.id, 1)
            slink2 = soulink_check(DM, gnotowner.id, 1)

            ###PASSIVE TRIGGER
            if DM.duelists[0].g1.ctype != '':
                pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
            if DM.duelists[1].g1.ctype != '':
                pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
            ###END OF PASSIVE TRIGGER
            
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 64:
        #'[I] Taunting Demeanour: The opposing Gemma cannot rotate out until you are defeated or rotate out.'
        if DM.phase == 1:
            w = '**>>** ' + gowner.name + ' activates *Taunting Demenour*, as long as ' + gowner.name + ' is in battle, ' + \
                gnotowner.name + ' cannot rotate out!'
            DM.duelists[notowner].rotblock = True
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 65:
        #'[-] Refocus: Fully restore your guard'
        if gowner.guard < gowner.maxguard:
            w = '**>>** ' + gowner.name + ' activates *Refocus*, fully restoring their guard.'
            gowner.guard = gowner.maxguard

            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'
    
    elif num == 66:
        #'[I] Pulsar wave: Reduce your opponent\'s power by 1 for their next attack'
        #downgrade power, it disappears at the next phase 1 or phase 4
        if DM.phase == 1 and abilityListIndex == -1:
            w = '**>>** ' + gowner.name + ' activates *Pulsar wave*, weakening their opponent\'s next attack!'
            gnotowner.power -= 1
            DM.abilityList.append([num, gnotowner.id, 0])
            gowner.ability[abIndex+1] -= 1

            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level) 

        elif DM.phase == 4 and abilityListIndex != -1:
            if memGemHasTurn(DM, abilityListElement[1]):
                #It is the opponent's turn, they've had an opportunity to attack
                DM.abilityList.remove(abilityListElement)
                gem = findGemIDduel(DM, abilityListElement[1])
                gem.power += 1
                w = '**>>** The *Pulsar wave* affecting ' + gem.name + ' fades.'            
        else:
            w = 'You cannot use this ability right now.'

    elif num == 67:
        #'[I] Close combat: Reduce your and your opponent\'s guard by 2'
        if DM.phase == 1:
            w = '**>>** ' + gowner.name + ' activates *Close combat*, reducing their and their opponent\'s guard by 2!'
            gowner.guard -= 2
            gnotowner.guard -= 2
            if gowner.guard <= 0:
                gowner.guard = 0
                w += '\n:diamond_shape_with_a_dot_inside: **Guard Break** :diamond_shape_with_a_dot_inside:'
            if gnotowner.guard <= 0:
                gnotowner.guard = 0
                w += '\n:diamond_shape_with_a_dot_inside: **Guard Break** :diamond_shape_with_a_dot_inside:'
            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level)
        else:
            w = 'You cannot use this ability right now.'

    elif num == 68:
        #'[I] Unstable flare: Add +1 power to your next attack, reduce your guard by 1
        if DM.phase == 1 and abilityListIndex == -1 and gowner.guard > 0:
            w = '**>>** ' + gowner.name + ' activates *Unstable flare*, reducing their guard by 1 and empowering their next attack!'
            gowner.power += 1
            gowner.guard -= 1
            if gowner.guard <= 0:
                gowner.guard = 0
                w += '\n:diamond_shape_with_a_dot_inside: **Guard Break** :diamond_shape_with_a_dot_inside:'
            DM.abilityList.append([num, gowner.id, 0])
            gowner.ability[abIndex+1] -= 1

            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level) 
            
        elif DM.phase == 4 and abilityListIndex != -1:
            if memGemHasTurn(DM, abilityListElement[1]):
                #If it's your turn you have had an opportunity to attack
                DM.abilityList.remove(abilityListElement)
                gem = findGemIDduel(DM, abilityListElement[1])
                gem.power -= 1
                w = '**>>** ' + gem.name + '\'s *Unstable flare* fades.'
            
        else:
            w = 'You cannot use this ability right now.'

    elif num == 69:
        #'[-] Shuffle: Switch the team order of your 2nd and 3rd Gemma'
        w = '**>>** ' + gowner.name + ' activates *Shuffle*, reorganizing their team.'
        temp = DM.duelists[owner].g2
        DM.duelists[owner].g2 = DM.duelists[owner].g3
        DM.duelists[owner].g3 = temp
        
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level) 
        
    elif num == 70:
        #'[-] Disorganize: Swith the team order of the opposing team\'s 2nd and 3rd Gemma'
        w = '**>>** ' + gowner.name + ' activates *Disorganize*, reorganizing their opponent\'s team.'
        temp = DM.duelists[notowner].g2
        DM.duelists[notowner].g2 = DM.duelists[notowner].g3
        DM.duelists[notowner].g3 = temp
        
        gowner.ability[abIndex+1] -= 1
        #Award affection points!
        awardAP(DM, owner, 1)
        #Award XP, check marker 2 for an ability
        awardXP(DM, owner, 2, gowner.level, gnotowner.level) 
    
    elif num == 71:
        #'[B] Life sap: Restore 2 hp, sacrifice 1 hp from the next Gemma in your team'
        if DM.phase == 3 and gowner.hp < gowner.maxhp and DM.duelists[owner].g2.alive:
            DM.duelists[owner].g2.hp -= 1    
            gowner.hp += 2
            if gowner.hp > gowner.maxhp: gowner.hp = gowner.maxhp
            if DM.duelists[owner].g2.hp <= 0:
                DM.duelists[owner].g2.hp = 0
                DM.duelists[owner].g2.alive = False
                w = '**>>** ' + gowner.name + ' activates *Life sap*, healing themselves for 2 by damaging ' \
                + DM.duelists[owner].g2.name + '. ' + DM.duelists[owner].g2.name + ' :skull: **faints!**'
            else:
                w = '**>>** ' + gowner.name + ' activates *Life sap*, healing themselves for 2 by damaging ' \
                + DM.duelists[owner].g2.name + '.'

            slink1 = soulink_check(DM, DM.duelists[owner].g2.id, 1)

            ###PASSIVE TRIGGER
            if DM.duelists[0].g1.ctype != '':
                pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
            if DM.duelists[1].g1.ctype != '':
                pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
            ###END OF PASSIVE TRIGGER

            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level) 

        elif DM.phase == 3 and gowner.hp < gowner.maxhp and DM.duelists[owner].g3.alive:
            DM.duelists[owner].g3.hp -= 1    
            gowner.hp += 2
            if gowner.hp > gowner.maxhp: gowner.hp = gowner.maxhp
            if DM.duelists[owner].g3.hp <= 0:
                DM.duelists[owner].g3.hp = 0
                DM.duelists[owner].g3.alive = False
                w = '**>>** ' + gowner.name + ' activates *Life sap*, healing themselves for 2 by damaging ' \
                + DM.duelists[owner].g3.name + '. ' + DM.duelists[owner].g3.name + ' :skull: **faints!**'
            else:
                w = '**>>** ' + gowner.name + ' activates *Life sap*, healing themselves for 2 by damaging ' \
                + DM.duelists[owner].g3.name + '.'

            slink1 = soulink_check(DM, DM.duelists[owner].g3.id, 1)

            ###PASSIVE TRIGGER
            if DM.duelists[0].g1.ctype != '':
                pas1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
            if DM.duelists[1].g1.ctype != '':
                pas2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
            ###END OF PASSIVE TRIGGER

            gowner.ability[abIndex+1] -= 1
            #Award affection points!
            awardAP(DM, owner, 1)
            #Award XP, check marker 2 for an ability
            awardXP(DM, owner, 2, gowner.level, gnotowner.level) 
        else:
            w = 'You cannot use this ability right now.'
    
    else:
        w = '-1'
        
    return w, slink1, slink2, pas1, pas2





def passive(num, DM, playerIndex, enemyIndex, owner, indicator, ab):
    w = '-1' #If nothing changes this, the bot will not say anything
    
    #These are only used when damage is dealt and something triggers
    #slink1 = '-1'
    #slink2 = '-1'
    #pas1 = '-1'
    #pas2 = '-1'

    if owner == 0:
        notowner = 1
    else:
        notowner = 0

    #Accessing the Gemma objects
    gowner = DM.duelists[owner].g1
    gnotowner = DM.duelists[notowner].g1
    #gplayer = DM.duelists[playerIndex].g1
    #genemy = DM.duelists[enemyIndex].g1

    if num == 0:
        #'Dragon: +2 to attack rolls when you have full hp.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                if gowner.hp == gowner.maxhp:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += 2*a
                    w = '*>> Dragon: +' + str(2*a) + ' attack for ' + gowner.name + '*'
                
    elif num == 1:
        #'Golem: +1 guard.'
        pass

    elif num == 2:
        #'Bug: +3 to your first defence roll.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == notowner and indicator == 'Attack':
                if gowner.passive[1] == 0:
                    gowner.passive[1] = 1
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.defbonus += 3*a
                    w = '*>> Bug: +' + str(3*a) + ' defence for ' + gowner.name + '\'s first defence roll.*'

    elif num == 3:
        #'Slime: +1 maximum hp, -1 maximum guard'
        pass

    elif num == 4:
        #'Spirit: When defeated, downgrade your opponent\'s attack dice by 3 tiers.'
        if (DM.phase == 4 and indicator == 'Go') or indicator == 'Dmg':
            if not gowner.alive:
                b = UpgradeLevelScaling[gowner.level-1]
                w = '*>> Spirit: When fainting, ' + gowner.name + ' curses ' + gnotowner.name + ' which downgrades their attack dice by ' + str(3+b) + ' tiers!*'
                gnotowner.attack -= 3+b
                if gnotowner.attack < 0: gnotowner.attack = 0
                
    elif num == 5:
        #'Puppet: When defeated, turn the opposing Gemma into a [Puppet] Gemma.'
        if (DM.phase == 4 and indicator == 'Go') or indicator == 'Dmg':
            if not gowner.alive:
                w = '*>> Puppet: When fainting, ' + gowner.name + ' curses ' + gnotowner.name + ' which turns them into a [Puppet]!*'
                gnotowner.type1 = gowner.type1
                gnotowner.type2 = gowner.type2
                gnotowner.ctype = gowner.ctype
                gnotowner.passive = [5, 0, 'Puppet: When defeated, turn the opposing Gemma into a [Puppet] Gemma.']

    elif num == 6:
        #'Fairy: +1 to defence rolls against heavy attacks.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == notowner and indicator == 'Attack':
                if DM.caliber == 1:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.defbonus += 1*a
                    w = '*>> Fairy: +' + str(1*a) + ' defence for ' + gowner.name + '*'
        
    elif num == 7:
        #'Ghost: The opposing Gemma cannot rotate out if you have taken damage.'
        #Enemy gemma has to be alive, if they are dead the rotblock will have been removed and shouldn't change 
        if gowner.alive and gowner.hp < gowner.maxhp and gnotowner.alive and not DM.duelists[notowner].rotblock:
            w = '*>> Ghost: ' + gowner.name + ' prevents ' + gnotowner.name + ' from escaping!*'
            DM.duelists[notowner].rotblock = True

    elif num == 8:
        #'Dog: +1 to attack and defence rolls if there is a living Sapien type in your team.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == notowner and indicator == 'Attack':
                dl = DM.duelists[owner]
                tm = [dl.g2, dl.g3]
                ok = False
                for gem in tm:
                    if (gem.type1 == 5 or gem.type2 == 5) and gem.alive:
                        ok = True
                        break
                if ok:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.defbonus += 1*a
                    w = '*>> Dog: +' + str(1*a) + ' defence for ' + gowner.name + '*'
                
            if DM.turn == owner and indicator == 'Attack':
                dl = DM.duelists[owner]
                tm = [dl.g2, dl.g3]
                ok = False
                for gem in tm:
                    if (gem.type1 == 5 or gem.type2 == 5) and gem.alive:
                        ok = True
                        break
                if ok:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += 1*a
                    w = '*>> Dog: +' + str(1*a) + ' attack for ' + gowner.name + '*'
                
    elif num == 9:
        #'Angel: +1 power when your guard is broken.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack' and gowner.guard == 0:
                DM.atkpower += 1
                w = '*>> Angel: Angelic fury grants ' + gowner.name + ' +1 power!*'

    elif num == 10:
        #'Cat: +1 to attack and speed rolls if there is a living Sapien type in your team.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                dl = DM.duelists[owner]
                tm = [dl.g2, dl.g3]
                ok = False
                for gem in tm:
                    if (gem.type1 == 5 or gem.type2 == 5) and gem.alive:
                        ok = True
                        break
                if ok:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += 1*a
                    w = '*>> Cat: +' + str(1*a) + ' attack for ' + gowner.name + '*'
                
        if DM.phase == 1 and indicator == '':
            dl = DM.duelists[owner]
            tm = [dl.g2, dl.g3]
            ok = False
            for gem in tm:
                if (gem.type1 == 5 or gem.type2 == 5) and gem.alive:
                    ok = True
                    break
            if ok:
                if playerIndex == owner:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.spdbonus += 1*a
                    w = '*>> Cat: +' + str(1*a) + ' speed for ' + gowner.name + '*'
                if enemyIndex == owner:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.espdbonus += 1*a
                    w = '*>> Cat: +' + str(1*a) + ' speed for ' + gowner.name + '*'

    elif num == 11:
        #'Demon: Restore 1 hp after defeating an opposing Gemma.'
        if DM.phase == 4 and not gnotowner.alive and gowner.hp < gowner.maxhp:
            w = '*>> Demon: ' + gowner.name + ' restores 1 hp after defeating ' + gnotowner.name + '*'
            gowner.hp += 1

    elif num == 12:
        #'Mystic: You may use one of your abilities twice, instead of using both once.'
        #Mystics automatically have 2 uses of each ability, but the moment one hits zero the other one also drops.
        if indicator == 'Ability' and gowner.passive[0] == 12:
            
            if ab == 1:
                if gowner.ability[1] == 1 and gowner.ability[3] == 1:
                    #drain both
                    gowner.ability[1] = 0
                    gowner.ability[3] = 0
                elif gowner.ability[1] == 0 and gowner.ability[3] == 2:
                    #msg and drain ab2
                    gowner.ability[3] = 0
                    w = '*>> Mystic: ' + gowner.name + ' expended their other ability to activate this ability twice.*' 
                
            if ab == 2:
                if gowner.ability[1] == 1 and gowner.ability[3] == 1:
                    #drain both
                    gowner.ability[1] = 0
                    gowner.ability[3] = 0
                elif gowner.ability[1] == 2 and gowner.ability[3] == 0:
                    #msg and drain ab1
                    gowner.ability[1] = 0
                    w = '*>> Mystic: ' + gowner.name + ' expended their other ability to activate this ability twice.*' 

    elif num == 13:
        #'Song:  When defeated, upgrade your next Gemma\'s attack dice by **' + str(3+b) + '** tiers.'
        if (DM.phase == 4 and indicator == 'Go') or indicator == 'Dmg':
            if not gowner.alive:
                g2 = DM.duelists[owner].g2
                b = UpgradeLevelScaling[gowner.level-1]
                w = '*>> Song: When fainting, ' + gowner.name + '\'s final crescendo upgrades ' + g2.name + '\'s attack dice by ' + str(3+b) + ' tiers!*'
                g2.attack += 3+b


    elif num == 14:
        #'Digital: Lock-on to the first opponent you see, +2 to attack rolls against that opponent.'
        if DM.phase == 1 and indicator == '':
            if gowner.passive[1] == 0:
                gowner.passive[1] = gnotowner.id
                w = '*>> Digital: ' + gowner.name + ' locks-on to ' + gnotowner.name + '!*'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                if gowner.passive[1] != 0 and gowner.passive[1] == gnotowner.id:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += 2*a
                    w = '*>> Digital: +' + str(2*a) + ' attack for ' + gowner.name + '*'
    
    elif num == 15:
        #'Trillium: Ignore the type modifier during your opponent\'s attacks.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == notowner and indicator == 'Typemod':
                DM.typemod = 0
                w = '*>> Trillium: Type modifier ignored.*' 
            
    elif num == 16:
        #'Celestial: +2 to attack rolls against composite type Gemma.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                if gnotowner.ctype != '':
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += 2*a
                    w = '*>> Celestial: +' + str(2*a) + ' attack for ' + gowner.name + '*'
    
    elif num == 17:
        #'Plague: When defeated, after 4 turns your opponent takes 2 damage.'
        if (DM.phase == 4 and indicator == 'Go') or indicator == 'Dmg':
            if not gowner.alive:
                DM.passiveList.append([num, gnotowner.id, 0])
                w = '*>> Plague: When fainting, ' + gowner.name + ' curses ' + gnotowner.name + ' to take 2 damage after 4 turns!*'
    
    elif num == 18:
        #'Shadow: Copy the attack dice of the opposing Gemma (once per duel).'
        if DM.phase == 1 and indicator == '':
            if gowner.passive[1] == 0:
                gowner.passive[1] = 1
                gowner.attack = gnotowner.attack	
                w = '*>> Shadow: ' + gowner.name + ' copied the attack of ' + gnotowner.name + '!*'

    elif num == 19:
        #'Bird: +3 to your first speed roll.'
        if DM.phase == 1 and indicator  == '':
            if gowner.passive[1] == 0:
                gowner.passive[1] = 1
                if playerIndex == owner:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.spdbonus += 3*a
                    w = '*>> Bird: +' + str(3*a) + ' speed for ' + gowner.name +  '\'s first speed roll.*'
                if enemyIndex == owner:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.espdbonus += 3*a
                    w = '*>> Bird: +' + str(3*a) + ' speed for ' + gowner.name +  '\'s first speed roll.*'

    elif num == 20:
        #'Elemental: Double the type modifier for attack and defence rolls.'
        if DM.phase == 2 or DM.phase == 4:
            if indicator == 'Typemod':
                DM.typemod = DM.typemod * 2
                w = '*>> Elemental: Double the type modifier.*'

    elif num == 21:
        #'Dream: Trade one of your abilities with your opponent (chosen randomly, once per duel).'
        if DM.phase == 1 and gowner.passive[1] == 0 and indicator == '':
            gowner.passive[1] = 1
            temp = [0, 0]
            p = {0: 0, 1: 2}
            r1 = p[random.randint(0, 1)]
            r2 = p[random.randint(0, 1)]
            if gowner.ability[0] == -1: r1 = 2
            elif gowner.ability[2] == -1: r1 = 0
            if gnotowner.ability[0] == -1: r2 = 2
            elif gnotowner.ability[2] == -1: r2 = 0
            
            temp[0] = gowner.ability[r1]
            temp[1] = gowner.ability[r1+1]
            gowner.ability[r1] = gnotowner.ability[r2]
            gowner.ability[r1+1] = gnotowner.ability[r2+1]
            gnotowner.ability[r2] = temp[0]
            gnotowner.ability[r2+1] = temp[1]

            w = '*>> Dream: ' + gowner.name + ' trades one of their abilities with ' + gnotowner.name + '*'

    elif num == 22:
        #'Crystal: +1 to attack rolls for every living Light type in your team.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                dl = DM.duelists[owner]
                tm = [dl.g2, dl.g3]
                gowner.passive[1] = 0
                for gem in tm:
                    if (gem.type1 == 8 or gem.type2 == 8) and gowner.passive[1] < 2 and gem.alive:
                        gowner.passive[1] += 1
                if gowner.passive[1] > 0:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += gowner.passive[1]*a
                    w = '*>> Crystal: +' + str(gowner.passive[1]*a) + ' attack for ' + gowner.name + '*'
                
    elif num == 23:
        #'Fish: +1 to speed rolls for every other living Aqua type in your team (max +2).'
        if DM.phase == 1 and indicator == '':
            dl = DM.duelists[owner]
            tm = [dl.g2, dl.g3]
            gowner.passive[1] = 0
            for gem in tm:
                if (gem.type1 == 12 or gem.type2 == 12) and gem.alive and gowner.passive[1] < 2:
                    gowner.passive[1] += 1

            if playerIndex == owner and gowner.passive[1] > 0:
                a = BonusLevelScaling[gowner.level-1] #Level scaling
                DM.spdbonus += gowner.passive[1]*a
                w = '*>> Fish: +' + str(gowner.passive[1]*a)+ ' speed for ' + gowner.name + '*'
            if enemyIndex == owner and gowner.passive[1] > 0:
                a = BonusLevelScaling[gowner.level-1] #Level scaling
                DM.espdbonus += gowner.passive[1]*a
                w = '*>> Fish: +' + str(gowner.passive[1]*a)+ ' speed for ' + gowner.name + '*'
            
    elif num == 24:
        #'Sea Serpent: +2 to defence rolls when you have full hp'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == notowner and indicator == 'Attack':
                if gowner.hp == gowner.maxhp:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.defbonus += 2*a
                    w = '*>> Sea Serpent: +' + str(2*a) + ' defence for ' + gowner.name + '*'
    
    elif num == 25:
        #'Merfolk: +2 to attack rolls if there is a [Sea Serpent] or [Fish] Gemma in your team'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                if gowner.passive[1] == 0: #saving time
                    gowner.passive[1] = -1
                    dl = DM.duelists[owner]
                    tm = [dl.g2.ctype, dl.g3.ctype]
                    ok = False
                    for ctype in tm:
                        if ctype == 'Sea Serpent' or ctype == 'Fish':
                            ok = True
                            gowner.passive[1] = 1
                            break
                    if ok:
                        a = BonusLevelScaling[gowner.level-1] #Level scaling
                        DM.atkbonus += 2*a
                        w = '*>> Merfolk: +' + str(2*a) + ' attack for ' + gowner.name + '*'
                elif gowner.passive[1] == 1:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += 2*a
                    w = '*>> Merfolk: +' + str(2*a) + ' attack for ' + gowner.name + '*'
    
    elif num == 26:
        #'Ice: +2 to attack rolls against Aqua and Organism types, -3 to defence rolls against Fire types.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                if (gnotowner.type1 == 12 or gnotowner.type2 == 12) \
                    or (gnotowner.type1 == 3 or gnotowner.type2 == 3):
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += 2*a
                    w = '*>> Ice: +' + str(2*a) + ' attack for ' + gowner.name + '*'

            elif DM.turn == notowner and indicator == 'Attack':
                if gnotowner.type1 == 13 or gnotowner.type2 == 13:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.defbonus -= 3*a
                    w = '*>> Ice: -' + str(3*a) + ' defence for ' + gowner.name + '*'

    elif num == 27:
        #'Storm: +1 to attack rolls for every other living Wind type in your team (max +2)'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                dl = DM.duelists[owner]
                tm = [dl.g2, dl.g3]
                gowner.passive[1] = 0
                for gem in tm:
                    if (gem.type1 == 10 or gem.type2 == 10) and gem.alive and gowner.passive[1] < 2:
                        gowner.passive[1] += 1
                if gowner.passive[1] > 0:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += gowner.passive[1]*a
                    w = '*>> Storm: +' + str(gowner.passive[1]*a) + ' attack for ' + gowner.name + '*'
                
    elif num == 28:
        #'Plant: Refresh your abilities after making 3 attacks (once per duel).'
        if DM.phase == 4 and indicator == 'Go':
            if DM.turn == owner:
                if gowner.passive[1] < 3 and (gowner.ability[1] < 1 or gowner.ability[3] < 1):
                    gowner.passive[1] += 1
                if gowner.passive[1] == 1:
                    gowner.passive[1] = 4 #To stop the counting and future refreshes
                    gowner.ability[1] = 1
                    gowner.ability[3] = 1
                    w = '*>> Plant: ' + gowner.name + '\'s abilities have refreshed!*'

    elif num == 29:
        #'Phoenix: When defeated, revive with 1 health after 6 turns (once per duel).'
        if (DM.phase == 4 and indicator == 'Go') or indicator == 'Dmg':
            if not gowner.alive and gowner.passive[1] == 0:
                gowner.passive[1] = 1
                DM.passiveList.append([num, gowner.id, 0])
                w = '*>> ' + 'Phoenix: ' + gowner.name + ' turns into a pile of ash, they will revive after 6 turns!*'
    
    elif num == 30:
        #'Holy: +2 to attack rolls if there is a [Celestial] or [Angel] Gemma in your team.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                if gowner.passive[1] == 0: #saving time
                    gowner.passive[1] = -1
                    dl = DM.duelists[owner]
                    tm = [dl.g2.ctype, dl.g3.ctype]
                    ok = False
                    for ctype in tm:
                        if ctype == 'Celestial' or ctype == 'Angel':
                            ok = True
                            gowner.passive[1] = 1
                            break
                    if ok:
                        a = BonusLevelScaling[gowner.level-1] #Level scaling
                        DM.atkbonus += 2*a
                        w = '*>> Holy: +' + str(2*a) + ' attack for ' + gowner.name + '*'
                elif gowner.passive[1] == 1:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += 2*a
                    w = '*>> Holy: +' + str(2*a) + ' attack for ' + gowner.name + '*'

    elif num == 31:
        #'Infernal: +1 to attack rolls for every other living Dark type in your team (max +2).'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                dl = DM.duelists[owner]
                tm = [dl.g2, dl.g3]
                gowner.passive[1] = 0
                for gem in tm:
                    if (gem.type1 == 9 or gem.type2 == 9) and gem.alive and gowner.passive[1] < 2:
                        gowner.passive[1] += 1
                
                if gowner.passive[1] > 0:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += gowner.passive[1]*a
                    w = '*>> Infernal: +' + str(gowner.passive[1]*a)+ ' attack for ' + gowner.name + '*'
        
    elif num == 32:
        #'Cloud: +1 to defence rolls for every other living Wind type in your team (max +2)'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == notowner and indicator == 'Attack':
                dl = DM.duelists[owner]
                tm = [dl.g2, dl.g3]
                gowner.passive[1] = 0
                for gem in tm:
                    if (gem.type1 == 10 or gem.type2 == 10) and gem.alive and gowner.passive[1] < 2:
                        gowner.passive[1] += 1
                if gowner.passive[1] > 0:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.defbonus += gowner.passive[1]*a
                    w = '*>> Cloud: +' + str(gowner.passive[1]*a) + ' defence for ' + gowner.name + '*'
                    
    elif num == 33:
        #'Explosion: Double all speed, attack and defence rolls.'
        if (DM.phase == 2 or DM.phase == 4) and indicator == 'Attack':
            at = round(DM.atkroll * 2)
            de = round(DM.defroll * 2)

            DM.atkroll = at
            DM.defroll = de
            w = '*>> Explosion: Double all rolls.*'
        elif DM.phase == 1 and indicator == '':
            sp = round(DM.spdroll * 2)
            esp = round(DM.espdroll * 2)
            
            DM.spdroll = sp
            DM.espdroll = esp
            w = '*>> Explosion: Double all rolls.*'
    
    elif num == 34:
        #'Titan: Your heavy attacks remove 1 guard regardless of the outcome.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack' and gnotowner.guard > 0:
                if DM.caliber == 1:
                    gnotowner.guard -= 1
                    w = '*>> Titan: ' + gowner.name + '\'s heavy attack removes 1 guard from ' + gnotowner.name + '.*'
                    if gnotowner.guard < 0:
                        gnotowner.guard = 0
                        w += '\n:diamond_shape_with_a_dot_inside: **Guard Break** :diamond_shape_with_a_dot_inside:'
                    
    elif num == 35:
        #'Sylph: +1 to attack rolls for regular attacks.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                if DM.caliber == 0:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += 1*a
                    w = '*>> Sylph: +' + str(1*a) + ' attack for ' + gowner.name + '*'
        
    elif num == 36:
        #'Dryad: Reset all stat changes to attack, defence, and speed in your team (once per duel)'
        if DM.phase == 1 and gowner.passive[1] == 0 and indicator == '':
            gowner.passive[1] = 1
            dl = DM.duelists[owner]
            index = findName(dl.duelistname)
            dl.g1.attack = TeamList[index].g1.attack
            dl.g1.defence = TeamList[index].g1.defence
            dl.g1.speed = TeamList[index].g1.speed
            dl.g2.attack = TeamList[index].g2.attack
            dl.g2.defence = TeamList[index].g2.defence
            dl.g2.speed = TeamList[index].g2.speed
            dl.g3.attack = TeamList[index].g3.attack
            dl.g3.defence = TeamList[index].g3.defence
            dl.g3.speed = TeamList[index].g3.speed
                
            w = '*>> Dryad: Attack, defence and speed changes in ' + gowner.name + '\'s team have been reset.*'
    
    elif num == 37:
        #'Undead: **+' + str(1*a) + '** to defence rolls for every fainted Gemma in your team.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == notowner and indicator == 'Attack':
                dl = DM.duelists[owner]
                tm = [dl.g2, dl.g3]
                gowner.passive[1] = 0
                for gem in tm:
                    if not gem.alive and gowner.passive[1] < 2 and gem.id != 'NULL':
                        gowner.passive[1] += 1
                if gowner.passive[1] > 0:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.defbonus += gowner.passive[1]*a
                    w = '*>> Undead: +' + str(gowner.passive[1]*a) + ' defence for ' + gowner.name + '*'

    elif num == 38:
        #'Monstrosity: **+' + str(1*a) + '** to attack rolls for every fainted Gemma in your team.'
        if DM.phase == 2 or DM.phase == 4:
            if DM.turn == owner and indicator == 'Attack':
                dl = DM.duelists[owner]
                tm = [dl.g2, dl.g3]
                gowner.passive[1] = 0
                for gem in tm:
                    if not gem.alive and gowner.passive[1] < 2 and gem.id != 'NULL':
                        gowner.passive[1] += 1
                if gowner.passive[1] > 0:
                    a = BonusLevelScaling[gowner.level-1] #Level scaling
                    DM.atkbonus += gowner.passive[1]*a
                    w = '*>> Monstrosity: +' + str(gowner.passive[1]*a) + ' attack for ' + gowner.name + '*'

    else:
        w = '-1'
        
    return w


############################################################################################################
############################################################################################################
############################################################################################################


#   HELP FUNCTIONS


############################################################################################################
############################################################################################################
############################################################################################################

def findTimeList(userid, gemID): #Returns the time stamp in TeamList, if none found, create one with timestamp now.
    temp = -1
    for i in range(len(TimeList)):
        if userid == TimeList[i][0] and gemID == TimeList[i][1]:
            temp = TimeList[i][2]
            break
    if temp == -1:
        temp = time.clock()
        i = len(TimeList)
        TimeList.append([userid, gemID, temp])
    ret = [temp, i]
    return ret

def assignTeamSlot(duelist, gnum, gem):
    if gnum == 1: duelist.g1 = gem
    elif gnum == 2: duelist.g2 = gem
    elif gnum == 3: duelist.g3 = gem

def getGem(duelist, no):
    if no == 1: return duelist.g1
    elif no == 2: return duelist.g2
    elif no == 3: return duelist.g3
    else: return -1

def getGemName(duelist, name):
    if name == duelist.g1.name: 
        return duelist.g1
    elif name == duelist.g2.name: 
        return duelist.g2
    elif name == duelist.g3.name: 
        return duelist.g3
    else: return -1

#Prepares the texts used in makeEmbed
def prepareEmbed(gem):
    ab1 = -1
    ab2 = -1
    pas  =-1
    title = gem.name + '\tLevel: **' + str(gem.level) + '**'
    
    if gem.mood == 5: mood = 'Great'
    elif gem.mood > 2: mood = 'Good'
    elif gem.mood == -5: mood = 'Awful'
    elif gem.mood < -2: mood = 'Bad'
    else: mood = 'Neutral'
    
    sp = '\u200B \u200B \u200B \u200B \u200B \u200B \u200B'

    disc = 'Type: **' + TypeList[gem.type1] + '/' + TypeList[gem.type2] + '**'
    if gem.ctype != '': disc += ' [**' + gem.ctype + '**]' 
    if gem.level == 10: next = 'MAX'
    else: next = '%.0f' % (TotalExp[gem.level-1] - gem.exp)
    disc += '\nEXP: **' + '%.0f' % gem.exp + '**' + sp + 'EXP to next level: **' + next + '**\n' \
        + 'Personality: **' + PetList[gem.personality][0] + '**' + sp + 'Mood: **' + mood + '**\nHealth: '
    
    if gem.hp <= 0: disc += ':skull:'
    else:
        for i in range(0, gem.hp): disc += ':heart:'
        for i in range(0, gem.maxhp - gem.hp): disc += ':black_heart:'
        for i in range(0, gem.guard): disc += ':shield:'
    
    disc += '\nAttack: **' + str(DiceList[gem.attack]) + '**, Defence: **' + str(DiceList[gem.defence]) + \
        '**, Speed: **' + str(DiceList[gem.speed]) + '**'
    
    if gem.ability[0] != -1:
        ab1 = '**>>** ' + abilityDict(gem.ability[0], gem.level)
        if gem.ability[1] == 0: ab1 += ' **- Used**'    
    if gem.ability[2] != -1:
        ab2 = '**>>** ' + abilityDict(gem.ability[2], gem.level) 
        if gem.ability[3] == 0: ab2 += ' **- Used**'
    if gem.ctype != '':
        pas = '**>>** ' + passiveDict(gem.passive[0], gem.level)
    
    return title, disc, ab1, ab2, pas

def makeEmbed(title, disc, ab1, ab2, pas):
    embed = discord.Embed(
        title = title,
        description = disc,
        color = discord.Colour.blue()
    )
    if ab2 == -1:
        embed.add_field(name='Abilities:', value = ab1)
    else:
        embed.add_field(name='Abilities:', value = ab1 + '\n' + ab2)
    if pas != -1:
        embed.add_field(name='Passive:', value = pas)
    return embed

#Only adds additional fields for an existing embed for showing a Gemma
def extendEmbed(embed, title, disc, ab1, ab2, pas):
    embed.add_field(name='**'+title+'**', value = disc)
    if ab2 == -1:
        embed.add_field(name='Abilities:', value = ab1)
    else:
        embed.add_field(name='Abilities:', value = ab1 + '\n' + ab2)
    if pas != -1:
        embed.add_field(name='Passive:', value = pas)
    return embed

#save(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, AItaskList)
def savelist(tm, dm, mg, ad, tl, tagl, e4):
    savebin = [tm, dm, mg, ad, tl, tagl, e4]
    with open('jaegersave.pickle', 'wb') as f:
        pickle.dump(savebin, f, protocol=pickle.HIGHEST_PROTOCOL)


#load(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, AItaskList)
def loadlist():
    global TeamList
    global DuelmemList
    global maxGID
    global AdminList
    global TimeList
    global TagList
    global E4
    try:
        with open('jaegersave.pickle', 'rb') as f:
            try:
                savebin = pickle.load(f)
                TeamList = savebin[0]
                DuelmemList = savebin[1]
                maxGID = savebin[2]
                AdminList = savebin[3]
                TimeList = savebin[4]
                TagList = savebin[5]
                E4 = savebin[6]
                print('All loaded')
            except EOFError:
                print('Did not manage to load')
    except FileNotFoundError:
        print('No save file found')

#Returns the user's index in TeamList by searching for userid
def findTeam(userid):
    temp = -1
    for i in range(len(TeamList)):
        if userid == TeamList[i].userid:
            temp = i
            break
    return temp

#Returns the user's index in TeamList by searching for duelistname
def findName(name):
    temp = -1
    for i in range(len(TeamList)):
        if name == TeamList[i].duelistname:
            temp = i
            break
    return temp

#Return the user's entry in the TagList, if present
def findTag(user):
    for i, entry in enumerate(TagList):
        if user == entry[0]:
            return [True, entry[1]]
    return [False, '-1']

#Return true if the gemma's user has the turn
def memGemHasTurn(DM, gemid):
    turn = DM.turn
    if gemid == DM.duelists[0].g1.id:
        if turn == 0: return True
        else: return False
    if gemid == DM.duelists[1].g1.id:
        if turn == 1: return True
        else: return False

#Return the index of a duel in the duelmemory using the dueltag
def memfindDueltag(dueltag):
    temp = -1
    for i in range(len(DuelmemList)):
        if dueltag == DuelmemList[i].dueltag:
            temp = i
            break
    return temp

#Return the index of a duelists team in the duel memory "duelists" slot
def memfindTeam(userid, dueltag):
    temp = -1
    temp2 = -1
    if dueltag != -1: 
        if DuelmemList[memfindDueltag(dueltag)].duelists[0].userid == userid:
            temp = 0
            temp2 = 1
        else:
            temp = 1
            temp2 = 0
    return [temp, temp2] #temp is the index of the user, temp2 is index for their opponent

def removeFromTagList(user, tagcommand): #Remove user from TagList
    for i, entry in enumerate(TagList):
        if entry[0] == user and entry[1] == tagcommand:
            del TagList[i]
            break

def rollInitiative(DM, playerIndex, enemyIndex):
    speed = DM.duelists[playerIndex].g1.speed #speed stat of user player's first Gemma
    espeed = DM.duelists[enemyIndex].g1.speed #speed stat of opponent player's first Gemma
    speedroll = random.randint(1, DiceList[speed])
    espeedroll = random.randint(1, DiceList[espeed])
    DM.spdroll = speedroll
    DM.espdroll = espeedroll
    DM.phase = 1

    player = DM.duelists[playerIndex]        
    enemy = DM.duelists[enemyIndex]        
    
    #The duelist with the player index has its roll stored in .spdroll, the duelist with the enemy index has it stored in .espdroll
    disc = player.g1.name + ' speed: **' + str(speedroll) + '**\n' + enemy.g1.name + ' speed: **' + str(espeedroll) + '**'

    embed = discord.Embed(
        title = 'Initiative',
        description = disc,
        color = discord.Colour.gold()
    )

    hpbar = ''
    if player.g1.hp <= 0: hpbar += ':skull:'
    else:
        for i in range(0, player.g1.hp): hpbar += ':heart:'
        for i in range(0, player.g1.maxhp - player.g1.hp): hpbar += ':black_heart:'
        for i in range(0, player.g1.guard): hpbar += ':shield:'

    disc1 = '**' + player.g1.name + '** - ' + hpbar 

    hpbar = ''
    if enemy.g1.hp <= 0: hpbar += ':skull:'
    else:
        for i in range(0, enemy.g1.hp): hpbar += ':heart:'
        for i in range(0, enemy.g1.maxhp - enemy.g1.hp): hpbar += ':black_heart:'
        for i in range(0, enemy.g1.guard): hpbar += ':shield:'

    disc2 = '**' + enemy.g1.name + '** - ' + hpbar
    
    disc1 += ' ' + TypeList[player.g1.type1] + '/' + TypeList[player.g1.type2]
    ctype = player.g1.ctype
    if ctype != '':
        disc1 += ' [' + ctype + ']'
    disc2 += ' ' + TypeList[enemy.g1.type1] + '/' + TypeList[enemy.g1.type2]
    ctype = enemy.g1.ctype
    if ctype != '':
        disc2 += ' [' + ctype + ']'

    embed.add_field(name='Gemma', value = disc1 + '\n' + disc2)
    
    ###PASSIVE TRIGGER
    if DM.duelists[0].g1.ctype != '':
        v1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, '', -1)
        if v1 != '-1':
            embed.add_field(name='Passive ability', value = v1)
    if DM.duelists[1].g1.ctype != '':
        v2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, '', -1)
        if v2 != '-1':
            embed.add_field(name='Passive ability', value = v2)
    ###END OF PASSIVE TRIGGER
    
    return embed

#sourceID: Attack = 0, Ability = 1, Deathbyendofduel = 2, (pet = 3), deposit = 4
def awardAP(DM, owner, sourceID): 
    gemID = DM.duelists[owner].g1.id
    [tstamp, TimeListIndex] = findTimeList(DM.duelists[owner].userid, gemID)
    nowtime = time.clock()+600
    
    gem = DM.duelists[owner].g1
    if abs(tstamp-nowtime) > 600:
        TimeList[TimeListIndex][2] = nowtime
        gem.AP += APImpact[gem.personality][sourceID]
        if gem.AP > 15: gem.AP = 15
        elif gem.AP < 0: gem.AP = 0
    
    gem.mood += MoodImpact[gem.personality][sourceID]
    if gem.mood > 6: gem.mood = 5
    elif gem.mood < -6: gem.mood = -5

#Used to sort abilityList
def getKey(item):
    return item[0]

#Find and return the Gemma object with the specific gemID in the duel
def findGemIDduel(DM, gemID):
    if gemID == DM.duelists[0].g1.id:
        retgemma = DM.duelists[0].g1
    elif gemID == DM.duelists[0].g2.id:
        retgemma = DM.duelists[0].g2
    elif gemID == DM.duelists[0].g3.id:
        retgemma = DM.duelists[0].g3
    elif gemID == DM.duelists[1].g1.id:
        retgemma = DM.duelists[1].g1
    elif gemID == DM.duelists[1].g2.id:
        retgemma = DM.duelists[1].g2
    else:
        retgemma = DM.duelists[1].g3
    return retgemma

#Searches through both teams, looking for a loser or a tie.
def findLoser(DM):
    LoserA = False
    LoserB = False
    if not DM.duelists[0].g1.alive and \
    not DM.duelists[0].g2.alive and \
    not DM.duelists[0].g3.alive:
        LoserA = True
    if not DM.duelists[1].g1.alive and \
    not DM.duelists[1].g2.alive and \
    not DM.duelists[1].g3.alive:
        LoserB = True

    result = -1
    if LoserA and LoserB:
        result = 0
    elif LoserA:
        result = 1
    elif LoserB:
        result = 2
    return result  

################

#TotalExp = [60, 180, 450, 900, 1500, 2250, 3200, 4300, 5500, -1]

def LevelUp(duelists_index, DM):
    w = ''
    index = findName(DM.duelists[duelists_index].duelistname)
    gem1 = TeamList[index].g1
    gem2 = TeamList[index].g2
    gem3 = TeamList[index].g3
    gems = [gem1, gem2, gem3]
    nothing = True
    for gem in gems:
        go = True
        while(go):
            if gem.level < 10:
                #If you have equal to or above the total exp for next level:
                if gem.exp >= TotalExp[gem.level-1]:
                    nothing = False
                    gem.level += 1
                    atkboost = StatDistribution[gem.personality][gem.level-2][0] 
                    defboost = StatDistribution[gem.personality][gem.level-2][1]
                    spdboost = StatDistribution[gem.personality][gem.level-2][2]
                    w += '\n**' + gem.name + '** reached **level ' + str(gem.level) + '!**' + '\nAttack: **+' \
                        + str(atkboost) + '**\nDefence: **+' + str(defboost) + '**\nSpeed: **+' + str(spdboost) + '**\n'
                    gem.attack += atkboost
                    gem.defence += defboost
                    gem.speed += spdboost
                    if gem.level == 3:
                        gem.levelup = 1
                        w += 'Use ``!upgrade`` to pick ' + gem.name + '\'s second ability!\n' #2nd ability, pick between 2 or 3 options
                    if gem.level == 5:
                        gem.maxhp += 1
                        gem.hp += 1
                        w += 'Max HP: **+1**\n'
                    if gem.level == 7:
                        if gem.levelup == 1:
                            gem.levelup = 3
                        else:
                            gem.levelup = 2
                        w += 'Use ``!upgrade`` to pick a new secondary type for ' + gem.name + ' (optional)\n' #Type switch
                    if gem.level == 10:
                        if gem.levelup == 2:
                            gem.levelup = 5
                        elif gem.levelup == 3:
                            gem.levelup = 6
                        else:
                            gem.levelup = 4
                        w += 'Use ``!upgrade`` to replace one of ' + gem.name + '\'s abilities (optional)\n' #Ability switch, pick between 2 or 3 options, replace 1st or 2nd
                else:
                    go = False
            else:
                go = False
                gem.exp = TotalExp[8]
    if nothing:
        w = '-1'
    return w


async def actOnLoser(result, DM, owner, notowner):
    disc = ''
    indA = findName(DM.duelists[0].duelistname)
    indB = findName(DM.duelists[1].duelistname)
    LVA = '-1'
    LVB = '-1'
    if result != -1:
        if result == 0:
            disc += '**The duel ends in a TIE!**'
            TeamList[indA].tokens += 1
            TeamList[indB].tokens += 1
            disc += '\n\nDuelist ' + TeamList[indA].duelistname + ' and duelist ' + TeamList[indB].duelistname + ' are both awarded 1 token!'
        
        if result == 1:
            disc += '**Duelist ' + DM.duelists[1].duelistname + ' wins the duel!**'
            TeamList[indB].wincount += 1
            TeamList[indB].star += 1
            TeamList[indA].losecount += 1
            TeamList[indA].star -= 1
            if TeamList[indA].star < 0: TeamList[indA].star = 0
            lindex = indA #Loser Index
            windex = indB #Winner Index

            TeamList[indA].tokens += 1
            TeamList[indB].tokens += 2
            if TeamList[indA].bot:
                disc += '\n\nDuelist ' + TeamList[indB].duelistname + ' is awarded 2 tokens!'
            elif TeamList[indB].bot:
                disc += '\n\nDuelist ' + TeamList[indA].duelistname + ' is awarded 1 token!'
            else:
                disc += '\n\nDuelist ' + TeamList[indA].duelistname + ' is awarded 1 token and duelist ' + TeamList[indB].duelistname + ' is awarded 2 tokens!'
            

            #Elite Four progress
            if TeamList[indA].bot and TeamList[indA].user == 1:
                if TeamList[indA].duelistname == 'NPC E4 Kimi': 
                    E4[0].append(TeamList[indB].userid)
                    disc += '\n\nKimi:\n\"It seems you are a cut above the average challenger, go ahead and face the next Elite Four duelist.\"'
                    disc += '\n\nYou have defeated Elite Four Kimi, your next opponent will be Elite Four Lorasatra'
                elif TeamList[indA].duelistname == 'NPC E4 Lorasatra': 
                    E4[1].append(TeamList[indB].userid)
                    disc += '\n\nLorasatra:\n\"Oh my, you\'re quite a tough cookie aren\'t you? Color me impressed, now run along to the next challenge.\"'
                    disc += '\n\nYou have defeated Elite Four Lorasatra, your next opponent will be Elite Four Gilbert'
                elif TeamList[indA].duelistname == 'NPC E4 Gilbert': 
                    E4[2].append(TeamList[indB].userid)
                    disc += '\n\nGilbert:\n\"Ahhahaha! Splendid! Wonderful! It\'s been a while since I had a duel that exhilarating! Go ahead duelist, you beat me fair and square.\"'
                    disc += '\n\nYou have defeated Elite Four Gilbert, your next opponent will be Elite Four Cosette'
                elif TeamList[indA].duelistname == 'NPC E4 Cosette': 
                    E4[3].append(TeamList[indB].userid)
                    disc += '\n\nCosette:\n\"...\"\n\"' + TeamList[indB].duelistname + ' huh? I\'ll remember your name.\"'
                    disc += '\n\nYou have defeated Elite Four Cosette, your next opponent will be the Champion, Sivaruz'
                elif TeamList[indA].duelistname == 'NPC Champion Sivaruz': 
                    E4[4].append(TeamList[indB].userid)
                    E4[5].append(TeamList[indB].userid)
                    disc += '\n\nSivaruz:\n\"Defeat is truly bittersweet. One will fall and one will rise, and today you have risen to the very top.\"'
                    disc += '\n\nCongratulations! You have defeated all of the Elite Four and the champion. Your name will be enscribed in the Hall of Fame :medal:'
            elif TeamList[indB].bot and TeamList[indB].user == 1:
                for i in range(0, 5): #Does not remove a hall of fame record
                    try:
                        E4[i].remove(TeamList[indA].userid)
                    except ValueError:
                        pass
                disc += '\n\nYou have failed the Elite Four challenge, but don\'t give up! Please try again from the beginning.'

        if result == 2:
            disc += '**Duelist ' + DM.duelists[0].duelistname + ' wins the duel!**'
            TeamList[indA].wincount += 1
            TeamList[indA].star += 1
            TeamList[indB].losecount += 1
            TeamList[indB].star -= 1
            if TeamList[indB].star < 0: TeamList[indB].star = 0
            lindex = indB #Loser Index
            windex = indA #Winner Index

            TeamList[indA].tokens += 2
            TeamList[indB].tokens += 1
            if TeamList[indB].bot:
                disc += '\n\nDuelist ' + TeamList[indA].duelistname + ' is awarded 2 tokens!'
            elif TeamList[indA].bot:
                disc += '\n\nDuelist ' + TeamList[indB].duelistname + ' is awarded 1 token!'    
            else:
                disc += '\n\nDuelist ' + TeamList[indA].duelistname + ' is awarded 2 tokens and duelist ' + TeamList[indB].duelistname + ' is awarded 1 token!'

            #Elite Four progress
            if TeamList[indB].bot and TeamList[indB].user == 1:
                if TeamList[indB].duelistname == 'NPC E4 Kimi': 
                    E4[0].append(TeamList[indA].userid)
                    disc += '\n\nKimi:\n\"It seems you are a cut above the average challenger, go ahead and face the next Elite Four duelist.\"'
                    disc += '\n\nYou have defeated Elite Four Kimi, your next opponent will be Elite Four Lorasatra'
                elif TeamList[indB].duelistname == 'NPC E4 Lorasatra': 
                    E4[1].append(TeamList[indA].userid)
                    disc += '\n\nLorasatra:\n\"Oh my, you\'re quite a tough cookie aren\'t you? Color me impressed, now run along to the next challenge.\"'
                    disc += '\n\nYou have defeated Elite Four Lorasatra, your next opponent will be Elite Four Gilbert'
                elif TeamList[indB].duelistname == 'NPC E4 Gilbert': 
                    E4[2].append(TeamList[indA].userid)
                    disc += '\n\nGilbert:\n\"Ahhahaha! Splendid! Wonderful! It\'s been a while since I had a duel that exhilarating! Go ahead duelist, you beat me fair and square.\"'
                    disc += '\n\nYou have defeated Elite Four Gilbert, your next opponent will be Elite Four Cosette'
                elif TeamList[indB].duelistname == 'NPC E4 Cosette': 
                    disc += '\n\nCosette:\n\"...\"\n\"' + TeamList[indA].duelistname + ' huh? I\'ll remember your name.\"'
                    disc += '\n\nYou have defeated Elite Four Cosette, your next opponent will be the Champion, Sivaruz'
                    E4[3].append(TeamList[indA].userid)
                elif TeamList[indB].duelistname == 'NPC Champion Sivaruz': 
                    E4[4].append(TeamList[indA].userid)
                    E4[5].append(TeamList[indA].userid)
                    disc += '\n\nSivaruz:\n\"Defeat is truly bittersweet. One will fall and one will rise, and today you have risen to the very top.\"'
                    disc += '\n\nCongratulations! You have defeated all of the Elite Four and the champion! Your name will be enscribed in the Hall of Fame :medal:'
            elif TeamList[indA].bot and TeamList[indA].user == 1:
                for i in range(0, 5): #Does not remove a hall of fame record
                    E4[i].remove(TeamList[indB].userid)

                    disc += '\n\nYou have failed the Elite Four challenge, but don\'t give up! Please try again from the beginning.'

        ###################### GANG START
        wgang = getGang(windex)
        lgang = getGang(lindex)
        user = TeamList[windex].user
        if wgang != -1 and not TeamList[lindex].bot: #If winner has a gang
            TeamList[lindex].elite[getGangIndex(wgang)] = [] #Lost win streak against winner gang
        if lgang != -1 and not TeamList[windex].bot: #If loser has a gang
    
            gangIndex = getGangIndex(lgang) #get index in RoleList
    
            if not (TeamList[windex].badge[gangIndex] == 1 or TeamList[windex].badge[gangIndex] == 3):
    
                if not TeamList[lindex].userid in TeamList[windex].basic[gangIndex]:
                    #You have not beaten this gang member before
    
                    TeamList[windex].basic[gangIndex].append(TeamList[lindex].userid)

                    if len(TeamList[windex].basic[gangIndex]) > 2:
                        if TeamList[windex].badge[gangIndex] == 0:
                            TeamList[windex].badge[gangIndex] = 1
                        elif TeamList[windex].badge[gangIndex] == 2:
                            TeamList[windex].badge[gangIndex] = 3
                        disc += '\n\nDuelist ' + TeamList[windex].duelistname + ' has earned the ' + BadgeDict[gangIndex] + ' badge!'
                        TeamList[windex].basic[gangIndex] = []
                    else:
                        r = get(TeamList[windex].user.server.roles, id = lgang.id)
                        disc += '\n' + str(len(TeamList[windex].basic[gangIndex])) + ' duelists from **' + r.name + '** beaten.'
            
            if not (TeamList[windex].badge[gangIndex] == 2 or TeamList[windex].badge[gangIndex] == 3):    
    
                if not TeamList[lindex].userid in TeamList[windex].elite[gangIndex]:
                    #This gang member is in your win streak
                    TeamList[windex].elite[gangIndex].append(TeamList[lindex].userid)
                    
                    if len(TeamList[windex].elite[gangIndex]) > 2:
                        if TeamList[windex].badge[gangIndex] == 0:
                            TeamList[windex].badge[gangIndex] = 2
                        elif TeamList[windex].badge[gangIndex] == 1:
                            TeamList[windex].badge[gangIndex] = 3
                        disc += '\n\nDuelist ' + TeamList[windex].duelistname + ' has earned the ' + EbadgeDict[gangIndex] + ' badge!'
                        TeamList[windex].elite[gangIndex] = []
                    else:
                        r = get(user.server.roles, id = lgang.id)
                        disc += '\nWin streak of ' + str(len(TeamList[windex].elite[gangIndex])) + ' against **' + r.name + '**'              
        ###################### GANG END

        if DM.duelists[0].bot or DM.duelists[1].bot:
            AIindex = findAItask(DM.duelists[0].dueltag)
            if AIindex != -1:
                AItaskList[AIindex].task.cancel()
                AItaskList.remove(AItaskList[AIindex])

        TeamList[indA].opponent = '-1'
        TeamList[indA].dueltag = -1
        TeamList[indB].opponent = '-1'
        TeamList[indB].dueltag = -1

        if not DM.duelists[0].bot:
            #Finds the Gemma object in TeamList corresponding to the Gemma in Duelmemory
            og1 = findGemID(DM, indA, DM.duelists[0].g1.id)
            og2 = findGemID(DM, indA, DM.duelists[0].g2.id)
            og3 = findGemID(DM, indA, DM.duelists[0].g3.id)
            
            #accesses its AP variable and update with the AP gained in the battle.
            og1.AP = DM.duelists[0].g1.AP
            og2.AP = DM.duelists[0].g2.AP
            og3.AP = DM.duelists[0].g3.AP

            #Award XP
            print(' &-&-&-&-& award ', DM.duelists[0].g1.exp, ' xp from ', DM.duelists[0].g1.name, ' to ', og1.name)
            og1.exp = DM.duelists[0].g1.exp
            print(' &-&-&-&-& award ', DM.duelists[0].g2.exp, ' xp from ', DM.duelists[0].g2.name, ' to ', og2.name)
            og2.exp = DM.duelists[0].g2.exp
            print(' &-&-&-&-& award ', DM.duelists[0].g3.exp, ' xp from ', DM.duelists[0].g3.name, ' to ', og3.name)
            og3.exp = DM.duelists[0].g3.exp
            
            LVA = LevelUp(0, DM)
            
        if not DM.duelists[1].bot:
            #Finds the Gemma object in TeamList corresponding to the Gemma in Duelmemory        
            nog1 = findGemID(DM, indB, DM.duelists[1].g1.id)
            nog2 = findGemID(DM, indB, DM.duelists[1].g2.id)
            nog3 = findGemID(DM, indB, DM.duelists[1].g3.id)

            #accesses its AP variable and update with the AP gained in the battle.
            nog1.AP = DM.duelists[1].g1.AP
            nog2.AP = DM.duelists[1].g2.AP
            nog3.AP = DM.duelists[1].g3.AP

            #Award XP
            print(' &-&-&-&-& award ', DM.duelists[1].g1.exp, ' xp from ', DM.duelists[1].g1.name, ' to ', nog1.name)
            nog1.exp = DM.duelists[1].g1.exp
            print(' &-&-&-&-& award ', DM.duelists[1].g2.exp, ' xp from ', DM.duelists[1].g2.name, ' to ', nog2.name)
            nog2.exp = DM.duelists[1].g2.exp
            print(' &-&-&-&-& award ', DM.duelists[1].g3.exp, ' xp from ', DM.duelists[1].g3.name, ' to ', nog3.name)
            nog3.exp = DM.duelists[1].g3.exp

            LVB = LevelUp(1, DM)
        
        await asyncio.sleep(0.5)
        print(' &-&-&-&-& still in actOnLoser, time to print endslate')
        embed = discord.Embed(
            title = 'End of duel',
            description = disc,
            color = discord.Colour.green()
        )

        await bot.send_message(DM.channel, embed=embed)
        await asyncio.sleep(0.5)
        if LVA != '-1':
            await bot.send_message(DM.channel, LVA)
        if LVB != '-1':
            await bot.send_message(DM.channel, LVB)   
                
        DuelmemList.remove(DM)
        print(' &-&-&-&-& Saving')        
        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)

        print(' &-&-&-&-& Deleting temporary bot')
        #Deleting temporary bots
        if TeamList[indA].bot and TeamList[indA].user == -1:
            #Random NPC, remove from TeamList
            TeamList.remove(TeamList[indA])
        elif TeamList[indB].bot and TeamList[indB].user == -1:
            #Random NPC, remove from TeamList
            TeamList.remove(TeamList[indB])


def getGang(index):
    g = -1
    if not TeamList[index].bot:
        for gang in TeamList[index].user.roles:
            for role in RoleList:
                if gang.id == role:
                    g = gang
    return g

def getGangCount(id):
    c = 0
    for i, d in enumerate(TeamList):
        gang = getGang(i)
        if gang != -1:
            if gang.id == id:
                c += 1
    return c

def getGangIndex(gang):
    ind = -1
    for i, role in enumerate(RoleList):
        if role == gang.id:
            return i
    return ind

#Find and return the Gemma object with the specific gemID in TeamList teams
def findGemID(DM, index, gemID):
    if gemID == TeamList[index].g1.id:
        retgemma = TeamList[index].g1
    elif gemID == TeamList[index].g2.id:
        retgemma = TeamList[index].g2
    else:
        retgemma = TeamList[index].g3
    return retgemma

def rotateTeam(DM, owner):
    playerIndex = DM.turn
    enemyIndex = -1 #temporary just to define it
    if playerIndex == 0:
        enemyIndex = 1
    else:
        enemyIndex = 0
    
    #Owner is the index in .duelists of the player that used the rotate command
    if owner == 1: notowner = 0
    else: notowner = 1

    """ 
    v1 = '-1'
    v2 = '-1'

    ###PASSIVE TRIGGER
    if DM.duelists[0].g1.ctype != '':
        v1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Rotate', -1)
    if DM.duelists[1].g1.ctype != '':
        v2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, notowner, 'Rotate', -1)
    ###END OF PASSIVE TRIGGER
    """

    #We rotate so new Gemma face each other, we should not remember any previous attack roll
    DM.atkroll = 0
    DM.defroll = 0
    DM.atkbonus = 0
    DM.defbonus = 0
    DM.typemod = 0

    DM.duelists[0].gotrigger = False
    DM.duelists[1].gotrigger = False
    
    frontAlive = False #Just to get the loop going
    while not frontAlive:
        temp1 = DM.duelists[owner].g1
        temp2 = DM.duelists[owner].g2 
        temp3 = DM.duelists[owner].g3
        
        DM.duelists[owner].g1 = temp2 
        DM.duelists[owner].g2 = temp3 
        DM.duelists[owner].g3 = temp1 
        frontAlive = DM.duelists[owner].g1.alive
    
    #Restore guard for all Gemma
    DM.duelists[owner].g1.guard = DM.duelists[owner].g1.maxguard
    DM.duelists[owner].g2.guard = DM.duelists[owner].g2.maxguard
    DM.duelists[owner].g3.guard = DM.duelists[owner].g3.maxguard

    disc = DM.duelists[owner].duelistname + '\'s new team order:\n'
    gem = DM.duelists[owner].g1
    disc += 'Lv.' + str(gem.level) + ' **' + gem.name + '** - '
    if gem.hp <= 0: disc += ':skull:'
    else:
        for i in range(0, gem.hp): disc += ':heart:'
        for i in range(0, gem.maxhp - gem.hp): disc += ':black_heart:'
        for i in range(0, gem.guard): disc += ':shield:'
    disc += ' The ' + TypeList[DM.duelists[owner].g1.type1] + '/' + TypeList[DM.duelists[owner].g1.type2]
    ctype = gem.ctype
    if ctype != '':
        disc += ' [' + ctype + ']'
    disc += ' Gemma'

    gem = DM.duelists[owner].g2
    if gem.id != 'NULL':
        disc += '\n\nLv.' + str(gem.level) + ' **' + gem.name + '** - '
        if gem.hp <= 0: disc += ':skull:'
        else:
            for i in range(0, gem.hp): disc += ':heart:'
            for i in range(0, gem.maxhp - gem.hp): disc += ':black_heart:'
            for i in range(0, gem.guard): disc += ':shield:'
    
    gem = DM.duelists[owner].g3
    if gem.id != 'NULL':
        disc += '\nLv.' + str(gem.level) + ' **' + gem.name + '** - '
        if gem.hp <= 0: disc += ':skull:'
        else:
            for i in range(0, gem.hp): disc += ':heart:'
            for i in range(0, gem.maxhp - gem.hp): disc += ':black_heart:'
            for i in range(0, gem.guard): disc += ':shield:'
    
    embed = discord.Embed(
        title = 'Rotation',
        description = disc,
        color = discord.Colour.red()
    )
    
    """
    if v1 != '-1':
        embed.add_field(name='Passive ability', value = v1)
    if v2 != '-1':
        embed.add_field(name='Passive ability', value = v2)
    """

    return embed

#Returns a string instead of an embed, used by abilities that rotate since their text will be in an ability embed already.
def rotateTeam_ab(DM, owner):
    playerIndex = DM.turn
    enemyIndex = -1 #temporary just to define it
    if playerIndex == 0:
        enemyIndex = 1
    else:
        enemyIndex = 0
    
    #Owner is the index in .duelists of the player that used the rotate command
    if owner == 1: notowner = 0
    else: notowner = 1
    
    v1 = '-1'
    v2 = '-1'
    ###PASSIVE TRIGGER
    if DM.duelists[0].g1.ctype != '':
        v1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Rotate', -1)
    if DM.duelists[1].g1.ctype != '':
        v2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, notowner, 'Rotate', -1)
    ###END OF PASSIVE TRIGGER
    
    #We rotate so new Gemma face each other, we should not remember any previous attack roll
    DM.atkroll = 0
    DM.defroll = 0
    DM.atkbonus = 0
    DM.defbonus = 0
    DM.typemod = 0

    DM.duelists[0].gotrigger = False
    DM.duelists[1].gotrigger = False
    
    frontAlive = False #Just to get the loop going
    while not frontAlive:
        temp1 = DM.duelists[owner].g1
        temp2 = DM.duelists[owner].g2 
        temp3 = DM.duelists[owner].g3
        
        DM.duelists[owner].g1 = temp2 
        DM.duelists[owner].g2 = temp3 
        DM.duelists[owner].g3 = temp1 
        frontAlive = DM.duelists[owner].g1.alive
    
    #Restore guard for front Gemma
    DM.duelists[owner].g1.guard = DM.duelists[owner].g1.maxguard

    disc = DM.duelists[owner].duelistname + '\'s new team order:\n'
    gem = DM.duelists[owner].g1
    disc += '**' + gem.name + '** - '
    if gem.hp <= 0: disc += ':skull:'
    else:
        for i in range(0, gem.hp): disc += ':heart:'
        for i in range(0, gem.maxhp - gem.hp): disc += ':black_heart:'
        for i in range(0, gem.guard): disc += ':shield:'
    disc += ' The ' + TypeList[DM.duelists[owner].g1.type1] + '/' + TypeList[DM.duelists[owner].g1.type2]
    ctype = gem.ctype
    if ctype != '':
        disc += ' [' + ctype + ']'
    disc += ' Gemma'

    gem = DM.duelists[owner].g2
    if gem.id != 'NULL':
        disc += '\n\n**' + gem.name + '** - '
        if gem.hp <= 0: disc += ':skull:'
        else:
            for i in range(0, gem.hp): disc += ':heart:'
            for i in range(0, gem.maxhp - gem.hp): disc += ':black_heart:'
            for i in range(0, gem.guard): disc += ':shield:'
    
    gem = DM.duelists[owner].g3
    if gem.id != 'NULL':
        disc += '\n**' + gem.name + '** - '
        if gem.hp <= 0: disc += ':skull:'
        else:
            for i in range(0, gem.hp): disc += ':heart:'
            for i in range(0, gem.maxhp - gem.hp): disc += ':black_heart:'
            for i in range(0, gem.guard): disc += ':shield:'

    if v1 != '-1':
        disc += '\n\n' + v1
    if v2 != '-1':
        disc += '\n\n' + v2
    
    return disc


#Award XP for surviving an attack, using an ability, or taking down an enemy Gemma
#check tells us if it's trying to award XP for surviving, using ability, or a takedown
#gem.check has information on what you've already been awarded
def awardXP(DM, duelistsIndex, check, Level, eLevel):
    gem = DM.duelists[duelistsIndex].g1
    if check == 1 and (gem.check != 1 and gem.check != 3) and gem.level < 10: #Survive
        if gem.check == 2:
            gem.check = 3
        else:
            gem.check = 1
        bonus = 5*(eLevel/Level) + (gem.mood + gem.AP)*gem.level/2
        gem.exp += round(5 + bonus)
        #print('awarded ' + str(round(5+bonus)) + ' to ' + gem.name + ' for surviving')
        #print('gem ap: ' + str(gem.AP) + ' gem mood: ' + str(gem.mood))

    elif check == 2 and (gem.check != 2 and gem.check != 3) and gem.level < 10:#Ability
        if gem.check == 1:
            gem.check = 3
        else:
            gem.check = 2
        bonus = 3*(eLevel/Level) + (gem.mood + gem.AP)*gem.level/2
        gem.exp += round(5 + bonus)
        #print('awarded ' + str(round(5+bonus)) + ' to ' + gem.name + ' for ability')
        #print('gem ap: ' + str(gem.AP) + ' gem mood: ' + str(gem.mood))

    elif check == 4 and gem.level < 10: #Takedown
        bonus = 10*(eLevel/Level) + (gem.mood + gem.AP)*gem.level/2
        gem.exp += round(20 + bonus)
        #print('awarded ' + str(round(20+bonus)) + ' to ' + gem.name + ' for takedown')
        #print('gem ap: ' + str(gem.AP) + ' gem mood: ' + str(gem.mood))


def soulink_check(DM, gemid, atkpower):
    #I should send the gem.id of the afflicted Gemma to check if they have it active
    slink = '-1'
    #We loop through this one since abilityList may get shorter when abilities trigger and remove themselves.
    #This deep copy will be static throughout the loop.
    loopabilityList = copy.copy(DM.abilityList)
    d0 = DM.duelists[0]
    d1 = DM.duelists[1]

    for i in range(0, len(loopabilityList)): 
        if loopabilityList[i][0] == 42:
            gem = -1
            gem2 = -1
            if d0.g1.id == gemid: 
                gem = d0.g1
                gem2 = d0.g2
            elif d0.g2.id == gemid: 
                gem = d0.g2
                gem2 = d0.g3
            elif d0.g3.id == gemid: 
                gem = d0.g3
                gem2 = d0.g1
            elif d1.g1.id == gemid: 
                gem = d1.g1
                gem2 = d1.g2
            elif d1.g2.id == gemid: 
                gem = d1.g2
                gem2 = d1.g3
            elif d1.g3.id == gemid: 
                gem = d1.g3
                gem2 = d1.g1
            
            if loopabilityList[i][1] == gem.id:
                DM.abilityList.remove(loopabilityList[i])
                if gem2.alive:
                    gem.hp += atkpower
                    gem2.hp -= atkpower
                    if gem2.hp <= 0: 
                        gem2.alive = False
                        slink = '**>>** *Soul Link* triggers and ' + gem2.name \
                            + ' takes the damage instead. ' + gem2.name + ' :skull: **faints!**'
                    else:
                        slink = '**>>** *Soul Link* triggers and ' + gem2.name \
                            + ' takes the damage instead. '
                    if gem.hp > 0:
                        gem.alive = True
    return slink


############################################################################################################
############################################################################################################
############################################################################################################


#   OUT OF DUEL USER COMMANDS


############################################################################################################
############################################################################################################
############################################################################################################

@bot.command(pass_context = True)
async def help(ctx):
    if not gamepause:
        sp = '\u200B \u200B \u200B \u200B \u200B \u200B \u200B'
        t1 = '\n``!help``' + sp + 'View the command list' \
            + '\n``!start``' + sp + 'Get your starting Gemma and pick your duelist name\n' + sp \
            
        t2 = '\n``!challenge <duelist name>``' + sp + 'Challenge another duelist to a duel' \
            + '\n``!challengenpc <duelist name>``' + sp + 'Challenge an NPC duelist to a duel' \
            + '\n``!go``' + sp + 'Proceed to the next phase in a duel' \
            + '\n``!rotate``' + sp + 'Rotate to your next Gemma' \
            + '\n``!attack``' + sp + 'Perform a regular attack' \
            + '\n``!hattack``' + sp + 'Perform a heavy attack' \
            + '\n``!ab1``' + sp + 'Use ability 1' \
            + '\n``!ab2``' + sp + 'Use ability 2' \
            + '\n``!cancel``' + sp + 'Cancel the current duel\n' + sp

        t3 = '\n``!team``' + sp + 'Show your team and duelist information' \
            + '\n``!switch <Gemma 1 slot number> <Gemma 2 slot number>``' + sp + 'Switch the team positions of two Gemma' \
            + '\n``!bc``' + sp + 'Show the Gemma in your Bracelet Computer (BC) and in your team' \
            + '\n``!bcw <Gemma slot number>``' + sp + 'Withdraw the selected Gemma from the BC' \
            + '\n``!bcd <Gemma slot number>``' + sp + 'Deposit the selected Gemma to the BC' \
            + '\n``!bcs <Gemma slot number>``' + sp + 'Show the selected Gemma in your BC or in your team' \
            + '\n``!pet <Gemma name or Gemma slot number>``' + sp + 'Pet the selected Gemma' \
            + '\n``!renamegemma <Gemma slot number>``' + sp + 'Rename the selected Gemma.' \
            + '\n``!upgrade``' + sp + 'Apply level-up upgrades to Gemma in your team' \
            + '\n``!fuse <Gemma 1 slot number> <Gemma 2 slot number>``' + sp + 'Fuse two Gemma for 5 tokens\n' + sp

        t4 ='\n``!buycapsule``' + sp + 'Buy a new Gemma for 3 tokens' \
            + '\n``!givetokento <duelist name>``' + sp + 'Give one of your tokens to another duelist' \
            + '\n``!trade <Gemma slot number> <duelist name>``' + sp + 'Trade the selected Gemma with another duelist, in return for one of their Gemma.' \
            '\n``!canceltrade``' + sp + 'Cancel the current trade\n' + sp

        t5 = '\nGangs commands can not be used in DM\'s with the bot' \
            + '\n``!gangs``' + sp + 'Show all gangs' \
            + '\n``!join <gang name or ID>``' + sp + 'Join a gang' \
            + '\n``!leave``' + sp + 'Leave current gang' \
            + '\n``!badges``' + sp + 'Show all your badges\n' + sp
            
        t6 = '\n``!lb``' + sp + 'Show the star leaderboard' \
            + '\n``!gangstar``' + sp + 'Show the gang star leaderboard' \
            + '\n``!list``' + sp + 'List all duelists\n' + sp
        
        t7 = '\n``!save``' + sp + 'Save all' \
            + '\n``!load``' + sp + 'Load all' \
            + '\n``!purge <duelist name>``' + sp + 'Delete duelist' \
            + '\n``!purgeall``' + sp + 'Delete all duelists' \
            + '\n``!renameduelist``' + sp + 'Rename a duelist' \
            + '\n``!addadmin <duelist name>``' + sp + 'Add user to admin list' \
            + '\n``!listadmin``' + sp + 'Show admin list' \
            + '\n``!removeadmin <duelist name>``' + sp + 'Remove user from admin list' \
            + '\n``!bigleaderboard``' + sp + 'Show the 16 top star holders' \
            + '\n``!stats``' + sp + 'Show stats' \
            + '\n``!pause``' + sp + 'Pause all player commands' \
            + '\n``!shutdown``' + sp + 'Notify players in a command' \
            + '\n``!lv <duelist name>``' + sp + 'Attempt to level up all Gemma in a team' \
            + '\n``!quitall``' + sp + 'Kill the bot'
        
        embed = discord.Embed(
            title = '**Command list**',
            description = '~ ~ ~ ~ ~',
            color = discord.Colour.gold()
        )
        embed.add_field(name='Get started:', value = t1, inline = False)
        embed.add_field(name='Dueling:', value = t2, inline = True)
        embed.add_field(name='Team management:', value = t3, inline = False)
        embed.add_field(name='Buying and trading:', value = t4, inline = True)
        embed.add_field(name='Gangs:', value = t5, inline = False)
        embed.add_field(name='Lists and Leaderboards:', value = t6, inline = True)
        embed.add_field(name='Misc', value = '``!unstuck``' + sp + 'If the bot has crashed you can free yourself if you are stuck in a command.')
        
        if ctx.message.author.id in AdminList:
            embed.add_field(name='Admin commands:', value = t7, inline = False)
        
        await bot.whisper(embed=embed)
        
@bot.command(pass_context = True)
async def team(ctx):
    userid = ctx.message.author.id
    index = findTeam(userid)
    if not gamepause:
        if index == -1:
            await bot.whisper('You do not have a team yet, create one with ``!start``.')
        else:
            duelindex = memfindDueltag(TeamList[index].dueltag)
            if duelindex == -1: #Normal team
                duelist = TeamList[index]
            else: #Team but from duelmemory
                DM = DuelmemList[duelindex]
                owner = memfindTeam(userid, TeamList[index].dueltag)[0]
                duelist = DM.duelists[owner]
            
            if duelist.opponent == '-1':
                opponent = 'None'
            else:
                opponent = duelist.opponent
            w = '**------- ' + duelist.duelistname + '\'s team -------**\n'
            w += 'Opponent: ' + opponent + '\nTokens: **' + str(duelist.tokens) + '**\t'
            w += 'Wins: **' + str(duelist.wincount) + '**\tLosses: **' + str(duelist.losecount) + '**\t'
            w += ' Stars: :star:**' + str(duelist.star) + '**\n'
            e4 = 'None'
            if duelist.userid in E4[5]: e4 = ':medal:'
            w += 'Hall of Fame: ' + e4 + '\n'
            w += 'Badges: '
            
            v = ''
            for i, badge in enumerate(duelist.badge):
                if badge == 1: #Basic badge
                    v += ' ' + BadgeDict[i]
                elif badge == 2: #Elite badge
                    v += ' ' + EbadgeDict[i]
                elif badge == 3: #Basic and Elite badge
                    v += ' ' + BadgeDict[i] + ' ' + EbadgeDict[i]
            if v == '':
                w += 'None'
            else:
                w += v + '\n'
            await bot.whisper(w)

            temp = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
            for i in range(0, 3):
                gem = getGem(duelist, i+1)
                if gem.id != 'NULL':
                    title, disc, ab1, ab2, pas = prepareEmbed(gem)
                    temp[i] = [title, disc, ab1, ab2, pas]

            if temp[0] != [0, 0, 0, 0, 0]:
                embed = makeEmbed(temp[0][0], temp[0][1], temp[0][2], temp[0][3], temp[0][4])
                await bot.whisper(embed=embed)

            if temp[1] != [0, 0, 0, 0, 0]:
                embed = makeEmbed(temp[1][0], temp[1][1], temp[1][2], temp[1][3], temp[1][4])
                await bot.whisper(embed=embed)

            if temp[2] != [0, 0, 0, 0, 0]:
                embed = makeEmbed(temp[2][0], temp[2][1], temp[2][2], temp[2][3], temp[2][4])
                await bot.whisper(embed=embed)


@bot.command(pass_context = True)
async def upgrade(ctx):
    #gem.levelup
    #1  pick 2nd ability at lv3         TG[i].ability[0] = random.randint(0, 71) #There are 72 abilities 
                                        #TG[i].ability[1] = 1
    #2  pick secondary type at lv7
    #3  pick 2nd ability and sec type
    #4  pick new ability at lv 10
    #5  pick sec type and new ability
    #6  pick 2nd ability, sec type and new ability
    user = ctx.message.author
    userid = ctx.message.author.id
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    
    #Loop through the team, if anyone has gem.levelup != 0 they get treated.
    #Loop until no one else found
    #while(found):
    #   found = False
    #   if do stuff
    #       found = True

    if not gamepause:
        if not tagged:
            duelindex = memfindDueltag(TeamList[index].dueltag)
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif duelindex != -1:
                await bot.whisper('You cannot upgrade while you are in a duel.')
            else:
                nothing = True
                global TagList
                TagList.append([user, '``!upgrade``'])        
                for i in range(1, 4):
                    gem = getGem(TeamList[index], i)
                    if gem != -1:
                        if gem.levelup != 0:
                            nothing = False
                            falsealarm = True
                            c = True
                            while c:
                                if gem.levelup == 6 or gem.levelup == 3 or gem.levelup == 1:
                                    falsealarm = False
                                    await bot.whisper('**Level 3 Upgrade detected** for **' + gem.name + '**')

                                    r1, r2, r3 = random.sample(range(0, 71), 3)
                                    while r1 == gem.ability[0] or r2 == gem.ability[0] or r3 == gem.ability[0] or r1 == r2 or r2 == r3 or r1 == r3:
                                        r1, r2, r3 = random.sample(range(0, 71), 3)
                                    await bot.whisper('Enter the number of the ability you want **' + gem.name + '** to learn:\n**1:** ' \
                                        + abilityDict(r1, gem.level) + '\n**2:** ' + abilityDict(r2, gem.level) + '\n**3:** ' + abilityDict(r3, gem.level))
                                    q = True
                                    while q:
                                        try:
                                            q = False
                                            ans = await bot.wait_for_message(author = user)
                                            ans = int(ans.content)
                                            if ans < 1 or ans > 3:
                                                await bot.whisper('Please enter the numbers 1, 2 or 3.')
                                                q = True
                                            else:
                                                if ans == 1: gem.ability[2] = r1
                                                elif ans == 2: gem.ability[2] = r2
                                                else: gem.ability[2] = r3
                                                await bot.whisper('Upgrade registered.')
                                        except ValueError:
                                            await bot.whisper('Please enter the numbers 1, 2 or 3.')
                                            q = True 

                                    if gem.levelup == 6: gem.levelup = 5
                                    elif gem.levelup == 3: gem.levelup = 2
                                    else: gem.levelup = 0

                                if gem.levelup == 5 or gem.levelup == 2: #We should never see gem.levelup == 6, always resolved above first
                                    falsealarm = False
                                    await bot.whisper('**Level 7 Upgrade detected** for **' + gem.name + '**') 

                                    r1, r2 = random.sample(range(0, 13), 2)
                                    while r1 == gem.type2 or r2 == gem.type2 or r1 == gem.type1 or r2 == gem.type1 or r1 == r2:
                                        r1 = random.randint(0, 13)
                                        r2 = random.randint(0, 13)
                                    await bot.whisper('Enter the number of the type you want **' + gem.name + '** to adapt, this replaces their current ' \
                                        + 'secondary type: ' + TypeList[gem.type2] + '\n**1:** ' \
                                        + TypeList[r1] + '\n**2:** ' + TypeList[r2] + '\n**3:** Cancel and keep the current type')

                                    q = True
                                    while q:
                                        try:
                                            q = False
                                            ans = await bot.wait_for_message(author = user)
                                            ans = int(ans.content)
                                            if ans < 1 or ans > 3:
                                                await bot.whisper('Please enter the numbers 1, 2 or 3.')
                                                q = True
                                            else:
                                                if ans == 1: 
                                                    gem.type2 = r1

                                                    gem.ctype = CompChart[gem.type1, gem.type2]                                                       
                                                    if gem.ctype != '':
                                                        gem.passive[0] = CompDict[gem.ctype]
                                                        if gem.ctype == 'Mystic':
                                                            gem.ability[1] = 2
                                                            gem.ability[3] = 2
                                                        elif gem.ctype == 'Slime':
                                                            gem.maxhp += 1
                                                            gem.hp += 1
                                                            gem.maxguard -= 1
                                                            gem.guard -= 1
                                                        elif gem.ctype == 'Golem':
                                                            gem.guard += 1
                                                            gem.maxguard += 1
                                                        elif gem.ctype != 'Mystic':
                                                            #If we switch from mystic to another ctype we must reset ability uses to 1
                                                            gem.ability[1] = 1
                                                            gem.ability[3] = 1

                                                    await bot.whisper('Upgrade registered.')
                                                elif ans == 2: 
                                                    gem.type2 = r2

                                                    gem.ctype = CompChart[gem.type1, gem.type2]                                                       
                                                    if gem.ctype != '':
                                                        gem.passive[0] = CompDict[gem.ctype]
                                                        if gem.ctype == 'Mystic':
                                                            gem.ability[1] = 2
                                                            gem.ability[3] = 2
                                                        elif gem.ctype == 'Slime':
                                                            gem.maxhp += 1
                                                            gem.hp += 1
                                                            gem.maxguard -= 1
                                                            gem.guard -= 1
                                                        elif gem.ctype == 'Golem':
                                                            gem.guard += 1
                                                            gem.maxguard += 1
                                                        elif gem.ctype != 'Mystic':
                                                            #If we switch from mystic to another ctype we must reset ability uses to 1
                                                            gem.ability[1] = 1
                                                            gem.ability[3] = 1

                                                    await bot.whisper('Upgrade registered.')
                                                else:
                                                    await bot.whisper('Upgrade declined.')
                                        except ValueError:
                                            await bot.whisper('Please enter the numbers 1, 2 or 3.')
                                            q = True 
                                    
                                    if gem.levelup == 5: gem.levelup = 4
                                    elif gem.levelup == 2: gem.levelup = 0
                                
                                if gem.levelup == 4: #We should never see gem.levelup == 6 or == 5, always resolved above first
                                    falsealarm = False
                                    await bot.whisper('**Level 10 Upgrade detected** for **' + gem.name + '**')

                                    r1, r2, r3 = random.sample(range(0, 71), 3)
                                    while r1 == gem.ability[0] or r2 == gem.ability[0] or r3 == gem.ability[0] or r1 == r2 or r2 == r3 or r1 == r3:
                                        r1, r2, r3 = random.sample(range(0, 71), 3)
                                    
                                    w = 'Enter a letter for the ability you want **' + gem.name + '** to learn, followed ' \
                                        + 'by the number of the ability you want to replace (for example: \'A 2\' to replace ablity 2 with ability A):'
                                    w +='\n**A:** ' + abilityDict(r1, gem.level) + '\n**B:** ' + abilityDict(r2, gem.level) + '\n**C:** ' + abilityDict(r3, gem.level)
                                    w += '\n\n**Current abilities:** \n**1:** ' + abilityDict(gem.ability[0], gem.level) + '\n**2:** ' + abilityDict(gem.ability[2], gem.level)
                                    w += '\n**3:** Cancel and keep the current abilities'
                                    await bot.whisper(w)
                                    q = True
                                    while q:
                                        try:
                                            q = False
                                            ans = await bot.wait_for_message(author = user)
                                            ans = ans.content
                                            if ans == '3':
                                                await bot.whisper('Update declined.')
                                            else:
                                                ans = ans.split()
                                                let = ans[0]
                                                num = ans[1]
                                                if num == '1':
                                                    if let == 'A' or let == 'a': 
                                                        gem.ability[0] = r1
                                                        await bot.whisper('Update registered')
                                                    elif let == 'B' or let == 'b': 
                                                        gem.ability[0] = r2
                                                        await bot.whisper('Update registered')
                                                    elif let == 'C' or let == 'c': 
                                                        gem.ability[0] = r3
                                                        await bot.whisper('Update registered')
                                                    else:
                                                        await bot.whisper('Please choose between abilities A, B and C to replace ability 1 or 2.')
                                                        q = True
                                                elif num == '2':
                                                    if let == 'A' or let == 'a': 
                                                        gem.ability[2] = r1
                                                        await bot.whisper('Update registered')
                                                    elif let == 'B' or let == 'b': 
                                                        gem.ability[2] = r2
                                                        await bot.whisper('Update registered')
                                                    elif let == 'C' or let == 'c': 
                                                        gem.ability[2] = r3
                                                        await bot.whisper('Update registered')
                                                    else:
                                                        await bot.whisper('Please choose between abilities A, B and C to replace ability 1 or 2.')
                                                        q = True
                                                #elif num == '3':
                                                #    await bot.whisper('Update declined.')
                                                else:
                                                    await bot.whisper('Please choose between abilities A, B and C to replace ability 1 or 2.')
                                                    q = True
                                        except IndexError:
                                            await bot.whisper('Invalid input. The input has to be on the format \'LETTER NUMBER\'')
                                            q = True

                                    gem.levelup = 0
                                if falsealarm or gem.levelup == 0:
                                    c = False

                removeFromTagList(user, '``!upgrade``')
                savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)     
                if nothing:
                    await bot.whisper('None of the Gemma in your team have an available upgrade.')
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

@bot.command(pass_context = True)
async def start(ctx):
        print('Starting start command')
        user = ctx.message.author
        userid = user.id
        index = findTeam(userid)
        tagged, tagcommand = findTag(user)
        print('Checked some stuff, index: ', index)
        if not gamepause:
            if ctx.message.channel.is_private:
                await bot.whisper('This command needs to be initiated on the Jaegergems server.')
            elif index != -1:
                await bot.whisper('You already have a team.')
            elif not tagged:
                print('We are good to go!')
                play = False
                message = 'Welcome to Jaegergems 3! Before we you get started, please be aware that this game contains random rewards'\
                    + ' (Gemma) that you purchase with in game currency. The game does not involve real money in any way shape or'\
                    + ' form, but if you suffer from gambling problems please reconsider and seek help.\n\nStart the game by typing'\
                    + ' "y" for yes and anything else for no.'
                embed = discord.Embed(
                    title = '**Jaegergems 3**',
                    description = message,
                    color = discord.Colour.gold()
                )
                await bot.whisper(embed=embed)

                ans = await bot.wait_for_message(author = user)
                if ans.content == 'Y' or ans.content == 'y':
                    play = True
                else:
                    await bot.whisper('Team generation cancelled.')
                if play:
                    global TagList
                    TagList.append([user, '``!start``'])

                    team = Duelist() #The Duelist object for the new user

                    #Generate 14 Gemma, one of each type.
                    TG = [Gemma(), Gemma(), Gemma(), Gemma(), Gemma(), Gemma(), Gemma(), Gemma(), Gemma(), Gemma(), Gemma(), Gemma(), Gemma(), Gemma()]
                    #Generate secondary types for each of them
                    for i in range(0, 14):
                        TG[i].type1 = i
                        TG[i].type2 = random.randint(0, 13)
                        while TG[i].type1 == TG[i].type2:    
                            TG[i].type2 = random.randint(0, 13)

                        TG[i].ctype = CompChart[TG[i].type1, TG[i].type2]
                        
                        if TG[i].ctype != '':
                            TG[i].passive[0] = CompDict[TG[i].ctype]
                            if TG[i].ctype == 'Mystic':
                                TG[i].ability[1] = 2
                                TG[i].ability[3] = 2
                            elif TG[i].ctype == 'Slime':
                                TG[i].maxhp += 1
                                TG[i].hp += 1
                                TG[i].maxguard -= 1
                                TG[i].guard -= 1
                            elif TG[i].ctype == 'Golem':
                                TG[i].guard += 1
                                TG[i].maxguard += 1
                    
                    #Present the capsules
                    w = '**Pick 3 out of the 14 capsules by entering one number at a time:\n**' \
                        + '1: Walnut\t 8: Indigo\n' \
                        + '2: Gold\t 9: Pearl\n' \
                        + '3: Iron\t 10: Ebony\n' \
                        + '4: Lime\t 11: Mint\n' \
                        + '5: Plum\t 12: Chestnut\n' \
                        + '6: Cinnamon\t 13: Azure\n' \
                        + '7: Cobalt\t 14: Scarlet'
                    await bot.whisper(w)

                    #The user picks capsules
                    picks = []
                    c = 0
                    while c < 3:
                        try:
                            ans = await bot.wait_for_message(author = user)
                            ans = int(ans.content)
                            if (ans-1) in picks:
                                await bot.whisper('You cannot pick the same capsule twice!')
                            elif ans < 1 or ans > 14:
                                await bot.whisper('Please enter a number between 1 and 14')
                            else:
                                picks.append(ans-1)
                                await bot.whisper(ColorDict[TG[ans-1].type1] + ' capsule picked!')
                                c += 1 #We only count the pick if we avoided a ValueError in int(ans.content)
                        except ValueError:
                            await bot.whisper('Please enter a number between 1 and 14')
                    TG = [TG[picks[0]], TG[picks[1]], TG[picks[2]]]

                    #Generating stats and abilities, then presenting the 3 choices
                    await bot.whisper('**Pick your starter Gemma by entering its corresponding number:**')
                    for i in range(0, 3):
                        points = 4 #The total dice size will be 10, but dice are +2 over stats. Stat 0 means d2, stat 1 means d3, etc.
                        stat = [-1, -1, -1]
                        stat[0] = random.randint(0, points)
                        points -= stat[0]
                        stat[1] = random.randint(0, points)
                        stat[2] = 4 - stat[0] - stat[1]
                        TG[i].attack = stat.pop(random.randint(0, len(stat)-1))
                        TG[i].defence = stat.pop(random.randint(0, len(stat)-1))
                        TG[i].speed = stat[0]

                        TG[i].ability[0] = random.randint(0, 71) #There are 72 abilities 

                        TG[i].personality = random.randint(0, 8)
                        TG[i].name = 'Gemma no. ' + str(i+1)
                        
                        title, disc, ab1, ab2, pas = prepareEmbed(TG[i])
                        embed = makeEmbed(title, disc, ab1, ab2, pas)
                        await bot.whisper(embed=embed)
                        await asyncio.sleep(0.1)

                    c = 1
                    while c == 1:
                        try:
                            ans = await bot.wait_for_message(author = user)
                            ans = int(ans.content)
                            if ans > 0 and ans < 4:
                                c = 0
                                team.g1 = TG[ans-1]
                            else:
                                await bot.whisper('Please enter a number between 1 and 3')
                        except ValueError:
                            await bot.whisper('Please enter a number between 1 and 3')
                    
                    #Name Gemma
                    c = True
                    while c:
                        c = False
                        await bot.whisper('Give it a name:')
                        ans = await bot.wait_for_message(author = user)
                        ans = ans.content
                        for x in ans:
                            if ord(x) > 127:
                                await bot.whisper('Please only use ASCII symbols')
                                c = True
                        if len(ans) > 30:
                            await bot.whisper('You cannot have names with over 30 characters')
                            c = True    
                        elif ans == '-':
                            await bot.whisper('You cannot name your Gemma that.')            
                            c = True
                    team.g1.name = ans

                    #duelistname
                    c = True
                    while c:
                        await bot.whisper('Choose your duelist name:')
                        name = await bot.wait_for_message(author = user)
                        index = findName(name.content)
                        for x in name.content:
                            if ord(x) > 127:
                                await bot.whisper('Please only use ASCII symbols')
                                break
                        if index != -1 or name == '-1':
                            await bot.whisper('This name is already taken.')
                        elif len(name.content) > 30:
                            await bot.whisper('You cannot have names with over 30 characters.')
                        else:
                            await bot.whisper('Are you happy with this name? Type "y" for yes and anything else for no: ')
                            ans = await bot.wait_for_message(author = user)
                            if ans.content == 'Y' or ans.content == 'y':
                                team.duelistname = name.content
                                c = False
                    
                    global maxGID
                    maxGID += 1
                    team.g1.id = maxGID

                    team.g1.alive = True
                    team.userid = userid
                    team.user = user
                    team.discname = user
                    
                    #Remove user from TagList
                    removeFromTagList(user, '``!start``')
                    TeamList.append(team)
                    await bot.whisper('Your team is complete and you are ready to duel! Find all commands with ``!help``')

                    savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)

            elif tagged:
                await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')


@bot.command(pass_context = True)
async def leave(ctx): #leave current gang
    user = ctx.message.author
    userid = ctx.message.author.id
    index = findTeam(userid)
    
    if not gamepause:
        if ctx.message.channel.is_private:
            await bot.whisper('This command needs to be initiated on the Jaegergems server.')
        else:
            for role in user.roles:
                for gang in RoleList:
                    if role.id == gang:
                        await bot.say('You have left the Gang: **' + role.name + '**')
                        await bot.remove_roles(user, role)

@bot.command(pass_context = True)
async def join(ctx, *, w = ''): #Join a new gang, and leave the gang you are currently in
    user = ctx.message.author
    userid = ctx.message.author.id
    index = findTeam(userid)
    
    if not gamepause:
        if ctx.message.channel.is_private:
            await bot.whisper('This command needs to be initiated on the Jaegergems server.')
        else:
            r = get(user.server.roles, name = w) #Get role object, None if there is no role with that name on the server.
            if w == '':
                await bot.say('Please specify which Gang you want to join in the command: ``!join <gang name or ID>``')
            elif r in user.roles:
                await bot.say('You are already in that gang')
            elif r != None:
                for role in user.roles:
                    for gang in RoleList:
                        if role.id == gang:
                            await bot.say('You have left the Gang: **' + role.name + '**')
                            await bot.remove_roles(user, role)
                            await asyncio.sleep(0.5)

                await bot.add_roles(user, r)
                await bot.say('You have joined the Gang: **' + r.name + '**')
                TeamList[index].user = user #Update user object with new roles.
                
            else:
                await bot.say('I can\'t find a Gang with that name.')

@bot.command(pass_context = True)
async def gangs(ctx): #View all gangs you can join
    if not gamepause:
        user = ctx.message.author
        w = '**Gang name\t\tGang ID**'
        for gangid in RoleList:
            r = get(user.server.roles, id = gangid)
            if r != None:
                w += '\n' + r.name + '\t\t' + gangid
        await bot.say(w)

@bot.command(pass_context = True)
async def gangstar(ctx): #View all gangs stars
    if not gamepause:
        glist = np.zeros(len(RoleList), dtype=int)
        for team in TeamList:
                if not team.bot:
                    roles = team.user.roles
                    for gangid in RoleList:
                        for role in roles:
                            if gangid == role.id:
                                gindex = getGangIndex(role)
                                glist[gindex] += team.star

        user = ctx.message.author
        sp = '\u200B \u200B \u200B \u200B \u200B \u200B \u200B'
        w = '**Gang name**' + sp + '**Total stars**'
        for i, gangid in enumerate(RoleList):
            r = get(user.server.roles, id = gangid)
            if r != None:
                w += '\n' + r.name + sp + sp + ':star:' + str(glist[i])
        
        embed = discord.Embed(
            title = '**Gang Stars**',
            description = w,
            color = discord.Colour.gold()
        )
        await bot.say(embed=embed)



@bot.command(pass_context = True)
async def badges(ctx):
    userid = ctx.message.author.id
    index = findTeam(userid)
    if not gamepause:
        if index == -1:
            await bot.whisper('You do not have a team yet, create one with ``!start``.')
        else:
            w = ''
            for i, badge in enumerate(TeamList[index].badge):
                if badge == 1: #Basic badge
                    w += ' ' + BadgeDict[i]
                elif badge == 2: #Elite badge
                    w += ' ' + EbadgeDict[i]
                elif badge == 3: #Basic and Elite badge
                    w += ' ' + BadgeDict[i] + ' ' + EbadgeDict[i]
            if w == '':
                await bot.say('You have no badges yet.')
            else:
                await bot.say('Badges: ' + w)

@bot.command(pass_context = True)
async def givetokento(ctx, *, enemy = ''):
    userid = ctx.message.author.id
    user = ctx.message.author
    index = findTeam(userid)
    eindex = findName(enemy)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif index == eindex:
                await bot.whisper('You cannot give tokens to yourself!')
            elif enemy == '':
                await bot.whisper('Please specify the target player in the command: ``!givetokento <duelist name>``')
            elif eindex == -1:
                await bot.whisper(enemy + ' does not have a team yet.')
            elif TeamList[index].tokens == 0:
                await bot.whisper('You have no tokens to give.')
            else:
                global TagList
                TagList.append([user, '``!givetokento``'])
                await bot.say('How many tokens? ')
                ans = await bot.wait_for_message(author = user)
                try:
                    ans = int(ans.content)
                    if ans < 0:
                        await bot.whisper('Please enter a positive number next time.')
                    elif ans <= TeamList[index].tokens:
                        TeamList[index].tokens = TeamList[index].tokens - ans
                        TeamList[eindex].tokens = TeamList[eindex].tokens + ans
                        await bot.say(TeamList[index].duelistname + ' has given ' + str(ans) + ' tokens to ' + enemy)
                        
                        #Remove user from TagList
                        removeFromTagList(user, '``!givetokento``')
                        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
                    else:
                        await bot.say('You don\'t have that many tokens')
                except ValueError:
                    await bot.whisper('Please enter a number next time.')

        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

@bot.command(pass_context = True)
async def canceltrade(ctx):
    userid = ctx.message.author.id
    user = ctx.message.author
    index = findTeam(userid)
    eindex = findName(TeamList[index].tradepartner)
    
    if not gamepause:
        if index == -1:
            await bot.whisper('You do not have a team yet, create one with ``!start``.')
        elif TeamList[index].tradepartner != '-1':
            global TagList
            if TeamList[eindex].tradepartner == TeamList[index].duelistname: #You are their tradepartner
                await bot.say('**Trade cancelled**')               
                TeamList[index].tradepartner = '-1'
                TeamList[index].tradeuser = '-1'
                TeamList[index].tradeslot = -1
                TeamList[eindex].tradepartner = '-1'
                TeamList[eindex].tradeuser = '-1'
                TeamList[eindex].tradeslot = -1

                #Remove user from TagList
                removeFromTagList(user, '``!trade``')
                #Remove user from TagList
                removeFromTagList(TeamList[eindex].user, '``!trade``')
                
            else: #You are not their trade partner, they haven't replied yet, but you still cancel.
                await bot.say('**Trade cancelled**')               
                TeamList[index].tradepartner = '-1'
                TeamList[index].tradeuser = '-1'
                TeamList[index].tradeslot = -1
                #Remove user from TagList
                removeFromTagList(user, '``!trade``')
            
@bot.command(pass_context = True)
async def trade(ctx, gemslot = '', *, partner = ''):
    userid = ctx.message.author.id
    user = ctx.message.author
    index = findTeam(userid)
    duelindex = memfindDueltag(TeamList[index].dueltag)
    eindex = findName(partner)
    
    if not gamepause:
        gemtime = True
        try:
            gemslot = int(gemslot)
        except ValueError:
            gemtime = False
        if gemtime:
            gem = getGem(TeamList[index], gemslot)
        else:
            gem = -1

        tagged, tagcommand = findTag(user)
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            else:
                if duelindex != -1:
                    await bot.say('You cannot trade Gemma while you are in a duel.')
                elif partner == '' or gemslot == '':
                    await bot.say('Pleace specify who you want to trade with in the command: ``!trade <Gemma slot number> <duelist name>``')
                elif index == eindex:
                    await bot.say('You cannot trade with yourself!')
                elif eindex == -1:
                    await bot.say(partner + ' does not have a team yet.')
                elif findName(TeamList[eindex].opponent) != -1:
                    await bot.say(partner + ' cannot trade when they are in a duel.')
                elif gem == -1:
                    await bot.whisper('Please specify team slot numbers from 1-6 in the command: ``!trade <Gemma slot number> <duelist name>``')
                elif gem.id == 'NULL':
                    await bot.whisper('You have to choose a team slots with Gemma in it.')
                else:
                    global TagList
                    TagList.append([user, '``!trade``'])

                    #PHASE have someone trade with you
                    if TeamList[eindex].tradepartner == TeamList[index].duelistname: #You are their tradepartner
                        partnergem = getGem(TeamList[eindex], TeamList[eindex].tradeslot)
                        await bot.say(TeamList[index].duelistname + ' offers to trade their **' + gem.name + '** for **' + partnergem.name + '**'
                            + '\nAccept by typing "y", decline by typing anything else.')
                        
                        ans1 = await bot.wait_for_message(author = user)
                        ans1 = ans1.content
                        ans2 = await bot.wait_for_message(author = TeamList[eindex].tradeuser)
                        ans2 = ans2.content
                        if (ans1 == 'y' or ans1 == 'Y') and (ans2 == 'y' or ans2 == 'Y'):
                            await bot.say('Both duelists have accepted the trade!\n**Trade complete**')
                            partnergem.AP = 0
                            gem.AP = 0
                            assignTeamSlot(TeamList[index], gemslot, partnergem)
                            assignTeamSlot(TeamList[eindex], TeamList[eindex].tradeslot, gem) 

                            savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)                       
                        else:
                            await bot.say('The trade was declined.\n**Trade cancelled**')
                        
                        TeamList[index].tradepartner = '-1'
                        TeamList[index].tradeuser = '-1'
                        TeamList[index].tradeslot = -1
                        TeamList[eindex].tradepartner = '-1'
                        TeamList[eindex].tradeuser = '-1'
                        TeamList[eindex].tradeslot = -1
                        #Remove user from TagList
                        removeFromTagList(TeamList[index].user, '``!trade``')
                        #Remove user from TagList
                        removeFromTagList(TeamList[eindex].user, '``!trade``')
                        
                    else:
                        TeamList[index].tradepartner = partner
                        TeamList[index].tradeuser = user
                        TeamList[index].tradeslot = gemslot
                        await bot.say(TeamList[index].duelistname + ' requests a trade their **' + gem.name + '** with ' + partner + 
                            '\n' + partner + ' can offer a Gemma to trade with a corresponding ``!trade <Gemma slot number> <duelist name>``'
                                + '\nCancel the trade with ``!canceltrade``')
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

@bot.command(pass_context = True)
async def switch(ctx, gemAslot = '', gemBslot = ''): #switch positions between two Gemma in your team
    userid = ctx.message.author.id
    user = ctx.message.author
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            else:
                try:
                    gemAslot = int(gemAslot)
                    gemBslot = int(gemBslot)
                except ValueError:
                    gemAslot = -1
                    gemBslot = -1
            
                gemA = getGem(TeamList[index], gemAslot)
                gemB = getGem(TeamList[index], gemBslot)
            
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex != -1:
                    await bot.whisper('You cannot switch Gemma positions in the middle of a duel.')
                elif gemAslot == -1 or gemBslot == -1:
                    await bot.whisper('Please specify two target Gemma from your active team in the command: ``!switch <Gemma 1 slot number> <Gemma 2 slot number>``')
                elif gemA == -1 or gemB == -1:
                    await bot.whisper('Please specify team slot numbers from 1-6 in the command: ``!switch <Gemma 1 slot number> <Gemma 2 slot number>``')
                else: 
                    assignTeamSlot(TeamList[index], gemAslot, gemB)
                    assignTeamSlot(TeamList[index], gemBslot, gemA)

                    await bot.say(TeamList[index].duelistname + '\'s new team order:')
                    await bot.say('``' + TeamList[index].g1.name + '``, ``' + TeamList[index].g2.name + '``, ``' + TeamList[index].g3.name + '``')
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

@bot.command(pass_context = True)
async def list(ctx):
    if not gamepause:    
        if not len(TeamList):
            await bot.whisper('There are no duelists yet')
        else:
            w = 'All duelists:\n__Duelist name__\t**|**\t__Discord name__\t**|**\t__Gang__'
            for team in TeamList:
                if not team.bot:
                    gangname = ''
                    roles = team.user.roles
                    for gangid in RoleList:
                        for role in roles:
                            if gangid == role.id:
                                gangname = role.name
                    
                    w += '\n' + team.duelistname + '\t**|**\t' + str(team.discname) + '\t**|**\t' + gangname
                    if len(w) > 1600:
                        await bot.whisper(w)
                        w = '-----\n'
            await bot.whisper(w)

@bot.command(pass_context = True)
async def renamegemma(ctx, gemslot = ''):
    user = ctx.message.author
    userid = ctx.message.author.id
    index = findTeam(userid)

    if not gamepause:    
        if index == -1:
            await bot.whisper('You do not have a team yet, create one with ``!start``.')
        elif gemslot == '':
            await bot.whisper('Please specify the target Gemma in the command: ``!renamegemma <Gemma slot number>``')
        else:
            try:
                gemslot = int(gemslot)
                if gemslot < 0 or gemslot > (3 + len(TeamList[index].PC)):
                    await bot.whisper('Please specify valid slot numbers in the command: ``!renamegemma <Gemma slot number>``')
                else:
                    if gemslot > 0 and gemslot < 4:
                        gem = getGem(TeamList[index], gemslot)
                    else:
                        gem = TeamList[index].PC[gemslot-4]    

                    if gem.id == 'NULL':
                        await bot.whisper('You cannot rename an empty slot.')
                        #We do not loop with c = True here. If someone had an empty team they'd be stuck.
                    else:
                        cc = True
                        while cc:
                            cc = False
                            await bot.whisper('Enter a new name: ')
                            ansname = await bot.wait_for_message(author = user)
                            for x in ansname.content:
                                if ord(x) > 127:
                                    await bot.whisper('Please only use ASCII symbols')
                                    cc = True
                            if len(ansname.content) > 30:
                                await bot.whisper('You cannot have names with over 30 characters')
                                cc = True
                        #We now have an accepted name
                        gem.name = ansname.content
                        await bot.whisper('Their new name is **' + ansname.content + '**')
                        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
            except ValueError:
                await bot.whisper('Please specify valid slot numbers in the command: ``!renamegemma <Gemma slot number>``')

@bot.command(pass_context = True)
async def buycapsule(ctx):
    user = ctx.message.author
    userid = user.id
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    yes = False

    if not gamepause:
        if index == -1:
            await bot.whisper('You do not have a team yet, create one with ``!start``.')
        elif TeamList[index].tokens < 3:
            await bot.whisper('You do not have enough tokens, a Gem capsule costs 3 tokens.')
        else:
            await bot.whisper('Are you sure you want to spend 3 tokens to purchase a Gem capsule?' + 
            ' Type "y" for yes and anything else for no.\n')
            ans = await bot.wait_for_message(author = user)
            if ans.content == 'y' or ans.content == 'Y':
                yes = True
                TeamList[index].tokens -= 3
        if yes and not tagged:
            global TagList
            TagList.append([user, '``!buycapsule``'])
            
            #Generating stats for colored capsules
            TG = [Gemma(), Gemma(), Gemma()]        
            for i in range(0, 3):
                TG[i].type1 = random.randint(0, 13)
                TG[i].type2 = random.randint(0, 13)
                while TG[i].type1 == TG[i].type2:    
                    TG[i].type2 = random.randint(0, 13)

                TG[i].ctype = CompChart[TG[i].type1, TG[i].type2]

                if TG[i].ctype != '':
                    TG[i].passive[0] = CompDict[TG[i].ctype]
                    if TG[i].ctype == 'Mystic':
                        TG[i].ability[1] = 2
                        TG[i].ability[3] = 2
                    elif TG[i].ctype == 'Slime':
                        TG[i].maxhp += 1
                        TG[i].hp += 1
                        TG[i].maxguard -= 1
                        TG[i].guard -= 1
                    elif TG[i].ctype == 'Golem':
                        TG[i].guard += 1
                        TG[i].maxguard += 1

            #Present colored capsules
            w = 'Pick one of the three capsules by entering a number between 1 and 3:'
            for i in range(0, 3):
                w += '\n**' + str(i+1) + ':** ' + ColorDict[TG[i].type1]
            await bot.whisper(w)

            #Pick colored capsules
            c = 1
            while c == 1:
                try:
                    ans = await bot.wait_for_message(author = user)
                    ans = int(ans.content)
                    if ans > 0 and ans < 4:
                        c = 0
                        TG = TG[ans-1]
                    else:
                        await bot.whisper('Please enter a number between 1 and 3')
                except ValueError:
                    await bot.whisper('Please enter a number between 1 and 3')
            
            #Generating stats and presenting Gemma
            points = 4
            stat = [-1, -1, -1]
            stat[0] = random.randint(0, points)
            points -= stat[0]
            stat[1] = random.randint(0, points)
            stat[2] = 4 - stat[0] - stat[1]
            TG.attack = stat.pop(random.randint(0, len(stat)-1))
            TG.defence = stat.pop(random.randint(0, len(stat)-1))
            TG.speed = stat[0]

            TG.ability[0] = random.randint(1, 71) #There are 72 abilities

            TG.personality = random.randint(0, 8)
            TG.name = 'New Gemma'

            await bot.whisper('**You got:**')
            title, disc, ab1, ab2, pas = prepareEmbed(TG)
            embed = makeEmbed(title, disc, ab1, ab2, pas)
            await bot.whisper(embed=embed)

            #Name Gemma
            c = True
            while c:
                c = False
                await bot.whisper('Give it a name:')
                ans = await bot.wait_for_message(author = user)
                ans = ans.content
                for x in ans:
                    if ord(x) > 127:
                        await bot.whisper('Please only use ASCII symbols')
                        c = True
                if len(ans) > 30:
                    await bot.whisper('You cannot have names with over 30 characters')
                    c = True
                elif ans == '-':
                    await bot.whisper('You cannot name your Gemma that.')
                    c = True
            TG.name = ans

            global maxGID
            maxGID += 1
            TG.id = maxGID
            TG.alive = True

            #Remove user from TagList
            removeFromTagList(user, '``!buycapsule``')
            
            #Put Gemma in PC
            TeamList[index].PC.append(TG)
            await bot.whisper('**' + TG.name + '** has been added to your Bracelet Computer (BC)!')

            savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
            
        elif tagged:#TO STOP Double buy:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

@bot.command(pass_context = True)
async def pet(ctx, *, gnum = ''):
    userid = ctx.message.author.id
    index = findTeam(userid)
    if not gamepause:
        if index == -1:
            await bot.whisper('You do not have a team yet, create one with ``!start``.')
        else:
            try:
                gnumber = int(gnum)
                gem = getGem(TeamList[index], gnumber)
            except ValueError:
                gem = getGemName(TeamList[index], gnum)
            if gem != -1:
                if gem.id != 'NULL':
                    #Determine mood:
                    MoodIndex = 1 #Neutral
                    if gem.mood < -2:
                        MoodIndex = 0 #Negative
                    elif gem.mood > 2:
                        MoodIndex = 2 #Positive
                        
                    if int(gem.AP/5) < 1:
                        await bot.say('*' + gem.name + PetList[gem.personality][1][MoodIndex] + '*')
                    if int(gem.AP/5) >= 1:
                        await bot.say('*' + gem.name + PetList[gem.personality][2][MoodIndex] + '*')
                    if int(gem.AP/5) >= 3:
                        await bot.say('*' + gem.name + PetList[gem.personality][3][MoodIndex] + '*')
                    
                    [tstamp, TimeListIndex] = findTimeList(TeamList[index].userid, gem.id)
                    nowtime = time.clock()+60
                    if abs(tstamp-nowtime) > 60:
                        
                        TimeList[TimeListIndex][2] = nowtime
                        #APImpact. MoodImpact
                        gem.AP += APImpact[gem.personality][3]
                        if gem.AP > 15: gem.AP = 15
                        elif gem.AP < 0: gem.AP = 0
                        gem.mood += MoodImpact[gem.personality][3]
                        if gem.mood > 6: gem.mood = 5
                        elif gem.mood < -6: gem.mood = -5


@bot.command(pass_context = True)
async def lb(ctx): #Show top 8 star holders.
    dummy = Duelist()
    dummy.duelistname = '-'
    dummy.discname = 'NULL'
    dummy.star = -1
    top = [dummy]*8
    
    if not gamepause:
        for i, duelist in enumerate(TeamList):
            if not duelist.bot:
                for k in range(0, 8):
                    if top[k].star <= duelist.star:
                        if k < 7:
                            for j in range(7, k-1, -1):
                                top[j] = top[j-1]
                        top[k] = duelist
                        break
        
        sp = '\u200B \u200B \u200B \u200B \u200B \u200B \u200B'
        w = '__Stars' + sp + 'Duelist__'
        for duelist in top:
            if duelist.discname != 'NULL':
                w += '\n:star:' + str(duelist.star) + sp + duelist.duelistname
        embed = discord.Embed(
            title = '**Top 8 Leaderboard**',
            description = w,
            color = discord.Colour.gold()
        )
        await bot.say(embed=embed)


############################################################################################################
############################################################################################################
############################################################################################################


#   OUT OF DUEL USER COMMANDS - BC


############################################################################################################
############################################################################################################
############################################################################################################

@bot.command(pass_context = True)
async def bc(ctx):
    userid = ctx.message.author.id
    index = findTeam(userid)
    if not gamepause:
        if index == -1:
            await bot.whisper('You do not have a team yet, create one with ``!start``.')
        else:
            duelindex = memfindDueltag(TeamList[index].dueltag)
            if duelindex != -1:
                await bot.whisper('You cannot use the BC while you are in a duel.')
            else:
                duelist = TeamList[index]
                scroll = [duelist.g1, duelist.g2, duelist.g3]
                w = '**Team:**'
                for i, gem in enumerate(scroll):
                    w += '\n' + str(i+1) + ': ``' + gem.name 
                    if gem.id != 'NULL': 
                        w += '\tLevel: ' + str(gem.level) + '\t' + TypeList[gem.type1] + '/' + TypeList[gem.type2]
                        ctype = gem.ctype
                        if ctype != '':
                            w += ' [' + ctype + ']'
                    w += '``'
                    
                w += '\n\n**BC Storage:**'
                for i, gem in enumerate(duelist.PC):
                    w += '\n' + str(i+4) + ': ``' + gem.name + '\tLevel: ' + str(gem.level) \
                        + '\t' + TypeList[gem.type1] + '/' + TypeList[gem.type2]
                    ctype = gem.ctype
                    if ctype != '':
                        w = w + ' [' + ctype + ']'
                    w += '``'
                    if len(w) > 1600:
                        await bot.whisper(w)
                        w = '-----\n'
                
                #w += '\n\nWithdraw Gemma with ``!bcw <Gemma slot number>``, deposit Gemma with ``!bcd <Gemma slot number>``, look at Gemma with ``!bcs <Gemma slot number>``'
                await bot.whisper(w)

@bot.command(pass_context = True)
async def bcw(ctx, gnum = ''):
    user = ctx.message.author
    userid = ctx.message.author.id
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            try:
                gnum = int(gnum)
                if index == -1:
                    await bot.whisper('You do not have a team yet, create one with ``!start``.')
                else:
                    duelindex = memfindDueltag(TeamList[index].dueltag)

                    if duelindex != -1:
                        await bot.whisper('You cannot use the BC while you are in a duel.')
                    elif gnum == '':
                        await bot.whisper('Please specify the target Gemma in the command: ``!bcw <Gemma slot number>``')
                    elif len(TeamList[index].PC) == 0:
                        await bot.whisper('Your BC is empty.')
                    elif gnum < 0 or gnum >= (len(TeamList[index].PC)+4):
                        await bot.whisper('Please enter a valid slot number between 1 and ' + str(len(TeamList[index].PC)+3))
                    elif gnum > 0 and gnum < 4: #Within the team
                        await bot.whisper('That Gemma is already in your team.')
                    else: #Now gnum should be between 4 and len(PC)+4-1
                        c = True
                        global TagList
                        TagList.append([user, '``!bcw``'])
                        while c:
                            try:
                                c = False
                                await bot.whisper('Which team slot do you want to put it in?')
                                ans = await bot.wait_for_message(author = user)
                                ans = int(ans.content)
                                if ans > 0 and ans <= 3:
                                    gem = getGem(TeamList[index], ans)
                                    if gem.id == 'NULL':
                                        await bot.say('You withdrew **' + TeamList[index].PC[gnum-4].name + '**')
                                        assignTeamSlot(TeamList[index], ans, TeamList[index].PC[gnum-4])
                                        del TeamList[index].PC[gnum-4]
                                        #Remove user from TagList
                                        removeFromTagList(user, '``!bcw``')
                                    else:
                                        await bot.whisper('**' + gem.name + '** was sent to the BC to make room for **' + TeamList[index].PC[gnum-4].name + '**')
                                        await bot.say('You withdrew **' + TeamList[index].PC[gnum-4].name + '**')
                                        TeamList[index].PC.append(gem)
                                        assignTeamSlot(TeamList[index], ans, TeamList[index].PC[gnum-4])
                                        del TeamList[index].PC[gnum-4]
                                        #Remove user from TagList
                                        removeFromTagList(user, '``!bcw``')
                                        
                                    savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)

                                else:
                                    await bot.whisper('Please enter a number between 1 and 3.')
                                    c = True
                            except ValueError:
                                await bot.whisper('Please enter a number between 1 and 3.')
                                c = True

            except ValueError:
                await bot.whisper('Please enter a valid slot number between 1 and ' + str(len(TeamList[index].PC)+3))
            
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

@bot.command(pass_context = True)
async def bcs(ctx, gnum = ''):
    userid = ctx.message.author.id
    index = findTeam(userid)
    
    if not gamepause:
        try:
            gnum = int(gnum)
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            else:
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex != -1:
                    await bot.whisper('You cannot use the BC while you are in a duel.')
                elif gnum == -1:
                    await bot.whisper('Please specify the target Gemma in the command: ``!bcs <Gemma slot number>``')
                elif gnum < 0 or gnum >= (len(TeamList[index].PC)+4):
                    await bot.whisper('Please enter a valid slot number between 1 and ' + str(len(TeamList[index].PC)+3))
                else:
                    if gnum > 0 and gnum <= 3:
                        gem = getGem(TeamList[index], gnum)
                        if gem.id != 'NULL':
                            title, disc, ab1, ab2, pas = prepareEmbed(gem)
                            embed = makeEmbed(title, disc, ab1, ab2, pas)
                            await bot.say(embed=embed)
                    else:
                        gem = TeamList[index].PC[gnum-4]
                        title, disc, ab1, ab2, pas = prepareEmbed(gem)
                        embed = makeEmbed(title, disc, ab1, ab2, pas)
                        await bot.whisper(embed=embed)
        except ValueError:
            await bot.whisper('Please enter a valid slot number between 1 and ' + str(len(TeamList[index].PC)+3))

@bot.command(pass_context = True)
async def bcd(ctx, gnum = ''):
    userid = ctx.message.author.id
    user = ctx.message.author
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            try:
                gnum = int(gnum)
                
                if index == -1:
                    await bot.whisper('You do not have a team yet, create one with ``!start``.')
                else:
                    duelindex = memfindDueltag(TeamList[index].dueltag)
                    if duelindex != -1:
                        await bot.whisper('You cannot use the BC while you are in a duel.')
                    elif gnum == -1:
                        await bot.whisper('Please specify the target Gemma in the command: ``!bcd <Gemma slot number>``')
                    elif gnum < 0 or gnum >= 4:
                        await bot.whisper('Please enter a valid team slot number when using ``!bcd < Gemma slot number>``.')
                    else:
                        gem = getGem(TeamList[index], gnum)
                        if gem.id != 'NULL':
                            [tstamp, TimeListIndex] = findTimeList(TeamList[index].userid, gem.id)
                            nowtime = time.clock()+600
                            if abs(tstamp-nowtime) > 600:
                                TimeList[TimeListIndex][2] = nowtime
                                #APImpact. MoodImpact
                                gem.AP += APImpact[gem.personality][4]
                                if gem.AP > 15: gem.AP = 15
                                elif gem.AP < 0: gem.AP = 0
                                gem.mood += MoodImpact[gem.personality][4]
                                if gem.mood > 6: gem.mood = 5
                                elif gem.mood < -6: gem.mood = -5

                            TeamList[index].PC.append(gem)
                            assignTeamSlot(TeamList[index], gnum, Gemma()) #Assign an empty Gemma in its place
                            await bot.say('You deposited **' + gem.name + '**')
                            savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
            except ValueError:
                await bot.whisper('Please enter a valid team slot number when using ``!bcd <Gemma slot number>``')
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

############################################################################################################
############################################################################################################
############################################################################################################


#   IN-DUEL USER COMMANDS


############################################################################################################
############################################################################################################
############################################################################################################

@bot.command(pass_context = True)#New, not yet tested
async def cancel(ctx):
    userid = ctx.message.author.id
    user = ctx.message.author
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)

    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif ctx.message.channel.is_private:
                await bot.whisper('Duel commands can only be used on the Jaegergems server.')
            else:
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex == -1:
                    await bot.say('You are currently not in a duel.')
                else:
                    DM = DuelmemList[duelindex]
                    global TagList
                    TagList.append([user, '``!cancel``'])
                    await bot.say('Are you sure you want to cancel your duel with ' + TeamList[index].opponent +
                                '? Type "y" for yes and anything else for no:')
                    ans = await bot.wait_for_message(author = user)
                    ans = ans.content
                    if ans == 'Y' or ans == 'y':
                        await bot.say(TeamList[index].duelistname + ' has cancelled their duel with ' + TeamList[index].opponent)
                        eindex = findName(TeamList[index].opponent)
                        
                        if TeamList[eindex].bot:
                            AIindex = findAItask(TeamList[index].dueltag)
                            if AIindex != -1:
                                AItaskList[AIindex].task.cancel()
                                AItaskList.remove(AItaskList[AIindex])
                        
                        TeamList[index].opponent = '-1'
                        TeamList[index].dueltag = -1
                        TeamList[eindex].opponent = '-1'
                        TeamList[eindex].dueltag = -1
                        
                        print('Duel between ', DM.duelists[0].duelistname, ' and ', DM.duelists[1].duelistname, ' is being cancelled!')

                        #Remove from duel memory
                        DuelmemList.remove(DM)

                        if TeamList[index].bot and TeamList[index].user == -1:
                            #Random NPC, remove from TeamList
                            TeamList.remove(TeamList[index])
                        elif TeamList[eindex].bot and TeamList[eindex].user == -1:
                            #Random NPC, remove from TeamList
                            TeamList.remove(TeamList[eindex])
                        
                    #Remove user from TagList
                    removeFromTagList(user, '``!cancel``')
                    savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
                    
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

@bot.command(pass_context = True)
async def challenge(ctx, *, enemy = ''): #Initiates duel phase 0
    user = ctx.message.author
    userid = user.id
    index = findTeam(userid)
    eindex = findName(enemy)    
    
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif ctx.message.channel.is_private:
                await bot.whisper('Duel commands can only be used on the Jaegergems server.')
            elif index == eindex:
                await bot.say('You cannot challenge yourself!')           
            elif enemy == '':
                await bot.whisper('Please specify the target player in the command: ``!challenge <duelist name>``')
            elif findName(TeamList[index].opponent) != -1:
                await bot.say('You are already in a duel with ' + str(TeamList[index].opponent))
            elif eindex == -1:
                await bot.say(enemy + ' does not have a team yet.')
            elif findName(TeamList[eindex].opponent) != -1:
                await bot.say(enemy + ' is already in a duel.')
            elif TeamList[index].g1.id == 'NULL':
                await bot.say('You must have a gemma in your first team slot to duel.')
            elif TeamList[eindex].g1.id == 'NULL':
                await bot.say(enemy + ' must have a Gemma in their first team slot to duel.')
            else:
                if TeamList[eindex].opponent == 'Waiting for a response from ' + TeamList[index].duelistname:
                    await bot.say(TeamList[index].duelistname + ' accepts ' + TeamList[eindex].duelistname + '\'s challenge!')
                    
                    #Removing duelmem remains
                    currentmem = copy.copy(DuelmemList)
                    for mem in currentmem:
                        if mem.duelists[0].userid == TeamList[index].userid or mem.duelists[1].userid == TeamList[index].userid:
                            print(' - - - - - Found remains of duelmem for duelist: ', TeamList[index].duelistname)
                            try:
                                DuelmemList.remove(mem)
                            except ValueError:
                                pass
                        if mem.duelists[0].userid == TeamList[eindex].userid or mem.duelists[1].userid == TeamList[eindex].userid:
                            print(' - - - - - Found remains of duelmem for duelist: ', TeamList[index].duelistname)
                            try:
                                DuelmemList.remove(mem)
                            except ValueError:
                                pass
                    
                    TeamList[eindex].opponent = TeamList[index].duelistname
                    TeamList[index].opponent = TeamList[eindex].duelistname

                    dueltag = TeamList[index].duelistname + TeamList[eindex].duelistname
                    TeamList[eindex].dueltag = dueltag
                    TeamList[index].dueltag = dueltag

                    duel = Duelmem()
                    duel.phase = 0
                    duel.dueltag = dueltag
                    duel.duelists[0] = copy.copy(TeamList[index])
                    duel.duelists[1] = copy.copy(TeamList[eindex])

                    #Deep copy of Gemma
                    duel.duelists[0].g1 = copy.copy(TeamList[index].g1)
                    duel.duelists[0].g2 = copy.copy(TeamList[index].g2)
                    duel.duelists[0].g3 = copy.copy(TeamList[index].g3)
                    duel.duelists[1].g1 = copy.copy(TeamList[eindex].g1)
                    duel.duelists[1].g2 = copy.copy(TeamList[eindex].g2)
                    duel.duelists[1].g3 = copy.copy(TeamList[eindex].g3)
                    
                    #Deep copy of Gemma abilities, otherwise the python list is shared
                    duel.duelists[0].g1.ability = copy.copy(TeamList[index].g1.ability)
                    duel.duelists[0].g2.ability = copy.copy(TeamList[index].g2.ability)
                    duel.duelists[0].g3.ability = copy.copy(TeamList[index].g3.ability)
                    duel.duelists[1].g1.ability = copy.copy(TeamList[eindex].g1.ability)
                    duel.duelists[1].g2.ability = copy.copy(TeamList[eindex].g2.ability)
                    duel.duelists[1].g3.ability = copy.copy(TeamList[eindex].g3.ability)

                    #Deep copy of Gemma passives, otherwise the python list is shared
                    duel.duelists[0].g1.passive = copy.copy(TeamList[index].g1.passive)
                    duel.duelists[0].g2.passive = copy.copy(TeamList[index].g2.passive)
                    duel.duelists[0].g3.passive = copy.copy(TeamList[index].g3.passive)
                    duel.duelists[1].g1.passive = copy.copy(TeamList[eindex].g1.passive)
                    duel.duelists[1].g2.passive = copy.copy(TeamList[eindex].g2.passive)
                    duel.duelists[1].g3.passive = copy.copy(TeamList[eindex].g3.passive)
                    
                    duel.channel = ctx.message.channel
                    DuelmemList.append(duel)
                    
                    hpbar = ''
                    if TeamList[index].g1.hp <= 0: hpbar += ':skull:'
                    else:
                        for i in range(0, TeamList[index].g1.hp): hpbar += ':heart:'
                        for i in range(0, TeamList[index].g1.maxhp - TeamList[index].g1.hp): hpbar += ':black_heart:'
                        for i in range(0, TeamList[index].g1.guard): hpbar += ':shield:'
    
                    disc1 = 'Lv.' + str(TeamList[index].g1.level) + ' **' + TeamList[index].g1.name + '**, the ' + TypeList[TeamList[index].g1.type1] \
                    + '/' + TypeList[TeamList[index].g1.type2]
                    ctype = TeamList[index].g1.ctype
                    if ctype != '':
                        disc1 += ' [' + ctype + ']'
                    disc1 += ' Gemma - ' + hpbar 

                    hpbar = ''
                    if TeamList[eindex].g1.hp <= 0: hpbar += ':skull:'
                    else:
                        for i in range(0, TeamList[eindex].g1.hp): hpbar += ':heart:'
                        for i in range(0, TeamList[eindex].g1.maxhp - TeamList[eindex].g1.hp): hpbar += ':black_heart:'
                        for i in range(0, TeamList[eindex].g1.guard): hpbar += ':shield:'

                    disc2 = 'Lv.' + str(TeamList[eindex].g1.level) + ' **' + TeamList[eindex].g1.name + '**, the ' + TypeList[TeamList[eindex].g1.type1] \
                    + '/' + TypeList[TeamList[eindex].g1.type2]
                    ctype = TeamList[eindex].g1.ctype
                    if ctype != '':
                        disc2 += ' [' + ctype + ']'
                    disc2 += ' Gemma - ' + hpbar
                    
                    disc = 'Duelist **' + TeamList[index].duelistname + '**\n' + disc1 + '\n\n**VS**\n\n' \
                            + 'Duelist **' + TeamList[eindex].duelistname + '**\n' + disc2
                    
                    embed = discord.Embed(
                        title = 'Duel',
                        description = disc,
                        color = discord.Colour.red()
                    )
                    await bot.say(embed=embed)
                    await bot.say('\nAdvance with ``!go``')

                else:
                    TeamList[index].opponent = 'Waiting for a response from ' + enemy
                    await bot.say(TeamList[index].duelistname + ' is challenging ' + enemy + ' to a Jaegergem duel! Accept with a corresponding ``!challenge <duelist name>``')
                savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

@bot.command(pass_context = True)
async def go(ctx):
    user = ctx.message.author
    userid = user.id
    index = findTeam(userid)
    #eindex = findName(TeamList[index].opponent)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif ctx.message.channel.is_private:
                await bot.whisper('Duel commands can only be used on the Jaegergems server.')
            else:
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex == -1:
                    await bot.whisper('You are currently not in a duel.')
                else:
                    DM = DuelmemList[duelindex]
                    if DM.phase == 0:
                        [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
                        if not DM.duelists[notowner].gotrigger: #Enemy team have not used !go yet
                            DM.duelists[owner].gotrigger = True #Set your !go trigger to True
                        else: #Enemy team has used !go            
                            #owner and notowner can be 0 or 1, it is the slot in Duelmem.duelists
                            DM.turn = owner
                            playerIndex = DM.turn 
                            enemyIndex = -1 #temporary just to define it
                            if playerIndex == 0:
                                enemyIndex = 1
                            else:
                                enemyIndex = 0
                            
                            #New initiative, clear out last initiative's rolls and bonuses
                            DM.spdroll = 0
                            DM.espdroll = 0
                            DM.spdbonus = 0
                            DM.espdbonus = 0

                            embed = rollInitiative(DM, playerIndex, enemyIndex) 
                            await bot.say(embed=embed)
                            await bot.say('Advance with ``!go``')
                            #Whoever uses !initiative get's the turn. HOWEVER, this does not affect any ability. It only tells us their speed is stored in spdroll.
                            
                            DM.turn = owner

                            #Clear go trigger
                            DM.duelists[owner].gotrigger = False
                            DM.duelists[notowner].gotrigger = False

                    elif DM.phase == 1:            
                        [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
                        if not DM.duelists[notowner].gotrigger: #Enemy team have not used !go yet
                            DM.duelists[owner].gotrigger = True #Set your !go trigger to True
                        else: #Enemy team has used !go
                            playerIndex = DM.turn
                            enemyIndex = -1 #temporary just to define it
                            if playerIndex == 0:
                                enemyIndex = 1
                            else:
                                enemyIndex = 0

                            speed = DM.spdroll
                            espeed = DM.espdroll
                            spdbonus = DM.spdbonus
                            espdbonus = DM.espdbonus

                            espeed = espeed + espdbonus
                            speed = speed + spdbonus
                            frac, whole = math.modf(espeed)
                            if frac == 0.0: espeed = int(espeed)
                            frac, whole = math.modf(speed)
                            if frac == 0.0: speed = int(speed)
                            
                            if speed > espeed:
                                disc = DM.duelists[playerIndex].g1.name + ': **' + str(speed) + '**\n' \
                                    + DM.duelists[enemyIndex].g1.name + ': **' + str(espeed) + '**\n\n' \
                                    + 'Duelist **' + DM.duelists[playerIndex].duelistname + '** has the turn!'
                                embed = discord.Embed(
                                    title = 'Initiative results',
                                    description = disc,
                                    color = discord.Colour.gold()
                                )
                                await bot.say(embed=embed)
                                
                                DM.turn = playerIndex
                                print('Playerindex: ', playerIndex)
                                print('turn: ', DM.turn)
                                DM.phase = 2

                            elif speed < espeed: 
                                disc = DM.duelists[playerIndex].g1.name + ': **' + str(speed) + '**\n' \
                                    + DM.duelists[enemyIndex].g1.name + ': **' + str(espeed) + '**\n\n' \
                                    + 'Duelist **' + DM.duelists[enemyIndex].duelistname + '** has the turn!'
                                embed = discord.Embed(
                                    title = 'Initiative results',
                                    description = disc,
                                    color = discord.Colour.gold()
                                )
                                await bot.say(embed=embed)
                                DM.turn = enemyIndex
                                DM.phase = 2

                            else:
                                DM.spdbonus = 0
                                DM.espdbonus = 0
                                
                                disc = DM.duelists[playerIndex].g1.name + ': **' + str(speed) + '**\n' \
                                    + DM.duelists[enemyIndex].g1.name + ': **' + str(espeed) + '**\n'

                                r = random.randint(0, 1)
                                if r == 0:
                                    DM.turn = enemyIndex
                                    print('enemyindex: ', enemyIndex)
                                    print('turn: ', DM.turn)
                                    disc += '\n**TIE** - The turn is randomly assigned to duelist **' + DM.duelists[enemyIndex].duelistname + '**!'
                                else:
                                    DM.turn = playerIndex
                                    print('Playerindex: ', playerIndex)
                                    print('turn: ', DM.turn)
                                    disc += '\n**TIE** - The turn is randomly assigned to duelist **' + DM.duelists[playerIndex].duelistname + '**!'
                                
                                embed = discord.Embed(
                                    title = 'Initiative results',
                                    description = disc,
                                    color = discord.Colour.gold()
                                )                       
                                await bot.say(embed=embed)
                                DM.phase = 2

                            #Clear go trigger
                            DM.duelists[owner].gotrigger = False
                            DM.duelists[notowner].gotrigger = False

                    elif DM.phase == 3:
                        [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
                        if not DM.duelists[notowner].gotrigger: #Enemy team have not used !go yet
                            DM.duelists[owner].gotrigger = True #Set your !go trigger to True
                        else: #Enemy team has used !go
                            atkIndex = DM.turn #They who has the turn, is the attacker
                            defIndex = -1 #Temporary just to define it
                            if atkIndex == 0:
                                defIndex = 1
                            else:
                                defIndex = 0

                            playerIndex = atkIndex
                            enemyIndex = defIndex

                            attack = DM.atkroll
                            defence = DM.defroll
                            typemod = DM.typemod
                            atkbonus = DM.atkbonus
                            defbonus = DM.defbonus
                            atkpower = DM.atkpower
                            
                            if typemod < 0:
                                defence = defence - typemod
                            elif typemod > 0:
                                attack = attack + typemod
                            
                            attack = attack + atkbonus
                            defence = defence + defbonus
                            frac, whole = math.modf(attack)
                            if frac == 0.0: attack = int(attack)
                            frac, whole = math.modf(defence)
                            if frac == 0.0: defence = int(defence)
                            

                            disc = 'Total attack for ' + DM.duelists[atkIndex].g1.name + ': **' \
                            + str(attack) + '**' + '\nTotal defence for ' + DM.duelists[defIndex].g1.name \
                            + ': **' + str(defence) + '**'

                            #Defence reduction if guardbreak
                            if DM.duelists[defIndex].g1.guard == 0:
                                disc += '\n\n:diamond_shape_with_a_dot_inside: **Guard Break - Defence is reduced by ' + str(GuardBreakMod[DM.duelists[defIndex].g1.level-1]) + '** :diamond_shape_with_a_dot_inside:'

                            slink = '-1'
                            vdmg1 = '-1'
                            vdmg2 = '-1'
                            if defence < attack:
                                DM.duelists[defIndex].g1.hp -= atkpower 
                                
                                slink = soulink_check(DM, DM.duelists[defIndex].g1.id, atkpower)

                                ###PASSIVE TRIGGER
                                if DM.duelists[0].g1.ctype != '':
                                    vdmg1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
                                if DM.duelists[1].g1.ctype != '':
                                    vdmg2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
                                ###END OF PASSIVE TRIGGER

                                if DM.duelists[defIndex].g1.hp <= 0:
                                    disc += '\n\n**' + DM.duelists[defIndex].g1.name + '** :skull: **faints!**'
                                    DM.duelists[defIndex].g1.alive = False
                                    awardAP(DM, defIndex, 2)
                                    DM.duelists[defIndex].rotblock = False #You should always be able to rotate out when dead
                                    #Award XP, check marker 4 for a takedown
                                    awardXP(DM, atkIndex, 4, DM.duelists[atkIndex].g1.level, DM.duelists[defIndex].g1.level)
                                else:
                                    hpbar = ''
                                    if DM.duelists[defIndex].g1.hp <= 0: hpbar += ':skull:'
                                    else:
                                        for i in range(0, DM.duelists[defIndex].g1.hp): hpbar += ':heart:'
                                        for i in range(0, DM.duelists[defIndex].g1.maxhp - DM.duelists[defIndex].g1.hp): hpbar += ':black_heart:'
                                        for i in range(0, DM.duelists[defIndex].g1.guard): hpbar += ':shield:'
                                    disc += '\n\n**' + DM.duelists[defIndex].g1.name + '** - ' + hpbar + ' **survives the attack!**'

                                    #Award XP, check marker 1 for surviving an attack
                                    awardXP(DM, defIndex, 1, DM.duelists[defIndex].g1.level, DM.duelists[atkIndex].g1.level)

                            else: #defence >= attack
                                DM.duelists[defIndex].g1.guard -= 1
                                if DM.duelists[defIndex].g1.guard <= 0:
                                    DM.duelists[defIndex].g1.guard = 0
                                    disc += '\n\n:diamond_shape_with_a_dot_inside: **Guard Break** :diamond_shape_with_a_dot_inside:'
                                
                                hpbar = ''
                                if DM.duelists[defIndex].g1.hp <= 0: hpbar += ':skull:'
                                else:
                                    for i in range(0, DM.duelists[defIndex].g1.hp): hpbar += ':heart:'
                                    for i in range(0, DM.duelists[defIndex].g1.maxhp - DM.duelists[defIndex].g1.hp): hpbar += ':black_heart:'
                                    for i in range(0, DM.duelists[defIndex].g1.guard): hpbar += ':shield:'
                                disc += '\n\n**' + DM.duelists[defIndex].g1.name + '** - ' + hpbar + ' **survives the attack!**'
                                
                                
                                #Award XP, check marker 1 for surviving an attack
                                awardXP(DM, defIndex, 1, DM.duelists[defIndex].g1.level, DM.duelists[atkIndex].g1.level)

                            embed = discord.Embed(
                                title = 'Aftermath',
                                description = disc,
                                color = discord.Colour.red()
                            )

                            if slink != '-1': embed.add_field(name='Ability trigger', value = slink)
                            if vdmg1 != '-1': embed.add_field(name='Passive ability', value = vdmg1)
                            if vdmg2 != '-1': embed.add_field(name='Passive ability', value = vdmg2)
                            
                            DM.phase = 4 #Phase 4

                            #Sorting abilityList by num before the search. This is to enforce priority, low number abilities are at the top of the
                            #abilityList, so they activate first. 
                            
                            DM.abilityList = sorted(DM.abilityList, key = getKey)
                            
                            #We loop through this one since abilityList may get shorter when abilities trigger and remove themselves.
                            #This deep copy will be static throughout the loop.
                            loopabilityList = copy.copy(DM.abilityList)

                            for i in range(0, len(loopabilityList)): 
                                w, loop_slink1, loop_slink2, loop_pas1, loop_pas2 = ability(loopabilityList[i][0], '-1', DM, atkIndex, defIndex, owner, i, loopabilityList[i])
                                #We send abIndex '-1', because we should never use abIndex for triggers. If we go, we'll get an error.
                                if w != '-1': embed.add_field(name='Ability trigger', value = w)
                                if loop_slink1 != '-1': embed.add_field(name='Ability trigger', value = loop_slink1)
                                if loop_slink2 != '-1': embed.add_field(name='Ability trigger', value = loop_slink2)
                                if loop_pas1 != '-1': embed.add_field(name='Passive ability', value = loop_pas1)
                                if loop_pas2 != '-1': embed.add_field(name='Passive ability', value = loop_pas2)

                            plague_slink = '-1'
                            plague_vdmg1 = '-1'
                            plague_vdmg2 = '-1'
                            #PASSIVE TRIGGER LIST
                            for entry in DM.passiveList:
                                if entry[0] == 17: #Plague passive
                                    if entry[2] < 4:
                                        entry[2] += 1
                                    elif entry[2] == 4:
                                        gem = findGemIDduel(DM, entry[1])
                                        gem.hp -= 2
                                        if gem.hp <= 0: 
                                            gem.alive = False
                                            if DM.duelists[0].g1.id == gem.id:
                                                DM.duelists[0].rotblock = False #You should always be able to rotate out when dead
                                            elif DM.duelists[1].g1.id == gem.id:
                                                DM.duelists[1].rotblock = False #You should always be able to rotate out when dead
                                            v = '*>> Plague: ' + gem.name + ' takes 2 damage from the plague curse! ' + gem.name + '* :skull: *faints!*'
                                        else:
                                            v = '*>> Plague: ' + gem.name + ' takes 2 damage from the plague curse!*'
                                        embed.add_field(name='Passive ability', value = v)
                                        DM.passiveList.remove(entry)
                                        
                                        plague_slink = soulink_check(DM, gem.id, atkpower)

                                        ###PASSIVE TRIGGER
                                        if DM.duelists[0].g1.ctype != '':
                                            plague_vdmg1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
                                        if DM.duelists[1].g1.ctype != '':
                                            plague_vdmg2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
                                        ###END OF PASSIVE TRIGGER
                                    
                                if entry[0] == 29: #Phoenix passive
                                    if entry[2] < 6:
                                        entry[2] += 1
                                    elif entry[2] == 6:
                                        gem = findGemIDduel(DM, entry[1])
                                        gem.alive = True
                                        gem.hp = 1
                                        DM.passiveList.remove(entry)
                                        v = '*>> Phoenix: ' + gem.name + ' rises from the ashes!*'
                                        embed.add_field(name='Passive ability', value = v)
                            #END OF PASSIVE TRIGGER LIST

                            ###PASSIVE TRIGGER
                            if DM.duelists[0].g1.ctype != '':
                                v = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Go', -1)
                                if v != '-1':
                                    embed.add_field(name='Passive ability', value = v)
                            if DM.duelists[1].g1.ctype != '':
                                v = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Go', -1)
                                if v != '-1':
                                    embed.add_field(name='Passive ability', value = v)
                            ###END OF PASSIVE TRIGGER

                            if plague_slink != '-1': embed.add_field(name='Ability trigger', value = plague_slink)
                            if plague_vdmg1 != '-1': embed.add_field(name='Passive ability', value = plague_vdmg1)
                            if plague_vdmg2 != '-1': embed.add_field(name='Passive ability', value = plague_vdmg2)
                            
                            await bot.say(embed=embed)

                            result = findLoser(DM) #Check if there is a loser
                            if result != -1:
                                
                                await actOnLoser(result, DM, owner, notowner)
                                
                            else:
                                DM.turn = defIndex #Assign turn to the defender

                                if DM.duelists[atkIndex].g1.alive and not DM.duelists[defIndex].g1.alive:
                                    await bot.say('Waiting for duelist **' + DM.duelists[defIndex].duelistname + '** to rotate Gemma.')
                                elif DM.duelists[atkIndex].g1.alive and DM.duelists[defIndex].g1.alive:
                                    await bot.say('Duelist **' + DM.duelists[defIndex].duelistname + '** has the turn!')
                                elif not DM.duelists[atkIndex].g1.alive and DM.duelists[defIndex].g1.alive:
                                    await bot.say('Waiting for duelist **' + DM.duelists[atkIndex].duelistname + '** to rotate Gemma.')
                                else: #attacker and defender dead
                                    await bot.say('Waiting for both duelists to rotate Gemma')
                                
                                #Clear !go trigger
                                DM.duelists[owner].gotrigger = False
                                DM.duelists[notowner].gotrigger = False
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')



@bot.command(pass_context = True)
async def attack(ctx):
    user = ctx.message.author
    userid = user.id
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif ctx.message.channel.is_private:
                await bot.whisper('Duel commands can only be used on the Jaegergems server.')
            else:
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex == -1:
                    await bot.whisper('You are currently not in a duel.')
                else:
                    DM = DuelmemList[duelindex]
                    if DM.phase != 2 and DM.phase != 4:
                        pass #To stop it saying "not your turn" when it is the wrong phase    
                    elif DM.phase == 2 or DM.phase == 4:  
                        [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
                        if DM.turn != owner:
                            await bot.say('It is not your turn.')
                        elif not DM.duelists[owner].g1.alive:
                            await bot.say('You cannot attack with a defeated Gemma.')
                        elif not DM.duelists[notowner].g1.alive:
                            await bot.say('You cannot attack, the opposing Gemma is defeated.')
                        else:
                            #New attack, clear out last attack's rolls and bonuses
                            DM.atkroll = 0
                            DM.defroll = 0
                            DM.atkbonus = 0
                            DM.defbonus = 0
                            DM.typemod = 0
                            DM.atkpower = DM.duelists[owner].g1.power

                            #This is a regular attack
                            DM.caliber = 0
                            
                            attack = DM.duelists[owner].g1.attack #attack stat of user player's first Gemma
                            defence = DM.duelists[notowner].g1.defence #defence stat of opponent player's first Gemma
                            atkroll = random.randint(1, DiceList[attack])
                            defroll = random.randint(1, DiceList[defence])

                            atk = DM.duelists[owner].g1.type1
                            defe = [DM.duelists[notowner].g1.type1, DM.duelists[notowner].g1.type2]
                            mod = TypeChart[ atk , defe[0] ] + TypeChart[ atk , defe[1] ] 

                            #Type modifier now scales with the level of the attacker or defender!
                            if mod > 0:
                                mod = mod * TypemodLevelScaling[DM.duelists[owner].g1.level-1]
                            else:
                                mod = mod * TypemodLevelScaling[DM.duelists[notowner].g1.level-1]
                            DM.typemod = mod


                            playerIndex = DM.turn 
                            enemyIndex = -1 #temporary just to define it
                            if playerIndex == 0:
                                enemyIndex = 1
                            else:
                                enemyIndex = 0

                            v1 = '-1'
                            v2 = '-1'
                            ###PASSIVE TRIGGER - This has to be before where we check modifier. A passive might change the modifier.
                            if DM.duelists[0].g1.ctype != '':
                                v1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Typemod', -1)
                            if DM.duelists[1].g1.ctype != '':
                                v2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Typemod', -1)
                            ###END OF PASSIVE TRIGGER

                            disc = DM.duelists[owner].g1.name + ' attacks ' + DM.duelists[notowner].g1.name + '!\n'
                            if mod > 0:
                                disc += 'Attack roll: **' + str(atkroll) + '**\nType modifier **+' + str(mod) + '** gives a Total attack of: **' + str(mod+atkroll) \
                                + '**\nDefence roll: **' + str(defroll) + '**\n'
                            elif mod < 0:
                                disc += 'Attack roll: **' + str(atkroll) + '**\nDefence roll: **' + str(defroll) + '**' \
                                    + '\nType modifier **+' + str(-mod) + '** gives a Total defence of: **' + str(-mod+defroll) \
                                    + '**\n'
                            else:
                                disc += 'Attack roll: **' + str(atkroll) + '**\nDefence roll: **' + str(defroll) + '**\n'
                            
                            #Auto hit if guardbreak
                            if DM.duelists[notowner].g1.guard == 0:
                                disc += '\n\n:diamond_shape_with_a_dot_inside: **Guard Break - Defence is reduced by ' + str(GuardBreakMod[DM.duelists[notowner].g1.level-1]) + '** :diamond_shape_with_a_dot_inside:'
                                DM.defbonus -= GuardBreakMod[DM.duelists[notowner].g1.level-1]
                            embed = discord.Embed(
                                title = TypeList[DM.duelists[owner].g1.type1] + ' Attack',
                                description = disc,
                                color = discord.Colour.red()
                            )

                            #Save rolls in memory
                            DM.atkroll = atkroll
                            DM.defroll = defroll

                            if v1 != '-1':
                                embed.add_field(name='Passive ability', value = v1)
                            if v2 != '-1':
                                embed.add_field(name='Passive ability', value = v2)
                            
                            ###PASSIVE TRIGGER
                            if DM.duelists[0].g1.ctype != '':
                                v3 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Attack', -1)
                                if v3 != '-1':
                                    embed.add_field(name='Passive ability', value = v3)

                            if DM.duelists[1].g1.ctype != '':
                                v4 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Attack', -1)
                                if v4 != '-1':
                                    embed.add_field(name='Passive ability', value = v4)
                            ###END OF PASSIVE TRIGGER

                            await bot.say(embed=embed)
                            await bot.say('Advance with ``!go``')

                            #Award affection points!
                            awardAP(DM, owner, 0)

                            DM.phase = 3 #Phase 3
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')


@bot.command(pass_context = True)
async def hattack(ctx):
    user = ctx.message.author
    userid = user.id
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif ctx.message.channel.is_private:
                await bot.whisper('Duel commands can only be used on the Jaegergems server.')
            else:
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex == -1:
                    await bot.whisper('You are currently not in a duel.')
                else:
                    DM = DuelmemList[duelindex]
                    if DM.phase != 2 and DM.phase != 4:
                        pass #To stop it saying "not your turn" when it is the wrong phase    
                    elif DM.phase == 2 or DM.phase == 4:  
                        [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
                        if DM.turn != owner:
                            await bot.say('It is not your turn.')
                        elif not DM.duelists[owner].g1.alive:
                            await bot.say('You cannot attack with a defeated Gemma.')
                        elif not DM.duelists[notowner].g1.alive:
                            await bot.say('You cannot attack, the opposing Gemma is defeated.')
                        else:
                            #New attack, clear out last attack's rolls and bonuses
                            DM.atkroll = 0
                            DM.defroll = 0
                            DM.atkbonus = 0
                            DM.defbonus = 0
                            DM.typemod = 0
                            DM.atkpower = DM.duelists[owner].g1.power + 1 #+1 for heavy attack

                            #This is a heavy attack
                            DM.caliber = 1
                            
                            attack = DM.duelists[owner].g1.attack #attack stat of user player's first Gemma
                            defence = DM.duelists[notowner].g1.defence #defence stat of opponent player's first Gemma
                            
                            defroll = random.randint(1, DiceList[defence])

                            #Heavy attack accuracy drawback, does not apply to modifiers
                            #Disadvantage for now, could be a scale drawback
                            atkroll = random.randint(1, DiceList[attack])
                            atkroll_dis = random.randint(1, DiceList[attack])
                            if atkroll_dis < atkroll: atkroll = atkroll_dis

                            atk = DM.duelists[owner].g1.type2
                            defe = [DM.duelists[notowner].g1.type1, DM.duelists[notowner].g1.type2]
                            mod = TypeChart[ atk , defe[0] ] + TypeChart[ atk , defe[1] ] 

                            #Type modifier now scales with the level of the attacker or defender!
                            if mod > 0:
                                mod = mod * TypemodLevelScaling[DM.duelists[owner].g1.level-1]
                            else:
                                mod = mod * TypemodLevelScaling[DM.duelists[notowner].g1.level-1]
                            DM.typemod = mod

                            playerIndex = DM.turn 
                            enemyIndex = -1 #temporary just to define it
                            if playerIndex == 0:
                                enemyIndex = 1
                            else:
                                enemyIndex = 0

                            v1 = '-1'
                            v2 = '-1'
                            ###PASSIVE TRIGGER - This has to be before where we check modifier. A passive might change the modifier.
                            if DM.duelists[0].g1.ctype != '':
                                v1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Typemod', -1)
                                
                            if DM.duelists[1].g1.ctype != '':
                                v2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Typemod', -1)
                            ###END OF PASSIVE TRIGGER

                            disc = DM.duelists[owner].g1.name + ' attacks ' + DM.duelists[notowner].g1.name + '!\n'
                            if mod > 0:
                                disc += 'Attack roll: **' + str(atkroll) + '**\nType modifier **+' + str(mod) + '** gives a Total attack of: **' + str(mod+atkroll) \
                                + '**\nDefence roll: **' + str(defroll) + '**\n'
                            elif mod < 0:
                                disc += 'Attack roll: **' + str(atkroll) + '**\nDefence roll: **' + str(defroll) + '**' \
                                    + '\nType modifier **+' + str(-mod) + '** gives a Total defence of: **' + str(-mod+defroll) \
                                    + '**\n'
                            else:
                                disc += 'Attack roll: **' + str(atkroll) + '**\nDefence roll: **' + str(defroll) + '**\n'

                            #Auto hit if guardbreak
                            if DM.duelists[notowner].g1.guard == 0:
                                disc += '\n\n:diamond_shape_with_a_dot_inside: **Guard Break - Defence is reduced by ' + str(GuardBreakMod[DM.duelists[notowner].g1.level-1]) + '** :diamond_shape_with_a_dot_inside:'
                                DM.defbonus -= GuardBreakMod[DM.duelists[notowner].g1.level-1]

                            embed = discord.Embed(
                                title = 'Heavy ' + TypeList[DM.duelists[owner].g1.type2] + ' Attack',
                                description = disc,
                                color = discord.Colour.red()
                            )

                            #Save rolls in memory
                            DM.atkroll = atkroll
                            DM.defroll = defroll

                            if v1 != '-1':
                                embed.add_field(name='Passive ability', value = v1)
                            if v2 != '-1':
                                embed.add_field(name='Passive ability', value = v2)
                            
                            ###PASSIVE TRIGGER
                            if DM.duelists[0].g1.ctype != '':
                                v3 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Attack', -1)
                                if v3 != '-1':
                                    embed.add_field(name='Passive ability', value = v3)

                            if DM.duelists[1].g1.ctype != '':
                                v4 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Attack', -1)
                                if v4 != '-1':
                                    embed.add_field(name='Passive ability', value = v4)
                            ###END OF PASSIVE TRIGGER

                            await bot.say(embed=embed)
                            await bot.say('Advance with ``!go``')

                            #Award affection points!
                            awardAP(DM, owner, 0)

                            DM.phase = 3 #Phase 3
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')


#______________________________________________________________________________________________________

###################################################################################################

@bot.command(pass_context = True)
async def ab1(ctx):
    userid = ctx.message.author.id
    user = ctx.message.author
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif ctx.message.channel.is_private:
                await bot.whisper('Duel commands can only be used on the Jaegergems server.')
            else:
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex == -1:
                    await bot.whisper('You are currently not in a duel.')
                else:
                    DM = DuelmemList[duelindex]
                    owner = memfindTeam(userid, TeamList[index].dueltag)[0]
                    if owner == 0: notowner = 1
                    else: notowner = 0
                    if DM.duelists[owner].gotrigger: #You have already used !go, you cannot use abilities.
                        await bot.say('You cannot activate abilities after using ``!go``')
                    else:
                        playerIndex = DM.turn 
                        enemyIndex = -1 #temporary just to define it
                        if playerIndex == 0:
                            enemyIndex = 1
                        else:
                            enemyIndex = 0

                        num = DM.duelists[owner].g1.ability[0]

                        #Check you have uses left on the old ability charge
                        if DM.duelists[owner].g1.ability[1] == 0: #If you are out of ability uses, donzo.
                            await bot.say('You have already used that ability this duel.')
                        else:
                            c = True
                            embed = -1
                            for i, ab in enumerate(DM.abilityList):
                                if ab[0] == 0 and ab[1] != owner: #Should not trigger for the owner of the null aura:
                                    #'[-] Null Aura: Nullify your opponent\'s next ability activation.'
                                    disc = '**>>** *Null Aura* triggers and nullifies the ability!'
                                    del DM.abilityList[i]
                                    DM.duelists[owner].g1.ability[1] -= 1
                                    c = False
                                    embed = discord.Embed(
                                        title = 'Ability',
                                        description = disc,
                                        color = discord.Colour.teal()
                                    )   
                            if c:
                                disc, slink1, slink2, pas1, pas2 = ability(num, 0, DM, playerIndex, enemyIndex, owner, -1, -1)
                                embed = discord.Embed(
                                    title = 'Ability',
                                    description = disc,
                                    color = discord.Colour.teal()
                                )
                                
                                if slink1 != '-1': embed.add_field(name='Ability trigger', value = slink1)
                                if slink2 != '-1': embed.add_field(name='Ability trigger', value = slink2)
                                if pas1 != '-1': embed.add_field(name='Passive ability', value = pas1)
                                if pas2 != '-1': embed.add_field(name='Passive ability', value = pas2)

                                ###PASSIVE TRIGGER
                                if DM.duelists[0].g1.ctype != '':
                                    v = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Ability', 1)
                                    if v != '-1':
                                        embed.add_field(name='Passive ability', value = v)
                                if DM.duelists[1].g1.ctype != '':
                                    v = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Ability', 1)
                                    if v != '-1':
                                        embed.add_field(name='Passive ability', value = v)
                                ###END OF PASSIVE TRIGGER         
                            await bot.say(embed=embed)

                        result = findLoser(DM) #Check if there is a loser
                        if result != -1:
                            await actOnLoser(result, DM, owner, notowner)
                            
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')

@bot.command(pass_context = True)
async def ab2(ctx):
    user = ctx.message.author
    userid = user.id
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif ctx.message.channel.is_private:
                await bot.whisper('Duel commands can only be used on the Jaegergems server.')
            else:
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex == -1:
                    await bot.whisper('You are currently not in a duel.')
                else:
                    DM = DuelmemList[duelindex]
                    owner = memfindTeam(userid, TeamList[index].dueltag)[0]
                    if owner == 0: notowner = 1
                    else: notowner = 0
                    if DM.duelists[owner].gotrigger: #You have already used !go, you cannot use abilities.
                        await bot.say('You cannot activate abilities after using ``!go``')
                    elif DM.duelists[owner].g1.ability[2] == -1:
                        await bot.say('Your second ability has not been unlocked yet.')
                    else:
                        playerIndex = DM.turn
                        enemyIndex = -1 #temporary just to define it
                        if playerIndex == 0:
                            enemyIndex = 1
                        else:
                            enemyIndex = 0

                        num = DM.duelists[owner].g1.ability[2]

                        #Check you have uses left on the old ability charge
                        if DM.duelists[owner].g1.ability[3] == 0: #If you are out of ability uses, donzo.
                            await bot.say('You have already used that ability this duel.')
                        else:
                            c = True
                            embed = -1
                            for i, ab in enumerate(DM.abilityList):
                                if ab[0] == 0 and ab[1] != owner: #Should not trigger for the owner of the null aura
                                    #'[-] Null Aura: Nullify your opponent\'s next ability activation.'
                                    disc = '**>>** *Null Aura* triggers and nullifies the ability!'
                                    del DM.abilityList[i]
                                    DM.duelists[owner].g1.ability[3] -= 1
                                    c = False
                                    embed = discord.Embed(
                                        title = 'Ability',
                                        description = disc,
                                        color = discord.Colour.teal()
                                    )
                            if c:
                                disc, slink1, slink2, pas1, pas2 = ability(num, 2, DM, playerIndex, enemyIndex, owner, -1, -1)
                                if disc == '-1': disc = 'You cannot use this ability right now.'
                                embed = discord.Embed(
                                    title = 'Ability',
                                    description = disc,
                                    color = discord.Colour.teal()
                                )

                                if slink1 != '-1': embed.add_field(name='Ability trigger', value = slink1)
                                if slink2 != '-1': embed.add_field(name='Ability trigger', value = slink2)
                                if pas1 != '-1': embed.add_field(name='Passive ability', value = pas1)
                                if pas2 != '-1': embed.add_field(name='Passive ability', value = pas2)

                                ###PASSIVE TRIGGER
                                if DM.duelists[0].g1.ctype != '':
                                    v = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Ability', 2)
                                    if v != '-1':
                                        embed.add_field(name='Passive ability', value = v)
                                if DM.duelists[1].g1.ctype != '':
                                    v = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Ability', 2)
                                    if v != '-1':
                                        embed.add_field(name='Passive ability', value = v)
                                ###END OF PASSIVE TRIGGER
                            await bot.say(embed=embed)

                        result = findLoser(DM) #Check if there is a loser
                        if result != -1:
                            await actOnLoser(result, DM, owner, notowner)
                            
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')



@bot.command(pass_context = True)
async def fuse(ctx, gemAslot = '', gemBslot = ''):
    userid = ctx.message.author.id
    user = ctx.message.author
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!generateteam``.')
            else:
                try:
                    gemAslot = int(gemAslot)
                    gemBslot = int(gemBslot)
                except ValueError:
                    gemAslot = -1
                    gemBslot = -1
                gemA = getGem(TeamList[index], gemAslot)
                gemB = getGem(TeamList[index], gemBslot)
                duelindex = memfindDueltag(TeamList[index].dueltag)

                if duelindex != -1:
                    await bot.whisper('You cannot fuse Gemma while you are in a duel.')
                elif gemAslot == -1 or gemBslot == -1:
                    await bot.whisper('Please specify two Gemma from your team in the command: ``!fuse <Gemma 1 slot number> <Gemma 2 slot number>``')
                elif gemA == -1 or gemB == -1:
                    await bot.whisper('Please specify team slot numbers from 1-3 in the command: ``!fuse <Gemma 1 slot number> <Gemma 2 slot number>``')
                elif TeamList[index].tokens < 5:
                    await bot.whisper('You do not have enough tokens to fuse (costs 5 tokens).')
                elif gemA.id == 'NULL' or gemB.id == 'NULL':
                    await bot.whisper('You cannot choose empty team slots.')
                elif gemAslot == gemBslot:
                    await bot.whisper('You cannot fuse a Gemma with itself.')
                else:
                    global TagList
                    TagList.append([user, '``!fuse``'])  

                    await bot.whisper('Are you sure you want to fuse **' + gemA.name + '** and **'
                    + gemB.name + '**? You cannot reverse this. Type "y" for yes and anything else for no.\n')
                    ans = await bot.wait_for_message(author = user)
                    if ans.content != 'Y' and ans.content != 'y':
                        await bot.whisper('Fuse cancelled.')
                        removeFromTagList(user, '``!upgrade``')
                        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)

                    else:
                        TeamList[index].tokens -= 5
                        new = Gemma()
                        new.personality = random.randint(0, 8)                        
                        new.exp = gemA.exp + gemA.level*10 + gemB.exp + gemB.level*10 
                        if new.exp > TotalExp[8]: new.exp = TotalExp[8]
                        new.alive = True

                        #Fuse first ability
                        ab = [gemA.ability[0], gemB.ability[0]]
                        random.shuffle(ab)
                        new.ability[0] = ab[0]

                        #Generate lv 1 stats
                        points = 4
                        stat = [-1, -1, -1]
                        stat[0] = random.randint(0, points)
                        points -= stat[0]
                        stat[1] = random.randint(0, points)
                        stat[2] = 4 - stat[0] - stat[1]
                        new.attack = stat.pop(random.randint(0, len(stat)-1))
                        new.defence = stat.pop(random.randint(0, len(stat)-1))
                        new.speed = stat[0]

                        while new.exp >= TotalExp[new.level-1] and new.level < 10:
                            new.level += 1
                            atkboost = StatDistribution[new.personality][new.level-2][0] 
                            defboost = StatDistribution[new.personality][new.level-2][1]
                            spdboost = StatDistribution[new.personality][new.level-2][2]
                            
                            new.attack += atkboost
                            new.defence += defboost
                            new.speed += spdboost
                            if new.level == 3:
                                new.ability[2] = ab[1]
                                
                            if new.level == 5:
                                new.maxhp += 1
                                new.hp += 1

                        #Determine type fuse
                        sel = [gemA.type1, gemB.type1]
                        random.shuffle(sel)
                        new.type1 = sel[0]
                        new.type2 = sel[1]
                        while new.type1 == new.type2:
                            new.type2 = random.randint(0, 13)
        
                        new.ctype = CompChart[new.type1, new.type2]

                        if new.ctype != '':
                            new.passive[0] = CompDict[new.ctype]
                            if new.ctype == 'Mystic':
                                new.ability[1] = 2
                                new.ability[3] = 2    
                            elif new.ctype == 'Slime':
                                new.maxhp += 1
                                new.hp += 1
                                new.maxguard -= 1
                                new.guard -= 1
                            elif new.ctype == 'Golem':
                                new.guard += 1
                                new.maxguard += 1

                        #Show it and name it!
                        w = '**' + gemA.name + '** and **' + gemB.name + '** fuse together into a new Gemma!'
                        await bot.whisper(w)
                        new.name = 'Transmuted Gemma'
                        title, disc, ab1, ab2, pas = prepareEmbed(new)
                        embed = makeEmbed(title, disc, ab1, ab2, pas)
                        await bot.whisper(embed=embed)                        
                        c = True
                        while c:
                            c = False
                            await bot.whisper('Give it a name:')
                            ans = await bot.wait_for_message(author = user)
                            for x in ans.content:
                                if ord(x) > 127:
                                    await bot.whisper('Please only use ASCII symbols')
                                    c = True
                            if len(ans.content) > 30:
                                await bot.whisper('You cannot have names with over 30 characters')
                                c = True

                        new.name = ans.content
                        new.id = gemA.id

                        #Assign it to the team and empty the B slot
                        assignTeamSlot(TeamList[index], gemAslot, new)
                        assignTeamSlot(TeamList[index], gemBslot, Gemma())
                        
                        removeFromTagList(user, '``!fuse``')
                        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
                        await bot.whisper(ans.content + ' has been added to your team')
                    
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')


########################################################################################################
#______________________________________________________________________________________________________
#initiative CUT COMMAND? GO INSTEAD     DONE
#go                                     DONE
#attack                                 DONE
#rotate                                 DONE
#ab1                                    DONE
#ab2                                    DONE
#cancelduel                             DONE
#concede                                DONE
#bcs                                    DONE
#pet                                    DONE
#abilities, new old update              DONE
        #ability descriptions           DONE
#XP system                              DONE
#Level up triggers and function         DONE
#Pick levelup rewards in !upgrade       DONE

#Changed passives                       DONE

#duel commands only on server           DONE

#Affection system, now shows in !team   DONE
    #adjusted AP and mood gain          DONE
    #AP and mood now affects XP         DONE

# Make the new gang roles               DONE

#fuse, cost 5, adds xp                  DONE

#buy higher level gemma...

#gang leadrboard, gangboard             DONE

#-----TODO------

#Put a decimal limit when printing numbers: initiative results, aftermath, etc. DONE

#switch from bot say to send_message for duels, send to designated channel  DONE

#AI                                     DONE
#Write the AI                           DONE
#Test AI                                DONE
#Make sure the AI does not get EXP      DONE
#Make sure the AI does not get any gang prompts DONE


#First make the random encounter        DONE
#Make random encounters fitting to your team size and level DONE
#AI dueling, rotate when guard is broken, unless you can kill the opponent  DONE
#Strong attack 100% when you can kill   DONE
#Add prickly thorns to the special abilty check list    DONE

#Make levels visible at duel start  DONE
#then make the elite four   DONE
#   reset if you lose to one of them    DONE              

#change the intro message about gambling warning    DONE
#Make the save file on the right server
#Make the new roles on the right server, add the role IDs to the lists
#Add all the NPCs to the teamlist   
#make promo stuff

#-------------------------------

@bot.command(pass_context = True)
async def rotate(ctx): #Rotates the front three Gemma in your team
    user = ctx.message.author
    userid = user.id
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            else:
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex == -1: #Normal out of combat rotation
                    temp1 = TeamList[index].g1
                    temp2 = TeamList[index].g2 
                    temp3 = TeamList[index].g3
                    
                    TeamList[index].g1 = temp2 
                    TeamList[index].g2 = temp3 
                    TeamList[index].g3 = temp1 

                    await bot.say(TeamList[index].duelistname + '\'s new team order:')
                    await bot.say('``' + TeamList[index].g1.name + '``, ``' + TeamList[index].g2.name + '``, ``' + TeamList[index].g3.name + '``')
                else:
                    DM = DuelmemList[duelindex]
                    if ctx.message.channel.is_private:
                        await bot.whisper('Duel commands can only be used on the Jaegergems server.')    
                    
                    elif DM.phase == 2: #Player picks rotate or attack
                        [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
                        if not DM.duelists[owner].g2.alive and not DM.duelists[owner].g3.alive:
                            await bot.say('All your other Gemma have already fainted.')
                        elif DM.duelists[owner].rotblock == True:
                            await bot.say('You cannot rotate.')
                        else:
                            if DM.turn == owner: #It is your turn
                                embed = rotateTeam(DM, owner)
                                await bot.say(embed=embed)
                                await bot.say('Advance with ``!go``')
                                DM.duelists[owner].rotblock = False
                                DM.duelists[notowner].rotblock = False
                                DM.phase = 0
                            else:
                                await bot.say('It is not your turn.')    
                    
                    elif DM.phase == 4:
                        [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
                        if not DM.duelists[owner].g2.alive and not DM.duelists[owner].g3.alive:
                            await bot.say('All your other Gemma have already fainted.')
                        elif DM.duelists[owner].rotblock == True:
                            await bot.say('You cannot rotate.')
                        else:
                            if DM.duelists[notowner].g1.alive: #Enemy front Gemma is alive
                                if DM.duelists[owner].g1.alive: #Your front Gemma is alive
                                    if DM.turn == owner: #It is your turn                                    
                                        embed = rotateTeam(DM, owner)
                                        await bot.say(embed=embed)
                                        await bot.say('Advance with ``!go``')
                                        DM.duelists[owner].rotblock = False
                                        DM.duelists[notowner].rotblock = False
                                        DM.phase = 0
                                    else: #It is not your turn
                                        await bot.say('It is not your turn')
                                else: #Your front Gemma is NOT alive
                                    if DM.turn == owner: #It is your turn
                                        embed = rotateTeam(DM, owner)
                                        await bot.say(embed=embed)
                                        await bot.say('Advance with ``!go``')
                                        DM.duelists[owner].rotblock = False
                                        DM.duelists[notowner].rotblock = False
                                        DM.phase = 0
                                    else: #It is NOT your turn
                                        embed = rotateTeam(DM, owner)
                                        await bot.say(embed=embed)
                                        await bot.say('Advance with ``!go``')
                                        DM.duelists[owner].rotblock = False
                                        DM.duelists[notowner].rotblock = False
                                        DM.phase = 0
                            else: #Enemy front Gemma is NOT alive
                                if DM.duelists[owner].g1.alive: #Your front Gemma is alive
                                    if DM.turn == owner: #It is your turn
                                        await bot.say('You cannot rotate now.')
                                    else:
                                        await bot.say('It is not your turn')
                                else: #Your front Gemma is NOT alive
                                    embed = rotateTeam(DM, owner)
                                    await bot.say(embed=embed)
                                    await bot.say('Advance with ``!go``')
                                    DM.duelists[owner].rotblock = True
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')



############################################################################################################
############################################################################################################
############################################################################################################


#   ADMIN COMMANDS


############################################################################################################
############################################################################################################
############################################################################################################

@bot.command(pass_context = True)   #Save all storage lists
async def save(ctx):
    #print(TeamList)
    #print(DuelmemList)
    #print(AdminList)
    #print(TimeList)
    #print(TagList)
    userid = ctx.message.author.id
    if userid in AdminList:
        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
        print('Saving!')

@bot.command(pass_context = False)  #Load all storage lists
async def load(ctx):
    userid = ctx.message.author.id
    if userid in AdminList:
        loadlist()
        print('Loading!')

@bot.command(pass_context = True)   #Remove a user
async def purge(ctx, *, target = ''):
    userid = ctx.message.author.id
    user = ctx.message.author
    index = findName(target)
    if userid in AdminList:
        if index == -1:
            await bot.whisper('This user does not have a team')
        elif target == '':
            await bot.whisper('Please specify the target player in the command: ``!purge <duelist name>``')
        else:
            await bot.whisper('Are you sure you want to delete this user\'s team? (y/n)')
            ans = await bot.wait_for_message(author = user)
            if ans.content == 'Y' or ans.content == 'y':
                del TeamList[index]
                await bot.whisper('The team of user ' + target + ' has been deleted')
                savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)

@bot.command(pass_context = True)   #Remove all users
async def purgeall(ctx):
    userid = ctx.message.author.id
    user = ctx.message.author
    if userid in AdminList:
        await bot.whisper('Are you sure you want to delete all teams? If you are, please repeat the following code:')
        code = random.randint(1000, 2000) + random.randint(100, 200) + random.randint(10, 20)
        await bot.whisper(str(code))
        ans = await bot.wait_for_message(author = user)
        if ans.content == str(code):
            del TeamList[:]
            await bot.whisper('The team list has been purged.')
            global maxGID
            maxGID = 0
            global TimeList
            TimeList = []
            global TagList
            TagList = []
            global DuelmemList
            DuelmemList = []
            savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
        else:
            await bot.whisper('Purge aborted')

@bot.command(pass_context = True)
async def renameduelist(ctx, *, target = ''):
    user = ctx.message.author
    userid = user.id
    index = findName(target)
    
    if userid in AdminList:
        if target == '':
            await bot.whisper('Please specify the target player in the command: ``!renameduelist <duelist name>``')
        elif index == -1:
            await bot.whisper('This user does not seem to have a team.')
        else:
            cc = True
            while cc:
                cc = False
                await bot.whisper('Enter a new name: ')
                ansname = await bot.wait_for_message(author = user)
                for x in ansname.content:
                    if ord(x) > 127:
                        await bot.whisper('Please only use ASCII symbols')
                        cc = True
                if len(ansname.content) > 30:
                    await bot.whisper('You cannot have names with over 30 characters')
                    cc = True            
            TeamList[index].duelistname = ansname.content
            await bot.whisper('Their new name is ' + ansname.content)
            savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)

@bot.command(pass_context = True)
async def addadmin(ctx, *, target = ''):
    index = findName(target)
    userid = ctx.message.author.id
    if userid in AdminList:
        if target == '':
            await bot.whisper('Please specify the target player in the command: ``!addadmin <duelist name>``')
        elif index == -1:
            await bot.whisper('This user does not have a team yet.')
        else:
            if TeamList[index].userid in AdminList:
                await bot.whisper('This user is already in the AdminList.')
            else:
                AdminList.append(TeamList[index].userid)
                await bot.whisper('The user ' + str(TeamList[index].discname) + ' has been added to the AdminList')
                savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
            
@bot.command(pass_context = True)
async def removeadmin(ctx, *, target = ''):
    userid = ctx.message.author.id
    if userid in AdminList:
        if target == '':
            await bot.whisper('Please specify the target player in the command: ``!addadmin <duelist name>``')
        else:
            index = findName(target)
            if TeamList[index].userid in AdminList:
                AdminList.remove(TeamList[index].userid)
                await bot.whisper('The user ' + TeamList[index].discname + ' has been removed from the AdminList.')
                savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
            else:
                await bot.whisper('This user is not in the AdminList.')

@bot.command(pass_context = True)
async def listadmin(ctx):
    userid = ctx.message.author.id
    if userid in AdminList:
        w = '**Admin list:\n**'
        for userid in AdminList:
            w += str(TeamList[findTeam(userid)].discname) + '\n'
        await bot.whisper(w)

@bot.command(pass_context = True)
async def stats(ctx):
    userid = ctx.message.author.id
    if userid in AdminList:
        w = 'maxGID: ' + str(maxGID)
        w += '\nTeamList length: ' + str(len(TeamList))
        w += '\nAdminList length: ' + str(len(AdminList))
        w += '\nTimeList length: ' + str(len(TimeList))
        w += '\nTagList length: ' + str(len(TagList))
        w += '\nPause: ' + str(gamepause)
        await bot.whisper(w)

@bot.command(pass_context = True)
async def shutdown(ctx): #Notify all users in a command that they need to finish their commands
    c = []
    userid = ctx.message.author.id
    if userid in AdminList:
        for entry in TagList:
            await bot.send_message(entry[0], 'The bot will soon shut down, please finish the current command ' + entry[1])
            c.append(entry[0].name)
        w = 'The following users where notified:\n'
        for d in c:
            w += str(d) + '\n'
        await bot.whisper(w) 

@bot.command(pass_context = True)
async def pause(ctx): #Pause user commands.
    userid = ctx.message.author.id
    if userid in AdminList:
        global gamepause
        if not gamepause:
            gamepause = True
            await bot.whisper('User commands paused')
        elif gamepause:
            gamepause = False
            await bot.whisper('User commands un-paused')

############################################################################################################
############################################################################################################
############################################################################################################


#   HOPEFULLY TEMPORARY COMMANDS


############################################################################################################
############################################################################################################
############################################################################################################


@bot.command(pass_context = True)
async def gbreak(ctx):
    user = ctx.message.author
    userid = user.id
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif ctx.message.channel.is_private:
                await bot.whisper('Duel commands can only be used on the Jaegergems server.')
            else:
                duelindex = memfindDueltag(TeamList[index].dueltag)
                if duelindex == -1:
                    await bot.whisper('You are currently not in a duel.')
                else:
                    DM = DuelmemList[duelindex]
                    [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
                    DM.duelists[owner].g1.guard = 0
                    DM.duelists[notowner].g1.guard = 0
                    print('BBBBBBBBBBBBBRRRRRRRRRRRRRRREEEEEEEEEEEEEEAAAAAAAAAAAAAAAAAKKKKKKKKKKk')
                    
                    
@bot.command(pass_context = True)
async def ctag(ctx): #TEMP
    userid = ctx.message.author.id
    if userid in AdminList:
        global TagList
        TagList = []

@bot.command(pass_context = True)
async def dtag(ctx): #TEMP
    userid = ctx.message.author.id
    if userid in AdminList:
        global DuelmemList
        DuelmemList = []
        global AItaskList
        for t in AItaskList:
            t.task.cancel()
        ATtaskList = []
        
        for team in TeamList:
            team.opponent = '-1'




@bot.command(pass_context = True)
async def quitall(ctx, num = ''):
    userid = ctx.message.author.id
    if userid in AdminList:
        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
        sys.exit()      

@bot.command(pass_context = True)
async def settoken(ctx, num = ''):
    userid = ctx.message.author.id
    index = findTeam(userid)
    if userid in AdminList:
        TeamList[index].tokens = int(num)

@bot.command(pass_context = True)
async def setmaxgid(ctx, num = ''):
    userid = ctx.message.author.id
    index = findTeam(userid)
    if userid in AdminList:
        global maxGID
        maxGID = 0
        

@bot.command(pass_context = True)
async def setab(ctx, num = ''):
    userid = ctx.message.author.id
    index = findTeam(userid)
    if userid in AdminList:
        try:
            duelindex = memfindDueltag(TeamList[index].dueltag)
            DM = DuelmemList[duelindex]
            owner = memfindTeam(userid, TeamList[index].dueltag)[0]
            gem = DM.duelists[owner].g1
            gem.ability[0] = int(num)
            gem.ability[1] = 1
            w = abilityDict(gem.ability[0], gem.level)
            await bot.say('Switched to: ' + w)
        except:
            pass
"""
@bot.command(pass_context = True)
async def setpa(ctx, num = ''):
    userid = ctx.message.author.id
    index = findTeam(userid)
    duelindex = memfindDueltag(TeamList[index].dueltag)
    owner = memfindTeam(userid, TeamList[index].dueltag)[0]
    gem = DM.duelists[owner].g1
    gem.passive[0] = int(num)

    CD = {0:'Dragon',
            1:'Golem',
            2:'Bug',
            3:'Slime',
            4:'Spirit',
            5:'Puppet',
            6:'Fairy',
            7:'Ghost',
            8:'Dog',
            9:'Angel',
            10:'Cat',
            11:'Demon',
            12:'Mystic',
            13:'Song',
            14:'Digital',
            15:'Trillium',
            16:'Celestial',
            17:'Plague',
            18:'Shadow',
            19:'Bird',
            20:'Elemental',
            21:'Dream',
            22:'Crystal',
            23:'Fish',
            24:'Sea Serpent',
            25:'Merfolk',
            26:'Ice',
            27:'Storm',
            28:'Plant',
            29:'Phoenix',
            30:'Holy',
            31:'Infernal',
            32:'Cloud',
            33:'Explosion',
            34:'Titan',
            35:'Sylph',
            36:'Dryad',
            37:'Undead',
            38:'Monstrosity'} 

    gem.ctype = CD[int(num)]
    w = passiveDict(gem.passive[0], gem.level)
    await bot.say('Switched to: ' + w)
"""


@bot.command(pass_context = True)
async def setexp(ctx, target, num = ''):
    userid = ctx.message.author.id
    index = findName(target)
    if userid in AdminList:
        if index == -1:
            await bot.whisper('This user does not have a team')
        elif target == '':
            await bot.whisper('Please specify the target player in the command: ``!lv <duelist name>``')
        else:    
            TeamList[index].g1.exp = int(num)
            await bot.say('Awarded them EXP')



@bot.command(pass_context = True)
async def info(ctx, target, num = ''):
    userid = ctx.message.author.id
    index = findName(target)
    if userid in AdminList:
        t = TeamList[index]
        print(t.userid)
        print(E4)
        for i, place in enumerate(E4):
            if t.userid in place:
                print('user is in location: ', i)



@bot.command(pass_context = True)
async def lv(ctx, target):
    userid = ctx.message.author.id
    index = findName(target)
    if userid in AdminList:
        if index == -1:
            await bot.whisper('This user does not have a team')
        elif target == '':
            await bot.whisper('Please specify the target player in the command: ``!lv <duelist name>``')
        else:
            w = ''
            gem1 = TeamList[index].g1
            gem2 = TeamList[index].g2
            gem3 = TeamList[index].g3
            gems = [gem1, gem2, gem3]
            nothing = True
            for gem in gems:
                go = True
                while(go):
                    if gem.level < 10:
                        #If you have equal to or above the total exp for next level:
                        if gem.exp >= TotalExp[gem.level-1]:
                            nothing = False
                            gem.level += 1
                            atkboost = StatDistribution[gem.personality][gem.level-2][0] 
                            defboost = StatDistribution[gem.personality][gem.level-2][1]
                            spdboost = StatDistribution[gem.personality][gem.level-2][2]
                            w += '\n**' + gem.name + '** reached **level ' + str(gem.level) + '!**' + '\nAttack: **+' \
                                + str(atkboost) + '**\nDefence: **+' + str(defboost) + '**\nSpeed: **+' + str(spdboost) + '**\n'
                            gem.attack += atkboost
                            gem.defence += defboost
                            gem.speed += spdboost
                            if gem.level == 3:
                                gem.levelup = 1
                                w += 'Use ``!upgrade`` to pick ' + gem.name + '\'s second ability!\n' #2nd ability, pick between 2 or 3 options
                            if gem.level == 5:
                                gem.maxhp += 1
                                gem.hp += 1
                                w += 'Max HP: **+1**\n'
                            if gem.level == 7:
                                if gem.levelup == 1:
                                    gem.levelup = 3
                                else:
                                    gem.levelup = 2
                                w += 'Use ``!upgrade`` to pick a new secondary type for ' + gem.name + ' (optional)\n' #Type switch
                            if gem.level == 10:
                                if gem.levelup == 2:
                                    gem.levelup = 5
                                elif gem.levelup == 3:
                                    gem.levelup = 6
                                else:
                                    gem.levelup = 4
                                w += 'Use ``!upgrade`` to replace one of ' + gem.name + '\'s abilities (optional)\n' #Ability switch, pick between 2 or 3 options, replace 1st or 2nd
                        else:
                            go = False
                    else:
                        go = False
                        gem.exp = TotalExp[8]
            if nothing:
                w = 'No Gemma found that could level up.'
            await bot.say(w)


@bot.command(pass_context = True)
async def unstuck(ctx): #TEMP
    user = ctx.message.author
    c = True
    while c:
        for i, entry in enumerate(TagList):
            if entry[0] == user:
                del TagList[i]
                await bot.say('Unstuck user.')
                

############################################################################################################
############################################################################################################
############################################################################################################


#   Elite 4


############################################################################################################
############################################################################################################
############################################################################################################

#TypeList = ['Beast','Myth','Construct','Organism','Phasma','Sapien','Order',
# 'Chaos','Light','Dark','Wind','Earth','Aqua', 'Flame']

@bot.command(pass_context = True)
async def sivaruz(ctx): #temp
    userid = ctx.message.author.id
    if userid in AdminList:    
        dg1 = Gemma()
        dg1.name = 'Aku'
        dg1.type1 = 1
        dg1.type2 = 7
        dg1.ctype = 'Demon'
        dg1.power = 1
        dg1.attack = 12
        dg1.defence = 7
        dg1.hp = 3         #Hearts/Health
        dg1.maxhp = 3      #Max hearts/Health
        dg1.speed = 3
        dg1.ability = [60, 1, 38, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg1.alive = True
        dg1.personality = 7
        dg1.id = -10
        dg1.passive = [11, 0] #num, counter
        dg1.exp = TotalExp[8]
        dg1.level = 10
        dg1.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg1.maxguard = 2 #Guard maximum
        
        dg2 = Gemma()
        dg2.name = 'Arel'
        dg2.type1 = 1
        dg2.type2 = 6
        dg2.ctype = 'Angel'
        dg2.power = 1
        dg2.attack = 7
        dg2.defence = 12
        dg2.hp = 3         #Hearts/Health
        dg2.maxhp = 3      #Max hearts/Health
        dg2.speed = 3
        dg2.ability = [50, 1, 41, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg2.alive = True
        dg2.personality = 3
        dg2.id = -11
        dg2.passive = [9, 0] #num, counter
        dg2.exp = TotalExp[8]
        dg2.level = 10
        dg2.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg2.maxguard = 2 #Guard maximum

        dg3 = Gemma()
        dg3.name = 'Goraking'
        dg3.type1 = 1
        dg3.type2 = 0
        dg3.ctype = 'Dragon'
        dg3.power = 1      
        dg3.attack = 8
        dg3.defence = 7
        dg3.hp = 3         #Hearts/Health
        dg3.maxhp = 3      #Max hearts/Health
        dg3.speed = 7
        dg3.ability = [22, 1, 61, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg3.alive = True
        dg3.personality = 0
        dg3.id = -12
        dg3.passive = [0, 0] #num, counter
        dg3.exp = TotalExp[8]
        dg3.level = 10
        dg3.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg3.maxguard = 2 #Guard maximum
        
        d = Duelist()

        d.userid = 6
        d.discname = 'Jaegergembot3'
        d.duelistname = 'NPC Champion Sivaruz'
        
        d.g1 = dg1
        d.g2 = dg2
        d.g3 = dg3
        d.bot = True

        d.user = 1
        TeamList.append(d)
        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)


@bot.command(pass_context = True)
async def cosette(ctx): #temp
    userid = ctx.message.author.id
    if userid in AdminList:    
        dg1 = Gemma()
        dg1.name = 'Snapper'
        dg1.type1 = 12
        dg1.type2 = 0
        dg1.ctype = 'Fish'
        dg1.power = 1
        dg1.attack = 5
        dg1.defence = 5
        dg1.hp = 3         #Hearts/Health
        dg1.maxhp = 3      #Max hearts/Health
        dg1.speed = 10
        dg1.ability = [54, 1, 36, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg1.alive = True
        dg1.personality = 6
        dg1.id = -10
        dg1.passive = [23, 0] #num, counter
        dg1.exp = TotalExp[8]
        dg1.level = 9
        dg1.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg1.maxguard = 2 #Guard maximum
        
        dg2 = Gemma()
        dg2.name = 'Orenami'
        dg2.type1 = 12
        dg2.type2 = 1
        dg2.ctype = 'Sea Serpent'
        dg2.power = 1
        dg2.attack = 8
        dg2.defence = 7
        dg2.hp = 3         #Hearts/Health
        dg2.maxhp = 3      #Max hearts/Health
        dg2.speed = 5
        dg2.ability = [60, 1, 53, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg2.alive = True
        dg2.personality = 6
        dg2.id = -11
        dg2.passive = [24, 0] #num, counter
        dg2.exp = TotalExp[8]
        dg2.level = 9
        dg2.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg2.maxguard = 2 #Guard maximum

        dg3 = Gemma()
        dg3.name = 'Sahugi'
        dg3.type1 = 12
        dg3.type2 = 5
        dg3.ctype = 'Merfolk'
        dg3.power = 1      
        dg3.attack = 9
        dg3.defence = 6
        dg3.hp = 3         #Hearts/Health
        dg3.maxhp = 3      #Max hearts/Health
        dg3.speed = 8
        dg3.ability = [25, 1, 16, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg3.alive = True
        dg3.personality = 1
        dg3.id = -12
        dg3.passive = [25, 0] #num, counter
        dg3.exp = TotalExp[8]
        dg3.level = 10
        dg3.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg3.maxguard = 2 #Guard maximum
        
        d = Duelist()

        d.userid = 5
        d.discname = 'Jaegergembot3'
        d.duelistname = 'NPC E4 Cosette'
        
        d.g1 = dg1
        d.g2 = dg2
        d.g3 = dg3
        d.bot = True

        d.user = 1
        TeamList.append(d)
        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)


@bot.command(pass_context = True)
async def gilbert(ctx): #temp
    userid = ctx.message.author.id
    if userid in AdminList:    
        dg1 = Gemma()
        dg1.name = 'Nitrodon'
        dg1.type1 = 13
        dg1.type2 = 10
        dg1.ctype = 'Explosion'
        dg1.power = 1      
        dg1.attack = 7
        dg1.defence = 5
        dg1.hp = 3         #Hearts/Health
        dg1.maxhp = 3      #Max hearts/Health
        dg1.speed = 10
        dg1.ability = [56, 1, 65, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg1.alive = True
        dg1.personality = 2
        dg1.id = -7
        dg1.passive = [33, 0] #num, counter
        dg1.exp = TotalExp[8]
        dg1.level = 9
        dg1.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg1.maxguard = 2 #Guard maximum
        
        dg2 = Gemma()
        dg2.name = 'Torino'
        dg2.type1 = 13
        dg2.type2 = 1
        dg2.ctype = 'Phoenix'
        dg2.power = 1      
        dg2.attack = 4
        dg2.defence = 6
        dg2.hp = 3         #Hearts/Health
        dg2.maxhp = 3      #Max hearts/Health
        dg2.speed = 8
        dg2.ability = [62, 1, 68, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg2.alive = True
        dg2.personality = 6
        dg2.id = -8
        dg2.passive = [29, 0] #num, counter
        dg2.exp = TotalExp[8]
        dg2.level = 8
        dg2.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg2.maxguard = 2 #Guard maximum

        dg3 = Gemma()
        dg3.name = 'Efrila'
        dg3.type1 = 13
        dg3.type2 = 4
        dg3.ctype = 'Elemental'
        dg3.power = 1      
        dg3.attack = 10
        dg3.defence = 7
        dg3.hp = 3         #Hearts/Health
        dg3.maxhp = 3      #Max hearts/Health
        dg3.speed = 3
        dg3.ability = [53, 1, 32, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg3.alive = True
        dg3.personality = 7
        dg3.id = -9
        dg3.passive = [20, 0] #num, counter
        dg3.exp = TotalExp[8]
        dg3.level = 9
        dg3.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg3.maxguard = 2 #Guard maximum
        
        d = Duelist()

        d.userid = 4
        d.discname = 'Jaegergembot3'
        d.duelistname = 'NPC E4 Gilbert'
        
        d.g1 = dg1
        d.g2 = dg2
        d.g3 = dg3
        d.bot = True

        d.user = 1
        TeamList.append(d)
        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
        

@bot.command(pass_context = True)
async def lorasatra(ctx): #temp 
    userid = ctx.message.author.id
    if userid in AdminList:    
        dg1 = Gemma()
        dg1.name = 'Gelloton'
        dg1.type1 = 3
        dg1.type2 = 1
        dg1.ctype = 'Slime'
        dg1.power = 1      
        dg1.attack = 6
        dg1.defence = 10
        dg1.hp = 4         #Hearts/Health
        dg1.maxhp = 4      #Max hearts/Health
        dg1.speed = 2
        dg1.ability = [67, 1, 71, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg1.alive = True
        dg1.personality = 3
        dg1.id = -4
        dg1.passive = [3, 0] #num, counter
        dg1.exp = TotalExp[8]
        dg1.level = 8
        dg1.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg1.maxguard = 2 #Guard maximum
        
        dg2 = Gemma()
        dg2.name = 'Arbonox'
        dg2.type1 = 3
        dg2.type2 = 9
        dg2.ctype = 'Plague'
        dg2.power = 1      
        dg2.attack = 3
        dg2.defence = 3
        dg2.hp = 3         #Hearts/Health
        dg2.maxhp = 3      #Max hearts/Health
        dg2.speed = 10
        dg2.ability = [0, 1, 63, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg2.alive = True
        dg2.personality = 1
        dg2.id = -5
        dg2.passive = [17, 0] #num, counter
        dg2.exp = TotalExp[8]
        dg2.level = 7
        dg2.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg2.maxguard = 2 #Guard maximum

        dg3 = Gemma()
        dg3.name = 'Roslug'
        dg3.type1 = 3
        dg3.type2 = 11
        dg3.ctype = 'Plant'
        dg3.power = 1      
        dg3.attack = 4
        dg3.defence = 12
        dg3.hp = 3         #Hearts/Health
        dg3.maxhp = 3      #Max hearts/Health
        dg3.speed = 2
        dg3.ability = [24, 1, 15, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg3.alive = True
        dg3.personality = 4
        dg3.id = -6
        dg3.passive = [28, 0] #num, counter
        dg3.exp = TotalExp[8]
        dg3.level = 8
        dg3.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg3.maxguard = 2 #Guard maximum
        
        d = Duelist()

        d.userid = 3
        d.discname = 'Jaegergembot3'
        d.duelistname = 'NPC E4 Lorasatra'
        
        d.g1 = dg1
        d.g2 = dg2
        d.g3 = dg3
        d.bot = True

        d.user = 1
        TeamList.append(d)
        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)


@bot.command(pass_context = True)
async def kimi(ctx): #temp 
    userid = ctx.message.author.id
    if userid in AdminList:    
        dg1 = Gemma()
        dg1.name = 'Mardropet'
        dg1.type1 = 4
        dg1.type2 = 2
        dg1.ctype = 'Puppet'
        dg1.power = 1      
        dg1.attack = 7
        dg1.defence = 4
        dg1.hp = 3         #Hearts/Health
        dg1.maxhp = 3      #Max hearts/Health
        dg1.speed = 5
        dg1.ability = [44, 1, 45, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg1.alive = True
        dg1.personality = 8
        dg1.id = -1
        dg1.passive = [5, 0] #num, counter
        dg1.exp = TotalExp[8]
        dg1.level = 7
        dg1.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg1.maxguard = 2 #Guard maximum
        
        dg2 = Gemma()
        dg2.name = 'Capello'
        dg2.type1 = 4
        dg2.type2 = 1
        dg2.ctype = 'Spirit'
        dg2.power = 1      
        dg2.attack = 12
        dg2.defence = 1
        dg2.hp = 3         #Hearts/Health
        dg2.maxhp = 3      #Max hearts/Health
        dg2.speed = 3
        dg2.ability = [42, 1, 44, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg2.alive = True
        dg2.personality = 7
        dg2.id = -2
        dg2.passive = [4, 0] #num, counter
        dg2.exp = TotalExp[8]
        dg2.level = 7
        dg2.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg2.maxguard = 2 #Guard maximum

        dg3 = Gemma()
        dg3.name = 'Blomvall'
        dg3.type1 = 4
        dg3.type2 = 5
        dg3.ctype = 'Ghost'
        dg3.power = 1      
        dg3.attack = 6
        dg3.defence = 6
        dg3.hp = 3         #Hearts/Health
        dg3.maxhp = 3      #Max hearts/Health
        dg3.speed = 4
        dg3.ability = [40, 1, 35, 1] #[ability1 number, ability1 uses, ab2 number, ab2 uses]
        dg3.alive = True
        dg3.personality = 4
        dg3.id = -3
        dg3.passive = [7, 0] #num, counter
        dg3.exp = TotalExp[8]
        dg3.level = 7
        dg3.guard = 2 #Lowers for each successful block. Guard break occurs at g = 0
        dg3.maxguard = 2 #Guard maximum
        
        d = Duelist()

        d.userid = 2
        d.discname = 'Jaegergembot3'
        d.duelistname = 'NPC E4 Kimi'
        
        d.g1 = dg1
        d.g2 = dg2
        d.g3 = dg3
        
        d.bot = True

        d.user = 1
        TeamList.append(d)
        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)

############################################################################################################
############################################################################################################
############################################################################################################


#   AI functions


############################################################################################################
############################################################################################################
############################################################################################################
#['Beast','Myth','Construct','Organism','Phasma','Sapien','Order','Chaos','Light','Dark','Wind','Earth','Aqua', 'Flame']

randomNameList = [
    ['Mongoof', 'Honelk', 'Gwolv', 'Rattnitu', 'Parroke', 'Crocath', 'Slowog', 'Fluffatee', 'Spidott', 'Wolletine'],    #Beast
    ['Galadron', 'Gligalor', 'Hadronox', 'Demodon', 'Manados', 'Llamagi', 'Carnacuda', 'Blabbernock', 'Dinopod'],   #Myth
    ['Basher', 'Coppclaw', 'Ferroc', 'Automalon', 'Leloron', 'Wallareon', 'Voltigator', 'Moltilla', 'Gnook', 'Spibil'],     #Construct
    ['Wittelee', 'Googon', 'Shrool', 'Florfog', 'Dewoyo', 'Swapod', 'Zilder', 'Octopine', 'Quicoon', 'Petalodon'],  #Organism
    ['Whifoo', 'Netshee', 'Spectrox', 'Voonoo', 'Padamonium', 'Ghozelle', 'Payak', 'Phanphant', 'Termime', 'Bamboa'],   #Phasma
    ['Ogun', 'Wemon', 'Quiclin', 'Falonn', 'Elamire', 'Specbil', 'Kinepion', 'Vultair', 'Barracama', 'Raptdon'],    #Sapien
    ['Brie', 'Specodon', 'Mirlorr', 'Sirdoll', 'Ramitar', 'Catesire', 'Jagoss', 'Knisotto', 'Raxthur', 'Leopof'],   #Order
    ['Blasmo', 'Twinner', 'Shifloff', 'Chydra', 'Bealow', 'Butterflux', 'Toazar', 'Fiedine', 'Tucain', 'Goath'],    #Chaos
    ['Arco', 'Lucs', 'Allmon', 'Midoren', 'Jaguarc', 'Magicandor', 'Flingo', 'Staramel', 'Cobray', 'Sparclee'],     #Light
    ['Roper', 'Blooblob', 'Bakoton', 'Umberlund', 'Donkeo', 'Skelepion', 'Tigaid', 'Armaduzz', 'Terroling', 'Sumouse'],     #Dark
    ['Crowl', 'Quirren', 'Heliswan', 'Cejet', 'Quilster', 'Vispark', 'Pegette', 'Vultaring', 'Quingo', 'Ingotter'],     #Wind
    ['Clayba', 'Mudoad', 'Drumler', 'Dungun', 'Iroibou', 'Coppan', 'Crocododo', 'Mountingale', 'Carnuar', 'Crazeroach'],    #Earth
    ['Algaero', 'Doomwhale', 'Shrimper', 'Eelneel', 'Frostrich', 'Pengug', 'Kingray', 'Shelyptus', 'Troutlaw', 'Whortoise'],     #Aqua
    ['Embear', 'Fyrell', 'Copyra', 'Lavoh', 'Armazar', 'Wumber', 'Chimpith', 'Charquito', 'Magmelon', 'Ashking']    #Flame
    ]

def randomGemma(level):
    if level == -1:
        return Gemma()
    else:        
        gem = Gemma()
        global maxGID
        maxGID += 1
        gem.id = maxGID
        gem.level = level
        gem.type1 = random.randint(0, 13)
        gem.type2 = random.randint(0, 13)
        while gem.type1 == gem.type2:    
            gem.type2 = random.randint(0, 13)

        gem.ctype = CompChart[gem.type1, gem.type2]

        if level > 4: 
            gem.maxhp +=1
            gem.hp += 1

        if gem.ctype != '':
            gem.passive[0] = CompDict[gem.ctype]
            if gem.ctype == 'Mystic':
                gem.ability[1] = 2
                gem.ability[3] = 2
            elif gem.ctype == 'Slime':
                gem.maxhp += 1
                gem.hp += 1
                gem.maxguard -= 1
                gem.guard -= 1
            elif gem.ctype == 'Golem':
                gem.guard += 1
                gem.maxguard += 1

        startpoints = 2 + 2*level #4
        points = startpoints
        stat = [-1, -1, -1]
        stat[0] = random.randint(0, points)
        points -= stat[0]
        stat[1] = random.randint(0, points)
        stat[2] = startpoints - stat[0] - stat[1]
        gem.attack = stat.pop(random.randint(0, len(stat)-1))
        gem.defence = stat.pop(random.randint(0, len(stat)-1))
        gem.speed = stat[0]

        gem.ability[0] = random.randint(1, 71) #There are 72 abilities
        if gem.level > 2:
            gem.ability[2] = random.randint(1, 71) #There are 72 abilities

        gem.personality = random.randint(0, 8)
        L = len(randomNameList[gem.type1]) - 1
        gem.name = randomNameList[gem.type1][random.randint(0, L)]
        gem.alive = True
        return gem

def randomEncounter(eindex, level1, level2, level3):
    TeamList[eindex].g1 = randomGemma(level1)
    TeamList[eindex].g2 = randomGemma(level2)
    TeamList[eindex].g3 = randomGemma(level3)
    
def checkab(num, DM, playerIndex, enemyIndex, npcowner, playerowner, phase, ab, yourturn):
    disc = AIability(num, 0, DM, playerIndex, enemyIndex, npcowner, -1, -1)
    if disc == '-1' or disc == 'You cannot use this ability right now.':
        return False
    if DM.duelists[npcowner].g1.ability[ab] == 0:
        return False
    if phase == 0: #Phase 0 don't reduce your speed
        if num == 48 or num == 51 or num == 53:
            return False
    if phase == 2:
        if yourturn: #Your turn don't reduce your attack
            if num == 49 or num == 52 or num == 54:
                return False
        else: #Not your turn don't reduce your defence
            if num == 47 or num == 50 or num == 55:
                return False

    trouble = introuble(playerIndex, enemyIndex, npcowner, playerowner, DM, phase)
    if trouble == 0:
        c = 100 #If you're not in trouble don't bother.
    elif trouble == 1:
        c = 0
    else:
        c = 5
    #More specific ability checks
    if num == 23:
        if yourturn:
            if DM.typemod < 0: #We have a negative typemod and we are attacking
                return False
        else:
            if DM.typemod > 0: #We have a positive typemod and we are defending
                return False
    if num == 24:
        totatk = DM.atkbonus + DM.atkroll
        totdef = DM.defbonus + DM.defroll
        if DM.typemod > 0:
            totatk += DM.typemod
        else:
            totdef -= DM.typemod
        if totatk <= totdef:
            return True
        else:
            return False
    if num == 33:
        atkboon = DM.atkbonus
        if DM.typemod > 0:
            atkboon += DM.typemod
        if (DM.atkroll + atkboon) >= 10:
            return True
        else:
            return False
        
    elif num == 34:
        defboon = DM.defbonus
        if DM.typemod < 0:
            defboon -= DM.typemod
        if (DM.defroll + defboon) >= 10:
            return True
        else:
            return False
    
    elif num == 35:
        atkboon = DM.atkbonus
        if DM.typemod > 0:
            atkboon += DM.typemod
        if (DM.atkroll + atkboon) <= 1:
            return True
        else:
            return False

    elif num == 54:
        if phase == 0:
            c = 30
        if phase == 1:
            return False

    elif num == 55:
        if phase == 0:
            c = 30
        if phase == 1:
            return False

    elif num == 56:
        if phase == 0:
            c = 30
        if phase == 1:
            return False

    elif num == 63:
        if DM.duelists[playerowner].g1.hp == 1 and DM.duelists[npcowner].g1.hp != 1:
            return True
        if DM.duelists[npcowner].g1.hp != 1:
            c = 50
        else:
            return False
        
    elif num == 65:
        if DM.duelists[npcowner].g1.guard == DM.duelists[npcowner].g1.maxguard:
            return False
        elif DM.duelists[npcowner].g1.guard == 0:
            return True
        else:
            c = 50
    r = random.randint(1, 100)
    #print('rolled r: ', r , 'need to be under c: ', c)
    if r < c:
        return False
    else:
        return True


def introuble(playerIndex, enemyIndex, owner, player, DM, phase):
    #Return 0   No we are not in trouble
    #Return 1   Yes we are in trouble
    #Return 2   We are not in phase 1 or 3, keep goin as normal
    if phase == 1:
        p = DM.spdroll + DM.spdbonus
        e = DM.espdroll + DM.espdbonus
        if p >= e:
            if owner == playerIndex: return 0
            else: return 1
        else:
            if owner == playerIndex: return 1
            else: return 0

    elif phase == 3:
        p = DM.atkroll + DM.atkbonus
        e = DM.defroll + DM.defbonus
        if DM.typemod > 0:
            p += DM.typemod
        else:
            e -= DM.typemod
        if p <= e: #Defender is going to win!
            if owner == playerIndex:
                if DM.duelists[enemyIndex].g1.guard == 0:
                    return 0
                else:
                    return 1
            else: 
                return 0
        else: #Attacker is going to win!
            if owner == playerIndex: 
                return 0
            else: 
                return 1
    else: 
        return 2

def checkrotatk(npc, gnpc, gplayer):
    atk = gnpc.type1
    defe = [gplayer.type1, gplayer.type2]
    mod = TypeChart[ atk , defe[0] ] + TypeChart[ atk , defe[1] ] 
    atk = gnpc.type2
    hmod = TypeChart[ atk , defe[0] ] + TypeChart[ atk , defe[1] ] 
    #Positive mod gives attack bonus, negative gives defence bonus
    
    if not gnpc.alive:
        return 'rot'
    elif not gplayer.alive:
        return 'wait'
    elif gplayer.guard < 1 and gplayer.hp <= (gnpc.power+1):
        #Their guard is broken and they die to a heavy attack, only one option
        return 'hat'
    elif gnpc.guard < 1 and (gnpc.power+1) < gplayer.hp:
        #Our guard is broken and we cannot bring them down in one hit, we have to bail
        r = random.randint(0, 100)
        print(npc.duelistname, ' ##### ##### my guard is broken, rolled r: ', r)
        if r < 96 and not npc.rotblock:
            print(npc.duelistname, ' ##### ##### possibly rotate, not rotblocked')
            if (npc.g2.id == 'NULL' or not npc.g2.alive) and (npc.g3.id == 'NULL' or not npc.g3.alive):
                print(npc.duelistname, ' ##### ##### no rotation because g2 id: ', npc.g2.id, ' ', npc.g2.alive, ' g3 id ', npc.g3.id, ' ', npc.g3.alive)
                if hmod > mod:         
                    return 'hat'
                else:
                    return 'lat'
            else:
                print(npc.duelistname, ' ##### ##### rotating time')
                return 'rot'
        else:#if r > 95:
            if hmod > mod:         
                return 'hat'
            else:
                return 'lat'
    elif gplayer.hp == 1:
        #Enemy has 1 hp, a regular attack is enough
        r = random.randint(0, 100)
        if r < 11 and (npc.g2.alive or npc.g3.alive) and not npc.rotblock:
            return 'rot'
        else:#if r > 10:
            if hmod > mod:
                if r < 56: #50/50 chance if heavy has bigger bonus
                    return 'hat'
                else:
                    return 'lat'
            else:
                #If regular attack has bigger bonus and they have 1 hp, regular attack
                return 'lat'
    else:
        r = random.randint(0, 100)
        if r < 6 and not (not npc.g2.alive and not npc.g3.alive) and not npc.rotblock:
            return 'rot'
        elif r > 5:
            if hmod > mod:
                if r < 47: #50/50 chance if heavy has bigger bonus
                    return 'lat'
                else:
                    return 'hat'
            else:
                if r < 66: #70/30 chance if heavy has bigger bonus
                    return 'lat'
                else:
                    return 'hat'
            

def findAItask(dueltag):
    temp = -1
    for i in range(0, len(AItaskList)):
        if AItaskList[i].dueltag == dueltag: 
            temp = i
            break
    return temp

def AIability(num, abIndex, DM, playerIndex, enemyIndex, owner, abilityListIndex, abilityListElement):
    w = '-1' #We should never return this, if it does happen something is wrong
    
    if owner == 0:
        notowner = 1
    else:
        notowner = 0

    #Accessing the Gemma objects
    gowner = DM.duelists[owner].g1
    gnotowner = DM.duelists[notowner].g1

    if num == 0:
        if abilityListIndex == -1: #This should not trigger normally ever 
            #'[-] Null Aura: Nullify your opponent\'s next ability activation.'
            w = '**>>** '
    elif num == 1:
        #'[I] Sprint: Add +3 to your speed roll'
        if DM.phase == 1: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 2:
        #'[I] Feather Weight: Reroll your speed roll'
        if DM.phase == 1:
            if playerIndex == owner:
                w = '**>>** '
            else:
                w = '**>>** '
        else: 
            w = 'You cannot use this ability right now.'

    elif num == 3:
        #'[I] Slime Trail: Reroll your opponent\'s speed roll'
        if DM.phase == 1:
            if playerIndex != owner:
                w = '**>>** '
            else:
                w = '**>>** '
        else: 
            w = 'You cannot use this ability right now.'

    elif num == 4:
        #'[I] Shadow shroud: Rotate your Gemma'
        if DM.phase == 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 5:
        #'[I] Tentacles: Rotate your opponent\'s Gemma'
        if DM.phase == 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 6:
        #'[I] Hallucination field: Rotate both your and your opponent\'s Gemma'
        if DM.phase == 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 7:
        #'[I] Cheap shot: Reduce your opponent\'s guard by 1'
        if DM.phase == 1 and gnotowner.guard > 0:
            gnotowner.guard -= 1
            if gnotowner.guard <= 0:
                gnotowner.guard = 0
                w = '**>>** '
            else:
                w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 8:
        #'[I] Overclocked: Add +3 to your speed roll'
        if DM.phase == 1: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** ' 
        else:
            w = 'You cannot use this ability right now.'

    elif num == 9:
        #'[I] Graceful Step: Reroll your speed roll'
        if DM.phase == 1:
            if playerIndex == owner:
                w = '**>>** '
            else:
                w = '**>>** '
        else: 
            w = 'You cannot use this ability right now.'

    elif num == 10:
        #'[I] Balance Disruptor: Reroll your opponent\'s speed roll'
        if DM.phase == 1:
            if playerIndex != owner:
                w = '**>>** '
            else:
                w = '**>>** '
        else: 
            w = 'You cannot use this ability right now.'

    elif num == 11:
        #'[I] Translocator: Rotate your Gemma'
        if DM.phase == 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 12:
        #'[I] Roundhouse Kick: Rotate your opponent\'s Gemma'
        if DM.phase == 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 13:
        #'[I] Ion Storm: Rotate both your and your opponent\'s Gemma'
        if DM.phase == 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 14:
        #'[B] Thermal Vision: Add +3 to your attack roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 15:
        #'[B] Hard Shell: Add +3 to your defence roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 16:
        #'[B] Many Limbs: Reroll your attack roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 17:
        #'[B] Heavy Weight: Reroll your defence roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 18:
        #'[B] Slippery Scales: Reroll your opponent\'s attack roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 19:
        #'[B] Corrosive Touch: Reroll your opponent\'s defence roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 20:
        #'[B] Elemental Affinity: Double the type modifier for this attack'
        if DM.phase == 3:
            w = '**>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 21:
        #[B] Withdraw: Add +2 to your defence roll for each guard you have
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
        
    elif num == 22:
        #[B] Shell bash: Add +2 to your attack roll for each guard you have
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
        
    elif num == 23:
        #'[B] Vacuum Aura: Ignore the type modifier for this attack'
        if DM.phase == 3:
            w = '**>** '
        else:
            w = 'You cannot use this ability right now.'


    elif num == 24:
        #'[B] Prickly Thorns: By the end of this attack, if you defend successfully your opponent takes 1 damage.'
        if DM.phase == 3 and enemyIndex == owner and abilityListIndex == -1:
            w = '**>>** '
        else:
            if abilityListIndex == -1:
                w = 'You cannot use this ability right now.'
            else:
                w = '-1'

    elif num == 25:
        #'[B] Heroic Grit: If this is your last Gemma, add +5 to your defence roll.'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            if (not DM.duelists[owner].g2.alive and not DM.duelists[owner].g3.alive):
                w = '**>>** '
            else:
                w = 'You cannot use this ability right now.'
        else:
            w = 'You cannot use this ability right now.'

    elif num == 26:
        #'[B] Lone Wolf: If this is your last Gemma, add +5 to your attack roll.'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            if (not DM.duelists[owner].g2.alive and not DM.duelists[owner].g3.alive):
                w = '**>>** '
            else:
                w = 'You cannot use this ability right now.'
        else:
            w = 'You cannot use this ability right now.'

    elif num == 27:
        #'[B] Power Surge: Add +3 to your attack roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 28:
        #'[B] Mental Shroud: Add +3 to your defence roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 29:
        #'[B] Tail Whip: Reroll your attack roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 30:
        #'[B] Outer Shell: Reroll your defence roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 31:
        #'[B] Mirage: Reroll your opponent\'s attack roll'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 32:
        #'[B] Armor Piercer: Reroll your opponent\'s defence roll'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
    
    elif num == 33:
        #'[B] Giant Slayer: If your opponent has a total attack of 10 or more, they take 2 damage after the attack'
        if DM.phase == 3 and enemyIndex == owner and abilityListIndex == -1:
            w = '**>>** '
        else:
            if abilityListIndex == -1:
                w = 'You cannot use this ability right now.'
            else:
                w = '-1'

    elif num == 34:
        #'[B] Bunker Buster: If your opponent has a total defence of 10 or more, they take 2 damage after the attack.
        if DM.phase == 3 and playerIndex == owner and abilityListIndex == -1:
            w = '**>>** '
        else:
            if abilityListIndex == -1:
                w = 'You cannot use this ability right now.'
            else:
                w = '-1'

    elif num == 35:
        #'[B] Predatory Reflexes: If your opponent has a total attack of 1 or less, they take 2 damage after the attack'
        if DM.phase == 3 and enemyIndex == owner and abilityListIndex == -1:
            w = '**>>** '
        else:
            if abilityListIndex == -1:
                w = 'You cannot use this ability right now.'
            else:
                w = '-1'

    elif num == 36:
        #'[B] Swift Strike: Reroll your attack roll with your speed dice'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 37:
        #'[B] Body Slam: Reroll your attack roll with your defence dice'
        if DM.phase == 3 and playerIndex == owner: #Phase 3 and your turn, i.e. you are the attacker.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 38:
        #'[B] Forceful Parry: Reroll your defence roll with your attack dice'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
    
    elif num == 39:
        #'[B] Combat Roll: Reroll your defence roll with your speed dice'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 40:
        #'[B] Nightmare Visage: Reduce your opponent\'s total attack by 3'
        if DM.phase == 3 and enemyIndex == owner: #Phase 3 and not your turn, i.e. you are the defender.
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 41:
        #'[B] Reckless lunge: Add +5 to your attack roll, reduce your guard by 1'
        if DM.phase == 3 and playerIndex == owner and gowner.guard > 0:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 42:
        #'[-] Soul link: The next damage you take is transferred to your next living Gemma.'
        if DM.duelists[owner].g2.alive or DM.duelists[owner].g3.alive and abilityListIndex == -1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 43:
        #'[-] Rejuvinate: Restore 1 hp to the next living Gemma in your team'        
        if DM.duelists[owner].g2.alive and \
                DM.duelists[owner].g2.hp < DM.duelists[owner].g2.maxhp:
            w = '**>>** '
        elif DM.duelists[owner].g3.alive and \
                DM.duelists[owner].g2.hp < DM.duelists[owner].g2.maxhp:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
        
    elif num == 44:
        #'[-] Disable: Downgrade your opponent\'s attack dice by 2 tiers'
        w = '**>>** '
    elif num == 45:
        #'[-] Pressure Point: Downgrade your opponent\'s defence dice by 2 tiers.'
        w = '**>>** '
    elif num == 46:
        #'[-] Impair: Downgrade your opponent\'s speed dice by 2 tiers.'
        w = '**>>** '
    elif num == 47:
        #'[-] Optimize Bloodlust: Upgrade your attack dice by 4 tiers, downgrade your defence and speed dice by 2 tier.'
        w = '**>>** '
    elif num == 48:
        #'[-] Optimize Instincts: Upgrade your defence dice by 4 tiers, downgrade your speed and attack dice by 2 tiers.'
        w = '**>>** '
    elif num == 49:
        #'[-] Optimize Reflexes: Upgrade your speed dice by 4 tiers, downgrade your attack and defence dice by 2 tier.'
        w = '**>>** '
    elif num == 50:
        #'[-] Berserk: Upgrade your attack dice by 3 tiers, downgrade your defence dice by 2 tiers.'
        w = '**>>** '
    elif num == 51:
        #'[-] Compose: Upgrade your attack dice by 3 tiers, downgrade your speed dice by 2 tiers.'
        w = '**>>** '
    elif num == 52:
        #'[-] Fortify: Upgrade your defence dice by 3 tiers, downgrade your attack dice by 2 tiers.'
        w = '**>>** '
    elif num == 53:
        #'[-] Entrench: Upgrade your defence dice by 3 tiers, downgrade your speed dice by 2 tiers.'
        w = '**>>** '
    elif num == 54:
        #'[-] Accelerate: Upgrade your speed dice by 3 tiers, downgrade your attack dice by 2 tiers.'
        w = '**>>** '
    elif num == 55:
        #'[-] Shed Skin: Upgrade your speed dice by 3 tiers, downgrade your defence dice by 2 tiers.'
        w = '**>>** '
    elif num == 56:
        #'[-] Munch: Upgrade your attack, defence and speed dice by 3 tiers, your next Gemma faints'
        if DM.duelists[owner].g2.alive:
            w = '**>>** '
        elif DM.duelists[owner].g3.alive:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 57:
        #'[-] Martial Exchange: Switch attack and defence dice with your next Gemma'
        if DM.duelists[owner].g2.id != 'NULL':
            w = '**>>** '
        elif DM.duelists[owner].g3.id != 'NULL':
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
        
    elif num == 58:
        #'[-] Feral Exchange: Switch speed and attack dice with your next Gemma'
        if DM.duelists[owner].g2.id != 'NULL':
            w = '**>>** '
        elif DM.duelists[owner].g3.id != 'NULL':
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 59:
        #'[-] Conscious Exchange: Switch defence and speed dice with your next Gemma'
        if DM.duelists[owner].g2.id != 'NULL':
            w = '**>>** '
        elif DM.duelists[owner].g3.id != 'NULL':
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
    
    elif num == 60:
        #[-] Regenerate: Restore 1 hp and 1 guard'
        if gowner.hp < gowner.maxhp or gowner.guard < gowner.maxguard:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 61:
        #'[I] Crystal Membrane: Downgrade your defence dice by 4 tiers, increase your current and maximum hp by 2'
        if DM.phase == 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 62:
        #[B] Life rite: Sacrifice 1 hp (and surviving), restore 2 hp to the next living Gemma in your team
        if DM.phase == 3 and DM.duelists[owner].g2.alive and DM.duelists[owner].g2.hp < DM.duelists[owner].g2.maxhp \
                and gowner.hp > 1:
            w = '**>>** '

        elif DM.phase == 3 and DM.duelists[owner].g3.alive and DM.duelists[owner].g3.hp < DM.duelists[owner].g3.maxhp \
                and gowner.hp > 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
    
    elif num == 63:
        #[A] Necrotic wave: Sacrifice 1 hp, deal 1 hp to your opponent
        if DM.phase == 4 and gowner.alive:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 64:
        #'[I] Taunting Demeanour: The opposing Gemma cannot rotate out until you are defeated or rotate out.'
        if DM.phase == 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 65:
        #'[-] Refocus: Fully restore your guard'
        if gowner.guard < gowner.maxguard:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
    
    elif num == 66:
        #'[I] Pulsar wave: Reduce your opponent\'s power by 1 for their next attack'
        #downgrade power, it disappears at the next phase 1 or phase 4
        if DM.phase == 1 and abilityListIndex == -1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 67:
        #'[I] Close combat: Reduce your and your opponent\'s guard by 2'
        if DM.phase == 1:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 68:
        #'[I] Unstable flare: Add +1 power to your next attack, reduce your guard by 1
        if DM.phase == 1 and abilityListIndex == -1 and gowner.guard > 0:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'

    elif num == 69:
        #'[-] Shuffle: Switch the team order of your 2nd and 3rd Gemma'
        w = '**>>** '
        
    elif num == 70:
        #'[-] Disorganize: Swith the team order of the opposing team\'s 2nd and 3rd Gemma'
        w = '**>>** '
    
    elif num == 71:
        #'[B] Life sap: Restore 2 hp, sacrifice 1 hp from the next Gemma in your team'
        if DM.phase == 3 and gowner.hp < gowner.maxhp and DM.duelists[owner].g2.alive:
            w = '**>>** '
        elif DM.phase == 3 and gowner.hp < gowner.maxhp and DM.duelists[owner].g3.alive:
            w = '**>>** '
        else:
            w = 'You cannot use this ability right now.'
    
    else:
        w = '-1'
        
    return w


############################################################################################################
############################################################################################################
############################################################################################################


#   AI commands and tasks


############################################################################################################
############################################################################################################
############################################################################################################


async def AIgo(channel, npc, DM):
    userid = npc.userid
    index = findTeam(userid)

    if not gamepause:
        if DM.phase == 0:
            [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
            if not DM.duelists[notowner].gotrigger: #Enemy team have not used !go yet
                DM.duelists[owner].gotrigger = True #Set your !go trigger to True
            else: #Enemy team has used !go            
                #owner and notowner can be 0 or 1, it is the slot in Duelmem.duelists
                DM.turn = owner
                playerIndex = DM.turn 
                enemyIndex = -1 #temporary just to define it
                if playerIndex == 0:
                    enemyIndex = 1
                else:
                    enemyIndex = 0
                
                #New initiative, clear out last initiative's rolls and bonuses
                DM.spdroll = 0
                DM.espdroll = 0
                DM.spdbonus = 0
                DM.espdbonus = 0

                embed = rollInitiative(DM, playerIndex, enemyIndex) 
                await bot.send_message(channel, embed=embed)
                await bot.send_message(channel, 'Advance with ``!go``')
                #Whoever uses !initiative get's the turn. HOWEVER, this does not affect any ability. It only tells us their speed is stored in spdroll.
                
                DM.turn = owner

                #Clear go trigger
                DM.duelists[owner].gotrigger = False
                DM.duelists[notowner].gotrigger = False

        elif DM.phase == 1:
            [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
            if not DM.duelists[notowner].gotrigger: #Enemy team have not used !go yet
                DM.duelists[owner].gotrigger = True #Set your !go trigger to True
            else: #Enemy team has used !go
                playerIndex = DM.turn
                enemyIndex = -1 #temporary just to define it
                if playerIndex == 0:
                    enemyIndex = 1
                else:
                    enemyIndex = 0

                speed = DM.spdroll
                espeed = DM.espdroll
                spdbonus = DM.spdbonus
                espdbonus = DM.espdbonus

                espeed = espeed + espdbonus
                speed = speed + spdbonus

                if speed > espeed:
                    disc = DM.duelists[playerIndex].g1.name + ': **' + str(speed) + '**\n' \
                        + DM.duelists[enemyIndex].g1.name + ': **' + str(espeed) + '**\n\n' \
                        + 'Duelist **' + DM.duelists[playerIndex].duelistname + '** has the turn!'
                    embed = discord.Embed(
                        title = 'Initiative results',
                        description = disc,
                        color = discord.Colour.gold()
                    )
                    await bot.send_message(channel, embed=embed)
                    DM.turn = playerIndex
                    DM.phase = 2

                elif speed < espeed: 
                    disc = DM.duelists[playerIndex].g1.name + ': **' + str(speed) + '**\n' \
                        + DM.duelists[enemyIndex].g1.name + ': **' + str(espeed) + '**\n\n' \
                        + 'Duelist **' + DM.duelists[enemyIndex].duelistname + '** has the turn!'
                    embed = discord.Embed(
                        title = 'Initiative results',
                        description = disc,
                        color = discord.Colour.gold()
                    )
                    await bot.send_message(channel, embed=embed)
                    DM.turn = enemyIndex
                    DM.phase = 2

                else:
                    DM.spdbonus = 0
                    DM.espdbonus = 0
                    


                    disc = DM.duelists[playerIndex].g1.name + ': **' + str(speed) + '**\n' \
                            + DM.duelists[enemyIndex].g1.name + ': **' + str(espeed) + '**\n'

                    r = random.randint(0, 1)
                    if r == 0:
                        DM.turn = enemyIndex
                        disc += '\n**TIE** - The turn is randomly assigned to duelist **' + DM.duelists[enemyIndex].duelistname + '**!'
                    else:
                        DM.turn = playerIndex
                        disc += '\n**TIE** - The turn is randomly assigned to duelist **' + DM.duelists[playerIndex].duelistname + '**!'
                    
                    embed = discord.Embed(
                        title = 'Initiative results',
                        description = disc,
                        color = discord.Colour.gold()
                    )                       
                    await bot.send_message(channel, embed=embed)
                    DM.phase = 2

                #Clear go trigger
                DM.duelists[owner].gotrigger = False
                DM.duelists[notowner].gotrigger = False

        elif DM.phase == 3:
            [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
            if not DM.duelists[notowner].gotrigger: #Enemy team have not used !go yet
                DM.duelists[owner].gotrigger = True #Set your !go trigger to True
            else: #Enemy team has used !go
                atkIndex = DM.turn #They who has the turn, is the attacker
                defIndex = -1 #Temporary just to define it
                if atkIndex == 0:
                    defIndex = 1
                else:
                    defIndex = 0

                playerIndex = atkIndex
                enemyIndex = defIndex

                attack = DM.atkroll
                defence = DM.defroll
                typemod = DM.typemod
                atkbonus = DM.atkbonus
                defbonus = DM.defbonus
                atkpower = DM.atkpower
                
                if typemod < 0:
                    defence = defence - typemod
                elif typemod > 0:
                    attack = attack + typemod
                    
                attack = attack + atkbonus
                defence = defence + defbonus

                disc = 'Total attack for ' + DM.duelists[atkIndex].g1.name + ': **' \
                + str(attack) + '**' + '\nTotal defence for ' + DM.duelists[defIndex].g1.name \
                + ': **' + str(defence) + '**'

                #Auto hit if guardbreak
                if DM.duelists[defIndex].g1.guard == 0:
                    disc += '\n\n:diamond_shape_with_a_dot_inside: **Guard Break - Defence is reduced by ' + str(GuardBreakMod[DM.duelists[defIndex].g1.level-1]) + '** :diamond_shape_with_a_dot_inside:'

                slink = '-1'
                vdmg1 = '-1'
                vdmg2 = '-1'
                if defence < attack:
                    DM.duelists[defIndex].g1.hp -= atkpower 
                    
                    slink = soulink_check(DM, DM.duelists[defIndex].g1.id, atkpower)

                    ###PASSIVE TRIGGER
                    if DM.duelists[0].g1.ctype != '':
                        vdmg1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
                    if DM.duelists[1].g1.ctype != '':
                        vdmg2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
                    ###END OF PASSIVE TRIGGER

                    if DM.duelists[defIndex].g1.hp <= 0:
                        disc += '\n\n**' + DM.duelists[defIndex].g1.name + '** :skull: **faints!**'
                        DM.duelists[defIndex].g1.alive = False
                        awardAP(DM, defIndex, 2)
                        DM.duelists[defIndex].rotblock = False #You should always be able to rotate out when dead
                        #Award XP, check marker 4 for a takedown
                        awardXP(DM, atkIndex, 4, DM.duelists[atkIndex].g1.level, DM.duelists[defIndex].g1.level)
                    else:
                        hpbar = ''
                        if DM.duelists[defIndex].g1.hp <= 0: hpbar += ':skull:'
                        else:
                            for i in range(0, DM.duelists[defIndex].g1.hp): hpbar += ':heart:'
                            for i in range(0, DM.duelists[defIndex].g1.maxhp - DM.duelists[defIndex].g1.hp): hpbar += ':black_heart:'
                            for i in range(0, DM.duelists[defIndex].g1.guard): hpbar += ':shield:'
                        disc += '\n\n**' + DM.duelists[defIndex].g1.name + '** - ' + hpbar + ' **survives the attack!**'

                        #Award XP, check marker 1 for surviving an attack
                        awardXP(DM, defIndex, 1, DM.duelists[defIndex].g1.level, DM.duelists[atkIndex].g1.level)

                else: #defence >= attack
                    DM.duelists[defIndex].g1.guard -= 1
                    if DM.duelists[defIndex].g1.guard <= 0:
                        DM.duelists[defIndex].g1.guard = 0
                        disc += '\n\n:diamond_shape_with_a_dot_inside: **Guard Break** :diamond_shape_with_a_dot_inside:'
                    
                    hpbar = ''
                    if DM.duelists[defIndex].g1.hp <= 0: hpbar += ':skull:'
                    else:
                        for i in range(0, DM.duelists[defIndex].g1.hp): hpbar += ':heart:'
                        for i in range(0, DM.duelists[defIndex].g1.maxhp - DM.duelists[defIndex].g1.hp): hpbar += ':black_heart:'
                        for i in range(0, DM.duelists[defIndex].g1.guard): hpbar += ':shield:'
                    disc += '\n\n**' + DM.duelists[defIndex].g1.name + '** - ' + hpbar + ' **survives the attack!**'
                    
                    
                    #Award XP, check marker 1 for surviving an attack
                    awardXP(DM, defIndex, 1, DM.duelists[defIndex].g1.level, DM.duelists[atkIndex].g1.level)

                embed = discord.Embed(
                    title = 'Aftermath',
                    description = disc,
                    color = discord.Colour.red()
                )

                if slink != '-1': embed.add_field(name='Ability trigger', value = slink)
                if vdmg1 != '-1': embed.add_field(name='Passive ability', value = vdmg1)
                if vdmg2 != '-1': embed.add_field(name='Passive ability', value = vdmg2)
                    
                DM.phase = 4 #Phase 4

                #Sorting abilityList by num before the search. This is to enforce priority, low number abilities are at the top of the
                #abilityList, so they activate first. 
                
                DM.abilityList = sorted(DM.abilityList, key = getKey)
                
                #We loop through this one since abilityList may get shorter when abilities trigger and remove themselves.
                #This deep copy will be static throughout the loop.
                loopabilityList = copy.copy(DM.abilityList)

                for i in range(0, len(loopabilityList)): 
                    w, loop_slink1, loop_slink2, loop_pas1, loop_pas2 = ability(loopabilityList[i][0], '-1', DM, atkIndex, defIndex, owner, i, loopabilityList[i])
                    #We send abIndex '-1', because we should never use abIndex for triggers. If we go, we'll get an error.
                    if w != '-1': embed.add_field(name='Ability trigger', value = w)
                    if loop_slink1 != '-1': embed.add_field(name='Ability trigger', value = loop_slink1)
                    if loop_slink2 != '-1': embed.add_field(name='Ability trigger', value = loop_slink2)
                    if loop_pas1 != '-1': embed.add_field(name='Passive ability', value = loop_pas1)
                    if loop_pas2 != '-1': embed.add_field(name='Passive ability', value = loop_pas2)

                plague_slink = '-1'
                plague_vdmg1 = '-1'
                plague_vdmg2 = '-1'
                #PASSIVE TRIGGER LIST
                for entry in DM.passiveList:
                    if entry[0] == 17: #Plague passive
                        if entry[2] < 4:
                            entry[2] += 1
                        elif entry[2] == 4:
                            gem = findGemIDduel(DM, entry[1])
                            gem.hp -= 2
                            if gem.hp <= 0: 
                                gem.alive = False
                                if DM.duelists[0].g1.id == gem.id:
                                    DM.duelists[0].rotblock = False #You should always be able to rotate out when dead
                                elif DM.duelists[1].g1.id == gem.id:
                                    DM.duelists[1].rotblock = False #You should always be able to rotate out when dead
                                v = '*>> Plague: ' + gem.name + ' takes 2 damage from the plague curse! ' + gem.name + '* :skull: *faints!*'
                            else:
                                v = '*>> Plague: ' + gem.name + ' takes 2 damage from the plague curse!*'
                            embed.add_field(name='Passive ability', value = v)
                            DM.passiveList.remove(entry)
                            
                            plague_slink = soulink_check(DM, gem.id, atkpower)

                            ###PASSIVE TRIGGER
                            if DM.duelists[0].g1.ctype != '':
                                plague_vdmg1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Dmg', -1)
                            if DM.duelists[1].g1.ctype != '':
                                plague_vdmg2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Dmg', -1)
                            ###END OF PASSIVE TRIGGER
                        
                    if entry[0] == 29: #Phoenix passive
                        if entry[2] < 6:
                            entry[2] += 1
                        elif entry[2] == 6:
                            gem = findGemIDduel(DM, entry[1])
                            gem.alive = True
                            gem.hp = 1
                            DM.passiveList.remove(entry)
                            v = '*>> Phoenix: ' + gem.name + ' rises from the ashes!*'
                            embed.add_field(name='Passive ability', value = v)
                #END OF PASSIVE TRIGGER LIST

                ###PASSIVE TRIGGER
                if DM.duelists[0].g1.ctype != '':
                    v = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Go', -1)
                    if v != '-1':
                        embed.add_field(name='Passive ability', value = v)
                if DM.duelists[1].g1.ctype != '':
                    v = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Go', -1)
                    if v != '-1':
                        embed.add_field(name='Passive ability', value = v)
                ###END OF PASSIVE TRIGGER

                if plague_slink != '-1': embed.add_field(name='Ability trigger', value = plague_slink)
                if plague_vdmg1 != '-1': embed.add_field(name='Passive ability', value = plague_vdmg1)
                if plague_vdmg2 != '-1': embed.add_field(name='Passive ability', value = plague_vdmg2)
                
                await bot.send_message(channel, embed=embed)
                    
                result = findLoser(DM) #Check if there is a loser
                if result != -1:
                    
                    await actOnLoser(result, DM, owner, notowner)
                    
                else:
                    DM.turn = defIndex #Assign turn to the defender

                    if DM.duelists[atkIndex].g1.alive and not DM.duelists[defIndex].g1.alive:
                        await bot.send_message(channel, 'Waiting for duelist **' + DM.duelists[defIndex].duelistname + '** to rotate Gemma.')
                    elif DM.duelists[atkIndex].g1.alive and DM.duelists[defIndex].g1.alive:
                        await bot.send_message(channel, 'Duelist **' + DM.duelists[defIndex].duelistname + '** has the turn!')
                    elif not DM.duelists[atkIndex].g1.alive and DM.duelists[defIndex].g1.alive:
                        await bot.send_message(channel, 'Waiting for duelist **' + DM.duelists[atkIndex].duelistname + '** to rotate Gemma.')
                    else: #attacker and defender dead
                        await bot.send_message(channel, 'Waiting for both duelists to rotate Gemma')
                    
                    #Clear !go trigger
                    DM.duelists[owner].gotrigger = False
                    DM.duelists[notowner].gotrigger = False

async def AIrotate(channel, npc, DM):
    userid = npc.userid
    index = findTeam(userid)

    if not gamepause:
        if DM.phase == 2: #Player picks rotate or attack
            [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
            if not DM.duelists[owner].g2.alive and not DM.duelists[owner].g3.alive:
                await bot.send_message(channel, 'All your other Gemma have already fainted.')
            elif DM.duelists[owner].rotblock == True:
                await bot.send_message(channel, 'You cannot rotate.')
            else:
                if DM.turn == owner: #It is your turn
                    embed = rotateTeam(DM, owner)
                    await bot.send_message(channel, embed=embed)
                    await bot.send_message(channel, 'Advance with ``!go``')
                    DM.duelists[owner].rotblock = False
                    DM.duelists[notowner].rotblock = False
                    DM.phase = 0
                else:
                    await bot.send_message(channel, 'It is not your turn.')    
        
        elif DM.phase == 4:
            [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
            if not DM.duelists[owner].g2.alive and not DM.duelists[owner].g3.alive:
                await bot.send_message(channel, 'All your other Gemma have already fainted.')
            elif DM.duelists[owner].rotblock == True:
                await bot.send_message(channel, 'You cannot rotate.')
            else:
                if DM.duelists[notowner].g1.alive: #Enemy front Gemma is alive
                    if DM.duelists[owner].g1.alive: #Your front Gemma is alive
                        if DM.turn == owner: #It is your turn                                    
                            embed = rotateTeam(DM, owner)
                            await bot.send_message(channel, embed=embed)
                            await bot.send_message(channel, 'Advance with ``!go``')
                            DM.duelists[owner].rotblock = False
                            DM.duelists[notowner].rotblock = False
                            DM.phase = 0
                        else: #It is not your turn
                            await bot.send_message(channel, 'It is not your turn')
                    else: #Your front Gemma is NOT alive
                        if DM.turn == owner: #It is your turn
                            embed = rotateTeam(DM, owner)
                            await bot.send_message(channel, embed=embed)
                            await bot.send_message(channel, 'Advance with ``!go``')
                            DM.duelists[owner].rotblock = False
                            DM.duelists[notowner].rotblock = False
                            DM.phase = 0
                        else: #It is NOT your turn
                            embed = rotateTeam(DM, owner)
                            await bot.send_message(channel, embed=embed)
                            await bot.send_message(channel, 'Advance with ``!go``')
                            DM.duelists[owner].rotblock = False
                            DM.duelists[notowner].rotblock = False
                            DM.phase = 0
                else: #Enemy front Gemma is NOT alive
                    if DM.duelists[owner].g1.alive: #Your front Gemma is alive
                        if DM.turn == owner: #It is your turn
                            await bot.send_message(channel, 'You cannot rotate now.')
                        else:
                            await bot.send_message(channel, 'It is not your turn')
                    else: #Your front Gemma is NOT alive
                        embed = rotateTeam(DM, owner)
                        await bot.send_message(channel, embed=embed)
                        await bot.send_message(channel, 'Advance with ``!go``')
                        DM.duelists[owner].rotblock = True


async def AIattack(channel, npc, DM):
    userid = npc.userid
    index = findTeam(userid)

    if not gamepause:
        if DM.phase != 2 and DM.phase != 4:
            pass #To stop it saying "not your turn" when it is the wrong phase    
        elif DM.phase == 2 or DM.phase == 4:  
            [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
            if DM.turn != owner:
                await bot.send_message(channel, 'It is not your turn.')
            elif not DM.duelists[owner].g1.alive:
                await bot.send_message(channel, 'You cannot attack with a defeated Gemma.')
            elif not DM.duelists[notowner].g1.alive:
                await bot.send_message(channel, 'You cannot attack, the opposing Gemma is defeated.')
            else:
                #New attack, clear out last attack's rolls and bonuses
                DM.atkroll = 0
                DM.defroll = 0
                DM.atkbonus = 0
                DM.defbonus = 0
                DM.typemod = 0
                DM.atkpower = DM.duelists[owner].g1.power

                #This is a regular attack
                DM.caliber = 0
                
                attack = DM.duelists[owner].g1.attack #attack stat of user player's first Gemma
                defence = DM.duelists[notowner].g1.defence #defence stat of opponent player's first Gemma
                atkroll = random.randint(1, DiceList[attack])
                defroll = random.randint(1, DiceList[defence])

                atk = DM.duelists[owner].g1.type1
                defe = [DM.duelists[notowner].g1.type1, DM.duelists[notowner].g1.type2]
                mod = TypeChart[ atk , defe[0] ] + TypeChart[ atk , defe[1] ] 
                
                #Type modifier now scales with the level of the attacker or defender!
                if mod > 0:
                    mod = mod * TypemodLevelScaling[DM.duelists[owner].g1.level-1]
                else:
                    mod = mod * TypemodLevelScaling[DM.duelists[notowner].g1.level-1]
                DM.typemod = mod


                playerIndex = DM.turn 
                enemyIndex = -1 #temporary just to define it
                if playerIndex == 0:
                    enemyIndex = 1
                else:
                    enemyIndex = 0

                v1 = '-1'
                v2 = '-1'
                ###PASSIVE TRIGGER - This has to be before where we check modifier. A passive might change the modifier.
                if DM.duelists[0].g1.ctype != '':
                    v1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Typemod', -1)
                if DM.duelists[1].g1.ctype != '':
                    v2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Typemod', -1)
                ###END OF PASSIVE TRIGGER

                disc = DM.duelists[owner].g1.name + ' attacks ' + DM.duelists[notowner].g1.name + '!\n'
                if mod > 0:
                    disc += 'Attack roll: **' + str(atkroll) + '**\nType modifier **+' + str(mod) + '** gives a Total attack of: **' + str(mod+atkroll) \
                    + '**\nDefence roll: **' + str(defroll) + '**\n'
                elif mod < 0:
                    disc += 'Attack roll: **' + str(atkroll) + '**\nDefence roll: **' + str(defroll) + '**' \
                        + '\nType modifier **+' + str(-mod) + '** gives a Total defence of: **' + str(-mod+defroll) \
                        + '**\n'
                else:
                    disc += 'Attack roll: **' + str(atkroll) + '**\nDefence roll: **' + str(defroll) + '**\n'
                
                #Auto hit if guardbreak
                if DM.duelists[notowner].g1.guard == 0:
                    disc += '\n\n:diamond_shape_with_a_dot_inside: **Guard Break - Defence is reduced by ' + str(GuardBreakMod[DM.duelists[notowner].g1.level-1]) + '** :diamond_shape_with_a_dot_inside:'
                    DM.defbonus -= GuardBreakMod[DM.duelists[notowner].g1.level-1]

                embed = discord.Embed(
                    title = TypeList[DM.duelists[owner].g1.type1] + ' Attack',
                    description = disc,
                    color = discord.Colour.red()
                )

                #Save rolls in memory
                DM.atkroll = atkroll
                DM.defroll = defroll

                if v1 != '-1':
                    embed.add_field(name='Passive ability', value = v1)
                if v2 != '-1':
                    embed.add_field(name='Passive ability', value = v2)
                
                ###PASSIVE TRIGGER
                if DM.duelists[0].g1.ctype != '':
                    v3 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Attack', -1)
                    if v3 != '-1':
                        embed.add_field(name='Passive ability', value = v3)

                if DM.duelists[1].g1.ctype != '':
                    v4 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Attack', -1)
                    if v4 != '-1':
                        embed.add_field(name='Passive ability', value = v4)
                ###END OF PASSIVE TRIGGER

                await bot.send_message(channel, embed=embed)
                await bot.send_message(channel, 'Advance with ``!go``')

                DM.phase = 3 #Phase 3


async def AIhattack(channel, npc, DM):
    userid = npc.userid
    index = findTeam(userid)

    if not gamepause:
        if DM.phase != 2 and DM.phase != 4:
            pass #To stop it saying "not your turn" when it is the wrong phase    
        elif DM.phase == 2 or DM.phase == 4:  
            [owner, notowner] = memfindTeam(userid, TeamList[index].dueltag)
            if DM.turn != owner:
                await bot.send_message(channel, 'It is not your turn.')
            elif not DM.duelists[owner].g1.alive:
                await bot.send_message(channel, 'You cannot attack with a defeated Gemma.')
            elif not DM.duelists[notowner].g1.alive:
                await bot.send_message(channel, 'You cannot attack, the opposing Gemma is defeated.')
            else:
                print('----------------------- AI Hattack')
                #New attack, clear out last attack's rolls and bonuses
                DM.atkroll = 0
                DM.defroll = 0
                DM.atkbonus = 0
                DM.defbonus = 0
                DM.typemod = 0
                DM.atkpower = DM.duelists[owner].g1.power + 1 #+1 for heavy attack

                #This is a heavy attack
                DM.caliber = 1
                
                attack = DM.duelists[owner].g1.attack #attack stat of user player's first Gemma
                defence = DM.duelists[notowner].g1.defence #defence stat of opponent player's first Gemma
                
                defroll = random.randint(1, DiceList[defence])

                #Heavy attack accuracy drawback, does not apply to modifiers
                #Disadvantage for now, could be a scale drawback
                atkroll = random.randint(1, DiceList[attack])
                atkroll_dis = random.randint(1, DiceList[attack])
                if atkroll_dis < atkroll: atkroll = atkroll_dis

                atk = DM.duelists[owner].g1.type2
                defe = [DM.duelists[notowner].g1.type1, DM.duelists[notowner].g1.type2]
                mod = TypeChart[ atk , defe[0] ] + TypeChart[ atk , defe[1] ] 
                print('----------------------- AI Hattack still well')
                #Type modifier now scales with the level of the attacker or defender!
                if mod > 0:
                    mod = mod * TypemodLevelScaling[DM.duelists[owner].g1.level-1]
                else:
                    mod = mod * TypemodLevelScaling[DM.duelists[notowner].g1.level-1]
                DM.typemod = mod

                playerIndex = DM.turn 
                enemyIndex = -1 #temporary just to define it
                if playerIndex == 0:
                    enemyIndex = 1
                else:
                    enemyIndex = 0

                v1 = '-1'
                v2 = '-1'
                ###PASSIVE TRIGGER - This has to be before where we check modifier. A passive might change the modifier.
                if DM.duelists[0].g1.ctype != '':
                    v1 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Typemod', -1)
                    
                if DM.duelists[1].g1.ctype != '':
                    v2 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Typemod', -1)
                ###END OF PASSIVE TRIGGER

                disc = DM.duelists[owner].g1.name + ' attacks ' + DM.duelists[notowner].g1.name + '!\n'
                if mod > 0:
                    disc += 'Attack roll: **' + str(atkroll) + '**\nType modifier **+' + str(mod) + '** gives a Total attack of: **' + str(mod+atkroll) \
                    + '**\nDefence roll: **' + str(defroll) + '**\n'
                elif mod < 0:
                    disc += 'Attack roll: **' + str(atkroll) + '**\nDefence roll: **' + str(defroll) + '**' \
                        + '\nType modifier **+' + str(-mod) + '** gives a Total defence of: **' + str(-mod+defroll) \
                        + '**\n'
                else:
                    disc += 'Attack roll: **' + str(atkroll) + '**\nDefence roll: **' + str(defroll) + '**\n'
                print('----------------------- AI Hattack look at guardbreak')
                #Auto hit if guardbreak
                if DM.duelists[notowner].g1.guard == 0:
                    disc += '\n\n:diamond_shape_with_a_dot_inside: **Guard Break - Defence is reduced by ' + str(GuardBreakMod[DM.duelists[notowner].g1.level-1]) + '** :diamond_shape_with_a_dot_inside:'
                    DM.defbonus -= GuardBreakMod[DM.duelists[notowner].g1.level-1]
                print('----------------------- AI Hattack passed gb')
                embed = discord.Embed(
                    title = 'Heavy ' + TypeList[DM.duelists[owner].g1.type2] + ' Attack',
                    description = disc,
                    color = discord.Colour.red()
                )

                #Save rolls in memory
                DM.atkroll = atkroll
                DM.defroll = defroll

                if v1 != '-1':
                    embed.add_field(name='Passive ability', value = v1)
                if v2 != '-1':
                    embed.add_field(name='Passive ability', value = v2)
                
                ###PASSIVE TRIGGER
                if DM.duelists[0].g1.ctype != '':
                    v3 = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, 0, 'Attack', -1)
                    if v3 != '-1':
                        embed.add_field(name='Passive ability', value = v3)

                if DM.duelists[1].g1.ctype != '':
                    v4 = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, 1, 'Attack', -1)
                    if v4 != '-1':
                        embed.add_field(name='Passive ability', value = v4)
                ###END OF PASSIVE TRIGGER

                await bot.send_message(channel, embed=embed)
                await bot.send_message(channel, 'Advance with ``!go``')

                DM.phase = 3 #Phase 3


async def AIab1(channel, npc, DM):
    userid = npc.userid
    index = findTeam(userid)

    if not gamepause:
        owner = memfindTeam(userid, TeamList[index].dueltag)[0]
        if owner == 0: notowner = 1
        else: notowner = 0
        playerIndex = DM.turn 
        enemyIndex = -1 #temporary just to define it
        if playerIndex == 0:
            enemyIndex = 1
        else:
            enemyIndex = 0

        num = DM.duelists[owner].g1.ability[0]

        #Check you have uses left on the old ability charge
        if DM.duelists[owner].g1.ability[1] == 0: #If you are out of ability uses, donzo.
            await bot.send_message(channel, 'You have already used that ability this duel.')
        else:
            c = True
            embed = -1
            for i, ab in enumerate(DM.abilityList):
                if ab[0] == 0 and ab[1] != owner: #Should not trigger for the owner of the null aura:
                    #'[-] Null Aura: Nullify your opponent\'s next ability activation.'
                    disc = '**>>** *Null Aura* triggers and nullifies the ability!'
                    del DM.abilityList[i]
                    DM.duelists[owner].g1.ability[1] -= 1
                    c = False
                    embed = discord.Embed(
                        title = 'Ability',
                        description = disc,
                        color = discord.Colour.teal()
                    )   
            if c:
                disc, slink1, slink2, pas1, pas2 = ability(num, 0, DM, playerIndex, enemyIndex, owner, -1, -1)
                embed = discord.Embed(
                    title = 'Ability',
                    description = disc,
                    color = discord.Colour.teal()
                )
                if slink1 != '-1': embed.add_field(name='Ability trigger', value = slink1)
                if slink2 != '-1': embed.add_field(name='Ability trigger', value = slink2)
                if pas1 != '-1': embed.add_field(name='Passive ability', value = pas1)
                if pas2 != '-1': embed.add_field(name='Passive ability', value = pas2)

                ###PASSIVE TRIGGER
                if DM.duelists[0].g1.ctype != '':
                    v = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Ability', 1)
                    if v != '-1':
                        embed.add_field(name='Passive ability', value = v)
                if DM.duelists[1].g1.ctype != '':
                    v = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Ability', 1)
                    if v != '-1':
                        embed.add_field(name='Passive ability', value = v)
                ###END OF PASSIVE TRIGGER 
            await bot.send_message(channel, embed=embed)

        result = findLoser(DM) #Check if there is a loser
        if result != -1:
            await actOnLoser(result, DM, owner, notowner)
            

async def AIab2(channel, npc, DM):
    userid = npc.userid
    index = findTeam(userid)

    if not gamepause:
        owner = memfindTeam(userid, TeamList[index].dueltag)[0]
        if owner == 0: notowner = 1
        else: notowner = 0
        if DM.duelists[owner].gotrigger: #You have already used !go, you cannot use abilities.
            await bot.send_message(channel, 'You cannot activate abilities after using ``!go``')
        elif DM.duelists[owner].g1.ability[2] == -1:
            await bot.send_message(channel, 'Your second ability has not been unlocked yet.')
        else:
            playerIndex = DM.turn
            enemyIndex = -1 #temporary just to define it
            if playerIndex == 0:
                enemyIndex = 1
            else:
                enemyIndex = 0

            num = DM.duelists[owner].g1.ability[2]

            #Check you have uses left on the old ability charge
            if DM.duelists[owner].g1.ability[3] == 0: #If you are out of ability uses, donzo.
                await bot.send_message(channel, 'You have already used that ability this duel.')
            else:
                c = True
                embed = -1
                for i, ab in enumerate(DM.abilityList):
                    if ab[0] == 0 and ab[1] != owner: #Should not trigger for the owner of the null aura
                        #'[-] Null Aura: Nullify your opponent\'s next ability activation.'
                        disc = '**>>** *Null Aura* triggers and nullifies the ability!'
                        del DM.abilityList[i]
                        DM.duelists[owner].g1.ability[3] -= 1
                        c = False
                        embed = discord.Embed(
                            title = 'Ability',
                            description = disc,
                            color = discord.Colour.teal()
                        )
                if c:
                    disc, slink1, slink2, pas1, pas2 = ability(num, 2, DM, playerIndex, enemyIndex, owner, -1, -1)
                    if disc == '-1': disc = 'You cannot use this ability right now.'
                    embed = discord.Embed(
                        title = 'Ability',
                        description = disc,
                        color = discord.Colour.teal()
                    )

                    if slink1 != '-1': embed.add_field(name='Ability trigger', value = slink1)
                    if slink2 != '-1': embed.add_field(name='Ability trigger', value = slink2)
                    if pas1 != '-1': embed.add_field(name='Passive ability', value = pas1)
                    if pas2 != '-1': embed.add_field(name='Passive ability', value = pas2)

                    ###PASSIVE TRIGGER
                    if DM.duelists[0].g1.ctype != '':
                        v = passive(DM.duelists[0].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Ability', 2)
                        if v != '-1':
                            embed.add_field(name='Passive ability', value = v)
                    if DM.duelists[1].g1.ctype != '':
                        v = passive(DM.duelists[1].g1.passive[0], DM, playerIndex, enemyIndex, owner, 'Ability', 2)
                        if v != '-1':
                            embed.add_field(name='Passive ability', value = v)
                    ###END OF PASSIVE TRIGGER
                await bot.send_message(channel, embed=embed)

            result = findLoser(DM) #Check if there is a loser
            if result != -1:
                await actOnLoser(result, DM, owner, notowner)
                

@bot.command(pass_context = True)
async def challengenpc(ctx):
    
    channel = ctx.message.channel
    user = ctx.message.author
    userid = user.id
    index = findTeam(userid)
    tagged, tagcommand = findTag(user)
    if not gamepause:
        if not tagged:
            if index == -1:
                await bot.whisper('You do not have a team yet, create one with ``!start``.')
            elif ctx.message.channel.is_private:
                await bot.whisper('Duel commands can only be used on the Jaegergems server.')
            elif findName(TeamList[index].opponent) != -1:
                await bot.send_message(channel, 'You are already in a duel with ' + str(TeamList[index].opponent))
            elif TeamList[index].g1.id == 'NULL':
                await bot.send_message(channel, 'You must have a gemma in your first team slot to duel.')
            else:
                await bot.send_message(channel, 'Choose your opponent:\n**1** - Equal duelist\n**2** - Strong duelist\n**3** - Elite Four')
                ans = await bot.wait_for_message(author = user)
                try:
                    ans = int(ans.content)
                    global maxGID
                    enemy = ''
                    if ans == 1:
                        d = Duelist()
                        maxGID += 1
                        d.userid = maxGID
                        d.discname = 'Jaegergembot3'
                        d.duelistname = 'NPC ' + str(random.randint(0, 100))
                        while findName(d.duelistname) != -1:
                            d.duelistname = 'NPC ' + str(random.randint(0, 100))
                        d.bot = True
                        d.user = -1 #We look at this at the end of the duel so we can remove the duelist from TeamList
                        TeamList.append(d)
                        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
                        eindex = findName(d.discname)
                        if TeamList[index].g1.id == 'NULL': 
                            level1 = -1
                        else:
                            level1 = TeamList[index].g1.level
                        if TeamList[index].g2.id == 'NULL': 
                            level2 = -1
                        else:
                            level2 = TeamList[index].g2.level
                        if TeamList[index].g3.id == 'NULL': 
                            level3 = -1
                        else:
                            level3 = TeamList[index].g3.level
                        randomEncounter(eindex, level1, level2, level3)
                    elif ans == 2:
                        d = Duelist()
                        maxGID += 1
                        d.userid = maxGID
                        d.discname = 'Jaegergembot3'
                        d.duelistname = 'NPC ' + str(random.randint(0, 100))
                        while findName(d.duelistname) != -1:
                            d.duelistname = 'NPC ' + str(random.randint(0, 100))
                        d.bot = True
                        d.user = -1 #We look at this at the end of the duel so we can remove the duelist from TeamList
                        TeamList.append(d)
                        savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
                        eindex = findName(d.discname)
                        if TeamList[index].g1.id == 'Null': 
                            level1 = -1
                        else:
                            level1 = TeamList[index].g1.level + 3
                            if level1 > 10: level1 = 10
                        if TeamList[index].g2.id == 'Null': 
                            level2 = -1
                        else:
                            level2 = TeamList[index].g1.level + 3
                            if level2 > 10: level2 = 10
                        if TeamList[index].g3.id == 'Null': 
                            level3 = -1
                        else:
                            level3 = TeamList[index].g1.level + 3
                            if level3 > 10: level3 = 10
                        randomEncounter(eindex, level1, level2, level3)

                    elif ans == 3:
                        if userid in E4[4]:
                            await asyncio.sleep(1)
                            #If you have defeated the champion you can start over
                            E4[0].remove(userid)
                            E4[1].remove(userid)
                            E4[2].remove(userid)
                            E4[3].remove(userid)
                            E4[4].remove(userid)
                            enemy = 'NPC E4 Kimi'
                            eindex = findName(enemy)
                        elif userid in E4[3]:
                            await asyncio.sleep(1)
                            #You have defeated Cosette, time for the Champion
                            enemy = 'NPC Champion Sivaruz'
                            eindex = findName(enemy)
                        elif userid in E4[2]:
                            await asyncio.sleep(1)
                            #You have defeated Gilbert, time for Cosette
                            enemy = 'NPC E4 Cosette'
                            eindex = findName(enemy)
                        elif userid in E4[1]:
                            await asyncio.sleep(1)
                            #You have defeated Lorasatra, time for Gilbert
                            enemy = 'NPC E4 Gilbert'
                            eindex = findName(enemy)
                        elif userid in E4[0]:
                            await asyncio.sleep(1)
                            #You have defeated Kimi, time for Lorasatra
                            enemy = 'NPC E4 Lorasatra'
                            eindex = findName(enemy)
                        else:
                            await asyncio.sleep(1)
                            #You are brand new here, time for Kimi
                            enemy = 'NPC E4 Kimi'
                            eindex = findName(enemy)   
                    else:
                        await bot.send_message(channel, 'Challenge cancelled')
                except ValueError:
                    await bot.send_message(channel, 'Challenge cancelled')

                if findName(TeamList[eindex].opponent) != -1:
                    await bot.send_message(channel, enemy + ' is already in a duel.')
                else:
                    
                    if enemy == 'NPC E4 Kimi':
                        await bot.send_message(channel, '```Kimi:\n\"Welcome to the Elite Four duelist ' + TeamList[index].duelistname
                            + '. My job is to weed out the weaklings that attempt the Elite Four challenge. Prove your worth, my Ghost type Gemma will show how weak you really are!\"```')
                    elif enemy == 'NPC E4 Lorasatra':
                        await bot.send_message(channel, '```Lorasatra:\n\"Oh, a new challenger? I am Lorasatra, a duelist specializing in Organism type Gemma.'
                            + ' My team can be quite tough to bring down, I\'m curious to see how long you can withstand the force of nature.\"```')
                    if enemy == 'NPC E4 Gilbert':
                        await bot.send_message(channel, '```Gilbert:\n\"So ye made it past Lorasatra ey? Good show! Now prepare yerself to face me, Gilbert the Flame duelist.'
                            + ' Don\'t get blown away too soon ey!\"```')
                    if enemy == 'NPC E4 Cosette':
                        await bot.send_message(channel, '```Cosette:\n\"The crashing wave, the raging ocean, the all-consuming flood. Do you have what it takes to survive my onslaught '
                            + 'duelist? Few challengers get this far and fewer still get past me. The name is Cosette, I\'ll make sure you remember it!\"```')
                    if enemy == 'NPC Champion Sivaruz':
                        await bot.send_message(channel, '```Sivaruz:\n\"Well met duelist ' + TeamList[index].duelistname + '! I am Sivaruz, the current Jaegergem Champion.'
                            + ' You must truly be a magnificent duelist to have made it this far. Now, show the world that you can overcome the true might of my Myth type Gemma!\"```')
                    
                    await bot.send_message(channel, TeamList[eindex].duelistname + ' accepts ' + TeamList[index].duelistname + '\'s challenge!')
                    
                    #Removing duelmem remains
                    currentmem = copy.copy(DuelmemList)
                    for mem in currentmem:
                        if mem.duelists[0].userid == TeamList[index].userid or mem.duelists[1].userid == TeamList[index].userid:
                            print(' - - - - - Found remains of duelmem for duelist: ', TeamList[index].duelistname)
                            try:
                                DuelmemList.remove(mem)
                            except ValueError:
                                pass
                        if mem.duelists[0].userid == TeamList[eindex].userid or mem.duelists[1].userid == TeamList[eindex].userid:
                            print(' - - - - - Found remains of duelmem for duelist: ', TeamList[index].duelistname)
                            try:
                                DuelmemList.remove(mem)
                            except ValueError:
                                pass
                    
                    
                    TeamList[eindex].opponent = TeamList[index].duelistname
                    TeamList[index].opponent = TeamList[eindex].duelistname

                    dueltag = TeamList[index].duelistname + TeamList[eindex].duelistname
                    TeamList[eindex].dueltag = dueltag
                    TeamList[index].dueltag = dueltag

                    duel = Duelmem()
                    duel.phase = 0
                    duel.dueltag = dueltag
                    duel.duelists[0] = copy.copy(TeamList[index])
                    duel.duelists[1] = copy.copy(TeamList[eindex])

                    #Deep copy of Gemma
                    duel.duelists[0].g1 = copy.copy(TeamList[index].g1)
                    duel.duelists[0].g2 = copy.copy(TeamList[index].g2)
                    duel.duelists[0].g3 = copy.copy(TeamList[index].g3)
                    duel.duelists[1].g1 = copy.copy(TeamList[eindex].g1)
                    duel.duelists[1].g2 = copy.copy(TeamList[eindex].g2)
                    duel.duelists[1].g3 = copy.copy(TeamList[eindex].g3)
                    
                    #Deep copy of Gemma abilities, otherwise the python list is shared
                    duel.duelists[0].g1.ability = copy.copy(TeamList[index].g1.ability)
                    duel.duelists[0].g2.ability = copy.copy(TeamList[index].g2.ability)
                    duel.duelists[0].g3.ability = copy.copy(TeamList[index].g3.ability)
                    duel.duelists[1].g1.ability = copy.copy(TeamList[eindex].g1.ability)
                    duel.duelists[1].g2.ability = copy.copy(TeamList[eindex].g2.ability)
                    duel.duelists[1].g3.ability = copy.copy(TeamList[eindex].g3.ability)

                    #Deep copy of Gemma passives, otherwise the python list is shared
                    duel.duelists[0].g1.passive = copy.copy(TeamList[index].g1.passive)
                    duel.duelists[0].g2.passive = copy.copy(TeamList[index].g2.passive)
                    duel.duelists[0].g3.passive = copy.copy(TeamList[index].g3.passive)
                    duel.duelists[1].g1.passive = copy.copy(TeamList[eindex].g1.passive)
                    duel.duelists[1].g2.passive = copy.copy(TeamList[eindex].g2.passive)
                    duel.duelists[1].g3.passive = copy.copy(TeamList[eindex].g3.passive)
                    
                    duel.channel = ctx.message.channel
                    DuelmemList.append(duel)
                    
                    hpbar = ''
                    if TeamList[index].g1.hp <= 0: hpbar += ':skull:'
                    else:
                        for i in range(0, TeamList[index].g1.hp): hpbar += ':heart:'
                        for i in range(0, TeamList[index].g1.maxhp - TeamList[index].g1.hp): hpbar += ':black_heart:'
                        for i in range(0, TeamList[index].g1.guard): hpbar += ':shield:'

                    disc1 = 'Lv.' + str(TeamList[index].g1.level) + ' **' + TeamList[index].g1.name + '**, the ' + TypeList[TeamList[index].g1.type1] \
                    + '/' + TypeList[TeamList[index].g1.type2]
                    ctype = TeamList[index].g1.ctype
                    if ctype != '':
                        disc1 += ' [' + ctype + ']'
                    disc1 += ' Gemma - ' + hpbar 

                    hpbar = ''
                    if TeamList[eindex].g1.hp <= 0: hpbar += ':skull:'
                    else:
                        for i in range(0, TeamList[eindex].g1.hp): hpbar += ':heart:'
                        for i in range(0, TeamList[eindex].g1.maxhp - TeamList[eindex].g1.hp): hpbar += ':black_heart:'
                        for i in range(0, TeamList[eindex].g1.guard): hpbar += ':shield:'

                    disc2 = 'Lv.' + str(TeamList[eindex].g1.level) + ' **' + TeamList[eindex].g1.name + '**, the ' + TypeList[TeamList[eindex].g1.type1] \
                    + '/' + TypeList[TeamList[eindex].g1.type2]
                    ctype = TeamList[eindex].g1.ctype
                    if ctype != '':
                        disc2 += ' [' + ctype + ']'
                    disc2 += ' Gemma - ' + hpbar
                    
                    disc = 'Duelist **' + TeamList[index].duelistname + '**\n' + disc1 + '\n\n**VS**\n\n' \
                            + 'Duelist **' + TeamList[eindex].duelistname + '**\n' + disc2
                    
                    embed = discord.Embed(
                        title = 'Duel',
                        description = disc,
                        color = discord.Colour.red()
                    )
                    await bot.send_message(channel, embed=embed)
                    await bot.send_message(channel, '\nAdvance with ``!go``')

                    ai = AItask()
                    ai.channel = ctx.message.channel
                    ai.dueltag = dueltag
                    ai.task = bot.loop.create_task(AIduel(dueltag))
                    AItaskList.append(ai)

                    savelist(TeamList, DuelmemList, maxGID, AdminList, TimeList, TagList, E4)
        elif tagged:
            await bot.whisper('You are already using the command ' + tagcommand + '\nPlease complete that command first.')


async def AIduel(dueltag):
    await bot.wait_until_ready()
    duelindex = memfindDueltag(dueltag)
    if duelindex == -1:
        AIindex = findAItask(dueltag)
        if AIindex != -1:
            AItaskList[AIindex].task.cancel()
            AItaskList.remove(AItaskList[AIindex])
    else:
        DM = DuelmemList[duelindex]
        while not bot.is_closed:
            await asyncio.sleep(1) 

            if DM.duelists[0].bot: 
                npcowner = 0
                playerowner = 1
            else: 
                npcowner = 1
                playerowner = 0
            npc = DM.duelists[npcowner]
            player = DM.duelists[playerowner]
            gnpc = npc.g1
            gplayer = player.g1
            yourturn = False
            if npcowner == DM.turn: yourturn = True
            if yourturn:
                playerIndex = npcowner
                enemyIndex = playerowner
            else:
                playerIndex = playerowner
                enemyIndex = npcowner
            num1 = gnpc.ability[0]
            num2 = gnpc.ability[2]
            channel = DM.channel

            #Duel - phase 0 - Use ability, othwerise !go
            #Initiative - phase 1 - Use ability, otherwise !go
            #Initiative resuls - phase 2 - If it's your turn pick !rotate or !attack or !hattack
            #Battle - phase 3 - Use ability, otherwise !go
            #Aftermath - phase 4 - Rotate if your Gemma is dead. If it's your turn pick !rotate or !attack or !hattack

            print(npc.duelistname, ' ##### ##### I have used !go and is waiting for my opponent ', player.duelistname)

            if not npc.gotrigger:
                if DM.phase == 0: #Before initiative & After rotation
                    #print(npc.duelistname, ' ##### ##### about to check ab1, num1: ', num1)
                    if checkab(num1, DM, playerIndex, enemyIndex, npcowner, playerowner, DM.phase, 1, yourturn): 
                        await bot.send_message(channel, '!ab1')
                        await AIab1(channel, npc, DM)
                    #print(npc.duelistname, ' ##### ##### about to check ab2, num2: ', num2)
                    if checkab(num2, DM, playerIndex, enemyIndex, npcowner, playerowner, DM.phase, 3, yourturn):
                        await bot.send_message(channel, '!ab2')
                        await AIab2(channel, npc, DM)
                    #print(npc.duelistname, ' ##### ##### time to !go')
                    await asyncio.sleep(1)
                    await bot.send_message(channel, '!go')
                    await AIgo(channel, npc, DM)

                elif DM.phase == 1: #During initiative
                    #print(npc.duelistname, ' ##### ##### about to check ab1, num1: ', num1)
                    if checkab(num1, DM, playerIndex, enemyIndex, npcowner, playerowner, DM.phase, 1, yourturn):
                        await bot.send_message(channel, '!ab1')
                        await AIab1(channel, npc, DM)
                    #print(npc.duelistname, ' ##### ##### about to check ab2, num2: ', num2)
                    if checkab(num2, DM, playerIndex, enemyIndex, npcowner, playerowner, DM.phase, 3, yourturn):
                        await bot.send_message(channel, '!ab2')
                        await AIab2(channel, npc, DM)
                    #print(npc.duelistname, ' ##### ##### time to !go')
                    await asyncio.sleep(1)
                    await AIgo(channel, npc, DM)

                elif DM.phase == 2: #After initiative, no abilities to activate here
                    #print('yourturn: ', yourturn)
                    #print('player: ', DM.duelists[playerIndex].duelistname)
                    #print('playerIndex: ', playerIndex)
                    #print('turn: ', DM.turn)
                    if yourturn:
                        ans = checkrotatk(npc, gnpc, gplayer)
                        if ans == 'rot':
                            await bot.send_message(channel, '!rotate')
                            await AIrotate(channel, npc, DM)
                        elif ans == 'lat':
                            await bot.send_message(channel, '!attack')
                            await AIattack(channel, npc, DM)
                        elif ans == 'hat':
                            await bot.send_message(channel, '!hattack')
                            await AIhattack(channel, npc, DM)

                elif DM.phase == 3: #During battle
                    #print(npc.duelistname, ' ##### ##### about to check ab1, num1: ', num1)
                    if checkab(num1, DM, playerIndex, enemyIndex, npcowner, playerowner, DM.phase, 1, yourturn):
                        await bot.send_message(channel, '!ab1')
                        await AIab1(channel, npc, DM)
                    #print(npc.duelistname, ' ##### ##### about to check ab2, num2: ', num2)
                    if checkab(num2, DM, playerIndex, enemyIndex, npcowner, playerowner, DM.phase, 3, yourturn):
                        await bot.send_message(channel, '!ab2')
                        await AIab2(channel, npc, DM)
                    #print(npc.duelistname, ' ##### ##### time to !go')
                    await asyncio.sleep(1)
                    await bot.send_message(channel, '!go')
                    await AIgo(channel, npc, DM)

                elif DM.phase == 4: #Aftermath
                    #print(npc.duelistname, ' ##### ##### about to check ab1, num1: ', num1)
                    if checkab(num1, DM, playerIndex, enemyIndex, npcowner, playerowner, DM.phase, 1, yourturn):
                        await bot.send_message(channel, '!ab1')
                        await AIab1(channel, npc, DM)
                    #print(npc.duelistname, ' ##### ##### about to check ab2, num2: ', num2)
                    if checkab(num2, DM, playerIndex, enemyIndex, npcowner, playerowner, DM.phase, 3, yourturn):
                        await bot.send_message(channel, '!ab2')
                        await AIab2(channel, npc, DM)
                    await asyncio.sleep(1)

                    if yourturn:
                        print(npc.duelistname, ' ##### ##### it is my turn, time to think.')

                        ans = checkrotatk(npc, gnpc, gplayer)
                        if ans == 'rot':
                            await bot.send_message(channel, '!rotate')
                            await AIrotate(channel, npc, DM)
                        elif ans == 'lat':
                            await bot.send_message(channel, '!attack')
                            await AIattack(channel, npc, DM)
                        elif ans == 'hat':
                            await bot.send_message(channel, '!hattack')
                            await AIhattack(channel, npc, DM)
                    else:
                        if not gnpc.alive:
                            if (npc.g2.id != 'NULL' and npc.g2.alive) or (npc.g3.id != 'NULL' and npc.g3.alive):                        
                                await bot.send_message(channel, '!rotate')
                                await AIrotate(channel, npc, DM)



############################################################################################################
############################################################################################################
############################################################################################################


#   bot run


############################################################################################################
############################################################################################################
############################################################################################################


bot.run('BOT TOKEN HERE')
