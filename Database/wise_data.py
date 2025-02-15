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
    
    if merchant=="UPI":
       # print("Doing for: ",merchant)
        for index_t, row_t in merchant_df.iterrows():
            txnId = row_t['txnId']
            #print(txnId)
            tup1= row_t[f[0]].partition(',')
            t1 = tup1[0]
            t2 = tup1[2]
            matched = 0
            for index_b, row_b in brand_df.iterrows():
                b = row_b["parsed"]
                index1 = t1.find(b)
                index2 = b.find(t1)
            
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
                #print ("Matching no. 2")
                #print("t2: ",t2)
                for index_b, row_b in brand_df.iterrows():
                    b = row_b["parsed"]
                    index1 = t2.find(b)
                    index2 = b.find(t2)
            
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
              #  print("Not found: ",tup1)
                matched_brand, matched_category = t2, "Transfer"
           # else:
                #print("TxnId: ", txnId, "  Brand Name: ", matched_brand, "  Category: ",matched_category)
            index = output_df.index[output_df['txnId']==txnId].tolist()
            output_df.at[index[0], "brand"] = matched_brand
            output_df.at[index[0], "category"] = matched_category
    #print("Matched brands: ",matching_count)
    return output_df


for i in range(len(merchants_list)):
    output_df = detect_brands(merchants_list[i],merchants_df_dict[merchants_list[i]], brand_df, output_df)


output_df['valueDate'] = pd.to_datetime(output_df['valueDate'], format='%Y-%m-%d')


#Till here same



