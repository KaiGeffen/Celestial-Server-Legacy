import torch
import random
import numpy as np
from collections import deque
# from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
# from helper import plot

import CardCodec
from logic.ServerController import ServerController


# For actions, 0th is pass, 1-6 are play that card

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
CHOICES = 7

class Agent:
	def __init__(self, player_number):
		self.player_number = player_number

		self.n_games = 0
		self.epsilon = 0 # randomness
		self.gamma = 0.9 # discount rate
		self.memory = deque(maxlen=MAX_MEMORY) # popleft()

		# TODO 11 should be 6 or 60 for building the deck
		self.model = Linear_QNet(CHOICES, 256, 3)
		self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
	
	def get_state(self, game):
		state = game.get_client_model(self.player_number)

		l = [hash(str(v)) for v in state.values()]

		return np.array(l, dtype=int)

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

	def get_action(self, state):
		# random moves: tradeoff exploration / exploitation
		self.epsilon = 80 - self.n_games
		# final_move = [0, 0,0,0, 0,0,0]

		valid_actions = [10] # Can always pass
		# for i in range(6):
		# 	if state.cards_playable[i]:
		# 		valid_actions.append(i)

		if random.randint(0, 200) < self.epsilon:
			move = random.choice(valid_actions)
			return 10
		else:
			state0 = torch.tensor(state, dtype=torch.float)
			prediction = self.model(state0)
			move = torch.argmax(prediction).item()
			return 10
			# if move in valid_actions:
			# 	return move
			# else:
			# 	return 10


def train():
	agent0 = Agent(0)
	agent1 = Agent(1)

	# TODO: Form the deck agent will use (Same each game)
	deck = get_deck()
	their_deck = get_deck()
	game = ServerController(deck, their_deck, 0, 0)

	while True:
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
		state0 = agent.get_state(game)

		# Get the action
		action = agent.get_action(state0)

		# Perform action and get new state
		# a = None # Integer version of the action vector
		# for i in range(len(action)):
		# 	if action[i]:
		# 		a = i
		game.attempt_play(player_number, action)
		state1 = agent.get_state(game)

		# Determine the reward/done of new state
		score = 0
		if state1.winner == None:
			done = False
			reward = 0
		elif state1.winner == 0:
			done = True
			reward = 1
		else:
			done = True
			reward = -1

		# Train short memory
		agent.train_short_memory(state0, action, reward, state1, done)

		# Remember
		agent.remember(state0, action, reward, state1, done)

		if done:
			# TODO Make a new game, write to long memory for both agents
			# Train the long memory
			game.reset()

			agent.n_games += 1

			agent.train_long_memory()

	# TODO: Save the agent model at the end

def get_deck():
	s = '65:65:4:4:4:26:26:33:33:33:31:58:53:53:62'

	deck = CardCodec.decode_deck(s)

	return deck

if __name__ == '__main__':
	train()
