"""
Advanced Reed Making Analytics
Statistical analysis for reed performance and optimization
"""
try:
    import pandas as pd
    import numpy as np
    from scipy import stats
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score, mean_squared_error
    ADVANCED_ANALYTICS_AVAILABLE = True
except ImportError as e:
    print(f"Advanced analytics libraries not available: {e}")
    ADVANCED_ANALYTICS_AVAILABLE = False

from django.db.models import Avg, Count, Q
from reedsdata.models import Reedsdata


class ReedAnalytics:
    def __init__(self, user):
        self.user = user
        self.reeds_queryset = Reedsdata.objects.filter(reedauthor=user)
        self.df = None
        self._prepare_dataframe()
    
    def _prepare_dataframe(self):
        """Convert reed data to pandas DataFrame for analysis"""
        if not ADVANCED_ANALYTICS_AVAILABLE:
            self.df = None
            return
            
        reeds_data = list(self.reeds_queryset.values())
        if reeds_data:
            self.df = pd.DataFrame(reeds_data)
            # Convert date fields to datetime
            if 'date' in self.df.columns:
                self.df['date'] = pd.to_datetime(self.df['date'])
            
            # Create composite quality score from available fields
            quality_fields = ['playing_ease', 'intonation', 'response']
            available_quality_fields = [field for field in quality_fields if field in self.df.columns and self.df[field].count() > 0]
            
            # Handle tone_color separately as it has inverted scale (middle = best)
            if 'tone_color' in self.df.columns and self.df['tone_color'].count() > 0:
                # Convert tone_color to tone_balance: middle values (4-6) = high quality
                # Formula: 10 - abs(tone_color - 5) * 2
                self.df['tone_balance'] = 10 - (abs(self.df['tone_color'] - 5) * 2)
                available_quality_fields.append('tone_balance')
            
            if len(available_quality_fields) >= 2:  # Need at least 2 fields for meaningful composite
                # Create composite from available fields only
                quality_subset = self.df[available_quality_fields]
                # Calculate mean for each row, ignoring NaN values
                self.df['composite_quality'] = quality_subset.mean(axis=1, skipna=True)
            else:
                # Not enough quality data - use global quality impressions as fallback
                global_quality_fields = ['global_quality_first_impression', 'global_quality_second_impression', 'global_quality_third_impression']
                available_global_fields = [field for field in global_quality_fields if field in self.df.columns and self.df[field].count() > 0]
                
                if available_global_fields:
                    global_subset = self.df[available_global_fields]
                    self.df['composite_quality'] = global_subset.mean(axis=1, skipna=True)
                else:
                    # No quality data at all - create empty column
                    self.df['composite_quality'] = pd.Series(dtype='float64')
        else:
            self.df = pd.DataFrame()
    
    def cane_brand_analysis(self, selected_instrument=None):
        """Analyze performance by cane brand, separated by instrument"""
        if not ADVANCED_ANALYTICS_AVAILABLE or self.df is None or self.df.empty:
            return {}
        
        analysis = {}
        
        # Get instruments in the data
        instruments = self.df['instrument'].dropna().unique()
        
        # If specific instrument selected, use that one
        if selected_instrument and selected_instrument in instruments:
            primary_instrument = selected_instrument
        else:
            # Find the instrument with the most data for primary analysis
            instrument_counts = self.df['instrument'].value_counts()
            primary_instrument = instrument_counts.index[0] if len(instrument_counts) > 0 else None
        
        if primary_instrument is None:
            return {'error': 'No instrument data available'}
        
        print(f"DEBUG: Cane brand analysis using instrument: {primary_instrument}")
        
        # Filter data to selected instrument only
        instrument_df = self.df[self.df['instrument'] == primary_instrument]
        print(f"DEBUG: Filtered to {len(instrument_df)} records for {primary_instrument}")
        
        # Basic statistics by brand for this instrument
        brand_stats = instrument_df.groupby('cane_brand').agg({
            'composite_quality': ['count', 'mean', 'std'],
            'playing_ease': 'mean',
            'intonation': 'mean',
            'tone_color': 'mean',
            'response': 'mean'
        }).round(2)
        
        analysis['primary_instrument'] = primary_instrument
        analysis['available_instruments'] = list(instruments)
        
        # Statistical significance testing (ANOVA) for this instrument only
        brands = instrument_df['cane_brand'].unique()
        if len(brands) > 1:
            quality_by_brand = [
                instrument_df[instrument_df['cane_brand'] == brand]['composite_quality'].dropna()
                for brand in brands
            ]
            quality_by_brand = [group for group in quality_by_brand if len(group) > 0]
            
            if len(quality_by_brand) > 1:
                f_stat, p_value = stats.f_oneway(*quality_by_brand)
                analysis['anova_results'] = {
                    'f_statistic': round(f_stat, 4),
                    'p_value': round(p_value, 4),
                    'significant': p_value < 0.05
                }
        
        # Convert to dict for template use
        analysis['brand_performance'] = {}
        for brand in brand_stats.index:
            analysis['brand_performance'][brand] = {
                'count': int(brand_stats.loc[brand, ('composite_quality', 'count')]),
                'avg_quality': brand_stats.loc[brand, ('composite_quality', 'mean')],
                'quality_std': brand_stats.loc[brand, ('composite_quality', 'std')],
                'avg_playing_ease': brand_stats.loc[brand, ('playing_ease', 'mean')],
                'avg_intonation': brand_stats.loc[brand, ('intonation', 'mean')],
                'avg_tone_color': brand_stats.loc[brand, ('tone_color', 'mean')],
                'avg_response': brand_stats.loc[brand, ('response', 'mean')]
            }
        
        return analysis
    
    def parameter_success_analysis(self):
        """Find optimal parameter combinations using machine learning"""
        if not ADVANCED_ANALYTICS_AVAILABLE or self.df is None or self.df.empty or 'composite_quality' not in self.df.columns:
            return {}
        
        # Prepare features for ML
        feature_columns = ['thickness', 'hardness', 'flexibility', 'density', 
                          'temperature', 'humidity', 'diameter']
        
        # Create dummy variables for categorical features
        categorical_features = ['cane_brand', 'gouging_machine', 'profile_model', 'shaper']
        df_encoded = self.df.copy()
        
        for cat_col in categorical_features:
            if cat_col in df_encoded.columns:
                dummies = pd.get_dummies(df_encoded[cat_col], prefix=cat_col)
                df_encoded = pd.concat([df_encoded, dummies], axis=1)
        
        # Select all feature columns
        all_feature_cols = feature_columns + [col for col in df_encoded.columns 
                                            if any(col.startswith(cat) for cat in categorical_features)]
        
        # Filter available columns and remove nulls
        available_features = [col for col in all_feature_cols if col in df_encoded.columns]
        ml_data = df_encoded[available_features + ['composite_quality']].dropna()
        
        if len(ml_data) < 10:  # Need minimum data for ML
            return {'error': 'Insufficient data for parameter analysis'}
        
        X = ml_data[available_features]
        y = ml_data['composite_quality']
        
        # Random Forest for feature importance
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False).head(10)
        
        # Correlation analysis
        correlations = {}
        for col in feature_columns:
            if col in self.df.columns:
                corr = self.df[col].corr(self.df['composite_quality'])
                if not pd.isna(corr):
                    correlations[col] = round(corr, 3)
        
        # Predictive insights
        predictions = {}
        if len(X) > 0:
            # Find optimal parameter ranges for high quality
            high_quality_reeds = ml_data[ml_data['composite_quality'] >= 8]
            if len(high_quality_reeds) >= 3:
                for param in ['thickness', 'hardness', 'flexibility']:
                    if param in high_quality_reeds.columns:
                        param_data = high_quality_reeds[param].dropna()
                        if len(param_data) >= 2:
                            predictions[f'optimal_{param}'] = {
                                'min': round(param_data.min(), 1),
                                'max': round(param_data.max(), 1),
                                'avg': round(param_data.mean(), 1)
                            }
        
        return {
            'feature_importance': feature_importance.to_dict('records'),
            'correlations': correlations,
            'model_score': round(rf.score(X, y), 3),
            'optimal_ranges': predictions
        }
    
    def reed_progression_analysis(self):
        """Analyze improvement over time"""
        if not ADVANCED_ANALYTICS_AVAILABLE or self.df is None or self.df.empty or 'date' not in self.df.columns:
            return {}
        
        # Monthly progress
        self.df['year_month'] = self.df['date'].dt.to_period('M')
        monthly_progress = self.df.groupby('year_month').agg({
            'composite_quality': ['count', 'mean'],
            'playing_ease': 'mean',
            'global_quality_first_impression': 'mean'
        }).round(2)
        
        # Trend analysis
        if len(monthly_progress) > 2:
            months_numeric = range(len(monthly_progress))
            quality_trend = monthly_progress[('composite_quality', 'mean')].values
            
            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                months_numeric, quality_trend
            )
            
            trend_analysis = {
                'slope': round(slope, 4),
                'r_squared': round(r_value**2, 4),
                'improving': slope > 0,
                'significant': p_value < 0.05
            }
        else:
            trend_analysis = {'error': 'Insufficient data for trend analysis'}
        
        # Recent vs early performance
        mid_point = len(self.df) // 2
        if mid_point > 0:
            early_reeds = self.df.head(mid_point)['composite_quality'].mean()
            recent_reeds = self.df.tail(mid_point)['composite_quality'].mean()
            improvement = recent_reeds - early_reeds
        else:
            early_reeds = recent_reeds = improvement = 0
        
        return {
            'monthly_data': monthly_progress.to_dict(),
            'trend_analysis': trend_analysis,
            'early_avg': round(early_reeds, 2),
            'recent_avg': round(recent_reeds, 2),
            'improvement': round(improvement, 2)
        }
    
    def usage_patterns_analysis(self):
        """Analyze reed usage and performance patterns"""
        if not ADVANCED_ANALYTICS_AVAILABLE or self.df is None or self.df.empty:
            return {}
        
        analysis = {}
        
        # Rehearsal vs Concert usage
        if 'counts_rehearsal' in self.df.columns and 'counts_concert' in self.df.columns:
            rehearsal_data = self.df[self.df['counts_rehearsal'].notna()]
            concert_data = self.df[self.df['counts_concert'].notna()]
            
            analysis['usage_stats'] = {
                'avg_rehearsals': round(rehearsal_data['counts_rehearsal'].mean(), 1) if not rehearsal_data.empty else 0,
                'avg_concerts': round(concert_data['counts_concert'].mean(), 1) if not concert_data.empty else 0,
                'total_rehearsals': int(rehearsal_data['counts_rehearsal'].sum()) if not rehearsal_data.empty else 0,
                'total_concerts': int(concert_data['counts_concert'].sum()) if not concert_data.empty else 0
            }
            
            # Quality vs usage correlation
            if not rehearsal_data.empty and 'composite_quality' in rehearsal_data.columns:
                usage_quality_corr = rehearsal_data['counts_rehearsal'].corr(
                    rehearsal_data['composite_quality']
                )
                analysis['usage_quality_correlation'] = round(usage_quality_corr, 3) if not pd.isna(usage_quality_corr) else None
        
        # Global quality progression (1st vs 2nd vs 3rd impressions)
        impression_cols = ['global_quality_first_impression', 
                          'global_quality_second_impression', 
                          'global_quality_third_impression']
        
        impression_data = {}
        for col in impression_cols:
            if col in self.df.columns:
                avg_rating = self.df[col].mean()
                impression_data[col] = round(avg_rating, 2) if not pd.isna(avg_rating) else None
        
        analysis['impression_progression'] = impression_data
        
        # Seasonal patterns
        if 'date' in self.df.columns:
            self.df['month'] = self.df['date'].dt.month
            seasonal_quality = self.df.groupby('month')['composite_quality'].mean()
            analysis['seasonal_patterns'] = seasonal_quality.to_dict()
        
        return analysis
    
    def clustering_analysis(self):
        """Identify different types of reeds using clustering"""
        if not ADVANCED_ANALYTICS_AVAILABLE or self.df is None or self.df.empty:
            return {}
        
        # Prepare data for clustering
        cluster_features = ['stiffness', 'playing_ease', 'intonation', 'tone_color', 'response']
        cluster_data = self.df[cluster_features].dropna()
        
        if len(cluster_data) < 6:  # Need minimum data for clustering
            return {'error': 'Insufficient data for clustering analysis'}
        
        # Standardize features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(cluster_data)
        
        # K-means clustering
        optimal_k = min(4, len(cluster_data) // 3)  # Reasonable cluster count
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        
        # Analyze clusters
        cluster_data['cluster'] = clusters
        cluster_summary = cluster_data.groupby('cluster').agg({
            'playing_ease': 'mean',
            'intonation': 'mean',
            'tone_color': 'mean',
            'response': 'mean'
        }).round(2)
        
        cluster_analysis = {}
        for cluster_id in range(optimal_k):
            cluster_reeds = cluster_data[cluster_data['cluster'] == cluster_id]
            cluster_analysis[f'cluster_{cluster_id}'] = {
                'count': len(cluster_reeds),
                'characteristics': cluster_summary.loc[cluster_id].to_dict(),
                'avg_overall': round(cluster_summary.loc[cluster_id].mean(), 2)
            }
        
        return cluster_analysis
    
    def specific_insights_analysis(self):
        """Generate specific actionable insights based on data patterns"""
        if not ADVANCED_ANALYTICS_AVAILABLE or self.df is None or self.df.empty:
            return {'insights': []}
        
        insights = []
        
        # Insight 1: Best brand + parameter combinations
        if 'cane_brand' in self.df.columns and 'composite_quality' in self.df.columns:
            brand_hardness = self.df.groupby(['cane_brand', 'hardness']).agg({
                'composite_quality': ['mean', 'count']
            }).round(1)
            
            # Find best combinations with at least 2 reeds
            for brand in self.df['cane_brand'].unique():
                if pd.isna(brand) or brand == '' or brand == '0':
                    continue
                    
                brand_data = self.df[self.df['cane_brand'] == brand]
                if len(brand_data) >= 3:
                    avg_quality = brand_data['composite_quality'].mean()
                    hardness_range = brand_data['hardness'].dropna()
                    
                    if not hardness_range.empty and avg_quality >= 6:
                        min_h, max_h = hardness_range.min(), hardness_range.max()
                        insights.append(
                            f"{brand} cane gives you {avg_quality:.1f}/10 average quality, "
                            f"with hardness typically {min_h:.0f}-{max_h:.0f}"
                        )
        
        # Insight 2: High-performing parameter ranges
        if 'composite_quality' in self.df.columns:
            high_quality = self.df[self.df['composite_quality'] >= 8]
            if len(high_quality) >= 3:
                # Hardness insights
                if 'hardness' in high_quality.columns:
                    hardness_data = high_quality['hardness'].dropna()
                    if len(hardness_data) >= 2:
                        avg_hardness = hardness_data.mean()
                        insights.append(
                            f"Your best reeds (8+ rating) consistently have hardness around {avg_hardness:.1f}"
                        )
                
                # Thickness insights
                if 'thickness' in high_quality.columns:
                    thickness_data = high_quality['thickness'].dropna()
                    if len(thickness_data) >= 2:
                        avg_thickness = thickness_data.mean()
                        insights.append(
                            f"High-quality reeds tend to use {avg_thickness:.0f} gouge thickness"
                        )
        
        # Insight 3: Brand-specific parameter preferences
        for brand in ['Rigotti', 'Heinkel', 'Marigaux']:
            brand_data = self.df[self.df['cane_brand'] == brand]
            if len(brand_data) >= 3:
                if 'thickness' in brand_data.columns:
                    thickness_data = brand_data['thickness'].dropna()
                    quality_data = brand_data['composite_quality'].dropna()
                    
                    if len(thickness_data) >= 2 and len(quality_data) >= 2:
                        avg_thickness = thickness_data.mean()
                        avg_quality = quality_data.mean()
                        
                        if avg_quality >= 6:
                            if avg_thickness >= 70:
                                insights.append(f"{brand} cane works better when thicker (70+ gouge)")
                            elif avg_thickness <= 68:
                                insights.append(f"{brand} cane prefers thinner gouges (68- thickness)")
        
        # Insight 4: Usage pattern insights
        if 'counts_rehearsal' in self.df.columns and 'counts_concert' in self.df.columns:
            rehearsal_data = self.df[self.df['counts_rehearsal'] > 0]
            concert_data = self.df[self.df['counts_concert'] > 0]
            
            if len(rehearsal_data) >= 3 and len(concert_data) >= 3:
                rehearsal_flexibility = rehearsal_data['flexibility'].dropna().mean()
                concert_flexibility = concert_data['flexibility'].dropna().mean()
                
                if not pd.isna(rehearsal_flexibility) and not pd.isna(concert_flexibility):
                    if abs(rehearsal_flexibility - concert_flexibility) > 1:
                        if concert_flexibility > rehearsal_flexibility:
                            insights.append("Concert reeds tend to use more flexible cane than practice reeds")
                        else:
                            insights.append("Practice reeds use more flexible cane than concert reeds")
        
        # Insight 5: Improvement patterns
        if 'date' in self.df.columns and len(self.df) >= 10:
            # Recent vs old performance
            sorted_data = self.df.sort_values('date')
            mid_point = len(sorted_data) // 2
            old_reeds = sorted_data.iloc[:mid_point]
            recent_reeds = sorted_data.iloc[mid_point:]
            
            old_avg = old_reeds['composite_quality'].mean()
            recent_avg = recent_reeds['composite_quality'].mean()
            
            if not pd.isna(old_avg) and not pd.isna(recent_avg):
                improvement = recent_avg - old_avg
                if improvement > 0.5:
                    insights.append(f"Your reed making has improved by {improvement:.1f} points over time")
                elif improvement < -0.5:
                    insights.append(f"Recent reeds are {abs(improvement):.1f} points lower than earlier ones")
        
        # Insight 6: Seasonal patterns
        if 'date' in self.df.columns:
            self.df['month'] = pd.to_datetime(self.df['date']).dt.month
            monthly_quality = self.df.groupby('month')['composite_quality'].mean()
            
            if len(monthly_quality) >= 3:
                best_month = monthly_quality.idxmax()
                worst_month = monthly_quality.idxmin()

                month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']

                # Check for valid values before accessing
                if pd.notna(best_month) and pd.notna(worst_month) and monthly_quality[best_month] - monthly_quality[worst_month] > 1:
                    insights.append(f"You make better reeds in {month_names[best_month]} than {month_names[worst_month]}")
        
        return {'insights': insights[:6]}  # Limit to top 6 insights
    
    def correlation_analysis(self, selected_instrument=None, x_param='hardness', y_param='latest_global_quality'):
        """Analyze correlations between physical parameters and quality by instrument"""
        if not ADVANCED_ANALYTICS_AVAILABLE or self.df is None or self.df.empty:
            return {'error': 'Insufficient data for correlation analysis'}
        
        # Create derived columns if they don't exist
        if 'latest_global_quality' not in self.df.columns:
            def get_latest_quality(row):
                if pd.notna(row.get('global_quality_third_impression')):
                    return row['global_quality_third_impression']
                elif pd.notna(row.get('global_quality_second_impression')):
                    return row['global_quality_second_impression']
                elif pd.notna(row.get('global_quality_first_impression')):
                    return row['global_quality_first_impression']
                return None
            
            self.df['latest_global_quality'] = self.df.apply(get_latest_quality, axis=1)
        
        # Create density_auto if it doesn't exist and we have m1, m2
        if 'density_auto' not in self.df.columns and 'm1' in self.df.columns and 'm2' in self.df.columns:
            def calculate_density_auto(row):
                if pd.notna(row.get('m1')) and pd.notna(row.get('m2')):
                    try:
                        return row['m1'] / (row['m1'] + row['m2'])
                    except ZeroDivisionError:
                        return None
                return None
            
            self.df['density_auto'] = self.df.apply(calculate_density_auto, axis=1)
        
        # Parameter mapping for display
        param_labels = {
            'hardness': 'Hardness',
            'chamber_temperature': 'Chamber Temperature',
            'chamber_humidity': 'Chamber Humidity',
            'harvest_year': 'Harvest Year',
            'gouging_machine': 'Gouging Machine',
            'profile_model': 'Profile Model',
            'diameter': 'Cane Diameter',
            'thickness': 'Thickness',
            'flexibility': 'Flexibility',
            'density': 'Density',
            'density_auto': 'Density Auto',
            'shaper': 'Shaper',
            'staple_model': 'Staple(ob)',
            'temperature': 'Temperature (from API)',
            'altitude': 'Altitude (from API)',
            'humidity': 'Humidity (from API)',
            'air_pressure': 'Air Pressure (from API)',
            'weather_description': 'Weather Description',
            'tone_color': 'Tone Color',
            'intonation': 'Intonation',
            'playing_ease': 'Playing Ease',
            'response': 'Response',
            'latest_global_quality': 'Global Quality'
        }
        
        print(f"DEBUG: Correlation analysis - X: {x_param}, Y: {y_param}")
        
        # Get available instruments
        instruments = self.df['instrument'].dropna().unique()
        
        # If specific instrument selected, analyze only that one
        if selected_instrument and selected_instrument in instruments:
            instruments_to_analyze = [selected_instrument]
        else:
            instruments_to_analyze = instruments
        
        instrument_analyses = {}
        
        for instrument in instruments_to_analyze:
            # Filter data for this instrument only
            instrument_df = self.df[self.df['instrument'] == instrument]
            
            # Filter records with both X and Y parameter data
            records_with_data = instrument_df.dropna(subset=[x_param])
            records_with_data = records_with_data[records_with_data[y_param].notnull()]
            
            if len(records_with_data) < 3:
                instrument_analyses[instrument] = {
                    'error': f'Insufficient data for {instrument} (need at least 3 points, have {len(records_with_data)})'
                }
                continue
            
            # Create scatter plot data for this instrument
            correlation_data = []
            for _, reed in records_with_data.iterrows():
                x_value = reed[x_param]
                y_value = reed[y_param]
                
                # Handle categorical parameters
                if x_param in ['gouging_machine', 'shaper', 'cane_brand']:
                    # For categorical data, we'll use a numeric mapping in the frontend
                    x_display = str(x_value) if pd.notna(x_value) else 'Unknown'
                    x_numeric = float(hash(str(x_value)) % 100) if pd.notna(x_value) else 0  # Simple hash for positioning
                else:
                    x_display = float(x_value) if pd.notna(x_value) else 0
                    x_numeric = float(x_value) if pd.notna(x_value) else 0
                
                y_numeric = float(y_value) if pd.notna(y_value) else 0
                
                correlation_data.append({
                    'reed_id': reed.get('reed_ID', 'Unknown'),
                    'x_value': x_numeric,
                    'y_value': y_numeric,
                    'x_display': x_display,
                    'y_display': y_numeric,
                    'cane_brand': reed.get('cane_brand', 'Unknown'),
                    'x_param': x_param,
                    'y_param': y_param
                })
            
            # Calculate correlation coefficient (only for numeric parameters)
            if x_param not in ['gouging_machine', 'shaper', 'cane_brand'] and y_param not in ['gouging_machine', 'shaper', 'cane_brand']:
                x_values = [point['x_value'] for point in correlation_data]
                y_values = [point['y_value'] for point in correlation_data]
                correlation_coef = np.corrcoef(x_values, y_values)[0, 1] if len(x_values) > 1 else 0
            else:
                correlation_coef = 0  # No correlation for categorical data
            
            # Interpret correlation strength
            if abs(correlation_coef) >= 0.7:
                strength = 'Strong'
            elif abs(correlation_coef) >= 0.4:
                strength = 'Moderate'
            elif abs(correlation_coef) >= 0.2:
                strength = 'Weak'
            else:
                strength = 'Very Weak'
            
            direction = 'Positive' if correlation_coef > 0 else 'Negative'
            
            # Generate insights for this instrument
            insights = []
            if x_param not in ['gouging_machine', 'shaper', 'cane_brand'] and y_param not in ['gouging_machine', 'shaper', 'cane_brand']:
                if correlation_coef > 0.4:
                    insights.append(f"For {instrument}: Higher {param_labels[x_param]} tends to produce higher {param_labels[y_param]} (r={correlation_coef:.3f})")
                elif correlation_coef < -0.4:
                    insights.append(f"For {instrument}: Higher {param_labels[x_param]} tends to produce lower {param_labels[y_param]} (r={correlation_coef:.3f})")
                else:
                    insights.append(f"For {instrument}: {param_labels[x_param]} shows little correlation with {param_labels[y_param]} (r={correlation_coef:.3f})")
            else:
                insights.append(f"For {instrument}: Showing distribution of {param_labels[x_param]} vs {param_labels[y_param]}")
            
            # Add optimal range suggestion for this instrument
            if len(correlation_data) >= 5 and y_param in ['playing_ease', 'intonation', 'tone_color', 'latest_global_quality']:
                # Find the parameter range of high-quality reeds
                high_quality_reeds = [point for point in correlation_data if point['y_value'] >= 8]
                if len(high_quality_reeds) >= 3 and x_param not in ['gouging_machine', 'shaper', 'cane_brand']:
                    x_values = [reed['x_value'] for reed in high_quality_reeds]
                    optimal_range = {
                        'min': min(x_values),
                        'max': max(x_values),
                        'avg': sum(x_values) / len(x_values)
                    }
                    insights.append(f"Best {instrument} reeds (8+ {param_labels[y_param]}) use {param_labels[x_param]} {optimal_range['min']:.1f}-{optimal_range['max']:.1f}")
            
            instrument_analyses[instrument] = {
                'scatter_data': correlation_data,
                'correlation_coefficient': correlation_coef,
                'correlation_strength': strength,
                'correlation_direction': direction,
                'sample_size': len(correlation_data),
                'insights': insights,
                'chart_config': {
                    'x_label': param_labels.get(x_param, x_param),
                    'y_label': param_labels.get(y_param, y_param),
                    'title': f'{instrument}: {param_labels.get(x_param, x_param)} vs {param_labels.get(y_param, y_param)}',
                    'x_param': x_param,
                    'y_param': y_param,
                    'y_scale_0_to_10': y_param in ['playing_ease', 'intonation', 'tone_color', 'latest_global_quality']
                }
            }
        
        # Return analysis for the selected instrument or the one with the most data
        if not instrument_analyses:
            print("DEBUG: No instrument analyses available")
            return {
                'error': 'No instruments have sufficient data for correlation analysis',
                'available_instruments': list(instruments),
                'selected_instrument': selected_instrument
            }
        
        # If specific instrument selected, use that one
        if selected_instrument and selected_instrument in instrument_analyses and 'error' not in instrument_analyses[selected_instrument]:
            best_instrument = selected_instrument
        else:
            # Find instrument with most data points
            best_instrument = max(
                [instr for instr, data in instrument_analyses.items() if 'error' not in data],
                key=lambda instr: instrument_analyses[instr]['sample_size'],
                default=None
            )
        
        print(f"DEBUG: Best instrument: {best_instrument}")
        
        if best_instrument is None:
            print("DEBUG: No best instrument found")
            return {
                'error': 'No instruments have sufficient data for correlation analysis',
                'available_instruments': list(instruments),
                'selected_instrument': selected_instrument
            }
        
        # Add summary of all instruments
        summary = {
            'total_instruments': len(instruments),
            'instruments_analyzed': len([data for data in instrument_analyses.values() if 'error' not in data]),
            'primary_instrument': best_instrument,
            'selected_instrument': selected_instrument,
            'available_instruments': list(instruments),
            'all_instruments': instrument_analyses
        }
        
        result = instrument_analyses[best_instrument].copy()
        result['instrument_summary'] = summary
        
        print(f"DEBUG: Correlation analysis result has {len(result.get('scatter_data', []))} scatter points")
        print(f"DEBUG: Sample scatter data: {result.get('scatter_data', [])[:2]}")
        
        return result
    
    def get_comprehensive_analysis(self, selected_instrument=None, x_param='hardness', y_param='latest_global_quality'):
        """Get all analyses in one call"""
        print(f"DEBUG: Running comprehensive analysis for instrument: {selected_instrument}, X: {x_param}, Y: {y_param}")
        return {
            'cane_brand_analysis': self.cane_brand_analysis(selected_instrument),
            'parameter_success_analysis': self.parameter_success_analysis(),
            'reed_progression_analysis': self.reed_progression_analysis(),
            'usage_patterns_analysis': self.usage_patterns_analysis(),
            'clustering_analysis': self.clustering_analysis(),
            'specific_insights': self.specific_insights_analysis(),
            'correlation_analysis': self.correlation_analysis(selected_instrument, x_param, y_param),
            'data_summary': {
                'total_reeds': len(self.df) if self.df is not None and not self.df.empty else 0,
                'has_sufficient_data': len(self.df) >= 10 if self.df is not None and not self.df.empty else False,
                'advanced_analytics_available': ADVANCED_ANALYTICS_AVAILABLE,
                'selected_instrument': selected_instrument
            }
        }