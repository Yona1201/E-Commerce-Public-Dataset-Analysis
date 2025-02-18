import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib

# Custom Functions
class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={"product_id": "product_count"}, inplace=True)
        sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)
        return sum_order_items_df

    def review_score_df(self):
        review_scores = self.df['review_score'].value_counts().sort_values(ascending=False)
        most_common_score = review_scores.idxmax()
        return review_scores, most_common_score

    def create_bystate_df(self):
        bystate_df = self.df.groupby(by="customer_state").customer_id.nunique().reset_index()
        bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
        most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
        bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)
        return bystate_df, most_common_state

    def create_order_status(self):
        order_status_df = self.df["order_status"].value_counts().sort_values(ascending=False)
        most_common_status = order_status_df.idxmax()
        return order_status_df, most_common_status


class BrazilMapPlotter:
    def __init__(self, data, plt, mpimg, urllib, st):
        self.data = data
        self.plt = plt
        self.mpimg = mpimg
        self.urllib = urllib
        self.st = st

    def plot(self):
        brazil = self.mpimg.imread(self.urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'), 'jpg')
        ax = self.data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10, 10), alpha=0.3, s=0.3, c='#9B59B6')
        self.plt.axis('off')
        self.plt.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
        self.st.pyplot()


# Main Code
sns.set(style='dark')


# Load datasets
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("data/all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

geolocation = pd.read_csv('data/geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

# Convert datetime columns
for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    st.title("Proyek Analisis Data: [E-Commerce Public Dataset]")
    st.image("https://img.freepik.com/free-vector/ecommerce-checkout-laptop-concept-illustration_114360-8243.jpg")
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Filter data based on selected date range
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & (all_df["order_approved_at"] <= str(end_date))]

# Initialize function objects
function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

# Prepare data for visualization
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Title
st.header("E-Commerce Dashboard :")

# Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)
with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")
with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))
colors = ["#9B59B6", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fig)

# Review Score
st.subheader("Review Score")
col1, col2 = st.columns(2)
with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score}**")
with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index, y=review_score.values, order=review_score.index, palette=["#9B59B6" if score == common_score else "#D3D3D3" for score in review_score.index])
plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)

# Customer Demographic
st.subheader("Geolocation")

# Geolocation Plot
map_plot.plot()
