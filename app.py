import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import requests
from io import StringIO
import time
import py3Dmol
from stmol import showmol
from streamlit_lottie import st_lottie

from utils.sequence_processor import (
    parse_fasta, 
    validate_sequence, 
    predict_amr_genes, 
    translate_to_protein
)
from utils.resistance_predictor import (
    analyze_protein_resistance,
    get_antibiotic_recommendations
)
from utils.visualization import (
    create_gene_visualization,
    create_resistance_heatmap,
    create_protein_domain_plot
)
from utils.openai_helper import generate_summary_report
from utils.protein_3d import render_protein_3d, create_interactive_protein_view, display_loading_animation

# Set page configuration
st.set_page_config(
    page_title="GeneHack AMR - Antimicrobial Resistance Predictor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for background, animations, and styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        background-image: linear-gradient(120deg, rgba(240,249,255,0.8) 0%, rgba(249,255,246,0.8) 100%);
    }
    .stApp {
        background-size: cover;
    }
    div.stButton > button {
        background-color: #2E86C1;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #1A5276;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .css-1v0mbdj.ebxwdo61 {
        border-radius: 0.7rem;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stAlert {
        border-radius: 0.7rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f3f4;
        border-radius: 4px 4px 0 0;
        padding-left: 16px;
        padding-right: 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E86C1;
        color: white;
    }
    h1, h2, h3 {
        color: #2C3E50;
    }
    .animate-charcter {
        background-image: linear-gradient(
            -225deg,
            #231557 0%,
            #44107a 29%,
            #ff1361 67%,
            #2E86C1 100%
        );
        background-size: auto auto;
        background-clip: border-box;
        background-size: 200% auto;
        color: #fff;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textclip 3s linear infinite;
        display: inline;
    }
    @keyframes textclip {
        to {
            background-position: 200% center;
        }
    }
    .loading-animation {
        width: 100%;
        height: 4px;
        background: linear-gradient(to right, #2E86C1, #2ECC71, #F4D03F);
        background-size: 200% 100%;
        animation: gradient-slide 2s linear infinite;
    }
    @keyframes gradient-slide {
        0% {background-position: 100% 0%;}
        100% {background-position: -100% 0%;}
    }
</style>
""", unsafe_allow_html=True)

# Function to load lottie files
def load_lottieurl(url: str):
    """
    Load a Lottie animation from a URL.
    """
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Load animations
dna_animation = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_xh8zdnlk.json")
bacteria_animation = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_ksyj8dkc.json")
analysis_animation = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_1cazwtnc.json")
laboratory_animation = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_wdqlqkhz.json")
molecule_animation = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_ry2uhxse.json")

# Create header with animation
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    # Application title and description with animated title
    st.markdown('<h1 class="animate-charcter">🧬 GeneHack AMR</h1>', unsafe_allow_html=True)
    st.subheader("Antimicrobial Resistance Prediction from Genomic Data")
    
    st.markdown("""
    This tool predicts antimicrobial resistance (AMR) from genetic sequences, identifies resistance genes, 
    translates them to proteins, and recommends effective antibiotics. Designed for researchers, healthcare 
    professionals, and bioinformatics experts.
    """)
    
    # Add loading animation bar
    st.markdown('<div class="loading-animation"></div>', unsafe_allow_html=True)

with header_col2:
    # DNA animation in the header
    if dna_animation:
        st_lottie(dna_animation, speed=1, height=200, key="dna_animation")

# Initialize session state variables if they don't exist
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'genes' not in st.session_state:
    st.session_state.genes = None
if 'proteins' not in st.session_state:
    st.session_state.proteins = None
if 'resistance_data' not in st.session_state:
    st.session_state.resistance_data = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'summary_report' not in st.session_state:
    st.session_state.summary_report = None

# Sidebar for input options
with st.sidebar:
    st.header("Input Options")
    
    # Add bacteria animation to sidebar
    if bacteria_animation:
        st_lottie(bacteria_animation, speed=1, height=150, key="bacteria_animation")
    
    input_method = st.radio("Select Input Method:", ["FASTA File", "Raw Sequence"])
    
    # Define sequence_data as None initially
    sequence_data = None
    
    if input_method == "FASTA File":
        uploaded_file = st.file_uploader("Upload FASTA file", type=["fasta", "fa", "fna", "ffn", "txt"])
        if uploaded_file is not None:
            sequence_data = uploaded_file.getvalue().decode("utf-8")
            st.success("File uploaded successfully!")
    else:
        sequence_data = st.text_area("Enter raw nucleotide sequence:", height=200, 
                                     help="Paste your DNA sequence here (A, T, G, C bases only)")
    
    analyze_button = st.button("Analyze Sequence", type="primary")
    
    if analyze_button and sequence_data:
        # Show loading animation before analysis
        progress_placeholder = st.empty()
        with progress_placeholder.container():
            if analysis_animation:
                st_lottie(analysis_animation, speed=1, height=200, key="analysis_animation")
            st.info("Analyzing your genetic sequence. This may take a moment...")
            
        try:
            # Validate and parse the sequence
            if input_method == "FASTA File":
                sequences = parse_fasta(sequence_data)
                if not sequences:
                    st.error("No valid sequences found in the FASTA file.")
                    st.stop()
            else:
                # For raw input, create a single sequence entry
                if validate_sequence(sequence_data):
                    sequences = [("Raw_Input_Sequence", sequence_data.strip().upper())]
                else:
                    st.error("Invalid nucleotide sequence. Please use only A, T, G, C characters.")
                    st.stop()
            
            # Add a small delay to show the animation
            time.sleep(1.5)
            
            # Clear the animation after loading is done
            progress_placeholder.empty()
            
            # Process all sequences
            all_genes = []
            all_proteins = []
            all_resistance = []
            
            for seq_name, seq in sequences:
                # Predict AMR genes
                genes = predict_amr_genes(seq)
                if genes:
                    for gene in genes:
                        gene['sequence_name'] = seq_name
                        all_genes.append(gene)
                        
                        # Translate gene to protein
                        protein = translate_to_protein(gene['sequence'])
                        protein_info = {
                            'gene_id': gene['id'],
                            'gene_name': gene['name'],
                            'sequence_name': seq_name,
                            'protein_sequence': protein
                        }
                        all_proteins.append(protein_info)
                        
                        # Analyze protein for resistance
                        resistance_info = analyze_protein_resistance(protein, gene['name'])
                        if resistance_info:
                            for info in resistance_info:
                                info['gene_id'] = gene['id']
                                info['gene_name'] = gene['name']
                                info['sequence_name'] = seq_name
                                all_resistance.append(info)
                
            if not all_genes:
                st.warning("No AMR genes detected in the provided sequence(s).")
                st.session_state.analyzed = False
                st.stop()
            
            # Get antibiotic recommendations
            recommendations = get_antibiotic_recommendations(all_resistance)
            
            # Generate summary report with OpenAI
            summary_data = {
                'genes': all_genes,
                'resistance': all_resistance,
                'recommendations': recommendations
            }
            summary_report = generate_summary_report(summary_data)
            
            # Update session state
            st.session_state.genes = all_genes
            st.session_state.proteins = all_proteins
            st.session_state.resistance_data = all_resistance
            st.session_state.recommendations = recommendations
            st.session_state.summary_report = summary_report
            st.session_state.analyzed = True
            
            st.success("Analysis complete!")
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            st.session_state.analyzed = False

# Main content area
if st.session_state.analyzed:
    # Summary section
    st.header("Analysis Summary")
    st.markdown(st.session_state.summary_report)
    
    # Create tabs for different result sections
    tab1, tab2, tab3, tab4 = st.tabs(["Predicted Genes", "Protein Sequences", "Resistance Analysis", "Antibiotic Recommendations"])
    
    with tab1:
        st.header("Predicted AMR Genes")
        
        if st.session_state.genes:
            # Convert to DataFrame for display
            genes_df = pd.DataFrame(st.session_state.genes)
            st.dataframe(genes_df[['sequence_name', 'id', 'name', 'start_pos', 'end_pos', 'confidence']], use_container_width=True)
            
            # Gene visualization
            st.subheader("Gene Location Visualization")
            gene_plot = create_gene_visualization(st.session_state.genes)
            st.plotly_chart(gene_plot, use_container_width=True)
        else:
            st.info("No AMR genes were detected in the sequence.")
    
    with tab2:
        st.header("Protein Sequences")
        
        if st.session_state.proteins:
            # Display protein sequences
            for i, protein in enumerate(st.session_state.proteins):
                with st.expander(f"Protein for gene {protein['gene_name']} ({protein['gene_id']})"):
                    # Create two columns for protein info and 3D structure
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown(f"**Sequence Name:** {protein['sequence_name']}")
                        st.markdown(f"**Gene Name:** {protein['gene_name']}")
                        st.markdown(f"**Gene ID:** {protein['gene_id']}")
                        st.text_area(f"Protein Sequence {i+1}", protein['protein_sequence'], height=150)
                    
                    with col2:
                        # Add 3D protein visualization
                        st.subheader("3D Protein Structure")
                        render_protein_3d(protein['gene_name'])
                        st.caption("Drag to rotate, scroll to zoom")
            
            # Protein domain visualization
            st.subheader("Protein Domain Analysis")
            protein_plot = create_protein_domain_plot(st.session_state.proteins)
            st.plotly_chart(protein_plot, use_container_width=True)
            
            # Add full 3D interactive view for the first protein
            if st.session_state.proteins:
                st.subheader("Interactive 3D Protein Analysis")
                st.info("Showing detailed 3D visualization and amino acid composition")
                create_interactive_protein_view(st.session_state.proteins[0])
        else:
            st.info("No protein sequences were generated.")
    
    with tab3:
        st.header("Resistance Analysis")
        
        if st.session_state.resistance_data:
            # Convert to DataFrame for display
            resistance_df = pd.DataFrame(st.session_state.resistance_data)
            st.dataframe(
                resistance_df[['sequence_name', 'gene_name', 'antibiotic', 'resistance_level', 'mechanism']], 
                use_container_width=True
            )
            
            # Resistance heatmap
            st.subheader("Resistance Heatmap")
            heatmap = create_resistance_heatmap(st.session_state.resistance_data)
            st.plotly_chart(heatmap, use_container_width=True)
            
            # Group resistance by mechanism
            if 'mechanism' in resistance_df.columns:
                st.subheader("Resistance Mechanisms")
                mech_counts = resistance_df['mechanism'].value_counts().reset_index()
                mech_counts.columns = ['Mechanism', 'Count']
                
                fig = px.pie(mech_counts, values='Count', names='Mechanism', 
                             title='Distribution of Resistance Mechanisms')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No resistance data was generated.")
    
    with tab4:
        st.header("Antibiotic Recommendations")
        
        if st.session_state.recommendations:
            # Separate effective and ineffective antibiotics
            effective = []
            ineffective = []
            
            for rec in st.session_state.recommendations:
                if rec['effective']:
                    effective.append(rec)
                else:
                    ineffective.append(rec)
            
            # Display effective antibiotics
            st.subheader("Recommended Effective Antibiotics")
            if effective:
                effective_df = pd.DataFrame(effective)
                st.dataframe(effective_df[['antibiotic', 'confidence', 'rationale']], use_container_width=True)
                
                # Visualize effectiveness confidence
                fig = px.bar(
                    effective_df, 
                    x='antibiotic', 
                    y='confidence',
                    title='Confidence in Antibiotic Effectiveness',
                    labels={'antibiotic': 'Antibiotic', 'confidence': 'Confidence Score (0-1)'},
                    color='confidence',
                    color_continuous_scale='Viridis',
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No effective antibiotics found based on the resistance profile.")
            
            # Display ineffective antibiotics
            st.subheader("Antibiotics Predicted to be Ineffective")
            if ineffective:
                ineffective_df = pd.DataFrame(ineffective)
                st.dataframe(ineffective_df[['antibiotic', 'confidence', 'rationale']], use_container_width=True)
            else:
                st.info("No ineffective antibiotics identified.")
        else:
            st.info("No antibiotic recommendations were generated.")
else:
    # Display instructions when no analysis has been done
    st.info("Please upload a FASTA file or enter a raw genetic sequence in the sidebar and click 'Analyze Sequence' to start.")
    
    # Add molecule animation to the main page when not analyzing
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if molecule_animation:
            st_lottie(molecule_animation, speed=1, height=300, key="molecule_animation")
    
    # Example/demo section
    with st.expander("How to use GeneHack AMR"):
        # Split content into columns
        demo_col1, demo_col2 = st.columns([3, 2])
        
        with demo_col1:
            st.markdown("""
            ### How to use this tool:
            
            1. **Input your genetic sequence** using one of two methods:
               - Upload a FASTA file (.fasta, .fa, .fna, .ffn, or .txt)
               - Paste a raw nucleotide sequence directly
            
            2. **Click 'Analyze Sequence'** to process the data
            
            3. **View the results** across different tabs:
               - Predicted AMR Genes
               - Protein Sequences
               - Resistance Analysis
               - Antibiotic Recommendations
            
            ### What GeneHack AMR does:
            
            - **Gene Prediction**: Identifies genes linked to antimicrobial resistance
            - **Protein Translation**: Converts genes to protein sequences
            - **Resistance Analysis**: Analyzes which antibiotics might be ineffective
            - **Recommendations**: Suggests which antibiotics might still be effective
            - **Visualization**: Provides interactive plots to understand the results
            """)
            
        with demo_col2:
            if laboratory_animation:
                st_lottie(laboratory_animation, speed=1, height=300, key="lab_animation")
