import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


st.set_page_config(page_title="IMDB Movie Analytics", layout="wide")
st.title("🎬 IMDB Top 1000: Executive Dashboard")
st.markdown("Interactive analysis of the world's highest-rated movies.")


@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_imdb_data.csv')
    return df

df = load_data()


st.sidebar.header("Filter Options")


# Year Range Slider
min_year = int(df['year'].min())
max_year = int(df['year'].max())
year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (1990, 2020))

# Genre Dropdown
unique_genres = sorted(list(set(df['genre'].str.split(', ').explode())))
selected_genre = st.sidebar.selectbox("Select Genre", ["All"] + unique_genres)


filtered_df = df[
    (df['year'] >= year_range[0]) & 
    (df['year'] <= year_range[1])
]

if selected_genre != "All":
    filtered_df = filtered_df[filtered_df['genre'].str.contains(selected_genre)]


col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Movies", len(filtered_df))
col2.metric("Avg Rating", f"⭐ {filtered_df['rating'].mean():.1f}")
col3.metric("Avg Revenue", f"💰 ${filtered_df['gross'].median()/1e6:.1f}M")
col4.metric("Avg Runtime", f"⏱️ {int(filtered_df['runtime'].mean())} min")

st.divider()

# 6. VISUALIZATIONS (ROW B: Distributions)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(f"Runtime Distribution: {selected_genre}")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.histplot(filtered_df['runtime'], kde=True, color='teal', bins=20, ax=ax1)
    ax1.set_xlabel("Runtime (Minutes)")
    st.pyplot(fig1)

with col_right:
    st.subheader("Revenue vs. Rating")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=filtered_df, x='rating', y='gross', color='purple', alpha=0.6, ax=ax2)
    ax2.set_yscale('log')
    ax2.set_xlabel("IMDB Rating")
    ax2.set_ylabel("Revenue (Log Scale)")
    st.pyplot(fig2)

st.divider()

# 7. NEW VISUALIZATIONS (ROW C: Market Trends)
col_trend1, col_trend2 = st.columns(2)

with col_trend1:
    st.subheader("Top High-Revenue Genres (In Selection)")
    
    # Data Prep: Explode genres for the bar chart
    df_exploded = filtered_df.copy()
    df_exploded['genre_list'] = df_exploded['genre'].str.split(', ')
    df_exploded = df_exploded.explode('genre_list')
    
    # Calculate avg gross per genre
    genre_gross = df_exploded.groupby('genre_list')['gross'].mean().sort_values(ascending=False).head(10)
    
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.barplot(x=genre_gross.values, y=genre_gross.index, palette='magma', ax=ax3)
    ax3.set_xlabel("Average Revenue ($)")
    st.pyplot(fig3)

with col_trend2:
    st.subheader("Revenue Trend Over Time")
    
    # Data Prep: Group by Year
    year_data = filtered_df.groupby('year')['gross'].mean().reset_index()
    
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=year_data, x='year', y='gross', color='green', linewidth=2.5, ax=ax4)
    ax4.fill_between(year_data['year'], year_data['gross'], color='green', alpha=0.1)
    ax4.set_ylabel("Average Revenue ($)")
    st.pyplot(fig4)

# 8. DATA TABLE 
st.subheader("Top Movies in Selection")
display_cols = ['title', 'year', 'rating', 'gross', 'director']
st.dataframe(filtered_df[display_cols].sort_values(by='rating', ascending=False).head(10))