#!/bin/bash

SCRIPT=/users/ljwinnie/Desktop/petrarch2/phrase_extractor/scripts
FILE=/users/ljwinnie/Desktop/petrarch2/phrase_extractor/data
STANFORD_SEG=/users/ljwinnie/Downloads/stanford-segmenter-2015-12-09
CLASSPATH=$STANFORD_SEG/stanford-segmenter-3.6.0.jar:$STANFORD_SEG/slf4j-api.jar
TurboParserPath=/users/ljwinnie/toolbox/turboParser/TurboParser-2.3.0
STANFORD_CORENLP=/users/ljwinnie/toolbox/stanford-corenlp-full-2015-01-29

FILENAME=$1

echo "Call Stanford CoreNLP to do sentence splitting..."
java -cp "$STANFORD_CORENLP/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP -props ${FILE}/StanfordCoreNLP-arabic.properties -file ${FILE}/$FILENAME -outputFormat text -outputDirectory ${FILE}

echo "Generate sentence xml file..."
python preprocess_doc.py ${FILE}/$FILENAME

SFILENAME=$FILENAME-sent.xml
echo "Call Stanford Segmenter to do word segmenting..."
java -mx1g -cp $CLASSPATH edu.stanford.nlp.international.arabic.process.ArabicSegmenter -loadClassifier $STANFORD_SEG/data/arabic-segmenter-atb+bn+arztrain.ser.gz -textFile ${FILE}/$FILENAME-sent.txt > ${FILE}/$SFILENAME.segmented

echo "Call TurboParser to do pos tagging and dependency parsing..."
${SCRIPT}/create_conll_corpus_from_text.pl ${FILE}/$SFILENAME.segmented > ${FILE}/$SFILENAME.conll
${SCRIPT}/create_tagging_corpus.sh ${FILE}/$SFILENAME.conll # Creates $FILENAME.conll.tagging.
${SCRIPT}/run_tagger.sh $TurboParserPath ${FILE}/$SFILENAME.conll.tagging # Does pos tagging
${SCRIPT}/create_conll_predicted_tags_corpus.sh ${FILE}/$SFILENAME.conll ${FILE}/$SFILENAME.conll.tagging.pred # Does Dependency parser and Creates $FILENAME.conll.predpos
${SCRIPT}/run_parser.sh $TurboParserPath ${FILE}/$SFILENAME.conll.predpos # Creates $FILENAME.conll.predpos.pred.

#rm ${FILE}/$SFILENAME.segmented
#rm ${FILE}/$SFILENAME.conll
#rm ${FILE}/$SFILENAME.conll.tagging
#rm ${FILE}/$SFILENAME.conll.tagging.pred
#rm ${FILE}/$SFILENAME.conll.predpos

echo "Do phrase extraction..."
python generateParsedFile.py ${FILE}/$SFILENAME
python arabic_phrase_extract.py ${FILE}/$SFILENAME

#rm ${FILE}/$FILENAME.out
#rm ${FILE}/$FILENAME-sent.txt
#rm ${FILE}/$SFILENAME.conll.predpos.pred
