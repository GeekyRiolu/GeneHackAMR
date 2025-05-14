import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

def create_resistance_frequency_bar_chart(genes: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a bar chart visualizing the frequency of resistant genes.
    
    Args:
        genes: List of gene dictionaries with resistance information
        
    Returns:
        Plotly figure object
    """
    if not genes:
        return go.Figure()
    
    # Count occurrences of each gene name
    gene_names = [gene['name'] for gene in genes]
    gene_counts = Counter(gene_names)
    
    # Convert to DataFrame
    df = pd.DataFrame({
        'Gene': list(gene_counts.keys()),
        'Count': list(gene_counts.values())
    }).sort_values('Count', ascending=False)
    
    # Create bar chart
    fig = px.bar(
        df, 
        x='Gene', 
        y='Count',
        title="Frequency of AMR Genes",
        labels={'Gene': 'Gene Name', 'Count': 'Frequency'},
        color='Count',
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        yaxis_title="Frequency",
        xaxis_title="Gene",
        margin=dict(l=50, r=50, t=50, b=100),
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_resistance_level_pie_chart(resistance_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a pie chart showing distribution of resistance levels.
    
    Args:
        resistance_data: List of resistance information dictionaries
        
    Returns:
        Plotly figure object
    """
    if not resistance_data:
        return go.Figure()
    
    # Count resistance levels
    resistance_levels = [item.get('resistance_level', 'unknown') for item in resistance_data]
    level_counts = Counter(resistance_levels)
    
    # Create dataset
    labels = list(level_counts.keys())
    values = list(level_counts.values())
    
    # Define colors for resistance levels
    colors = {
        'high': 'rgb(255,0,0)',      # Red
        'medium': 'rgb(255,165,0)',  # Orange
        'low': 'rgb(255,255,0)',     # Yellow
        'unknown': 'rgb(200,200,200)' # Gray
    }
    
    color_map = [colors.get(label, 'rgb(200,200,200)') for label in labels]
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=color_map,
        textinfo='label+percent',
        hoverinfo='label+value',
        textfont=dict(size=14),
        hole=0.3,
    )])
    
    # Update layout
    fig.update_layout(
        title="Distribution of Antimicrobial Resistance Levels",
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_antibiotic_resistance_count_chart(resistance_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a bar chart showing the count of resistant genes per antibiotic.
    
    Args:
        resistance_data: List of resistance information dictionaries
        
    Returns:
        Plotly figure object
    """
    if not resistance_data:
        return go.Figure()
    
    # Count antibiotics
    antibiotics = [item.get('antibiotic', 'unknown') for item in resistance_data]
    antibiotic_counts = Counter(antibiotics)
    
    # Convert to DataFrame
    df = pd.DataFrame({
        'Antibiotic': list(antibiotic_counts.keys()),
        'Count': list(antibiotic_counts.values())
    }).sort_values('Count', ascending=False)
    
    # Create horizontal bar chart
    fig = px.bar(
        df, 
        y='Antibiotic', 
        x='Count',
        title="Number of Genes Resistant to Each Antibiotic",
        labels={'Antibiotic': 'Antibiotic', 'Count': 'Number of Resistant Genes'},
        color='Count',
        color_continuous_scale='Reds',
        orientation='h'
    )
    
    # Update layout
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Number of Resistant Genes",
        yaxis_title="Antibiotic",
        margin=dict(l=150, r=50, t=50, b=50),
    )
    
    return fig

def create_resistance_mechanism_donut(resistance_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a donut chart showing distribution of resistance mechanisms.
    
    Args:
        resistance_data: List of resistance information dictionaries
        
    Returns:
        Plotly figure object
    """
    if not resistance_data:
        return go.Figure()
    
    # Count resistance mechanisms
    mechanisms = [item.get('mechanism', 'Unknown') for item in resistance_data]
    mechanism_counts = Counter(mechanisms)
    
    # Create dataset
    labels = list(mechanism_counts.keys())
    values = list(mechanism_counts.values())
    
    # Create pie chart with hole (donut)
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        textinfo='label+percent',
        hoverinfo='label+value',
        textfont=dict(size=14),
        hole=0.5,
    )])
    
    # Update layout
    fig.update_layout(
        title="Distribution of Resistance Mechanisms",
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_3d_gene_clustering(genes: List[Dict[str, Any]], resistance_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a 3D scatter plot showing clustering of genes based on their properties
    and resistance characteristics.
    
    Args:
        genes: List of gene dictionaries
        resistance_data: List of resistance information dictionaries
        
    Returns:
        Plotly figure object
    """
    if not genes or not resistance_data:
        return go.Figure()
    
    # Combine gene and resistance data
    gene_resistance_map = {}
    for res in resistance_data:
        gene_name = res.get('gene_name', '')
        if gene_name not in gene_resistance_map:
            gene_resistance_map[gene_name] = []
        gene_resistance_map[gene_name].append(res)
    
    # Prepare data for 3D visualization
    data = []
    
    for gene in genes:
        name = gene.get('name', '')
        resistance_info = gene_resistance_map.get(name, [])
        
        # Calculate resistance metrics
        num_antibiotics = len(set(r.get('antibiotic', '') for r in resistance_info))
        avg_resistance = 0
        mechanisms = set()
        
        if resistance_info:
            # Convert resistance levels to numeric values
            resistance_values = {'low': 1, 'medium': 2, 'high': 3, 'unknown': 0}
            resistance_nums = [resistance_values.get(r.get('resistance_level', 'unknown'), 0) 
                              for r in resistance_info]
            avg_resistance = sum(resistance_nums) / len(resistance_nums)
            mechanisms = set(r.get('mechanism', 'Unknown') for r in resistance_info)
        
        # Create data point
        data.append({
            'gene_name': name,
            'gene_id': gene.get('id', ''),
            'sequence_length': gene.get('end_pos', 0) - gene.get('start_pos', 0),
            'confidence': gene.get('confidence', 0),
            'num_antibiotics': num_antibiotics,
            'avg_resistance': avg_resistance,
            'mechanisms': ', '.join(mechanisms),
            'mechanism_count': len(mechanisms)
        })
    
    df = pd.DataFrame(data)
    
    # Create 3D scatter plot
    fig = px.scatter_3d(
        df,
        x='sequence_length',
        y='num_antibiotics',
        z='avg_resistance',
        color='mechanism_count',
        size='confidence',
        hover_name='gene_name',
        hover_data={
            'gene_id': True,
            'mechanisms': True,
            'mechanism_count': False,
            'sequence_length': True,
            'num_antibiotics': True,
            'avg_resistance': True,
            'confidence': True
        },
        color_continuous_scale='Viridis',
        title="3D Clustering of AMR Genes",
        labels={
            'sequence_length': 'Gene Length (bp)',
            'num_antibiotics': 'Number of Antibiotics',
            'avg_resistance': 'Average Resistance Level',
            'mechanism_count': 'Number of Mechanisms'
        }
    )
    
    # Update layout
    fig.update_layout(
        scene=dict(
            xaxis_title='Gene Length (bp)',
            yaxis_title='Number of Antibiotics',
            zaxis_title='Avg Resistance Level'
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=600
    )
    
    return fig

def create_3d_protein_comparison(proteins: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a 3D visualization comparing multiple protein properties.
    
    Args:
        proteins: List of protein information dictionaries
        
    Returns:
        Plotly figure object
    """
    if not proteins:
        return go.Figure()
    
    # Calculate protein properties
    data = []
    for protein in proteins:
        sequence = protein.get('protein_sequence', '')
        if not sequence:
            continue
            
        # Calculate basic protein properties
        length = len(sequence)
        
        # Count amino acid types
        aa_counts = Counter(sequence)
        
        # Group amino acids by properties
        hydrophobic = sum(aa_counts.get(aa, 0) for aa in 'AVILMFYW')
        polar = sum(aa_counts.get(aa, 0) for aa in 'STNQC')
        charged = sum(aa_counts.get(aa, 0) for aa in 'DEKRH')
        
        # Calculate percentages
        hydrophobic_percent = (hydrophobic / length) * 100 if length > 0 else 0
        polar_percent = (polar / length) * 100 if length > 0 else 0
        charged_percent = (charged / length) * 100 if length > 0 else 0
        
        # Molecular weight approximation (very rough estimate)
        avg_aa_weight = 110  # Average amino acid weight in Daltons
        mol_weight = length * avg_aa_weight
        
        data.append({
            'protein_name': f"{protein.get('gene_name', 'Unknown')}",
            'gene_id': protein.get('gene_id', ''),
            'length': length,
            'hydrophobic_percent': hydrophobic_percent,
            'polar_percent': polar_percent,
            'charged_percent': charged_percent,
            'molecular_weight': mol_weight
        })
    
    df = pd.DataFrame(data)
    
    # Create 3D scatter plot with mesh surface
    fig = go.Figure()
    
    # Add data points
    fig.add_trace(go.Scatter3d(
        x=df['hydrophobic_percent'],
        y=df['polar_percent'],
        z=df['charged_percent'],
        mode='markers',
        marker=dict(
            size=df['length'] / 50,  # Size based on protein length
            color=df['molecular_weight'],
            colorscale='Viridis',
            colorbar=dict(title="Molecular Weight (Da)"),
            opacity=0.8
        ),
        text=df['protein_name'],
        hoverinfo='text',
        name='Proteins'
    ))
    
    # Create a mesh surface to show the relationship between the three amino acid properties
    # The sum of these should be around 100%
    x = np.linspace(0, 100, 10)
    y = np.linspace(0, 100, 10)
    X, Y = np.meshgrid(x, y)
    Z = 100 - X - Y
    Z[Z < 0] = 0  # Set negative values to 0
    
    fig.add_trace(go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale='Greys',
        opacity=0.3,
        showscale=False,
        name='AA Composition Surface'
    ))
    
    # Update layout
    fig.update_layout(
        title="3D Protein Properties Comparison",
        scene=dict(
            xaxis_title='Hydrophobic AA (%)',
            yaxis_title='Polar AA (%)',
            zaxis_title='Charged AA (%)',
            xaxis=dict(range=[0, 100]),
            yaxis=dict(range=[0, 100]),
            zaxis=dict(range=[0, 100]),
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig