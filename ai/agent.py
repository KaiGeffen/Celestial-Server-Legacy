import torch
import random
import numpy as np
import time
from collections import deque
# from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from Translator import translate_state
# from helper import plot

import CardCodec
from logic.ServerController import ServerController


# For actions, 0th is pass, 1-6 are play that card

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
# Vectors that express any given state
STATE_SIZE = 7 + 30 + 1 + 30*2 + 3 + 3 + 1
CHOICES = 7
# How many games to play before saving the model
N_GAMES = 1000

class Agent:
	def __init__(self, player_number):
		self.player_number = player_number

		self.n_games = 0
		self.epsilon = 0 # randomness
		self.gamma = 0.9 # discount rate
		self.memory = deque(maxlen=MAX_MEMORY) # popleft()

		# TODO 11 should be 6 or 60 for building the deck
		self.model = Linear_QNet(STATE_SIZE, 256, CHOICES)
		self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

	def remember(self, state, action, reward, next_state, done):
		self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

	def train_long_memory(self):
		if len(self.memory) > BATCH_SIZE:
			mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
		else:
			mini_sample = self.memory

		states, actions, rewards, next_states, dones = zip(*mini_sample)
		self.trainer.train_step(states, actions, rewards, next_states, dones)

	def train_short_memory(self, state, action, reward, next_state, done):
		self.trainer.train_step(state, action, reward, next_state, done)

	# NOTE Model views passing as 6 instead of 10!
	# Return list of valid actions (As index in hand)
	def get_valid_actions(self, client_state):
		# Passing is always allowed
		result = [6]

		playable_list = client_state['cards_playable']
		for i in range(len(playable_list)):
			if playable_list[i]:
				result.append(i)

		return result

	def get_action(self, state, valid_actions):
		# random moves: tradeoff exploration / exploitation
		self.epsilon = 80 - self.n_games
		# final_move = [0, 0,0,0, 0,0,0]

		if random.randint(0, 200) < self.epsilon:
			move = random.choice(valid_actions)
			return move
		else:
			# Get the best prediction 
			state0 = torch.tensor(state, dtype=torch.float)
			prediction = self.model(state0)

			# Get the best options in order
			for best_choice in torch.argsort(prediction, descending=True):
				if best_choice in valid_actions:
					return best_choice
			# print()
			# move = torch.argmax(prediction).item()

			# # Pass if what we want to do isn't valid
			# if move in valid_actions:
			# 	return move
			# else:
			# 	return 10


def train():
	start_time = time.time()

	agent0 = Agent(0)
	agent1 = Agent(1)

	# TODO: Form the deck agent will use (Same each game)
	deck = get_deck()
	their_deck = get_deck()
	game = ServerController(deck, their_deck, 0, 0)
	game.start()
	# TODO Mulligans
	game.do_mulligan(0, [False, False, False])
	game.do_mulligan(1, [False, False, False])

	while agent0.n_games < N_GAMES:
		# Determine which agent is acting/learning
		agent = None
		player_number = None
		
		if game.model.priority == 0:
			agent = agent0
			player_number = 0
		else:
			agent = agent1
			player_number = 1

		# Get the current state
		client_state = game.get_client_model(player_number)
		state0 = translate_state(client_state)

		# Get the action
		valid_actions = agent.get_valid_actions(client_state)
		action = agent.get_action(state0, valid_actions)

		# Perform action and get new state
		# a = None # Integer version of the action vector
		# for i in range(len(action)):
		# 	if action[i]:
		# 		a = i
		result = game.on_player_input(player_number, action)
		state1 = translate_state(game.get_client_model(player_number))

		# Determine the reward/done of new state
		done = reward = None
		if client_state['winner'] is None:
			done = False
			reward = 0
		elif client_state['winner'] == 0:
			done = True
			reward = 1
		# This never occurs because the player with 5 wins starts the round
		# else:
			# done = True
			# reward = -1

		# Train short memory
		agent.train_short_memory(state0, action, reward, state1, done)

		# Remember
		agent.remember(state0, action, reward, state1, done)

		# If the game is done (Has a winner) or has gone on for too long, start a new game
		if done or game.model.version_no > 10 ** 5:
			for agent in [agent0, agent1]:
				agent.n_games += 1
			
			round_results = client_state['round_results']
			delta_t = time.time() - start_time
			start_time = time.time()
			print(f'Round Scores Game {agent.n_games} (Took {delta_t}):\n{round_results[0]}\n{round_results[1]}')

			# TODO Make a new game, write to long memory for both agents
			# Train the long memory
			# TODO: Form the deck agent will use (Same each game)
			deck = get_deck()
			their_deck = get_deck()
			game = ServerController(deck, their_deck, 0, 0)
			game.start()
			# TODO Mulligans
			game.do_mulligan(0, [False, False, False])
			game.do_mulligan(1, [False, False, False])

			# TODO Al suggest not needed, reconsider this
			agent.train_long_memory()

	# TODO Save and manage both agents
	agent0.model.save()

def get_deck():
	s = '65:65:4:4:4:26:26:33:33:33:31:58:53:53:62'

	deck = CardCodec.decode_deck(s)

	return deck

if __name__ == '__main__':
	train()
