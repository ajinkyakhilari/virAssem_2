#!/bin/bash

# A bash pipeline workflow for reference guided assembly.

# Default parameters
INPUT_DIR="" # Input directory
OUTPUT_DIR="" # Output directory
REFERENCE="" # Reference genome file
BEDPE="" # BEDPE file with primer positions
THREADS=4 # Default number of threads
max_length=5000 # Default maximum read length
min_length=150 # Default minimum read length

# Function to display help
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -i  Input directory containing barcode folders with FASTQ files"
    echo "  -o  Output directory for processed data"
    echo "  -r  Reference genome file path"
    echo "  -p  BEDPE file path with primer positions"
    echo "  -t  Number of threads (default: 4)"
    echo "  -m  Maximum read length (default: 25000)"
    echo "  -l  Minimum read length (default: 1000)"
    echo "  -h  Display this help and exit"
}

# Parse command-line options
while getopts ":hi:o:r:p:t:m:l:" opt; do
    case ${opt} in
        i ) INPUT_DIR=$OPTARG ;;
        o ) OUTPUT_DIR=$OPTARG ;;
        r ) REFERENCE=$OPTARG ;;
        p ) BEDPE=$OPTARG ;;
        t ) THREADS=$OPTARG ;;
        m ) max_length=$OPTARG ;;
        l ) min_length=$OPTARG ;;
        h ) show_help
            exit 0 ;;
        \? ) echo "Invalid option: $OPTARG" 1>&2
             show_help
             exit 1 ;;
        : ) echo "Invalid option: $OPTARG requires an argument" 1>&2
            show_help
            exit 1 ;;
    esac
done

# Validate required inputs
if [ -z "$INPUT_DIR" ] || [ -z "$OUTPUT_DIR" ] || [ -z "$REFERENCE" ] || [ -z "$BEDPE" ]; then
    echo "Error: Missing required arguments"
    show_help
    exit 1
fi

# Ensure the output and log directories exist
mkdir -p "$OUTPUT_DIR"
LOG_DIR="$OUTPUT_DIR/logs"
mkdir -p "$LOG_DIR"

# Process each barcode folder
for barcode_dir in "$INPUT_DIR"/*; do
    if [ -d "$barcode_dir" ]; then
        barcode=$(basename "$barcode_dir")
        barcode_output_dir="$OUTPUT_DIR/$barcode"
        mkdir -p "$barcode_output_dir"

        echo "Concatenate FASTQ files"
        cat "$barcode_dir"/*.fastq > "$barcode_output_dir/$barcode.fastq"

        echo "Quality control with fastp"
        fastp -i "$barcode_output_dir/$barcode.fastq" -o "$barcode_output_dir/${barcode}_filt.fastq" -q 8 -A -w $THREADS --length_limit $max_length -l $min_length -j "$LOG_DIR/${barcode}_fastp.json" -h "$LOG_DIR/${barcode}_fastp.html"

        echo "Align reads with minimap2"
        minimap2 -a -x map-ont -t $THREADS $REFERENCE "$barcode_output_dir/${barcode}_filt.fastq" | samtools view -bS -F 4 - | samtools sort -o "$barcode_output_dir/$barcode.sorted.bam" -
        samtools index "$barcode_output_dir/$barcode.sorted.bam"
        samtools stats "$barcode_output_dir/$barcode.sorted.bam" > "$LOG_DIR/${barcode}_samtools_stats.txt"
        samtools flagstat "$barcode_output_dir/$barcode.sorted.bam" > "$LOG_DIR/${barcode}_samtools_flagstat.txt"
        bedtools genomecov -ibam "$barcode_output_dir/$barcode.sorted.bam" -bg > "$LOG_DIR/${barcode}_coverage.bedgraph"
        bedtools coverage -a "${BEDPE%.bedpe}.bed" -b "$barcode_output_dir/$barcode.sorted.bam" > "$LOG_DIR/${barcode}_amplicon_coverage.txt"

        echo "Primer clipping with bamclipper"
        pushd "$barcode_output_dir"
        bamclipper.sh -b "$barcode.sorted.bam" -p $BEDPE -n $THREADS
        popd

        echo "Consensus and variant calling with Medaka"
        medaka consensus --model r941_min_high_g303 --threads $THREADS --chunk_len 800 --chunk_ovlp 400 "$barcode_output_dir/$barcode.sorted.primerclipped.bam" "$barcode_output_dir/$barcode.hdf"
        medaka variant $REFERENCE "$barcode_output_dir/$barcode.hdf" "$barcode_output_dir/$barcode.medaka.vcf"

        echo "Compress and index VCF for long-shot"
        bgzip -f "$barcode_output_dir/$barcode.medaka.vcf"
        tabix -f -p vcf "$barcode_output_dir/$barcode.medaka.vcf.gz"

        echo "Variant calling with long-shot"
        longshot -P 0 -F -A --no_haps --bam "$barcode_output_dir/$barcode.sorted.primerclipped.bam" --ref $REFERENCE --out "$barcode_output_dir/$barcode.variant.vcf" --potential_variants "$barcode_output_dir/$barcode.medaka.vcf.gz"
        bgzip -c "$barcode_output_dir/$barcode.variant.vcf" > "$barcode_output_dir/$barcode.variant.vcf.gz"
        tabix "$barcode_output_dir/$barcode.variant.vcf.gz"
        bcftools stats "$barcode_output_dir/$barcode.variant.vcf.gz" > "$LOG_DIR/${barcode}_longshot_bcftools_stats.txt"
        bcftools stats "$barcode_output_dir/$barcode.variant.vcf.gz" > "$LOG_DIR/${barcode}_vcf_stats.vchk"

        echo "Coverage analysis with bedtools"
        bedtools genomecov -bga -ibam "$barcode_output_dir/$barcode.sorted.primerclipped.bam" -g $REFERENCE | awk '$4 < 20' | bedtools merge > "$barcode_output_dir/$barcode.mask.bed"
        cp "$barcode_output_dir/$barcode.mask.bed" "$LOG_DIR/${barcode}_coverage.bed"

        echo "Generate consensus"
        bcftools consensus -f $REFERENCE "$barcode_output_dir/$barcode.variant.vcf.gz" > "$barcode_output_dir/$barcode.preconsensus.fasta"

        echo "Mask low-coverage regions in the consensus"
        bedtools maskfasta -fi "$barcode_output_dir/$barcode.preconsensus.fasta" -bed "$barcode_output_dir/$barcode.mask.bed" -fo "$barcode_output_dir/$barcode.BCF.consensus.fasta"

        echo "Rename the FASTA headers to include the barcode name"
        sed -E "s/>/>$barcode-/" "$barcode_output_dir/$barcode.BCF.consensus.fasta" > "$barcode_output_dir/$barcode.final.consensus.fasta"

        echo "$barcode processing completed."
    fi
done

# Run MultiQC to aggregate results into a single report for all barcodes
multiqc "$LOG_DIR" -o "$OUTPUT_DIR"

echo "All barcodes processed. MultiQC report generated."

