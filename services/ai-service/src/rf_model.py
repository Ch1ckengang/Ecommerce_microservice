"""
Random Forest Classifier for Purchase Prediction
Feature-based recommendation using ensemble learning
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
from typing import List, Tuple, Dict

class RandomForestRecommender:
    """
    Random Forest model for predicting purchase probability
    based on rich feature set
    """
    
    def __init__(self, n_estimators=100, max_depth=10, random_state=42):
        """
        Args:
            n_estimators: Number of trees
            max_depth: Maximum depth of trees
            random_state: Random seed
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.category_encoder = LabelEncoder()
        self.brand_encoder = LabelEncoder()
        
    def _engineer_features(self, 
                          user_behavior_df: pd.DataFrame,
                          product_features_df: pd.DataFrame,
                          interactions_df: pd.DataFrame,
                          category_trends_df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features from multiple data sources
        
        Returns:
            DataFrame with engineered features
        """
        print("🔧 Engineering features...")
        
        # Merge datasets
        # 1. User behavior + Product features (on product_id only, category exists in behavior)
        df = user_behavior_df.merge(
            product_features_df[['product_id', 'brand', 'stock', 'rating', 'num_reviews', 
                                'discount', 'is_new', 'popularity_score']],
            on='product_id',
            how='left'
        )
        
        # 2. Add interaction statistics
        if interactions_df is not None and len(interactions_df) > 0:
            # Aggregate interactions per user-product
            interaction_stats = interactions_df.groupby(['user_id', 'product_id']).agg({
                'duration_seconds': 'sum',
                'interaction_type': 'count'
            }).reset_index()
            interaction_stats.columns = ['user_id', 'product_id', 'total_duration', 'num_interactions']
            
            df = df.merge(
                interaction_stats,
                on=['user_id', 'product_id'],
                how='left'
            )
            df['total_duration'] = df['total_duration'].fillna(0)
            df['num_interactions'] = df['num_interactions'].fillna(0)
        else:
            df['total_duration'] = 0
            df['num_interactions'] = 0
        
        # 3. Add category trends
        if category_trends_df is not None and len(category_trends_df) > 0:
            # Use latest trends
            latest_trends = category_trends_df.sort_values('date').groupby('category').last().reset_index()
            latest_trends = latest_trends[['category', 'trending_score', 'view_count', 'purchase_count']]
            
            df = df.merge(
                latest_trends,
                left_on='category',
                right_on='category',
                how='left'
            )
            df['trending_score'] = df['trending_score'].fillna(0.5)
            df['category_view_count'] = df['view_count'].fillna(0)
            df['category_purchase_count'] = df['purchase_count'].fillna(0)
        else:
            df['trending_score'] = 0.5
            df['category_view_count'] = 0
            df['category_purchase_count'] = 0
        
        # 4. User-level features
        user_stats = user_behavior_df.groupby('user_id').agg({
            'action': 'count',
            'product_id': 'nunique',
            'price': 'mean'
        }).reset_index()
        user_stats.columns = ['user_id', 'user_total_actions', 'user_unique_products', 'user_avg_price']
        
        df = df.merge(user_stats, on='user_id', how='left')
        
        # 5. Product-level features
        product_stats = user_behavior_df.groupby('product_id').agg({
            'user_id': 'nunique',
            'action': 'count'
        }).reset_index()
        product_stats.columns = ['product_id', 'product_unique_users', 'product_total_views']
        
        df = df.merge(product_stats, on='product_id', how='left')
        
        # 6. Temporal features
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        else:
            df['hour'] = 12
            df['day_of_week'] = 1
            df['is_weekend'] = 0
        
        # 7. Derived features
        df['price_relative_to_user'] = df['price'] / (df['user_avg_price'] + 1)
        df['conversion_rate'] = df['category_purchase_count'] / (df['category_view_count'] + 1)
        df['engagement_score'] = df['total_duration'] * df['num_interactions']
        
        print(f"   ✅ Features engineered: {len(df)} samples")
        return df
    
    def _select_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Select and encode features for training
        
        Returns:
            X (features), y (target)
        """
        # Define feature columns
        numeric_features = [
            'price', 'stock', 'rating', 'num_reviews', 'discount',
            'is_new', 'popularity_score',
            'total_duration', 'num_interactions',
            'trending_score', 'category_view_count', 'category_purchase_count',
            'user_total_actions', 'user_unique_products', 'user_avg_price',
            'product_unique_users', 'product_total_views',
            'hour', 'day_of_week', 'is_weekend',
            'price_relative_to_user', 'conversion_rate', 'engagement_score'
        ]
        
        categorical_features = ['category', 'brand']
        
        # Fill missing values
        for col in numeric_features:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        for col in categorical_features:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown')
        
        # Encode categorical features
        if 'category' in df.columns:
            df['category_encoded'] = self.category_encoder.fit_transform(df['category'])
        if 'brand' in df.columns:
            df['brand_encoded'] = self.brand_encoder.fit_transform(df['brand'])
        
        # Select features
        feature_cols = [col for col in numeric_features if col in df.columns]
        if 'category_encoded' in df.columns:
            feature_cols.append('category_encoded')
        if 'brand_encoded' in df.columns:
            feature_cols.append('brand_encoded')
        
        self.feature_names = feature_cols
        X = df[feature_cols]
        
        # Create target: 1 if purchased, 0 otherwise
        y = (df['action'] == 'purchase').astype(int)
        
        return X, y
    
    def train(self,
              user_behavior_df: pd.DataFrame,
              product_features_df: pd.DataFrame,
              interactions_df: pd.DataFrame = None,
              category_trends_df: pd.DataFrame = None):
        """
        Train Random Forest model
        
        Args:
            user_behavior_df: User behavior data
            product_features_df: Product features
            interactions_df: Product interactions (optional)
            category_trends_df: Category trends (optional)
        """
        print(f"🤖 Training Random Forest Recommender...")
        print(f"   n_estimators: {self.model.n_estimators}")
        print(f"   max_depth: {self.model.max_depth}")
        
        # Engineer features
        df = self._engineer_features(
            user_behavior_df,
            product_features_df,
            interactions_df,
            category_trends_df
        )
        
        # Select features and target
        X, y = self._select_features(df)
        
        print(f"   Features: {len(self.feature_names)}")
        print(f"   Samples: {len(X)}")
        print(f"   Positive samples (purchases): {y.sum()} ({y.mean()*100:.2f}%)")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        print(f"   Training Random Forest...")
        self.model.fit(X_scaled, y)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n   ✅ Training completed!")
        print(f"\n   📊 Top 10 Important Features:")
        for idx, row in feature_importance.head(10).iterrows():
            print(f"      {row['feature']}: {row['importance']:.4f}")
    
    def predict_proba(self, 
                      user_id: int,
                      product_id: int,
                      product_features: Dict,
                      user_stats: Dict = None,
                      interaction_stats: Dict = None) -> float:
        """
        Predict purchase probability for user-product pair
        
        Args:
            user_id: User ID
            product_id: Product ID
            product_features: Dict with product features
            user_stats: Optional user statistics
            interaction_stats: Optional interaction statistics
            
        Returns:
            Purchase probability (0-1)
        """
        # Prepare feature vector
        features = {}
        
        # Product features
        features.update({
            'price': product_features.get('price', 0),
            'stock': product_features.get('stock', 0),
            'rating': product_features.get('rating', 3.5),
            'num_reviews': product_features.get('num_reviews', 0),
            'discount': product_features.get('discount', 0),
            'is_new': product_features.get('is_new', 0),
            'popularity_score': product_features.get('popularity_score', 0.5),
        })
        
        # Interaction features
        if interaction_stats:
            features.update({
                'total_duration': interaction_stats.get('total_duration', 0),
                'num_interactions': interaction_stats.get('num_interactions', 0),
            })
        else:
            features.update({'total_duration': 0, 'num_interactions': 0})
        
        # Trend features
        features.update({
            'trending_score': product_features.get('trending_score', 0.5),
            'category_view_count': product_features.get('category_view_count', 0),
            'category_purchase_count': product_features.get('category_purchase_count', 0),
        })
        
        # User features
        if user_stats:
            features.update({
                'user_total_actions': user_stats.get('total_actions', 0),
                'user_unique_products': user_stats.get('unique_products', 0),
                'user_avg_price': user_stats.get('avg_price', 0),
            })
        else:
            features.update({
                'user_total_actions': 0,
                'user_unique_products': 0,
                'user_avg_price': 0,
            })
        
        # Product popularity
        features.update({
            'product_unique_users': product_features.get('unique_users', 0),
            'product_total_views': product_features.get('total_views', 0),
        })
        
        # Temporal features (use current time)
        import datetime
        now = datetime.datetime.now()
        features.update({
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'is_weekend': 1 if now.weekday() >= 5 else 0,
        })
        
        # Derived features
        features['price_relative_to_user'] = features['price'] / (features['user_avg_price'] + 1)
        features['conversion_rate'] = features['category_purchase_count'] / (features['category_view_count'] + 1)
        features['engagement_score'] = features['total_duration'] * features['num_interactions']
        
        # Encode categorical
        category = product_features.get('category', 'Unknown')
        brand = product_features.get('brand', 'Unknown')
        
        try:
            features['category_encoded'] = self.category_encoder.transform([category])[0]
        except:
            features['category_encoded'] = 0
        
        try:
            features['brand_encoded'] = self.brand_encoder.transform([brand])[0]
        except:
            features['brand_encoded'] = 0
        
        # Create feature vector
        X = np.array([[features.get(f, 0) for f in self.feature_names]])
        X_scaled = self.scaler.transform(X)
        
        # Predict
        proba = self.model.predict_proba(X_scaled)[0, 1]
        return float(proba)
    
    def recommend(self, 
                  user_id: int,
                  candidate_products: List[Dict],
                  k: int = 10) -> List[Tuple[int, float]]:
        """
        Recommend top-k products based on purchase probability
        
        Args:
            user_id: User ID
            candidate_products: List of product dicts with features
            k: Number of recommendations
            
        Returns:
            List of (product_id, probability) tuples
        """
        predictions = []
        
        for product in candidate_products:
            product_id = product['product_id']
            proba = self.predict_proba(user_id, product_id, product)
            predictions.append((product_id, proba))
        
        # Sort by probability
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:k]
    
    def save(self, filepath: str):
        """Save model to disk"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'category_encoder': self.category_encoder,
            'brand_encoder': self.brand_encoder
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 Model saved to: {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        model = cls()
        model.model = model_data['model']
        model.scaler = model_data['scaler']
        model.feature_names = model_data['feature_names']
        model.category_encoder = model_data['category_encoder']
        model.brand_encoder = model_data['brand_encoder']
        
        print(f"📂 Model loaded from: {filepath}")
        return model
