import json
import random
from typing import List, Dict, Any, Optional

def analyze_protein_resistance(protein_sequence: str, gene_name: str) -> List[Dict[str, Any]]:
    """
    Analyze a protein sequence for antimicrobial resistance markers.
    
    Args:
        protein_sequence: The protein sequence to analyze
        gene_name: The name of the gene this protein is from
        
    Returns:
        List of dictionaries containing resistance information
    """
    # In a real implementation, this would use a trained ML model and database comparison
    
    # Mapping of gene types to potential resistance information
    resistance_mapping = {
        'mecA': [
            {'antibiotic': 'Methicillin', 'resistance_level': 'high', 'mechanism': 'PBP2a production'},
            {'antibiotic': 'Oxacillin', 'resistance_level': 'high', 'mechanism': 'PBP2a production'},
            {'antibiotic': 'Dicloxacillin', 'resistance_level': 'high', 'mechanism': 'PBP2a production'},
        ],
        'vanA': [
            {'antibiotic': 'Vancomycin', 'resistance_level': 'high', 'mechanism': 'Cell wall target modification'},
            {'antibiotic': 'Teicoplanin', 'resistance_level': 'high', 'mechanism': 'Cell wall target modification'},
        ],
        'tetM': [
            {'antibiotic': 'Tetracycline', 'resistance_level': 'high', 'mechanism': 'Ribosomal protection'},
            {'antibiotic': 'Doxycycline', 'resistance_level': 'medium', 'mechanism': 'Ribosomal protection'},
            {'antibiotic': 'Minocycline', 'resistance_level': 'low', 'mechanism': 'Ribosomal protection'},
        ],
        'blaTEM': [
            {'antibiotic': 'Ampicillin', 'resistance_level': 'high', 'mechanism': 'Beta-lactamase production'},
            {'antibiotic': 'Penicillin', 'resistance_level': 'high', 'mechanism': 'Beta-lactamase production'},
            {'antibiotic': 'Cefazolin', 'resistance_level': 'medium', 'mechanism': 'Beta-lactamase production'},
        ],
        'aac': [
            {'antibiotic': 'Gentamicin', 'resistance_level': 'high', 'mechanism': 'Enzymatic modification'},
            {'antibiotic': 'Tobramycin', 'resistance_level': 'high', 'mechanism': 'Enzymatic modification'},
            {'antibiotic': 'Amikacin', 'resistance_level': 'medium', 'mechanism': 'Enzymatic modification'},
        ],
        'qnrS': [
            {'antibiotic': 'Ciprofloxacin', 'resistance_level': 'medium', 'mechanism': 'Target protection'},
            {'antibiotic': 'Levofloxacin', 'resistance_level': 'medium', 'mechanism': 'Target protection'},
            {'antibiotic': 'Moxifloxacin', 'resistance_level': 'low', 'mechanism': 'Target protection'},
        ],
    }
    
    # For novel genes, assign potential resistance based on sequence features
    if gene_name.startswith('novel_AMR_candidate'):
        # Look for specific protein motifs or features that might indicate resistance
        # This is a simplified implementation - in reality, would use sophisticated ML
        resistance_info = []
        
        # Simulate finding some resistance markers based on sequence characteristics
        if 'SXXK' in protein_sequence:  # Common motif in beta-lactamases
            resistance_info.append({
                'antibiotic': 'Ampicillin', 
                'resistance_level': 'medium', 
                'mechanism': 'Possible beta-lactamase activity',
                'confidence': round(random.uniform(0.60, 0.80), 2)
            })
        
        if 'HXXXD' in protein_sequence:  # Common motif in acetyltransferases
            resistance_info.append({
                'antibiotic': 'Gentamicin', 
                'resistance_level': 'medium', 
                'mechanism': 'Possible aminoglycoside modification',
                'confidence': round(random.uniform(0.60, 0.80), 2)
            })
            
        # Add a random potential resistance for novel genes to simulate discovery
        antibiotics = ['Ceftriaxone', 'Azithromycin', 'Meropenem', 'Colistin', 'Tigecycline']
        mechanisms = ['Efflux pump', 'Target modification', 'Enzymatic inactivation', 'Reduced permeability']
        
        resistance_info.append({
            'antibiotic': random.choice(antibiotics),
            'resistance_level': random.choice(['low', 'medium']),
            'mechanism': random.choice(mechanisms),
            'confidence': round(random.uniform(0.50, 0.70), 2)  # Lower confidence for novel genes
        })
        
        return resistance_info
    
    # For known genes, return the mapped resistance information
    if gene_name in resistance_mapping:
        result = resistance_mapping[gene_name]
        # Add confidence scores
        for item in result:
            item['confidence'] = round(random.uniform(0.85, 0.98), 2)
        return result
    
    # For unknown genes, return empty list
    return []

def get_antibiotic_recommendations(resistance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate antibiotic recommendations based on the resistance analysis.
    
    Args:
        resistance_data: List of dictionaries containing resistance information
        
    Returns:
        List of dictionaries with antibiotic recommendations
    """
    if not resistance_data:
        return []
    
    # Extract all antibiotics with resistance
    resistant_antibiotics = {item['antibiotic'].lower(): item['resistance_level'] for item in resistance_data}
    
    # Common antibiotics to consider (this would be a larger database in a real implementation)
    all_antibiotics = [
        "Ampicillin", "Penicillin", "Methicillin", "Oxacillin", "Dicloxacillin",
        "Cefazolin", "Ceftriaxone", "Ceftazidime", "Cefepime", "Meropenem",
        "Imipenem", "Aztreonam", "Vancomycin", "Teicoplanin", "Daptomycin",
        "Gentamicin", "Tobramycin", "Amikacin", "Tetracycline", "Doxycycline",
        "Minocycline", "Tigecycline", "Ciprofloxacin", "Levofloxacin", "Moxifloxacin", 
        "Azithromycin", "Erythromycin", "Clarithromycin", "Clindamycin", "Linezolid",
        "Chloramphenicol", "Colistin", "Polymyxin B", "Trimethoprim", "Sulfamethoxazole"
    ]
    
    recommendations = []
    
    # Evaluate each antibiotic
    for antibiotic in all_antibiotics:
        # Check if we have resistance data for this antibiotic
        if antibiotic.lower() in resistant_antibiotics:
            resistance_level = resistant_antibiotics[antibiotic.lower()]
            
            # Determine effectiveness based on resistance level
            effective = False
            if resistance_level == 'low':
                effective = random.random() > 0.3  # 70% chance still effective
                confidence = round(random.uniform(0.60, 0.80), 2)
                rationale = "Low-level resistance detected, may still be effective at higher doses"
            elif resistance_level == 'medium':
                effective = random.random() > 0.7  # 30% chance still effective
                confidence = round(random.uniform(0.70, 0.85), 2)
                rationale = "Moderate resistance detected, limited effectiveness likely"
            else:  # high
                effective = False
                confidence = round(random.uniform(0.85, 0.98), 2)
                rationale = "High-level resistance detected, unlikely to be effective"
        else:
            # No resistance data - likely effective
            effective = True
            confidence = round(random.uniform(0.75, 0.95), 2)
            rationale = "No resistance markers detected for this antibiotic"
        
        recommendations.append({
            'antibiotic': antibiotic,
            'effective': effective,
            'confidence': confidence,
            'rationale': rationale
        })
    
    # Sort by effectiveness and confidence
    return sorted(recommendations, key=lambda x: (-int(x['effective']), -x['confidence']))
