#Matthew Oakley
#CSCI 3202 Assignment 8
#Speech tagging/recognition using Hidden Markov Models

from __future__ import division

#Class for Tag objects used during transition probability calculation
class Tag():
	tag_name = ""
	total = 0

#Open training file
def open_file(filename):
	lines = []
	lines.append("SSSS")

	#Append <s> and </s> tags
	with open(filename, "r") as sentences:
		for line in sentences:
			if line == "\n":
				lines.append("EEEE")
				lines.append("SSSS")

			else:
				lines.append(line.rstrip())

	lines.append("EEEE")

	#Return list of all words/tags in training file
	ret = lines[:len(lines) - 2]
	return ret

#Calculate transition probability from training set
def transition(lines):
	tags = {}
	tag_names = []

	#Create Tag objects (corresponds to states)
	for line in lines:
		if "\t" in line:
			index = line.index("\t") + 1
			tag = line[index:]
		else:
			tag = line

		#Calculate total number of appearances for each tag
		if tag not in tags:
			new_tag = Tag()
			new_tag.tag_name = tag
			new_tag.total = 1
			tags[tag] = new_tag
		else:
			tags[tag].total += 1

		#Store tag identifiers in list for reference
		if tag not in tag_names:
			tag_names.append(tag)

	#Create all, unique 'next' state attributes for each states
	for tag in tags:
		cur_tag = tags[tag]
		for tag_name in tag_names:
			setattr(cur_tag, tag_name, 0)

	#Calculate count(TAGi TAGj)
	for i in range(1, len(lines)):
		cur = lines[i - 1]
		after = lines[i]
		if "\t" in cur:
			index = cur.index("\t") + 1
			cur_tag = cur[index:]
		else:
			cur_tag = cur

		if "\t" in after:
			index = after.index("\t") + 1
			after_tag = after[index:]
		else:
			after_tag = after

		cur_obj = tags[cur_tag]
		setattr(cur_obj, after_tag, getattr(cur_obj, after_tag) + 1)

	#Return dictionary of Tag objects and reference-list for tag names
	return tags, tag_names

#Calculate emission probability from training set
def emission(lines, tags):
	observations = {}
	words = []
	states = []

	#Populate observations dictionary with empty dictionary for each unique state
	for line in lines:
		if "\t" in line:
			index = line.index("\t") + 1
			obv = line[:index - 1]
			state = line[index:]
			if obv not in words:
				words.append(obv)

		else:
			obv = line
			state = line
			if obv not in words:
				words.append(obv)

		if state not in observations:
			observations[state] = {}

		if state not in states:
			states.append(state)

	#Calculate count(word AND TAG)
	for line in lines:
		if "\t" in line:
			index = line.index("\t") + 1
			obv = line[:index - 1]
			state = line[index:]

		else:
			obv = line
			state = line

		cur_state = observations[state]
		if obv not in cur_state:
			cur_state[obv] = 1
		else:
			cur_state[obv] += 1

	#Return dictionary of dictionary of tags and reference-list for words
	return observations, words

#Viterbi algorithm
#NOTE: I am using/modifying the provided "In-class viterbi.py" file on Moodle
def viterbi(obs, states, start_p, trans_p, emit_p):
	V = [{}]

	#Calculate first entry in the transition matrix
	for st in states:
		try:
			emission_prob = emit_p[st][obs[0]]
		except KeyError:
			emission_prob = 0.0
		V[0][st] = {"prob": start_p[st] * emission_prob, "prev": None}

	#Calculate rest of transition matrix
	for t in range(1, len(obs)):
		V.append({})
		for st in states:
			max_tr_prob = max(V[t-1][prev_st]["prob"]*trans_p[prev_st][st] for prev_st in states)
			for prev_st in states:
				if V[t-1][prev_st]["prob"] * trans_p[prev_st][st] == max_tr_prob:
					try:
						emission_prob = emit_p[st][obs[t]]
					except KeyError:
						emission_prob = 0.0
					max_prob = max_tr_prob * emission_prob
					V[t][st] = {"prob": max_prob, "prev": prev_st}
					break

	opt = []
	max_prob = max(value["prob"] for value in V[-1].values())
	previous = None

	# Get most probable state and its backtrack
	for st, data in V[-1].items():
		if data["prob"] == max_prob:
			opt.append(st)
			previous = st
			break

	# Follow the backtrack till the first observation
	for t in range(len(V) - 2, -1, -1):
		opt.insert(0, V[t + 1][previous]["prev"])
		previous = V[t + 1][previous]["prev"]

	opt = opt[1:len(opt) - 1]

	return 'The steps of states are: \n' + "-->\t" + ' '.join(opt)

def dptable(V):
	yield " ".join(("%12d" % i) for i in range(len(V)))
	for state in V[0]:
		yield "%.7s: " % state + " ".join("%.7s" % ("%f" % v[state]["prob"]) for v in V)



if __name__ == "__main__":

	#Retrieve user-inputted sentence
	sentence = raw_input("Enter a sentence: ")

	print "...Opening file"
	lines = open_file("penntree.tag")

	#Tags: Dictionary of different Tag objects
	#Each tag object has attributes corresponding to the number of 'next' tags
	print "...Training on transition probability"
	tags, tag_names = transition(lines)

	#Words: Dictionary of different Word objects
	#Each word object has attributes corresponding to the number of associated tags
	print "...Training on emission probability"
	obvs, words = emission(lines, tag_names)
	
	#States are the different tags
	states = []
	for tag in tag_names:
		states.append(tag)

	#Parse user-inputted sentence and store in observations list
	observations = []
	observations.append("SSSS")
	key_words = sentence.split()
	for i in range(0, len(key_words) - 1):
		observations.append(key_words[i])
	observations.append(key_words[-1][:len(key_words[-1]) - 1])
	observations.append(key_words[-1][-1])
	observations.append("EEEE")

	#Start probability is that we're in a 'SSSS' state 100% of the time
	print "...Calculating start probability"
	start_probability = {}
	for state in states:
		if state != "SSSS":
			start_probability[state] = 0.0
		else:
			start_probability[state] = 1.0

	#Transition probability is what probability our 'next' state will be
	print "...Calculating transition probabilities"
	transition_probability = {}
	for state in states:
		state_obj = tags[state]
		transition_probability[state_obj.tag_name] = {}
		for tag in tag_names:
			follow_num = getattr(state_obj, tag)
			total = state_obj.total
			transition_probability[state_obj.tag_name][tag] = follow_num / total

	#Emission probability is what probability our state is associated with a specific word
	print "...Calculating emission probabilities"
	for obv in obvs:
		state_total = tags[obv].total
		for word in obvs[obv]:
			obvs[obv][word] /= state_total
	emission_probability = obvs

	print "\n"
	print viterbi(observations, states, start_probability, transition_probability, emission_probability)
	print "\n"
	print "...EXITING"

