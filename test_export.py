# Test Export Functionality - Kalkulator Cicilan & Bunga Pro

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import json

def test_export_functions():
    """Test all export functions"""
    
    # Test data
    test_input = {
        'Jumlah Pinjaman': 100000000,
        'Suku Bunga': 12.0,
        'Jangka Waktu': 5
    }
    
    test_results = {
        'Cicilan Bulanan': 2224444,
        'Total Pembayaran': 133466667,
        'Total Bunga': 33466667
    }
    
    test_schedule = pd.DataFrame({
        'Bulan': [1, 2, 3, 4, 5],
        'Cicilan': [2224444, 2224444, 2224444, 2224444, 2224444],
        'Pokok': [1224444, 1236667, 1249013, 1261482, 1274077],
        'Bunga': [1000000, 987777, 975431, 962962, 950367],
        'Sisa_Pokok': [98775556, 97538889, 96289876, 95028394, 93754317]
    })
    
    print("=== TESTING EXPORT FUNCTIONS ===")
    
    # Test create_export_data
    try:
        export_data = create_export_data("Test Calculator", test_input, test_results, test_schedule)
        print("✅ create_export_data: PASSED")
        print(f"   - Metadata: {export_data['metadata']['calculator_type']}")
        print(f"   - Export date: {export_data['metadata']['export_date']}")
    except Exception as e:
        print(f"❌ create_export_data: FAILED - {e}")
    
    # Test CSV export
    try:
        csv_data = export_to_csv(test_schedule, "test.csv")
        print("✅ export_to_csv: PASSED")
        print(f"   - CSV length: {len(csv_data)} characters")
    except Exception as e:
        print(f"❌ export_to_csv: FAILED - {e}")
    
    # Test JSON export
    try:
        json_data = export_to_json(export_data, "test.json")
        print("✅ export_to_json: PASSED")
        print(f"   - JSON length: {len(json_data)} characters")
    except Exception as e:
        print(f"❌ export_to_json: FAILED - {e}")
    
    # Test Excel export
    try:
        excel_data = export_to_excel(export_data, "test.xlsx")
        print("✅ export_to_excel: PASSED")
        print(f"   - Excel size: {len(excel_data)} bytes")
    except Exception as e:
        print(f"❌ export_to_excel: FAILED - {e}")
    
    # Test summary report
    try:
        summary = create_summary_report("Test Calculator", test_input, test_results)
        print("✅ create_summary_report: PASSED")
        print(f"   - Report length: {len(summary)} characters")
    except Exception as e:
        print(f"❌ create_summary_report: FAILED - {e}")
    
    print("\n=== TEST SUMMARY ===")
    print("All export functions have been tested!")
    print("Check the output above for any failures.")

if __name__ == "__main__":
    # This file is for testing purposes only
    # Import the functions from app.py first
    print("Export functionality test file created!")
    print("To test, run the functions from app.py in a Python environment.")
