# virAssem_2


This script is a comprehensive Bash pipeline designed for reference-guided assembly, specifically tailored for Lumpy Skin Disease Virus with Oxford Nanopore Technologies (ONT) sequencing data. It integrates several bioinformatics tools to automate the process from raw sequencing reads to consensus sequence generation, including quality control, alignment, variant calling, and coverage analysis. Here's a breakdown of its components and functionalities:

# Input and Output
•	Input Directory (-i): Contains barcode-specific folders with FASTQ files.

•	Output Directory (-o): Destination for processed data and reports.

•	Reference Genome (-r): Path to the reference genome file.

•	BEDPE File (-p): Contains primer positions for primer clipping.
# Optional Parameters
•	Number of Threads (-t): Adjusts the parallel processing capability.

•	Maximum and Minimum Read Lengths (-m, -l): Filters reads by length.
# Workflow Steps
1.	Quality Control with fastp: Trims and filters reads based on quality metrics.
2.	Alignment with minimap2: Maps reads to the reference genome.
3.	Primer Clipping with bamclipper: Removes primer sequences from aligned reads.
4.	Consensus and Variant Calling with Medaka and long-shot: Generates consensus sequences and identifies variants.
5.	Coverage Analysis with bedtools: Identifies low-coverage regions for masking in the consensus sequence.
6.	Consensus Generation with bcftools: Applies variants to the reference genome to produce a consensus sequence.
7.	Post-Processing: Renames FASTA headers and masks low-coverage areas.
# Usage
The script is executed from the command line with specified options for input and output directories, reference genome, and other parameters as needed. It's adaptable for various projects by adjusting the input parameters and can handle multiple barcodes in parallel, making it efficient for large datasets.
To use the pipeline, you can run the script with the following command:

./virAssem_2.sh -i <input_dir> -o <output_dir> -r <reference_genome> -p <bedpe_file> -t <threads> -m <max_length> -l <min_length> 

Where:
•	-i specifies the input directory containing barcode folders with FASTQ files.

•	-o specifies the output directory for processed data.

•	-r is the path to the reference genome file.

•	-p is the path to the BEDPE file with primer positions.

•	-t (optional) sets the number of threads (default is 4).

•	-m (optional) sets the maximum read length (default is 5000).

•	-l (optional) sets the minimum read length (default is 150).

# Example
./virAssem_2.sh -i /path/to/input -o /path/to/output -r /path/to/reference.fasta -p /path/to/primers.bedpe -t 8 

Help

For additional information or to display help, run:

./virAssem_2.sh -h 

# Dependencies
This pipeline relies on several external tools:

•	fastp for read quality control.

•	minimap2 and samtools for read alignment and processing.

•	bedtools for coverage analysis and genomecov.

•	bamclipper for primer clipping.

•	Medaka and long-shot for consensus and variant calling.

•	bcftools for consensus sequence refinement.

•	MultiQC for report generation.

These dependencies need to be installed and accessible in the user's $PATH for the script to function properly. It's designed for users with intermediate to advanced knowledge in bioinformatics workflows, offering a streamlined process for generating high-quality consensus sequences from ONT sequencing data.

# Contributing
Contributions to improve the script or documentation are welcome. Please follow the standard GitHub pull request process to submit your changes.

# License
The Script is released under GPU


