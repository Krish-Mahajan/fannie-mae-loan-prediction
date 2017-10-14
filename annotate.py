
import os 
import settings 
import pandas as pd 


def count_performance_rows(): 
	counts = {}
	with open(os.path.join(settings.PROCESSED_DIR,"performance.txt"),'r') as f:
		for i,line in enumerate(f):
			if i==0:
				# Skip header row 
				continue 
			loan_id,date = line.split("|")
			loan_id = int(loan_id) 
			if loan_id not in counts: 
				counts[loan_id] = {
				  "foreclosure_status": False,
				  "performance_count":0
				}
			counts[loan_id]["performance_count"] +=1  

			if len(date.strip()) > 0:
				counts[loan_id]["foreclosure_status"] =True 

	return counts 



def get_performance_summary_value(loan_id,key,counts):
	value = counts.get(loan_id,{
		"foreclosure_status": False,
		"performance_count":0
	})  
	return value[key]   


def annotate(acquisition,counts): 
	acquisition["foreclosure_status"] = acquisition["id"].apply(lambda x:get_performance_summary_value(x,"foreclosure_status",counts))
	acquisition["performance_count"] = acquisition["id"].apply(lambda x:get_performance_summary_value(x,"performance_count",counts))

	cols = ["channel","seller","first_time_homebuyer","loan_purpose","property_type","occupancy_status","property_state","product_type"]

	for column in cols:
		acquisition[column] =acquisition[column].astype('category').cat.codes


	for start in ["first_payment","origination"]:
		column = "{}_date".format(start)  
		acquisition["{}_year".format(start)]=pd.to_numeric(acquisition[column].str.split('/').str.get(1))
		acquisition["{}_month".format(start)]=pd.to_numeric(acquisition[column].str.split('/').str.get(0))
		del acquisition[column]


	acquisition = acquisition.fillna(-1)
	acquisition = acquisition[acquisition["performance_count"]>settings.MINIMUM_TRACKING_QUARTERS]

	return acquisition


def read():
 	acquisition = pd.read_csv(os.path.join(settings.PROCESSED_DIR,"acquisition.txt"),sep="|")	
 	return acquisition  


def write(acquisition):
 	acquisition.to_csv(os.path.join(settings.PROCESSED_DIR,"train.csv"),index=False)	



if __name__ == "__main__":
	acquisition =read()
	counts = count_performance_rows() 
	acquisition = annotate(acquisition,counts) 
	write(acquisition) 

