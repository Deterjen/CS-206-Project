import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def load_and_explore_data(file_path):
    """Load preprocessing and provide basic statistics"""
    # Load preprocessing
    df = pd.read_csv(file_path)

    # Basic information
    print(f"Dataset shape: {df.shape}")
    print("\nFirst 5 rows:")
    print(df.head())

    # Data types and missing values
    print("\nData types and missing values:")
    missing_data = pd.DataFrame({
        'Data Type': df.dtypes,
        'Missing Values': df.isnull().sum(),
        'Missing Percentage': (df.isnull().sum() / len(df) * 100).round(2)
    })
    print(missing_data)

    # Statistical summary for numerical columns
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numerical_cols) > 0:
        print("\nStatistical summary for numerical columns:")
        print(df[numerical_cols].describe())

    return df


def visualize_distributions(df):
    """Visualize distributions of numerical features"""
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns

    if len(numerical_cols) == 0:
        print("No numerical columns to visualize")
        return

    # Create distribution plots
    n_cols = min(3, len(numerical_cols))
    n_rows = (len(numerical_cols) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 4))
    axes = axes.flatten() if n_rows > 1 or n_cols > 1 else [axes]

    for i, col in enumerate(numerical_cols):
        if i < len(axes):
            sns.histplot(df[col].dropna(), kde=True, ax=axes[i])
            axes[i].set_title(f'Distribution of {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Frequency')

    # Hide unused subplots
    for j in range(len(numerical_cols), len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.savefig('feature_distributions.png')
    plt.close()


def correlation_analysis(df):
    """Analyze and visualize correlations between features"""
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns

    if len(numerical_cols) < 2:
        print("Not enough numerical columns for correlation analysis")
        return

    # Calculate correlation matrix
    corr_matrix = df[numerical_cols].corr()

    # Visualize correlation matrix
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    sns.heatmap(corr_matrix, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
                annot=True, fmt=".2f", square=True, linewidths=.5)

    plt.title('Feature Correlation Matrix', fontsize=16)
    plt.tight_layout()
    plt.savefig('correlation_matrix.png')
    plt.close()

    # Find highly correlated features
    high_corr_threshold = 0.7
    high_corr_features = []

    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) >= high_corr_threshold:
                high_corr_features.append((corr_matrix.columns[i], corr_matrix.columns[j],
                                           corr_matrix.iloc[i, j]))

    if high_corr_features:
        print("\nHighly correlated features (|correlation| >= 0.7):")
        for feat1, feat2, corr in high_corr_features:
            print(f"{feat1} and {feat2}: {corr:.4f}")


def visualize_relationships(df, target_col=None):
    """Visualize relationships between features and target"""
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns

    if target_col is not None and target_col in df.columns:
        # If target column exists, create pairplots with target highlighting
        plot_cols = [col for col in numerical_cols if col != target_col][:5]  # Limit to 5 features
        if plot_cols:
            plt.figure(figsize=(15, 15))
            sns.pairplot(df[plot_cols + [target_col]], hue=target_col)
            plt.suptitle('Feature Relationships by Target', y=1.02, fontsize=16)
            plt.savefig('feature_relationships_by_target.png')
            plt.close()

            # Feature importance/correlation with target
            if df[target_col].nunique() > 10:  # Continuous target
                correlations = []
                for col in plot_cols:
                    valid_data = df[[col, target_col]].dropna()
                    if len(valid_data) > 1:
                        corr, p_value = pearsonr(valid_data[col], valid_data[target_col])
                        correlations.append((col, corr, p_value))

                correlations.sort(key=lambda x: abs(x[1]), reverse=True)

                plt.figure(figsize=(12, 6))
                feature_names = [x[0] for x in correlations]
                correlation_values = [x[1] for x in correlations]

                sns.barplot(x=correlation_values, y=feature_names)
                plt.title('Feature Correlation with Target Variable', fontsize=14)
                plt.xlabel('Pearson Correlation Coefficient')
                plt.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
                plt.tight_layout()
                plt.savefig('feature_importance.png')
                plt.close()

                print("\nFeature correlation with target variable:")
                for feature, corr, p_value in correlations:
                    significance = "significant" if p_value < 0.05 else "not significant"
                    print(f"{feature}: {corr:.4f} (p-value: {p_value:.4f}, {significance})")
    else:
        # If no target, create a pairplot of top numerical features
        plot_cols = list(numerical_cols)[:5]  # Limit to 5 features
        if len(plot_cols) > 1:
            plt.figure(figsize=(15, 15))
            sns.pairplot(df[plot_cols])
            plt.suptitle('Feature Relationships', y=1.02, fontsize=16)
            plt.savefig('feature_relationships.png')
            plt.close()


