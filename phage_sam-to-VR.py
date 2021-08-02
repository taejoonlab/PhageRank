#!/usr/bin/env python3
import pysam
import sys

filename_sam = sys.argv[1]

umi_len = 6
VR_len = 36

read2VR = dict()
VR_freq = dict()

samfile = pysam.AlignmentFile(filename_sam, "r")
for s in samfile:
    q_name = s.query_name
    t_name = s.reference_name
    q_seq = s.query_sequence
    c_tuples = s.cigartuples

    if c_tuples == None:
        continue
    
    if q_name not in read2VR:
        read2VR[q_name] = dict()
        read2VR[q_name]['R1'] = {'umi': '', 'VR_seq': '', 'is_multi':False}
        read2VR[q_name]['R2'] = {'umi': '', 'VR_seq': '', 'is_multi':False}
    
    if s.is_reverse == True and s.is_read1 == True and t_name.endswith('_flank3'):
        umi_3 = ''
        (tmp_umi_code, tmp_umi_len) = c_tuples[-1]
        if tmp_umi_code == 4 and tmp_umi_len == umi_len:
            umi_3 = q_seq[umi_len*-1:]
        
        if umi_3 == '':
            continue
       
        tmp_VR_seq = ''
        (tmp_VR_code, tmp_VR_len) = c_tuples[0]
        if tmp_VR_code == 4:
            tmp_VR_start = tmp_VR_len - VR_len
            tmp_VR_seq = q_seq[tmp_VR_start:tmp_VR_len]
        
        if read2VR[q_name]['R1']['umi'] != '':
            read2VR[q_name]['R1']['is_multi'] = True
            continue
        
        read2VR[q_name]['R1']['umi'] = umi_3
        read2VR[q_name]['R1']['VR_seq'] = tmp_VR_seq

        if tmp_VR_seq not in VR_freq:
            VR_freq[tmp_VR_seq] = 0
        VR_freq[tmp_VR_seq] += 1

    elif s.is_reverse == False and s.is_read2 == True and t_name.endswith('_flank5'):
        umi_5 = ''
        (tmp_umi_code, tmp_umi_len) = c_tuples[0]
        if tmp_umi_code == 4 and tmp_umi_len == umi_len:
            umi_5 = q_seq[:umi_len]
        
        # if UMI is not found, skip the read.
        if umi_5 == '':
            continue

        tmp_VR_start = umi_len
        for (tmp_code, tmp_len) in c_tuples:
            if tmp_code == 0:   # match
                tmp_VR_start += tmp_len
            elif tmp_code == 1: # insert
                tmp_VR_start += tmp_len
            elif tmp_code == 2: # delete
                pass

        tmp_flank_5 = q_seq[umi_len:tmp_VR_start]
        tmp_VR_seq = q_seq[tmp_VR_start:tmp_VR_start+VR_len]
        flank_3 = q_seq[tmp_VR_start+VR_len:]

        if read2VR[q_name]['R2']['umi'] != '':
            read2VR[q_name]['R2']['is_multi'] = True
            continue

        read2VR[q_name]['R2']['umi'] = umi_5
        read2VR[q_name]['R2']['VR_seq'] = tmp_VR_seq

        if tmp_VR_seq not in VR_freq:
            VR_freq[tmp_VR_seq] = 0
        VR_freq[tmp_VR_seq] += 1


for q_name, tmp in read2VR.items():
    VR_R1 = tmp['R1']['VR_seq']
    VR_R2 = tmp['R2']['VR_seq']

    if VR_R1 == VR_R2:
        print(VR_freq[VR_R1])
        pass
        #print("Match")
    else:
        print("NoMatch")
        if VR_R1 != '' and VR_R2 != '':
            print(VR_R1, VR_freq[VR_R1], VR_R2, VR_freq[VR_R2])
    #print(q_name, tmp['R1']['VR_seq'], tmp['R1']['umi'], tmp['R1']['is_multi'])
    #print(q_name, tmp['R2']['VR_seq'], tmp['R2']['umi'], tmp['R2']['is_multi'])
