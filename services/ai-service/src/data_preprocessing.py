"""
Data preprocessing for LSTM training
Converts user behavior sequences into training samples
"""
import pandas as pd
import numpy as np
from collections import defaultdict
from typing import List, Tuple, Dict
import pickle

class DataPreprocessor:
    """Preprocess user behavior data for LSTM training"""
    
    def __init__(self, csv_path: str):
        """
        Initialize preprocessor
        
        Args:
            csv_path: Path to user_behavior.csv
        """
        self.csv_path = csv_path
        self.df = None
        self.user_sequences = {}
        self.product_to_idx = {}
        self.idx_to_product = {}
        self.num_products = 0
        
    def load_data(self):
        """Load CSV data"""
        print("📂 Loading data from CSV...")
        self.df = pd.read_csv(self.csv_path)
        print(f"   Loaded {len(self.df)} records")
        print(f"   Columns: {list(self.df.columns)}")
        return self.df
    
    def create_product_mapping(self):
        """Create product_id to index mapping"""
        print("\n🔢 Creating product mapping...")
        unique_products = sorted(self.df['product_id'].unique())
        
        # Create bidirectional mapping
        # Index 0 is reserved for padding
        self.product_to_idx = {pid: idx + 1 for idx, pid in enumerate(unique_products)}
        self.idx_to_product = {idx + 1: pid for idx, pid in enumerate(unique_products)}
        self.idx_to_product[0] = 0  # Padding
        
        self.num_products = len(unique_products) + 1  # +1 for padding
        
        print(f"   Total unique products: {len(unique_products)}")
        print(f"   Vocabulary size (with padding): {self.num_products}")
        
        return self.product_to_idx, self.idx_to_product
    
    def group_by_user(self) -> Dict[int, List[int]]:
        """
        Group interactions by user and create sequences
        
        Returns:
            Dictionary mapping user_id to list of product indices
        """
        print("\n👥 Grouping by user...")
        
        # Sort by user_id and timestamp
        self.df = self.df.sort_values(['user_id', 'timestamp'])
        
        # Group by user
        for user_id, group in self.df.groupby('user_id'):
            # Convert product_ids to indices
            product_sequence = [
                self.product_to_idx[pid] 
                for pid in group['product_id'].tolist()
            ]
            self.user_sequences[user_id] = product_sequence
        
        print(f"   Total users: {len(self.user_sequences)}")
        
        # Print sample
        sample_user = list(self.user_sequences.keys())[0]
        sample_seq = self.user_sequences[sample_user]
        print(f"   Sample user {sample_user}: {sample_seq[:10]}... (length: {len(sample_seq)})")
        
        return self.user_sequences
    
    def create_training_samples(
        self, 
        min_seq_length: int = 3,
        max_seq_length: int = 20
    ) -> Tuple[List[List[int]], List[int]]:
        """
        Create training samples from user sequences
        
        For each user sequence [p1, p2, p3, p4, p5]:
        - Input: [p1, p2, p3, p4], Output: p5
        - Input: [p1, p2, p3], Output: p4
        - etc.
        
        Args:
            min_seq_length: Minimum sequence length to consider
            max_seq_length: Maximum input sequence length
            
        Returns:
            X: List of input sequences
            y: List of target products
        """
        print(f"\n🎯 Creating training samples...")
        print(f"   Min sequence length: {min_seq_length}")
        print(f"   Max sequence length: {max_seq_length}")
        
        X = []  # Input sequences
        y = []  # Target products
        
        for user_id, sequence in self.user_sequences.items():
            seq_len = len(sequence)
            
            # Skip if sequence too short
            if seq_len < min_seq_length:
                continue
            
            # Create multiple samples from one sequence
            for i in range(min_seq_length - 1, seq_len):
                # Input: sequence up to position i
                input_seq = sequence[max(0, i - max_seq_length):i]
                
                # Output: next product
                target = sequence[i]
                
                X.append(input_seq)
                y.append(target)
        
        print(f"   Created {len(X)} training samples")
        print(f"   Sample input: {X[0]}")
        print(f"   Sample target: {y[0]}")
        
        return X, y
    
    def pad_sequences(
        self, 
        sequences: List[List[int]], 
        max_length: int = 20,
        padding_value: int = 0
    ) -> np.ndarray:
        """
        Pad sequences to same length
        
        Args:
            sequences: List of sequences
            max_length: Maximum sequence length
            padding_value: Value to use for padding
            
        Returns:
            Padded numpy array
        """
        print(f"\n📏 Padding sequences to length {max_length}...")
        
        padded = np.full((len(sequences), max_length), padding_value, dtype=np.int32)
        
        for i, seq in enumerate(sequences):
            seq_len = min(len(seq), max_length)
            padded[i, -seq_len:] = seq[-seq_len:]  # Right-align
        
        print(f"   Padded shape: {padded.shape}")
        
        return padded
    
    def save_mappings(self, output_path: str = 'data/mappings.pkl'):
        """Save product mappings for later use"""
        mappings = {
            'product_to_idx': self.product_to_idx,
            'idx_to_product': self.idx_to_product,
            'num_products': self.num_products
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(mappings, f)
        
        print(f"\n💾 Saved mappings to {output_path}")
    
    def get_statistics(self):
        """Print dataset statistics"""
        print("\n📊 Dataset Statistics:")
        print(f"   Total records: {len(self.df)}")
        print(f"   Unique users: {self.df['user_id'].nunique()}")
        print(f"   Unique products: {self.df['product_id'].nunique()}")
        print(f"   Date range: {self.df['timestamp'].min()} to {self.df['timestamp'].max()}")
        
        print("\n   Action distribution:")
        action_counts = self.df['action'].value_counts()
        for action, count in action_counts.items():
            print(f"      {action}: {count} ({count/len(self.df)*100:.1f}%)")
        
        print("\n   Sequence length distribution:")
        seq_lengths = [len(seq) for seq in self.user_sequences.values()]
        print(f"      Min: {min(seq_lengths)}")
        print(f"      Max: {max(seq_lengths)}")
        print(f"      Mean: {np.mean(seq_lengths):.1f}")
        print(f"      Median: {np.median(seq_lengths):.1f}")


def preprocess_pipeline(csv_path: str = 'data/user_behavior.csv'):
    """
    Complete preprocessing pipeline
    
    Args:
        csv_path: Path to user behavior CSV
        
    Returns:
        X_padded: Padded input sequences
        y: Target products
        preprocessor: DataPreprocessor instance
    """
    print("=" * 60)
    print("🚀 Starting Data Preprocessing Pipeline")
    print("=" * 60)
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor(csv_path)
    
    # Step 1: Load data
    preprocessor.load_data()
    
    # Step 2: Create product mapping
    preprocessor.create_product_mapping()
    
    # Step 3: Group by user
    preprocessor.group_by_user()
    
    # Step 4: Create training samples
    X, y = preprocessor.create_training_samples(
        min_seq_length=3,
        max_seq_length=20
    )
    
    # Step 5: Pad sequences
    X_padded = preprocessor.pad_sequences(X, max_length=20)
    y_array = np.array(y, dtype=np.int32)
    
    # Step 6: Save mappings
    preprocessor.save_mappings()
    
    # Step 7: Statistics
    preprocessor.get_statistics()
    
    print("\n" + "=" * 60)
    print("✅ Preprocessing Complete!")
    print("=" * 60)
    print(f"   Training samples: {len(X_padded)}")
    print(f"   Input shape: {X_padded.shape}")
    print(f"   Output shape: {y_array.shape}")
    print(f"   Vocabulary size: {preprocessor.num_products}")
    
    return X_padded, y_array, preprocessor


if __name__ == '__main__':
    # Run preprocessing
    X, y, preprocessor = preprocess_pipeline()
    
    # Save processed data
    np.save('data/X_train.npy', X)
    np.save('data/y_train.npy', y)
    print("\n💾 Saved training data to data/X_train.npy and data/y_train.npy")
