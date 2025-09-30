Fraud Detection Project

All the required files can be downloaded from here, kindly download them and paste on the root folder then run the program:
https://drive.google.com/drive/folders/16t_MbiN-RgqEgBSzV4d5DleMOoUc-MmD?usp=drive_link

The application allows analysts, investigators, and general users to analyze transaction behavior, evaluate fraud probability 
for single transactions, or perform batch predictions on uploaded datasets. Core components include data preprocessing, 
feature engineering, and probabilistic scoring, supported by SHAP-based visual explanations to enhance model transparency. 
The frontend offers a comprehensive dashboard, raw and processed data exploration, exploratory visualizations, 
and insights into model performance and feature importance.

Dataset Layout

Please Download the Dataset first to use from the same google drive and paste it in the root folder:
https://drive.google.com/file/d/1ZvZpYSk8cAQKK9nVRqBT4u0v1Rt2XoTf/view?usp=drive_link

and put them like:
data/
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
> Open `Sample_Dataset_view` by simply opening a bash/powershell command
> Type `streamlit run Sample_Dataset_view.py`

To Run and install all the dependency and Modules
> Run the `install_modules.bat` file on the root
then follow the steps below

Starting the Application

1) After Running the `install_modules.bat` file
   Run the Application by simply clicking `run.bat`

Make sure to have all the files in the root folder as shown

Streamlit App

- Upload .csv for multiples outcomes at one go, or input the results to get the desired result of one
- The Application has various graphs and SHAP Analysis to help understand the prediction.

Marked Most Likely to be Flagged are these 3 conditions

**1. Any transaction whose amount is more than 220 is a fraud. This is not inspired by a real-world scenario. It provides an obvious fraud pattern that should be detected by any baseline fraud detector. This will be useful to validate the implementation of a fraud detection technique.  **
**2. Every day, a list of two terminals is drawn at random. All transactions on these terminals in the next 28 days will be marked as fraudulent. This scenario simulates a criminal use of a terminal, through phishing for example. You could add features that keep track of the number of fraudulent transactions on the terminal to help with this scenario.  **
**3. Every day, a list of 3 customers is drawn at random. In the next 14 days, 1/3 of their transactions have their amounts multiplied by 5 and marked as fraudulent. This scenario simulates a card-not-present fraud where the credentials of a customer have been leaked. The customer continues to make transactions, and transactions of higher values are made by the fraudster who tries to maximize their gains. You could add features that keep track of the spending habits of the customer for this scenario.  **


Features

- Home → Introduction and Overview of how Fraud Detection detects
- Raw Data Viewer → Helpful to Analyse the dataset in the raw form
- Engineered Featured → Overview of the Model, in-depth information and Overview
- Single Fraud Prediction → It has various columns for the user to input and get the result
- Batch Fraud Prediction → For Multiple Prediction at ones, the result can be seen in Simple and Advanced/Detailed Modes
