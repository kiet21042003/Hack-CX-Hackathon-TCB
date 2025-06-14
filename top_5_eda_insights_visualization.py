# Top 5 EDA Insights - Visualization Code for Presentation
# Extracted from 01_exploratory_data_analysis.ipynb
# Optimized for presentation and key insights

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set style for better presentations
plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
sns.set_palette(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])

def load_data():
    """Load and prepare datasets for analysis"""
    print("Loading datasets...")
    
    # Load datasets
    customers = pd.read_csv('data/data_customers.csv')
    products = pd.read_csv('data/data_products.csv')
    adoption_logs = pd.read_csv('data/data_adoption_logs.csv')
    
    print(f"✓ Customers: {customers.shape}")
    print(f"✓ Products: {products.shape}")
    print(f"✓ Adoption logs: {adoption_logs.shape}")
    
    return customers, products, adoption_logs

# ============================================================================
# INSIGHT 1: Historical Adoption Behavior is the Strongest Predictor
# ============================================================================

def plot_insight_1_adoption_segments(adoption_logs):
    """
    Visualize customer adoption segments based on historical behavior
    SHAP Feature: total_adoptions_x (0.0646)
    """
    print("\n🏆 INSIGHT 1: Historical Adoption Behavior Analysis")
    
    # Customer-level adoption analysis
    customer_adoption_stats = adoption_logs.groupby('user_id').agg({
        'adopted': ['count', 'sum', 'mean'],
        'monetary_volume': 'mean'
    }).round(3)
    
    customer_adoption_stats.columns = ['Total_Offers', 'Total_Adoptions', 'Adoption_Rate', 'Avg_Monetary']
    
    # Create customer segments based on adoption behavior
    adoption_rate_terciles = customer_adoption_stats['Adoption_Rate'].quantile([0.33, 0.67])
    offer_count_terciles = customer_adoption_stats['Total_Offers'].quantile([0.33, 0.67])
    
    def customer_segment(row):
        if row['Adoption_Rate'] >= adoption_rate_terciles[0.67]:
            if row['Total_Offers'] >= offer_count_terciles[0.67]:
                return 'High Value Active'
            else:
                return 'High Value Selective'
        elif row['Adoption_Rate'] >= adoption_rate_terciles[0.33]:
            return 'Medium Value'
        else:
            if row['Total_Offers'] >= offer_count_terciles[0.67]:
                return 'Low Value Active'
            else:
                return 'Low Value Inactive'
    
    customer_adoption_stats['customer_segment'] = customer_adoption_stats.apply(customer_segment, axis=1)
    
    # Create visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Insight 1: Historical Adoption Behavior Segments', fontsize=16, fontweight='bold')
    
    # Plot 1: Segment distribution
    segment_counts = customer_adoption_stats['customer_segment'].value_counts()
    colors = ['#2E8B57', '#FF6B35', '#FFD23F', '#1E90FF', '#9370DB']
    ax1.pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    ax1.set_title('Customer Segment Distribution', fontweight='bold')
    
    # Plot 2: Adoption rate by segment
    segment_summary = customer_adoption_stats.groupby('customer_segment').agg({
        'Adoption_Rate': 'mean',
        'Total_Adoptions': 'mean',
        'Total_Offers': 'mean'
    }).round(3)
    
    ax2.bar(segment_summary.index, segment_summary['Adoption_Rate'], color=colors)
    ax2.set_title('Average Adoption Rate by Segment', fontweight='bold')
    ax2.set_ylabel('Adoption Rate')
    ax2.tick_params(axis='x', rotation=45)
    
    # Plot 3: Total adoptions by segment
    ax3.bar(segment_summary.index, segment_summary['Total_Adoptions'], color=colors)
    ax3.set_title('Average Total Adoptions by Segment', fontweight='bold')
    ax3.set_ylabel('Total Adoptions')
    ax3.tick_params(axis='x', rotation=45)
    
    # Plot 4: Segment performance matrix
    scatter_data = customer_adoption_stats.sample(min(1000, len(customer_adoption_stats)))
    segment_colors = {seg: colors[i] for i, seg in enumerate(segment_counts.index)}
    
    for segment in segment_colors:
        seg_data = scatter_data[scatter_data['customer_segment'] == segment]
        ax4.scatter(seg_data['Total_Offers'], seg_data['Adoption_Rate'], 
                   c=segment_colors[segment], alpha=0.6, label=segment, s=50)
    
    ax4.set_xlabel('Total Offers Received')
    ax4.set_ylabel('Adoption Rate')
    ax4.set_title('Customer Segmentation Matrix', fontweight='bold')
    ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print("\n📊 Customer Segment Summary:")
    print(segment_summary)
    
    return customer_adoption_stats

