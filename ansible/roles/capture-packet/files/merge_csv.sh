#!/bin/bash

INPUT_DIR="csv"
OUTPUT_DIR="csv_merged"
DONE_DIR="csv_done"

while getopts i:t:o:d: OPT
do
  case ${OPT} in
     i) INPUT_DIR=$OPTARG;;
     o) OUTPUT_DIR=$OPTARG;;
     d) DONE_DIR=$OPTARG;;
  esac
done

mkdir -p ${DONE_DIR}

PREFIX=$(find ${INPUT_DIR} -maxdepth 1 -name "*.csv.gz" -printf "%f\n" | cut -d "-" -f 1,2,3,4 | sort | uniq)

for p in ${PREFIX}; do
    echo "merge ${p}*.csv.gz => ${p}.csv.gz"
    # find ${INPUT_DIR} -maxdepth 1 -name "${p}*.csv.gz" | xargs /bin/mv -t ${TEMP_DIR}
    merge_csv.py -i ${INPUT_DIR} -o ${OUTPUT_DIR} -p ${p}
    pigz ${OUTPUT_DIR}/${p}*.csv
    /bin/mv -f ${INPUT_DIR}/${p}*.csv.gz ${DONE_DIR}/
done