def dimensionality_reduction_visualization(df, target_col=None):
    """Use PCA to visualize high-dimensional preprocessing in 2D"""
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if target_col in numerical_cols:
        numerical_cols = [col for col in numerical_cols if col != target_col]

    if len(numerical_cols) < 3:
        print("Not enough numerical columns for PCA visualization")
        return

    # Handle missing values by using medians
    df_numeric = df[numerical_cols].copy()
    for col in df_numeric.columns:
        df_numeric[col] = df_numeric[col].fillna(df_numeric[col].median())

    # Standardize the preprocessing
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_numeric)

    # Apply PCA
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(scaled_data)

    # Create dataframe with principal components
    pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])

    # Explained variance
    explained_variance = pca.explained_variance_ratio_
    print(f"\nExplained variance by the first two principal components: {sum(explained_variance) * 100:.2f}%")
    print(f"PC1: {explained_variance[0] * 100:.2f}%")
    print(f"PC2: {explained_variance[1] * 100:.2f}%")

    # Get feature importance
    components_df = pd.DataFrame(
        pca.components_.T,
        columns=['PC1', 'PC2'],
        index=numerical_cols
    )

    # Visualize PCA results
    plt.figure(figsize=(12, 10))

    if target_col is not None and target_col in df.columns:
        # If there's a target column, color by target
        pca_df['target'] = df[target_col].values

        if df[target_col].nunique() <= 10:  # Categorical target
            plt.figure(figsize=(12, 10))
            sns.scatterplot(x='PC1', y='PC2', hue='target', data=pca_df, palette='viridis')
            plt.title('PCA: First Two Principal Components by Target Class', fontsize=16)
        else:  # Continuous target
            plt.figure(figsize=(12, 10))
            scatter = plt.scatter(pca_df['PC1'], pca_df['PC2'], c=pca_df['target'], cmap='viridis')
            plt.colorbar(scatter, label=target_col)
            plt.title('PCA: First Two Principal Components by Target Value', fontsize=16)
    else:
        # Without target, just show the distribution
        plt.figure(figsize=(12, 10))
        sns.scatterplot(x='PC1', y='PC2', data=pca_df)
        plt.title('PCA: First Two Principal Components', fontsize=16)

    plt.xlabel(f'Principal Component 1 ({explained_variance[0] * 100:.2f}%)', fontsize=14)
    plt.ylabel(f'Principal Component 2 ({explained_variance[1] * 100:.2f}%)', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('pca_visualization.png')
    plt.close()

    # Visualize feature contributions to principal components
    plt.figure(figsize=(14, 8))
    components_df = components_df.reset_index()
    components_df = pd.melt(components_df, id_vars=['index'],
                            value_vars=['PC1', 'PC2'],
                            var_name='Principal Component',
                            value_name='Contribution')

    sns.barplot(x='index', y='Contribution', hue='Principal Component', data=components_df)
    plt.xticks(rotation=90)
    plt.xlabel('Features', fontsize=14)
    plt.ylabel('Contribution', fontsize=14)
    plt.title('Feature Contributions to Principal Components', fontsize=16)
    plt.tight_layout()
    plt.savefig('pca_feature_contributions.png')
    plt.close()


def analyze_categorical_features(df, target_col=None):
    """Analyze categorical features and their relationship with target"""
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    if len(categorical_cols) == 0:
        print("No categorical columns to analyze")
        return

    print("\nCategorical feature distribution:")
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        print(f"\n{col} distribution:")
        print(value_counts.head(10))  # Show top 10 values
        if len(value_counts) > 10:
            print(f"...and {len(value_counts) - 10} more values")

        # Visualize distribution
        plt.figure(figsize=(12, 6))
        top_categories = value_counts.head(10).index
        plot_data = df[df[col].isin(top_categories)]

        sns.countplot(y=col, data=plot_data, order=top_categories)
        plt.title(f'Distribution of {col}', fontsize=14)
        plt.xlabel('Count', fontsize=12)
        plt.ylabel(col, fontsize=12)
        plt.tight_layout()
        plt.savefig(f'categorical_distribution_{col}.png')
        plt.close()

        # If target column exists and is numerical, analyze relationship
        if target_col is not None and target_col in df.columns:
            if df[target_col].dtype in ['int64', 'float64'] and df[target_col].nunique() > 10:
                plt.figure(figsize=(14, 8))
                sns.boxplot(x=col, y=target_col, data=plot_data, order=top_categories)
                plt.title(f'Relationship between {col} and {target_col}', fontsize=14)
                plt.xticks(rotation=90)
                plt.tight_layout()
                plt.savefig(f'categorical_relationship_{col}.png')
                plt.close()
            elif df[target_col].nunique() <= 10:
                # For categorical target, create a stacked bar chart
                plt.figure(figsize=(14, 8))
                crosstab = pd.crosstab(df[col], df[target_col], normalize='index')
                crosstab.plot(kind='bar', stacked=True)
                plt.title(f'Relationship between {col} and {target_col}', fontsize=14)
                plt.xlabel(col, fontsize=12)
                plt.ylabel('Proportion', fontsize=12)
                plt.legend(title=target_col)
                plt.tight_layout()
                plt.savefig(f'categorical_stacked_{col}.png')
                plt.close()


def main(file_path, target_column=None):
    """Main function to analyze preprocessing"""
    print("Starting preprocessing analysis...")
    df = load_and_explore_data(file_path)

    visualize_distributions(df)
    correlation_analysis(df)
    visualize_relationships(df, target_column)
    dimensionality_reduction_visualization(df, target_column)
    analyze_categorical_features(df, target_column)

    print("\nAnalysis complete. Visualizations saved.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Analyze and visualize preprocessing')
    parser.add_argument('file_path', default="analysis_ready_survey_data.csv", type=str, help='Path to the preprocessing file (CSV)')
    parser.add_argument('--target', type=str, default=None,
                        help='Target column name (if applicable)')

    args = parser.parse_args()
    main(args.file_path, args.target)
