#!/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_data(filename):
    """Load data from CSV file."""
    return pd.read_csv(filename)

def analyze_performance(data):
    """Analyze model performance metrics."""
    accuracy = data['accuracy'].mean()
    precision = data['precision'].mean()
    recall = data['recall'].mean()
    return accuracy, precision, recall

if __name__ == "__main__":
    data = load_data("results.csv")
    metrics = analyze_performance(data)
    print(f"Performance: {metrics}")