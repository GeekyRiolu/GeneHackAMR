"""
This module provides functions for creating 3D visualizations of protein structures.
"""

import py3Dmol
from stmol import showmol
import streamlit as st
import random
import time
import pandas as pd
import plotly.express as px

# Sample PDB structures for common AMR proteins
SAMPLE_PDB_STRUCTURES = {
    'mecA': '1MWR',  # PBP2a from MRSA (methicillin resistance)
    'vanA': '2Y8P',  # D-Ala-D-Lac ligase (vancomycin resistance)
    'tetM': '4V9O',  # Tetracycline resistance protein
    'blaTEM': '1ZG4',  # TEM-1 beta-lactamase
    'aac': '4QC6',   # Aminoglycoside acetyltransferase
    'qnrS': '2XTW',  # Quinolone resistance protein
    'blaCTX-M': '4U0X', # CTX-M beta-lactamase
    'blaKPC': '3RXW',  # KPC carbapenemase
    'blaNDM': '4HL2',  # NDM-1 metallo-beta-lactamase
    'ermB': '4AT5',   # rRNA methyltransferase
}

# Fallback PDB IDs if gene not found in the mapping
FALLBACK_PDB_IDS = ['1MWR', '2Y8P', '4V9O', '1ZG4', '4QC6', '2XTW', '4U0X', '3RXW']

def get_pdb_structure(gene_name):
    """
    Get the PDB structure ID for a given gene name.
    
    Args:
        gene_name: Name of the gene
        
    Returns:
        PDB ID as a string
    """
    # First try exact match
    if gene_name in SAMPLE_PDB_STRUCTURES:
        return SAMPLE_PDB_STRUCTURES[gene_name]
    
    # Then try partial match
    for key in SAMPLE_PDB_STRUCTURES:
        if key.lower() in gene_name.lower() or gene_name.lower() in key.lower():
            return SAMPLE_PDB_STRUCTURES[key]
    
    # Return a fallback structure
    return random.choice(FALLBACK_PDB_IDS)

def render_protein_3d(gene_name, container=None):
    """
    Render a 3D protein structure visualization.
    
    Args:
        gene_name: Name of the gene
        container: Optional Streamlit container to render in
        
    Returns:
        None - displays the visualization
    """
    pdb_id = get_pdb_structure(gene_name)
    
    # Initialize the viewer
    view = py3Dmol.view(width=500, height=400)
    
    # Fetch the protein structure
    view.addModel(f'https://files.rcsb.org/download/{pdb_id}.pdb', 'pdb')
    
    # Style the protein
    view.setStyle({'cartoon': {'color': 'spectrum', 'thickness': 1.0}})
    view.addStyle({'hetflag': True}, {'stick': {'radius': 0.2, 'opacity': 0.9, 'color': 'white'}})
    view.addSurface(py3Dmol.VDW, {'opacity': 0.7, 'color': 'white'})
    
    # Zoom to fit
    view.zoomTo()
    
    # Render in the provided container or directly
    if container:
        with container:
            showmol(view, height=400, width=500)
    else:
        showmol(view, height=400, width=500)
    
    return pdb_id

def create_interactive_protein_view(protein_info, container=None):
    """
    Create an interactive protein view with information about the protein.
    
    Args:
        protein_info: Dictionary containing protein information
        container: Optional Streamlit container to render in
        
    Returns:
        None - displays the visualization
    """
    gene_name = protein_info['gene_name']
    
    if container:
        col1, col2 = container.columns([2, 3])
        
        with col1:
            st.subheader(f"3D Structure: {gene_name}")
            st.caption("Interactive 3D model - drag to rotate, scroll to zoom")
            pdb_id = render_protein_3d(gene_name)
            st.caption(f"PDB ID: {pdb_id} (representative structure)")
        
        with col2:
            st.subheader("Protein Information")
            st.markdown(f"**Gene:** {gene_name}")
            st.markdown(f"**Gene ID:** {protein_info['gene_id']}")
            
            # Display sequence info
            st.markdown("**Amino Acid Composition:**")
            
            # Calculate amino acid composition
            seq = protein_info['protein_sequence']
            total_aa = len(seq)
            
            # Group amino acids by properties
            hydrophobic = ['A', 'V', 'I', 'L', 'M', 'F', 'Y', 'W']
            charged = ['K', 'R', 'D', 'E']
            polar = ['S', 'T', 'N', 'Q', 'C', 'G', 'P', 'H']
            
            # Count occurrences
            h_count = sum(seq.count(aa) for aa in hydrophobic)
            c_count = sum(seq.count(aa) for aa in charged)
            p_count = sum(seq.count(aa) for aa in polar)
            
            # Calculate percentages
            h_pct = (h_count / total_aa) * 100
            c_pct = (c_count / total_aa) * 100
            p_pct = (p_count / total_aa) * 100
            
            # Create composition chart
            data = {
                'Property': ['Hydrophobic', 'Charged', 'Polar'],
                'Percentage': [h_pct, c_pct, p_pct]
            }
            chart_df = pd.DataFrame(data)
            
            # Show the chart
            fig = px.bar(
                chart_df, 
                x='Property', 
                y='Percentage',
                color='Property',
                color_discrete_sequence=['#2C3E50', '#E74C3C', '#3498DB'],
                labels={'Percentage': 'Percentage (%)'},
                title='Amino Acid Composition'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Display sequence length
            st.markdown(f"**Sequence Length:** {total_aa} amino acids")
            
            # Display a snippet of the sequence
            st.markdown("**Sequence Preview:**")
            st.code(seq[:50] + "..." if len(seq) > 50 else seq)
    else:
        # Default rendering without container
        st.subheader(f"3D Structure: {gene_name}")
        pdb_id = render_protein_3d(gene_name)
        st.caption(f"PDB ID: {pdb_id} (representative structure)")

def display_loading_animation():
    """
    Display a loading animation.
    
    Returns:
        None - displays the animation
    """
    # Create a placeholder for the animation
    placeholder = st.empty()
    
    # Display a loading spinner
    with placeholder.container():
        with st.spinner("Processing your sequence..."):
            # This keeps the spinner visible for a moment
            time.sleep(2)
    
    # Clear the placeholder after loading
    placeholder.empty()