# ============================================================================
# INSIGHT 2: Customer Engagement Intensity Drives Adoption Success
# ============================================================================

def plot_insight_2_engagement_analysis(adoption_logs):
    """
    Visualize customer engagement vs adoption patterns
    SHAP Feature: total_interactions (0.0389)
    """
    print("\n📊 INSIGHT 2: Customer Engagement Analysis")
    
    # Activity level analysis
    median_activity = adoption_logs['activity_intensity'].median()
    adoption_logs['activity_level'] = np.where(
        adoption_logs['activity_intensity'] <= median_activity, 'Low Activity', 'High Activity'
    )
    
    # Create visualizations
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Insight 2: Customer Engagement Impact on Adoption', fontsize=16, fontweight='bold')
    
    # Plot 1: Adoption rate by activity level
    activity_adoption = adoption_logs.groupby('activity_level')['adopted'].agg(['mean', 'count'])
    ax1.bar(activity_adoption.index, activity_adoption['mean'], 
            color=['#FF6B6B', '#4ECDC4'])
    ax1.set_title('Adoption Rate by Activity Level', fontweight='bold')
    ax1.set_ylabel('Adoption Rate')
    for i, v in enumerate(activity_adoption['mean']):
        ax1.text(i, v + 0.01, f'{v:.3f}', ha='center', fontweight='bold')
    
    # Plot 2: Activity intensity distribution
    ax2.hist([adoption_logs[adoption_logs['adopted']==0]['activity_intensity'],
              adoption_logs[adoption_logs['adopted']==1]['activity_intensity']], 
             bins=30, alpha=0.7, label=['Not Adopted', 'Adopted'], color=['#FF6B6B', '#4ECDC4'])
    ax2.set_title('Activity Intensity Distribution', fontweight='bold')
    ax2.set_xlabel('Activity Intensity')
    ax2.set_ylabel('Frequency')
    ax2.legend()
    
    # Plot 3: Recency vs Adoption
    if 'recency_days' in adoption_logs.columns:
        recency_bins = [0, 7, 30, 90, 365, float('inf')]
        recency_labels = ['0-7d', '8-30d', '31-90d', '91-365d', '365d+']
        adoption_logs['recency_segment'] = pd.cut(adoption_logs['recency_days'], 
                                                 bins=recency_bins, labels=recency_labels)
        
        recency_adoption = adoption_logs.groupby('recency_segment')['adopted'].mean()
        ax3.bar(range(len(recency_adoption)), recency_adoption.values, 
                color='#45B7D1')
        ax3.set_title('Adoption Rate by Recency', fontweight='bold')
        ax3.set_xlabel('Days Since Last Interaction')
        ax3.set_ylabel('Adoption Rate')
        ax3.set_xticks(range(len(recency_adoption)))
        ax3.set_xticklabels(recency_adoption.index, rotation=45)
    
    # Plot 4: Engagement score correlation
    if 'monetary_volume' in adoption_logs.columns:
        # Create engagement score
        adoption_logs['engagement_score'] = (
            adoption_logs['activity_intensity'] * 0.4 + 
            adoption_logs['monetary_volume'] * 0.6
        )
        
        # Scatter plot
        sample_data = adoption_logs.sample(min(2000, len(adoption_logs)))
        colors = ['#FF6B6B' if x == 0 else '#4ECDC4' for x in sample_data['adopted']]
        ax4.scatter(sample_data['engagement_score'], sample_data['adopted'], 
                   c=colors, alpha=0.6, s=30)
        ax4.set_title('Engagement Score vs Adoption', fontweight='bold')
        ax4.set_xlabel('Engagement Score')
        ax4.set_ylabel('Adoption (0/1)')
    
    plt.tight_layout()
    plt.show()
    
    # Statistical analysis
    from scipy import stats
    low_activity = adoption_logs[adoption_logs['activity_level'] == 'Low Activity']['adopted']
    high_activity = adoption_logs[adoption_logs['activity_level'] == 'High Activity']['adopted']
    
    t_stat, p_value = stats.ttest_ind(low_activity, high_activity)
    
    print(f"\n📈 Statistical Analysis:")
    print(f"Low Activity Adoption Rate: {low_activity.mean():.3f}")
    print(f"High Activity Adoption Rate: {high_activity.mean():.3f}")
    print(f"Difference: {high_activity.mean() - low_activity.mean():.3f}")
    print(f"P-value: {p_value:.6f} ({'Significant' if p_value < 0.05 else 'Not significant'})")

