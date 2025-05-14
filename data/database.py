"""
Database module for GeneHack AMR - handles database connections and operations.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSON, JSONB

# Get database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Create SQLAlchemy engine and session
engine = sa.create_engine(DATABASE_URL if DATABASE_URL else "sqlite:///genehack.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class AnalysisResult(Base):
    """Model for storing analysis results."""
    __tablename__ = 'analysis_results'
    
    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    sequence_name = sa.Column(sa.String(255))
    sequence_type = sa.Column(sa.String(50))  # 'fasta' or 'raw'
    
    # Store detailed results as JSON
    genes = sa.Column(JSONB)
    proteins = sa.Column(JSONB)
    resistance_data = sa.Column(JSONB)
    recommendations = sa.Column(JSONB)
    summary_report = sa.Column(sa.Text)
    
    # Metrics
    num_genes = sa.Column(sa.Integer)
    num_resistance_markers = sa.Column(sa.Integer)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'sequence_name': self.sequence_name,
            'sequence_type': self.sequence_type,
            'num_genes': self.num_genes,
            'num_resistance_markers': self.num_resistance_markers,
            'genes': self.genes,
            'proteins': self.proteins,
            'resistance_data': self.resistance_data,
            'recommendations': self.recommendations,
            'summary_report': self.summary_report
        }

class SequenceData(Base):
    """Model for storing sequence data."""
    __tablename__ = 'sequence_data'
    
    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    name = sa.Column(sa.String(255))
    data_type = sa.Column(sa.String(50))  # 'fasta' or 'raw'
    sequence = sa.Column(sa.Text)
    description = sa.Column(sa.Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'name': self.name,
            'data_type': self.data_type,
            'sequence': self.sequence,
            'description': self.description
        }

def create_tables():
    """Create database tables."""
    Base.metadata.create_all(engine)

def save_analysis_result(
    sequence_name: str,
    sequence_type: str,
    genes: List[Dict[str, Any]],
    proteins: List[Dict[str, Any]],
    resistance_data: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]],
    summary_report: str
) -> int:
    """
    Save analysis results to the database.
    
    Args:
        sequence_name: Name of the sequence
        sequence_type: Type of sequence ('fasta' or 'raw')
        genes: List of gene dictionaries
        proteins: List of protein dictionaries
        resistance_data: List of resistance data dictionaries
        recommendations: List of recommendation dictionaries
        summary_report: Summary report text
        
    Returns:
        ID of the created record
    """
    session = Session()
    
    try:
        result = AnalysisResult(
            sequence_name=sequence_name,
            sequence_type=sequence_type,
            genes=genes,
            proteins=proteins,
            resistance_data=resistance_data,
            recommendations=recommendations,
            summary_report=summary_report,
            num_genes=len(genes),
            num_resistance_markers=len(resistance_data)
        )
        
        session.add(result)
        session.commit()
        # Get the id of the newly committed row
        result_id = result.id
        return result_id
    
    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        session.close()

def get_analysis_result(result_id: int) -> Optional[Dict[str, Any]]:
    """
    Get analysis result by ID.
    
    Args:
        result_id: ID of the analysis result
        
    Returns:
        Dictionary with the analysis result, or None if not found
    """
    session = Session()
    
    try:
        result = session.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
        return result.to_dict() if result else None
    
    finally:
        session.close()

def get_analysis_history(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get analysis history.
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of analysis result dictionaries
    """
    session = Session()
    
    try:
        results = session.query(AnalysisResult).order_by(
            AnalysisResult.created_at.desc()
        ).limit(limit).all()
        
        return [result.to_dict() for result in results]
    
    finally:
        session.close()

def save_sequence_data(
    name: str,
    data_type: str,
    sequence: str,
    description: Optional[str] = None
) -> int:
    """
    Save sequence data to the database.
    
    Args:
        name: Name of the sequence
        data_type: Type of data ('fasta' or 'raw')
        sequence: The sequence data
        description: Optional description
        
    Returns:
        ID of the created record
    """
    session = Session()
    
    try:
        data = SequenceData(
            name=name,
            data_type=data_type,
            sequence=sequence,
            description=description
        )
        
        session.add(data)
        session.commit()
        # Get the id of the newly committed row
        data_id = data.id
        return data_id
    
    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        session.close()

def get_sequence_data(data_id: int) -> Optional[Dict[str, Any]]:
    """
    Get sequence data by ID.
    
    Args:
        data_id: ID of the sequence data
        
    Returns:
        Dictionary with the sequence data, or None if not found
    """
    session = Session()
    
    try:
        data = session.query(SequenceData).filter(SequenceData.id == data_id).first()
        return data.to_dict() if data else None
    
    finally:
        session.close()

def get_stored_sequences(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get stored sequences.
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of sequence data dictionaries
    """
    session = Session()
    
    try:
        sequences = session.query(SequenceData).order_by(
            SequenceData.created_at.desc()
        ).limit(limit).all()
        
        return [sequence.to_dict() for sequence in sequences]
    
    finally:
        session.close()

# Create tables on module import
try:
    create_tables()
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {e}")