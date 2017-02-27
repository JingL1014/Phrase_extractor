#!/bin/bash

SCRIPT=/users/ljwinnie/Desktop/petrarch2/phrase_extractor/scripts
FILE=/users/ljwinnie/Desktop/petrarch2/phrase_extractor/data
STANFORD_SEG=/users/ljwinnie/Downloads/stanford-segmenter-2015-12-09
CLASSPATH=$STANFORD_SEG/stanford-segmenter-3.6.0.jar:$STANFORD_SEG/slf4j-api.jar
udpipePath=/users/ljwinnie/Desktop/petrarch2/phrase_extractor/udpipe-1.0.0-bin
languageModel=/users/ljwinnie/Desktop/petrarch2/phrase_extractor/udpipe-1.0.0-bin/model/ar.ud-1.4.model
#arabic-ud-1.2-160523.udpipe
STANFORD_CORENLP=/users/ljwinnie/toolbox/stanford-corenlp-full-2015-01-29

FILENAME=$1

echo "Call Stanford CoreNLP to do sentence splitting..."
java -cp "$STANFORD_CORENLP/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP -props ${FILE}/StanfordCoreNLP-arabic.properties -file ${FILE}/$FILENAME -outputFormat text -outputDirectory ${FILE}

echo "Generate sentence xml file..."
python preprocess_doc.py ${FILE}/$FILENAME

SFILENAME=$FILENAME-sent.xml
echo "Call Stanford Segmenter to do word segmenting..."
java -mx1g -cp $CLASSPATH edu.stanford.nlp.international.arabic.process.ArabicSegmenter -loadClassifier $STANFORD_SEG/data/arabic-segmenter-atb+bn+arztrain.ser.gz -textFile ${FILE}/$FILENAME-sent.txt > ${FILE}/$SFILENAME.segmented

echo "Call udpipe to do pos tagging and dependency parsing..."
${SCRIPT}/create_conll_corpus_from_text.pl ${FILE}/$SFILENAME.segmented > ${FILE}/$SFILENAME.conll
${udpipePath}/udpipe --tag --parse --outfile=${FILE}/$SFILENAME.conll.predpos.pred --input=conllu $languageModel ${FILE}/$SFILENAME.conll 
# Creates $FILENAME.conll.predpos.pred

#rm ${FILE}/$SFILENAME.segmented
#rm ${FILE}/$SFILENAME.conll

echo "Do phrase extraction..."
python generateParsedFile.py ${FILE}/$SFILENAME
python arabic_phrase_extract.py ${FILE}/$SFILENAME

#rm ${FILE}/$FILENAME.out
#rm ${FILE}/$FILENAME-sent.txt
#rm ${FILE}/$SFILENAME.conll.predpos.pred