#Defining dictionary for identifying days
days_dict = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thurday", 4:"Friday", 5: "Saturday", 6: "Sunday"}
months_dict = {1: "January", 2: "February", 3: "March", 4: "April", 5:"May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}


month_wise_exp = pd.DataFrame({"Month":[months_dict[i] for i in months_dict.keys()],"Total_Expense":0, "Total_Income":0})



def get_monthly_exp(df, month_wise_exp):
    df = df.copy()
    month_wise_exp = month_wise_exp.copy()
    for index_1, row_1 in df.iterrows():
            date = row_1['valueDate']
            type_trans = row_1['type']
            amnt = row_1["amount"]
            m = date.month
            m = months_dict[m]
            for index_2, row_2 in month_wise_exp.iterrows():
                mon = row_2['Month']
                if mon == m:
                    ind = month_wise_exp.index[month_wise_exp['Month']==mon].tolist()
                    if type_trans == "DEBIT":
                        month_wise_exp.at[ind[0], "Total_Expense"] += amnt  
                    if type_trans == "CREDIT":
                        month_wise_exp.at[ind[0], "Total_Income"] += amnt  
                    continue
    return month_wise_exp


month_wise_exp = get_monthly_exp(output_df, month_wise_exp)


month_wise_exp.to_json(r"C:\FreeFinance2\FreeFinance2\Database\monthWiseEI.json", orient = 'records')


opening_closing = pd.DataFrame({"Month":[months_dict[i] for i in months_dict.keys()], "Opening_Balance":0, "Closing_Balance":0})

def get_opening_closing(df, opening_closing):
    df = df.copy()
    opening_closing = opening_closing.copy()
    for index_1, row_1 in opening_closing.iterrows():
                mon = row_1['Month']
                for index_2, row_2 in df.iterrows():
                    date = row_2['valueDate']
                    type_trans = row_2['type']
                    bal = row_2["balance"]
                    amnt = row_2["amount"]
                    m = date.month
                    m = months_dict[m]
                    if m == mon:
                        ind = opening_closing.index[opening_closing['Month']==mon].tolist()
                        if type_trans == "DEBIT":
                            opening_closing.at[ind[0], "Opening_Balance"] = bal + amnt
                        else:
                            opening_closing.at[ind[0], "Opening_Balance"] = bal - amnt
                        break
    
    for index_1, row_1 in opening_closing.iterrows():
        mon = row_1['Month']
        opening = row_1['Opening_Balance']
        ind = opening_closing.index[opening_closing['Month']==mon].tolist()
        #print (ind)
        if ind[0] == 0:
                opening_closing.at[11, "Closing_Balance"] = opening
        else:
            opening_closing.at[ind[0]-1, "Closing_Balance"] = opening
    return opening_closing            
opening_closing = get_opening_closing(output_df, opening_closing)

opening_closing.to_json(r"C:\FreeFinance2\FreeFinance2\Database\openingClosing.json", orient = 'records')

category_list = brand_df["Category"].unique()
category_list.sort()

category_wise_exp = pd.DataFrame({"Category": category_list, "Total_Expense":0})

def get_category_exp(df, category_wise_exp):
    df = df.copy()
    category_wise_exp = category_wise_exp.copy()
    for index_1, row_1 in df.iterrows():
            cat = row_1['category']
            type_trans = row_1['type']
            amnt = row_1["amount"]
            for index_2, row_2 in category_wise_exp.iterrows():
                c = row_2['Category']
                if cat == c:
                    ind = category_wise_exp.index[category_wise_exp['Category']==cat].tolist()
                    if type_trans == "DEBIT":
                        category_wise_exp.at[ind[0], "Total_Expense"] += amnt 
                    break
    return category_wise_exp

category_wise_exp = get_category_exp(output_df, category_wise_exp)

category_wise_exp.to_json(r"C:\FreeFinance2\FreeFinance2\Database\categoryWiseYearly.json", orient = 'records')


def Convert(lst): 
    li = list(months_dict.values())
    res_dct = {"Month": li} 
    res_dct.update({lst[i]: [0]*12  for i in range(0, len(lst))})
    res_dct.update({'Total_Expense' : [0]*12})
    return res_dct
res_dict = Convert(category_list)

category_month_wise_exp = pd.DataFrame(res_dict)


def get_month_wise_category(df, category_month_wise_exp):
    df = df.copy()
    category_month_wise_exp = category_month_wise_exp.copy()
    for index_1, row_1 in df.iterrows():
            date = row_1['valueDate']
            mon_no = date.month
            type_trans = row_1['type']
            mon = months_dict[mon_no]
            amnt = row_1["amount"]
            category = row_1["category"]
            for index_2, row_2 in category_month_wise_exp.iterrows():
                m = row_2['Month']
                if mon == m:
                    ind = category_month_wise_exp.index[category_month_wise_exp['Month']==mon].tolist()
                    if type_trans == "DEBIT":
                        category_month_wise_exp.at[ind[0],category ] += amnt 
    return category_month_wise_exp          

category_month_wise_exp = get_month_wise_category(output_df, category_month_wise_exp)
category_month_wise_exp["Total_Expense"] = month_wise_exp["Total_Expense"]      
        
category_month_wise_exp.to_json(r"C:\FreeFinance2\FreeFinance2\Database\categoryMonthWise.json", orient = 'records')


def get_current_balance(df):
    df = df.copy()
    '''
    y = datetime.now().year
    m = datetime.now().month
    d = datetime.now().day
    '''
    y = 2020
    m = 6
    d = 22
    dif = 31
    act_date = d
    for index_1, row_1 in df.iterrows():
        date = row_1['valueDate']
        year = date.year
        mon = date.month
        day = date.day
        if year == y and mon == m:
            #print (day)
            dif_cur = abs(d - day)
            dif = min(dif, dif_cur)
    #print(dif)
    act_date = d - dif
    for index_1, row_1 in df.iterrows():
        bal = row_1['balance']
        date = row_1['valueDate']
        year = date.year
        mon = date.month
        day = date.day
        #print (d)
        if year == y and mon == m and act_date == day:
            #print (d)
            return (round(bal,0), str(y)+"-"+str(m)+"-"+str(d))


current_balance, date = get_current_balance(output_df)
cur_balance_df = pd.DataFrame({"date":[date], "balance":[current_balance]})
cur_balance_df.to_json(r"C:\FreeFinance2\FreeFinance2\Database\currentBalance.json", orient = 'records')


def get_month_wise_transaction(df, month):
    df = df.copy()
    df["month"] = ""
    for index_1, row_1 in df.iterrows():
        date = row_1['valueDate']
        txnId = row_1['txnId']
        mon_no = date.month
        mon = months_dict[mon_no]
        ind = df.index[df['txnId']==txnId].tolist()
        df.at[ind[0],"month"] = mon 
    df = df[df['month'] == month] 
    return df



month_wise_transactions = pd.DataFrame()
for mon in months_dict.values():
    month_wise_transac = get_month_wise_transaction(output_df, mon)
    month_wise_transactions = pd.concat([month_wise_transactions, month_wise_transac], axis = 0, ignore_index= True)

def to_str_date(x):
    x = str(x)[:10]
    return x
month_wise_transactions["valueDate"] =month_wise_transactions["valueDate"].apply(to_str_date)

for i in range(month_wise_transactions.shape[0]):
    #print (month_wise_transactions["valueDate"][i])
    da = int(month_wise_transactions["valueDate"][i][-2:])
    mo = int(month_wise_transactions["valueDate"][i][5:7])
    mon = months_dict[mo]
    month_wise_transactions.at[i,"valueDate"] = str(da) + " " + mon

month_wise_transactions.to_json(r"C:\FreeFinance2\FreeFinance2\Database\monthWiseTransactions.json", orient = 'records')

month_wise_transactions.columns
def get_category_wise_transaction(df, category):
    df = df.copy()
    df = df[df['category']==category]
    return df


category_wise_transactions = pd.DataFrame()
for cat in category_list:
    cat_wise_transac = get_category_wise_transaction(output_df, cat)
    category_wise_transactions = pd.concat([category_wise_transactions, cat_wise_transac], axis = 0, ignore_index= True)

category_wise_transactions.to_json(r"C:\FreeFinance2\FreeFinance2\Database\categoryWiseTransactions.json", orient = 'records')
brands_list = output_df["brand"].unique().tolist()


brand, amount = [],[]
invalid_categories = ["Bills", "Cash Withdrawal", "Health", "Insurance", "Investment", "Loan (EMI)", "Other", "Rent", "Transfer", "Credit Card"]
def get_brand_wise(output_df):
    output_df = output_df.copy()
    for b in brands_list:
        ind = output_df.index[output_df['brand']==b].tolist()
        t_type = output_df.at[ind[0],"type"]
        cat = output_df.at[ind[0],"category"]
        b_amount = 0
        if t_type == "DEBIT" and cat not in invalid_categories:
            for i in ind:
                amnt = output_df.at[i, "amount"]
                b_amount += amnt
            brand.append(b)
            amount.append(b_amount) 

get_brand_wise(output_df)             
amount, brand = zip(*sorted(zip(amount, brand), reverse =True))

brandWise = pd.DataFrame({"brand": brand, "amount": amount})

brandWise.to_json(r"C:\FreeFinance2\FreeFinance2\Database\brandWise.json", orient = 'records')


# Assume brandWise is already defined as a DataFrame
brandWiseOther = brandWise.iloc[:7].copy()  # Use .iloc for slicing
others = brandWise.iloc[7:].copy()  # Get remaining rows

# Calculate total amount for 'Others'
oth_amnt = others["amount"].astype(int).sum()

# Append "Others" row correctly using pd.concat()
others_row = pd.DataFrame([{"brand": "Others", "amount": oth_amnt}])
brandWiseOther = pd.concat([brandWiseOther, others_row], ignore_index=True)

# Save to JSON
output_path = r"C:\FreeFinance2\FreeFinance2\Database\brandWiseOther.json"
brandWiseOther.to_json(output_path, orient="records", indent=4)


july_trans = month_wise_transactions[month_wise_transactions["month"] == "July"]

july_trans = july_trans[july_trans["type"]=="DEBIT"]
july_brands = july_trans["brand"].tolist()
july_brands = set(july_brands)
july_trans = july_trans.reset_index()
# MANUAL WORK: MAKE IT PROPER IF TIME
july_brands.remove(' IDBI Home Loan')
july_brands.remove('Axis Privilege CC PMT')
july_brands.remove('BESCOM')
july_brands.remove('Cash Withdrawal (cashwdl)')
july_brands.remove('IndiaFirst Life Insurance')
july_brands.remove('Indian Oil')
july_brands.remove('Ion Broadband')
july_brands.remove('Max Life Insurance')
july_brands.remove('Motilal Oswal ')
july_brands.remove('PNB Personal Loan')
july_brands.remove('Principal Mutual Fund')
july_brands.remove('Rent')
july_brands.remove('SBI Elite CC PMT')
july_brands.remove('Tatasky')

br_dict = {}
for i in july_brands:
    br_dict[i] = 0

for i in range(july_trans.shape[0]):
   # print(i)
    brd = july_trans["brand"][i]
    #print(brd)
    amnt = july_trans["amount"][i]
    if brd in july_brands:
        br_dict[brd] += int(amnt)

br_dict = sorted(br_dict.items(), key=lambda x: x[1], reverse=True)
brd_li = []
amnt_li = []
for i in br_dict:
    brd_li.append(i[0])
    amnt_li.append(i[1])

brandWiseMonth = pd.DataFrame({"brand":brd_li, "amount":amnt_li})
brandWiseMonth.to_json(r"C:\FreeFinance2\FreeFinance2\Database\brandWiseMonth.json", orient = 'records')


month_li = list(months_dict.values())

mo_li = []
br_li = []
amt_li = [] 
da_li = []

avoid = ["SAL FINTECH PRODUCTS and SOLUTIONS", " IDBI Home Loan", "IndiaFirst Life Insurance", "Axis Privilege CC PMT", "Max Life Insurance", "PNB Personal Loan", "Motilal Oswal ", "SBI Elite CC PMT" ,"Unknown", "Cash Withdrawal (cashwdl)" ,"Rent", "BESCOM", "Principal Mutual Fund"]
done = 0
for m in month_li:
    done = 0
    d = month_wise_transactions[month_wise_transactions["month"]==m]
    d = d.reset_index()
    d.sort_values(by=['amount'], inplace=True, ascending=False)
    d = d.reset_index()
    for i in range(d.shape[0]):
        if done==0:
            bnd = d['brand'][i]
            amt = d['amount'][i]
            da = d['valueDate'][i]
            if bnd not in avoid:
                mo_li.append(m)
                br_li.append(bnd)
                amt_li.append(amt)
                da_li.append(da)
                done = 1

topBrandMonth = pd.DataFrame({"month": mo_li, "brand":br_li, "amount":amt_li, "date":da_li})
topBrandMonth.to_json(r"C:\FreeFinance2\FreeFinance2\DatabasetopBrandMonth.json", orient = 'records')


fav_brands = ["iPlanet", "Adidas", "Gilly's", "H&M"]
favBrands = pd.DataFrame({"brand":fav_brands})
favBrands.to_json(r"C:\FreeFinance2\FreeFinance2\Database\favBrands.json", orient = 'records')


print("Files generated")
