from analysis_utils import updated_clean_csv,updated_extract_metrics,extract_sensitivity_data, extract_confidence_arrays, find_outliers
from meta_d_analysis import fit_meta_d_MLE
import numpy as np 
import pandas as pd
from os import listdir
import re
from scipy.stats import *
from scipy import stats
from scipy.optimize import Bounds, LinearConstraint, minimize, SR1
import warnings
import matplotlib.pyplot as plt
#### list of all files 
dir = listdir('all_data_from_prolific')


df_labels =['meta_d','accuracy','post_hoc_accuracy','times_info_sought','average_confidence','st_dev_confidence','average_difficulty_level_reached','corrective_info_seeking','corrective_info_seeking_vis','corrective_info_seeking_disc','wasteful_info_seeking','wasteful_info_seeking_vis',
            'wasteful_info_seeking_desc']
aggregate_df = pd.DataFrame(columns = df_labels)
all_data_df = pd.DataFrame(columns = ['meta_d','participant_n','trial_number','initial_rt','ndots','initial_response','inital_confidence','confidence_rt', 'info_searched','type_of_info','decision_change','decision_change_rt','final_resp_value','final_conf','info_strength','info_seek_rt'])


participant_n = 1
for f in range(len(dir)):
  file = dir[f]
 
  if 'dot' in file: ### check if its a data file.
  
    csv = updated_clean_csv("all_data_from_prolific"+"//"+file) ### Clean the dataset 
    unbinned_correct_confidence, unbinned_incorrect_confidence = extract_confidence_arrays(csv)
    correct_confidence, incorrect_confidence = extract_sensitivity_data(csv) ### extract correct and incorrect confidences
    correct_confidence +=1 ### replace with normalisation term
    incorrect_confidence += 1
    
    fit = fit_meta_d_MLE(incorrect_confidence,correct_confidence) ## fit metacognitive sensitivity 
    meta_d = fit['meta_da']
  
    csv.insert(0,'meta_d', meta_d)
    csv.insert(0,'participant_n',participant_n)
    participant_n +=1
    csv = csv[csv['trial_number'] >= 44]
    all_data_df = all_data_df.append(csv)
    all_data_df.reset_index(drop=True)
    participant_vars = updated_extract_metrics(csv)
    participant_vars.insert(0,meta_d)
    aggregate_df.loc[len(aggregate_df)] = participant_vars
aggregate_df.to_csv('aggregate_df.csv')
all_data_df.to_csv('all_data.csv')