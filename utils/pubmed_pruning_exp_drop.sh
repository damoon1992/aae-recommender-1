DATASET_PATH=/data22/ggerstenkorn/citation_data_preprocessing/final_data/owner_list_cleaned.csv
DATASET_YEAR=2011
OUTPUT_PREFIX=/data22/ivagliano/cit2vec-journal-results/pubmed/drop/titles-only
# RUN=1
THRESHOLD=55
mkdir -p $OUTPUT_PREFIX
for RUN  in 1 2 3
do
  for DROP in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 #0.9
  do
    echo python3 ../main.py $DATASET_PATH $DATASET_YEAR -m $THRESHOLD -dr $DROP -o $OUTPUT_PREFIX/pubmed-$DATASET_YEAR-$THRESHOLD-$RUN-$DROP.txt
    #python3 ../main.py $DATASET_PATH $DATASET_YEAR -m $THRESHOLD -dr $DROP -o $OUTPUT_PREFIX/pubmed-$DATASET_YEAR-$THRESHOLD-$RUN-$DROP.txt
  done
done
exit 0
