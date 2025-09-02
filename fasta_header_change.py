import sys



def replace_fasta_headers(fasta_file, replacement_file, output_file):

    # Read the replacement information from the tab-separated file

    replacement_dict = {}

    with open(replacement_file, 'r') as replacement_file:

        for line in replacement_file:

            fields = line.strip().split('\t')

            if len(fields) == 2:

                replacement_dict[fields[0]] = fields[1]



    # Open the FASTA file and create a new file with replaced headers

    with open(fasta_file, 'r') as fasta, open(output_file, 'w') as output:

        current_header = None

        for line in fasta:

            if line.startswith('>'):

                # Extract the header from the FASTA file

                current_header = line.strip()[1:]

                # Check if there is a replacement header in the dictionary

                if current_header in replacement_dict:

                    current_header = replacement_dict[current_header]

                # Write the new header to the output file

                output.write('>' + current_header + '\n')

            else:

                # Write sequence lines to the output file

                output.write(line)



if __name__ == "__main__":

    # Check if the correct number of command-line arguments is provided

    if len(sys.argv) != 4:

        print("Usage: python script_name.py <fasta_file> <replacement_file> <output_file>")

        sys.exit(1)



    # Extract input file paths from command-line arguments

    fasta_file_path = sys.argv[1]

    replacement_file_path = sys.argv[2]

    output_file_path = sys.argv[3]



    replace_fasta_headers(fasta_file_path, replacement_file_path, output_file_path)

