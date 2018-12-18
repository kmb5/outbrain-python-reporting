import outbrain
import datetime
import pandas as pd
import yaml

#--- VARIABLES TO BE DEFINED ---

marketer_id = ["YOUR_MARKETER_ID_HERE"] #Use the get_marketers() method to find out the ID

# --- LOAD CREDENTIALS AND CREATE OUTBRAIN OBJECT

creds = yaml.load(open("outbrain.yml"))
outb = outbrain.OutbrainAmplifyApi()

# --- FUNCTIONS

def authorize(outb, creds):
	try:
		outb.token = creds["token"] #If token exists in yaml, outbrain object will get the attribute "token" with the token string
		token_gen_date = datetime.datetime.strptime(creds["token_generated_on"],"%Y-%m-%d__%H_%M_%S") #Convert token generated date to datetime object for comparison
		if (datetime.datetime.now() - datetime.timedelta(days=28)) > token_gen_date: #If token was generated more than 28 days ago...
			print("Token was created more than 28 days ago, re-authorizing...")
			outb.token = outb.get_token(outb.user, outb.password) #... get another token...
			creds["token"] = outb.token #... add it to outb object as the token attribute
			creds["token_generated_on"] = datetime.datetime.now().strftime("%Y-%m-%d__%H_%M_%S")
			with open("outbrain.yml", "w") as f:
				yaml.dump(creds, f, default_flow_style=False) #... and dump everything to the yaml file
		else:
			print("Token was created less than 28 days ago, no authorization needed. Continuing...") #Token attribute is in outb object and is still valid, just go on
	except KeyError: #If token is not in yaml file...
		outb.token = outb.get_token(outb.user, outb.password) #... get the token...
		creds["token"] = outb.token
		creds["token_generated_on"] = datetime.datetime.now().strftime("%Y-%m-%d__%H_%M_%S")
		with open("outbrain.yml", "w") as f:
			yaml.dump(creds, f, default_flow_style=False) #... and dump everything to the yaml file

def get_camp_ids_names_containing_str(marketer_id, string):
	#Returns a list of dicts with all the campaign ids and names for the marketer_id
	all_campaigns = outb.get_campaigns_per_marketer(marketer_id).get(marketer_id[0])
	return [{"id": x.get("id"), "name": x.get("name")} for x in all_campaigns if string in x["name"]]

def get_camp_ids_containing_str(marketer_id, string):
	#Returns a list of campaign IDs which contain a given string
	all_campaigns = outb.get_campaigns_per_marketer(marketer_id).get(marketer_id[0])
	return [x.get("id") for x in all_campaigns if string in x["name"]]

def transform_and_filter_result(result,camp_ids_to_filter):
#Transforms the result of get_campaign_performance_per_period() function and only includes campaign IDs that are in the list of camp_ids_to_filter
	final_result = list()
	for x in result[0][0]:
		if x["campaignId"] in camp_ids_to_filter:
			result_per_id = list()
			for result in x["results"]:
				result_per_id_per_day = dict()
				#The resulting dict can be modified if you need different items in it for your reporting
				result_per_id_per_day["campaign_id"] = x["campaignId"]
				result_per_id_per_day["date_from"] = result.get("metadata").get("fromDate")
				result_per_id_per_day["date_to"] = result.get("metadata").get("toDate")
				result_per_id_per_day["impressions"] = result.get("metrics").get("impressions")
				result_per_id_per_day["clicks"] = result.get("metrics").get("clicks")
				result_per_id_per_day["conversions"] = result.get("metrics").get("conversions")
				result_per_id_per_day["spend"] = result.get("metrics").get("spend")
				result_per_id.append(result_per_id_per_day)
			final_result.append(result_per_id)
	return final_result

def merge(list_of_lists):
	#To merge a list of lists into a single list
	#transform_and_filter_result will output a list of as many lists as there are campaign IDs with the given string - this needs to be concatenated for pandas
	merged = list()
	for l in list_of_lists:
		merged.extend(l)
	return merged

def main():

	authorize(outb, creds)

	string = input("Which campaigns do you want to include? >>> ")

	while True:
		date_from = input("From which date? Use the format 'YYYY-MM-DD please. >>> ")
		try:
			date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d") #Input string will only be converted if the user gives the correct format...
			break
		except ValueError:
			print("Please input the date in the correct format!") #... else it keeps asking for the correct format.

	while True:
		date_to = input("To which date? Use the format 'YYYY-MM-DD please. >>> ")
		try:
			date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")
			break
		except ValueError:
			print("Please input the date in the correct format!")

	while True:
		breakdown = input("What should be the breakdown? Type 'daily' or 'monthly' >>> ")
		if breakdown in ("daily", "monthly"):
			break
		else:
			print("Please input only 'daily' or 'monthly'")

	filename = input("What should be the filename? >>> ")

	result = outb.get_campaign_performance_per_period(marketer_id,date_from,date_to,breakdown) #Get the report object with the given params
	filtered_camp_ids = get_camp_ids_containing_str(marketer_id,string) #Filter out campaign IDs containing the given string
	tf = merge(transform_and_filter_result(result,filtered_camp_ids)) #Transform and merge the filtered results to a dict for pandas
	dataframe = pd.DataFrame(tf, columns=["campaign_id", "date_from", "date_to", "impressions", "clicks", "conversions", "spend"])
	dataframe.set_index("date_from", inplace=True)
	final_pivot_df = dataframe.groupby("date_from").sum().reindex(["impressions","clicks","spend","conversions"], axis=1) #I only need these metrics for my final export, can be changed if necessary
	date_now = datetime.datetime.now().strftime("%Y-%m-%d__%H_%M_%S") #For the date in the filename
	writer = pd.ExcelWriter(f"{filename}_{date_now}.xlsx") #Pandas excel writer object
	final_pivot_df.to_excel(writer,"Sheet1") #Write the dataframe to excel Sheet 1
	writer.save()
	print(f"Finished!, your report is saved as {filename}_{date_now}.xlsx")


main()

