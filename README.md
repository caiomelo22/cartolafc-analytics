# cartolafc-analytics

## Overview
This project uses data from [fbref](https://fbref.com/en/) and the official CartolaFC API to analyze fantasy football picks for the next round of the Brasileirão Série A. 
Through a Streamlit dashboard, you can explore team and player statistics, with players grouped by position to make fantasy selection easier.

![image](https://github.com/user-attachments/assets/62846b56-3776-49ea-9fea-4fd8339d5b60)
![image](https://github.com/user-attachments/assets/3766b84b-52c7-4d39-ac5e-2b10e1fad0a9)

## Setup
This project depends on data from [football-data](https://github.com/caiomelo22/football-data). To gather and load the necessary data into your database, make sure to clone that repository and run the [get_overall_info.py](https://github.com/caiomelo22/football-data/blob/main/src/get_overall_info.py) script.

### Environment File
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=pwd
DB_DATABASE=football-data
```

## Executing
To run this project, start by installing the required packages:
```
>> pip install -r requirements.txt
```
Then, launch the Streamlit application with:
```
>> streamlit run .\app.py
```
