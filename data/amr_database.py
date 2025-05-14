"""
This module provides a simulated database of antimicrobial resistance (AMR) genes,
resistance mechanisms, and antibiotic effectiveness.

In a production environment, this would connect to a real database or API of
AMR data such as CARD (Comprehensive Antibiotic Resistance Database),
ResFinder, or NCBI's AMR database.
"""

# List of common AMR genes and their associated information
AMR_GENES = {
    'mecA': {
        'full_name': 'Methicillin resistance gene A',
        'description': 'Confers resistance to beta-lactam antibiotics including methicillin and other penicillins',
        'mechanism': 'Produces altered penicillin-binding protein (PBP2a) with low affinity for beta-lactams',
        'prevalence': 'Common in MRSA (Methicillin-resistant Staphylococcus aureus)',
        'antibiotics_affected': ['methicillin', 'oxacillin', 'nafcillin', 'dicloxacillin', 'cefazolin']
    },
    'vanA': {
        'full_name': 'Vancomycin resistance gene A',
        'description': 'Confers high-level resistance to vancomycin and teicoplanin',
        'mechanism': 'Modifies the D-Ala-D-Ala terminus of peptidoglycan to D-Ala-D-Lac, reducing vancomycin binding',
        'prevalence': 'Found in VRE (Vancomycin-resistant Enterococcus)',
        'antibiotics_affected': ['vancomycin', 'teicoplanin']
    },
    'tetM': {
        'full_name': 'Tetracycline resistance gene M',
        'description': 'Provides ribosomal protection against tetracyclines',
        'mechanism': 'Produces a protein that prevents tetracycline from binding to the ribosome',
        'prevalence': 'Widely distributed in gram-positive and gram-negative bacteria',
        'antibiotics_affected': ['tetracycline', 'doxycycline', 'minocycline']
    },
    'blaTEM': {
        'full_name': 'Beta-lactamase TEM',
        'description': 'Hydrolyzes the beta-lactam ring of many penicillins and some early cephalosporins',
        'mechanism': 'Enzymatic inactivation of beta-lactam antibiotics',
        'prevalence': 'One of the most common beta-lactamases in gram-negative bacteria',
        'antibiotics_affected': ['ampicillin', 'penicillin', 'amoxicillin', 'cefazolin']
    },
    'blaCTX-M': {
        'full_name': 'Beta-lactamase CTX-M',
        'description': 'Extended-spectrum beta-lactamase with increased activity against cefotaxime',
        'mechanism': 'Enzymatic inactivation of extended-spectrum beta-lactam antibiotics',
        'prevalence': 'Increasingly common in Enterobacteriaceae',
        'antibiotics_affected': ['cefotaxime', 'ceftriaxone', 'ceftazidime', 'aztreonam']
    },
    'blaKPC': {
        'full_name': 'Klebsiella pneumoniae carbapenemase',
        'description': 'Carbapenemase that hydrolyzes a broad range of beta-lactams including carbapenems',
        'mechanism': 'Enzymatic inactivation of all beta-lactam antibiotics including carbapenems',
        'prevalence': 'Increasing globally, especially in Klebsiella and other Enterobacteriaceae',
        'antibiotics_affected': ['ertapenem', 'imipenem', 'meropenem', 'doripenem', 'all penicillins and cephalosporins']
    },
    'blaNDM': {
        'full_name': 'New Delhi metallo-beta-lactamase',
        'description': 'Metallo-beta-lactamase that confers resistance to almost all beta-lactams',
        'mechanism': 'Zinc-dependent hydrolysis of the beta-lactam ring',
        'prevalence': 'Emerging global threat, especially in Enterobacteriaceae',
        'antibiotics_affected': ['all beta-lactams except aztreonam']
    },
    'qnrA': {
        'full_name': 'Quinolone resistance gene A',
        'description': 'Protects DNA gyrase from quinolone inhibition',
        'mechanism': 'Protein binding that prevents quinolones from interacting with target enzymes',
        'prevalence': 'Increasingly common in Enterobacteriaceae',
        'antibiotics_affected': ['ciprofloxacin', 'levofloxacin', 'moxifloxacin', 'norfloxacin']
    },
    'aac(6\')-Ib-cr': {
        'full_name': 'Aminoglycoside acetyltransferase Ib-cr variant',
        'description': 'Modified aminoglycoside acetyltransferase that also affects fluoroquinolones',
        'mechanism': 'Acetylation of aminoglycosides and some fluoroquinolones',
        'prevalence': 'Increasingly common in Enterobacteriaceae',
        'antibiotics_affected': ['kanamycin', 'tobramycin', 'ciprofloxacin', 'norfloxacin']
    },
    'ermB': {
        'full_name': 'Erythromycin ribosome methylase B',
        'description': 'Methylates 23S rRNA, reducing binding of macrolides, lincosamides, and streptogramins',
        'mechanism': 'Target modification of bacterial ribosome',
        'prevalence': 'Common in gram-positive bacteria',
        'antibiotics_affected': ['erythromycin', 'clarithromycin', 'azithromycin', 'clindamycin']
    }
}