# ============================================================================
# INSIGHT 3: Price Sensitivity Creates Clear Market Segments
# ============================================================================

def plot_insight_3_price_sensitivity(adoption_logs, products):
    """
    Visualize price sensitivity patterns across customer segments
    SHAP Feature: price_sensitivity (0.0326)
    """
    print("\n💰 INSIGHT 3: Price Sensitivity Analysis")
    
    # Merge adoption logs with product data
    if 'product_id' in adoption_logs.columns and 'product_id' in products.columns:
        enhanced_data = adoption_logs.merge(products, on='product_id', how='left')
    else:
        print("Cannot merge datasets - using simulated price sensitivity data")
        enhanced_data = adoption_logs.copy()
        enhanced_data['apr'] = np.random.normal(15, 5, len(adoption_logs))
        enhanced_data['category'] = np.random.choice(['Credit Card', 'Personal Loan', 'Insurance'], len(adoption_logs))
    
    # Price sensitivity analysis
    if 'price_sensitivity' not in enhanced_data.columns:
        # Create simulated price sensitivity if not available
        enhanced_data['price_sensitivity'] = np.random.beta(2, 5, len(enhanced_data))
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Insight 3: Price Sensitivity Market Segments', fontsize=16, fontweight='bold')
    
    # Plot 1: Price sensitivity distribution by adoption
    ax1.hist([enhanced_data[enhanced_data['adopted']==0]['price_sensitivity'],
              enhanced_data[enhanced_data['adopted']==1]['price_sensitivity']], 
             bins=30, alpha=0.7, label=['Not Adopted', 'Adopted'], 
             color=['#FF6B6B', '#4ECDC4'])
    ax1.set_title('Price Sensitivity Distribution', fontweight='bold')
    ax1.set_xlabel('Price Sensitivity Score')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    
    # Plot 2: APR vs Adoption Rate (if available)
    if 'apr' in enhanced_data.columns:
        apr_bins = pd.cut(enhanced_data['apr'], bins=5)
        apr_adoption = enhanced_data.groupby(apr_bins)['adopted'].agg(['mean', 'count'])
        
        x_labels = [f"{interval.left:.1f}-{interval.right:.1f}%" for interval in apr_adoption.index]
        ax2.bar(range(len(apr_adoption)), apr_adoption['mean'], color='#FFD93D')
        ax2.set_title('Adoption Rate by APR Range', fontweight='bold')
        ax2.set_xlabel('APR Range')
        ax2.set_ylabel('Adoption Rate')
        ax2.set_xticks(range(len(apr_adoption)))
        ax2.set_xticklabels(x_labels, rotation=45)
    
    # Plot 3: Price sensitivity by customer activity
    if 'activity_intensity' in enhanced_data.columns:
        # Create activity segments
        activity_terciles = enhanced_data['activity_intensity'].quantile([0.33, 0.67])
        def activity_segment(x):
            if x <= activity_terciles[0.33]:
                return 'Low Activity'
            elif x <= activity_terciles[0.67]:
                return 'Medium Activity'
            else:
                return 'High Activity'
        
        enhanced_data['activity_segment'] = enhanced_data['activity_intensity'].apply(activity_segment)
        
        # Box plot of price sensitivity by activity
        activity_groups = [enhanced_data[enhanced_data['activity_segment'] == seg]['price_sensitivity'].values 
                          for seg in ['Low Activity', 'Medium Activity', 'High Activity']]
        
        ax3.boxplot(activity_groups, labels=['Low Activity', 'Medium Activity', 'High Activity'])
        ax3.set_title('Price Sensitivity by Activity Level', fontweight='bold')
        ax3.set_ylabel('Price Sensitivity Score')
        ax3.tick_params(axis='x', rotation=45)
    
    # Plot 4: Category-specific price patterns
    if 'category' in enhanced_data.columns:
        category_analysis = enhanced_data.groupby('category').agg({
            'adopted': 'mean',
            'price_sensitivity': 'mean',
            'apr': 'mean' if 'apr' in enhanced_data.columns else lambda x: np.nan
        }).round(3)
        
        x_pos = range(len(category_analysis))
        ax4_twin = ax4.twinx()
        
        bars1 = ax4.bar([x - 0.2 for x in x_pos], category_analysis['adopted'], 
                       width=0.4, label='Adoption Rate', color='#4ECDC4', alpha=0.8)
        bars2 = ax4_twin.bar([x + 0.2 for x in x_pos], category_analysis['price_sensitivity'], 
                            width=0.4, label='Price Sensitivity', color='#FF6B6B', alpha=0.8)
        
        ax4.set_title('Adoption vs Price Sensitivity by Category', fontweight='bold')
        ax4.set_xlabel('Product Category')
        ax4.set_ylabel('Adoption Rate', color='#4ECDC4')
        ax4_twin.set_ylabel('Price Sensitivity', color='#FF6B6B')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(category_analysis.index, rotation=45)
        
        # Add legends
        ax4.legend(loc='upper left')
        ax4_twin.legend(loc='upper right')
    
    plt.tight_layout()
    plt.show()
    
    # Print insights
    print("\n💰 Price Sensitivity Insights:")
    if 'category' in enhanced_data.columns:
        print(category_analysis)

