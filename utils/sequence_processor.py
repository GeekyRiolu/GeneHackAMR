import re
from typing import List, Tuple, Dict, Any, Optional
import random
from Bio.Seq import Seq
from Bio import SeqIO
from io import StringIO

def validate_sequence(sequence: str) -> bool:
    """
    Validate if a sequence contains only valid nucleotide characters (A, T, G, C).
    
    Args:
        sequence: The DNA sequence to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Remove whitespace and convert to uppercase
    sequence = sequence.strip().upper()
    
    # Check if the sequence contains only valid nucleotides
    return bool(re.match(r'^[ATGC]+$', sequence))

def parse_fasta(fasta_content: str) -> List[Tuple[str, str]]:
    """
    Parse FASTA format content and return a list of (sequence_name, sequence) tuples.
    
    Args:
        fasta_content: String containing FASTA formatted sequences
        
    Returns:
        List of tuples with (sequence_name, sequence)
    """
    sequences = []
    
    try:
        # Parse FASTA using BioPython
        fasta_handle = StringIO(fasta_content)
        for record in SeqIO.parse(fasta_handle, "fasta"):
            seq_str = str(record.seq).upper()
            # Validate each sequence
            if validate_sequence(seq_str):
                sequences.append((record.id, seq_str))
    except Exception as e:
        raise ValueError(f"Error parsing FASTA content: {str(e)}")
    
    return sequences

def predict_amr_genes(sequence: str, sequence_name: str = "Unknown") -> List[Dict[str, Any]]:
    """
    Predict antimicrobial resistance (AMR) genes from a given DNA sequence.
    
    Args:
        sequence: A DNA sequence
        sequence_name: Name of the sequence being analyzed
        
    Returns:
        List of dictionaries containing gene information
    """
    # This is a simplified model
    # In a real implementation, this would use a trained ML model with a database of known AMR genes
    
    # Common AMR gene patterns (this is a simplified approach - real implementation would use ML)
    amr_patterns = {
        'mecA': r'ATGAAAAAGATAAAAATTGTTC',  # Methicillin resistance
        'vanA': r'ATGAAAATAGTTGTTAATA',     # Vancomycin resistance
        'tetM': r'ATGAAAATTATTAATATTGGAG',  # Tetracycline resistance
        'blaTEM': r'ATGAGTATTCAACATTTCCG',  # Beta-lactam resistance
        'aac': r'ATGACCTTGCGATGCTCTATG',    # Aminoglycoside resistance
        'qnrS': r'ATGGAAACCTACAATCATACA',   # Quinolone resistance
    }
    
    # List to store detected genes
    detected_genes = []
    gene_id = 1
    
    for gene_name, pattern in amr_patterns.items():
        # In a real implementation, would use more sophisticated pattern matching or ML
        start_pos = sequence.find(pattern)
        if start_pos != -1:
            # Simulate finding a gene - in reality, would use more sophisticated methods
            gene_length = random.randint(400, 1200)  # Typical gene lengths vary
            end_pos = min(start_pos + gene_length, len(sequence))
            gene_seq = sequence[start_pos:end_pos]
            
            detected_genes.append({
                'id': f'AMR_{gene_id}',
                'name': gene_name,
                'sequence': gene_seq,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'confidence': round(random.uniform(0.70, 0.99), 2),  # Simulated confidence score
                'sequence_name': sequence_name
            })
            gene_id += 1
    
    # If no genes matched our patterns, simulate finding a few genes
    # In a real implementation, would use ML to detect novel AMR genes
    if not detected_genes and len(sequence) > 1000:
        # Simulate 1-3 potential novel AMR genes
        num_genes = random.randint(1, 3)
        for i in range(num_genes):
            start_pos = random.randint(0, max(0, len(sequence) - 1000))
            gene_length = random.randint(400, 1000)
            end_pos = min(start_pos + gene_length, len(sequence))
            gene_seq = sequence[start_pos:end_pos]
            
            detected_genes.append({
                'id': f'AMR_{gene_id}',
                'name': f'novel_AMR_candidate_{i+1}',
                'sequence': gene_seq,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'confidence': round(random.uniform(0.60, 0.85), 2),  # Lower confidence for novel genes
                'sequence_name': sequence_name
            })
            gene_id += 1
    
    return detected_genes

def translate_to_protein(dna_sequence: str) -> str:
    """
    Translate a DNA sequence to a protein sequence using Biopython.
    
    Args:
        dna_sequence: The DNA sequence to translate
        
    Returns:
        The translated protein sequence
    """
    try:
        # Create a Seq object and translate
        coding_dna = Seq(dna_sequence)
        protein_sequence = str(coding_dna.translate())
        
        # Remove stop codon if present (*)
        if protein_sequence.endswith('*'):
            protein_sequence = protein_sequence[:-1]
            
        return protein_sequence
    except Exception as e:
        raise ValueError(f"Error translating DNA to protein: {str(e)}")
