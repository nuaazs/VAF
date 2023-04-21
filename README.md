## Introduction
声纹识别系统

## Requirements
Python 3.6 or higher
Flask 1.0 or higher
ECAPATDNN 1.0 or higher

## Installation
Before using this project, you need to install Python and related dependencies first. The specific installation steps are as follows:

Download and install Python 3.6 or higher version, you can download the installation package from the official website https://www.python.org/downloads/, and complete the installation according to the prompts.

Open the command line terminal (cmd for Windows and Terminal for Linux), execute the following command to install Flask:

pip install Flask
Download and install ECAPATDNN, please refer to the ECAPATDNN documentation for installation.

## Usage
### Data Preparation
Before conducting voiceprint recognition, you need to prepare training and testing data. This project provides example data in the data directory, or you can use your own data for training and testing.

### Model Training
Train the voiceprint model in train.py using the ECAPATDNN model. Execute the following command:

python train.py
### Model Testing
Verify the voiceprint model using test data in test.py. Execute the following command:

python test.py
Run the Web Framework
Implement the web framework in app.py, and use the API provided by Flask to perform functions such as identity verification and speech recognition. Execute the following command:

python app.py
## API Documentation
/api/verify POST method, performs identity verification, with parameters audio_file and speaker_id passed in, and returns whether the verification result matches.
/api/recognize POST method, performs speech recognition, with parameter audio_file passed in, and returns the predicted speaker identity.
Copyright and License
This project adopts the MIT license and can be freely modified and distributed. However, please note that the dataset and model weights in this project are protected by copyright and are not allowed for commercial use and resale.

## Copyright and License