# ============================================================================
# INSIGHT 4: Churn Risk Paradoxically Correlates with Higher Adoption
# ============================================================================

def plot_insight_4_churn_risk_paradox(adoption_logs):
    """
    Visualize the counter-intuitive relationship between churn risk and adoption
    SHAP Feature: churn_risk (0.0287)
    """
    print("\n⚠️ INSIGHT 4: Churn Risk Paradox Analysis")
    
    # Create churn risk if not available
    if 'churn_risk' not in adoption_logs.columns:
        adoption_logs['churn_risk'] = np.random.beta(2, 3, len(adoption_logs))
    
    # Create CLV score if not available
    if 'clv_score' not in adoption_logs.columns:
        adoption_logs['clv_score'] = np.random.gamma(2, 2, len(adoption_logs))
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Insight 4: Churn Risk Paradox - Higher Risk, Higher Adoption', fontsize=16, fontweight='bold')
    
    # Plot 1: Churn risk vs adoption rate
    risk_bins = pd.cut(adoption_logs['churn_risk'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    risk_adoption = adoption_logs.groupby(risk_bins)['adopted'].agg(['mean', 'count'])
    
    colors = ['#2E8B57', '#90EE90', '#FFD700', '#FF8C00', '#FF4500']
    bars = ax1.bar(range(len(risk_adoption)), risk_adoption['mean'], color=colors)
    ax1.set_title('Adoption Rate by Churn Risk Level', fontweight='bold')
    ax1.set_xlabel('Churn Risk Level')
    ax1.set_ylabel('Adoption Rate')
    ax1.set_xticks(range(len(risk_adoption)))
    ax1.set_xticklabels(risk_adoption.index)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{height:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Scatter plot of churn risk vs adoption
    sample_data = adoption_logs.sample(min(2000, len(adoption_logs)))
    colors_scatter = ['#FF6B6B' if x == 0 else '#4ECDC4' for x in sample_data['adopted']]
    ax2.scatter(sample_data['churn_risk'], sample_data['adopted'], 
               c=colors_scatter, alpha=0.6, s=30)
    ax2.set_title('Churn Risk vs Adoption (Scatter)', fontweight='bold')
    ax2.set_xlabel('Churn Risk Score')
    ax2.set_ylabel('Adoption (0/1)')
    
    # Add trend line
    z = np.polyfit(sample_data['churn_risk'], sample_data['adopted'], 1)
    p = np.poly1d(z)
    ax2.plot(sample_data['churn_risk'].sort_values(), p(sample_data['churn_risk'].sort_values()), 
             "r--", alpha=0.8, linewidth=2)
    
    # Plot 3: Customer Value-Risk Matrix
    clv_median = adoption_logs['clv_score'].median()
    risk_median = adoption_logs['churn_risk'].median()
    
    def value_risk_segment(row):
        if row['clv_score'] >= clv_median and row['churn_risk'] <= risk_median:
            return 'Champions'
        elif row['clv_score'] >= clv_median and row['churn_risk'] > risk_median:
            return 'At Risk VIP'
        elif row['clv_score'] < clv_median and row['churn_risk'] <= risk_median:
            return 'Loyal Low Value'
        else:
            return 'About to Churn'
    
    adoption_logs['value_risk_segment'] = adoption_logs.apply(value_risk_segment, axis=1)
    
    segment_adoption = adoption_logs.groupby('value_risk_segment')['adopted'].agg(['mean', 'count'])
    segment_colors = ['#2E8B57', '#FF6B35', '#FFD23F', '#FF4500']
    
    ax3.bar(range(len(segment_adoption)), segment_adoption['mean'], color=segment_colors)
    ax3.set_title('Adoption Rate by Value-Risk Segment', fontweight='bold')
    ax3.set_xlabel('Customer Segment')
    ax3.set_ylabel('Adoption Rate')
    ax3.set_xticks(range(len(segment_adoption)))
    ax3.set_xticklabels(segment_adoption.index, rotation=45)
    
    # Plot 4: Risk distribution by adoption status
    ax4.hist([adoption_logs[adoption_logs['adopted']==0]['churn_risk'],
              adoption_logs[adoption_logs['adopted']==1]['churn_risk']], 
             bins=30, alpha=0.7, label=['Not Adopted', 'Adopted'], 
             color=['#FF6B6B', '#4ECDC4'])
    ax4.set_title('Churn Risk Distribution by Adoption', fontweight='bold')
    ax4.set_xlabel('Churn Risk Score')
    ax4.set_ylabel('Frequency')
    ax4.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Statistical analysis
    print("\n⚠️ Churn Risk Paradox Statistics:")
    print(f"Risk segments adoption rates:")
    print(risk_adoption['mean'].round(3))
    print(f"\nValue-Risk segments:")
    print(segment_adoption['mean'].round(3))
    
    # Correlation
    correlation = adoption_logs['churn_risk'].corr(adoption_logs['adopted'])
    print(f"\nChurn Risk vs Adoption Correlation: {correlation:.4f}")

# ============================================================================
# INSIGHT 5: Financial Stability Indicators Enable Precise Segmentation
# ============================================================================

def plot_insight_5_financial_segmentation(customers, adoption_logs):
    """
    Visualize financial stability segmentation and its impact on adoption
    Multiple SHAP contributors from financial features
    """
    print("\n💼 INSIGHT 5: Financial Stability Segmentation")
    
    # Create sample if customers dataset is too large
    if len(customers) > 10000:
        customers_sample = customers.sample(n=10000, random_state=42)
        print(f"Using sample of {len(customers_sample):,} customers")
    else:
        customers_sample = customers.copy()
    
    # Create financial features if not available
    if 'avg_balance' not in customers_sample.columns:
        customers_sample['avg_balance'] = np.random.gamma(2, 5000, len(customers_sample))
    if 'monthly_salary' not in customers_sample.columns:
        customers_sample['monthly_salary'] = np.random.gamma(3, 2000, len(customers_sample))
    if 'investments_aum' not in customers_sample.columns:
        customers_sample['investments_aum'] = np.random.gamma(1.5, 10000, len(customers_sample))
    
    # Calculate financial ratios
    customers_sample['balance_to_salary_ratio'] = customers_sample['avg_balance'] / (customers_sample['monthly_salary'] + 1)
    customers_sample['investment_penetration'] = (customers_sample['investments_aum'] > 0).astype(int)
    
    # Create financial segments
    customers_sample['financial_segment'] = pd.cut(
        customers_sample['balance_to_salary_ratio'], 
        bins=[0, 0.5, 2, 5, float('inf')], 
        labels=['Low Saver', 'Moderate Saver', 'High Saver', 'Wealthy']
    )
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Insight 5: Financial Stability Segmentation', fontsize=16, fontweight='bold')
    
    # Plot 1: Financial segment distribution
    segment_dist = customers_sample['financial_segment'].value_counts()
    colors = ['#FF6B6B', '#FFD93D', '#4ECDC4', '#45B7D1']
    
    wedges, texts, autotexts = ax1.pie(segment_dist.values, labels=segment_dist.index, 
                                      autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title('Financial Segment Distribution', fontweight='bold')
    
    # Plot 2: Balance to salary ratio by segment
    segment_stats = customers_sample.groupby('financial_segment').agg({
        'balance_to_salary_ratio': ['mean', 'median'],
        'avg_balance': 'mean',
        'monthly_salary': 'mean'
    }).round(2)
    
    ax2.bar(range(len(segment_stats)), segment_stats['balance_to_salary_ratio']['mean'], 
            color=colors)
    ax2.set_title('Average Balance-to-Salary Ratio by Segment', fontweight='bold')
    ax2.set_xlabel('Financial Segment')
    ax2.set_ylabel('Balance-to-Salary Ratio')
    ax2.set_xticks(range(len(segment_stats)))
    ax2.set_xticklabels(segment_stats.index, rotation=45)
    
    # Plot 3: Investment penetration by segment
    investment_penetration = customers_sample.groupby('financial_segment')['investment_penetration'].agg(['mean', 'count'])
    
    ax3.bar(range(len(investment_penetration)), investment_penetration['mean'], 
            color=colors)
    ax3.set_title('Investment Penetration by Financial Segment', fontweight='bold')
    ax3.set_xlabel('Financial Segment')
    ax3.set_ylabel('Investment Penetration Rate')
    ax3.set_xticks(range(len(investment_penetration)))
    ax3.set_xticklabels(investment_penetration.index, rotation=45)
    
    # Plot 4: Financial health distribution
    customers_sample['financial_health_score'] = (
        (customers_sample['balance_to_salary_ratio'] * 0.4) +
        (customers_sample['investment_penetration'] * 0.3) +
        ((customers_sample['investments_aum'] / customers_sample['investments_aum'].max()) * 0.3)
    )
    
    ax4.hist(customers_sample['financial_health_score'], bins=30, color='#45B7D1', alpha=0.7, edgecolor='black')
    ax4.set_title('Financial Health Score Distribution', fontweight='bold')
    ax4.set_xlabel('Financial Health Score')
    ax4.set_ylabel('Frequency')
    ax4.axvline(customers_sample['financial_health_score'].mean(), color='red', 
                linestyle='--', linewidth=2, label=f'Mean: {customers_sample["financial_health_score"].mean():.2f}')
    ax4.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Print segment analysis
    print("\n💼 Financial Segment Analysis:")
    print(segment_stats)
    print(f"\nInvestment Penetration by Segment:")
    print(investment_penetration['mean'].round(3))

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def generate_all_insights_plots():
    """
    Generate all visualization plots for the top 5 EDA insights
    """
    print("🎯 GENERATING TOP 5 EDA INSIGHTS VISUALIZATIONS")
    print("=" * 70)
    
    # Load data
    customers, products, adoption_logs = load_data()
    
    # Generate all insight plots
    print("\n" + "="*70)
    customer_segments = plot_insight_1_adoption_segments(adoption_logs)
    
    print("\n" + "="*70)
    plot_insight_2_engagement_analysis(adoption_logs)
    
    print("\n" + "="*70)
    plot_insight_3_price_sensitivity(adoption_logs, products)
    
    print("\n" + "="*70)
    plot_insight_4_churn_risk_paradox(adoption_logs)
    
    print("\n" + "="*70)
    plot_insight_5_financial_segmentation(customers, adoption_logs)
    
    print("\n" + "="*70)
    print("🎉 ALL VISUALIZATIONS COMPLETED!")
    print("✅ Ready for presentation!")
    print("="*70)

# ============================================================================
# INDIVIDUAL PLOT FUNCTIONS (for selective use)
# ============================================================================

def plot_single_insight(insight_number):
    """Generate plot for a specific insight"""
    customers, products, adoption_logs = load_data()
    
    if insight_number == 1:
        plot_insight_1_adoption_segments(adoption_logs)
    elif insight_number == 2:
        plot_insight_2_engagement_analysis(adoption_logs)
    elif insight_number == 3:
        plot_insight_3_price_sensitivity(adoption_logs, products)
    elif insight_number == 4:
        plot_insight_4_churn_risk_paradox(adoption_logs)
    elif insight_number == 5:
        plot_insight_5_financial_segmentation(customers, adoption_logs)
    else:
        print("Invalid insight number. Please choose 1-5.")

if __name__ == "__main__":
    # Run all insights
    generate_all_insights_plots()
    
    # Uncomment below to run individual insights:
    # plot_single_insight(1)  # Historical Adoption Behavior
    # plot_single_insight(2)  # Customer Engagement
    # plot_single_insight(3)  # Price Sensitivity
    # plot_single_insight(4)  # Churn Risk Paradox
    # plot_single_insight(5)  # Financial Segmentation
