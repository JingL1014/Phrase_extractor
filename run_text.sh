#!/bin/bash

SCRIPT=/users/ljwinnie/toolbox/turboParser/TurboParser-2.3.0/phrase_extractor/scripts
FILE=/users/ljwinnie/toolbox/turboParser/TurboParser-2.3.0/phrase_extractor/data
STANFORD_SEG=/users/ljwinnie/Downloads/stanford-segmenter-2015-12-09
CLASSPATH=$STANFORD_SEG/stanford-segmenter-3.6.0.jar:$STANFORD_SEG/slf4j-api.jar
TurboParserPath=/users/ljwinnie/toolbox/turboParser/TurboParser-2.3.0

FILENAME=$1

python preprocess.py ${FILE}/$FILENAME

java -mx1g -cp $CLASSPATH edu.stanford.nlp.international.arabic.process.ArabicSegmenter -loadClassifier $STANFORD_SEG/data/arabic-segmenter-atb+bn+arztrain.ser.gz -textFile ${FILE}/$FILENAME.txt > ${FILE}/$FILENAME.segmented
${SCRIPT}/create_conll_corpus_from_text.pl ${FILE}/$FILENAME.segmented > ${FILE}/$FILENAME.conll
${SCRIPT}/create_tagging_corpus.sh ${FILE}/$FILENAME.conll # Creates $FILENAME.conll.tagging.
${SCRIPT}/run_tagger.sh $TurboParserPath ${FILE}/$FILENAME.conll.tagging # Does pos tagging
${SCRIPT}/create_conll_predicted_tags_corpus.sh ${FILE}/$FILENAME.conll ${FILE}/$FILENAME.conll.tagging.pred # Does Dependency parser and Creates $FILENAME.conll.predpos
${SCRIPT}/run_parser.sh $TurboParserPath ${FILE}/$FILENAME.conll.predpos # Creates $FILENAME.conll.predpos.pred.

rm ${FILE}/$FILENAME.segmented
rm ${FILE}/$FILENAME.conll
rm ${FILE}/$FILENAME.conll.tagging
rm ${FILE}/$FILENAME.conll.tagging.pred
rm ${FILE}/$FILENAME.conll.predpos

python generateParsedFile.py ${FILE}/$FILENAME
python arabic_phrase_extract.py ${FILE}/$FILENAME

rm ${FILE}/$FILENAME.txt
rm ${FILE}/$FILENAME.conll.predpos.pred
