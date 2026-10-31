> **Disclaimer:** Educational Flask demo: symptom-based disease prediction with medication and diet suggestions. Not medical advice.

# Personalized Medical Recommendation System

An AI-powered health assistant that helps users identify potential diseases based on symptoms and provides personalized recommendations for medications, diet, workouts, and precautions.

## 🚀 Features

- **Symptom-Based Disease Prediction** - Input symptoms to get instant disease predictions
- **Voice Recognition Support** - Describe symptoms using voice input (mic-enabled devices)
- **Personalized Recommendations** - Get suggestions for:
  - Top 5 medications
  - Precautionary measures  
  - Diet plans
  - Workout routines
- **Web Interface** - User-friendly Flask web application
- **Privacy Focused** - User data is processed locally and securely

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 2. Clone & Setup
```bash
# Clone repository
git clone https://github.com/bmo1177/medsrecommendation.git
cd medsrecommendation

# Create virtual environment (Recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Required Files
Ensure these files are in your project directory:
- `model.pkl` - Trained machine learning model
- `symptom_df.txt` - List of recognized symptoms  
- `medications.csv` - Medication database
- `diets.csv` - Diet recommendations
- `test.txt` - Sample symptoms for testing

### 4. Run Application
```bash
python main.py
```
Then open your browser to: `http://127.0.0.1:5000`

## 📁 Project Structure
```
medsrecommendation/
├── main.py                 # Main application
├── model.pkl              # Trained ML model
├── symptom_df.txt         # Symptom database
├── medications.csv        # Medication data
├── diets.csv             # Diet recommendations
├── requirements.txt       # Dependencies
└── test.txt              # Sample symptoms
```

## 🧪 Testing
Use `test.txt` with sample symptoms:
```
fatigue, weight_loss, restlessness, lethargy
fever, cough, headache, body_pain
```

## 👥 Developers
Educational project Only.

## ⚠️ Important Disclaimer
> **Warning**: This system is for **educational purposes only**. Not intended to replace professional medical advice. Always consult healthcare providers for medical decisions.

## 📄 License
Academic project 


