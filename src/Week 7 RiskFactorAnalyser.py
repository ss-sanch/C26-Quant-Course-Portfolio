import numpy as np
import pandas as pd

class RiskFactorAnalyzer:
    """
    Analyzes portfolio risk factors using Eigen Decomposition to prevent 
    highly correlated strategy blow-ups during regime shifts.
    """
    def __init__(self, variance_threshold=0.65):
        # If one factor explains more than 65% of variance, the portfolio is too concentrated.
        self.variance_threshold = variance_threshold

    def calculate_covariance_matrix(self, strategy_returns: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the covariance matrix of returns across different strategies.
        """
        return strategy_returns.cov()

    def perform_eigen_decomposition(self, cov_matrix: pd.DataFrame):
        """
        Decomposes the covariance matrix to find underlying risk factors.
        Returns eigenvalues (magnitude of risk) and eigenvectors (direction of risk).
        """
        # Using eigh since covariance matrices are symmetric
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        
        # Sort them in descending order (largest risk factor first)
        sorted_indices = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[sorted_indices]
        eigenvectors = eigenvectors[:, sorted_indices]
        
        return eigenvalues, eigenvectors

    def check_concentration_risk(self, strategy_returns: pd.DataFrame) -> dict:
        """
        Evaluates if the portfolio is overly exposed to a single principal component.
        """
        cov_matrix = self.calculate_covariance_matrix(strategy_returns)
        eigenvalues, _ = self.perform_eigen_decomposition(cov_matrix)
        
        total_variance = np.sum(eigenvalues)
        explained_variances = eigenvalues / total_variance
        
        # The largest eigenvalue represents the dominant market factor (e.g., overall market direction)
        dominant_factor_risk = explained_variances[0]
        
        is_dangerously_concentrated = dominant_factor_risk > self.variance_threshold
        
        return {
            "dominant_factor_variance": dominant_factor_risk,
            "is_concentrated": is_dangerously_concentrated,
            "warning": "CRITICAL: Portfolio heavily exposed to a single risk factor. Reduce correlation." if is_dangerously_concentrated else "Risk factors are adequately diversified."
        }
