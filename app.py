import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import math
import io
import json

# Page configuration
st.set_page_config(
    page_title="Kalkulator Cicilan & Bunga Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .info-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>💰 Kalkulator Cicilan & Bunga Pro</h1>
    <p>Simulasi Kredit Bank • Bunga Majemuk • Investasi Deposito • Cicilan Kendaraan & Properti</p>
</div>
""", unsafe_allow_html=True)

# Sidebar untuk navigasi
st.sidebar.title("🧮 Menu Kalkulator")
calculator_type = st.sidebar.selectbox(
    "Pilih Jenis Kalkulator:",
    ["Simulasi Kredit Bank", "Bunga Majemuk", "Investasi Deposito", "Cicilan Kendaraan", "Cicilan Properti", "Pinjaman Online/Fintech", "Perbandingan Skenario"]
)

def format_currency(amount):
    """Format angka menjadi format mata uang Indonesia"""
    return f"Rp {amount:,.0f}".replace(",", ".")

def calculate_loan_payment(principal, annual_rate, years):
    """Hitung cicilan bulanan dengan rumus anuitas"""
    monthly_rate = annual_rate / 12 / 100
    num_payments = years * 12
    
    if monthly_rate == 0:
        return principal / num_payments
    
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return monthly_payment

def generate_amortization_schedule(principal, annual_rate, years):
    """Generate tabel amortisasi"""
    monthly_rate = annual_rate / 12 / 100
    num_payments = years * 12
    monthly_payment = calculate_loan_payment(principal, annual_rate, years)
    
    schedule = []
    remaining_balance = principal
    
    for month in range(1, num_payments + 1):
        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        
        schedule.append({
            'Bulan': month,
            'Cicilan': monthly_payment,
            'Pokok': principal_payment,
            'Bunga': interest_payment,
            'Sisa_Pokok': max(0, remaining_balance)
        })
    
    return pd.DataFrame(schedule)

def compound_interest(principal, rate, time, compound_frequency=12):
    """Hitung bunga majemuk"""
    return principal * (1 + rate/100/compound_frequency) ** (compound_frequency * time)

def create_export_data(calculator_type, input_params, results, schedule_data=None):
    """Create comprehensive export data"""
    export_data = {
        'metadata': {
            'calculator_type': calculator_type,
            'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'app_version': '2.3',
            'disclaimer': 'Perhitungan ini bersifat estimasi. Konsultasikan dengan ahli keuangan untuk keputusan finansial.'
        },
        'input_parameters': input_params,
        'results': results,
        'schedule': schedule_data.to_dict('records') if schedule_data is not None else None
    }
    return export_data

def export_to_csv(data, filename):
    """Export data to CSV format"""
    output = io.StringIO()
    if isinstance(data, pd.DataFrame):
        data.to_csv(output, index=False)
    else:
        # Convert dict to DataFrame for CSV export
        df = pd.DataFrame([data])
        df.to_csv(output, index=False)
    
    output.seek(0)
    return output.getvalue()

def export_to_json(data, filename):
    """Export data to JSON format"""
    return json.dumps(data, indent=2, ensure_ascii=False)

def export_to_excel(data, filename):
    """Export data to Excel format"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if isinstance(data, dict):
            # Write metadata
            if 'metadata' in data:
                metadata_df = pd.DataFrame([data['metadata']])
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            # Write input parameters
            if 'input_parameters' in data:
                input_df = pd.DataFrame([data['input_parameters']])
                input_df.to_excel(writer, sheet_name='Input Parameters', index=False)
            
            # Write results
            if 'results' in data:
                results_df = pd.DataFrame([data['results']])
                results_df.to_excel(writer, sheet_name='Results', index=False)
            
            # Write schedule if available
            if 'schedule' in data and data['schedule']:
                schedule_df = pd.DataFrame(data['schedule'])
                schedule_df.to_excel(writer, sheet_name='Schedule', index=False)
        else:
            # Simple DataFrame export
            data.to_excel(writer, sheet_name='Data', index=False)
    
    output.seek(0)
    return output.getvalue()

def create_summary_report(calculator_type, input_params, results):
    """Create a summary report text"""
    report = f"""
=== LAPORAN KALKULATOR CICILAN & BUNGA PRO ===
Jenis Kalkulator: {calculator_type}
Tanggal: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

--- PARAMETER INPUT ---
"""
    
    for key, value in input_params.items():
        if isinstance(value, (int, float)):
            if 'amount' in key.lower() or 'price' in key.lower() or 'pinjaman' in key.lower():
                report += f"{key}: {format_currency(value)}\n"
            elif 'rate' in key.lower() or 'bunga' in key.lower():
                report += f"{key}: {value}%\n"
            else:
                report += f"{key}: {value}\n"
        else:
            report += f"{key}: {value}\n"
    
    report += "\n--- HASIL PERHITUNGAN ---\n"
    
    for key, value in results.items():
        if isinstance(value, (int, float)):
            if 'amount' in key.lower() or 'total' in key.lower() or 'cicilan' in key.lower():
                report += f"{key}: {format_currency(value)}\n"
            elif 'rate' in key.lower() or 'bunga' in key.lower():
                report += f"{key}: {value}%\n"
            else:
                report += f"{key}: {value}\n"
        else:
            report += f"{key}: {value}\n"
    
    report += f"""
--- DISCLAIMER ---
Perhitungan ini bersifat estimasi berdasarkan parameter yang diinput.
Suku bunga dan biaya dapat berubah sewaktu-waktu.
Untuk keputusan finansial yang tepat, konsultasikan dengan ahli keuangan.
Pastikan platform yang dipilih terdaftar dan diawasi oleh OJK.

Generated by: Kalkulator Cicilan & Bunga Pro v2.3
"""
    
    return report

# Main content berdasarkan pilihan
if calculator_type == "Simulasi Kredit Bank":
    st.header("🏦 Simulasi Kredit Bank")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameter")
        loan_amount = st.number_input("Jumlah Pinjaman (Rp)", min_value=1000000, value=100000000, step=1000000)
        interest_rate = st.slider("Suku Bunga Tahunan (%)", min_value=1.0, max_value=30.0, value=12.0, step=0.1)
        loan_term = st.slider("Jangka Waktu (Tahun)", min_value=1, max_value=30, value=5)
        
        # Pilihan jenis bunga
        interest_type = st.selectbox("Jenis Bunga", ["Anuitas (Tetap)", "Efektif (Menurun)"])
    
    with col2:
        st.subheader("Hasil Perhitungan")
        
        if interest_type == "Anuitas (Tetap)":
            monthly_payment = calculate_loan_payment(loan_amount, interest_rate, loan_term)
            total_payment = monthly_payment * loan_term * 12
            total_interest = total_payment - loan_amount
            
            st.metric("Cicilan Bulanan", format_currency(monthly_payment))
            st.metric("Total Pembayaran", format_currency(total_payment))
            st.metric("Total Bunga", format_currency(total_interest))
            st.metric("Rasio Bunga", f"{(total_interest/loan_amount)*100:.1f}%")
        
        else:  # Efektif (Menurun)
            monthly_rate = interest_rate / 12 / 100
            num_payments = loan_term * 12
            principal_payment = loan_amount / num_payments
            
            # Hitung cicilan pertama dan terakhir
            first_payment = principal_payment + (loan_amount * monthly_rate)
            last_payment = principal_payment + (principal_payment * monthly_rate)
            
            # Hitung total bunga dengan rumus deret aritmatika
            total_interest = (loan_amount * monthly_rate * num_payments) - (principal_payment * monthly_rate * (num_payments - 1) * num_payments / 2)
            total_payment = loan_amount + total_interest
            
            st.metric("Cicilan Pertama", format_currency(first_payment))
            st.metric("Cicilan Terakhir", format_currency(last_payment))
            st.metric("Total Pembayaran", format_currency(total_payment))
            st.metric("Total Bunga", format_currency(total_interest))
    
    # Grafik dan tabel amortisasi
    st.subheader("📊 Analisis Pembayaran")
    
    if interest_type == "Anuitas (Tetap)":
        df_schedule = generate_amortization_schedule(loan_amount, interest_rate, loan_term)
        
        # Grafik komposisi pembayaran
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_schedule['Bulan'],
            y=df_schedule['Pokok'],
            mode='lines',
            name='Pembayaran Pokok',
            fill='tonexty'
        ))
        fig.add_trace(go.Scatter(
            x=df_schedule['Bulan'],
            y=df_schedule['Bunga'],
            mode='lines',
            name='Pembayaran Bunga',
            fill='tozeroy'
        ))
        fig.update_layout(
            title="Komposisi Pembayaran Bulanan",
            xaxis_title="Bulan",
            yaxis_title="Jumlah (Rp)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabel amortisasi (10 baris pertama)
        st.subheader("Tabel Amortisasi (10 Bulan Pertama)")
        df_display = df_schedule.head(10).copy()
        df_display['Cicilan'] = df_display['Cicilan'].apply(format_currency)
        df_display['Pokok'] = df_display['Pokok'].apply(format_currency)
        df_display['Bunga'] = df_display['Bunga'].apply(format_currency)
        df_display['Sisa_Pokok'] = df_display['Sisa_Pokok'].apply(format_currency)
        st.dataframe(df_display, use_container_width=True)
        
        # Export functionality for Bank Credit Calculator
        st.subheader("📥 Export Data")
        col_export1, col_export2, col_export3 = st.columns(3)
        
        # Prepare export data
        input_params = {
            'Jumlah Pinjaman': loan_amount,
            'Suku Bunga Tahunan': interest_rate,
            'Jangka Waktu': loan_term,
            'Jenis Bunga': interest_type
        }
        
        results = {
            'Cicilan Bulanan': monthly_payment,
            'Total Pembayaran': total_payment,
            'Total Bunga': total_interest,
            'Rasio Bunga': f"{(total_interest/loan_amount)*100:.1f}%"
        }
        
        export_data = create_export_data("Simulasi Kredit Bank", input_params, results, df_schedule)
        
        with col_export1:
            # CSV Export
            csv_data = export_to_csv(df_schedule, "amortization_schedule.csv")
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"kredit_bank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_export2:
            # Excel Export
            excel_data = export_to_excel(export_data, "kredit_bank_analysis.xlsx")
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name=f"kredit_bank_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col_export3:
            # Summary Report
            summary_report = create_summary_report("Simulasi Kredit Bank", input_params, results)
            st.download_button(
                label="📋 Download Report",
                data=summary_report,
                file_name=f"kredit_bank_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

elif calculator_type == "Bunga Majemuk":
    st.header("📈 Kalkulator Bunga Majemuk")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameter")
        principal = st.number_input("Modal Awal (Rp)", min_value=100000, value=10000000, step=100000)
        annual_rate = st.slider("Suku Bunga Tahunan (%)", min_value=1.0, max_value=30.0, value=10.0, step=0.1)
        years = st.slider("Jangka Waktu (Tahun)", min_value=1, max_value=50, value=10)
        compound_freq = st.selectbox("Frekuensi Bunga", [1, 2, 4, 12], format_func=lambda x: {1: "Tahunan", 2: "6 Bulanan", 4: "Kuartalan", 12: "Bulanan"}[x])
        
        # Tambahan setoran berkala
        additional_payment = st.number_input("Setoran Berkala (Rp)", min_value=0, value=0, step=100000)
        payment_frequency = st.selectbox("Frekuensi Setoran", ["Bulanan", "Kuartalan", "Tahunan"])
    
    with col2:
        st.subheader("Hasil Perhitungan")
        
        final_amount = compound_interest(principal, annual_rate, years, compound_freq)
        
        # Hitung dengan setoran berkala jika ada
        if additional_payment > 0:
            payment_per_year = {"Bulanan": 12, "Kuartalan": 4, "Tahunan": 1}[payment_frequency]
            # Rumus anuitas untuk setoran berkala
            r = annual_rate / 100 / payment_per_year
            n = years * payment_per_year
            future_value_annuity = additional_payment * (((1 + r)**n - 1) / r)
            final_amount += future_value_annuity
        
        total_interest = final_amount - principal - (additional_payment * years * {"Bulanan": 12, "Kuartalan": 4, "Tahunan": 1}.get(payment_frequency, 0))
        
        st.metric("Nilai Akhir", format_currency(final_amount))
        st.metric("Total Bunga", format_currency(total_interest))
        st.metric("Pertumbuhan", f"{((final_amount/principal - 1) * 100):.1f}%")
        st.metric("Rata-rata Return/Tahun", f"{(((final_amount/principal)**(1/years) - 1) * 100):.1f}%")
    
    # Grafik pertumbuhan
    st.subheader("📊 Grafik Pertumbuhan")
    
    years_range = list(range(years + 1))
    amounts = []
    
    for year in years_range:
        amount = compound_interest(principal, annual_rate, year, compound_freq)
        if additional_payment > 0:
            payment_per_year = {"Bulanan": 12, "Kuartalan": 4, "Tahunan": 1}[payment_frequency]
            if year > 0:
                r = annual_rate / 100 / payment_per_year
                n = year * payment_per_year
                future_value_annuity = additional_payment * (((1 + r)**n - 1) / r)
                amount += future_value_annuity
        amounts.append(amount)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years_range,
        y=amounts,
        mode='lines+markers',
        name='Nilai Investasi',
        line=dict(color='#667eea', width=3)
    ))
    fig.update_layout(
        title="Pertumbuhan Investasi dengan Bunga Majemuk",
        xaxis_title="Tahun",
        yaxis_title="Nilai (Rp)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Export functionality for Compound Interest Calculator
    st.subheader("📥 Export Data")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    # Prepare export data
    input_params = {
        'Modal Awal': principal,
        'Suku Bunga Tahunan': annual_rate,
        'Jangka Waktu': years,
        'Frekuensi Bunga': compound_freq,
        'Setoran Berkala': additional_payment,
        'Frekuensi Setoran': payment_frequency
    }
    
    results = {
        'Nilai Akhir': final_amount,
        'Total Bunga': total_interest,
        'Pertumbuhan': f"{((final_amount/principal - 1) * 100):.1f}%",
        'Rata-rata Return/Tahun': f"{(((final_amount/principal)**(1/years) - 1) * 100):.1f}%"
    }
    
    # Create growth schedule DataFrame
    growth_schedule = pd.DataFrame({
        'Tahun': years_range,
        'Nilai Investasi': amounts,
        'Bunga Kumulatif': [amount - principal - (additional_payment * year * {"Bulanan": 12, "Kuartalan": 4, "Tahunan": 1}.get(payment_frequency, 0)) for year, amount in zip(years_range, amounts)]
    })
    
    export_data = create_export_data("Bunga Majemuk", input_params, results, growth_schedule)
    
    with col_export1:
        # CSV Export
        csv_data = export_to_csv(growth_schedule, "compound_interest_growth.csv")
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"bunga_majemuk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_export2:
        # Excel Export
        excel_data = export_to_excel(export_data, "bunga_majemuk_analysis.xlsx")
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"bunga_majemuk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_export3:
        # Summary Report
        summary_report = create_summary_report("Bunga Majemuk", input_params, results)
        st.download_button(
            label="📋 Download Report",
            data=summary_report,
            file_name=f"bunga_majemuk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

elif calculator_type == "Investasi Deposito":
    st.header("🏛️ Kalkulator Investasi Deposito")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameter")
        deposit_amount = st.number_input("Jumlah Deposito (Rp)", min_value=1000000, value=50000000, step=1000000)
        deposit_rate = st.slider("Suku Bunga Deposito (%)", min_value=1.0, max_value=15.0, value=6.0, step=0.1)
        deposit_term = st.selectbox("Jangka Waktu Deposito", [1, 3, 6, 12, 24, 36], format_func=lambda x: f"{x} Bulan")
        tax_rate = st.slider("Pajak Bunga (%)", min_value=0.0, max_value=25.0, value=20.0, step=0.1)
        
        # Auto Roll Over
        auto_rollover = st.checkbox("Auto Roll Over")
        if auto_rollover:
            rollover_times = st.slider("Jumlah Roll Over", min_value=1, max_value=10, value=3)
        else:
            rollover_times = 1
    
    with col2:
        st.subheader("Hasil Perhitungan")
        
        # Hitung bunga deposito
        monthly_rate = deposit_rate / 12 / 100
        gross_interest = deposit_amount * monthly_rate * deposit_term
        tax_amount = gross_interest * tax_rate / 100
        net_interest = gross_interest - tax_amount
        
        # Dengan auto rollover
        if auto_rollover:
            total_amount = deposit_amount
            total_net_interest = 0
            total_tax = 0
            
            for i in range(rollover_times):
                period_interest = total_amount * monthly_rate * deposit_term
                period_tax = period_interest * tax_rate / 100
                period_net_interest = period_interest - period_tax
                
                total_net_interest += period_net_interest
                total_tax += period_tax
                total_amount += period_net_interest
            
            final_amount = total_amount
        else:
            final_amount = deposit_amount + net_interest
            total_net_interest = net_interest
            total_tax = tax_amount
        
        st.metric("Bunga Kotor", format_currency(gross_interest * rollover_times))
        st.metric("Pajak Bunga", format_currency(total_tax))
        st.metric("Bunga Bersih", format_currency(total_net_interest))
        st.metric("Total Akhir", format_currency(final_amount))
        st.metric("Yield Bersih", f"{(total_net_interest/deposit_amount)*100:.2f}%")
    
    # Breakdown per periode
    st.subheader("📊 Breakdown per Periode")
    
    if auto_rollover:
        periods = []
        current_amount = deposit_amount
        
        for i in range(rollover_times):
            period_interest = current_amount * monthly_rate * deposit_term
            period_tax = period_interest * tax_rate / 100
            period_net_interest = period_interest - period_tax
            
            periods.append({
                'Periode': i + 1,
                'Pokok_Awal': current_amount,
                'Bunga_Kotor': period_interest,
                'Pajak': period_tax,
                'Bunga_Bersih': period_net_interest,
                'Pokok_Akhir': current_amount + period_net_interest
            })
            
            current_amount += period_net_interest
        
        df_periods = pd.DataFrame(periods)
        
        # Format currency
        for col in ['Pokok_Awal', 'Bunga_Kotor', 'Pajak', 'Bunga_Bersih', 'Pokok_Akhir']:
            df_periods[col] = df_periods[col].apply(format_currency)
        
        st.dataframe(df_periods, use_container_width=True)
        
        # Export functionality for Deposit Calculator
        st.subheader("📥 Export Data")
        col_export1, col_export2, col_export3 = st.columns(3)
        
        # Prepare export data
        input_params = {
            'Jumlah Deposito': deposit_amount,
            'Suku Bunga Deposito': deposit_rate,
            'Jangka Waktu': deposit_term,
            'Pajak Bunga': tax_rate,
            'Auto Roll Over': auto_rollover,
            'Jumlah Roll Over': rollover_times
        }
        
        results = {
            'Bunga Per Periode': period_interest,
            'Pajak Per Periode': period_tax,
            'Bunga Bersih Per Periode': period_net_interest,
            'Total Akhir': final_amount,
            'Yield Bersih': f"{(total_net_interest/deposit_amount)*100:.2f}%"
        }
        
        # Use the periods DataFrame for export
        export_data = create_export_data("Investasi Deposito", input_params, results, df_periods)
        
        with col_export1:
            # CSV Export
            csv_data = export_to_csv(df_periods, "deposit_breakdown.csv")
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"deposito_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_export2:
            # Excel Export
            excel_data = export_to_excel(export_data, "deposit_analysis.xlsx")
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name=f"deposito_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col_export3:
            # Summary Report
            summary_report = create_summary_report("Investasi Deposito", input_params, results)
            st.download_button(
                label="📋 Download Report",
                data=summary_report,
                file_name=f"deposito_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

elif calculator_type == "Cicilan Kendaraan":
    st.header("🚗 Kalkulator Cicilan Kendaraan")
    
    # Pilihan platform financing
    st.subheader("🏦 Pilih Platform Financing")
    financing_platform = st.selectbox(
        "Platform Financing:",
        ["Custom", "Astra Credit Companies (ACC)", "Mandiri Tunas Finance", "BCA Finance", "Adira Finance", "BAF (Toyota)", "FIFGROUP", "Maybank Finance", "WOM Finance", "CIMB Niaga Auto Finance", "Mega Central Finance", "Suzuki Finance", "Honda Finance", "Yamaha Finance", "MPM Finance", "Summit Oto Finance", "Bussan Auto Finance", "Clipan Finance", "Federal International Finance", "Oto Multiartha", "Radana Finance", "Smart Finance", "Kredit Plus", "Dipo Star Finance", "Kreditpro", "Fortech", "Kredivo Motor", "Akulaku Motor", "TunaiKita Motor", "Danamas Motor", "OVO PayLater Motor", "Sinarmas Finance", "Suzuki Finance Indonesia", "Daihatsu Finance", "Isuzu Finance", "Mitsubishi Motors Finance", "Nissan Finance", "Mazda Finance", "KrediFazz Motor", "Fundaztic Motor", "Kredit Pintar Motor", "Rupiah Plus Motor"]
    )
    
    # Preset berdasarkan platform
    platform_presets = {
        # Multifinance Traditional
        "Astra Credit Companies (ACC)": {"rate": 7.5, "admin": 2500000, "insurance": 2.8, "dp_min": 20, "type": "Multifinance", "info": "Leader market motor & mobil"},
        "Mandiri Tunas Finance": {"rate": 8.2, "admin": 3000000, "insurance": 3.0, "dp_min": 25, "type": "Bank Affiliate", "info": "Anak perusahaan Bank Mandiri"},
        "BCA Finance": {"rate": 7.8, "admin": 2000000, "insurance": 2.5, "dp_min": 20, "type": "Bank Affiliate", "info": "Anak perusahaan BCA Group"},
        "Adira Finance": {"rate": 9.5, "admin": 2500000, "insurance": 3.2, "dp_min": 20, "type": "Multifinance", "info": "Multifinance terbesar kedua"},
        "BAF (Toyota)": {"rate": 6.8, "admin": 2000000, "insurance": 2.3, "dp_min": 20, "type": "Captive Finance", "info": "Finance resmi Toyota"},
        "FIFGROUP": {"rate": 8.5, "admin": 2800000, "insurance": 3.0, "dp_min": 25, "type": "Multifinance", "info": "Federal International Finance"},
        "Maybank Finance": {"rate": 8.0, "admin": 2200000, "insurance": 2.7, "dp_min": 20, "type": "Bank Affiliate", "info": "Anak perusahaan Maybank"},
        "WOM Finance": {"rate": 9.0, "admin": 2600000, "insurance": 3.1, "dp_min": 25, "type": "Multifinance", "info": "Wahana Ottomitra Multiartha"},
        "CIMB Niaga Auto Finance": {"rate": 8.3, "admin": 2400000, "insurance": 2.9, "dp_min": 20, "type": "Bank Affiliate", "info": "Auto finance CIMB Niaga"},
        "Mega Central Finance": {"rate": 8.7, "admin": 2300000, "insurance": 2.8, "dp_min": 20, "type": "Bank Affiliate", "info": "Anak perusahaan Bank Mega"},
        
        # Captive Finance (Brand Specific)
        "Suzuki Finance": {"rate": 7.2, "admin": 2100000, "insurance": 2.4, "dp_min": 15, "type": "Captive Finance", "info": "Finance resmi Suzuki"},
        "Honda Finance": {"rate": 7.0, "admin": 2000000, "insurance": 2.2, "dp_min": 15, "type": "Captive Finance", "info": "Finance resmi Honda"},
        "Yamaha Finance": {"rate": 7.3, "admin": 2200000, "insurance": 2.5, "dp_min": 15, "type": "Captive Finance", "info": "Finance resmi Yamaha"},
        "MPM Finance": {"rate": 7.8, "admin": 2300000, "insurance": 2.6, "dp_min": 20, "type": "Captive Finance", "info": "Finance Mitsubishi"},
        
        # Multifinance Independent
        "Summit Oto Finance": {"rate": 8.8, "admin": 2400000, "insurance": 3.0, "dp_min": 25, "type": "Multifinance", "info": "Summit Oto Finance"},
        "Bussan Auto Finance": {"rate": 8.6, "admin": 2500000, "insurance": 2.9, "dp_min": 20, "type": "Multifinance", "info": "Bussan Auto Finance"},
        "Clipan Finance": {"rate": 9.2, "admin": 2600000, "insurance": 3.1, "dp_min": 25, "type": "Multifinance", "info": "Clipan Finance Indonesia"},
        "Federal International Finance": {"rate": 8.9, "admin": 2700000, "insurance": 3.0, "dp_min": 25, "type": "Multifinance", "info": "Federal International Finance"},
        "Oto Multiartha": {"rate": 9.0, "admin": 2400000, "insurance": 3.0, "dp_min": 20, "type": "Multifinance", "info": "Oto Multiartha Finance"},
        "Radana Finance": {"rate": 9.3, "admin": 2500000, "insurance": 3.2, "dp_min": 25, "type": "Multifinance", "info": "Radana Finance"},
        "Smart Finance": {"rate": 8.4, "admin": 2300000, "insurance": 2.8, "dp_min": 20, "type": "Multifinance", "info": "Smart Finance Indonesia"},
        "Kredit Plus": {"rate": 10.5, "admin": 3000000, "insurance": 3.5, "dp_min": 30, "type": "Multifinance", "info": "Kredit Plus financing"},
        "Dipo Star Finance": {"rate": 9.1, "admin": 2600000, "insurance": 3.1, "dp_min": 25, "type": "Multifinance", "info": "Dipo Star Finance"},
        "Kreditpro": {"rate": 11.0, "admin": 2800000, "insurance": 3.3, "dp_min": 25, "type": "Multifinance", "info": "Kreditpro Financing"},
        "Fortech": {"rate": 10.2, "admin": 2700000, "insurance": 3.2, "dp_min": 25, "type": "Multifinance", "info": "Fortech Financing"},
        
        # Fintech/Digital
        "Kredivo Motor": {"rate": 12.0, "admin": 1500000, "insurance": 2.0, "dp_min": 10, "type": "Fintech", "info": "Pinjaman online motor"},
        "Akulaku Motor": {"rate": 15.0, "admin": 1000000, "insurance": 1.8, "dp_min": 5, "type": "Fintech", "info": "Cicilan motor online"},
        "TunaiKita Motor": {"rate": 13.5, "admin": 1200000, "insurance": 1.9, "dp_min": 10, "type": "Fintech", "info": "Pinjaman motor digital"},
        "Danamas Motor": {"rate": 14.0, "admin": 1300000, "insurance": 2.1, "dp_min": 10, "type": "Fintech", "info": "Kredit motor Danamas"},
        "OVO PayLater Motor": {"rate": 16.0, "admin": 800000, "insurance": 1.5, "dp_min": 5, "type": "Fintech", "info": "PayLater untuk motor"},
        
        # High Priority Additional Platforms
        "Sinarmas Finance": {"rate": 8.9, "admin": 2400000, "insurance": 2.9, "dp_min": 20, "type": "Multifinance", "info": "Sinarmas multifinance terpercaya"},
        "Suzuki Finance Indonesia": {"rate": 7.1, "admin": 2100000, "insurance": 2.3, "dp_min": 15, "type": "Captive Finance", "info": "Finance resmi Suzuki Indonesia"},
        "Daihatsu Finance": {"rate": 7.4, "admin": 2200000, "insurance": 2.4, "dp_min": 15, "type": "Captive Finance", "info": "Finance resmi Daihatsu"},
        "Isuzu Finance": {"rate": 7.6, "admin": 2300000, "insurance": 2.5, "dp_min": 20, "type": "Captive Finance", "info": "Finance resmi Isuzu"},
        "Mitsubishi Motors Finance": {"rate": 7.7, "admin": 2400000, "insurance": 2.6, "dp_min": 20, "type": "Captive Finance", "info": "Finance resmi Mitsubishi"},
        "Nissan Finance": {"rate": 8.1, "admin": 2500000, "insurance": 2.7, "dp_min": 20, "type": "Captive Finance", "info": "Finance resmi Nissan"},
        "Mazda Finance": {"rate": 8.3, "admin": 2600000, "insurance": 2.8, "dp_min": 20, "type": "Captive Finance", "info": "Finance resmi Mazda"},
        
        # Digital/Fintech Additional
        "KrediFazz Motor": {"rate": 13.0, "admin": 1200000, "insurance": 1.8, "dp_min": 10, "type": "Fintech", "info": "Kredit motor digital KrediFazz"},
        "Fundaztic Motor": {"rate": 14.5, "admin": 1000000, "insurance": 1.7, "dp_min": 10, "type": "Fintech", "info": "Platform kredit motor Fundaztic"},
        "Kredit Pintar Motor": {"rate": 16.0, "admin": 800000, "insurance": 1.5, "dp_min": 5, "type": "Fintech", "info": "Kredit motor dari Kredit Pintar"},
        "Rupiah Plus Motor": {"rate": 17.0, "admin": 600000, "insurance": 1.4, "dp_min": 5, "type": "Fintech", "info": "Pinjaman motor Rupiah Plus"}
    }
    
    # Vehicle Finance Safety Information
    if financing_platform != "Custom":
        if financing_platform in platform_presets and platform_presets[financing_platform]["type"] == "Fintech":
            st.warning("⚠️ **PERINGATAN**: Platform fintech memiliki bunga tinggi. Pastikan terdaftar OJK dan pahami risiko!")
        else:
            st.info("💡 **Tips Kredit Kendaraan**: Bandingkan suku bunga, biaya admin, dan asuransi. Pertimbangkan kemampuan bayar jangka panjang.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameter")
        vehicle_price = st.number_input("Harga Kendaraan (Rp)", min_value=50000000, value=200000000, step=5000000)
        
        # Set default values berdasarkan platform
        if financing_platform != "Custom" and financing_platform in platform_presets:
            preset = platform_presets[financing_platform]
            default_rate = preset["rate"]
            default_admin = preset["admin"]
            default_insurance = preset["insurance"]
            min_dp = preset["dp_min"]
        else:
            default_rate = 8.0
            default_admin = 2000000
            default_insurance = 2.5
            min_dp = 0
        
        down_payment_pct = st.slider("Uang Muka (%)", min_value=min_dp, max_value=50, value=max(20, min_dp))
        down_payment = vehicle_price * down_payment_pct / 100
        
        st.info(f"Uang Muka: {format_currency(down_payment)}")
        
        loan_amount = vehicle_price - down_payment
        interest_rate = st.slider("Suku Bunga Tahunan (%)", min_value=3.0, max_value=20.0, value=default_rate, step=0.1)
        loan_term = st.selectbox("Jangka Waktu", [1, 2, 3, 4, 5, 6, 7], format_func=lambda x: f"{x} Tahun")
        
        # Biaya tambahan
        admin_fee = st.number_input("Biaya Admin (Rp)", min_value=0, value=default_admin, step=100000)
        insurance_rate = st.slider("Asuransi per Tahun (% dari harga)", min_value=0.0, max_value=5.0, value=default_insurance, step=0.1)
        
        # Informasi platform
        if financing_platform != "Custom":
            st.info(f"📋 **Info {financing_platform}**")
            if financing_platform == "Astra Credit Companies (ACC)":
                st.write("• Bunga kompetitif untuk motor Honda, Yamaha, Suzuki")
                st.write("• Proses persetujuan cepat")
                st.write("• Jaringan dealer luas")
            elif financing_platform == "Kredivo Motor":
                st.write("• Pinjaman online tanpa jaminan")
                st.write("• Approval instan via aplikasi")
                st.write("• Cicilan fleksibel 3-12 bulan")
            elif financing_platform == "Akulaku Motor":
                st.write("• Cicilan 0% untuk motor tertentu")
                st.write("• Proses online 100%")
                st.write("• Syarat mudah, cukup KTP & selfie")
        
    with col2:
        st.subheader("Hasil Perhitungan")
        
        monthly_payment = calculate_loan_payment(loan_amount, interest_rate, loan_term)
        total_payment = monthly_payment * loan_term * 12
        total_interest = total_payment - loan_amount
        
        # Biaya asuransi
        annual_insurance = vehicle_price * insurance_rate / 100
        total_insurance = annual_insurance * loan_term
        
        # Total biaya
        total_cost = down_payment + total_payment + admin_fee + total_insurance
        
        st.metric("Jumlah Pinjaman", format_currency(loan_amount))
        st.metric("Cicilan Bulanan", format_currency(monthly_payment))
        st.metric("Total Bunga", format_currency(total_interest))
        st.metric("Biaya Asuransi", format_currency(total_insurance))
        st.metric("Total Biaya", format_currency(total_cost))
        
        # Perbandingan cash vs kredit
        st.subheader("💰 Cash vs Kredit")
        cash_price = vehicle_price
        credit_total = total_cost
        difference = credit_total - cash_price
        
        st.metric("Beli Cash", format_currency(cash_price))
        st.metric("Beli Kredit", format_currency(credit_total))
        st.metric("Selisih", format_currency(difference))
        st.metric("Selisih %", f"{(difference/cash_price)*100:.1f}%")
    
    # Export functionality for Vehicle Financing Calculator
    st.subheader("📥 Export Data")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    # Prepare export data
    input_params = {
        'Platform Financing': financing_platform,
        'Harga Kendaraan': vehicle_price,
        'Uang Muka': down_payment,
        'Suku Bunga': interest_rate,
        'Jangka Waktu': loan_term,
        'Biaya Admin': admin_fee,
        'Biaya Asuransi': insurance_rate
    }
    
    results = {
        'Jumlah Pinjaman': loan_amount,
        'Cicilan Bulanan': monthly_payment,
        'Total Bunga': total_interest,
        'Biaya Asuransi Total': total_insurance,
        'Total Biaya': total_cost,
        'Selisih Cash vs Kredit': difference,
        'Selisih Persentase': f"{(difference/cash_price)*100:.1f}%"
    }
    
    # Create financing comparison data
    financing_data = pd.DataFrame({
        'Komponen': ['Harga Kendaraan', 'Uang Muka', 'Jumlah Pinjaman', 'Total Bunga', 'Biaya Admin', 'Biaya Asuransi', 'Total Biaya'],
        'Nilai': [vehicle_price, down_payment, loan_amount, total_interest, admin_fee, total_insurance, total_cost]
    })
    
    export_data = create_export_data("Cicilan Kendaraan", input_params, results, financing_data)
    
    with col_export1:
        # CSV Export
        csv_data = export_to_csv(financing_data, "vehicle_financing.csv")
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"cicilan_kendaraan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_export2:
        # Excel Export
        excel_data = export_to_excel(export_data, "vehicle_financing_analysis.xlsx")
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"cicilan_kendaraan_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_export3:
        # Summary Report
        summary_report = create_summary_report("Cicilan Kendaraan", input_params, results)
        st.download_button(
            label="📋 Download Report",
            data=summary_report,
            file_name=f"cicilan_kendaraan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

elif calculator_type == "Cicilan Properti":
    st.header("🏠 Kalkulator Cicilan Properti")
    
    # Pilihan platform KPR
    st.subheader("🏦 Pilih Platform KPR")
    kpr_platform = st.selectbox(
        "Platform KPR:",
        ["Custom", "BTN (Bank Tabungan Negara)", "BRI", "BCA", "Mandiri", "BNI", "CIMB Niaga", "Danamon", "Maybank", "OCBC NISP", "Permata Bank", "Bank Syariah Indonesia", "Muamalat", "Panin Bank", "Bank DKI", "Bank Jateng", "Bank Jatim", "Bank Bukopin", "Citibank", "HSBC", "Standard Chartered", "Bank Sinarmas", "Bank Mega Syariah", "Sinar Mas Land Finance", "Agung Sedayu Finance", "Ciputra Finance", "Lippo Finance", "Rumah123 Finance", "GoPay Later (Pinjol)", "ShopeePay Later", "Kredivo", "Akulaku"]
    )
    
    # Preset berdasarkan platform
    kpr_presets = {
        "BTN (Bank Tabungan Negara)": {"rate": 8.5, "dp_min": 10, "notary": 12000000, "type": "Bank", "info": "KPR Subsidi & Komersial"},
        "BRI": {"rate": 9.2, "dp_min": 10, "notary": 15000000, "type": "Bank", "info": "KPR BRI dengan bunga kompetitif"},
        "BCA": {"rate": 8.8, "dp_min": 20, "notary": 18000000, "type": "Bank", "info": "KPR BCA dengan layanan premium"},
        "Mandiri": {"rate": 9.0, "dp_min": 15, "notary": 16000000, "type": "Bank", "info": "KPR Mandiri dengan berbagai program"},
        "BNI": {"rate": 8.7, "dp_min": 15, "notary": 14000000, "type": "Bank", "info": "KPR BNI dengan bunga bersaing"},
        "CIMB Niaga": {"rate": 9.5, "dp_min": 20, "notary": 15000000, "type": "Bank", "info": "KPR CIMB dengan proses cepat"},
        "Danamon": {"rate": 9.8, "dp_min": 20, "notary": 17000000, "type": "Bank", "info": "KPR Danamon dengan fleksibilitas tinggi"},
        "Maybank": {"rate": 9.3, "dp_min": 20, "notary": 16000000, "type": "Bank", "info": "KPR Maybank dengan layanan personal"},
        "OCBC NISP": {"rate": 9.1, "dp_min": 20, "notary": 16500000, "type": "Bank", "info": "KPR OCBC NISP dengan bunga kompetitif"},
        "Permata Bank": {"rate": 9.4, "dp_min": 20, "notary": 15500000, "type": "Bank", "info": "KPR Permata dengan berbagai pilihan"},
        "Bank Syariah Indonesia": {"rate": 8.9, "dp_min": 20, "notary": 13000000, "type": "Syariah", "info": "KPR Syariah dengan akad Murabahah"},
        "Muamalat": {"rate": 9.2, "dp_min": 20, "notary": 14000000, "type": "Syariah", "info": "KPR Syariah dengan prinsip Islam"},
        "Panin Bank": {"rate": 9.6, "dp_min": 20, "notary": 16000000, "type": "Bank", "info": "KPR Panin dengan layanan personal"},
        "Bank DKI": {"rate": 9.5, "dp_min": 20, "notary": 14000000, "type": "Regional", "info": "KPR Bank DKI untuk warga Jakarta"},
        "Bank Jateng": {"rate": 9.3, "dp_min": 15, "notary": 12000000, "type": "Regional", "info": "KPR Bank Jateng dengan bunga kompetitif"},
        "Bank Jatim": {"rate": 9.4, "dp_min": 15, "notary": 13000000, "type": "Regional", "info": "KPR Bank Jatim untuk warga Jawa Timur"},
        "Bank Bukopin": {"rate": 9.9, "dp_min": 20, "notary": 15000000, "type": "Bank", "info": "KPR Bukopin dengan layanan personal"},
        "Citibank": {"rate": 8.5, "dp_min": 30, "notary": 20000000, "type": "Asing", "info": "KPR Citibank premium dengan bunga rendah"},
        "HSBC": {"rate": 8.3, "dp_min": 30, "notary": 22000000, "type": "Asing", "info": "KPR HSBC untuk nasabah premium"},
        "Standard Chartered": {"rate": 8.7, "dp_min": 25, "notary": 19000000, "type": "Asing", "info": "KPR Standard Chartered dengan layanan internasional"},
        "Bank Sinarmas": {"rate": 9.8, "dp_min": 20, "notary": 15000000, "type": "Bank", "info": "KPR Sinarmas dengan proses mudah"},
        "Bank Mega Syariah": {"rate": 9.1, "dp_min": 20, "notary": 13000000, "type": "Syariah", "info": "KPR Syariah dengan akad Murabahah"},
        "Sinar Mas Land Finance": {"rate": 10.5, "dp_min": 10, "notary": 8000000, "type": "Developer", "info": "KPR Developer dengan DP ringan"},
        "Agung Sedayu Finance": {"rate": 11.0, "dp_min": 5, "notary": 6000000, "type": "Developer", "info": "KPR Developer dengan DP minimal"},
        "Ciputra Finance": {"rate": 10.8, "dp_min": 10, "notary": 7000000, "type": "Developer", "info": "KPR Developer Ciputra Group"},
        "Lippo Finance": {"rate": 11.2, "dp_min": 5, "notary": 5000000, "type": "Developer", "info": "KPR Developer Lippo Group"},
        "Rumah123 Finance": {"rate": 12.0, "dp_min": 0, "notary": 3000000, "type": "Fintech", "info": "KPR Fintech dengan teknologi digital"},
        "GoPay Later (Pinjol)": {"rate": 15.0, "dp_min": 0, "notary": 5000000, "type": "Pinjol", "info": "Pinjaman online untuk renovasi rumah"},
        "ShopeePay Later": {"rate": 18.0, "dp_min": 0, "notary": 3000000, "type": "Pinjol", "info": "Pinjaman online untuk kebutuhan properti"},
        "Kredivo": {"rate": 12.0, "dp_min": 0, "notary": 4000000, "type": "Pinjol", "info": "Pinjaman online tanpa jaminan"},
        "Akulaku": {"rate": 20.0, "dp_min": 0, "notary": 2000000, "type": "Pinjol", "info": "Pinjaman online dengan proses cepat"}
    }
    
    # KPR Safety Information
    if kpr_platform != "Custom":
        if kpr_platform in kpr_presets and kpr_presets[kpr_platform]["type"] == "Pinjol":
            st.warning("⚠️ **PERINGATAN**: Platform ini adalah pinjaman online, bukan KPR tradisional. Pastikan terdaftar OJK!")
        else:
            st.info("💡 **Tips KPR**: Bandingkan suku bunga, biaya admin, dan persyaratan. Pastikan kemampuan bayar sesuai dengan pendapatan.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameter")
        
        # Batasan berdasarkan platform
        if kpr_platform != "Custom" and kpr_platform in kpr_presets:
            preset = kpr_presets[kpr_platform]
            if preset["type"] == "Pinjol":
                property_price = st.number_input("Jumlah Pinjaman (Rp)", min_value=5000000, max_value=500000000, value=100000000, step=5000000)
                st.warning("⚠️ Pinjaman online biasanya untuk renovasi/kebutuhan properti, bukan pembelian rumah utuh")
            else:
                property_price = st.number_input("Harga Properti (Rp)", min_value=100000000, value=500000000, step=10000000)
        else:
            property_price = st.number_input("Harga Properti (Rp)", min_value=100000000, value=500000000, step=10000000)
        
        # Set default values berdasarkan platform
        if kpr_platform != "Custom" and kpr_platform in kpr_presets:
            preset = kpr_presets[kpr_platform]
            default_rate = preset["rate"]
            default_notary = preset["notary"]
            min_dp = preset["dp_min"]
        else:
            default_rate = 10.0
            default_notary = 15000000
            min_dp = 10
        
        down_payment_pct = st.slider("Uang Muka (%)", min_value=min_dp, max_value=50, value=max(20, min_dp))
        down_payment = property_price * down_payment_pct / 100
        
        st.info(f"Uang Muka: {format_currency(down_payment)}")
        
        loan_amount = property_price - down_payment
        interest_rate = st.slider("Suku Bunga Tahunan (%)", min_value=5.0, max_value=25.0, value=default_rate, step=0.1)
        
        # Batasan jangka waktu berdasarkan platform
        if kpr_platform != "Custom" and kpr_platform in kpr_presets:
            preset = kpr_presets[kpr_platform]
            if preset["type"] == "Pinjol":
                loan_term = st.selectbox("Jangka Waktu", [1, 2, 3, 4, 5], format_func=lambda x: f"{x} Tahun")
            else:
                loan_term = st.selectbox("Jangka Waktu", [5, 10, 15, 20, 25, 30], format_func=lambda x: f"{x} Tahun")
        else:
            loan_term = st.selectbox("Jangka Waktu", [5, 10, 15, 20, 25, 30], format_func=lambda x: f"{x} Tahun")
        
        # Biaya tambahan
        notary_fee = st.number_input("Biaya Notaris (Rp)", min_value=0, value=default_notary, step=1000000)
        
        # Hitung pajak berdasarkan platform
        if kpr_platform != "Custom" and kpr_platform in kpr_presets:
            preset = kpr_presets[kpr_platform]
            if preset["type"] == "Pinjol":
                tax_fee = property_price * 0.01  # Fee pinjol biasanya 1%
                st.info(f"Biaya Platform (1%): {format_currency(tax_fee)}")
            else:
                tax_fee = property_price * 0.05  # BPHTB 5%
                st.info(f"Pajak BPHTB (5%): {format_currency(tax_fee)}")
        else:
            tax_fee = property_price * 0.05
            st.info(f"Pajak BPHTB (5%): {format_currency(tax_fee)}")
        
        # Pilihan suku bunga (hanya untuk bank konvensional)
        if kpr_platform != "Custom" and kpr_platform in kpr_presets:
            preset = kpr_presets[kpr_platform]
            if preset["type"] == "Bank":
                interest_type = st.selectbox("Jenis Suku Bunga", ["Fixed", "Floating"])
                if interest_type == "Floating":
                    rate_change_year = st.slider("Perubahan Bunga Tahun Ke-", min_value=1, max_value=5, value=2)
                    new_rate = st.slider("Suku Bunga Baru (%)", min_value=5.0, max_value=15.0, value=12.0, step=0.1)
            else:
                interest_type = "Fixed"
                st.info("💡 Pinjaman online umumnya menggunakan bunga tetap")
        else:
            interest_type = st.selectbox("Jenis Suku Bunga", ["Fixed", "Floating"])
            if interest_type == "Floating":
                rate_change_year = st.slider("Perubahan Bunga Tahun Ke-", min_value=1, max_value=5, value=2)
                new_rate = st.slider("Suku Bunga Baru (%)", min_value=5.0, max_value=15.0, value=12.0, step=0.1)
        
        # Informasi platform
        if kpr_platform != "Custom":
            st.info(f"📋 **Info {kpr_platform}**")
            if kpr_platform in kpr_presets:
                preset = kpr_presets[kpr_platform]
                st.write(f"• {preset['info']}")
                if preset["type"] == "Bank":
                    st.write("• Syarat: Slip gaji, NPWP, agunan properti")
                    st.write("• Proses: 7-14 hari kerja")
                elif preset["type"] == "Syariah":
                    st.write("• Syarat: Slip gaji, NPWP, agunan properti")
                    st.write("• Prinsip: Sesuai syariah Islam")
                elif preset["type"] == "Pinjol":
                    st.write("• Syarat: KTP, selfie, rekening bank")
                    st.write("• Proses: Instant - 24 jam")
                    st.write("• ⚠️ Bunga tinggi, hati-hati dengan cicilan")
    
    with col2:
        st.subheader("Hasil Perhitungan")
        
        if interest_type == "Fixed":
            monthly_payment = calculate_loan_payment(loan_amount, interest_rate, loan_term)
            total_payment = monthly_payment * loan_term * 12
            total_interest = total_payment - loan_amount
            
            st.metric("Jumlah Pinjaman", format_currency(loan_amount))
            st.metric("Cicilan Bulanan", format_currency(monthly_payment))
            st.metric("Total Bunga", format_currency(total_interest))
            
        else:  # Floating
            # Periode 1: Bunga awal
            monthly_payment_1 = calculate_loan_payment(loan_amount, interest_rate, loan_term)
            payments_period_1 = rate_change_year * 12
            
            # Sisa pokok setelah periode 1
            df_schedule_1 = generate_amortization_schedule(loan_amount, interest_rate, loan_term)
            remaining_balance = df_schedule_1.iloc[payments_period_1-1]['Sisa_Pokok']
            
            # Periode 2: Bunga baru
            remaining_years = loan_term - rate_change_year
            monthly_payment_2 = calculate_loan_payment(remaining_balance, new_rate, remaining_years)
            
            # Total pembayaran
            total_payment_1 = monthly_payment_1 * payments_period_1
            total_payment_2 = monthly_payment_2 * (remaining_years * 12)
            total_payment = total_payment_1 + total_payment_2
            total_interest = total_payment - loan_amount
            
            # Set monthly_payment untuk analisis affordability (gunakan cicilan periode 1)
            monthly_payment = monthly_payment_1
            
            st.metric("Cicilan Awal", format_currency(monthly_payment_1))
            st.metric("Cicilan Setelah Tahun Ke-" + str(rate_change_year), format_currency(monthly_payment_2))
            st.metric("Total Bunga", format_currency(total_interest))
        
        # Total biaya pembelian
        total_cost = down_payment + total_payment + notary_fee + tax_fee
        
        st.metric("Biaya Notaris", format_currency(notary_fee))
        st.metric("Pajak BPHTB", format_currency(tax_fee))
        st.metric("Total Biaya", format_currency(total_cost))
        
        # Analisis affordability
        st.subheader("📊 Analisis Kemampuan")
        monthly_income = st.number_input("Penghasilan Bulanan (Rp)", min_value=5000000, value=20000000, step=1000000)
        
        # monthly_payment sudah didefinisikan di atas untuk kedua kasus
        debt_to_income = (monthly_payment / monthly_income) * 100
        
        if debt_to_income <= 30:
            st.success(f"Debt-to-Income Ratio: {debt_to_income:.1f}% (Aman)")
        elif debt_to_income <= 40:
            st.warning(f"Debt-to-Income Ratio: {debt_to_income:.1f}% (Hati-hati)")
        else:
            st.error(f"Debt-to-Income Ratio: {debt_to_income:.1f}% (Berisiko)")
    
    # Export functionality for Property/KPR Calculator
    st.subheader("📥 Export Data")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    # Prepare export data
    input_params = {
        'Platform KPR': kpr_platform,
        'Harga Properti': property_price,
        'Uang Muka': down_payment,
        'Uang Muka (%)': down_payment_pct,
        'Jumlah Pinjaman': loan_amount,
        'Suku Bunga': interest_rate,
        'Jenis Bunga': interest_type,
        'Jangka Waktu': loan_term,
        'Biaya Notaris': notary_fee,
        'Penghasilan Bulanan': monthly_income
    }
    
    if interest_type == "Fixed":
        results = {
            'Jumlah Pinjaman': loan_amount,
            'Cicilan Bulanan': monthly_payment,
            'Total Pembayaran': total_payment,
            'Total Bunga': total_interest,
            'Total Biaya': total_cost,
            'Debt-to-Income Ratio': f"{debt_to_income:.1f}%"
        }
        
        # Create KPR schedule
        kpr_schedule = generate_amortization_schedule(loan_amount, interest_rate, loan_term)
    else:
        # Floating rate results
        results = {
            'Jumlah Pinjaman': loan_amount,
            'Cicilan Awal (Tahun 1-3)': monthly_payment_1,
            'Cicilan Setelah Tahun 3': monthly_payment_2,
            'Total Pembayaran': total_payment,
            'Total Bunga': total_interest,
            'Total Biaya': total_cost,
            'Debt-to-Income Ratio': f"{debt_to_income:.1f}%"
        }
        
        # Create floating rate schedule combining both periods
        kpr_schedule_1 = generate_amortization_schedule(loan_amount, interest_rate, rate_change_year)
        kpr_schedule_2 = generate_amortization_schedule(remaining_balance, new_rate, remaining_years)
        kpr_schedule_2['Bulan'] = kpr_schedule_2['Bulan'] + (rate_change_year * 12)
        kpr_schedule = pd.concat([kpr_schedule_1, kpr_schedule_2], ignore_index=True)
    
    # Add cost breakdown
    cost_breakdown = pd.DataFrame({
        'Komponen': ['Harga Properti', 'Uang Muka', 'Jumlah Pinjaman', 'Total Bunga', 'Biaya Notaris', 'Pajak/Biaya Lain', 'Total Biaya'],
        'Nilai': [property_price, down_payment, loan_amount, total_interest, notary_fee, tax_fee, total_cost]
    })
    
    export_data = create_export_data("Cicilan Properti/KPR", input_params, results, kpr_schedule)
    export_data['cost_breakdown'] = cost_breakdown.to_dict('records')
    
    with col_export1:
        # CSV Export
        csv_data = export_to_csv(kpr_schedule, "kpr_schedule.csv")
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"kpr_cicilan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_export2:
        # Excel Export
        excel_data = export_to_excel(export_data, "kpr_analysis.xlsx")
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"kpr_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_export3:
        # Summary Report
        summary_report = create_summary_report("Cicilan Properti/KPR", input_params, results)
        st.download_button(
            label="📋 Download Report",
            data=summary_report,
            file_name=f"kpr_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

elif calculator_type == "Pinjaman Online/Fintech":
    st.header("💳 Kalkulator Pinjaman Online/Fintech")
    
    # Pilihan platform pinjol
    st.subheader("📱 Pilih Platform Pinjaman Online")
    pinjol_platform = st.selectbox(
        "Platform Pinjol:",
        ["Custom", "GoPay Later", "ShopeePay Later", "Kredivo", "Akulaku", "Indodana", "Julo", "Tunaiku", "KoinWorks", "Investree", "Modalku", "Amartha", "UangTeman", "DanaRupiah", "CashWagon", "AdaKami", "Rupiah Cepat", "KTA Kilat", "Funding Societies", "Alami", "Ethis", "Kapitalku", "Mekar", "Akseleran", "Dana Syariah", "Atome", "Spaylater", "PayLater Bukalapak", "TokoCash", "Cicil", "Dana Tunai", "Kredit Cepat", "Pinjam Yuk", "UangMe", "KreditGo", "Gajiku", "PayDay", "KaryaOne"]
    )
    
    # Preset berdasarkan platform
    pinjol_presets = {
        "GoPay Later": {"rate": 2.5, "tenor": [1, 3, 6, 12], "limit": 20000000, "admin": 0, "type": "BNPL", "info": "Buy Now Pay Later tanpa bunga untuk tenor 1 bulan"},
        "ShopeePay Later": {"rate": 2.95, "tenor": [1, 3, 6, 12], "limit": 15000000, "admin": 0, "type": "BNPL", "info": "Cicilan 0% untuk merchant tertentu"},
        "Kredivo": {"rate": 2.6, "tenor": [1, 3, 6, 12, 24], "limit": 30000000, "admin": 50000, "type": "BNPL", "info": "Cicilan 0% untuk partner merchant"},
        "Akulaku": {"rate": 2.5, "tenor": [1, 3, 6, 12, 18], "limit": 20000000, "admin": 0, "type": "BNPL", "info": "Cicilan tanpa kartu kredit"},
        "Indodana": {"rate": 0.8, "tenor": [1, 3, 6, 12], "limit": 8000000, "admin": 25000, "type": "BNPL", "info": "Cicilan untuk belanja online"},
        "Julo": {"rate": 1.5, "tenor": [3, 6, 12], "limit": 8000000, "admin": 100000, "type": "P2P", "info": "Pinjaman dana tunai"},
        "Tunaiku": {"rate": 3.0, "tenor": [6, 12, 18, 24], "limit": 20000000, "admin": 150000, "type": "P2P", "info": "Pinjaman tanpa jaminan Amar Bank"},
        "KoinWorks": {"rate": 0.75, "tenor": [3, 6, 12, 24], "limit": 100000000, "admin": 200000, "type": "P2P", "info": "Pinjaman produktif untuk UMKM"},
        "Investree": {"rate": 1.0, "tenor": [3, 6, 12, 24, 36], "limit": 2000000000, "admin": 300000, "type": "P2P", "info": "Pinjaman invoice financing"},
        "Modalku": {"rate": 1.2, "tenor": [3, 6, 12, 24], "limit": 500000000, "admin": 250000, "type": "P2P", "info": "Pinjaman untuk ekspansi bisnis"},
        "Amartha": {"rate": 1.8, "tenor": [12, 24], "limit": 25000000, "admin": 100000, "type": "P2P", "info": "Pinjaman untuk mikro bisnis"},
        "UangTeman": {"rate": 0.8, "tenor": [1, 3, 6], "limit": 5000000, "admin": 50000, "type": "P2P", "info": "Pinjaman kilat untuk kebutuhan mendesak"},
        "DanaRupiah": {"rate": 0.75, "tenor": [3, 6, 12], "limit": 10000000, "admin": 75000, "type": "P2P", "info": "Pinjaman online terpercaya"},
        "CashWagon": {"rate": 1.0, "tenor": [3, 6, 12], "limit": 4000000, "admin": 100000, "type": "P2P", "info": "Pinjaman cepat tanpa ribet"},
        "AdaKami": {"rate": 0.75, "tenor": [3, 6, 12], "limit": 20000000, "admin": 150000, "type": "P2P", "info": "Pinjaman untuk karyawan"},
        "Rupiah Cepat": {"rate": 0.8, "tenor": [3, 6, 12], "limit": 8000000, "admin": 80000, "type": "P2P", "info": "Pinjaman mudah dan cepat"},
        "KTA Kilat": {"rate": 1.5, "tenor": [6, 12, 24], "limit": 50000000, "admin": 200000, "type": "P2P", "info": "Kredit tanpa agunan kilat"},
        
        # High Priority Additional Platforms
        "Funding Societies": {"rate": 1.0, "tenor": [3, 6, 12, 24, 36], "limit": 2000000000, "admin": 300000, "type": "P2P", "info": "Platform P2P lending untuk UMKM terbesar"},
        "Alami": {"rate": 1.2, "tenor": [6, 12, 24], "limit": 100000000, "admin": 200000, "type": "Syariah", "info": "P2P lending syariah terpercaya"},
        "Ethis": {"rate": 1.5, "tenor": [6, 12, 24, 36], "limit": 500000000, "admin": 250000, "type": "Syariah", "info": "Crowdfunding syariah untuk properti"},
        "Kapitalku": {"rate": 1.8, "tenor": [3, 6, 12, 24], "limit": 200000000, "admin": 150000, "type": "P2P", "info": "Pinjaman untuk ekspansi UMKM"},
        "Mekar": {"rate": 2.0, "tenor": [6, 12, 24], "limit": 50000000, "admin": 100000, "type": "P2P", "info": "Pinjaman untuk usaha mikro"},
        "Akseleran": {"rate": 1.3, "tenor": [3, 6, 12, 24], "limit": 2000000000, "admin": 300000, "type": "P2P", "info": "Invoice financing untuk bisnis"},
        "Dana Syariah": {"rate": 1.4, "tenor": [6, 12, 24], "limit": 100000000, "admin": 150000, "type": "Syariah", "info": "Pinjaman syariah tanpa riba"},
        "Atome": {"rate": 0.0, "tenor": [3, 6, 12], "limit": 10000000, "admin": 0, "type": "BNPL", "info": "Buy Now Pay Later 0% bunga untuk merchant partner"},
        "Spaylater": {"rate": 2.95, "tenor": [1, 3, 6, 12], "limit": 8000000, "admin": 0, "type": "BNPL", "info": "Cicilan 0% untuk merchant Sea Group"},
        "PayLater Bukalapak": {"rate": 2.5, "tenor": [1, 3, 6], "limit": 5000000, "admin": 0, "type": "BNPL", "info": "Cicilan tanpa bunga untuk pembelian di Bukalapak"},
        "TokoCash": {"rate": 1.2, "tenor": [3, 6, 12], "limit": 15000000, "admin": 75000, "type": "P2P", "info": "Pinjaman online untuk kebutuhan mendadak"},
        "Cicil": {"rate": 0.99, "tenor": [3, 6, 12, 24], "limit": 20000000, "admin": 100000, "type": "BNPL", "info": "Cicilan 0% untuk gadget dan elektronik"},
        "Dana Tunai": {"rate": 1.5, "tenor": [3, 6, 12], "limit": 10000000, "admin": 80000, "type": "P2P", "info": "Pinjaman tunai cepat cair"},
        "Kredit Cepat": {"rate": 1.8, "tenor": [3, 6, 12], "limit": 8000000, "admin": 100000, "type": "P2P", "info": "Pinjaman kilat untuk kebutuhan mendesak"},
        "Pinjam Yuk": {"rate": 1.0, "tenor": [3, 6, 12], "limit": 12000000, "admin": 60000, "type": "P2P", "info": "Pinjaman online mudah dan terpercaya"},
        "UangMe": {"rate": 0.75, "tenor": [1, 3, 6], "limit": 5000000, "admin": 50000, "type": "P2P", "info": "Pinjaman micro untuk kebutuhan harian"},
        "KreditGo": {"rate": 1.3, "tenor": [3, 6, 12], "limit": 15000000, "admin": 90000, "type": "P2P", "info": "Pinjaman cepat tanpa ribet"},
        "Gajiku": {"rate": 0.8, "tenor": [1, 3, 6], "limit": 10000000, "admin": 50000, "type": "P2P", "info": "Pinjaman untuk karyawan dengan potongan gaji"},
        "PayDay": {"rate": 1.5, "tenor": [1, 3, 6], "limit": 5000000, "admin": 75000, "type": "P2P", "info": "Pinjaman jangka pendek untuk kebutuhan mendesak"},
        "KaryaOne": {"rate": 1.2, "tenor": [3, 6, 12, 24], "limit": 200000000, "admin": 200000, "type": "P2P", "info": "Pinjaman untuk pengembangan bisnis dan investasi"}
    }
    
    # OJK Compliance Warning
    if pinjol_platform != "Custom":
        st.warning("⚠️ **PERINGATAN OJK**: Pastikan platform yang dipilih terdaftar dan diawasi oleh OJK. Hindari pinjaman online ilegal!")
        st.info("💡 **Tips Bijak**: Pahami biaya, bunga, dan konsekuensi sebelum mengajukan pinjaman. Pinjam sesuai kebutuhan dan kemampuan bayar.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameter")
        
        # Set limit berdasarkan platform
        if pinjol_platform != "Custom" and pinjol_platform in pinjol_presets:
            preset = pinjol_presets[pinjol_platform]
            max_limit = preset["limit"]
            loan_amount = st.number_input("Jumlah Pinjaman (Rp)", min_value=500000, max_value=max_limit, value=min(5000000, max_limit), step=100000)
            st.info(f"Limit maksimal: {format_currency(max_limit)}")
        else:
            loan_amount = st.number_input("Jumlah Pinjaman (Rp)", min_value=500000, max_value=100000000, value=5000000, step=100000)
        
        # Set tenor berdasarkan platform
        if pinjol_platform != "Custom" and pinjol_platform in pinjol_presets:
            preset = pinjol_presets[pinjol_platform]
            available_tenors = preset["tenor"]
            loan_term_months = st.selectbox("Jangka Waktu", available_tenors, format_func=lambda x: f"{x} Bulan")
            default_rate = preset["rate"]
            default_admin = preset["admin"]
        else:
            loan_term_months = st.selectbox("Jangka Waktu", [1, 3, 6, 12, 18, 24, 36], format_func=lambda x: f"{x} Bulan")
            default_rate = 2.5
            default_admin = 100000
        
        # Rate dalam persen per bulan
        monthly_rate = st.slider("Suku Bunga per Bulan (%)", min_value=0.1, max_value=10.0, value=default_rate, step=0.1)
        admin_fee = st.number_input("Biaya Admin (Rp)", min_value=0, value=default_admin, step=25000)
        
        # Informasi platform
        if pinjol_platform != "Custom":
            st.info(f"📋 **Info {pinjol_platform}**")
            if pinjol_platform in pinjol_presets:
                preset = pinjol_presets[pinjol_platform]
                st.write(f"• {preset['info']}")
                if preset["type"] == "BNPL":
                    st.write("• Jenis: Buy Now Pay Later")
                    st.write("• Syarat: Minimal KTP & rekening bank")
                    st.write("• Cicilan 0% untuk merchant partner")
                elif preset["type"] == "P2P":
                    st.write("• Jenis: Peer to Peer Lending")
                    st.write("• Syarat: KTP, slip gaji, rekening bank")
                    st.write("• Proses: 1-3 hari kerja")
                
                st.warning("⚠️ **Perhatian**: Pastikan platform terdaftar OJK dan pahami risiko bunga tinggi")
    
    with col2:
        st.subheader("Hasil Perhitungan")
        
        # Hitung cicilan per bulan
        monthly_payment = loan_amount / loan_term_months
        monthly_interest = loan_amount * monthly_rate / 100
        total_monthly_payment = monthly_payment + monthly_interest
        
        total_payment = total_monthly_payment * loan_term_months + admin_fee
        total_interest = total_payment - loan_amount
        
        # Hitung APR (Annual Percentage Rate)
        if loan_term_months > 0:
            apr = (monthly_rate * 12)
        else:
            apr = 0
        
        st.metric("Cicilan per Bulan", format_currency(total_monthly_payment))
        st.metric("Total Pembayaran", format_currency(total_payment))
        st.metric("Total Bunga & Biaya", format_currency(total_interest))
        st.metric("APR (Tahunan)", f"{apr:.1f}%")
        
        # Warning untuk bunga tinggi
        if apr > 36:
            st.error("🚨 **BUNGA SANGAT TINGGI!** Pertimbangkan alternatif lain")
        elif apr > 24:
            st.warning("⚠️ **BUNGA TINGGI!** Pastikan mampu bayar cicilan")
        elif apr > 12:
            st.warning("⚠️ Bunga cukup tinggi, pertimbangkan dengan baik")
        else:
            st.success("✅ Bunga masih dalam batas wajar")
        
        # Breakdown pembayaran
        st.subheader("📊 Breakdown Pembayaran")
        
        # Tabel cicilan
        cicilan_data = []
        sisa_pokok = loan_amount
        
        for bulan in range(1, loan_term_months + 1):
            bunga_bulan = sisa_pokok * monthly_rate / 100
            pokok_bulan = loan_amount / loan_term_months
            sisa_pokok -= pokok_bulan
            
            cicilan_data.append({
                'Bulan': bulan,
                'Cicilan_Pokok': pokok_bulan,
                'Cicilan_Bunga': bunga_bulan,
                'Total_Cicilan': pokok_bulan + bunga_bulan,
                'Sisa_Pokok': max(0, sisa_pokok)
            })
        
        df_cicilan = pd.DataFrame(cicilan_data)
        
        # Tampilkan 5 cicilan pertama
        st.write("**5 Cicilan Pertama:**")
        df_display = df_cicilan.head(5).copy()
        for col in ['Cicilan_Pokok', 'Cicilan_Bunga', 'Total_Cicilan', 'Sisa_Pokok']:
            df_display[col] = df_display[col].apply(format_currency)
        st.dataframe(df_display, use_container_width=True)
        
        # Perbandingan dengan alternatif
        st.subheader("💡 Perbandingan Alternatif")
        
        # Kartu kredit
        cc_rate = 2.5  # 2.5% per bulan
        cc_payment = loan_amount / loan_term_months + (loan_amount * cc_rate / 100)
        cc_total = cc_payment * loan_term_months
        
        # Bank konvensional
        bank_rate = 1.0  # 12% per tahun = 1% per bulan
        bank_payment = loan_amount / loan_term_months + (loan_amount * bank_rate / 100)
        bank_total = bank_payment * loan_term_months
        
        comparison_data = {
            'Jenis': [pinjol_platform, 'Kartu Kredit', 'KTA Bank'],
            'Cicilan_Bulanan': [total_monthly_payment, cc_payment, bank_payment],
            'Total_Bayar': [total_payment, cc_total, bank_total],
            'Selisih': [0, cc_total - total_payment, bank_total - total_payment]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        for col in ['Cicilan_Bulanan', 'Total_Bayar', 'Selisih']:
            df_comparison[col] = df_comparison[col].apply(format_currency)
        
        st.dataframe(df_comparison, use_container_width=True)
    
    # Export functionality for Pinjaman Online/Fintech Calculator
    st.subheader("📥 Export Data")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    # Prepare export data
    input_params = {
        'Platform Pinjol': pinjol_platform,
        'Jumlah Pinjaman': loan_amount,
        'Tenor': loan_term_months,
        'Suku Bunga Bulanan': monthly_rate,
        'Biaya Admin': admin_fee
    }
    
    results = {
        'Cicilan per Bulan': total_monthly_payment,
        'Total Pembayaran': total_payment,
        'Total Bunga & Biaya': total_interest,
        'APR (Tahunan)': f"{apr:.1f}%",
        'Perbandingan dengan Kartu Kredit': format_currency(cc_total - total_payment),
        'Perbandingan dengan Bank': format_currency(bank_total - total_payment)
    }
    
    # Create payment schedule
    payment_schedule = []
    remaining_balance = loan_amount
    
    for month in range(1, loan_term_months + 1):
        principal_payment = loan_amount / loan_term_months
        interest_payment = remaining_balance * monthly_rate / 100
        total_payment_month = principal_payment + interest_payment
        remaining_balance -= principal_payment
        
        payment_schedule.append({
            'Bulan': month,
            'Cicilan_Pokok': principal_payment,
            'Cicilan_Bunga': interest_payment,
            'Total_Cicilan': total_payment_month,
            'Sisa_Pinjaman': max(0, remaining_balance)
        })
    
    schedule_df = pd.DataFrame(payment_schedule)
    
    # Add comparison data
    comparison_df = df_comparison.copy()
    
    export_data = create_export_data("Pinjaman Online/Fintech", input_params, results, schedule_df)
    export_data['platform_comparison'] = comparison_df.to_dict('records')
    
    with col_export1:
        # CSV Export
        csv_data = export_to_csv(schedule_df, "pinjol_schedule.csv")
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"pinjol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_export2:
        # Excel Export
        excel_data = export_to_excel(export_data, "pinjol_analysis.xlsx")
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"pinjol_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_export3:
        # Summary Report
        summary_report = create_summary_report("Pinjaman Online/Fintech", input_params, results)
        st.download_button(
            label="📋 Download Report",
            data=summary_report,
            file_name=f"pinjol_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

elif calculator_type == "Perbandingan Skenario":
    st.header("⚖️ Perbandingan Multiple Skenario")
    
    st.subheader("Bandingkan Hingga 3 Skenario Kredit")
    
    scenarios = []
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Skenario 1")
        amount_1 = st.number_input("Pinjaman 1 (Rp)", min_value=1000000, value=100000000, step=1000000, key="amount1")
        rate_1 = st.slider("Bunga 1 (%)", min_value=1.0, max_value=30.0, value=10.0, step=0.1, key="rate1")
        term_1 = st.slider("Jangka Waktu 1 (Tahun)", min_value=1, max_value=30, value=5, key="term1")
        
        payment_1 = calculate_loan_payment(amount_1, rate_1, term_1)
        total_1 = payment_1 * term_1 * 12
        interest_1 = total_1 - amount_1
        
        scenarios.append({
            'Skenario': 'Skenario 1',
            'Pinjaman': amount_1,
            'Bunga': rate_1,
            'Jangka_Waktu': term_1,
            'Cicilan_Bulanan': payment_1,
            'Total_Pembayaran': total_1,
            'Total_Bunga': interest_1
        })
        
        st.metric("Cicilan Bulanan", format_currency(payment_1))
        st.metric("Total Bunga", format_currency(interest_1))
    
    with col2:
        st.subheader("Skenario 2")
        amount_2 = st.number_input("Pinjaman 2 (Rp)", min_value=1000000, value=100000000, step=1000000, key="amount2")
        rate_2 = st.slider("Bunga 2 (%)", min_value=1.0, max_value=30.0, value=12.0, step=0.1, key="rate2")
        term_2 = st.slider("Jangka Waktu 2 (Tahun)", min_value=1, max_value=30, value=7, key="term2")
        
        payment_2 = calculate_loan_payment(amount_2, rate_2, term_2)
        total_2 = payment_2 * term_2 * 12
        interest_2 = total_2 - amount_2
        
        scenarios.append({
            'Skenario': 'Skenario 2',
            'Pinjaman': amount_2,
            'Bunga': rate_2,
            'Jangka_Waktu': term_2,
            'Cicilan_Bulanan': payment_2,
            'Total_Pembayaran': total_2,
            'Total_Bunga': interest_2
        })
        
        st.metric("Cicilan Bulanan", format_currency(payment_2))
        st.metric("Total Bunga", format_currency(interest_2))
    
    with col3:
        st.subheader("Skenario 3")
        amount_3 = st.number_input("Pinjaman 3 (Rp)", min_value=1000000, value=100000000, step=1000000, key="amount3")
        rate_3 = st.slider("Bunga 3 (%)", min_value=1.0, max_value=30.0, value=15.0, step=0.1, key="rate3")
        term_3 = st.slider("Jangka Waktu 3 (Tahun)", min_value=1, max_value=30, value=10, key="term3")
        
        payment_3 = calculate_loan_payment(amount_3, rate_3, term_3)
        total_3 = payment_3 * term_3 * 12
        interest_3 = total_3 - amount_3
        
        scenarios.append({
            'Skenario': 'Skenario 3',
            'Pinjaman': amount_3,
            'Bunga': rate_3,
            'Jangka_Waktu': term_3,
            'Cicilan_Bulanan': payment_3,
            'Total_Pembayaran': total_3,
            'Total_Bunga': interest_3
        })
        
        st.metric("Cicilan Bulanan", format_currency(payment_3))
        st.metric("Total Bunga", format_currency(interest_3))
    
    # Tabel perbandingan
    st.subheader("📊 Tabel Perbandingan")
    df_comparison = pd.DataFrame(scenarios)
    
    # Format currency columns
    df_display = df_comparison.copy()
    df_display['Pinjaman'] = df_display['Pinjaman'].apply(format_currency)
    df_display['Cicilan_Bulanan'] = df_display['Cicilan_Bulanan'].apply(format_currency)
    df_display['Total_Pembayaran'] = df_display['Total_Pembayaran'].apply(format_currency)
    df_display['Total_Bunga'] = df_display['Total_Bunga'].apply(format_currency)
    df_display['Bunga'] = df_display['Bunga'].apply(lambda x: f"{x}%")
    df_display['Jangka_Waktu'] = df_display['Jangka_Waktu'].apply(lambda x: f"{x} Tahun")
    
    st.dataframe(df_display, use_container_width=True)
    
    # Grafik perbandingan
    st.subheader("📈 Grafik Perbandingan")
    
    # Perbandingan cicilan bulanan
    fig1 = px.bar(df_comparison, x='Skenario', y='Cicilan_Bulanan', 
                  title='Perbandingan Cicilan Bulanan',
                  color='Skenario')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Perbandingan total bunga
    fig2 = px.bar(df_comparison, x='Skenario', y='Total_Bunga', 
                  title='Perbandingan Total Bunga',
                  color='Skenario')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Export functionality for Scenario Comparison
    st.subheader("📥 Export Data")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    # Prepare export data
    input_params = {
        'Jumlah Skenario': len(scenarios),
        'Skenario 1 - Pinjaman': amount_1,
        'Skenario 1 - Bunga': rate_1,
        'Skenario 1 - Jangka Waktu': term_1,
        'Skenario 2 - Pinjaman': amount_2,
        'Skenario 2 - Bunga': rate_2,
        'Skenario 2 - Jangka Waktu': term_2,
        'Skenario 3 - Pinjaman': amount_3,
        'Skenario 3 - Bunga': rate_3,
        'Skenario 3 - Jangka Waktu': term_3
    }
    
    results = {
        'Skenario Terbaik (Cicilan Terendah)': df_comparison.loc[df_comparison['Cicilan_Bulanan'].idxmin(), 'Skenario'],
        'Skenario Terbaik (Total Bunga Terendah)': df_comparison.loc[df_comparison['Total_Bunga'].idxmin(), 'Skenario'],
        'Selisih Cicilan (Max-Min)': format_currency(df_comparison['Cicilan_Bulanan'].max() - df_comparison['Cicilan_Bulanan'].min()),
        'Selisih Total Bunga (Max-Min)': format_currency(df_comparison['Total_Bunga'].max() - df_comparison['Total_Bunga'].min())
    }
    
    # Create detailed comparison data
    comparison_detailed = pd.DataFrame(scenarios)
    
    export_data = create_export_data("Perbandingan Skenario", input_params, results, comparison_detailed)
    
    with col_export1:
        # CSV Export
        csv_data = export_to_csv(comparison_detailed, "scenario_comparison.csv")
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"perbandingan_skenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_export2:
        # Excel Export
        excel_data = export_to_excel(export_data, "scenario_analysis.xlsx")
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"perbandingan_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_export3:
        # Summary Report
        summary_report = create_summary_report("Perbandingan Skenario", input_params, results)
        st.download_button(
            label="📋 Download Report",
            data=summary_report,
            file_name=f"perbandingan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>💰 <strong>Kalkulator Cicilan & Bunga Pro</strong> - Developed by [Your Name]</p>
    <p>📧 Email: your.email@domain.com | 📱 WhatsApp: +62-xxx-xxx-xxxx</p>
    <p><em>Disclaimer: Perhitungan ini bersifat estimasi. Untuk keputusan finansial yang tepat, konsultasikan dengan ahli keuangan.</em></p>
</div>
""", unsafe_allow_html=True)

# Sidebar Export Section
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Export Center")
st.sidebar.markdown("""
**Fitur Export Tersedia:**
- 📄 CSV untuk data tabel
- 📊 Excel untuk analisis lengkap  
- 📋 Report untuk ringkasan
- 📈 JSON untuk integrasi sistem

**Export tersedia di setiap kalkulator**
""")

if st.sidebar.button("ℹ️ Panduan Export"):
    st.sidebar.info("""
    **Cara menggunakan export:**
    1. Pilih kalkulator yang diinginkan
    2. Input parameter yang sesuai
    3. Scroll ke bawah untuk melihat section 'Export Data'
    4. Pilih format export yang diinginkan
    5. Klik tombol download
    """)

# Additional Export Features
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Tools Tambahan")

if st.sidebar.button("📊 Export All Calculator Summary"):
    all_calculators = [
        "Simulasi Kredit Bank",
        "Bunga Majemuk", 
        "Investasi Deposito",
        "Cicilan Kendaraan",
        "Cicilan Properti",
        "Pinjaman Online/Fintech"
    ]
    
    summary_data = {
        'app_info': {
            'name': 'Kalkulator Cicilan & Bunga Pro',
            'version': '2.3',
            'total_platforms': '100+',
            'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        'calculators': all_calculators,
        'platform_count': {
            'Vehicle Financing': '40+',
            'KPR/Property': '30+', 
            'Online Lending': '35+'
        }
    }
    
    json_data = json.dumps(summary_data, indent=2, ensure_ascii=False)
    st.sidebar.download_button(
        label="📄 Download App Summary",
        data=json_data,
        file_name=f"app_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
