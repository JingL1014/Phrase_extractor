# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import sys



def read_doc_input(inputxml,inputparsed,outputfile):
	'''
		input:
			input document xml file and Stanford CoreNLP output
		output:

			1. a new xml file of splitted sentences 
			2. a txt file with one sentence in each line for word segmentation in the later step
	'''

	#read input xml file, store documents in a dictionary.
	#the key of dictionary is the text part of document, the value is the infomartion about the document, e.g date,id
	docdict = {}
	doctexts = []
	output = []

	tree = ET.iterparse(inputxml)
	
	for event, elem in tree:
		if event == "end" and elem.tag == "Article":
			story = elem

			# Check to make sure all the proper XML attributes are included
			attribute_check = [key in story.attrib for key in ['date', 'id', 'mongoId','sentence', 'source']]
			if not attribute_check:
				print('Need to properly format your XML...')
				break

			entry_id = story.attrib['id'];
			mongoid = story.attrib['mongoId']
			date = story.attrib['date']
			sentence = story.attrib['sentence']
			source = story.attrib['source']

			text = story.find('Text').text
			text = text.replace('\n', ' ').replace('  ', ' ').strip()

			if entry_id in docdict:
				print('id must be unique, this article is in document dictionary :'+entry_id)
				break

			docdict[text] = {'id':entry_id,'date':date,'mongoid':mongoid,'sentence':sentence,'source':source,'text':text}

			doctexts.append(text)

			elem.clear()

	#read Stanford CoreNLP parsed file		
	parsed = open(inputparsed)
	parsedfile = parsed.readlines()
	parsedlines = []
	for line in parsedfile:
		if "Sentence #" in line or "[" in line:
			continue
		else:
			#print(line)
			parsedlines.append(line.replace("\n"," ").strip())



	#match CoreNLP parsed file with input xml file
	sents_dict = {}
	sents = []
	sentidx = 1
	#print(len(doctexts))

	for line in parsedlines:
		doc = doctexts[0]
		#print(doc)
		#print(line+"#")
		#print(isinstance(doc,str))
		#print(isinstance(line,str))
		#print(doc.encode('UTF-8').find(line))
		

		if doc.encode('UTF-8').find(line) ==-1:
			#print(line)
			doctexts.remove(doc)
			sentidx = 1
			doc = doctexts[0]
		
		if doc.encode('UTF-8').find(line) != -1:
			#print(docdict[doc]['id']+"#"+line)
			key = docdict[doc]['id']+"#"+line
			sents.append(key)
			output.append(line+"\n")
			sents_dict[key] = {}
			sents_dict[key]['sentence_id']=str(sentidx)
			sents_dict[key].update(docdict[doc])
			#print(sents_dict[key]['sentence_id']+":"+key)
			sentidx = sentidx + 1
		

	#print(len(parsedlines))
	#print(len(sents))
	#for sent in sents:
		#print(sent)
		#print(sents_dict.get(sent).get('sentence_id'))
		#print(sents_dict[sent]['sentence_id']+":"+key)

	create_sentence_xml(sents,sents_dict,inputxml+"-sent.xml")

	ofile = open(outputfile,'w')
	for line in output:
		ofile.write(line)
	ofile.close()

def create_sentence_xml(sentences,sents_dict,outputxml):
	root = ET.Element("Sentences")

	for s in sentences:
		#print(isinstance(s,unicode))
		sentinfo = sents_dict[s]
		#print(s+" "+sentinfo['id']+"-"+sentinfo['sentence_id'])
		sentence = ET.SubElement(root,"Sentence", {"date":sentinfo['date'],"source":sentinfo['source'],"id":sentinfo['id']+"-"+sentinfo['sentence_id'],"sentence":sentinfo['sentence']})
		ET.SubElement(sentence,"Text").text = s[s.index('#')+1:].decode('UTF-8')

	tree = ET.ElementTree(root)
	tree.write(outputxml,'UTF-8')



inputxml=sys.argv[1]
inputparsed = inputxml+".out"
outputfile = inputxml+"-sent.txt"
read_doc_input(inputxml,inputparsed,outputfile)