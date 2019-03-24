import logging
import random
import numpy as np
from game import Game
from card import DevelopCard, Noble


GEMS_DICT = {"blue": 0, "green": 1, "red": 2, "black": 3, "white": 4, "gold": 5}
COLORS = ['blue', 'green', 'red', 'black', 'white']
bi2index = {'11100':0, '11010':1, '11001':2, '10110':3, '10101':4, '10011':5, '01110':6, '01101':7, '01011':8, '00111':9}
index2bi = ['11100', '11010', '11001', '10110', '10101', '10011', '01110', '01101', '01011', '00111' ]


def gen_card(lvl):
    arg_card = {'level':lvl, 'score':0, 'color':'', 'costs':[]}
    arg_card['color'] = COLORS[random.randint(0, 4)]
    cnum = random.randint(3, 5)
    arg_card['score'] = random.randint(0, 1)
    clist = np.zeros(5)
    if (lvl == 2):
        cnum = random.randint(7, 10)
        arg_card['score'] = random.randint(1, 3)
    elif (lvl == 3):
        cnum = random.randint(11, 15)
        arg_card['score'] = random.randint(3, 5)
    for i in range(cnum):
        j = random.randint(0, 4)
        clist[j] += 1
    for i in range(5):
        if (clist[i] > 0):
            arg_card['costs'].append({'color':COLORS[i], 'count':clist[i]})
    return arg_card

def gen_noble():
    arg_card = {'score':3, 'requirements':[]}
    f = random.randint(2, 3)
    clist = []
    for i in range(f):
        c = COLORS[random.randint(0, 4)]
        while (clist.count(c) > 0):
            c = COLORS[random.randint(0, 4)]
        clist.append(c)
        arg_card['requirements'].append({'color':c, 'count':6-f})
    return arg_card

def getGame():
    arg_game = {'round':1, 'playerName':'player1', 'players':[]}
    for i in range(3):
        genlist = []
        for c in COLORS:
            genlist.append({'color':c, 'count':0})
        arg_player = {'name':'player'+str(i+1), 'score':0, 'gems':genlist, 'purcahsed_cards':[], 'reserved_cards':[], 'nobles':[]}
        arg_game['players'].append(arg_player)
    arg_table = {'gems':[], 'cards':[], 'nobles':[]}
    for c in COLORS:
        arg_table['gems'].append({'color':c, 'count':5})
    arg_table['gems'].append({'color':'gold', 'count':5})
    for i in range(3):
        for j in range(4):
            arg_table['cards'].append(gen_card(i+1))
    for i in range(4):
        arg_table['nobles'].append(gen_noble())
    arg_game['table'] = arg_table
    return Game(arg_game)


