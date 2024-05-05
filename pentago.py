import sys
from random import randint
from constants.ui import PRINT_BOARD_PLACE_MARBLE, PRINT_BOARD_ROTATE, PRINT_BOARD_FINISHED
from game import Game, player_finished_his_turn

from board import add_marble_to_board, is_board_full, get_position_if_valid, rotate_quarter_of_board, is_at_least_one_quarter_symetric

from render import print_game

from win import get_all_marbles_combinations_correctly_aligned
#player1 =AI
#player2 =human
def init_game():
    try:
        name_player_1 = ask_player_name("Player 1")
        name_player_2 = ask_player_name("Player 2")

        player_who_start = randint(1,2)
        game = Game(name_player_1, name_player_2, player_who_start)

        correct_combinations = []

        while is_board_full(game.board) == False and len(correct_combinations) == 0:
            print_game(game, PRINT_BOARD_PLACE_MARBLE)
            game.board = ask_player_to_place_marble(
                game.board, game.current_player_id
            )

            game.one_quarter_is_symetric = is_at_least_one_quarter_symetric(game.board)
    
            print_game(game, PRINT_BOARD_ROTATE)
            game.board = ask_player_to_rotate_quarter(game.board, game.one_quarter_is_symetric)

            game.current_player_id = player_finished_his_turn(
                game.current_player_id
            )

            correct_combinations = get_all_marbles_combinations_correctly_aligned(game.board)


        print_game(game, PRINT_BOARD_FINISHED, True, correct_combinations)

    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        print("\nIt was fun, see you soon !")

def ask_player_name(default_name):
    name = input(" " + default_name +", enter your name: (" +default_name+ ") ")
    if len(name) == 0:
        return default_name

    return name

def ask_player_to_place_marble(board, current_player_id):
    player_input_value_is_wrong = True;

    while player_input_value_is_wrong:
        player_input_value = input(" Place a marble: ")

        try:
            board = add_marble_to_board(board, current_player_id, player_input_value)
            player_input_value_is_wrong = False
        except ValueError:
            print(" Please play on a valid & empty cell")
            player_input_value_is_wrong = True;

    return board

def ask_player_to_rotate_quarter(board, one_quarter_is_symetric):
    player_input_value_is_wrong = True;
    
    while player_input_value_is_wrong:
        string = " Now rotate one quarter: "
        if one_quarter_is_symetric == True:
            string += "(enter to skip) "

        player_input_value = input(string)
        
        try:
            board = rotate_quarter_of_board(board, player_input_value, one_quarter_is_symetric)
            player_input_value_is_wrong = False
        except ValueError:
            print("Please enter a valid rotation (1..8): ")
            player_input_value_is_wrong = True

    return board

if __name__ == "__main__":
    init_game()
    


import numpy as np
import pickle

BOARD_ROWS = 6
BOARD_COLS = 6
lengte_winnen=4

