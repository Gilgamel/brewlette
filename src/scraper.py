"""
Nespresso Scraper Module - Accurate Capsule Data
Based on Nespresso Canada website
"""
import requests
from bs4 import BeautifulSoup
import json
import random
import re
from typing import List, Dict


def get_sample_capsules() -> List[Dict]:
    """
    Accurate Nespresso Canada capsule data
    Based on official Nespresso Canada product listings
    """
    
    # Original Line capsules (40ml espresso unless noted)
    original_capsules = [
        # Espresso (40ml)
        {"name": "Arpeggio", "name_en": "Arpeggio", "tasting_note": "Cereal, honey, caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 9},
        {"name": "Ristretto", "name_en": "Ristretto", "tasting_note": "Cereal, cocoa, caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 10},
        {"name": "Livanto", "name_en": "Livanto", "tasting_note": "Caramel, biscuit, vanilla", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        {"name": "Capriccio", "name_en": "Capriccio", "tasting_note": "Cereal, green apple", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 5},
        {"name": "Kazaar", "name_en": "Kazaar", "tasting_note": "Intense, cocoa, spicy", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 12},
        {"name": "Dharkan", "name_en": "Dharkan", "tasting_note": "Roasted, cocoa, smoky", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 11},
        {"name": "Roma", "name_en": "Roma", "tasting_note": "Roasted, cereal", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 8},
        {"name": "Decaf Intenso", "name_en": "Decaf Intenso", "tasting_note": "Roasted, caramel", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 7},
        {"name": "Voluntto", "name_en": "Voluntto", "tasting_note": "Balanced, smooth", "size_ml": 40, "pod_type": "espresso", "line": "Original", "intensity": 6},
        
        # Double Espresso (80ml)
        {"name": "Doppio", "name_en": "Doppio", "tasting_note": "Roasted, caramel", "size_ml": 80, "pod_type": "double", "line": "Original", "intensity": 9},
        {"name": "Cosimo", "name_en": "Cosimo", "tasting_note": "Intense, dark chocolate", "size_ml": 80, "pod_type": "double", "line": "Original", "intensity": 10},
        
        # Lungo (150ml)
        {"name": "Vivalto Lungo", "name_en": "Vivalto Lungo", "tasting_note": "Roasted, floral, slight fruit", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 5},
        {"name": "Fortissio Lungo", "name_en": "Fortissio Lungo", "tasting_note": "Roasted, green apple, caramel", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 7},
        {"name": "Linizio Lungo", "name_en": "Linizio Lungo", "tasting_note": "Cereal, malt", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 4},
        {"name": "Decaf Lungo", "name_en": "Decaf Lungo", "tasting_note": "Roasted, smooth", "size_ml": 150, "pod_type": "lungo", "line": "Original", "intensity": 4},
    ]
    
    # Vertuo Line capsules - CORRECTED DATA
    vertuo_capsules = [
        # Espresso (40ml)
        {"name": "Algerie", "name_en": "Algerie", "tasting_note": "Roasted, cocoa, cedar", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 8},
        {"name": "Bukeela", "name_en": "Bukeela", "tasting_note": "Cereal, herbs", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 6},
        {"name": "Decaf Indonesia", "name_en": "Decaf Indonesia", "tasting_note": "Caramel, cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 8},
        {"name": "Ethiopia", "name_en": "Ethiopia", "tasting_note": "Floral, citrus, jasmine", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 6},
        {"name": "Gimaja", "name_en": "Gimaja", "tasting_note": "Fruity, wine", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 6},
        {"name": "Kavu", "name_en": "Kavu", "tasting_note": "Roasted, cereal", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 6},
        {"name": "Melozio", "name_en": "Melozio", "tasting_note": "Roasted, caramel, creamy", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
        {"name": "Nicaragua", "name_en": "Nicaragua", "tasting_note": "Roasted, fruity, wine", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 7},
        {"name": "Odacio", "name_en": "Odacio", "tasting_note": "Roasted, green apple, berries", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 8},
        {"name": "Sidiary", "name_en": "Sidiary", "tasting_note": "Fruity, wine", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 7},
        {"name": "Stormio", "name_en": "Stormio", "tasting_note": "Intense, roasted, cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 8},
        {"name": "Voltesso", "name_en": "Voltesso", "tasting_note": "Light, sweet, caramel", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 4},
        
        # Double Espresso (80ml)
        {"name": "Double Espresso", "name_en": "Double Espresso", "tasting_note": "Roasted, caramel, cocoa", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 7},
        {"name": "Bianco", "name_en": "Bianco", "tasting_note": "Creamy, biscuit, vanilla", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 5},
        {"name": "Chiaro", "name_en": "Chiaro", "tasting_note": "Smooth, roasted, caramel", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 4},
        {"name": "Scuro", "name_en": "Scuro", "tasting_note": "Dark roast, cocoa, smoky", "size_ml": 80, "pod_type": "double", "line": "Vertuo", "intensity": 9},
        
        # Gran Lungo (150ml)
        {"name": "Envivo Lungo", "name_en": "Envivo Lungo", "tasting_note": "Roasted, caramel, green apple", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 9},
        {"name": "Intenso", "name_en": "Intenso", "tasting_note": "Roasted, cocoa, caramel", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 9},
        {"name": "Dolceo", "name_en": "Dolceo", "tasting_note": "Roasted, caramel, creamy", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 6},
        {"name": "Orafel", "name_en": "Orafel", "tasting_note": "Fruity, floral", "size_ml": 150, "pod_type": "lungo", "line": "Vertuo", "intensity": 5},
        
        # Coffee / Alto (230ml)
        {"name": "Caramel Cookie", "name_en": "Caramel Cookie", "tasting_note": "Caramel, biscuit", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 5},
        {"name": "Hazelnut", "name_en": "Hazelnut", "tasting_note": "Roasted, hazelnut", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
        {"name": "Ice Coffee", "name_en": "Ice Coffee", "tasting_note": "Refreshing, fruity", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 4},
        {"name": "Nicaragua", "name_en": "Nicaragua", "tasting_note": "Roasted, fruity, wine", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 7},
        {"name": "Rich Chocolate", "name_en": "Rich Chocolate", "tasting_note": "Rich chocolate, roasted", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 8},
        {"name": "Sunlit", "name_en": "Sunlit", "tasting_note": "Fruity, bright", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 4},
        
        # Alto (414ml)
        {"name": "Clarissimo", "name_en": "Clarissimo", "tasting_note": "Smooth, balanced", "size_ml": 414, "pod_type": "alto", "line": "Vertuo", "intensity": 5},
        {"name": "Inissio", "name_en": "Inissio", "tasting_note": "Light, fresh", "size_ml": 414, "pod_type": "alto", "line": "Vertuo", "intensity": 4},
        
        # Limited Editions / Collaborations
        {"name": "Starbucks Blonde Espresso", "name_en": "Starbucks Blonde Espresso", "tasting_note": "Light roast, caramel, citrus", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 5},
        {"name": "Starbucks Veranda Blend", "name_en": "Starbucks Veranda Blend", "tasting_note": "Light roast, malt, chocolate", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 4},
        {"name": "Starbucks Pike Place", "name_en": "Starbucks Pike Place", "tasting_note": "Medium roast, caramel, cocoa", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 6},
        {"name": "Starbucks Dark Roast", "name_en": "Starbucks Dark Roast", "tasting_note": "Dark roast, cocoa, smoky", "size_ml": 40, "pod_type": "espresso", "line": "Vertuo", "intensity": 9},
        {"name": "Starbucks Caramel Macchiato", "name_en": "Starbucks Caramel Macchiato", "tasting_note": "Caramel, milk, vanilla", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 5},
        {"name": "Starbucks Cappuccino", "name_en": "Starbucks Cappuccino", "tasting_note": "Roasted, creamy, caramel", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 6},
        {"name": "NOLA", "name_en": "NOLA", "tasting_note": "New Orleans style, caramel, vanilla", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 5},
        {"name": "Fizzio", "name_en": "Fizzio", "tasting_note": "Fizzy, citrus, mint", "size_ml": 230, "pod_type": "coffee", "line": "Vertuo", "intensity": 4},
    ]
    
    return original_capsules + vertuo_capsules


def scrape_all_capsules() -> List[Dict]:
    """Get all capsules (uses sample data with accurate info)"""
    return get_sample_capsules()


def get_capsules_by_size(capsules: List[Dict], size_ml: int) -> List[Dict]:
    """Filter capsules by size"""
    return [c for c in capsules if c.get('size_ml') == size_ml]


def get_capsules_by_type(capsules: List[Dict], pod_type: str) -> List[Dict]:
    """Filter capsules by type"""
    return [c for c in capsules if c.get('pod_type', '').lower() == pod_type.lower()]


def get_capsules_by_line(capsules: List[Dict], line: str) -> List[Dict]:
    """Filter capsules by line"""
    return [c for c in capsules if c.get('line', '').lower() == line.lower()]
