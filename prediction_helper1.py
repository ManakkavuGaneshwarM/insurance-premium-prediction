import pandas as pd
import pickle

# Load scalers and models
with open('artifacts1/scaler_young.pkl', 'rb') as f:
    scaler_young = pickle.load(f)
with open('artifacts1/scaler_rest.pkl', 'rb') as f:
    scaler_rest = pickle.load(f)

with open('artifacts1/model_young.pkl', 'rb') as f:
    model_young = pickle.load(f)
with open('artifacts1/model_rest.pkl', 'rb') as f:
    model_rest = pickle.load(f)

#calculating the normalized_risk_score
def calculate_normalized_risk(medical_history):
    risk_scores = {
        "diabetes": 6,
        "heart disease": 8,
        "high blood pressure": 6,
        "thyroid": 5,
        "no disease": 0,
        "none": 0
    }
    diseases = medical_history.lower().split(" & ")
    total_risk_score = sum(risk_scores.get(disease.strip(), 0) for disease in diseases)
    
    max_score = 14
    min_score = 0
    
    normalized_risk_score = (total_risk_score - min_score)/(max_score - min_score)
    return normalized_risk_score

#calculating the life style risk score
def calculate_life_style_risk_score(physical_activity, stress_level):
    physical_activity_encoding = {'High': 0, 'Medium': 1, 'Low': 4}
    stress_level_encoding = {'Low': 0, 'Medium': 1, 'High': 4}
    return physical_activity_encoding.get(physical_activity, 0) + stress_level_encoding.get(stress_level, 0)

#preprocessing the features 
def preprocess_input(input_dict):
    expected_columns = [
        'age', 'number_of_dependants', 'income_lakhs', 'insurance_plan',
        'normalized_risk_score', 'life_style_risk_score', 'gender_Male',
        'region_Northwest', 'region_Southeast', 'region_Southwest',
        'marital_status_Unmarried', 'bmi_category_Obesity',
        'bmi_category_Overweight', 'bmi_category_Underweight',
        'smoking_status_Occasional', 'smoking_status_Regular',
        'employment_status_Salaried', 'employment_status_Self-Employed'
    ]

    insurance_plan_encoding = {'Bronze': 1, 'Silver': 2, 'Gold': 3}
    df = pd.DataFrame(0, columns=expected_columns, index=[0])
    
    #numerical variable preprocessing
    df['age'] = input_dict.get('Age', 0)
    df['number_of_dependants'] = input_dict.get('Number of Dependants', 0)
    df['income_lakhs'] = input_dict.get('Income in Lakhs', 0)
    df['insurance_plan'] = insurance_plan_encoding.get(input_dict.get('Insurance Plan', 'Bronze'), 1)
    df['normalized_risk_score'] = calculate_normalized_risk(input_dict.get('Medical History', 'none'))
    df['life_style_risk_score'] = calculate_life_style_risk_score(
        input_dict.get('Physical Activity', 'Medium'),
        input_dict.get('Stress Level', 'Medium')
    )
    
    #categorical features preprocessing
    if input_dict.get('Gender') == 'Male':
        df['gender_Male'] = 1

    region = input_dict.get('Region', '')
    if region in ['Northwest', 'Southeast', 'Southwest']:
        df[f'region_{region}'] = 1

    if input_dict.get('Marital Status') == 'Unmarried':
        df['marital_status_Unmarried'] = 1

    bmi_cat = input_dict.get('BMI Category', '')
    if bmi_cat in ['Obesity', 'Overweight', 'Underweight']:
        df[f'bmi_category_{bmi_cat}'] = 1

    smoking = input_dict.get('Smoking Status', '')
    if smoking in ['Occasional', 'Regular']:
        df[f'smoking_status_{smoking}'] = 1

    employment = input_dict.get('Employment Status', '')
    if employment in ['Salaried', 'Self-Employed']:
        df[f'employment_status_{employment}'] = 1

    return handle_scaling(df['age'].values[0], df)

#scaling the features based on the age
def handle_scaling(age, df):
    scaler_object = scaler_young if age <= 25 else scaler_rest
    cols_to_scale = scaler_object['cols_to_scale']
    scaler = scaler_object['scaler']
    df[cols_to_scale] = scaler.transform(df[cols_to_scale])
    return df

#data preprocessing and model prediction
def predict(input_dict):
    input_df = preprocess_input(input_dict)
    model = model_young if input_dict['Age'] <= 25 else model_rest
    prediction = model.predict(input_df)
    return int(prediction)