# Common antimicrobial resistance mechanisms
RESISTANCE_MECHANISMS = [
    {
        'name': 'Enzymatic inactivation',
        'description': 'Production of enzymes that modify or destroy the antibiotic molecule',
        'examples': ['Beta-lactamases', 'Aminoglycoside-modifying enzymes', 'Chloramphenicol acetyltransferases']
    },
    {
        'name': 'Target modification',
        'description': 'Alteration of the antibiotic target site to reduce binding affinity',
        'examples': ['PBP modifications', 'Ribosomal methylation', 'DNA gyrase mutations']
    },
    {
        'name': 'Reduced permeability',
        'description': 'Decreased antibiotic entry into the bacterial cell',
        'examples': ['Porin mutations', 'Altered membrane composition', 'Biofilm formation']
    },
    {
        'name': 'Efflux pumps',
        'description': 'Active export of antibiotics from the bacterial cell',
        'examples': ['RND family pumps', 'MFS transporters', 'ABC transporters']
    },
    {
        'name': 'Target protection',
        'description': 'Production of proteins that shield the target from antibiotic binding',
        'examples': ['Tet(M)', 'Qnr proteins', 'Ribosomal protection proteins']
    },
    {
        'name': 'Target overproduction',
        'description': 'Increased production of the antibiotic target',
        'examples': ['DHPS overexpression', 'DHFR overexpression']
    },
    {
        'name': 'Bypass pathway',
        'description': 'Use of alternative metabolic pathways to circumvent antibiotic action',
        'examples': ['Alternative PBPs', 'Alternative folate synthesis']
    }
]

# List of antibiotic classes and examples
ANTIBIOTIC_CLASSES = [
    {
        'class': 'Penicillins',
        'mechanism': 'Cell wall synthesis inhibition',
        'examples': ['Penicillin G', 'Ampicillin', 'Amoxicillin', 'Nafcillin', 'Oxacillin', 'Dicloxacillin']
    },
    {
        'class': 'Cephalosporins',
        'mechanism': 'Cell wall synthesis inhibition',
        'examples': ['Cefazolin', 'Cefuroxime', 'Ceftriaxone', 'Cefotaxime', 'Ceftazidime', 'Cefepime']
    },
    {
        'class': 'Carbapenems',
        'mechanism': 'Cell wall synthesis inhibition',
        'examples': ['Imipenem', 'Meropenem', 'Ertapenem', 'Doripenem']
    },
    {
        'class': 'Monobactams',
        'mechanism': 'Cell wall synthesis inhibition',
        'examples': ['Aztreonam']
    },
    {
        'class': 'Glycopeptides',
        'mechanism': 'Cell wall synthesis inhibition',
        'examples': ['Vancomycin', 'Teicoplanin']
    },
    {
        'class': 'Lipopeptides',
        'mechanism': 'Cell membrane disruption',
        'examples': ['Daptomycin', 'Polymyxin B', 'Colistin']
    },
    {
        'class': 'Aminoglycosides',
        'mechanism': 'Protein synthesis inhibition (30S)',
        'examples': ['Gentamicin', 'Tobramycin', 'Amikacin', 'Streptomycin']
    },
    {
        'class': 'Tetracyclines',
        'mechanism': 'Protein synthesis inhibition (30S)',
        'examples': ['Tetracycline', 'Doxycycline', 'Minocycline', 'Tigecycline']
    },
    {
        'class': 'Macrolides',
        'mechanism': 'Protein synthesis inhibition (50S)',
        'examples': ['Erythromycin', 'Clarithromycin', 'Azithromycin']
    },
    {
        'class': 'Lincosamides',
        'mechanism': 'Protein synthesis inhibition (50S)',
        'examples': ['Clindamycin', 'Lincomycin']
    },
    {
        'class': 'Streptogramins',
        'mechanism': 'Protein synthesis inhibition (50S)',
        'examples': ['Quinupristin/Dalfopristin']
    },
    {
        'class': 'Phenicols',
        'mechanism': 'Protein synthesis inhibition (50S)',
        'examples': ['Chloramphenicol']
    },
    {
        'class': 'Oxazolidinones',
        'mechanism': 'Protein synthesis inhibition (50S)',
        'examples': ['Linezolid', 'Tedizolid']
    },
    {
        'class': 'Fluoroquinolones',
        'mechanism': 'DNA replication inhibition',
        'examples': ['Ciprofloxacin', 'Levofloxacin', 'Moxifloxacin', 'Ofloxacin']
    },
    {
        'class': 'Folate pathway inhibitors',
        'mechanism': 'Nucleic acid synthesis inhibition',
        'examples': ['Trimethoprim', 'Sulfamethoxazole', 'Trimethoprim-Sulfamethoxazole']
    }
]
