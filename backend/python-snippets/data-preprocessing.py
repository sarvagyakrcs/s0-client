import pandas as pd
from sqlalchemy import create_engine, text
from bs4 import BeautifulSoup
import re
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = "postgresql://neondb_owner:npg_LkgS8BGKhw9c@ep-morning-shadow-a17ijyhw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)

def clean_html(code: str) -> str:
    """Clean and format HTML code."""
    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(code, 'html.parser')
        # Pretty print with consistent formatting
        cleaned = soup.prettify()
        # Remove excessive blank lines
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        return cleaned.strip()
    except Exception as e:
        print(f"Error cleaning HTML: {e}")
        return code

def extract_component_features(code: str) -> Dict[str, any]:
    """Extract relevant features from component code."""
    soup = BeautifulSoup(code, 'html.parser')
    
    return {
        'element_count': len(soup.find_all()),
        'has_form': len(soup.find_all('form')) > 0,
        'has_button': len(soup.find_all('button')) > 0,
        'has_input': len(soup.find_all('input')) > 0,
        'has_image': len(soup.find_all('img')) > 0,
        'classes_used': len(set([cls for tag in soup.find_all() for cls in tag.get('class', [])]))
    }

def analyze_components():
    """Analyze and preprocess components in the database."""
    
    # Get all components
    query = """
    SELECT id, title, summary, code_snippet 
    FROM code_components 
    ORDER BY id;
    """
    
    df = pd.read_sql(query, engine)
    print(f"Loaded {len(df)} components")
    
    # Initialize feature columns
    feature_columns = ['element_count', 'has_form', 'has_button', 'has_input', 'has_image', 'classes_used']
    for col in feature_columns:
        df[col] = 0
    
    # Process each component
    for idx, row in df.iterrows():
        print(f"\nProcessing component {idx + 1}/{len(df)}")
        
        try:
            # Clean code
            cleaned_code = clean_html(row['code_snippet'])
            
            # Extract features
            features = extract_component_features(cleaned_code)
            
            # Update dataframe
            for feature, value in features.items():
                df.at[idx, feature] = value
            
            # Update database with cleaned code
            with engine.connect() as conn:
                update_query = text("""
                    UPDATE code_components 
                    SET code_snippet = :code,
                        element_count = :element_count,
                        has_form = :has_form,
                        has_button = :has_button,
                        has_input = :has_input,
                        has_image = :has_image,
                        classes_used = :classes_used
                    WHERE id = :id
                """)
                
                conn.execute(update_query, {
                    'code': cleaned_code,
                    'id': row['id'],
                    **features
                })
                conn.commit()
                
        except Exception as e:
            print(f"Error processing component {row['id']}: {e}")
            continue
    
    # Generate statistics
    print("\nComponent Statistics:")
    print("-" * 50)
    print(f"Total components: {len(df)}")
    print("\nFeature Statistics:")
    for feature in feature_columns:
        if feature == 'element_count' or feature == 'classes_used':
            print(f"\n{feature}:")
            print(f"  Mean: {df[feature].mean():.2f}")
            print(f"  Median: {df[feature].median():.2f}")
            print(f"  Max: {df[feature].max()}")
        else:
            count = df[df[feature] == True].shape[0]
            percentage = (count / len(df)) * 100
            print(f"\n{feature}:")
            print(f"  Count: {count}")
            print(f"  Percentage: {percentage:.2f}%")
    
    # Add new columns to database
    with engine.connect() as conn:
        for feature in feature_columns:
            try:
                conn.execute(text(f"ALTER TABLE code_components ADD COLUMN IF NOT EXISTS {feature} INTEGER DEFAULT 0"))
                conn.commit()
            except Exception as e:
                print(f"Column {feature} might already exist: {e}")
                continue

def analyze_html_structure(code_snippet):
    """Analyze HTML structure and return tag statistics"""
    soup = BeautifulSoup(code_snippet, 'html.parser')
    tags = [tag.name for tag in soup.find_all()]
    classes = [cls for tag in soup.find_all() for cls in tag.get('class', [])]
    depth = max([len(list(tag.parents)) for tag in soup.find_all()])
    return tags, classes, depth

def explore_dataset():
    """Explore and analyze the dataset."""
    print("Starting data exploration...")
    
    # Query only existing columns
    query = """
    SELECT id, title, summary, code_snippet
    FROM code_components
    """
    
    try:
        # Load data into DataFrame
        df = pd.read_sql(query, engine)
        print(f"\nTotal components: {len(df)}")
        
        # Add analysis columns
        df['element_count'] = df['code_snippet'].apply(lambda x: len(BeautifulSoup(x, 'html.parser').find_all()))
        df['has_form'] = df['code_snippet'].apply(lambda x: 1 if 'form' in x.lower() else 0)
        df['has_button'] = df['code_snippet'].apply(lambda x: 1 if 'button' in x.lower() else 0)
        df['has_input'] = df['code_snippet'].apply(lambda x: 1 if 'input' in x.lower() else 0)
        df['has_image'] = df['code_snippet'].apply(lambda x: 1 if 'img' in x.lower() else 0)
        
        # Extract classes
        def extract_classes(html):
            soup = BeautifulSoup(html, 'html.parser')
            classes = []
            for tag in soup.find_all(True):
                if 'class' in tag.attrs:
                    classes.extend(tag['class'])
            return list(set(classes))
            
        df['classes_used'] = df['code_snippet'].apply(extract_classes)
        
        # Print summary statistics
        print("\nComponent Analysis:")
        print(f"Average elements per component: {df['element_count'].mean():.2f}")
        print(f"Components with forms: {df['has_form'].sum()}")
        print(f"Components with buttons: {df['has_button'].sum()}")
        print(f"Components with inputs: {df['has_input'].sum()}")
        print(f"Components with images: {df['has_image'].sum()}")
        
        # Most common classes
        all_classes = [cls for classes in df['classes_used'] for cls in classes]
        class_counts = pd.Series(all_classes).value_counts()
        print("\nTop 10 most used classes:")
        print(class_counts.head(10))
        
        # Save analysis results
        output_dir = 'analysis_results'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save summary to CSV
        summary_df = pd.DataFrame({
            'Metric': ['Total Components', 'Avg Elements', 'Has Form', 'Has Button', 'Has Input', 'Has Image'],
            'Value': [
                len(df),
                df['element_count'].mean(),
                df['has_form'].sum(),
                df['has_button'].sum(),
                df['has_input'].sum(),
                df['has_image'].sum()
            ]
        })
        summary_df.to_csv(f'{output_dir}/summary_stats.csv', index=False)
        
        # Save class usage to CSV
        class_counts.head(50).to_csv(f'{output_dir}/top_classes.csv')
        
        print(f"\nAnalysis results saved to {output_dir}/")
        
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    explore_dataset()
