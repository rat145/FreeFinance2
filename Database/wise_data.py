import pandas as pd
import numpy as np
import csv
import json
import datetime as dt
from datetime import datetime
pd.options.display.max_columns = 20


def json2csv(json_name, csv_name, key):
    with open(json_name) as json_file:
        data = json.load(json_file)
    transaction_data = data[key]
    data_file = open(csv_name, 'w') 
    csv_writer = csv.writer(data_file)
    count = 0
    for tran in transaction_data:
        if count == 0: 
            # Writing headers of CSV file 
            header = tran.keys()
            csv_writer.writerow(header) 
            count += 1
        # Writing data of CSV file 
        csv_writer.writerow(tran.values())
    data_file.close() 

json2csv(r'C:\FreeFinance2\FreeFinance2\Database\customer_data.json', r'C:\FreeFinance2\FreeFinance2\Database\customer_data.csv', 'fiData')
df = pd.read_csv(r'C:\FreeFinance2\FreeFinance2\Database\customer_data.csv')

new_df = df.drop(["transactionTimestamp","balance","reference"],axis = 1)


def gen_narrations(df):
    nan = df["narration"].isna().sum()
    if nan!=0:
        return ("The narration is empty for nan no. of transactions!")
    n = df.shape[0]
    narrations = []
    for i in range(0,n):
        li = [df["txnId"][i]]
        li+=(df["narration"][i].split('/'))
        narrations.append(li)
    return pd.DataFrame(narrations, columns =['txnId','f1','f2','f3','f4','f5','f6'], dtype = str)

narrations = gen_narrations(new_df)


    
#Making separate dataframes for specific merchants: These 7 are unique ones
upi_df = narrations[narrations["f1"]=="UPI"]
gib_df = narrations[narrations["f1"]=="GIB"]
vps_df = narrations[narrations["f1"]=="VPS"]
atm_df = narrations[narrations["f1"]=="ATM"]
ach_df = narrations[narrations["f1"]=="ACH"]
mmt_df = narrations[narrations["f1"]=="MMT"]
iin_df = narrations[narrations["f1"]=="IIN"]



#Making separate dataframes for specific merchants: These are for the others
ips_df = narrations[narrations["f1"]=="IPS"]
vin_df = narrations[narrations["f1"]=="VIN"]
cms_df = narrations[narrations["f1"]=="CMS"]
bil_df = narrations[narrations["f1"]=="BIL"]
nfs_df = narrations[narrations["f1"]=="NFS"]
other_df = narrations[narrations["f1"]!="UPI"]
other_df = other_df[other_df["f1"]!="GIB"]
other_df = other_df[other_df["f1"]!="VPS"]
other_df = other_df[other_df["f1"]!="ATM"]
other_df = other_df[other_df["f1"]!="ACH"]
other_df = other_df[other_df["f1"]!="MMT"]
other_df = other_df[other_df["f1"]!="IIN"]
other_df = other_df[other_df["f1"]!="IPS"]
other_df = other_df[other_df["f1"]!="VIN"]
other_df = other_df[other_df["f1"]!="CMS"]
other_df = other_df[other_df["f1"]!="BIL"]
other_df = other_df[other_df["f1"]!="NFS"]


#This dictionary indicates the column name which gives us the insights about the brand/company/reciever of money/transaction etc (CMS: there is no description)
merchants_list = ["UPI","GIB","VPS","ATM","ACH","MMT","IIN","IPS","VIN","CMS","BIL","NFS","OTHER"]
merchants_df_dict = {"UPI":upi_df, "GIB":gib_df, "VPS":vps_df, "ATM":atm_df, "ACH":ach_df, "MMT":mmt_df, "IIN":iin_df, "IPS":ips_df, "VIN":vin_df, "CMS":cms_df, "BIL":bil_df, "NFS":nfs_df, "OTHER":other_df}
selector_dict = {"UPI":["f3", "f4"], "GIB":["f3"], "VPS":["f2"], "ATM":["f3"], "ACH":["f2"], "MMT":["f4"], "IIN":["f3"], "IPS":["f2"], "VIN":["f2"], "CMS":["f3"], "BIL":["f3","f4"], "NFS":["f3"], "OTHER":["f1"]}


