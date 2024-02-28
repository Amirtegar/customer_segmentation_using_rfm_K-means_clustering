import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt


# Membaca file CSV
saas = pd.read_csv('https://ee-assets-prod-us-east-1.s3.amazonaws.com/modules/337d5d05acc64a6fa37bcba6b921071c/v1/SaaS-Sales.csv')
saas['Order Date'] = pd.to_datetime(saas['Order Date'])

# Produk
product_orders = saas.groupby('Product')['Order Date'].count().reset_index()
product_orders.columns = ['Product', 'Total Orders']
top_5_products = product_orders.sort_values(by='Total Orders', ascending=False).head(5)
bottom_5_products = product_orders.sort_values(by='Total Orders').head(5)

# Industry, Country
order_by_industry = saas.groupby('Industry').size().reset_index(name='Total Orders')
order_by_industry = order_by_industry.sort_values(by='Total Orders', ascending=False)

# Tentukan industri dengan jumlah order paling banyak
top_industry_order = order_by_industry.head(1)

# Hitung jumlah order per negara
order_by_country = saas.groupby('Country').size().reset_index(name='Total Orders')
order_by_country = order_by_country.sort_values(by='Total Orders', ascending=False)

# Tentukan negara dengan jumlah order paling banyak
top_country_order = order_by_country.head(1)


# Menghitung RFM
# Recency
saas_recency = saas.groupby(by='Customer', as_index=False)['Order Date'].max()
saas_recency.columns = ['CustomerName', 'LastPurchaseDate']
recent_date = saas_recency['LastPurchaseDate'].max()
saas_recency["Recency"] = saas_recency['LastPurchaseDate'].apply(lambda x: (recent_date - x).days)

# Frequency
saas_frequency = saas.drop_duplicates().groupby(by=['Customer'], as_index=False)['Order Date'].count()
saas_frequency.columns = ['CustomerName', 'Frequency']
# Monetary
saas['Total'] = saas['Sales']*saas['Quantity']
saas_monetary = saas.groupby(by='Customer', as_index=False)['Total'].sum()
saas_monetary.columns = ['CustomerName', 'Monetary']
saas_monetary['OrderDate'] = saas.groupby('Customer')['Order Date'].first().values
saas_monetary['Segment'] = saas.groupby('Customer')['Segment'].first().values
# RFM
saas_rf = saas_recency.merge(saas_frequency, on='CustomerName')
saas_rfm = saas_rf.merge(saas_monetary, on='CustomerName').drop(columns='LastPurchaseDate')
saas_rfm1 = saas_rfm.drop(columns= 'CustomerName')
saas_rfm1.drop(columns=['OrderDate', 'Segment'], inplace=True)
saas_rfm2 = saas_rfm.drop(columns=['OrderDate', 'Segment'])

#TOP 3 Recency
fig3 = pd.DataFrame(saas_rfm)
fig3_sorted_recency = fig3.sort_values(by='Recency', ascending=False).head(3)
fig3_sorted_frequency = fig3.sort_values(by='Frequency', ascending=False).head(3)
fig3_sorted_monetary = fig3.sort_values(by='Monetary', ascending=False).head(3)

# Tren Monetary
saas_monetary['OrderDate'] = pd.to_datetime(saas_monetary['OrderDate'])
saas_monetary['Year'] = saas_monetary['OrderDate'].dt.year
saas_monetary['Year_Month'] = saas_monetary['OrderDate'].dt.to_period('6M')
saas_monthly_monetary = saas_monetary.groupby('Year_Month')['Monetary'].sum().reset_index()
saas_monthly_monetary['Year_Month'] = saas_monthly_monetary['Year_Month'].astype(str)
total_monetary = saas_monetary['Monetary'].sum()
total_order = saas_monetary.shape[0]

# Pie Chart Segment
segment_counts = saas_monetary['Segment'].value_counts()

#Customer Segmentation
data = {
    'Cluster': [0, 1, 2],
    'Count': [270, 24, 3],
    'Percent': [90.9, 8.1, 1.0],
    'CustomText': [
        'Cluster 0: High count, most common cluster.',
        'Cluster 1: Medium count, moderate cluster.',
        'Cluster 2: Low count, least common cluster.'
    ]
}
customer_segmentation = pd.DataFrame(data)
#Menyiapkan aplikasi Streamlit

# Customer Segmentation data
data = {
    'Cluster': [0, 1, 2],
    'Count': [270, 24, 3],
    'Percent': [90.9, 8.1, 1.0],
    'CustomText': [
        'Cluster 0: At Risk Customer.',
        'Cluster 1: New Customer.',
        'Cluster 2: Churned Customer.'
    ]
}

# Data Frame Customer Segmentation
customer_segmentation = pd.DataFrame(data)


# Judul
st.title('Customer Segmentation Dashboard')
# st.write('Dashboard ini menyajikan analisis segmentasi pelanggan.')
# Main dashboard

# Tabs
menu_options = ["Overview", "EDA", "Customer Segmentation"]
selected_tab = st.sidebar.selectbox("Main Menu", menu_options)

# Display selected tab content
if selected_tab =="Overview":
    st.markdown(
        """
        ### About dataset
        This dataset contains transaction data from a SaaS company selling sales and marketing software to other companies (B2B). In the dataset, each row represents a single transaction/order (9,994 transactions), and the columns include:
        """
    )
    link = "https://ee-assets-prod-us-east-1.s3.amazonaws.com/modules/337d5d05acc64a6fa37bcba6b921071c/v1/SaaS-Sales.csv"
    st.write("[Download Dataset](%s)" % link)

