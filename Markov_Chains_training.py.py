

import pandas as pd
import numpy as np
import math
from datetime import datetime

# Reading dataframe

dateparsefunct = lambda x: datetime.strptime(x, '%Y%m')
dataframe_ts = pd.read_csv('train.csv', parse_dates= ['Date'] , date_parser= dateparsefunct)

dataframe_ts = dataframe_ts.sort_values(['PID','Date'])
dataframe_ts = dataframe_ts.reset_index(drop = True)

dataframe_ts_num = dataframe_ts[dataframe_ts.Event.map(lambda x : True if x.isnumeric() else False )]

dataframe_ts_num.loc[: ,'Event'] = dataframe_ts_num.Event.astype(int, copy = False)


list_of_pids = list(set(dataframe_ts_num.PID.tolist()))
list_of_pids.sort()


dict_of_len = {}
for patient_id in list_of_pids:
    list_of_dis = dataframe_ts_num[dataframe_ts_num.PID == patient_id].Event.tolist()
    dict_of_len.update({patient_id : len(list_of_dis)})

sorted_dict_of_len = sorted(dict_of_len.items(), key = lambda x : x[1])
sorted_dict_of_len[:10]


# For later use
# For seeing orphan keys(keys not in occurance_dictionary but were there in training data(1st time occuring values in last 2 datapoint for each patient) 
main_dis_list = [] 
for patient_id in list_of_pids:
    list_of_dis = dataframe_ts_num[dataframe_ts_num.PID == patient_id].Event.tolist()
    for element in list_of_dis:
        main_dis_list.append(element)

a = set(main_dis_list)
len (list(a))



# ## Training set creation 
patients_diseases_dict = {}

for patient_id in list_of_pids:
    list_of_dis = dataframe_ts_num[dataframe_ts_num.PID == patient_id].Event.tolist()
    patients_diseases_dict.update({patient_id : list_of_dis})


# # Making a current_state --> possible_state dictionary 


occ_dictionary = {}
for pid, patient_x_diseases in patients_diseases_dict.items():
    no_of_dis = len(patient_x_diseases)
    for i in range(no_of_dis):
        current_state_key = occ_dictionary.get(patient_x_diseases[i], 0)
        if( (current_state_key == 0) and ((i+1)<no_of_dis) ):
            occ_dictionary.update({patient_x_diseases[i] : {} })
            occ_dictionary[patient_x_diseases[i]].update( {patient_x_diseases[i+1] : 1 } )
        else:
            if((i+1) < no_of_dis):
                possible_token_key_value = occ_dictionary[patient_x_diseases[i]].get(patient_x_diseases[i+1], 0)
                if (possible_token_key_value == 0):
                    occ_dictionary[patient_x_diseases[i]].update( {patient_x_diseases[i+1] : 1} )
                else:
                    occ_dictionary[patient_x_diseases[i]][patient_x_diseases[i+1]]+= 1

b = set(occ_dictionary.keys())
orphan_keys = list(a - b)
orphan_keys.sort()
orphan_keys[:10]


# Sorting the inner dictionary in its value
sorted_occ_dict = {}
for current_key, dictionary in occ_dictionary.items():
    temp_list = [] 
    temp_list = sorted(occ_dictionary[current_key].items(), key = lambda x: x[1], reverse= True)
    sorted_occ_dict.update( {current_key : temp_list} )


# Predicting the next 10 values  
number_of_predictions = 10
prediction_list = {}
for pid in list_of_pids:
    prediction_for_patient = []
    for i in range(-1,-5,-1): #testing for 5 previous values if this shows a keyerror
        try:
            current_state = patients_diseases_dict[pid][i]
            dummy = sorted_occ_dict[current_state][0][0]
            new_no_of_prediction = number_of_predictions - i 
            break
        except KeyError:
            print("For {} , the starting D_id as {} showed KeyError in sorted_occ_dict".format(pid, current_state))
            print("Trying the previous key as current_state")
            continue
        
    for i in range(new_no_of_prediction):
        next_value = sorted_occ_dict[current_state][0][0]
        prediction_for_patient.append(next_value)
        current_state = next_value
        
    prediction_list.update({ pid : prediction_for_patient[-number_of_predictions:] })




