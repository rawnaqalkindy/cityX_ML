# model.py
# Code from Level 2
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

 
base_path = "/app/"
csv_path = os.path.join(base_path, "Competition_Dataset.csv")

def load_and_train_model():

    df = pd.read_csv(csv_path)
    df['Dates'] = pd.to_datetime(df['Dates'])
    df['Year'] = df['Dates'].dt.year
    df['Month'] = df['Dates'].dt.month
    df['Day'] = df['Dates'].dt.day
    df['Hour'] = df['Dates'].dt.hour
    df['DayOfWeek'] = df['Dates'].dt.day_name()
    df.drop_duplicates(inplace=True)
    df.columns = df.columns.str.strip().str.lower()
    df['descript'] = df['descript'].astype(str)
    df['category'] = df['category'].astype(str)

    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X = vectorizer.fit_transform(df['descript'])
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df['category'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = SVC(kernel='linear', random_state=42)
    model.fit(X_train, y_train)

    return vectorizer, model, label_encoder

def assign_severity(category):
    if category in ['NON-CRIMINAL', 'SUSPICIOUS OCCURRENCE', 'MISSING PERSON', 'RUNAWAY', 'RECOVERED VEHICLE', 'SUSPICIOUS OCC']:
        return 1 
    elif category in ['WARRANTS', 'OTHER OFFENSES', 'VANDALISM', 'TRESPASS', 'DISORDERLY CONDUCT', 'BAD CHECKS']:
        return 2  
    elif category in ['LARCENY/THEFT', 'VEHICLE THEFT', 'FORGERY/COUNTERFEITING', 'DRUG/NARCOTIC', 
                      'STOLEN PROPERTY', 'FRAUD', 'BRIBERY', 'EMBEZZLEMENT']:
        return 3 
    elif category in ['ROBBERY', 'WEAPON LAWS', 'BURGLARY', 'EXTORTION']:
        return 4  
    elif category in ['KIDNAPPING', 'ARSON']:
        return 5 
    else:
        return None


