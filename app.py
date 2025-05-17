    
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
