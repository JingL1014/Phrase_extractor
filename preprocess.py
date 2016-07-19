# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import sys

def read_xml_input(inputfile,outputfile):
	
	output = []

	tree = ET.iterparse(inputfile)
	
	for event, elem in tree:
		if event == "end" and elem.tag == "Sentence":
			story = elem

			# Check to make sure all the proper XML attributes are included
			attribute_check = [key in story.attrib for key in ['date', 'id', 'sentence', 'source']]
			if not attribute_check:
				print('Need to properly format your XML...')
				break

			
			text = story.find('Text').text
			text = text.replace('\n', ' ').replace('  ', ' ').strip()

			output.append(text+"\n")
		

			elem.clear()

	ofile = open(outputfile,'w')
	for line in output:
		ofile.write(line.encode('utf8'))
	ofile.close()

inputFile=sys.argv[1]
outputFile = inputFile+".txt"
read_xml_input(inputFile,outputFile)
