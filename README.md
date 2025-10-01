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
> Open `Sample_Dataset_view` by simply opening a bash/powershell command
```bash
> Type `streamlit run Sample_Dataset_view.py`
```
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

> 1. Any transaction whose amount is more than 220 is a fraud. This is not inspired by a real-world scenario. It provides an obvious fraud pattern that should be detected by any baseline fraud detector. This will be useful to validate the implementation of a fraud detection technique.
> 2. Every day, a list of two terminals is drawn at random. All transactions on these terminals in the next 28 days will be marked as fraudulent. This scenario simulates a criminal use of a terminal, through phishing for example. You could add features that keep track of the number of fraudulent transactions on the terminal to help with this scenario.
> 3. Every day, a list of 3 customers is drawn at random. In the next 14 days, 1/3 of their transactions have their amounts multiplied by 5 and marked as fraudulent. This scenario simulates a card-not-present fraud where the credentials of a customer have been leaked. The customer continues to make transactions, and transactions of higher values are made by the fraudster who tries to maximize their gains. You could add features that keep track of the spending habits of the customer for this scenario.


Features

- Home → Introduction and Overview of how Fraud Detection detects
- Raw Data Viewer → Helpful to Analyse the dataset in the raw form
- Engineered Featured → Overview of the Model, in-depth information and Overview
- Single Fraud Prediction → It has various columns for the user to input and get the result
- Batch Fraud Prediction → For Multiple Prediction at ones, the result can be seen in Simple and Advanced/Detailed Modes
