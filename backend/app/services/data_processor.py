"""
Data Processing Service

This service handles large dataset processing, transformations, and feature extraction.
It uses Polars for high-performance data processing.
"""

import asyncio
import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import polars as pl
import structlog

from app.core.config import settings
from app.core.logger import get_logger
from app.models.dataset import Dataset, DatasetStatus, DatasetType

logger = get_logger(__name__)


class DataProcessor:
    """
    High-performance data processing service for crisis prediction.
    
    Features:
    - Process large CSV, JSON, Parquet, and Excel files
    - Chunked processing for memory efficiency
    - Feature engineering and data cleaning
    - Parallel processing support
    - Progress tracking
    """
    
    def __init__(self):
        """Initialize the data processor."""
        self.chunk_size = settings.CHUNK_SIZE
        self.max_memory_usage = settings.MAX_MEMORY_USAGE
        self.temp_dir = Path(tempfile.gettempdir())
        
    async def process_file(
        self,
        file_path: str,
        dataset_type: DatasetType = DatasetType.RAW,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a data file and extract key information.
        
        Args:
            file_path: Path to the file to process
            dataset_type: Type of dataset
            config: Processing configuration
            
        Returns:
            Dict: Processing results with statistics and metadata
        """
        logger.info("Starting data processing", file_path=file_path)
        
        start_time = datetime.now()
        result = {
            "success": False,
            "file_path": file_path,
            "dataset_type": dataset_type,
            "start_time": start_time.isoformat(),
            "end_time": None,
            "processing_time": 0.0,
            "row_count": 0,
            "column_count": 0,
            "file_size": 0,
            "memory_usage": 0.0,
            "columns": [],
            "data_types": {},
            "statistics": {},
            "issues": [],
            "error": None,
        }
        
        try:
            # Get file info
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                result["file_size"] = file_path_obj.stat().st_size
            
            # Process based on file type
            file_extension = file_path_obj.suffix.lower()
            
            if file_extension == ".csv":
                processing_result = await self._process_csv(file_path, config)
            elif file_extension == ".json":
                processing_result = await self._process_json(file_path, config)
            elif file_extension == ".parquet":
                processing_result = await self._process_parquet(file_path, config)
            elif file_extension in [".xlsx", ".xls"]:
                processing_result = await self._process_excel(file_path, config)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Merge results
            result.update(processing_result)
            result["success"] = True
            
        except Exception as e:
            logger.error("Data processing failed", error=str(e), file_path=file_path)
            result["error"] = str(e)
            result["success"] = False
            
        finally:
            result["end_time"] = datetime.now().isoformat()
            result["processing_time"] = (datetime.now() - start_time).total_seconds()
            
        logger.info("Data processing completed", 
                   file_path=file_path, 
                   success=result["success"],
                   processing_time=result["processing_time"])
        
        return result
    
    async def _process_csv(
        self,
        file_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process CSV file."""
        logger.info("Processing CSV file", file_path=file_path)
        
        # Use polars for efficient CSV reading
        df = pl.scan_csv(file_path)
        
        # Get schema info
        schema = df.schema
        columns = list(schema.keys())
        data_types = {col: str(dtype) for col, dtype in schema.items()}
        
        # Collect the data to get row count and basic stats
        collected_df = df.collect()
        row_count = collected_df.height
        column_count = collected_df.width
        
        # Calculate basic statistics for numeric columns
        statistics = self._calculate_statistics(collected_df, columns, data_types)
        
        return {
            "row_count": row_count,
            "column_count": column_count,
            "columns": columns,
            "data_types": data_types,
            "statistics": statistics,
            "memory_usage": collected_df.estimated_size("mb"),
        }
    
    async def _process_json(
        self,
        file_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process JSON file."""
        logger.info("Processing JSON file", file_path=file_path)
        
        try:
            df = pl.read_ndjson(file_path)
            
            # Get schema info
            schema = df.schema
            columns = list(schema.keys())
            data_types = {col: str(dtype) for col, dtype in schema.items()}
            
            row_count = df.height
            column_count = df.width
            
            # Calculate basic statistics
            statistics = self._calculate_statistics(df, columns, data_types)
            
            return {
                "row_count": row_count,
                "column_count": column_count,
                "columns": columns,
                "data_types": data_types,
                "statistics": statistics,
                "memory_usage": df.estimated_size("mb"),
            }
        except Exception as e:
            # Try reading as regular JSON and convert to DataFrame
            logger.warning("NDJSON read failed, trying regular JSON", error=str(e))
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pl.DataFrame(data)
            elif isinstance(data, dict):
                # Handle nested JSON
                df = pl.DataFrame([data])
            else:
                raise ValueError(f"Invalid JSON format: {type(data)}")
            
            schema = df.schema
            columns = list(schema.keys())
            data_types = {col: str(dtype) for col, dtype in schema.items()}
            
            row_count = df.height
            column_count = df.width
            
            statistics = self._calculate_statistics(df, columns, data_types)
            
            return {
                "row_count": row_count,
                "column_count": column_count,
                "columns": columns,
                "data_types": data_types,
                "statistics": statistics,
                "memory_usage": df.estimated_size("mb"),
            }
    
    async def _process_parquet(
        self,
        file_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process Parquet file."""
        logger.info("Processing Parquet file", file_path=file_path)
        
        df = pl.read_parquet(file_path)
        
        # Get schema info
        schema = df.schema
        columns = list(schema.keys())
        data_types = {col: str(dtype) for col, dtype in schema.items()}
        
        row_count = df.height
        column_count = df.width
        
        # Calculate basic statistics
        statistics = self._calculate_statistics(df, columns, data_types)
        
        return {
            "row_count": row_count,
            "column_count": column_count,
            "columns": columns,
            "data_types": data_types,
            "statistics": statistics,
            "memory_usage": df.estimated_size("mb"),
        }
    
    async def _process_excel(
        self,
        file_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process Excel file."""
        logger.info("Processing Excel file", file_path=file_path)
        
        df = pl.read_excel(file_path)
        
        # Get schema info
        schema = df.schema
        columns = list(schema.keys())
        data_types = {col: str(dtype) for col, dtype in schema.items()}
        
        row_count = df.height
        column_count = df.width
        
        # Calculate basic statistics
        statistics = self._calculate_statistics(df, columns, data_types)
        
        return {
            "row_count": row_count,
            "column_count": column_count,
            "columns": columns,
            "data_types": data_types,
            "statistics": statistics,
            "memory_usage": df.estimated_size("mb"),
        }
    
    def _calculate_statistics(
        self,
        df: pl.DataFrame,
        columns: List[str],
        data_types: Dict[str, str]
    ) -> Dict[str, Any]:
        """Calculate basic statistics for the dataset."""
        statistics = {}
        
        for col in columns:
            col_stats = {}
            dtype = data_types.get(col, "unknown")
            
            try:
                if "int" in dtype or "float" in dtype:
                    # Numeric column
                    col_data = df[col]
                    col_stats["type"] = "numeric"
                    col_stats["min"] = float(col_data.min())
                    col_stats["max"] = float(col_data.max())
                    col_stats["mean"] = float(col_data.mean())
                    col_stats["median"] = float(col_data.median())
                    col_stats["std"] = float(col_data.std())
                    col_stats["null_count"] = int(col_data.null_count())
                    col_stats["non_null_count"] = int(col_data.count())
                    
                    # Check for outliers
                    q1 = col_data.quantile(0.25, method="linear")
                    q3 = col_data.quantile(0.75, method="linear")
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = col_data.filter((col_data < lower_bound) | (col_data > upper_bound)).len()
                    col_stats["outliers"] = int(outliers)
                    
                elif "str" in dtype or "utf" in dtype:
                    # String column
                    col_data = df[col]
                    col_stats["type"] = "string"
                    col_stats["unique_count"] = int(col_data.n_unique())
                    col_stats["null_count"] = int(col_data.null_count())
                    col_stats["non_null_count"] = int(col_data.count())
                    
                    # Get most common values
                    if col_data.null_count() < col_data.len():
                        value_counts = col_data.value_counts()
                        if len(value_counts) > 0:
                            col_stats["most_common"] = value_counts[0][0]
                            col_stats["most_common_count"] = int(value_counts[0][1])
                    
                elif "bool" in dtype:
                    # Boolean column
                    col_data = df[col]
                    col_stats["type"] = "boolean"
                    col_stats["true_count"] = int(col_data.sum())
                    col_stats["false_count"] = int(col_data.len() - col_data.sum() - col_data.null_count())
                    col_stats["null_count"] = int(col_data.null_count())
                    
                elif "datetime" in dtype or "date" in dtype:
                    # Date/time column
                    col_data = df[col]
                    col_stats["type"] = "datetime"
                    col_stats["min"] = str(col_data.min())
                    col_stats["max"] = str(col_data.max())
                    col_stats["null_count"] = int(col_data.null_count())
                    col_stats["non_null_count"] = int(col_data.count())
                
                else:
                    # Unknown type - get basic info
                    col_data = df[col]
                    col_stats["type"] = dtype
                    col_stats["null_count"] = int(col_data.null_count())
                    col_stats["non_null_count"] = int(col_data.count())
                    
            except Exception as e:
                logger.warning("Failed to calculate statistics for column", 
                              column=col, error=str(e))
                col_stats["error"] = str(e)
            
            statistics[col] = col_stats
        
        return statistics
    
    async def process_chunked(
        self,
        file_path: str,
        chunk_size: int = None,
        callback: callable = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a large file in chunks to avoid memory issues.
        
        Args:
            file_path: Path to the file to process
            chunk_size: Number of rows per chunk
            callback: Function to call for each chunk
            config: Processing configuration
            
        Returns:
            Dict: Processing summary
        """
        if chunk_size is None:
            chunk_size = self.chunk_size
        
        logger.info("Processing file in chunks", 
                   file_path=file_path, 
                   chunk_size=chunk_size)
        
        file_path_obj = Path(file_path)
        file_extension = file_path_obj.suffix.lower()
        
        total_rows = 0
        total_chunks = 0
        issues = []
        
        try:
            if file_extension == ".csv":
                # Process CSV in chunks
                for chunk in pl.read_csv_batch(file_path, batch_size=chunk_size):
                    total_rows += chunk.height
                    total_chunks += 1
                    
                    if callback:
                        try:
                            await callback(chunk, total_chunks)
                        except Exception as e:
                            issues.append(f"Chunk {total_chunks} callback failed: {str(e)}")
            else:
                raise ValueError(f"Chunked processing not supported for {file_extension}")
            
        except Exception as e:
            logger.error("Chunked processing failed", error=str(e))
            issues.append(f"Processing failed: {str(e)}")
        
        return {
            "total_rows": total_rows,
            "total_chunks": total_chunks,
            "chunk_size": chunk_size,
            "issues": issues,
        }
    
    async def clean_data(
        self,
        df: Union[pl.DataFrame, pd.DataFrame],
        config: Optional[Dict[str, Any]] = None
    ) -> Union[pl.DataFrame, pd.DataFrame]:
        """
        Clean the dataset by handling missing values, duplicates, and outliers.
        
        Args:
            df: Input dataframe (Polars or Pandas)
            config: Cleaning configuration
            
        Returns:
            Cleaned dataframe
        """
        logger.info("Cleaning dataset")
        
        is_polars = isinstance(df, pl.DataFrame)
        
        if config is None:
            config = {}
        
        try:
            # Handle missing values
            missing_strategy = config.get("missing_strategy", "drop")
            
            if missing_strategy == "drop":
                if is_polars:
                    df = df.drop_nulls()
                else:
                    df = df.dropna()
            elif missing_strategy == "fill":
                fill_value = config.get("fill_value", 0)
                if is_polars:
                    df = df.fill_null(fill_value)
                else:
                    df = df.fillna(fill_value)
            
            # Remove duplicates
            if config.get("remove_duplicates", True):
                if is_polars:
                    df = df.unique()
                else:
                    df = df.drop_duplicates()
            
            # Handle outliers (for numeric columns)
            if config.get("handle_outliers", False):
                numeric_cols = config.get("numeric_columns", [])
                for col in numeric_cols:
                    if col in (df.columns if is_polars else df.columns):
                        if is_polars:
                            q1 = df[col].quantile(0.25, method="linear")
                            q3 = df[col].quantile(0.75, method="linear")
                            iqr = q3 - q1
                            lower_bound = q1 - 1.5 * iqr
                            upper_bound = q3 + 1.5 * iqr
                            df = df.with_columns(
                                pl.when(pl.col(col) < lower_bound)
                                    .then(lower_bound)
                                    .when(pl.col(col) > upper_bound)
                                    .then(upper_bound)
                                    .otherwise(pl.col(col))
                                    .alias(col)
                            )
                        else:
                            q1 = df[col].quantile(0.25)
                            q3 = df[col].quantile(0.75)
                            iqr = q3 - q1
                            lower_bound = q1 - 1.5 * iqr
                            upper_bound = q3 + 1.5 * iqr
                            df[col] = df[col].clip(lower_bound, upper_bound)
            
            # Standardize column names
            if config.get("standardize_columns", True):
                if is_polars:
                    df = df.rename({
                        col: col.lower().replace(" ", "_").replace("-", "_")
                        for col in df.columns
                    })
                else:
                    df.columns = [
                        col.lower().replace(" ", "_").replace("-", "_")
                        for col in df.columns
                    ]
            
        except Exception as e:
            logger.error("Data cleaning failed", error=str(e))
            raise
        
        return df
    
    async def extract_features(
        self,
        df: Union[pl.DataFrame, pd.DataFrame],
        config: Optional[Dict[str, Any]] = None
    ) -> Union[pl.DataFrame, pd.DataFrame]:
        """
        Extract features from the dataset for ML modeling.
        
        Args:
            df: Input dataframe
            config: Feature extraction configuration
            
        Returns:
            Dataframe with extracted features
        """
        logger.info("Extracting features from dataset")
        
        if config is None:
            config = {}
        
        is_polars = isinstance(df, pl.DataFrame)
        
        try:
            # Example feature extraction operations
            # This would be customized based on your specific crisis prediction needs
            
            # 1. Create interaction features
            if config.get("create_interactions", False):
                numeric_cols = config.get("numeric_columns", [])
                for i, col1 in enumerate(numeric_cols):
                    for col2 in numeric_cols[i+1:]:
                        if is_polars:
                            df = df.with_columns(
                                (pl.col(col1) * pl.col(col2)).alias(f"{col1}_x_{col2}")
                            )
                        else:
                            df[f"{col1}_x_{col2}"] = df[col1] * df[col2]
            
            # 2. Create time-based features (if datetime columns exist)
            datetime_cols = config.get("datetime_columns", [])
            for col in datetime_cols:
                if col in (df.columns if is_polars else df.columns):
                    if is_polars:
                        df = df.with_columns(
                            pl.col(col).dt.year().alias(f"{col}_year"),
                            pl.col(col).dt.month().alias(f"{col}_month"),
                            pl.col(col).dt.day().alias(f"{col}_day"),
                            pl.col(col).dt.hour().alias(f"{col}_hour"),
                            pl.col(col).dt.day_of_week().alias(f"{col}_dow"),
                        )
                    else:
                        df[f"{col}_year"] = df[col].dt.year
                        df[f"{col}_month"] = df[col].dt.month
                        df[f"{col}_day"] = df[col].dt.day
                        df[f"{col}_hour"] = df[col].dt.hour
                        df[f"{col}_dow"] = df[col].dt.dayofweek
            
            # 3. Create aggregation features
            if config.get("create_aggregations", False):
                group_cols = config.get("group_columns", [])
                for group_col in group_cols:
                    if group_col in (df.columns if is_polars else df.columns):
                        numeric_cols = config.get("numeric_columns", [])
                        for numeric_col in numeric_cols:
                            if numeric_col in (df.columns if is_polars else df.columns):
                                if is_polars:
                                    # For Polars, we'd need to use group_by and aggregations
                                    # This is simplified for the example
                                    pass
                                else:
                                    # Create group aggregates as new columns
                                    grouped = df.groupby(group_col)[numeric_col]
                                    df[f"{group_col}_{numeric_col}_mean"] = df[group_col].map(grouped.mean())
                                    df[f"{group_col}_{numeric_col}_std"] = df[group_col].map(grouped.std())
            
        except Exception as e:
            logger.error("Feature extraction failed", error=str(e))
            raise
        
        return df
    
    async def save_processed_data(
        self,
        df: Union[pl.DataFrame, pd.DataFrame],
        output_path: str,
        format: str = "parquet"
    ) -> str:
        """
        Save processed data to file.
        
        Args:
            df: Dataframe to save
            output_path: Output file path
            format: File format (csv, json, parquet)
            
        Returns:
            Path to saved file
        """
        logger.info("Saving processed data", output_path=output_path, format=format)
        
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if isinstance(df, pl.DataFrame):
                if format == "csv":
                    df.write_csv(output_path)
                elif format == "json":
                    df.write_ndjson(output_path)
                elif format == "parquet":
                    df.write_parquet(output_path)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            else:  # pandas
                if format == "csv":
                    df.to_csv(output_path, index=False)
                elif format == "json":
                    df.to_json(output_path, orient="records", lines=True)
                elif format == "parquet":
                    df.to_parquet(output_path)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            logger.error("Failed to save processed data", 
                        error=str(e), 
                        output_path=output_path)
            raise
        
        return output_path