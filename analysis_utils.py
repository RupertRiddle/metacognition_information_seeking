import numpy as np
import pandas as pd
import warnings
from scipy import stats
warnings.filterwarnings('ignore')

def adj_arrays(arr_1,adj_factor):
  ''' Per Hautus (1995) , an Adjustment factor is added to the array to account for potential 0s in the data. As suggested by the paper, this factor is added to all data to prevent the induction of bias.'''
  if len(adj_factor) < len(arr_1):
      arr = arr1.copy()
      arr[:len(adj_factor)] += adj_factor
  else:
      arr = adj_factor.copy()
      arr[:len(arr_1)] += arr_1

  return arr

def extract_sensitivity_data(df):
  ''' takes a preprocessed dataframe and extracts confidence ratings for correct and incorrect trials, returning them as binned arrays'''
  bin_boundries =  [16.7,33.33,50,66.66,83.33,101]
  df = df.loc[df['inital_confidence']!= 'null'] ## exclude trials which did not contain a confidence estimation
  df_cor= df.loc[df['initial_response'] ==1] ## extract the correct responses and convert them to an array
  cor_arr = df_cor.inital_confidence.to_numpy()
  cor_arr = np.bincount(np.digitize(cor_arr,bin_boundries)) ## convert list to binned representation of data
  df_inc = df.loc[df['initial_response'] ==0] ## extract the incorrect responses and convert them to an array
  inc_arr = df_inc.inital_confidence.to_numpy()
  inc_arr = np.bincount(np.digitize(inc_arr,bin_boundries))
  inc_arr = np.asfarray(inc_arr)
  cor_arr = np.asfarray(cor_arr)
  adj_arr = np.zeros(6)+(1/6)
  cor_arr = adj_arrays(cor_arr,adj_arr)
  inc_arr = adj_arrays(inc_arr,adj_arr)

  return cor_arr, inc_arr, 
def extract_confidence_arrays(df):
  df = df.loc[df['inital_confidence']!= 'null'] ## exclude trials which did not contain a confidence estimation
  df_cor= df.loc[df['initial_response'] ==1] ## extract the correct responses and convert them to an array
  cor_arr = df_cor.inital_confidence.to_numpy()
  df_inc = df.loc[df['initial_response'] ==0] ## extract the incorrect responses and convert them to an array
  inc_arr = df_inc.inital_confidence.to_numpy()
  return cor_arr, inc_arr


def updated_clean_csv(csv):
  

  df = pd.read_csv(csv,sep=r",(?![^[]*\])")
  df.columns = list(map(lambda c:  c.replace('\\"', ''), df.columns)) ## strips /" in col names.
  col_names = df.columns.to_list() ## lists col names 
  for col in col_names:
     df[col] = df[col].str.replace('\\',"") ## iterate through list of col names, stripping extra data
     df[col] = df[col].str.replace("\"","")
  df = df.applymap(lambda x: pd.to_numeric(x, errors='ignore')) ## where neccesary, change str containing numbers to ints/foloats
  df = df.iloc[:,8:] ## Trim irrelelvent data
  initial_rows = len(df.index)
   #df = df[df.initial_rt < 12000] ### remove trials in which participants spent more than 10 seconds choosing stimulus
  trimmed_rows =len(df.index)
  omitted_rows = initial_rows - trimmed_rows
  ### Transform Binary Variables such that they are more easily factorised.
  df['initial_response'] = df['initial_response'].map({'true': 1,'false':0})
  df['info_searched'] = df['info_searched'].map({'y': 1, 'n':0,  "null":"null"})
  df['final_resp_value'] = df['final_resp_value'].map({'true': 1,'false':0,"null":"null"})
  df['final_resp_value'] = df['final_resp_value'].fillna("ignore")
  df['decision_change'] = df['decision_change'].map({'y': 1, 'n':0,  "null":"null"})
  df['type_of_info'] = df['type_of_info'].fillna("ignore")
  df['type_of_info'] =df['type_of_info'].map({'visual_evidence':1,'descriptive_evidence':0,'null':'null'}) ### vis evidence = 1, desc evidence =0
  df['answer_lagged'] = df['initial_response'].shift(1)
  df['type_of_info_lagged'] = df['type_of_info'].shift(1)
  df['info_seeking_lagged'] = df['info_searched'].shift(1)
  df['lagged_confidence'] = df['inital_confidence'].shift(1)
  df['lagged_revised_confidence'] = df['final_conf'].shift(1)

  #df['initial_response'] = df['initial_response'].map({True: 'true', False: 'false'})
  #df['final_resp_value'] = df['final_resp_value'].map({True: 'true', False: 'false'})
  return df
 
