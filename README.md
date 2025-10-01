# Fraud Detection System Project

All the required files can be downloaded from here, kindly download them and paste on the root folder then run the program, without them the project will not work as intended:
https://drive.google.com/drive/folders/16t_MbiN-RgqEgBSzV4d5DleMOoUc-MmD?usp=drive_link

An end-to-end project to train and deploy a **Fraud Detection system** with real-time probability scoring, SHAP-based model explainability, and an interactive dashboard for analysts and investigators.

## Dataset Layout

Put them like, the program expects this structure:
> data/
>   2018-04-01.pkl
>   2018-04-02.pkl
    --------------
>   2018-09-30.pkl

> processed/
>   feature_engineered_df.pkl

> models/
>  encoders.pkl
>  fraud_detection_model.pkl

The Dataset is provided in all pickle file, If the user wants to check without running the entire application then kindly,
> Open `Sample_Dataset_view` by simply opening a bash/powershell command and paste this:
```bash
> `streamlit run Sample_Dataset_view.py`
```

## Quickstart

To Run and install all the dependency
1) > Run the `install_modules.bat` file on the root
then follow the steps below

Run the Application
2a) Option A
```bash
run.bat
```

2b) Option B
- Open the command/bash and do the follow:
```bash
cd {Location of the Drive:/file/.../Fraud_detection/}
```
and type
```bash
streamlit run main.py
```

Make sure all files are placed as shown in the dataset layout.

##Model & Scenarios

The system is designed to flag fraudulent transactions based on:
- High Transaction Amounts – Any transaction above 220 is flagged.
- Terminal Fraud Simulation – Random terminals are marked fraudulent for 28 days.
- Customer Credential Theft – Certain customers show 5× inflated transaction values for 14 days.

## Core Components

- Preprocessing & Feature Engineering – Transform raw transactions
- Model Training – Probabilistic fraud scoring
- Explainability – SHAP visualizations for feature-level insights

## Streamlit App Features

- Home → Introduction & overview of fraud detection
- Raw Data Viewer → Explore transactions in raw format
- Engineered Features → View model-ready data and feature transformations
- Single Fraud Prediction → Input transaction details and get instant fraud probability
- Batch Fraud Prediction → Upload CSVs for multiple predictions (Simple & Detailed modes)
- Visual Insights → Interactive charts, feature importance, and SHAP explainability
