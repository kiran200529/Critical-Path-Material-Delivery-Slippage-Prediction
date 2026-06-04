# Critical-Path Material Delivery Slippage Prediction

## Project Overview

This project focuses on predicting material delivery slippage in the construction supply chain. The main objective is to identify scheduled site material deliveries that are likely to arrive more than three working days after the committed gate delivery date.

Using Machine Learning-based classification techniques, this project helps construction planners detect high-risk deliveries early and take preventive actions before the delay affects critical-path activities. The solution supports better planning, supplier coordination, carrier decisions, backup material arrangement, and site work re-sequencing.

## Business Problem

Construction projects depend heavily on timely delivery of bulk and specialist materials. When important materials arrive late, site crews may remain idle, planned work may be disturbed, and project schedules may be delayed.

Planners need a data-led way to predict which material deliveries are likely to slip beyond the committed delivery date by more than three working days.

The prediction helps construction teams act early by:

- Re-sequencing site work
- Switching suppliers or carriers
- Contacting suppliers in advance
- Arranging backup materials
- Protecting critical-path trades
- Reducing project schedule disruption

## Project Objectives

- Predict whether a scheduled material delivery will be delayed by more than three working days
- Analyze construction delivery patterns and supplier-related risk factors
- Identify important features that influence delivery slippage
- Build a machine learning model for early delivery risk prediction
- Improve delay detection using threshold tuning
- Support proactive construction planning and risk mitigation

## Machine Learning Approach

### Algorithm Used

Improved Random Forest Classifier

### Problem Type

Binary Classification

The model predicts two possible outcomes:

- Not Delayed: The delivery is not delayed by more than three working days
- Delayed: The delivery is delayed by more than three working days

## Key Steps Performed

- Project Setup
- Dataset Loading
- Dataset Understanding
- Missing Value Analysis
- Duplicate Value Analysis
- Target Column Identification
- Target Class Distribution Analysis
- Numerical and Categorical Feature Separation
- Categorical Delay Rate Analysis
- Outlier Checking
- Correlation Analysis
- Date Feature Engineering
- Feature and Target Preparation
- Train-Test Split
- Preprocessing Pipeline Creation
- Model Selection
- Improved Random Forest Model Training
- Model Evaluation
- Threshold Tuning
- Final Threshold Selection
- Confusion Matrix Generation
- Confusion Matrix Interpretation
- Feature Importance Analysis
- Sample Prediction Testing
- Final Model Saving

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Scikit-Learn
- Joblib
- Google Colab

## Important Features Considered

The project uses delivery-related, supplier-related, site-related, and schedule-related features for prediction.

Important features include:

- Supplier Tier
- Delivery Terms
- Site Access Restriction Level
- Import or Customs Hold Liability
- Market Shortage Stress Band
- Supplier Rolling OTIF Band
- Packaging and Handling Complexity
- Order Placed Date
- Committed Delivery Date
- Other Construction Supply-Chain Factors

## Feature Engineering

Date feature engineering was applied to convert raw date columns into useful machine learning features.

The date columns were transformed into:

- Month
- Day of Week
- Quarter

This helps the model understand whether certain months, weekdays, or quarters have higher chances of delivery delay.

## Final Model Selected

The final selected model is the Improved Random Forest Classifier.

Random Forest was selected because it performs well on structured construction supply-chain data. It can handle nonlinear relationships and provides feature importance, which helps explain the main factors behind material delivery slippage.

The model was improved using parameter tuning and class weighting to give more importance to delayed delivery cases.

## Threshold Tuning

Threshold tuning was performed to improve the model’s ability to detect delayed deliveries.

The final selected threshold is 0.40.

This threshold was selected because missing an actually delayed delivery is more dangerous than raising a false alarm. In construction planning, failing to detect a risky delivery can cause idle crews, work stoppage, and project schedule slippage.

## Evaluation Metrics

The model was evaluated using:

- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC Score
- Classification Report
- Confusion Matrix

In this project, recall is especially important because the main goal is to identify as many risky delayed deliveries as possible.

## Key Findings

- The model successfully predicts whether a construction material delivery is likely to be delayed by more than three working days
- Supplier performance, delivery terms, site access restrictions, customs hold liability, market shortage conditions, and packaging complexity are important factors in delivery slippage prediction
- Threshold tuning helps improve the detection of risky deliveries
- False negatives are the most dangerous errors because they represent delayed deliveries that the model failed to identify
- Feature importance analysis helps construction planners understand the major risk factors behind delivery delays

## Business Impact

The proposed machine learning solution enables construction teams to:

- Identify high-risk material deliveries early
- Reduce idle crew time
- Protect critical-path construction activities
- Improve supplier and carrier coordination
- Take preventive action before delays become serious
- Reduce project schedule disruption
- Improve construction supply-chain planning
- Support data-driven decision-making

## Project Outcome

A complete machine learning-based material delivery slippage prediction solution was developed using an Improved Random Forest Classifier.

The final model predicts whether a scheduled site material delivery will arrive more than three working days after the committed gate delivery date. The solution helps construction planners identify risky deliveries early and take proactive actions such as supplier follow-up, carrier switching, backup material arrangement, and site work re-sequencing.

This project provides a practical data-driven approach to reducing delivery risk and protecting critical-path construction activities.

## Author

G Kiran Kumar
