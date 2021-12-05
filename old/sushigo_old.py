import random
import copy
from scipy.stats import rankdata

NUM_CARD_ON_TABLE = 13

MAKI = 'Maki' # For the board
ONE_MAKI = 'One maki' # Card type
TWO_MAKI = 'Two maki' # Card type
THREE_MAKI = 'Three maki' # Card type
TEMPURA = 'Tempura'
SASHIMI = 'Sashimi'
DUMPLINGS = 'Dumplings'
SQUID_NIGIRI = 'Squid Nigiri'
SALMON_NIGIRI = 'Salmon Nigiri'
EGG_NIGIRI = 'Egg Nigiri'
WASABI = 'Wasabi'
WASABI_SQUID = 'Wasabi Squid'
WASABI_SALMON = 'Wasabi Salmon'
WASABI_EGG = 'Wasabi Egg'
CHOPSTICKS = 'Chopsticks'
PUDDING = 'Pudding'


def score(board):
    """
    Scores board outside of pudding and maki which are calculated in separate functions
    """
    score = 0 # Chopsticks score nothing, maki and pudding are special
    num_dumplings = board[DUMPLINGS]
    if num_dumplings == 1:
        score += 1
    elif num_dumplings == 2:
        score += 3
    elif num_dumplings == 3:
        score += 6
    elif num_dumplings == 4:
        score += 10
    elif num_dumplings == 5:
        score += 15

    score += (board[TEMPURA] // 2) * 5 # Single tempura set is worth nothing -> Can have as many sets as you want
    score += (board[SASHIMI]) // 3 * 10  # Single or Double sashimi set is worth nothing -> Can have as many sets as you want
    score += board[SQUID_NIGIRI] * 3  # Squid Nigiri
    score += board[SALMON_NIGIRI] * 2  # Salmon Nigiri
    score += board[EGG_NIGIRI] * 1  # Egg Nigiri
    score += board[WASABI_SQUID] * 9  # Wasabi Squid Nigiri
    score += board[WASABI_SALMON] * 6  # Wasabi Salmon Nigiri
    score += board[WASABI_EGG] * 3  # Wasabi Egg Nigiri
    return score


def add_card_to_board(board, card): 
    if card == ONE_MAKI:
        board[MAKI] += 1
    elif card == TWO_MAKI:
        board[MAKI] += 2
    elif card == THREE_MAKI:
        board[MAKI] += 3
    elif card == TEMPURA:
        board[TEMPURA] += 1
    elif card == SASHIMI:
        board[SASHIMI] += 1
    elif card == DUMPLINGS:
        board[DUMPLINGS] += 1
    elif card == SQUID_NIGIRI:
        if board[WASABI] > 0:
            board[WASABI] -= 1
            board[WASABI_SQUID] += 1
        else:
            board[SQUID_NIGIRI] += 1
    elif card == SALMON_NIGIRI:
        if board[WASABI] > 0:
            board[WASABI] -= 1
            board[WASABI_SALMON] += 1
        else:
            board[SALMON_NIGIRI] += 1
    elif card == EGG_NIGIRI:
        if board[WASABI] > 0:
            board[WASABI] -= 1
            board[WASABI_EGG] += 1
        else:
            board[EGG_NIGIRI] += 1
    elif card == PUDDING:
        board[PUDDING] += 1


def get_maki_score(maki_counts):
    """
    Just like how the game scores outside of the fact that we are simplifying by
    removing tiebreakers. 
    """
    maki_scores = []
    maki_ranks = rankdata([-1 * count for count in maki_counts], method='min')
    for rank in maki_ranks:
        if rank == 1:
            maki_scores.append(6)
        elif rank == 2:
            maki_scores.append(3)
        else:
            maki_scores.append(0)
    return maki_scores


def get_pudding_score(pudding_cnt_list):
    pudding_scores = []
    pudding_ranks = rankdata([-1 * count for count in pudding_cnt_list], method='min')
    lowest_rank = min(pudding_ranks)
    for rank in pudding_ranks:
        if rank == 1:
            pudding_scores.append(6)
        elif rank == lowest_rank:
            pudding_scores.append(-6)
        else:
            pudding_scores.append(0)
    return pudding_scores

class SushiGo:
    def __init__(self, players):
        self.cards = self.get_all_cards()
        self.players = players
        self.all_scores = [0] * len(players)
        self.starting_hand_size = self.determine_starting_hand_size()
        self.train = True
    
    def determine_starting_hand_size(self):
        num_players = len(self.players)
        if num_players == 2:
            return 10
        elif num_players == 3:
            return 9
        elif num_players == 4:
            return 8
        elif num_players == 5:
            return 7
        raise Exception('Unrecognized number of players must be between 2 - 5 players')
    
    def get_all_cards(self):
        cards = []
        cards.extend([TEMPURA] * 14)
        cards.extend([SASHIMI] * 14)
        cards.extend([DUMPLINGS] * 14)
        cards.extend([TWO_MAKI] * 12)
        cards.extend([THREE_MAKI] * 8)
        cards.extend([ONE_MAKI] * 6)
        cards.extend([SALMON_NIGIRI] * 10)
        cards.extend([SQUID_NIGIRI] * 5)
        cards.extend([EGG_NIGIRI] * 5)
        cards.extend([PUDDING] * 10)
        cards.extend([WASABI] * 6)
        # cards.extend([CHOPSTICKS] * 4) # Leaving this out for now to simplify
        return cards
    
    def reset(self):
        self.cards = self.get_all_cards()
        self.all_scores = []
    
    def pass_hands_around(self): # Pass all the hands in a circle
        last_hand = self.players[-1].hand
        for i in range(len(self.players) - 1, 0, -1):
            self.players[i].hand = self.players[i - 1].hand  
        self.players[0].hand = last_hand  

    def deal_cards(self):
        for player in self.players:
            for _ in range(self.starting_hand_size):
                random.shuffle(self.cards)
                player.hand.append(self.cards.pop())

    def play(self, num_rounds=3): # 3 rounds per game just like in real life
        self.all_scores = [0] * len(self.players)
        for player in self.players:
            player.next_round()

        for round in range(num_rounds):
            self.deal_cards()
            for hand_size in range(self.starting_hand_size): # Play until all hands are empty
                for player in self.players:
                    player.pick_card()
                self.pass_hands_around()
            for i, player in enumerate(self.players):
                self.all_scores[i] += player.get_score()

            maki_score = get_maki_score([player.board[MAKI] for player in self.players])
            for i in range(len(self.players)):
                self.all_scores[i] += maki_score[i] 

        # Pudding is only scored at the end of each game
        pudding_score = get_pudding_score([player.board[PUDDING] for player in self.players])
        for i in range(len(pudding_score)):
            self.all_scores[i] += pudding_score[i]
        
        # Give reward to those that need it (Q-learning player)
        highest_score = max(self.all_scores)

        if self.train: # Only feed reward if we are training
            for i, p in enumerate(self.players):
                if self.all_scores[i] == highest_score:
                    #self.players_games_won[i] += 1
                    p.reward(len(self.players)) # Higher reward the more players there are
                else:
                    p.reward(-1) # How could you lose??

        #for i, player in enumerate(self.players):
            #print(player.name + ' scored: ' + str(self.all_scores[i]))
        #print('The winner was: ' + self.players[self.all_scores.index(highest_score)].name + ' with a score of ' + str(highest_score))

        self.players_games_won[self.all_scores.index(highest_score)] += 1



    def play_games(self, num_games=1, num_rounds=3):
        self.players_games_won = [0] * len(self.players)
        for _ in range(num_games):
            self.reset()
            self.play(num_rounds) 
        print(self.players_games_won)

class SushiGo:
    def __init__(self, players):
        self.cards = self.get_all_cards()
        self.players = players
        self.all_scores = [0] * len(players)
        self.starting_hand_size = self.determine_starting_hand_size()
        self.train = True
    
    def determine_starting_hand_size(self):
        num_players = len(self.players)
        if num_players == 2:
            return 10
        elif num_players == 3:
            return 9
        elif num_players == 4:
            return 8
        elif num_players == 5:
            return 7
        raise Exception('Unrecognized number of players must be between 2 - 5 players')
    
    def get_all_cards(self):
        cards = []
        cards.extend([TEMPURA] * 14)
        cards.extend([SASHIMI] * 14)
        cards.extend([DUMPLINGS] * 14)
        cards.extend([TWO_MAKI] * 12)
        cards.extend([THREE_MAKI] * 8)
        cards.extend([ONE_MAKI] * 6)
        cards.extend([SALMON_NIGIRI] * 10)
        cards.extend([SQUID_NIGIRI] * 5)
        cards.extend([EGG_NIGIRI] * 5)
        cards.extend([PUDDING] * 10)
        cards.extend([WASABI] * 6)
        # cards.extend([CHOPSTICKS] * 4) # Leaving this out for now to simplify
        return cards
    
    def reset(self):
        self.cards = self.get_all_cards()
        self.all_scores = []
    
    def pass_hands_around(self): # Pass all the hands in a circle
        last_hand = self.players[-1].hand
        for i in range(len(self.players) - 1, 0, -1):
            self.players[i].hand = self.players[i - 1].hand  
        self.players[0].hand = last_hand  

    def deal_cards(self):
        for player in self.players:
            for _ in range(self.starting_hand_size):
                random.shuffle(self.cards)
                player.hand.append(self.cards.pop())

    def play(self, num_rounds=3): # 3 rounds per game just like in real life
        self.all_scores = [0] * len(self.players)
        for player in self.players:
            player.next_round()

        for round in range(num_rounds):
            self.deal_cards()
            for hand_size in range(self.starting_hand_size): # Play until all hands are empty
                for player in self.players:
                    player.pick_card()
                self.pass_hands_around()
            for i, player in enumerate(self.players):
                self.all_scores[i] += player.get_score()

            maki_score = get_maki_score([player.board[MAKI] for player in self.players])
            for i in range(len(self.players)):
                self.all_scores[i] += maki_score[i] 

        # Pudding is only scored at the end of each game
        pudding_score = get_pudding_score([player.board[PUDDING] for player in self.players])
        for i in range(len(pudding_score)):
            self.all_scores[i] += pudding_score[i]
        
        # Give reward to those that need it (Q-learning player)
        highest_score = max(self.all_scores)

        if self.train: # Only feed reward if we are training
            for i, p in enumerate(self.players):
                if self.all_scores[i] == highest_score:
                    #self.players_games_won[i] += 1
                    p.reward(len(self.players)) # Higher reward the more players there are
                else:
                    p.reward(-1) # How could you lose??

        #for i, player in enumerate(self.players):
            #print(player.name + ' scored: ' + str(self.all_scores[i]))
        #print('The winner was: ' + self.players[self.all_scores.index(highest_score)].name + ' with a score of ' + str(highest_score))

        self.players_games_won[self.all_scores.index(highest_score)] += 1



    def play_games(self, num_games=1, num_rounds=3):
        self.players_games_won = [0] * len(self.players)
        for _ in range(num_games):
            self.reset()
            self.play(num_rounds) 
        print(self.players_games_won)

from collections import defaultdict
class Player:
    def __init__(self, name):
        self.board = defaultdict(int)
        self.hand = []
        self.name = name

    def pick_card(self):
        raise NotImplementedError

    def get_score(self):
        return score(self.board)
    
    def reward(self, reward):
        raise NotImplementedError

    def next_round(self):
        self.hand = []
        pudding_count = self.board[PUDDING] # Save pudding count
        self.board = defaultdict(int)
        self.board[PUDDING] = pudding_count

    def next_game(self):
        self.hand = []
        self.board = defaultdict(int)

class QLearnPlayer(Player):

    def __init__(self, name):
        super().__init__(name)
        self.learning_rate = 0.01
        self.disc_factor = 0.95
        self.Q = {}
        self.states_actions = []

    def pick_card(self):
        action = None
        max_value = float('-inf')
        orig_board = copy.deepcopy(self.board)
        for possible_card in set(self.hand):
            value = self.Q.get((str(self.board), possible_card), random.random() / 1e5)
            if value > max_value:
                max_value = value
                action = possible_card

        assert action is not None
        
        self.hand.remove(action)
        add_card_to_board(self.board, action)
        self.states_actions.append((orig_board, action))

    def get_score(self):
        return score(self.board)

    def max_Qprime_aprime(self, state_action):
        state, action = state_action
        state_cpy = copy.deepcopy(state)
        add_card_to_board(state_cpy, action)

        sprime_aprime = []
        for state, action in self.states_actions:
            if state == state_cpy:
                sprime_aprime.append((str(state_cpy), action))
        
        max = float('-inf')
        result_val = 0
        for sp_ap in sprime_aprime:
            temp = self.Q.get(sp_ap, random.random() / 1e5)
            if temp > max:
                result_val = temp
                max = result_val
        return result_val


    def reward(self, reward):
        for state, action in self.states_actions:
            str_state = str(state)
            if (str_state, action) not in self.Q:
                self.Q[(str_state, action)] = 0
            self.Q[(str_state, action)] += self.learning_rate * (reward + self.disc_factor * self.max_Qprime_aprime((state, action)) - self.Q[(str_state, action)])

    def next_round(self):
        super().next_round()
        self.states = []
        self.states.append(self.board)

class RandomPlayer(Player):

    def __init__(self, name):
        super().__init__(name)
        self.next_round()

    def pick_card(self):
        random.shuffle(self.hand)
        action = self.hand.pop()
        add_card_to_board(self.board, action)
        return

    def get_score(self):
        return score(self.board)

    def reward(self, reward):
        return

class DumplingPlayer(Player):

    def __init__(self, name):
        super().__init__(name)
        self.next_round()

    def pick_card(self):
        if DUMPLINGS in self.hand:
            action = self.hand.remove(DUMPLINGS)
        else: 
            random.shuffle(self.hand)
            action = self.hand.pop()
        add_card_to_board(self.board, action)
        return

    def get_score(self):
        return score(self.board)

    def reward(self, reward):
        return