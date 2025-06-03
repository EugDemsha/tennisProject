# Tennis Stats Scraper and Dashboard

This project scrapes professional tennis match statistics, stores them in a PostgreSQL database, and visualizes them using a Plotly Dash web dashboard.

## 📦 Project Structure

- `scrape_atp` – script to scrape match and player statistics from the ATP website  
- `db` – SQLModel-based models and utility functions for interacting with the PostgreSQL database  
- `deploy` – Dash web app for visualizing player statistics  
- `utils.py` – utility functions for data processing and plotting   

## ⚙️ Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/tennis-dashboard.git
   cd tennis-dashboard
