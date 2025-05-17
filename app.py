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

# Initialize session state variables if they don't exist
if 'genes' not in st.session_state:
    st.session_state.genes = []
if 'proteins' not in st.session_state:
    st.session_state.proteins = []
if 'resistance_data' not in st.session_state:
    st.session_state.resistance_data = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4f8bf9;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #6c757d;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4f8bf9;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://i.imgur.com/1HZXeGH.png", width=100)
    st.markdown('<div class="main-header">GeneHack AMR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Antimicrobial Resistance Analysis</div>', unsafe_allow_html=True)
    
    # Input section
    st.subheader("Sequence Input")
    input_method = st.radio("Select input method", 
                            ["Upload FASTA File", "Enter Raw Sequence", "Load Saved Sequence"])
    
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
        
        # Show progress
        with st.spinner("Analyzing genetic sequence..."):
            # 1. Predict AMR genes
            st.session_state.genes = predict_amr_genes(sequence)
            
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
    
    # Display history
    with st.expander("View Analysis History", expanded=False):
        st.subheader("Past Analyses")
        
        history = get_analysis_history(limit=10)
        if history:
            for item in history:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{item['sequence_name']}**")
                        st.caption(f"ID: {item['id']} | Date: {item['created_at'].strftime('%Y-%m-%d %H:%M')}")
                        st.caption(f"Genes: {item['num_genes']} | Markers: {item['num_resistance_markers']}")
                    with col2:
                        if st.button("Load", key=f"load_{item['id']}"):
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
                                
                                # Rerun to update UI
                                st.rerun()
                            else:
                                st.error("Failed to load result.")
                    st.divider()
        else:
            st.info("No analysis history found.")

# Main content
st.title("Genomic Antimicrobial Resistance Analysis")

# Only show analysis results if we have data
if st.session_state.has_analysis:
    # Create columns for save UI
    save_col1, save_col2 = st.columns([3, 1])
    
    with save_col1:
        if not st.session_state.result_saved:
            sequence_name = st.text_input("Sequence Name for Saving", 
                                         value=st.session_state.current_sequence_name if st.session_state.current_sequence_name else "My Sequence")
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

# Add chatbot assistant
st.markdown("---")
st.header("💬 AI Research Assistant")
st.markdown("Ask questions about your analysis or get help interpreting results.")

# Create two columns - one for chat history and one for suggestions
chat_col1, chat_col2 = st.columns([2, 1])

with chat_col1:
    # Chat input area
    user_input = st.text_input("Enter your question:", key="chat_input", placeholder="e.g., What do the resistance findings mean?")
    
    # Process user input
    if user_input:
        # Get AI response
        response = chat_with_assistant(st.session_state.chat_history, user_input)
        
        # Update chat history
        st.session_state.chat_history = response["chat_history"]
        
        # Clear input after processing
        st.rerun()
    
    # Display chat history
    st.subheader("Conversation")
    
    # Skip the system message when displaying
    for message in st.session_state.chat_history[1:]:
        role = message['role']
        content = message['content']
        
        if role == "user":
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <b>You:</b> {content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #e1f5fe; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <b>AI Assistant:</b> {content}
            </div>
            """, unsafe_allow_html=True)

with chat_col2:
    # Generate and display suggestions if an analysis was performed
    if st.session_state.has_analysis:
        st.subheader("Suggested Questions")
        
        # Generate suggestions based on the analysis data
        suggestions = generate_analysis_suggestions({
            'genes': st.session_state.genes,
            'proteins': st.session_state.proteins,
            'resistance_data': st.session_state.resistance_data
        })
        
        # Display suggested questions
        for question in suggestions.get('questions', []):
            if st.button(question, key=f"suggest_{hash(question)}"):
                # Add question to chat history and get response
                response = chat_with_assistant(st.session_state.chat_history, question)
                
                # Update chat history
                st.session_state.chat_history = response["chat_history"]
                
                # Rerun to update UI
                st.rerun()
        
        # Display suggested research directions
        st.subheader("Research Directions")
        for direction in suggestions.get('research_directions', []):
            st.markdown(f"- {direction}")
    else:
        st.info("Analysis suggestions will appear here once you've analyzed a sequence.")

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