def updated_extract_metrics(df):
  ''' Aggregate DF
  
      accuracy 
      post-hoc accuracy 
      info sought when wrong / total times wrong
        - general info seeking 
        - checking
        - descriptive
      info sought when right / total times when right 
        - general info seeking 
        - checking
        - descriptive
      '''

  ## Accuracy 
  correct_answers = df['initial_response'].value_counts()[1]
  incorrect_answers =  df['initial_response'].value_counts()[0]
  accuracy = correct_answers/(correct_answers+incorrect_answers)

  ##########################################################################################################

  ## post_hoc_accuracy 

  df['final_answer_outcome'] =  np.where(((df.initial_response == 1) & ((df.final_resp_value == 1) | ((df.final_resp_value =='null')) | ((df.final_resp_value == "ignore")))| ((df.initial_response == 0) & (df.final_resp_value == 1))), 1, 0)
  correct_final_ans = df['final_answer_outcome'].value_counts()[1]
  incorrect_final_ans = df['final_answer_outcome'].value_counts()[0]
  final_accuracy = correct_final_ans/(correct_final_ans+ incorrect_final_ans)
  average_confidence = df['inital_confidence'].mean()
  
  ##########################################################################################################
  non_practice_trials = df.loc[df['inital_confidence'] !='null']
  average_difficulty_reached = non_practice_trials['ndots'].mean()
  st_dev_confidence = df['inital_confidence'].std()
  info_seeking = df.loc[df['info_searched'] ==1 ]
  average_confidence = df['inital_confidence'].mean()
  times_information_sought = len(info_seeking.index)

  ##########################################################################################################

  ### Info sought when wrong / total times wrong 


  df_incorrect_responses = df.loc[df['initial_response']== 0]
  
  df_information_sought_whilst_Wrong = df_incorrect_responses.loc[df_incorrect_responses['info_searched']==1]
  rate_of_corrective_seeking = len(df_information_sought_whilst_Wrong.index)/len(df_incorrect_responses.index)

  ## broken down by info type. 
  # vis evidence 
  df_incorrect_vis = df_incorrect_responses.loc[df_incorrect_responses['type_of_info']==1]
  df_information_sought_incorrect_vis = df_incorrect_vis[df_incorrect_vis['info_searched']==1]
  rate_of_corrective_seeking_vis = len(df_information_sought_incorrect_vis)/ len(df_incorrect_vis)
 
  # desc evidence
  df_incorrect_desc = df_incorrect_responses.loc[df_incorrect_responses['type_of_info']==0]
  df_information_sought_incorrect_desc = df_incorrect_desc.loc[df_incorrect_desc['info_searched']==1]
  rate_of_corrective_seeking_desc = len(df_information_sought_incorrect_desc)/ len( df_incorrect_desc)

##########################################################################################################

 ### Info sought when right / total times right 
  df_correct_responses = df.loc[df['initial_response']== 1]
  df_information_sought_whilst_right = df_correct_responses.loc[df_correct_responses['info_searched']==1]
  rate_of_wasteful_seeking = len(df_information_sought_whilst_right.index)/len(df_correct_responses.index)

  ## broken down by info type. 
  # vis evidence 
  df_correct_vis = df_correct_responses.loc[df_correct_responses['type_of_info']==1]
  df_information_sought_correct_vis = df_correct_vis[df_correct_vis['info_searched']==1]
  rate_of_wasteful_seeking_vis = len(df_information_sought_correct_vis)/ len(df_correct_vis)

  # desc evidence 

  df_correct_desc = df_correct_responses.loc[df_correct_responses['type_of_info']==0]
  df_information_sought_correct_desc = df_correct_desc.loc[df_correct_desc['info_searched']==1]
  rate_of_wasteful_seeking_desc = len(df_information_sought_correct_desc)/ len( df_correct_desc)


  
  vars= list([accuracy, final_accuracy, times_information_sought, average_confidence, st_dev_confidence,average_difficulty_reached, rate_of_corrective_seeking, rate_of_corrective_seeking_vis, rate_of_corrective_seeking_desc, rate_of_wasteful_seeking, rate_of_wasteful_seeking_vis, rate_of_wasteful_seeking_desc])
  return vars

def find_outliers(col):
    z = np.abs(stats.zscore(col))
    idx_outliers = np.where(z>3,True,False)
    return pd.Series(idx_outliers,index=col.index)