import streamlit as st
# Set page config first
st.set_page_config(
    page_title="Carbon Footprint Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
import re
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Define product data with categories and carbon footprint
products_data = {
    "Laptop": {"category": "Electronics", "base_footprint": 300},
    "Smartphone": {"category": "Electronics", "base_footprint": 100},
    "Headphones": {"category": "Electronics", "base_footprint": 30},
    "Smartwatch": {"category": "Electronics", "base_footprint": 50},
    "Tablet": {"category": "Electronics", "base_footprint": 150},
    "Camera": {"category": "Electronics", "base_footprint": 80},
    "Coffee Maker": {"category": "Appliances", "base_footprint": 120},
    "Air Purifier": {"category": "Appliances", "base_footprint": 200},
    "Electric Kettle": {"category": "Appliances", "base_footprint": 60},
    "Vacuum Cleaner": {"category": "Appliances", "base_footprint": 180}
}

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .title-container {
        background-color: #1E1E1E;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-title {
        color: #4CAF50;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        color: #FFFFFF;
        font-size: 1.2rem;
    }
    .stMetric {
        background-color: #2E2E2E;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #4CAF50;
    }
    .metric-label {
        color: #4CAF50 !important;
        font-weight: bold;
    }
    .chart-container {
        background-color: #2E2E2E;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .streamlit-expanderHeader {
        background-color: #2E2E2E;
        border-radius: 10px;
        color: #4CAF50;
    }
    .uploadedFile {
        background-color: #2E2E2E;
        border-radius: 10px;
        padding: 1rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .css-1d391kg {
        background-color: #1E1E1E;
    }
    .stDataFrame {
        background-color: #2E2E2E;
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def generate_sample_email():
    """Generate a sample email for demonstration"""
    product = random.choice(list(products_data.keys()))
    customer_name = fake.name()
    order_id = fake.uuid4()
    amount = f"${random.uniform(20, 2000):.2f}"
    date = fake.date_this_year().strftime("%Y-%m-%d")

    return (
        f"Hello {customer_name},\n\n"
        f"Thank you for purchasing the {product}. Your order ID is {order_id}. "
        f"The total amount of {amount} was successfully processed on {date}. "
        "We'll notify you once your item ships.\n\n"
        "Best Regards,\nSales Team"
    )

def extract_entities(text):
    """Extract entities from text using rule-based approach"""
    entities = {
        "Product_Name": "",
        "Amount": "",
        "Date": "",
        "Order_ID": ""
    }
    
    # Extract product name
    for product in products_data.keys():
        if product in text:
            entities["Product_Name"] = product
            break
    
    # Extract amount
    amount_pattern = r'\$\d+(?:\.\d{2})?'
    amount_match = re.search(amount_pattern, text)
    if amount_match:
        entities["Amount"] = amount_match.group()
    
    # Extract date
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    date_match = re.search(date_pattern, text)
    if date_match:
        entities["Date"] = date_match.group()
    
    # Extract order ID
    order_pattern = r'order ID is ([A-Za-z0-9-]+)'
    order_match = re.search(order_pattern, text)
    if order_match:
        entities["Order_ID"] = order_match.group(1)
    
    return entities

def calculate_carbon_footprint(product_name):
    """Calculate carbon footprint for a product"""
    if product_name in products_data:
        return products_data[product_name]["base_footprint"]
    return 0

def create_plotly_theme():
    """Create a consistent theme for Plotly charts"""
    return {
        'layout': {
            'paper_bgcolor': '#2E2E2E',
            'plot_bgcolor': '#2E2E2E',
            'font': {'color': '#FFFFFF'},
            'title': {'font': {'color': '#4CAF50'}},
            'xaxis': {
                'gridcolor': '#444444',
                'linecolor': '#444444',
                'tickfont': {'color': '#FFFFFF'}
            },
            'yaxis': {
                'gridcolor': '#444444',
                'linecolor': '#444444',
                'tickfont': {'color': '#FFFFFF'}
            }
        }
    }
def process_emails(emails):
    """Process list of emails and return transactions"""
    all_transactions = []
    
    with st.spinner('Processing emails...'):
        for email_content in emails:
            entities = extract_entities(email_content)
            
            if entities["Product_Name"]:
                carbon_footprint = calculate_carbon_footprint(entities["Product_Name"])
                
                transaction = {
                    "date": entities["Date"],
                    "product": entities["Product_Name"],
                    "amount": entities["Amount"],
                    "order_id": entities["Order_ID"],
                    "carbon_footprint": carbon_footprint
                }
                
                all_transactions.append(transaction)
    
    return all_transactions

def display_analysis(transactions):
    """Display the analysis dashboard"""
    try:
        if not transactions:
            return
        
        df = pd.DataFrame(transactions)
        
        # Convert amount strings to numeric values for calculations
        df['amount_numeric'] = df['amount'].str.replace('$', '').astype(float)
        
        # Get unique products count
        unique_products = len(df['product'].unique())
        
        # Metrics row
        st.markdown("### 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Carbon Footprint",
                f"{df['carbon_footprint'].sum():.2f} kg CO2",
                delta=f"{df['carbon_footprint'].mean():.2f} kg avg"
            )
        
        with col2:
            st.metric(
                "Number of Transactions",
                len(df),
                delta=f"{unique_products} unique products"
            )
        
        with col3:
            st.metric(
                "Highest Impact Product",
                df.loc[df['carbon_footprint'].idxmax(), 'product'],
                delta=f"{df['carbon_footprint'].max():.2f} kg CO2"
            )
        
        with col4:
            st.metric(
                "Total Spend",
                f"${df['amount_numeric'].sum():.2f}",
                delta="total"
            )
        
        # Charts
        st.markdown("### 📈 Visualization")
        col1, col2 = st.columns(2)
        
        with col1:
            # Product Impact Chart
            fig1 = px.bar(
                df,
                x='product',
                y='carbon_footprint',
                title='Carbon Footprint by Product',
                color='carbon_footprint',
                color_continuous_scale='viridis'
            )
            fig1.update_layout(**create_plotly_theme()['layout'])
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Time Series Chart
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df_sorted = df.sort_values('date')
                fig2 = px.line(
                    df_sorted,
                    x='date',
                    y='carbon_footprint',
                    title='Carbon Footprint Trend',
                    markers=True
                )
                fig2.update_layout(**create_plotly_theme()['layout'])
                st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed Analysis
        st.markdown("### 🔍 Detailed Analysis")
        
        # Transaction Table (Full width)
        st.markdown("#### Transaction Details")
        display_df = df.drop('amount_numeric', axis=1)
        
        styled_df = display_df.style.background_gradient(
            subset=['carbon_footprint'],
            cmap='RdYlGn_r'
        )
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Sustainability Suggestions (Full width)
        st.markdown("#### 💡 Sustainability Suggestions")
        high_impact_products = df.groupby('product')['carbon_footprint'].sum().sort_values(ascending=False)
        
        for product, footprint in high_impact_products.items():
            with st.expander(f"Suggestions for {product}"):
                lower_footprint_products = {
                    k: v for k, v in products_data.items()
                    if v['base_footprint'] < products_data[product]['base_footprint']
                    and v['category'] == products_data[product]['category']
                }
                
                if lower_footprint_products:
                    st.write("🌱 Alternative products with lower carbon footprint:")
                    for alt_product, alt_data in lower_footprint_products.items():
                        reduction = ((products_data[product]['base_footprint'] - alt_data['base_footprint']) 
                                  / products_data[product]['base_footprint'] * 100)
                        st.markdown(f"""
                            - **{alt_product}**
                            - Potential reduction: `{reduction:.1f}%`
                            - CO2 savings: `{products_data[product]['base_footprint'] - alt_data['base_footprint']:.1f} kg`
                        """)
                else:
                    st.success(f"✅ {product} is already among the lower carbon footprint options in its category.")
                    
    except Exception as e:
        st.error(f"Error in analysis: {str(e)}")

def main():
    # Custom header
    st.markdown("""
        <div class="title-container">
            <h1 class="main-title">🌍 Email Carbon Footprint Analyzer</h1>
            <p class="subtitle">Analyze your purchase emails and track your carbon footprint</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "",
            ["Dashboard", "Upload Emails", "Analysis", "About"],
            label_visibility="collapsed"
        )
    
    if page == "Dashboard":
        # Sample data option with improved UI
        col1, col2 = st.columns([2, 1])
        with col1:
            use_sample = st.checkbox(
                "Use sample data for demonstration",
                value=True,
                help="Generate sample emails for demonstration purposes"
            )
        
        if use_sample:
            with col2:
                num_samples = st.slider(
                    "Number of sample emails",
                    1, 10, 5,
                    help="Select the number of sample emails to generate"
                )
            
            # Generate and process sample emails
            sample_emails = [generate_sample_email() for _ in range(num_samples)]
            all_transactions = process_emails(sample_emails)
            
            # Show sample emails in expandable sections
            with st.expander("📧 View Sample Emails", expanded=False):
                for i, email in enumerate(sample_emails, 1):
                    st.markdown(f"**Email {i}**")
                    st.text_area("", email, height=100, key=f"email_{i}")
        else:
            st.info("Please switch to the Upload Emails page to process your own emails.")
            all_transactions = []
    
    elif page == "Upload Emails":
        st.markdown("### 📤 Upload Your Emails")
        
        uploaded_files = st.file_uploader(
            "Upload your email files (text format)",
            accept_multiple_files=True,
            type=['txt'],
            help="Select one or more text files containing email content"
        )
        
        if uploaded_files:
            emails = []
            for uploaded_file in uploaded_files:
                email_content = uploaded_file.getvalue().decode('utf-8')
                emails.append(email_content)
            
            all_transactions = process_emails(emails)
            
            with st.expander("📧 View Uploaded Emails", expanded=False):
                for i, email in enumerate(emails, 1):
                    st.markdown(f"**Email {i}**")
                    st.text_area("", email, height=100, key=f"uploaded_email_{i}")
        else:
            st.info("👆 Upload your email files above to start the analysis")
            all_transactions = []
    
    elif page == "Analysis":
        st.markdown("### 📊 Detailed Analysis")
        if 'all_transactions' not in locals() or not all_transactions:
            st.warning("No data available for analysis. Please generate sample data or upload emails.")
            return
    
    elif page == "About":
        st.markdown("""
            ### About the Carbon Footprint Analyzer
            
            This application helps you track and analyze the carbon footprint of your purchases
            by processing your email receipts. Key features include:
            
            - 📧 Email parsing and analysis
            - 📊 Interactive dashboards
            - 💡 Sustainability suggestions
            - 📈 Trend analysis
            
            #### How it works
            
            1. Upload your purchase confirmation emails
            2. Our system analyzes the products and purchase patterns
            3. View your carbon footprint metrics and trends
            4. Get personalized suggestions for reducing your impact
            
            #### Features
            
            - **Email Analysis**: Automatically extracts purchase information
            - **Carbon Tracking**: Calculates the carbon footprint of purchases
            - **Smart Suggestions**: Provides personalized recommendations
            - **Interactive Dashboard**: Visualize your environmental impact
            - **Privacy Focused**: All processing is done locally
            
            #### Supported Products
            
            Currently, we analyze carbon footprint for the following categories:
            
            **Electronics**
            - Laptops (300 kg CO2)
            - Smartphones (100 kg CO2)
            - Headphones (30 kg CO2)
            - Smartwatches (50 kg CO2)
            - Tablets (150 kg CO2)
            - Cameras (80 kg CO2)
            
            **Appliances**
            - Coffee Makers (120 kg CO2)
            - Air Purifiers (200 kg CO2)
            - Electric Kettles (60 kg CO2)
            - Vacuum Cleaners (180 kg CO2)
            
            #### Privacy Notice
            
            Your email data is processed locally and is not stored or shared.
            We take your privacy seriously and implement the following measures:
            
            - No data storage
            - Local processing only
            - No external API calls
            - No tracking or analytics
            
            #### Tips for Reducing Your Carbon Footprint
            
            1. **Choose Energy-Efficient Products**
               - Look for energy star ratings
               - Research product lifecycle emissions
               
            2. **Extend Product Lifespan**
               - Regular maintenance
               - Repair instead of replace
               
            3. **Sustainable Shopping Habits**
               - Buy refurbished when possible
               - Consider second-hand options
               
            4. **Responsible Disposal**
               - Recycle electronics properly
               - Donate working devices
            
            #### Version Information
            
            - Current Version: 1.0.0
            - Last Updated: October 2024
            - Framework: Streamlit
            - Data Processing: Python
        """)
        
        # Add a feedback section
        st.markdown("### 📝 Feedback")
        with st.form("feedback_form"):
            st.write("Help us improve!")
            feedback_type = st.selectbox(
                "Type of Feedback",
                ["General", "Bug Report", "Feature Request", "Suggestion"]
            )
            feedback_text = st.text_area("Your Feedback")
            submit_button = st.form_submit_button("Submit Feedback")
            
            if submit_button:
                st.success("Thank you for your feedback! We'll review it carefully.")
    
    # Display analysis if there's data
    if any(page == p for p in ["Dashboard", "Upload Emails", "Analysis"]):
        if 'all_transactions' in locals() and all_transactions:
            display_analysis(all_transactions)

if __name__ == "__main__":
    main()
