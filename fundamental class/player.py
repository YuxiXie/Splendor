# author: zhangge9194@pku.edu.cn
# file: player.py

from card import DevelopCard, Noble


class Player(object):
    """docstring for Player"""

    def __init__(self, arg):
        super(Player, self).__init__()
        self.name = arg['name']
        self.score = arg.get('score', 0)

        self.gems = arg.get('gems', [])
        self.gems_count = sum([gem['count'] for gem in self.gems])
        self.purchased_cards = []
        self.reserved_cards = []
        self.nobles = []
        for card in arg.get('purchased_cards', []):
            self.purchased_cards.append(DevelopCard(card))
        for card in arg.get('reserved_cards', []):
            self.reserved_cards.append(DevelopCard(card))
        for card in arg.get('nobles', []):
            self.nobles.append(Noble(card))

        self.purchase_power = self._set_purchase_power()
        self.noble_power = self._set_noble_power()

    def token_available(self):
        return self.gems_count < 10

    def reserve_available(self):
        return len(self.reserved_cards) < 3

    def _set_purchase_power(self):
        '''
		purchase_power: {'green': 0, 'white': 0, 'blue': 0, 'black': 0, 'red': 0, 'gold': 0}
    	'''
        purchase_power = {'green': 0, 'white': 0,
                          'blue': 0, 'black': 0, 'red': 0, 'gold': 0}
        for gem in self.gems:
            purchase_power[gem['color']] += gem['count']
        for card in self.purchased_cards:
            purchase_power[card.color] += 1
        return purchase_power

    def _set_noble_power(self):
        '''
		noble_power: {'green': 0, 'white': 0, 'blue': 0, 'black': 0, 'red': 0, 'gold': 0}
    	'''
        noble_power = {'green': 0, 'white': 0,
                       'blue': 0, 'black': 0, 'red': 0, 'gold': 0}
        for card in self.purchased_cards:
            noble_power[card.color] += 1
        return noble_power
        pass

    def afford_develop_card(self, card):
        costs = card.costs
        dist = 0
        for gem in costs:
            dist += max(0, gem['count'] - self.purchase_power[gem['color']])
        return dist <= self.purchase_power['gold']

    def afford_noble(self, card):
        requirements = card.requirements
        for gem in requirements:
            if gem['count'] > self.noble_power[gem['color']]:
                return False
        return True
