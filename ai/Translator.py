import numpy as np
import CardCodec

# Pass in the generic client_state that the server conveys and translate it to state as the model sees it
def translate_state(state):

	# TODO For each card have a count of it in your hand, then also have an ordering
	# This uncompressed format makes the training work better

	# TODO Dynamic card points (Child / Pet)

	# Form the least of features
	l = []

	# Have we played any cards? TODO Use story not mana
	l.append(state['max_mana'][0] - state['mana'])

	# Our hand
	stack = CardCodec.decode_deck(state['hand'])
	for i in range(6):
		if len(stack) > i:
			l.append(stack[i].id)
		else:
			l.append(-1)

	# Opponent Hand
	l.append(len(state['opp_hand']))

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