class State:
    def __init__(self, p1, p2):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        # init p1 plays first
        self.playerSymbol = 1

    # get unique hash of current board state
    def getHash(self):
        self.boardHash = str(self.board.reshape(BOARD_COLS * BOARD_ROWS))
        return self.boardHash

    def winner(self):
        # row
        for i in range(BOARD_ROWS):
            if sum(self.board[i, :]) == lengte_winnen:
                self.isEnd = True
                return 1
            if sum(self.board[i, :]) == -lengte_winnen:
                self.isEnd = True
                return -1
        # col
        for i in range(BOARD_COLS):
            if sum(self.board[:, i]) == lengte_winnen:
                self.isEnd = True
                return 1
            if sum(self.board[:, i]) == -lengte_winnen:
                self.isEnd = True
                return -1
        # diagonal
        diag_sum1 = sum([self.board[i, i] for i in range(BOARD_COLS)])
        diag_sum2 = sum([self.board[i, BOARD_COLS - i - 1] for i in range(BOARD_COLS)])
        diag_sum = max(abs(diag_sum1), abs(diag_sum2))
        if diag_sum == lengte_winnen:
            self.isEnd = True
            if diag_sum1 == lengte_winnen or diag_sum2 == lengte_winnen:
                return 1
            else:
                return -1

        # tie
        # no available positions
        if len(self.availablePositions()) == 0:
            self.isEnd = True
            return 0
        # not end
        self.isEnd = False
        return None

    def availablePositions(self):
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if self.board[i, j] == 0:
                    positions.append((i, j))  # need to be tuple
        return positions

    def updateState(self, position):
        self.board[position] = self.playerSymbol
        # switch to another player
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1

    # only when game ends
    def giveReward(self):
        result = self.winner()
        # backpropagate reward
        if result == 1:
            self.p1.feedReward(1)
            self.p2.feedReward(0)
        elif result == -1:
            self.p1.feedReward(0)
            self.p2.feedReward(1)
        else:
            self.p1.feedReward(0.1)
            self.p2.feedReward(0.5)

    # board reset
    def reset(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 1

    def play(self, rounds=100):
        for i in range(rounds):
            if i % 5000 == 0:
                print("Rounds {}".format(i))
            while not self.isEnd:
                # Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
                # take action and upate board state
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                # check board status if it is end

                win = self.winner()
                if win is not None:
                    # self.showBoard()
                    # ended with p1 either win or draw
                    self.giveReward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break

                else:
                    # Player 2
                    positions = self.availablePositions()
                    p2_action = self.p2.chooseAction(positions, self.board, self.playerSymbol)
                    self.updateState(p2_action)
                    board_hash = self.getHash()
                    self.p2.addState(board_hash)

                    win = self.winner()
                    if win is not None:
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break

    # play with human
    def play2(self):
        while not self.isEnd:
            # Player 1
            positions = self.availablePositions()
            p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
            # take action and upate board state
            self.updateState(p1_action)
            self.showBoard()
            # check board status if it is end
            win = self.winner()
            if win is not None:
                if win == 1:
                    print(self.p1.name, "wins!")
                else:
                    print("tie!")
                self.reset()
                break

            else:
                # Player 2
                positions = self.availablePositions()
                p2_action = self.p2.chooseAction(positions)

                self.updateState(p2_action)
                self.showBoard()
                win = self.winner()
                if win is not None:
                    if win == -1:
                        print(self.p2.name, "wins!")
                    else:
                        print("tie!")
                    self.reset()
                    break

class Player:
    def __init__(self, name, exp_rate=1):#pas aan naar 0 of 0.1 bij gebruik na training
        self.name = name
        self.states = []  # record all positions taken
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {}  # state -> value

    def getHash(self, board):
        boardHash = str(board.reshape(BOARD_COLS * BOARD_ROWS))
        return boardHash

    def chooseAction(self, positions, current_board, symbol):
        if np.random.uniform(0, 1) <= self.exp_rate:
            # take random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else:
            value_max = -999
            for p in positions:
                next_board = current_board.copy()
                next_board[p] = symbol
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
                # print("value", value)
                if value >= value_max:
                    value_max = value
                    action = p
        # print("{} takes action {}".format(self.name, action))
        return action

    # append a hash state
    def addState(self, state):
        self.states.append(state)

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        for st in reversed(self.states):
            if self.states_value.get(st) is None:
                self.states_value[st] = 0
            self.states_value[st] += self.lr * (self.decay_gamma * reward - self.states_value[st])
            reward = self.states_value[st]

    def reset(self):
        self.states = []

    def savePolicy(self):
        fw = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.states_value = pickle.load(fr)
        fr.close()


class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def chooseAction(self, positions):
        while True:
            col=-1
            row=-1
            while col==-1 or row==-1:#niet gedefinieerd
                try:
                    row = int(input("Input your action row:"))-1
                    col = int(input("Input your action col:"))-1
                except:
                    print("geef een integer")
        
            action = (row, col)
            if action in positions:
                return action

    # append a hash state
    def addState(self, state):
        pass

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        pass

    def reset(self):
        pass


if __name__ == "__main__":
    # training
    p1 = Player("p1")
    p2 = Player("p2")

    st = State(p1, p2)
    print("training...")
    st.play(int(input("hoeveel keer moet er getraind worden?")))

    # play with human
    p1 = Player("computer", exp_rate=0)
    p1.loadPolicy("policy_p1")

    p2 = HumanPlayer("human")

    st = State(p1, p2)
    st.play2()