class ENV():

    def __init__(self):
        # self.game = Game()
        self.state = np.zeros(1344)
        # self.next_game = Game()
        self.next_state = np.zeros(1344)
        self.done = False
        #self.valid = True
        self.act = np.zeros(45)

    def reset(self):
        # with open('sample_splendor_request.json', 'r') as f:
        #    data = json.load(f)
        self.game = getGame()
        self.state = self.game2vec(self.game)
        #print(self.state[10:50])
        return self.state

    def game2vec(self, game):
        self.state = np.zeros(1344)

        self.state[0] = game.round

        for index, gem in enumerate(self.game.table.gems):
            self.state[1 + GEMS_DICT[gem.get('color')]] = gem.get('count', 0)

        for index, card in enumerate(self.game.table.cards):
            for cost in card.costs:
                self.state[7 + 11*index + GEMS_DICT[cost.get('color')]] = cost.get('count', 0)
            self.state[7 + 11*index + 5] = card.score
            self.state[7 + 11*index + 6 + GEMS_DICT[card.color]] = 1

        for index, noble in enumerate(self.game.table.nobles):
            for requirement in noble.requirements:
                self.state[139 + 6*index + GEMS_DICT[requirement.get('color')]] = requirement.get('count', 0)
            self.state[139 + 6*index + 5] = noble.score

        for index, (player_name, player) in enumerate(self.game.players.items()):
            self.state[163 + 394*index] = player.score
            for gem in (player.gems):
                self.state[163 + 394*index + 1 + GEMS_DICT[gem.get('color')]] = gem.get('count', 0)
            for ind, purchased_card in enumerate(player.purchased_cards):
                for cost in purchased_card.costs:
                    self.state[163 + 394*index + 7 + 11*ind + GEMS_DICT[cost.get('color')]] = cost.get('count', 0)
            for ind, reserved_card in enumerate(player.reserved_cards):
                for cost in reserved_card.costs:
                    self.state[163 + 394*index + 40 + 11*ind + GEMS_DICT[cost.get('color')]] = cost.get('count', 0)
            for ind, noble in enumerate(player.nobles):
                for requirement in noble.requirements:
                    self.state[163 + 394*index + 370 + 6*ind + GEMS_DICT[requirement.get('color')]] = requirement.get('count', 0)
                self.state[163 + 394*index + 370 + 6*ind + 5] = noble.score

        return self.state

    def action2vec(self, action):
        for i in range(len(self.act)):
            self.act[i] = 0
        for key, values in action.items():
            if key == "get_different_color_gems":
                gem_str = '00000'
                for gem_color in values:
                    gem[GEMS_DICT[gem_color]] = '1'
                act[bi2index[gem_str]] = 1
            elif key == "get_two_same_color_gems":
                act[10 + GEMS_DICT[values]] = 1
            elif key == "reserve_card":
                act[15]
        return self.act

    def vec2action(self, act):
        label = 0
        action = {}
        cnt = 0
        for i in act:
            if (i == 1):
                label = cnt
                label = int(label)
                break
            cnt += 1
        if (label < 10):
            binary = index2bi[label]
            action['get_different_color_gems'] = []
            for i in range(5):
                if (binary[i] == '1'):
                    action['get_different_color_gems'].append(COLORS[i])
        elif (label < 15):
            action['get_two_same_color_gems'] = COLORS[label-10]
        elif (label < 27):
            action = None
            if (len(self.game.table.cards) > label-15):
                card = self.game.table.cards[label-15]
                action = {}
                action['reserve_card'] = {'card': {'color': card.color, 'costs': card.costs, 'level': card.level, 'score': card.score} }
        elif (label < 30):
            action['reserve_card'] = {'level': label - 26}
        elif (label < 42):
            action = None
            if (len(self.game.table.cards) > label-30):
                card = self.game.table.cards[label-30]
                action = {}
                action['purchase_card'] = {'color': card.color, 'costs': card.costs, 'level': card.level, 'score': card.score}
        else:
            action = None
            if (len(self.game.players[self.game.player_name].reserved_cards) > label-42):
                card = self.game.players[self.game.player_name].reserved_cards[label-42]
                action = {}
                action['purchase_reserved_card'] = {'color': card.color, 'costs': card.costs, 'level': card.level, 'score': card.score}
        return action
    
    def gem_available(self, gem_color, num):
        for gem in self.game.table.gems:
            if gem_color == gem.get('color'):
                return gem.get('count', 0) >= num
                 
    def step(self, act_vec):
        valid = False
        action = self.vec2action(act_vec)
        next_game = self.game
        reward = 0.0
        DIC = action
        v = self.game2vec(self.game)

        if act_vec.all() == None:
            return self.next_state, reward, self.done, valid, DIC

        for key, values in action.items():
            player = self.game.players[self.game.player_name]
            #print(player.gems_count)
            table = self.game.table
            if key == "get_different_color_gems":
                if player.token_available() == False:
                    break
                tmp_val = []
                for value in values:
                    if self.gem_available(value, 1) == True:
                        tmp_val.append(value)
                values = tmp_val
                if values == None:
                    break
                for value in values:
                    reward += 0.1
                    for index, gem in enumerate(player.gems):
                        #print(gem.get('color'))
                        if gem.get('color') == value:
                            player.gems[index]['count'] += 1
                            for index2, ta_gem in enumerate(table.gems):
                                if ta_gem.get('color') == value:
                                    table.gems[index2]['count'] -= 1
                                    break
                            break
                    if player.token_available() == False:
                        break 
                valid = True
                player.purchase_power = player._set_purchase_power()
                player.noble_power = player._set_noble_power()
                next_game.players[self.game.player_name] = player
                next_game.table = table
                next_game.player_name = self.getNextPlayer()
                self.next_state = self.game2vec(next_game)

            elif key == "get_two_same_color_gems":
                if player.token_available() == False:
                    break
                value = values
                if self.gem_available(value, 4) == False:
                    break
                for index, gem in enumerate(player.gems):

                    if gem.get('color') == value:
                        player.gems[index]['count'] += 1
                        reward += 0.1
                        for index2, ta_gem in enumerate(table.gems):
                            if ta_gem.get('color') == value:
                                table.gems[index2]['count'] -= 1
                                break
                        break

                if  player.token_available():
                    for index, gem in enumerate(player.gems):
                        if gem.get('color') == value:
                            player.gems[index]['count'] += 1
                            reward += 0.1
                            for index2, ta_gem in enumerate(table.gems):
                                if ta_gem.get('color') == value:
                                    table.gems[index2]['count'] -= 1
                                    break
                            break
                valid = True
                player.purchase_power = player._set_purchase_power()
                player.noble_power = player._set_noble_power()
                next_game.players[player_name] = player
                next_game.player_name = self.getNextPlayer()
                next_game.table = table
                self.next_state = game2vec(next_game)
                
            elif key == "reserve_card":
                if not player.reserve_available():
                    break
                
                for kk, vv in values.items():

                    if kk == 'card':
                        DevCard = DevelopCard(vv)
                        player.reserved_cards.append(DevCard)
                        table.cards.remove(DevCard)
                        table.cards.append(DevelopCard(gen_card(DevCard.level)))

                        for index, gem in enumerate(table.gems):
                            if gem['color'] == 'gold' and gem['count'] >= 1:
                                table.gems[index]['count'] -= 1
                                reward += 0.2
                                for ind, g in enumerate(player.gems):
                                    if g['color'] == 'gold':
                                        player.gems[ind]['count'] += 1
                                        player.gems_count += 1
                                        break
                                break
                        gem_cost = 0
                        for cost in DevCard.costs:
                            gem_cost += cost['count']
                        reward += DevCard.score / (2 * gem_cost)                
                        next_game.table = table
     
                    elif kk == 'level':
                        level = vv
                        DevCard = DevelopCard(gen_card(level))
                        player.reserved_cards.append(DevCard)

                        for index, gem in enumerate(table.gems):
                            if gem['color'] == 'gold' and gem['count'] >= 1:
                                table.gems[index]['count'] -= 1
                                reward += 0.2
                                for ind, g in enumerate(player.gems):
                                    if g['color'] == 'gold':
                                        player.gems[ind]['count'] += 1
                                        player.gems_count += 1
                                        break
                                break

                        gem_cost = 0
                        for cost in DevCard.costs:
                            gem_cost += cost['count']
                        reward += DevCard.score / (2 * gem_cost)

                valid = True
                player.purchase_power = player._set_purchase_power()
                player.noble_power = player._set_noble_power()
                next_game.players[self.game.player_name] = player
                next_game.player_name = self.getNextPlayer()
                self.next_state = game2vec(next_game)
               
            elif key == "purchase_card":
                value = values
                DevCard = DevelopCard(value)
                if not player.afford_develop_card(DevCard):
                    break

                table.cards.remove(DevCard)
                table.cards.append(DevelopCard(gen_card(DevCard.level)))

                gem_cost = 0
                for cost in DevCard.costs:
                    gem_cost += cost['count']
                reward += DevCard.score / (gem_cost)

                reward += 0.3

                player = self.purchase_card(DevCard, player)
                valid = True
                player.purchase_power = player._set_purchase_power()
                player.noble_power = player._set_noble_power()
                flag, reward, next_game, dic = self.judgeNoble(next_game, reward)
                if flag == True:
                    DIC['noble'] = dic['noble']
                next_game.player_name = self.getNextPlayer()
                self.next_state = game2vec(next_game)                

            elif key == "purchase_reserved_card":
                value = values
                DevCard = DevelopCard(value)
                if not player.afford_develop_card(DevCard):
                    break

                gem_cost = 0
                for cost in DevCard.costs:
                    gem_cost += cost['count']
                reward += DevCard.score / (gem_cost)

                reward += 0.3

                player.reserved_cards.remove(DevCard)

                player = self.purchase_card(DevCard, player)
                valid = True
                player.purchase_power = player._set_purchase_power()
                player.noble_power = player._set_noble_power()
                flag, reward, next_game, dic = self.judgeNoble(next_game, reward)
                if flag == True:
                    DIC['noble'] = dic['noble']
                next_game.player_name = self.getNextPlayer()
                self.next_state = game2vec(next_game)
        if (valid):
            v = self.game2vec(self.game)
        self.is_done(next_game)
        return self.next_state, reward, self.done, valid, DIC

    def purchase_card(self, DevCard, player):
        dev_power = {'green': 0, 'white': 0,
                          'blue': 0, 'black': 0, 'red': 0, 'gold': 0}
        
        for card in player.purchased_cards:
            dev_power[card.color] += 1

        gold_ind = 0
        for index, gem in enumerate(player.gems):
            if gem['color'] == 'gold':
                gold_ind = index
                break

        for cost in DevCard.costs:
            color = cost['color']
            for gem in player.gems:
                if color == gem['color']:
                    gem['count'] -= max((cost['count'] - dev_power[color]), 0)
                    if gem['count'] < 0:
                        player.gems[gold_ind] += gem['count']
                        gem['count'] = 0
                    break
        player.append(DevCard)
        return player

    def getNextPlayer(self):
        pos = 0
        key_list = list(self.game.players.keys())
        for index, name in enumerate(key_list):
            if name == self.game.player_name:
                pos = (index + 1) % 3
                break
        return key_list[pos]

    def judgeNoble(self, next_game, reward):
        flag = False
        nobles = next_game.table.nobles
        player = next_game.players[next_game.player_name]
        dic = {}
        for noble in nobles:
            if player.afford_noble(noble) == True:
                flag = True
                next_game.table.nobles.remove(noble)
                dic['noble'] = {'requirements':noble.requirements, 'score':noble.score}
                reward += noble.score / 10
                player.nobles.append(noble)
                break
        next_game[next_game.player_name] = player
        return flag, reward, next_game, dic

    def loadenv(self, game):
        self.game = Game(game)
        self.state = self.game2vec(self.game)
        #print(self.state[10:50])
        return self.state

    def is_done(self, game):
        score = 0
        for k,v in self.game.players.items():
            if v.score >= 15:
                score = v.score
        self.done = score >= 15
        