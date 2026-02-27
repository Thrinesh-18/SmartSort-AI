Smart Sort AI

AI-Powered Plastic Waste Classification for Smart Recycling

Smart Sort AI is an intelligent waste classification system that uses Deep Learning and Computer Vision to identify plastic types from images. The system classifies waste into:

♻️ PET

♻️ HDPE

♻️ Others

Built using TensorFlow, deployed with FastAPI, and presented through an interactive Streamlit dashboard, Smart Sort AI enables real-time predictions to support efficient waste segregation and sustainable recycling practices.

🚀 Features

🔍 Image-based plastic classification using CNN

⚡ Real-time prediction API built with FastAPI

🖥️ Interactive Streamlit web interface

📊 Live analytics dashboard (tracks total predictions & class distribution)

🧠 TensorFlow deep learning model

🌍 Scalable backend architecture

🏗️ System Architecture

User → Streamlit Frontend → FastAPI Backend → TensorFlow Model → Prediction → Analytics Dashboard

🔹 Frontend

Built with Streamlit

Upload image interface

Displays prediction results with confidence score

Analytics dashboard for usage monitoring

🔹 Backend

Built with FastAPI

Handles image preprocessing

Serves model predictions via REST API

Lightweight and high-performance async architecture

🔹 Model

Convolutional Neural Network (CNN)

Trained on labeled plastic waste dataset

Optimized for multi-class classification

🛠️ Tech Stack

Frontend	Streamlit

Backend API	FastAPI

ML Framework	TensorFlow

Language	Python

Deployment	Local / Cloud-ready

📊 Analytics

The system maintains global analytics including:

Total predictions made

Distribution of PET / HDPE / Others classifications

This enables:

Monitoring model usage

Understanding waste trends

Improving future model performance

📦 Installation & Setup

1️⃣ Clone the Repository

git clone https://github.com/your-username/SmartSort-AI.git

cd SmartSort-AI.git

2️⃣ Create Virtual Environment

python -m venv venv

source venv/bin/activate  # Mac/Linux

venv\Scripts\activate     # Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Run FastAPI Backend

uvicorn main:app --reload

5️⃣ Run Streamlit Frontend

streamlit run app.py
