import json
import csv
import pandas as pd
import numpy as np


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

json2csv(r'C:\FreeFinance2\FreeFinance2\Database\customer_alldata.json', r'C:\FreeFinance2\FreeFinance2\Database\bank_details.csv','accounts')

df = pd.read_csv(r'C:\FreeFinance2\FreeFinance2\Database\bank_details.csv')


bank_name, account_type, account_no, principalAmount, currentValue, maturityAmount, recurringAmount, tenureDays, tenureMonths, tenureYears, interestRate, description  = [], [], [], [], [], [], [], [], [], [], [], []
for i in range(df.shape[0]):
    stri1 = df.at[i,"Summary"].replace("{","")
    stri1 = stri1.replace("}","")
    stri1 = stri1.replace("'",'')
    #print(stri1)
    li = stri1.split(',')
    #print(li)
    type_ac = li[3].split(':')
    #print(type_ac)
    type_account1 = type_ac[1].strip() #Account type
    #print(type_account1)
    if type_account1 == "RECURRING":
        print("in")
        bank_name1 = df.at[i,"bank"] #Bank name
        account_no1 = df.at[i,"maskedAccountNumber"] #Account no
        maturity_am = li[4].split(":")
        maturity_amount1 = maturity_am[1].strip() #Maturity Amount
        desc = li[6].split(":")
        description1 = desc[1].strip() #Description
        int_rate = li[8].split(":")
        interest_rate1 = int_rate[1].strip() #Interest Rate
        principal_am = li[9].split(':')
        principal_amount1 = principal_am[1].strip() #Principal Amount
        tenure_da = li[10].split(":")
        tenure_days1 = tenure_da[1].strip() #Tenure Days
        tenure_mo = li[11].split(":")
        tenure_months1 = tenure_mo[1].strip() #Tenure Months
        tenure_ye = li[12].split(":")
        tenure_years1 = tenure_ye[1].strip() #Tenure Year
        rec_amount = li[13].split(":")
        recurring_amount1 = rec_amount[1].strip() #Recurring Amount
        cur_value = li[19].split(":")
        current_value1 = cur_value[1].strip() #Current Value
        bank_name.append(bank_name1)
        account_type.append(type_account1)
        account_no.append(account_no1)
        maturityAmount.append(maturity_amount1)
        description.append(description1)
        interestRate.append(interest_rate1)
        principalAmount.append(principal_amount1)
        tenureDays.append(tenure_days1)
        tenureMonths.append(tenure_months1)
        tenureYears.append(tenure_years1)
        recurringAmount.append(recurring_amount1)
        currentValue.append(current_value1)       
        

        print(bank_name, account_type, account_no, principalAmount, currentValue, maturityAmount, recurringAmount, tenureDays, tenureMonths, tenureYears, interestRate, description
    )
        #Account Type
        #print (bank_name1, current_balance1, account_no1, type_account1)

        
df_out = pd.DataFrame({"bankName": bank_name, "accountNo": account_no, "typeAccount": account_type, 
                      "principalAmount": principalAmount, "maturityAmount": maturityAmount, "recurringAmount": recurringAmount, "tenureDays": tenureDays, "tenureMonths" : tenureMonths,
                       "tenureYears": tenureYears, "currentValue": currentValue, "interestRate": interestRate, "description": description})
        

df_out.to_json(r"C:\FreeFinance2\FreeFinance2\Database\rdDetails.json", orient = 'records')
print("File generated")