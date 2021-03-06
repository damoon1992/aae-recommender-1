#DATASET_PATH=/data21/lgalke/datasets/econbiz62k.tsv
DATASET_YEAR=2012
OUTPUT_PREFIX=/data22/ivagliano/cit2vec-journal-results/econis/generic-condition
RUN=1
mkdir -p $OUTPUT_PREFIX
for THRESHOLD in 1 2 3 4 5 10 15
do
  # With TSV file
  # echo python3 ../main.py $DATASET_PATH $DATASET_YEAR -m $THRESHOLD -o $OUTPUT_PREFIX/econis-$DATASET_YEAR-$THRESHOLD-$RUN.txt
  # python3 ../main.py $DATASET_PATH $DATASET_YEAR -m $THRESHOLD -o $OUTPUT_PREFIX/econis-$DATASET_YEAR-$THRESHOLD-$RUN.txt
  # With JSON file
  echo python3 ../eval/econis.py $DATASET_YEAR -m $THRESHOLD -o $OUTPUT_PREFIX/econis-$DATASET_YEAR-$THRESHOLD-$RUN.txt
  python3 ../eval/econis.py $DATASET_YEAR -m $THRESHOLD -o $OUTPUT_PREFIX/econis-$DATASET_YEAR-$THRESHOLD-$RUN.txt
done
exit 0
