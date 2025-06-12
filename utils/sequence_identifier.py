"""
Sequence identifier module for mapping NCBI sequence IDs to organism names and other metadata.
"""
import os
import re
import streamlit as st
from typing import Dict, Any, List
from openai import OpenAI

# Initialize OpenAI client
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def identify_organism_from_accession(accession_id: str) -> Dict[str, str]:
    """
    Identify organism name and characteristics from NCBI accession ID using OpenAI.
    
    Args:
        accession_id: NCBI sequence accession ID (e.g., gi|2949256985|gb|PV357209.1|)
        
    Returns:
        Dictionary with organism name and potential antibiotic resistance
    """
    # Clean the accession ID (extract the main accession number)
    cleaned_id = accession_id
    match = re.search(r'\|gb\|([^|]+)', accession_id)
    if match:
        cleaned_id = match.group(1)

    # Default response if API call fails
    default_response = {
        "organism": "Unknown species",
        "type": "Unknown",
        "potential_resistance": "Unknown",
        "accession": cleaned_id
    }

    try:
        # Skip API call if no API key is available
        if not OPENAI_API_KEY:
            return default_response

        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a genomics expert. Based on the NCBI accession ID provided, predict the most likely organism it's associated with and potential antibiotic resistance. Never indicate uncertainty - provide your best scientific assessment based on the ID pattern."
                },
                {
                    "role": "user",
                    "content": f"Provide information about this NCBI sequence accession: {cleaned_id}. Return a JSON with keys: organism (species name), type (bacteria/virus/etc), potential_resistance (specific antibiotics or 'None')"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        import json
        if result:
            data = json.loads(result)
            
            # Ensure all required fields are present
            return {
                "organism": data.get("organism", default_response["organism"]),
                "type": data.get("type", default_response["type"]),
                "potential_resistance": data.get("potential_resistance", default_response["potential_resistance"]),
                "accession": cleaned_id
            }
        return default_response
    except Exception as e:
        print(f"Error identifying organism: {e}")
        return default_response


def get_organism_mapping(gene_names: List[str], sequence_ids: List[str] = []) -> Dict[str, str]:
    """
    Generate mapping of gene names to likely organism names.
    Uses both predefined mappings and OpenAI for unknown IDs.
    
    Args:
        gene_names: List of gene names to map to organisms
        sequence_ids: Optional list of sequence IDs to help with identification
        
    Returns:
        Dictionary mapping gene names to organism names
    """
    # Base mapping for known AMR genes to organisms
    base_mapping = {
        'mecA': 'Staphylococcus aureus',
        'vanA': 'Enterococcus faecium',
        'tetM': 'Multiple species',
        'blaTEM': 'Escherichia coli',
        'blaCTX-M': 'Enterobacteriaceae',
        'blaKPC': 'Klebsiella pneumoniae',
        'blaNDM': 'Enterobacteriaceae',
        'qnrA': 'Enterobacteriaceae',
        'qnrS': 'Enterobacteriaceae',
        'aac': 'Multiple species',
        'ermB': 'Streptococcus species'
    }
    
    # If sequence IDs are provided, enhance the mapping with OpenAI identifications
    sequence_info = {}
    if sequence_ids:
        for seq_id in sequence_ids:
            try:
                info = identify_organism_from_accession(seq_id)
                # Use the sequence ID as the key, organism as the value
                sequence_info[seq_id] = info["organism"]
            except Exception as e:
                print(f"Error processing sequence ID {seq_id}: {e}")
                sequence_info[seq_id] = "Unknown organism"
    
    # Combine base mapping with information from sequence IDs
    final_mapping = {}
    for gene in gene_names:
        if gene in base_mapping:
            final_mapping[gene] = base_mapping[gene]
        elif sequence_ids and len(sequence_ids) > 0:
            # If we have sequence info but no specific mapping for this gene,
            # use the first sequence organism (better than nothing)
            first_seq_id = sequence_ids[0]
            final_mapping[gene] = sequence_info.get(first_seq_id, "Unknown organism")
        else:
            final_mapping[gene] = "Unknown organism"
    
    return final_mapping