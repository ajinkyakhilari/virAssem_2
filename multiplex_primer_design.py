import argparse

from Bio import SeqIO, AlignIO

from primer3 import designPrimers

import pandas as pd



# Define function to find conserved regions from multiple sequence alignment

def find_conserved_regions(msa_file, threshold=0.9):

    alignment = AlignIO.read(msa_file, "fasta")

    seq_length = alignment.get_alignment_length()

    consensus = ""

    

    for i in range(seq_length):

        column = [record.seq[i] for record in alignment]

        most_common_base = max(set(column), key=column.count)

        freq = column.count(most_common_base) / len(column)

        consensus += most_common_base if freq >= threshold else "N"

    

    return consensus



# Define function to design primers from conserved regions

def design_multiplex_primers(msa_file, output_file, amplicon_size):

    primers_list = []

    

    # Get conserved regions from alignment

    consensus_seq = find_conserved_regions(msa_file)

    seq_length = len(consensus_seq)

    

    for start in range(0, seq_length, amplicon_size):

        end = min(start + amplicon_size, seq_length)

        subseq = consensus_seq[start:end]

        

        # Primer3 input settings

        primer_design = designPrimers(

            {

                'SEQUENCE_ID': "Consensus",

                'SEQUENCE_TEMPLATE': str(subseq),

            },

            {

                'PRIMER_OPT_SIZE': 20,

                'PRIMER_PICK_INTERNAL_OLIGO': 0,

                'PRIMER_MIN_SIZE': 18,

                'PRIMER_MAX_SIZE': 25,

                'PRIMER_OPT_TM': 60.0,

                'PRIMER_MIN_TM': 57.0,

                'PRIMER_MAX_TM': 63.0,

                'PRIMER_MIN_GC': 40.0,

                'PRIMER_MAX_GC': 60.0,

                'PRIMER_MAX_POLY_X': 4,

                'PRIMER_PRODUCT_SIZE_RANGE': [[amplicon_size, amplicon_size]],  # Fixed amplicon size

                'PRIMER_NUM_RETURN': 1

            }

        )

        

        primers_list.append({

            "Start": start,

            "End": end,

            "Forward Primer": primer_design['PRIMER_LEFT_0_SEQUENCE'],

            "Reverse Primer": primer_design['PRIMER_RIGHT_0_SEQUENCE'],

            "Amplicon Size": primer_design['PRIMER_PAIR_0_PRODUCT_SIZE']

        })

    

    # Save to CSV file

    df = pd.DataFrame(primers_list)

    df.to_csv(output_file, index=False)

    print(f"Primer design completed. Results saved to {output_file}")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Multiplex PCR Primer Design from MSA")

    parser.add_argument("-m", "--msa", required=True, help="Path to multiple sequence alignment FASTA file")

    parser.add_argument("-o", "--output", required=True, help="Output file for primers (CSV)")

    parser.add_argument("-a", "--amplicon", type=int, required=True, help="Fixed amplicon size")

    

    args = parser.parse_args()

    

    # Run primer design

    design_multiplex_primers(args.msa, args.output, args.amplicon)

