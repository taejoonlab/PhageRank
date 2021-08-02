#!/bin/bash
for FQ1 in $(ls *_R1.raw.fastq.gz)
do
  FQ2=${FQ1/_R1/_R2}
  OUT=${FQ1/_R1.raw.fastq.gz}".PhageM13.sam"
  echo $OUT
  bowtie2 --local -x PhageM13_amplicon -1 $FQ1 -2 $FQ2 -S $OUT
done