elif selected_tab =="EDA":
    st.subheader("Exploratory Data Analysis")
    col1_left, col2_right = st.columns(2)

    with col1_left:
        st.metric("Total Monetary", value=f"${total_monetary:,.2f}")

    with col2_right:
        st.metric("Total Order", value=total_order)
    # Tren Monetary
    st.write('---')
    fig_tren = px.line(saas_monthly_monetary, x='Year_Month', y='Monetary', title='Monetary Line Chart')
    fig_tren.update_traces(hoverinfo='y')
    st.plotly_chart(fig_tren)
    # Produk
    st.write('---')
    col1, col2 = st.columns(2)

    # Visualisasi untuk produk paling banyak di order
    with col1:
        st.plotly_chart(px.bar(top_5_products, x='Product', y='Total Orders', title='Top 5 Most Ordered Products',width=350, height=400))

    # Visualisasi untuk produk paling sedikit di order
    with col2:
        st.plotly_chart(px.bar(bottom_5_products, x='Product', y='Total Orders', title='Top 5 Least Ordered Products',width=400, height=415))
    st.write('---')
    # Visualisasi Industri
    # st.subheader("Industri dengan Jumlah Order Terbanyak")
    st.plotly_chart(
        px.bar(order_by_industry, x='Total Orders', y='Industry', orientation='h',
               title="Industry with the most orders", width=800, height=400)
    )
    st.write('---')
    # Visualisasi Negara
    st.plotly_chart(
        px.bar(order_by_country, x='Total Orders', y='Country', orientation='h',
               title="Country with the most orders", width=800, height=400)
    )
    # EDA analysis
    # Add your EDA analysis here
else:
    # st.write("Customer Segmentation tab.")
    # Customer Segmentation
    color_discrete_map = {0: 'rgb(31, 119, 180)',  # Biru
                          1: 'rgb(255, 127, 14)',  # Oranye
                          2: 'rgb(44, 160, 44)'}  # Hijau

    # Buat treemap dengan Plotly
    fig_cust = px.treemap(customer_segmentation, path=['Cluster'], values='Count',
                          hover_data=['CustomText'], branchvalues='total',
                          color_continuous_scale='RdYlBu',
                          title='Customer Cluster',
                          labels={'Cluster': 'Cluster ID', 'Count': 'Number of Customers'},
                          template='plotly_dark',  # Tema gelap
                          width=800, height=500)  # Ukuran
    # Tampilkan chart di Streamlit
    st.write("### Customer Segmentation")
    st.plotly_chart(fig_cust, use_container_width=True)
    st.write("Cluster 0 : Customers who make last purchases not too long with relatively moderate purchasing frequency")
    st.write("Cluster 1 : New customers make transactions with not too large amounts of purchases, and ongoing purchase frequency")
    st.write("Cluster 2 : A customer who has not been doing a purchase transaction for a long time, only performs a small purchase. Therefore, it is likely to be a cluster of customers who have lost or quit subscribing.")
    # Pie Chart Segment
    st.write('---')
    # st.subheader('Distribusi Segmen Pelanggan')
    fig_pie = px.pie(names=segment_counts.index, values=segment_counts.values,
                     title='Customer Segment')
    fig_pie.update_traces(hoverinfo='label+percent')
    st.plotly_chart(fig_pie)

    st.write('---')

    # Visualisasi untuk Customer dengan Recency Tertinggi
    # st.header("Customer dengan Recency Tertinggi")
    fig_recency = px.bar(saas_rfm, x='CustomerName', y='Recency', title='Recency',
                         labels={'Recency': 'Recency'}, text='Recency')
    fig_recency.update_layout(width=800, height=500,
                              xaxis_tickangle=-45)  # Menyesuaikan ukuran dan memutar label sumbu x
    st.plotly_chart(fig_recency)

    st.write('---')

    # Visualisasi untuk Customer dengan Frequency Tertinggi
    # st.header("Customer dengan Frequency Tertinggi")
    fig_frequency = px.bar(saas_rfm, x='CustomerName', y='Frequency', title='Frequency',
                           labels={'Frequency': 'Frequency'}, text='Frequency')
    fig_frequency.update_layout(width=800, height=500,
                                xaxis_tickangle=-45)  # Menyesuaikan ukuran dan memutar label sumbu x
    st.plotly_chart(fig_frequency)

    st.write('---')

    # Visualisasi untuk Customer dengan Monetary Tertinggi
    # st.header("Customer dengan Monetary Tertinggi")
    fig_monetary = px.bar(saas_rfm, x='CustomerName', y='Monetary', title='Monetary',
                          labels={'Monetary': 'Monetary'}, text='Monetary')
    fig_monetary.update_layout(width=800, height=500,
                               xaxis_tickangle=-45)  # Menyesuaikan ukuran dan memutar label sumbu x
    st.plotly_chart(fig_monetary)

    st.write('---')
    st.subheader("Actonable Insight")
    st.write("New Customers, To convert them into Champion customers, the Online Store should engage them more frequently")
    st.write("At Risk Customer,The online store should offer the customer popular products at a discount or reconnect the customer")
    st.write("Churned Customer, A marketing campaign should be launched to revive interest in online stores")


st.markdown(
    """
    <style>
    .reportview-container {
        background: #f0f2f6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