brand_df = pd.read_csv(r"C:\FreeFinance2\FreeFinance2\Database\Brand_db.csv")



#Function to remove whitespace (called by simply_string)
def remove(string): 
    return string.replace(" ", "") 
#Function to bring entire string to lower case and remove any spaces
def simplify_string(string):
    string = remove(string)
    string = string.casefold()
    return string
#Function to parse UPI id
import re
def parse_upi(string):
    alphanumeric = ""
    pattern = '[0-9.]'
    string = re.sub(pattern,'',string)
    tup = string.partition('@')
    return tup[0]
    
def parse_cms(string):
    pattern = '[0-9_]'
    return re.sub(pattern,'',string)



output_df = df.copy()

output_df.drop(["transactionTimestamp", "narration", "reference"],axis = 1, inplace = True)

output_df["brand"] = ""

output_df["category"] = ""


def detect_brands(merchant, merchant_df, brand_df,output_df):
    output_df = output_df.copy()
    brand_df = brand_df.copy()
    merchant_df = merchant_df.copy()
    f = selector_dict[merchant]
    
    if merchant=="UPI":
        merchant_df[f[0]] = merchant_df[f[0]].apply(simplify_string)
        merchant_df[f[1]] = merchant_df[f[1]].apply(simplify_string)
        merchant_df[f[1]] = merchant_df[f[1]].apply(parse_upi)
        merchant_df[f[0]] = merchant_df[f[0]].str.cat(merchant_df[f[1]], sep =",")
        #print(merchant_df.head())
    elif merchant=="CMS":
        merchant_df[f[0]] = merchant_df[f[0]].apply(simplify_string)
        merchant_df[f[0]] = merchant_df[f[0]].apply(parse_cms)
        
    elif merchant=="BIL":
        merchant_df[f[0]] = merchant_df[f[0]].apply(simplify_string)
        merchant_df[f[1]] = merchant_df[f[1]].apply(simplify_string)
        merchant_df[f[0]] = merchant_df[f[0]] .str.cat(merchant_df[f[1]], sep ="")
        
    else:
        merchant_df[f[0]] = merchant_df[f[0]].apply(simplify_string)
        
    brand_df['parsed'] = brand_df['Brand_name'].apply(simplify_string)
    
    #print("brands: \n", brands)
    #print("trans_summaries: \n", trans_data)
   # print("The total transactions under ",merchant,": ",len(merchant_df[f[0]]))
    matching_count = 0
    matched = 0
    if merchant!="UPI":
       # print("Doing for: ",merchant)
        for index_t, row_t in merchant_df.iterrows():
            txnId = row_t['txnId']
            t = row_t[f[0]]
            matched = 0
            for index_b, row_b in brand_df.iterrows():
                b = row_b["parsed"]
                index1 = t.find(b)
                index2 = b.find(t)
            
                if index1!=-1: #and index2!=-1:
                    #print(t)
                    matched = 1
                    matched_brand = row_b["Brand_name"]
                    matched_category = row_b["Category"]
                    matching_count+=1
                    continue
                elif index2!=-1:
                    #print(t)
                    matched = 1
                    matched_brand = row_b["Brand_name"]
                    matched_category = row_b["Category"]
                    matching_count+=1
                    continue
            if matched == 0:
              #  print("Not found: ",t)
                matched_brand, matched_category = "Unknown", "Other"
            #else:
                #print("TxnId: ", txnId, "  Brand Name: ", matched_brand, "  Category: ",matched_category)
            
            index = output_df.index[output_df['txnId']==txnId].tolist()
            output_df.at[index[0], "brand"] = matched_brand
            output_df.at[index[0], "category"] = matched_category
    