import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

def create_gene_visualization(genes: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a visualization of gene locations within sequences.
    
    Args:
        genes: List of gene dictionaries with position information
        
    Returns:
        Plotly figure object
    """
    if not genes:
        return go.Figure()
    
    # Prepare data for visualization
    data = []
    for gene in genes:
        data.append({
            'sequence_name': gene.get('sequence_name', 'Unknown'),
            'gene_name': gene['name'],
            'gene_id': gene['id'],
            'start_pos': gene['start_pos'],
            'end_pos': gene['end_pos'],
            'confidence': gene['confidence'],
            'length': gene['end_pos'] - gene['start_pos']
        })
    
    df = pd.DataFrame(data)
    
    # Group by sequence name
    sequences = df['sequence_name'].unique()
    
    fig = go.Figure()
    
    # Color scale
    colors = px.colors.qualitative.Plotly
    
    for i, seq_name in enumerate(sequences):
        seq_genes = df[df['sequence_name'] == seq_name]
        
        # Add a line representing the sequence
        max_pos = seq_genes['end_pos'].max()
        
        # Add sequence line
        fig.add_trace(go.Scatter(
            x=[0, max_pos],
            y=[i, i],
            mode='lines',
            line=dict(color='gray', width=2),
            name=seq_name,
            hoverinfo='name'
        ))
        
        # Add genes as markers/segments
        for _, gene in seq_genes.iterrows():
            color_idx = hash(gene['gene_name']) % len(colors)
            
            # Add gene segment
            fig.add_trace(go.Scatter(
                x=[gene['start_pos'], gene['end_pos']],
                y=[i, i],
                mode='lines',
                line=dict(color=colors[color_idx], width=10),
                name=f"{gene['gene_name']} ({gene['gene_id']})",
                text=f"Gene: {gene['gene_name']}<br>ID: {gene['gene_id']}<br>Length: {gene['length']} bp<br>Confidence: {gene['confidence']}",
                hoverinfo='text'
            ))
    
    # Update layout
    fig.update_layout(
        title="AMR Gene Locations",
        xaxis_title="Position (bp)",
        yaxis=dict(
            tickvals=list(range(len(sequences))),
            ticktext=sequences,
            title="Sequence"
        ),
        showlegend=False,
        height=100 + 100 * len(sequences),
        margin=dict(l=50, r=50, t=50, b=50),
    )
    
    return fig

def create_resistance_heatmap(resistance_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a heatmap visualization of antibiotic resistance levels.
    
    Args:
        resistance_data: List of resistance information dictionaries
        
    Returns:
        Plotly figure object
    """
    if not resistance_data:
        return go.Figure()
    
    # Convert resistance levels to numeric values
    resistance_values = {'low': 1, 'medium': 2, 'high': 3}
    
    # Prepare data for heatmap
    data = []
    for item in resistance_data:
        data.append({
            'gene_name': item['gene_name'],
            'antibiotic': item['antibiotic'],
            'resistance_level': resistance_values.get(item.get('resistance_level', 'low'), 0),
            'mechanism': item.get('mechanism', 'Unknown'),
        })
    
    df = pd.DataFrame(data)
    
    # Create pivot table for heatmap
    pivot_table = df.pivot_table(
        index='gene_name', 
        columns='antibiotic', 
        values='resistance_level',
        aggfunc='max'  # Take maximum resistance level if duplicates
    ).fillna(0)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale=[
            [0, 'rgb(255,255,255)'],    # No resistance
            [0.33, 'rgb(255,255,0)'],   # Low resistance
            [0.67, 'rgb(255,165,0)'],   # Medium resistance
            [1, 'rgb(255,0,0)']         # High resistance
        ],
        showscale=True,
        colorbar=dict(
            title="Resistance Level",
            tickvals=[0, 1, 2, 3],
            ticktext=["None", "Low", "Medium", "High"]
        ),
        hovertemplate='Gene: %{y}<br>Antibiotic: %{x}<br>Resistance Level: %{z}<extra></extra>',
    ))
    
    # Update layout
    fig.update_layout(
        title="Antibiotic Resistance Heatmap",
        xaxis_title="Antibiotic",
        yaxis_title="Gene",
        height=max(300, 100 + 30 * len(pivot_table.index)),
        margin=dict(l=100, r=50, t=50, b=100),
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_protein_domain_plot(proteins: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a visualization of protein domains and features.
    
    Args:
        proteins: List of protein information dictionaries
        
    Returns:
        Plotly figure object
    """
    if not proteins:
        return go.Figure()
    
    # For a real implementation, this would analyze the protein sequences
    # to identify domains, motifs, and functional regions
    
    # Here we'll simulate protein domains for visualization purposes
    fig = go.Figure()
    
    # Color scale
    colors = px.colors.qualitative.Set3
    
    # Common protein domains in AMR proteins
    domain_types = [
        "Beta-lactamase", "PBP binding", "Acetyltransferase", "DNA binding",
        "ATP binding", "Hydrolase", "Efflux pump", "Ribosomal binding",
        "Transmembrane", "Catalytic", "Aminoglycoside binding"
    ]
    
    # Create simulated domains for each protein
    for i, protein in enumerate(proteins):
        # Get protein length
        protein_length = len(protein['protein_sequence'])
        
        # Simulate 2-4 domains per protein
        num_domains = random.randint(2, 4)
        domains = []
        
        # Ensure domains don't overlap too much
        protein_range = list(range(protein_length))
        for j in range(num_domains):
            if not protein_range:
                break
                
            # Domain length is typically 50-200 amino acids
            domain_length = min(random.randint(50, 200), len(protein_range))
            start_idx = random.randint(0, len(protein_range) - domain_length)
            start_pos = protein_range[start_idx]
            end_pos = start_pos + domain_length
            
            # Remove this range from available positions (with some overlap allowed)
            overlap = domain_length // 3
            remove_start = max(0, start_idx - overlap)
            remove_end = min(len(protein_range), start_idx + domain_length + overlap)
            protein_range = protein_range[:remove_start] + protein_range[remove_end:]
            
            domain_type = random.choice(domain_types)
            domains.append({
                'start': start_pos,
                'end': end_pos,
                'type': domain_type,
                'confidence': round(random.uniform(0.70, 0.95), 2)
            })
        
        # Add protein backbone
        fig.add_trace(go.Scatter(
            x=[0, protein_length],
            y=[i, i],
            mode='lines',
            line=dict(color='gray', width=2),
            name=f"{protein['gene_name']}",
            hoverinfo='name'
        ))
        
        # Add domains
        for domain in domains:
            color_idx = hash(domain['type']) % len(colors)
            
            # Add domain as a colored segment
            fig.add_trace(go.Scatter(
                x=[domain['start'], domain['end']],
                y=[i, i],
                mode='lines',
                line=dict(color=colors[color_idx], width=15),
                name=domain['type'],
                text=f"Domain: {domain['type']}<br>Position: {domain['start']}-{domain['end']}<br>Confidence: {domain['confidence']}",
                hoverinfo='text'
            ))
    
    # Add legend with domain types
    for i, domain_type in enumerate(domain_types):
        if i >= len(colors):
            break
            
        # Add invisible trace just for the legend
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='lines',
            line=dict(color=colors[i], width=10),
            name=domain_type
        ))
    
    # Update layout
    fig.update_layout(
        title="Protein Domain Analysis (Simulated)",
        xaxis_title="Amino Acid Position",
        yaxis=dict(
            tickvals=list(range(len(proteins))),
            ticktext=[f"{p['gene_name']} ({p['gene_id']})" for p in proteins],
            title="Protein"
        ),
        height=100 + 100 * len(proteins),
        margin=dict(l=150, r=50, t=50, b=50),
        legend=dict(
            title="Domain Types",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )
    
    return fig
