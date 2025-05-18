import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
import json

# Import custom modules
from data.database import (
    create_tables, save_analysis_result, get_analysis_result,
    get_analysis_history, save_sequence_data, get_sequence_data, 
    get_stored_sequences
)
from utils.sequence_processor import (
    validate_sequence, parse_fasta, predict_amr_genes, translate_to_protein
)
from utils.blast_search import search_amr_database
from utils.resistance_predictor import (
    analyze_protein_resistance, get_antibiotic_recommendations
)
from utils.visualization import (
    create_gene_visualization, create_resistance_heatmap, create_protein_domain_plot
)
from utils.protein_3d import render_protein_3d, create_interactive_protein_view
from utils.chatbot_assistant import (
    initialize_chat_history, add_analysis_context, 
    chat_with_assistant, generate_analysis_suggestions
)
from utils.openai_helper import generate_summary_report, generate_basic_report
from utils.enhanced_visualizations import (
    create_resistance_frequency_bar_chart, create_resistance_level_pie_chart,
    create_antibiotic_resistance_count_chart, create_resistance_mechanism_donut,
    create_3d_gene_clustering, create_3d_protein_comparison
)

# Create database tables if they don't exist
create_tables()

# Page configuration
st.set_page_config(
    page_title="GeneHack AMR - Antimicrobial Resistance Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load animations
def load_lottie_url(url):
    """Load a Lottie animation from a URL."""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load animations
molecule_animation = load_lottie_url('https://assets3.lottiefiles.com/packages/lf20_UgZWvP.json')
laboratory_animation = load_lottie_url('https://assets5.lottiefiles.com/packages/lf20_vwgfy3ve.json')
dna_loading_animation = load_lottie_url('https://assets6.lottiefiles.com/packages/lf20_ft8ck4lv.json')
analysis_loading_animation = load_lottie_url('https://assets2.lottiefiles.com/private_files/lf30_l8csvun7.json')
search_loading_animation = load_lottie_url('https://assets2.lottiefiles.com/packages/lf20_zwn6fgkj.json')
team_animation = load_lottie_url('https://assets1.lottiefiles.com/packages/lf20_vkwkzftx.json')
doctor_animation = load_lottie_url('https://assets1.lottiefiles.com/packages/lf20_s7vzlpm5.json')
genome_animation = load_lottie_url('https://assets4.lottiefiles.com/packages/lf20_xlmz9xwm.json')

# Initialize session state variables if they don't exist
if 'genes' not in st.session_state:
    st.session_state.genes = []
if 'proteins' not in st.session_state:
    st.session_state.proteins = []
if 'resistance_data' not in st.session_state:
    st.session_state.resistance_data = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'blast_results' not in st.session_state:
    st.session_state.blast_results = {}
if 'summary_report' not in st.session_state:
    st.session_state.summary_report = ""
if 'has_analysis' not in st.session_state:
    st.session_state.has_analysis = False
if 'result_saved' not in st.session_state:
    st.session_state.result_saved = False
if 'current_sequence_name' not in st.session_state:
    st.session_state.current_sequence_name = ""
if 'current_sequence_type' not in st.session_state:
    st.session_state.current_sequence_type = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = initialize_chat_history()
if 'current_sequence' not in st.session_state:
    st.session_state.current_sequence = ""
if 'use_blast_search' not in st.session_state:
    st.session_state.use_blast_search = True
if 'nav_page' not in st.session_state:
    st.session_state.nav_page = "home"
if 'show_landing_page' not in st.session_state:
    st.session_state.show_landing_page = True

# Custom CSS with medical theme
st.markdown("""
<style>
    /* Main Background styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    
    [data-testid="stAppViewBlockContainer"] {
        background-color: #ffffff;
        background-image: 
            linear-gradient(135deg, rgba(210, 235, 255, 0.1) 25%, transparent 25%),
            linear-gradient(225deg, rgba(210, 235, 255, 0.1) 25%, transparent 25%),
            linear-gradient(45deg, rgba(210, 235, 255, 0.1) 25%, transparent 25%),
            linear-gradient(315deg, rgba(210, 235, 255, 0.1) 25%, transparent 25%);
        background-position: 40px 0, 40px 0, 0 0, 0 0;
        background-size: 80px 80px;
        background-repeat: repeat;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        color: #1976d2;
        margin-bottom: 1rem;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0d47a1;
        margin-bottom: 1rem;
        font-weight: 400;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding: 10px 16px;
        font-weight: 500;
        border: 1px solid #e9ecef;
        border-bottom: none;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1976d2;
        color: white;
        border-color: #1976d2;
        transform: translateY(-4px);
    }
    
    /* Cards for content */
    .stCard {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Metrics styling */
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #e9ecef;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e9ecef;
    }
    .dataframe th {
        background-color: #1976d2;
        color: white;
        font-weight: 500;
    }
    
    /* Info/warning boxes */
    .stAlert {
        border-radius: 8px;
    }
    
    /* Navigation buttons */
    .nav-button {
        display: block;
        width: 100%;
        padding: 12px 15px;
        margin-bottom: 8px;
        background-color: #f8f9fa;
        border-radius: 8px;
        text-decoration: none;
        color: #0d47a1;
        font-weight: 500;
        font-size: 1.05rem;
        border-left: 3px solid transparent;
        transition: all 0.2s ease;
    }
    .nav-button:hover {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
        cursor: pointer;
    }
    .nav-button.active {
        background-color: #e3f2fd;
        border-left-color: #1976d2;
        color: #1976d2;
        font-weight: 600;
    }
    .nav-icon {
        margin-right: 10px;
        font-size: 1.2em;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with medical theme
with st.sidebar:
    st.markdown('<div class="main-header">GeneHack AMR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Antimicrobial Resistance Analysis</div>', unsafe_allow_html=True)
    
    # Add a divider
    st.markdown('<hr style="height:2px;border:none;color:#e0e0e0;background-color:#e0e0e0;" />', unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        home_class = "nav-button active" if st.session_state.nav_page == "home" else "nav-button"
        if st.button("🏠 Home", key="home_nav", help="Search and analyze bacterial genomes"):
            st.session_state.nav_page = "home"
            st.rerun()
    
    with col2:
        history_class = "nav-button active" if st.session_state.nav_page == "history" else "nav-button"
        if st.button("📋 History", key="history_nav", help="View analysis history"):
            st.session_state.nav_page = "history"
            st.rerun()
            
    # Input options visible only in Home page
    if st.session_state.nav_page == "home":
        # Input section
        st.subheader("Sequence Input")
        st.markdown("Input bacterial genome sequence for antimicrobial resistance analysis")
        input_method = st.radio("Select input method", 
                                ["Upload FASTA File", "Enter Raw Sequence", "Load Saved Sequence"])
        
        # Analysis options
        with st.expander("Analysis Options", expanded=True):
            use_blast = st.checkbox("Use BLAST for resistance gene detection", 
                                   value=st.session_state.use_blast_search,
                                   help="Use BLAST to search for resistance genes against known AMR databases")
            st.session_state.use_blast_search = use_blast
            
            if use_blast:
                st.info("BLAST search will provide more accurate resistance gene identification and antibiotic effectiveness predictions.")
        
        # Initialize sequence variable
        sequence = ""
        
        if input_method == "Upload FASTA File":
            uploaded_file = st.file_uploader("Upload FASTA file", 
                                             type=["fasta", "fa", "fna", "ffn", "txt"])
            
            if uploaded_file is not None:
                file_content = uploaded_file.getvalue().decode("utf-8")
                sequences = parse_fasta(file_content)
                
                if sequences:
                    # If multiple sequences found, let user select one
                    if len(sequences) > 1:
                        sequence_options = [f"{name} ({len(seq)} bp)" for name, seq in sequences]
                        selected_seq = st.selectbox("Select sequence to analyze:", sequence_options)
                        selected_idx = sequence_options.index(selected_seq)
                        seq_name, sequence = sequences[selected_idx]
                    else:
                        seq_name, sequence = sequences[0]
                    
                    st.session_state.current_sequence_name = seq_name
                    st.session_state.current_sequence_type = "fasta"
                    
                    # Display sequence info
                    st.info(f"Sequence: {seq_name} ({len(sequence)} bp)")
                else:
                    st.error("No valid sequences found in file.")
                    sequence = ""
        
        elif input_method == "Enter Raw Sequence":
            sequence = st.text_area("Enter DNA sequence", 
                                 height=150, 
                                 help="Paste a raw DNA sequence (A, T, G, C).")
            
            st.session_state.current_sequence_name = "Raw Sequence"
            st.session_state.current_sequence_type = "raw"
            
            # Validate sequence
            if sequence:
                if validate_sequence(sequence):
                    st.info(f"Valid DNA sequence ({len(sequence)} bp)")
                else:
                    st.error("Invalid DNA sequence. Please use only A, T, G, and C nucleotides.")
                    sequence = ""
        
        elif input_method == "Load Saved Sequence":
            saved_sequences = get_stored_sequences(limit=50)
            
            if saved_sequences:
                sequence_options = [f"{seq['name']} ({seq['data_type']}, ID: {seq['id']})" for seq in saved_sequences]
                selected_option = st.selectbox("Select saved sequence:", sequence_options)
                
                # Extract ID from selected option
                selected_id = int(selected_option.split("ID: ")[1].split(")")[0])
                
                # Get the selected sequence data
                selected_seq = get_sequence_data(selected_id)
                
                if selected_seq:
                    sequence = selected_seq["sequence"]
                    st.session_state.current_sequence_name = selected_seq["name"]
                    st.session_state.current_sequence_type = selected_seq["data_type"]
                    
                    st.info(f"Loaded sequence: {selected_seq['name']} ({len(sequence)} bp)")
                else:
                    st.error("Failed to load sequence data.")
                    sequence = ""
            else:
                st.info("No saved sequences found.")
                sequence = ""
        
        # Analysis button
        analyze_button = st.button("Analyze Sequence", type="primary", disabled=not sequence)
        
        if analyze_button and sequence:
            # Reset session state for new analysis
            st.session_state.genes = []
            st.session_state.proteins = []
            st.session_state.resistance_data = []
            st.session_state.recommendations = []
            st.session_state.summary_report = ""
            st.session_state.has_analysis = False
            st.session_state.result_saved = False
            
            # Save current sequence for later use
            st.session_state.current_sequence = sequence
            
            # Create a container for the loading animation
            loading_container = st.empty()
            
            # Show animated loading indicators
            with loading_container.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown("<h3 style='text-align: center; color: #1976d2;'>Analyzing Bacterial Genome</h3>", unsafe_allow_html=True)
                    if dna_loading_animation:
                        st_lottie(dna_loading_animation, speed=1, height=200, key="dna_loading")
                    st.markdown("<p style='text-align: center; color: #666;'>Processing sequence data for resistance markers...</p>", unsafe_allow_html=True)
            
            # Show progress
            with st.spinner("Analyzing bacterial genome for resistance genes..."):
                if st.session_state.use_blast_search:
                    # Approach 1: Use BLAST search for more accurate results
                    with st.status("Running BLAST search against AMR databases...", expanded=True) as status:
                        # Update animation to show search-specific animation
                        with loading_container.container():
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                st.markdown("<h3 style='text-align: center; color: #1976d2;'>Running BLAST Search</h3>", unsafe_allow_html=True)
                                if search_loading_animation:
                                    st_lottie(search_loading_animation, speed=1, height=200, key="search_loading")
                                st.markdown("<p style='text-align: center; color: #666;'>Searching for resistance genes in databases...</p>", unsafe_allow_html=True)
                        
                        st.write("Searching for resistance genes...")
                        
                        # Run BLAST search
                        blast_results = search_amr_database(
                            sequence=sequence,
                            sequence_name=st.session_state.current_sequence_name
                        )
                        
                        # Store BLAST results
                        st.session_state.blast_results = blast_results
                        
                        # Convert BLAST hits to gene predictions
                        st.session_state.genes = []
                        gene_id = 1
                        
                        for hit in blast_results.get('all_hits', []):
                            gene_name = hit['title'].split()[0]  # First word of hit title
                            st.session_state.genes.append({
                                'id': f"BLAST_{gene_id}",
                                'name': gene_name,
                                'sequence_name': st.session_state.current_sequence_name,
                                'start_pos': hit['query_start'],
                                'end_pos': hit['query_end'],
                                'confidence': hit['identity'],
                                'description': hit['title'],
                                'e_value': hit['e_value']
                            })
                            gene_id += 1
                        
                        # Extract resistance data from BLAST results
                        st.session_state.resistance_data = []
                        
                        for class_name, hits in blast_results.get('hits_by_class', {}).items():
                            for hit in hits:
                                antibiotic_class = class_name.replace('_', ' ').title()
                                st.session_state.resistance_data.append({
                                    'sequence_name': st.session_state.current_sequence_name,
                                    'gene_name': hit['title'].split()[0],
                                    'gene_id': hit['accession'],
                                    'antibiotic': antibiotic_class,
                                    'resistance_level': 'High' if hit['identity'] > 0.9 else 'Moderate' if hit['identity'] > 0.8 else 'Low',
                                    'mechanism': 'Unknown' if 'mechanism' not in hit else hit['mechanism'],
                                    'confidence': hit['identity']
                                })
                        
                        # Set recommendations from BLAST results
                        st.session_state.recommendations = []
                        
                        for antibiotic, data in blast_results.get('antibiotic_effectiveness', {}).items():
                            st.session_state.recommendations.append({
                                'antibiotic': antibiotic,
                                'effective': data['effective'],
                                'confidence': data['confidence'],
                                'rationale': data['rationale']
                            })
                        
                        # Generate protein sequences from genes
                        st.session_state.proteins = []
                        for gene in st.session_state.genes:
                            # Extract gene sequence if we have position info
                            if 'start_pos' in gene and 'end_pos' in gene:
                                start = max(0, gene['start_pos'] - 1)  # 1-based to 0-based
                                end = min(len(sequence), gene['end_pos'])
                                gene_seq = sequence[start:end]
                                
                                # Translate to protein
                                protein_seq = translate_to_protein(gene_seq)
                                
                                # Store protein data
                                st.session_state.proteins.append({
                                    'sequence_name': gene['sequence_name'],
                                    'gene_id': gene['id'],
                                    'gene_name': gene['name'],
                                    'protein_sequence': protein_seq,
                                    'length': len(protein_seq),
                                    'domains': gene.get('domains', []),
                                    'functions': gene.get('functions', [])
                                })
                        
                        # Update animation to show analysis animation
                        with loading_container.container():
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                st.markdown("<h3 style='text-align: center; color: #1976d2;'>Analyzing Results</h3>", unsafe_allow_html=True)
                                if analysis_loading_animation:
                                    st_lottie(analysis_loading_animation, speed=1, height=200, key="analysis_loading")
                                st.markdown("<p style='text-align: center; color: #666;'>Analyzing resistance patterns and generating recommendations...</p>", unsafe_allow_html=True)
                        
                        status.update(label="BLAST search complete", state="complete", expanded=False)
                else:
                    # Approach 2: Use built-in prediction methods (fallback)
                    # Show different animation for this path
                    with loading_container.container():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.markdown("<h3 style='text-align: center; color: #1976d2;'>Gene Prediction</h3>", unsafe_allow_html=True)
                            if analysis_loading_animation:
                                st_lottie(analysis_loading_animation, speed=1, height=200, key="gene_loading")
                            st.markdown("<p style='text-align: center; color: #666;'>Predicting resistance genes from sequence patterns...</p>", unsafe_allow_html=True)
                    
                    # 1. Predict AMR genes
                    st.session_state.genes = predict_amr_genes(
                        sequence=sequence,
                        sequence_name=st.session_state.current_sequence_name
                    )
                    
                    # 2. Generate protein sequences
                    st.session_state.proteins = []
                    for gene in st.session_state.genes:
                        # Extract gene sequence
                        gene_seq = sequence[gene['start_pos']:gene['end_pos']]
                        
                        # Translate to protein
                        protein_seq = translate_to_protein(gene_seq)
                        
                        # Store protein data
                        st.session_state.proteins.append({
                            'sequence_name': gene['sequence_name'],
                            'gene_id': gene['id'],
                            'gene_name': gene['name'],
                            'protein_sequence': protein_seq,
                            'length': len(protein_seq),
                            'domains': gene.get('domains', []),
                            'functions': gene.get('functions', [])
                        })
                    
                    # 3. Analyze resistance
                    st.session_state.resistance_data = []
                    for protein in st.session_state.proteins:
                        # Analyze protein for resistance markers
                        resistance_results = analyze_protein_resistance(
                            protein['protein_sequence'], 
                            protein['gene_name']
                        )
                        
                        # Add sequence name to resistance data
                        for r in resistance_results:
                            r['sequence_name'] = protein['sequence_name']
                            r['gene_id'] = protein['gene_id']
                        
                        # Add to session state
                        st.session_state.resistance_data.extend(resistance_results)
                    
                    # 4. Generate recommendations
                    st.session_state.recommendations = get_antibiotic_recommendations(
                        st.session_state.resistance_data
                    )
                
                # 5. Generate summary report
                # Show final report generation animation
                with loading_container.container():
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.markdown("<h3 style='text-align: center; color: #1976d2;'>Generating Report</h3>", unsafe_allow_html=True)
                        if dna_loading_animation:
                            st_lottie(dna_loading_animation, speed=1, height=200, key="summary_loading")
                        st.markdown("<p style='text-align: center; color: #666;'>Creating comprehensive analysis report...</p>", unsafe_allow_html=True)
                
                try:
                    st.session_state.summary_report = generate_summary_report({
                        'genes': st.session_state.genes,
                        'resistance_data': st.session_state.resistance_data,
                        'recommendations': st.session_state.recommendations
                    })
                except Exception as e:
                    # Fallback to basic report if API call fails
                    st.warning(f"Could not generate AI summary: {str(e)}. Using basic summary instead.")
                    st.session_state.summary_report = generate_basic_report({
                        'genes': st.session_state.genes,
                        'resistance_data': st.session_state.resistance_data,
                        'recommendations': st.session_state.recommendations
                    })
                    
                # Clear the loading animation container when done
                loading_container.empty()
                
                # 6. Save sequence if it's not already in the database
                if input_method != "Load Saved Sequence":
                    try:
                        save_sequence_data(
                            name=st.session_state.current_sequence_name,
                            data_type=st.session_state.current_sequence_type,
                            sequence=sequence,
                            description=f"Sequence with {len(st.session_state.genes)} AMR genes"
                        )
                    except Exception as e:
                        st.sidebar.warning(f"Failed to save sequence: {str(e)}")
                
                # Update chat history with analysis context
                st.session_state.chat_history = add_analysis_context(
                    st.session_state.chat_history,
                    {
                        'genes': st.session_state.genes,
                        'proteins': st.session_state.proteins,
                        'resistance_data': st.session_state.resistance_data
                    }
                )
                
                # Mark analysis as complete
                st.session_state.has_analysis = True
                
                # Rerun to update UI
                st.rerun()

# Check if we should show the landing page or the main app
if st.session_state.show_landing_page:
    # Hide sidebar for landing page
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Landing page content
    st.markdown("""
    <div style="text-align: center; margin-top: 10px;">
        <h1 style="color: #0d47a1; font-size: 3.5rem; margin-bottom: 10px; font-weight: 700;">GeneHack AMR</h1>
        <p style="color: #424242; font-size: 1.5rem; margin-bottom: 30px;">Revolutionizing Antimicrobial Resistance Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Animated banner
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if genome_animation:
            st_lottie(genome_animation, speed=1, height=250, key="genome")
    
    # Project introduction
    st.markdown("""
    <div style="background-color: #f0f7ff; padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #1976d2;">
        <h2 style="color: #0d47a1; margin-top: 0;">Docathon Collaboration Project</h2>
        <p style="color: #424242; font-size: 1.1rem; line-height: 1.6;">
            GeneHack AMR is a groundbreaking tool developed during the Docathon - an innovative hackathon bringing together 
            healthcare professionals and software engineers to solve critical medical challenges. This tool emerged from 
            the collaboration between doctors with expertise in infectious diseases and engineers skilled in genomic analysis and AI.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("<h2 style='color: #0d47a1; text-align: center; margin: 40px 0 30px;'>Key Features</h2>", unsafe_allow_html=True)
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 10px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
            <h3 style="color: #1976d2; font-size: 1.3rem;">🧬 Genomic Analysis</h3>
            <p style="color: #616161;">Identify antimicrobial resistance genes in bacterial genomes with precision using advanced BLAST technology.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 10px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
            <h3 style="color: #1976d2; font-size: 1.3rem;">💊 Antibiotic Recommendations</h3>
            <p style="color: #616161;">Receive data-driven guidance on effective antibiotics based on the resistance profile of analyzed bacteria.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with feature_col3:
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 10px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
            <h3 style="color: #1976d2; font-size: 1.3rem;">🔬 Interactive Visualizations</h3>
            <p style="color: #616161;">Explore resistance markers, protein structures, and antibiotic effectiveness through intuitive visual interfaces.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Team section
    st.markdown("<h2 style='color: #0d47a1; text-align: center; margin: 40px 0 30px;'>Interdisciplinary Team</h2>", unsafe_allow_html=True)
    
    team_col1, team_col2 = st.columns([1, 1])
    
    with team_col1:
        if doctor_animation:
            st_lottie(doctor_animation, speed=1, height=200, key="doctor")
        st.markdown("""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;">
            <h3 style="color: #1565c0; margin-top: 0;">Medical Professionals</h3>
            <p style="color: #424242;">Infectious disease specialists contributing clinical expertise on antimicrobial resistance mechanisms and treatment protocols.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with team_col2:
        if team_animation:
            st_lottie(team_animation, speed=1, height=200, key="team")
        st.markdown("""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;">
            <h3 style="color: #1565c0; margin-top: 0;">Software Engineers</h3>
            <p style="color: #424242;">Bioinformatics and AI specialists building the computational infrastructure for genetic analysis and data visualization.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Impact section
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 25px; border-radius: 10px; margin: 40px 0 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #43a047;">
        <h2 style="color: #2e7d32; margin-top: 0;">Healthcare Impact</h2>
        <p style="color: #424242; font-size: 1.1rem; line-height: 1.6;">
            Antimicrobial resistance is one of the top 10 global public health threats facing humanity according to the WHO. 
            GeneHack AMR empowers healthcare providers with rapid bacterial genome analysis to choose effective antibiotics, 
            leading to better patient outcomes, reduced treatment failures, and slower development of resistance.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Call to action button
    st.markdown("<div style='text-align: center; margin: 50px 0;'>", unsafe_allow_html=True)
    
    if st.button("🚀 Try GeneHack AMR Now", key="try_app_button", type="primary", 
                use_container_width=True, help="Launch the application"):
        # Switch to main app
        st.session_state.show_landing_page = False
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
        <p style="color: #9e9e9e; font-size: 0.9rem;">
            © 2025 GeneHack AMR | Developed during Docathon | Streamlit Powered
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Regular app content with sidebar visible
    # Title with medical styling
    st.markdown("""
    <div style="background-color: #f0f7ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1976d2; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
        <h1 style="color: #0d47a1; margin: 0; font-size: 2.2rem;">Bacterial Genome Antimicrobial Resistance Analysis</h1>
        <p style="color: #666; margin-top: 5px; font-size: 1.1rem;">Identify resistance genes and effective antibiotics through genomic analysis</p>
    </div>
    """, unsafe_allow_html=True)

# Handle navigation between Home and History pages
if st.session_state.nav_page == "history":
    # History page - show past analyses
    st.subheader("Analysis History")
    st.markdown("View and load previous bacterial genome analyses")
    
    # Display history in a styled container
    history_container = st.container()
    with history_container:
        history = get_analysis_history(limit=20)
        if history:
            for i, item in enumerate(history):
                with st.container():
                    # Create a styled card for each history item
                    # Format the date - handling both datetime and string formats
                    date_str = ""
                    if item['created_at']:
                        if hasattr(item['created_at'], 'strftime'):
                            # If it's a datetime object
                            date_str = item['created_at'].strftime('%Y-%m-%d %H:%M')
                        else:
                            # If it's already a string
                            date_str = str(item['created_at'])
                    
                    st.markdown(f"""
                    <div style="background-color: white; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
                        <h3 style="color: #0d47a1; margin-top: 0; font-size: 1.2rem;">{item['sequence_name']}</h3>
                        <p style="color: #666; margin-bottom: 5px; font-size: 0.9rem;">
                            <span style="color: #1976d2;">ID:</span> {item['id']} | 
                            <span style="color: #1976d2;">Date:</span> {date_str}
                        </p>
                        <p style="color: #666; font-size: 0.9rem;">
                            <span style="background-color: #e3f2fd; padding: 3px 8px; border-radius: 4px; margin-right: 10px;">
                                <span style="color: #1976d2;">Genes:</span> {item['num_genes']}
                            </span>
                            <span style="background-color: #e3f2fd; padding: 3px 8px; border-radius: 4px;">
                                <span style="color: #1976d2;">Resistance Markers:</span> {item['num_resistance_markers']}
                            </span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Load Analysis", key=f"load_{item['id']}", help="Load this analysis result"):
                        # Load analysis from history
                        result = get_analysis_result(item['id'])
                        if result:
                            # Update session state
                            st.session_state.genes = result['genes']
                            st.session_state.proteins = result['proteins']
                            st.session_state.resistance_data = result['resistance_data']
                            st.session_state.recommendations = result['recommendations']
                            st.session_state.summary_report = result['summary_report']
                            st.session_state.has_analysis = True
                            st.session_state.result_saved = True
                            st.session_state.current_sequence_name = result['sequence_name']
                            st.session_state.current_sequence_type = result['sequence_type']
                            
                            # Switch to home page to display results
                            st.session_state.nav_page = "home"
                            
                            # Rerun to update UI
                            st.rerun()
                        else:
                            st.error("Failed to load result.")
        else:
            st.info("No analysis history found. Run analyses from the Home page to see them here.")
            
            # Add a button to go to home page
            if st.button("Go to Home Page", type="primary"):
                st.session_state.nav_page = "home"
                st.rerun()

elif st.session_state.nav_page == "home":
    # Home page - show analysis results if available
    
    # Only show analysis results if we have data
    if st.session_state.has_analysis:
        # Create columns for save UI
        save_col1, save_col2 = st.columns([3, 1])
        
        # Initialize sequence_name variable
        sequence_name = st.session_state.current_sequence_name if st.session_state.current_sequence_name else "My Sequence"
        
        with save_col1:
            if not st.session_state.result_saved:
                sequence_name = st.text_input("Sequence Name for Saving", 
                                             value=sequence_name)
            else:
                st.info(f"Saved as: {st.session_state.current_sequence_name} ✓")
        
        # Initialize save_button variable
        save_button = False
        
        with save_col2:
            if not st.session_state.result_saved:
                save_button = st.button("Save Results", type="primary")
            else:
                st.success("Saved to Database")
        
        # Handle save button click
        if not st.session_state.result_saved and save_button:
            # Check for required data
            if not st.session_state.genes or not st.session_state.proteins:
                st.error("Missing analysis data. Cannot save incomplete results.")
            else:
                try:
                    # Make sure summary report is not None
                    summary_report = st.session_state.summary_report or ""
                    
                    # Save analysis result to database
                    result_id = save_analysis_result(
                        sequence_name=sequence_name,
                        sequence_type=st.session_state.current_sequence_type or "raw",
                        genes=st.session_state.genes,
                        proteins=st.session_state.proteins,
                        resistance_data=st.session_state.resistance_data,
                        recommendations=st.session_state.recommendations,
                        summary_report=summary_report
                    )
                    
                    # Update session state
                    st.session_state.result_saved = True
                    st.session_state.current_sequence_name = sequence_name
                    
                    # Show success message
                    st.success(f"Results saved successfully! ID: {result_id}")
                    
                    # Refresh the page to update the UI
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving results: {str(e)}")
        
        # Display summary report
        st.markdown(st.session_state.summary_report)
        
        # Create tabs for different result sections
        tabs = ["Predicted Genes", "Protein Sequences", "Resistance Analysis", "Antibiotic Recommendations"]
        
        # Add BLAST results tab if using BLAST search
        if st.session_state.use_blast_search:
            tabs.append("BLAST Results")
        
        # Create the tabs dynamically
        all_tabs = st.tabs(tabs)
        
        # Tab 0: Predicted Genes
        with all_tabs[0]:
            st.header("Predicted AMR Genes")
            
            if st.session_state.genes:
                # Convert to DataFrame for display
                genes_df = pd.DataFrame(st.session_state.genes)
                
                # Create organism mapping dictionary based on gene names
                organism_mapping = {
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
                
                # Map gene names to organism names
                genes_df['organism'] = genes_df['name'].apply(
                    lambda x: organism_mapping.get(x, 'Unknown organism')
                )
                
                # Display the DataFrame with organism names instead of sequence_name
                st.dataframe(genes_df[['organism', 'id', 'name', 'start_pos', 'end_pos', 'confidence']], use_container_width=True)
                
                # Gene visualization
                st.subheader("Gene Location Visualization")
                gene_plot = create_gene_visualization(st.session_state.genes)
                st.plotly_chart(gene_plot, use_container_width=True)
            else:
                st.info("No AMR genes were detected in the sequence.")
        
        # Tab 1: Protein Sequences
        with all_tabs[1]:
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
        
        # Tab 2: Resistance Analysis
        with all_tabs[2]:
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
        
        # Tab 3: Antibiotic Recommendations
        with all_tabs[3]:
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
                
                # Display effective antibiotics with medical styling
                st.markdown("""
                <div style="background-color: #f0fff0; padding: 15px; border-radius: 8px; border-left: 5px solid #4caf50; margin-bottom: 15px;">
                    <h3 style="color: #2e7d32; margin-top: 0;">Recommended Effective Antibiotics</h3>
                    <p style="color: #666; font-size: 0.9rem;">Based on resistance gene analysis from bacterial genome sequencing</p>
                </div>
                """, unsafe_allow_html=True)
                
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
                
                # Display ineffective antibiotics with medical styling
                st.markdown("""
                <div style="background-color: #fff5f5; padding: 15px; border-radius: 8px; border-left: 5px solid #f44336; margin-bottom: 15px; margin-top: 25px;">
                    <h3 style="color: #c62828; margin-top: 0;">Antibiotics Predicted to be Ineffective</h3>
                    <p style="color: #666; font-size: 0.9rem;">Resistance genes detected in bacterial genome analysis</p>
                </div>
                """, unsafe_allow_html=True)
                
                if ineffective:
                    ineffective_df = pd.DataFrame(ineffective)
                    st.dataframe(ineffective_df[['antibiotic', 'confidence', 'rationale']], use_container_width=True)
                    
                    # Add visualization for ineffective antibiotics
                    if len(ineffective) > 1:
                        fig = px.bar(
                            ineffective_df, 
                            x='antibiotic', 
                            y='confidence',
                            title='Confidence in Antibiotic Ineffectiveness',
                            labels={'antibiotic': 'Antibiotic', 'confidence': 'Confidence Score (0-1)'},
                            color='confidence',
                            color_continuous_scale='Reds',
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No ineffective antibiotics identified.")
            else:
                st.info("No antibiotic recommendations were generated.")
        
        # Tab 4: BLAST Results (only shown if using BLAST search)
        if st.session_state.use_blast_search and len(all_tabs) > 4:
            with all_tabs[4]:
                st.header("BLAST Search Results")
                
                if st.session_state.blast_results:
                    # Overview statistics
                    st.subheader("Overview")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Hits", st.session_state.blast_results.get('total_hits', 0))
                    
                    with col2:
                        num_classes = len(st.session_state.blast_results.get('hits_by_class', {}))
                        st.metric("Resistance Classes", num_classes)
                    
                    with col3:
                        num_antibiotics = len(st.session_state.blast_results.get('antibiotic_effectiveness', {}))
                        st.metric("Antibiotics Analyzed", num_antibiotics)
                    
                    # Resistance classes bar chart
                    st.subheader("Resistance Genes by Class")
                    hits_by_class = st.session_state.blast_results.get('hits_by_class', {})
                    
                    if hits_by_class:
                        class_counts = {k: len(v) for k, v in hits_by_class.items()}
                        class_df = pd.DataFrame({
                            'Class': [k.replace('_', ' ').title() for k in class_counts.keys()],
                            'Count': list(class_counts.values())
                        })
                        
                        fig = px.bar(
                            class_df,
                            x='Class',
                            y='Count',
                            title='Resistance Genes Detected by Class',
                            color='Count',
                            color_continuous_scale='Reds'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Top hits table
                    st.subheader("Top Resistance Gene Hits")
                    all_hits = st.session_state.blast_results.get('all_hits', [])
                    
                    if all_hits:
                        # Create DataFrame with relevant columns
                        hits_df = pd.DataFrame([{
                            'Title': hit['title'],
                            'E-value': hit['e_value'],
                            'Identity (%)': round(hit['identity'] * 100, 2),
                            'Length': hit['length'],
                            'Score': hit['score'],
                            'Accession': hit['accession']
                        } for hit in all_hits])
                        
                        # Sort by identity (higher is better)
                        hits_df = hits_df.sort_values('Identity (%)', ascending=False)
                        
                        # Display table
                        st.dataframe(hits_df, use_container_width=True)
                        
                        # Show detailed hit information in expanders
                        st.subheader("Detailed Hit Information")
                        
                        for i, hit in enumerate(all_hits[:10]):  # Show top 10 hits only to avoid clutter
                            with st.expander(f"Hit {i+1}: {hit['title'][:50]}..."):
                                st.markdown(f"**Accession:** {hit['accession']}")
                                st.markdown(f"**E-value:** {hit['e_value']:.2e}")
                                st.markdown(f"**Identity:** {hit['identity']*100:.2f}%")
                                st.markdown(f"**Alignment Length:** {hit['length']} bp")
                                st.markdown(f"**Query Range:** {hit['query_start']} - {hit['query_end']}")
                                
                                # Show sequence alignment
                                st.subheader("Sequence Alignment")
                                alignment_text = f"""
                                ```
                                Query: {hit['query']}
                                       {hit['alignment']}
                                Sbjct: {hit['sbjct']}
                                ```
                                """
                                st.markdown(alignment_text)
                                
                                # Get related antibiotics
                                related_antibiotics = []
                                for antibiotic, data in st.session_state.blast_results.get('antibiotic_effectiveness', {}).items():
                                    if hit['title'].lower() in data['rationale'].lower():
                                        effectiveness = "✅ Effective" if data['effective'] else "❌ Not Effective"
                                        related_antibiotics.append(f"{antibiotic}: {effectiveness} ({data['rationale']})")
                                
                                if related_antibiotics:
                                    st.subheader("Related Antibiotics")
                                    for ab in related_antibiotics:
                                        st.markdown(f"- {ab}")
                    else:
                        st.info("No BLAST hits found. Try lowering the significance threshold or use a different sequence.")
                else:
                    st.info("No BLAST results available. Run the analysis with BLAST search enabled to see results here.")
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

# Add footer
st.markdown("---")
st.markdown("### 🧬 GeneHack AMR")
st.markdown("Antimicrobial Resistance Analysis Platform for Bacterial Genomes")

# Create Streamlit config directory and config.toml file if not exists
import os
if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")

if not os.path.exists(".streamlit/config.toml"):
    with open(".streamlit/config.toml", "w") as f:
        f.write("""
[server]
headless = true
address = "0.0.0.0"
port = 5000
        """)