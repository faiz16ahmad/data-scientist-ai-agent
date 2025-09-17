import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from typing import Dict, Any, Optional, List, Union
import os
import tempfile
from pathlib import Path

class DataProcessor:
    """Utility class for data processing operations"""
    
    @staticmethod
    def load_data(file_path: str) -> pd.DataFrame:
        """Load data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Loaded pandas DataFrame
        """
        return pd.read_csv(file_path)
    
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a summary of the DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary containing various summary statistics
        """
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "summary_stats": df.describe(include='all').to_dict()
        }
    
    @staticmethod
    def filter_data(
        df: pd.DataFrame, 
        column: str, 
        operator: str, 
        value: Union[str, int, float]
    ) -> pd.DataFrame:
        """Filter DataFrame based on a condition.
        
        Args:
            df: Input DataFrame
            column: Column to filter on
            operator: Comparison operator ('==', '>', '<', '>=', '<=', '!=')
            value: Value to compare against
            
        Returns:
            Filtered DataFrame
        """
        if operator == '==':
            return df[df[column] == value]
        elif operator == '>':
            return df[df[column] > value]
        elif operator == '<':
            return df[df[column] < value]
        elif operator == '>=':
            return df[df[column] >= value]
        elif operator == '<=':
            return df[df[column] <= value]
        elif operator == '!=':
            return df[df[column] != value]
        else:
            raise ValueError(f"Unsupported operator: {operator}")


class VisualizationEngine:
    """Utility class for creating interactive Plotly visualizations"""
    
    @staticmethod
    def create_plot(
        df: pd.DataFrame,
        plot_type: str,
        x: Optional[str] = None,
        y: Optional[str] = None,
        color: Optional[str] = None,
        title: str = "",
        **kwargs
    ):
        """Create an interactive Plotly plot.
        
        Args:
            df: Input DataFrame
            plot_type: Type of plot to create ('bar', 'line', 'scatter', 'hist', 'box', 'violin', 'heatmap')
            x: Column to use for x-axis
            y: Column to use for y-axis
            color: Column to use for color encoding
            title: Plot title
            **kwargs: Additional keyword arguments for the plot
            
        Returns:
            Plotly figure object
        """
        
        if plot_type == 'bar':
            fig = px.bar(df, x=x, y=y, color=color, title=title, **kwargs)
        elif plot_type == 'line':
            fig = px.line(df, x=x, y=y, color=color, title=title, **kwargs)
        elif plot_type == 'scatter':
            fig = px.scatter(df, x=x, y=y, color=color, title=title, **kwargs)
        elif plot_type == 'hist':
            fig = px.histogram(df, x=x, color=color, title=title, **kwargs)
        elif plot_type == 'box':
            fig = px.box(df, x=x, y=y, color=color, title=title, **kwargs)
        elif plot_type == 'violin':
            fig = px.violin(df, x=x, y=y, color=color, title=title, **kwargs)
        elif plot_type == 'heatmap':
            if x and y:
                # Pivot table for heatmap
                pivot_df = df.pivot_table(values=color or df.select_dtypes(include=['number']).columns[0], 
                                        index=y, columns=x, aggfunc='mean')
                fig = px.imshow(pivot_df, title=title, **kwargs)
            else:
                # Correlation heatmap
                corr_matrix = df.select_dtypes(include=['number']).corr()
                fig = px.imshow(corr_matrix, title=title or "Correlation Matrix", **kwargs)
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")
        
        # Update layout for better appearance
        fig.update_layout(
            title_x=0.5,  # Center title
            showlegend=True if color else False,
            template="plotly_white"
        )
        
        return fig
    
    @staticmethod
    def get_supported_plot_types() -> List[str]:
        """Get a list of supported plot types.
        
        Returns:
            List of supported plot types
        """
        return [
            'bar', 'line', 'scatter', 
            'hist', 'box', 'violin', 'heatmap'
        ]


def clean_temp_files():
    """Clean up temporary files created by the application."""
    temp_dir = Path(tempfile.gettempdir()) / "data_scientist_agent"
    if temp_dir.exists():
        for file in temp_dir.glob("*.png"):
            try:
                file.unlink()
            except Exception as e:
                print(f"Error deleting {file}: {e}")
