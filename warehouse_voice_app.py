import streamlit as st
import pandas as pd
import speech_recognition as sr

# Load user data
def load_users():
    try:
        users_df = pd.read_csv("users.csv")
        return users_df
    except FileNotFoundError:
        st.error("Error: users.csv file not found!")
        return None

# Authenticate user
def authenticate(username, password):
    users_df = load_users()
    if users_df is not None:
        user = users_df[(users_df["username"] == username) & (users_df["password"] == password)]
        if not user.empty:
            return user.iloc[0]["role"]  # Return user role
    return None

# Load inventory data
@st.cache_data
def load_inventory():
    try:
        df = pd.read_excel("cleaned_voice_picking_data.xlsx")  # Update with your actual data file
        return df
    except FileNotFoundError:
        st.error("Error: Inventory data file not found!")
        return None

# Speech-to-text function
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 Listening... Speak now")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success(f"🗣 Recognized: {text}")
            return text
        except sr.UnknownValueError:
            st.error("❌ Could not understand the speech. Please try again.")
            return ""
        except sr.RequestError:
            st.error("❌ Speech service is unavailable. Check your internet connection.")
            return ""

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

# Login section
if not st.session_state.logged_in:
    st.title("🔑 Warehouse Voice Inventory System - Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.user_role = role
            st.success(f"✅ Logged in as {role}")
            st.rerun()
        else:
            st.error("❌ Invalid username or password!")

else:
    st.title("📦 Warehouse Voice Inventory System")

    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()

    # Load inventory
    inventory_df = load_inventory()
    
    if inventory_df is not None:
        st.write("### 📋 Inventory Data")
        st.dataframe(inventory_df)

        # Search function for stock location
        st.write("#### 🔎 Find Stock Location")
        stock_name = st.text_input("Enter stock name (e.g., 'Salmon')") 
        if st.button("🎤 Speak", key="stock_location_voice"):
            stock_name = recognize_speech()
        if st.button("Find Stock Location"):
            stock_result = inventory_df[inventory_df["Stock Name"].str.contains(stock_name, case=False, na=False)]
            if not stock_result.empty:
                for index, row in stock_result.iterrows():
                    st.success(f"📍 {row['Stock Name']} is located at {row['Location']}")
            else:
                st.warning("❌ Stock not found!")

        # Check stock quantity
        st.write("#### 📦 Check Stock Quantity")
        stock_quantity_check = st.text_input("Enter stock name (e.g., 'Shrimp')")
        if st.button("🎤 Speak", key="stock_quantity_voice"):
            stock_quantity_check = recognize_speech()
        if st.button("Check Quantity"):
            quantity_result = inventory_df[inventory_df["Stock Name"].str.contains(stock_quantity_check, case=False, na=False)]
            if not quantity_result.empty:
                for index, row in quantity_result.iterrows():
                    st.success(f"📦 {row['Stock Name']} has {row['Quantity']} units in stock.")
            else:
                st.warning("❌ Stock not found!")

        # Stock replenishment date
        st.write("#### 🔄 Check Replenishment Date")
        stock_replenish_check = st.text_input("Enter stock name (e.g., 'Tuna')")
        if st.button("🎤 Speak", key="replenish_voice"):
            stock_replenish_check = recognize_speech()
        if st.button("Check Replenishment Date"):
            replenish_result = inventory_df[inventory_df["Stock Name"].str.contains(stock_replenish_check, case=False, na=False)]
            if not replenish_result.empty:
                for index, row in replenish_result.iterrows():
                    st.info(f"🔄 {row['Stock Name']} should be restocked by {row['Replenishment Date']}.")
            else:
                st.warning("❌ No restocking information found!")

