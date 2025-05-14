import os
import json
from typing import Dict, Any, List
from openai import OpenAI

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_summary_report(data: Dict[str, Any]) -> str:
    """
    Generate a summary report of the AMR analysis using OpenAI.
    
    Args:
        data: Dictionary containing genes, resistance, and recommendations information
        
    Returns:
        A formatted summary report string
    """
    try:
        # If no OpenAI API key is provided, generate a basic report
        if not OPENAI_API_KEY:
            return generate_basic_report(data)
        
        # Prepare the data for the prompt
        genes = data.get('genes', [])
        resistance = data.get('resistance', [])
        recommendations = data.get('recommendations', [])
        
        # Create a structured prompt
        prompt = f"""
        Please provide a concise summary report of antimicrobial resistance analysis results. Here's the data:

        GENES IDENTIFIED ({len(genes)}):
        {json.dumps(genes, indent=2)}

        RESISTANCE PROFILE ({len(resistance)}):
        {json.dumps(resistance, indent=2)}

        ANTIBIOTIC RECOMMENDATIONS:
        {json.dumps([r for r in recommendations if r.get('effective', False)][:5], indent=2)}

        Format the response as a professional clinical microbiology report with these sections:
        1. A brief overview of what was found
        2. Key resistance genes and their significance
        3. Resistance mechanisms identified
        4. Antibiotic susceptibility summary
        5. Treatment recommendations

        Keep the language technical but accessible to healthcare professionals.
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        
        # Extract the generated summary
        summary = response.choices[0].message.content.strip()
        
        return summary
    
    except Exception as e:
        # Fallback to basic report in case of API error
        return f"Error generating detailed report: {str(e)}\n\n" + generate_basic_report(data)

def generate_basic_report(data: Dict[str, Any]) -> str:
    """
    Generate a basic summary report without using OpenAI.
    Used as a fallback when API is unavailable.
    
    Args:
        data: Dictionary containing genes, resistance, and recommendations information
        
    Returns:
        A formatted summary report string
    """
    genes = data.get('genes', [])
    resistance = data.get('resistance', [])
    recommendations = data.get('recommendations', [])
    
    # Get effective antibiotics
    effective_antibiotics = [r['antibiotic'] for r in recommendations if r.get('effective', False)]
    
    # Get resistant antibiotics
    resistant_antibiotics = list(set([r['antibiotic'] for r in resistance]))
    
    # Generate basic report
    report = f"""
    ## Antimicrobial Resistance Analysis Summary

    ### Overview
    - **Total AMR genes identified:** {len(genes)}
    - **Resistance mechanisms detected:** {len(set([r.get('mechanism', 'Unknown') for r in resistance]))}
    - **Antibiotics with detected resistance:** {len(resistant_antibiotics)}
    
    ### Key Findings
    """
    
    if genes:
        report += "\n#### AMR Genes Detected\n"
        for gene in genes[:5]:  # Show top 5 genes
            report += f"- **{gene['name']}** (Confidence: {gene['confidence']})\n"
        if len(genes) > 5:
            report += f"- And {len(genes) - 5} more gene(s)\n"
    
    if resistance:
        report += "\n#### Resistance Profile\n"
        mechanisms = {}
        for r in resistance:
            mech = r.get('mechanism', 'Unknown')
            if mech not in mechanisms:
                mechanisms[mech] = []
            mechanisms[mech].append(r['antibiotic'])
        
        for mech, antibiotics in mechanisms.items():
            report += f"- **{mech}**: {', '.join(antibiotics[:3])}"
            if len(antibiotics) > 3:
                report += f" and {len(antibiotics) - 3} more"
            report += "\n"
    
    report += "\n### Treatment Recommendations\n"
    
    if effective_antibiotics:
        report += "#### Potentially Effective Antibiotics\n"
        report += ", ".join(effective_antibiotics[:7])
        if len(effective_antibiotics) > 7:
            report += f" and {len(effective_antibiotics) - 7} more"
        report += "\n"
    else:
        report += "No effective antibiotics identified based on the resistance profile. Consider consulting an infectious disease specialist.\n"
    
    if resistant_antibiotics:
        report += "\n#### Antibiotics with Detected Resistance\n"
        report += ", ".join(resistant_antibiotics[:7])
        if len(resistant_antibiotics) > 7:
            report += f" and {len(resistant_antibiotics) - 7} more"
    
    return report
