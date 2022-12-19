import torch
import random
import numpy as np
import time
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
# Vectors that express any given state
STATE_SIZE = 7 + 30 + 1 + 30*2 + 3 + 3
CHOICES = 7

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
	
	# Pass in the generic client_state that the server conveys
	def get_state(self, state):

		# TODO For each card have a count of it in your hand, then also have an ordering
		# This uncompressed format makes the training work better

		# TODO Dynamic card points (Child / Pet)

		# Form the least of features
		l = []

		# Our hand
		stack = CardCodec.decode_deck(state['hand'])
		for i in range(6):
			if len(stack) > i:
				l.append(stack[i].id)
			else:
				l.append(-1)

		# Opponent Hand
		l.append(state['opp_hand'])

		# Our deck
		stack = CardCodec.decode_deck(state['deck'])
		for i in range(30): # Large number
			if len(stack) > i:
				l.append(stack[i].id)
			else:
				l.append(-1)

		# Their deck
		l.append(state['opp_deck'])

		# Our pile
		pile = CardCodec.decode_deck(state['pile'][0])
		for i in range(30): # Large number
			if len(stack) > i:
				l.append(stack[i].id)
			else:
				l.append(-1)

		# Their pile
		pile = CardCodec.decode_deck(state['pile'][1])
		for i in range(30): # Large number
			if len(stack) > i:
				l.append(stack[i].id)
			else:
				l.append(-1)

		# Max mana
		l.append(state['max_mana'][0])

		# Current mana
		l.append(state['mana'])

		# Passes
		l.append(state['passes'])

		# Vision
		l.append(state['vision'])

		# Statuses
		l.append(hash(state['status']))
		l.append(hash(state['opp_status']))

		# {
		#     'hand': CardCodec.encode_deck(self.hand[player]),
		#     'opp_hand': len(self.hand[player ^ 1]),
		#     'deck': CardCodec.encode_deck(sorted(self.deck[player], key=deck_sort)),
		#     'opp_deck': len(self.deck[player ^ 1]),
		#     'pile': list(map(CardCodec.encode_deck, self.pile[::slice_step])),
		#     # Only send the opponent's last shuffle
		#     'last_shuffle': CardCodec.encode_deck(sorted(self.last_shuffle[player ^ 1], key=deck_sort)),
		#     'expended': list(map(CardCodec.encode_deck, self.expended[::slice_step])),
		#     'wins': self.wins[::slice_step],
		#     'max_mana': self.max_mana[::slice_step],
		#     'mana': self.mana[player],
		#     'status': CardCodec.encode_statuses(self.status[player]),
		#     'opp_status': CardCodec.encode_statuses(self.status[player ^ 1]),
		#     'story': self.get_relative_story(player, total_vision=is_recap),
		#     'priority': self.priority ^ player,
		#     'passes': self.passes,
		#     'recap': CardCodec.encode_recap(relative_recap, shallow=is_recap),
		#     'mulligans_complete': self.mulligans_complete[::slice_step],
		#     'version_number': self.version_no,
		#     'cards_playable': cards_playable,
		#     'vision': self.vision[player],
		#     'winner': None if self.get_winner() is None else self.get_winner() ^ player,
		#     'score': self.score[::slice_step],
		#     'sound_effect': self.sound_effect,
		#     'animations': self.hide_opp_animations(self.animations[::slice_step]),
		#     'costs': costs,
		#     'avatars': self.avatars[::slice_step],
		#     'round_results': self.round_results[::slice_step]
		# }
		# winner = state['winner']
		# if winner is None:
		# 	winner = -1
		# l = [winner, state['opp_hand'], len(state['hand'])]

		# Append all values that 
		# for v in state.values():
		# 	try:
		# 		l.append(int(v))
		# 	except:
		# 		l.append(-1)


		# for v in state.values():
		
		# for i in range(4):
		# 	l.append(99)
			

		# l = [hash(str(v)) for v in state.values()]

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
			for best_choice in torch.argsort(prediction):
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
		client_state = game.get_client_model(player_number)
		state0 = agent.get_state(client_state)

		# Get the action
		valid_actions = agent.get_valid_actions(client_state)
		action = agent.get_action(state0, valid_actions)

		# Perform action and get new state
		# a = None # Integer version of the action vector
		# for i in range(len(action)):
		# 	if action[i]:
		# 		a = i
		result = game.on_player_input(player_number, action)
		state1 = agent.get_state(game.get_client_model(player_number))

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
			# Expensive, todo
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

	# TODO: Save the agent model at the end

def get_deck():
	s = '65:65:4:4:4:26:26:33:33:33:31:58:53:53:62'

	deck = CardCodec.decode_deck(s)

	return deck

if __name__ == '__main__':
	train()
