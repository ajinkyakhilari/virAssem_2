import os
import sys
import pandas as pd
from Bio import SeqIO

def calculate_coverage(fasta_file):
    # Initialize variables
    total_bases = 0
    total_n_count = 0

    # Iterate through the sequences in the FASTA file
    for record in SeqIO.parse(fasta_file, "fasta"):
        total_bases += len(record.seq)
        total_n_count += record.seq.count('N')

    # Calculate coverage using the provided equation
    coverage = ((total_bases - total_n_count) / total_bases) * 100

    return coverage

def process_folder(folder_path):
    # Check if the provided path is a directory
    if not os.path.isdir(folder_path):
        print("Error: The provided path is not a directory.")
        sys.exit(1)

    # Create a DataFrame to store the results
    results_df = pd.DataFrame(columns=['File', 'Coverage'])

    # Process all FASTA files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".fasta") or filename.endswith(".fa"):
            fasta_file_path = os.path.join(folder_path, filename)
            result = calculate_coverage(fasta_file_path)
            results_df = pd.concat([results_df, pd.DataFrame({'File': [filename], 'Coverage': [result]})], ignore_index=True)

    return results_df

if __name__ == "__main__":
    # Check if a folder path is provided
    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)

    # Get the folder path from the command line arguments
    folder_path = sys.argv[1]

    # Process all FASTA files in the folder
    results = process_folder(folder_path)

    # Output results to Excel
    excel_output_path = 'coverage_results.xlsx'
    results.to_excel(excel_output_path, index=False)
    print(f"Coverage results saved to '{excel_output_path}'")

