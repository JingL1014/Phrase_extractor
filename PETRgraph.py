# -*- coding: utf-8 -*-


import networkx as nx


class Sentence:
	"""
    Holds the information of a sentence and its tree.
    
    Methods
    -------
    
    __init__ : Initialization and instantiation
    
    str_to_graph: Reads UD parse into memory
	"""

	def __init__(self, parse, text, date):
		self.parse = parse
		self.agent = ""
		self.ID = -1
		self.actor = ""
		self.date = date
		self.longlat = (-1,-1)
		self.verbs = []
		self.txt = ""
		self.udgraph = self.str_to_graph(parse)
		self.verb_analysis = {}
		self.events = []
		self.metadata = {'nouns': [], 'verbs':[],'triplets':[]}
    

	def str_to_graph(self,str):
		dpgraph = nx.DiGraph()
		parsed = self.parse.split("\n")
		#print(parsed)

		dpgraph.add_node(0, token = 'ROOT')
		for p in parsed:
			temp = p.split("\t")

			#print(temp)
			dpgraph.add_node(int(temp[0]), token = temp[1], pos = temp[3])
			dpgraph.add_edge(int(temp[6]),int(temp[0]),relation = temp[7])

		return dpgraph


	def get_nounPharse(self, nounhead):
		npIDs=[]
		if(self.udgraph.node[nounhead]['pos'] in ['NOUN','ADJ','PROPN']):
			allsuccessors = nx.dfs_successors(self.udgraph,nounhead)

			flag = True
			parents = [nounhead]
			
			while len(parents)>0:
				temp = []
				for parent in parents:
					if parent in allsuccessors.keys():
						for child in allsuccessors[parent]:
							if (parent==nounhead and self.udgraph[parent][child]['relation'] not in ['acl','acl:relcl','cc','conj','appos','punct']) or (parent!=nounhead and self.udgraph[parent][child]['relation'] not in ['acl','acl:relcl','appos','dobj','punct']):
								#if parent!=nounhead or self.udgraph[parent][child]['relation'] not in []:
								npIDs.append(child)
								temp.append(child)
				parents = temp
			
			'''
			for parent,child in allsuccessors.items():
				print(str(parent))
				print(child)
			'''		
			#raw_input(" ")

			#for value in allsuccessors.values():
			#	npIDs.extend(value)
			#print(npIDs)

		npIDs.append(nounhead)
		npTokens =[]
		npIDs.sort()
		#print(npIDs)
		if self.udgraph.node[npIDs[0]]['pos']=='ADP':
			npIDs = npIDs[1:]
		for npID in npIDs:
			npTokens.append(self.udgraph.node[npID]['token'])
			
		nounPhrase = (' ').join(npTokens)

		return nounPhrase

	def get_nounPharse_short(self, nounhead):
		npIDs=[]
		if(self.udgraph.node[nounhead]['pos'] in ['NOUN','PROPN']):
			allsuccessors = nx.dfs_successors(self.udgraph,nounhead)

			flag = True
			parents = [nounhead]
			
			while len(parents)>0:
				temp = []
				for parent in parents:
					if parent in allsuccessors.keys():
						for child in allsuccessors[parent]:
							if (parent==nounhead and self.udgraph[parent][child]['relation'] not in ['acl','acl:relcl','cc','conj','appos','punct','amod']):
							#or (parent!=nounhead and self.udgraph[parent][child]['relation'] not in ['acl','acl:relcl','appos','dobj','punct']):
								#if parent!=nounhead or self.udgraph[parent][child]['relation'] not in []:
								npIDs.append(child)
								temp.append(child)
				parents = temp
			
			'''
			for parent,child in allsuccessors.items():
				print(str(parent))
				print(child)
			'''		
			#raw_input(" ")

			#for value in allsuccessors.values():
			#	npIDs.extend(value)
			#print(npIDs)

		npIDs.append(nounhead)
		npTokens =[]
		npIDs.sort()
		#print(npIDs)

		start = 0
		for i in range(0,len(npIDs)):
			if self.udgraph.node[npIDs[i]]['pos']=='ADP':
				start = i+1
		npIDs = npIDs[start:]

		flag = False
		for i in range(1,len(npIDs)):
			if npIDs[i]-npIDs[i-1] != 1:
				flag = True

		if flag == True:
			npIDs = []
			npIDs.append(nounhead)


		for npID in npIDs:
			npTokens.append(self.udgraph.node[npID]['token'])
			
		nounPhrase = (' ').join(npTokens)

		return nounPhrase





	def get_source_target(self,nodeID):
		source = []
		target = []
		othernoun = []
		for successor in self.udgraph.successors(nodeID):
			#print(str(nodeID)+"\t"+str(successor)+"\t"+self.udgraph.node[successor]['pos'])
			if('relation' in self.udgraph[nodeID][successor]):
				#print(self.udgraph[nodeID][successor]['relation'])
				if(self.udgraph[nodeID][successor]['relation']=='nsubj'):
					#source.append(self.udgraph.node[successor]['token'])
					source.append(self.get_nounPharse(successor))
					source.extend(self.get_conj_noun(successor))
				elif(self.udgraph[nodeID][successor]['relation'] in ['dobj','iobj','nsubjpass']):
					target.append(self.get_nounPharse(successor))
					target.extend(self.get_conj_noun(successor))
				elif(self.udgraph[nodeID][successor]['relation'] in ['nmod']):
					othernoun.append(self.get_nounPharse(successor))
					othernoun.extend(self.get_conj_noun(successor))

		return source,target,othernoun

	def get_conj_noun(self,nodeID):
		conj_noun = []
		for successor in self.udgraph.successors(nodeID):
			if(self.udgraph[nodeID][successor]['relation']=='conj'):
				conj_noun.append(self.get_nounPharse(successor))

		return conj_noun


	def get_phrases(self):
		for node in self.udgraph.nodes(data=True):
			nodeID = node[0]
			attrs = node[1]
			if 'pos' in attrs and attrs['pos']== 'VERB':
				#print(str(nodeID)+"\t"+attrs['pos']+"\t"+(" ").join(str(e) for e in self.udgraph.successors(nodeID)))
				#print(self.udgraph.successors(nodeID))
				
				verb = attrs['token']
				source,target,othernoun = self.get_source_target(nodeID)

					#check for conjuncting verbs
				predecessors = self.udgraph.predecessors(nodeID)
				for predecessor in predecessors:
					if 'relation' in self.udgraph[predecessor][nodeID] and self.udgraph[predecessor][nodeID]['relation'] in ['conj']:
						psource,ptarget,pothernoun = self.get_source_target(predecessor)
						source.extend(psource)
						#print(self.udgraph.node[predecessor]['token'])
						#raw_input("find conj verb:"+str(predecessor))

				#find the subject for 'xcomp' relation
				#An open clausal complement (xcomp) of a verb or an adjective is a predicative or clausal complement without its own subject. 
				#The reference of the subject is necessarily determined by an argument external to the xcomp 
				#(normally by the object of the next higher clause, if there is one, or else by the subject of the next higher clause).
				for predecessor in predecessors:
					if 'relation' in self.udgraph[predecessor][nodeID] and self.udgraph[predecessor][nodeID]['relation'] in ['xcomp']: 
						psource,ptarget,pothernoun = self.get_source_target(predecessor)
						if len(ptarget)>0:
							source.extend(ptarget)
						elif len(psource)>0:
							source.extend(psource)
						#print(self.udgraph.node[predecessor]['token'])
						#raw_input("find xcomp relation:"+str(predecessor))

				#for s in source: print(s)
				#for t in target: print(t)
				if len(source)==0 and len(target)>0:
					for t in target:
						triplet = ("-",t,verb,othernoun)
						self.metadata['triplets'].append(triplet)
				elif len(source)>0 and len(target)==0:
					for s in source:
						triplet = (s,"-",verb,othernoun)
						self.metadata['triplets'].append(triplet)
				#elif len(source)==0 and len(target)==0:
				#	continue
				else:
					for s in source:
						for t in target:
							triplet = (s,t,verb,othernoun)
							self.metadata['triplets'].append(triplet)

				self.metadata['verbs'].append(verb)
				self.metadata['nouns'].extend(source)
				self.metadata['nouns'].extend(target)
				self.metadata['nouns'].extend(othernoun)

	def get_phrases_short(self):
		for node in self.udgraph.nodes(data=True):
			nodeID = node[0]
			attrs = node[1]
			if 'pos' in attrs and attrs['pos']== 'VERB':
				#print(str(nodeID)+"\t"+attrs['pos']+"\t"+(" ").join(str(e) for e in self.udgraph.successors(nodeID)))
				#print(self.udgraph.successors(nodeID))
				
				verb = attrs['token']

				self.metadata['verbs'].append(verb)

			elif 'pos' in attrs and attrs['pos'] in ['NOUN','ADJ','PROPN']:

				nouns = self.get_nounPharse_short(nodeID)
				self.metadata['nouns'].append(nouns)




		