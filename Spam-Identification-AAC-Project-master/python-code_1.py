# -*- coding: utf-8 -*-
#Spyder Editor - HimanshuGupta- created 13 Jan 2021

import pandas as pd
from nltk.tokenize import RegexpTokenizer
import mysql.connector

#creating mysql connection
print("\nConnecting to Database....")
mydb = mysql.connector.connect(
  host="localhost",
  user="himanshu",
  password="himanshu123",
  database="AAC_Project_Spam_Filteration"
)
mycursor = mydb.cursor()
print("Database connection successful....")


#insert in db function - table : tokens
def insertInDatabaseTokens(sno,sendermail,category,status,subject,content,num_tokens) :    
    sql = "INSERT INTO tokens (sno,sender,category,status,subject,content,num_tokens) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    val = (sno,sendermail,category,status,subject,content,num_tokens)
    mycursor.execute(sql, val)
    mydb.commit() 

    
#insert in db function - table : statistics
def insertInDatabaseStatistics(token,numSpam,numNonspam) :  
    spam = numSpam[0]
    nonspam = numNonspam[0]
    sql = "INSERT INTO statistics (token,num_NONSPAM,num_SPAM) VALUES (%s,%s,%s)"
    val = (token,nonspam[0],spam[0])
    mycursor.execute(sql, val)
    mydb.commit() 


#execute query ofn db - tokens
def executeInDatabaseAndReturnSingleOutput(sql):
    mycursor.execute(sql)
    output_temp = mycursor.fetchall()
    output = output_temp[0]
    return output[0]


#delete from db function
def deleteFromDatabase():
    sql = "DELETE FROM tokens"
    mycursor.execute(sql)
    mydb.commit()
    sql = "DELETE FROM statistics"
    mycursor.execute(sql)
    mydb.commit()
    print("Local storage cleared..!!")


#function to read data from csv and load in cache, that is, mysql db
def readDataAndLoad(garbage):
    deleteFromDatabase()
    excel = pd.read_csv('DataBase_Mails.csv')
    rows = len(excel)
    cols = len(list(excel))
    print("Number of Rows in DataSheet : ",rows,"\nNumber of Columns in DataSheet : ",cols) 
    data = {}
    
    #fetch excel data and store in Dictionary
    for i in range(rows) :
        temp = []
        X = excel.iloc[[i],1:].values
        temp.append(X[-1])
        data[i] = temp
        
    #iterate over dictionary and create tokens
    for i in range(rows) :
        temp_row = data.get(i)
        row = temp_row[0]
        content_list = row[4]
        tokenizer = RegexpTokenizer(r'\w+')
        tokenizer1 = RegexpTokenizer(r'\d+')
        content_mail = tokenizer.tokenize(content_list)
        content_mail_1 = tokenizer1.tokenize(content_list)
        
        #remove numbers from token list created
        for j in range(len(content_mail_1)):
            item1 = content_mail_1[j]
            if item1 in content_mail:
                content_mail.remove(item1)
    
        #remove garbage values from token list created
        content_token = ""
        counter_token = 0;
        content_mail.sort()
        for x in content_mail:
            count_content = 0
            for y in garbage:
                if (x.lower() == y.lower()) :
                    count_content += 1
                    break;    
            if ((count_content == 0) and (x.lower() not in content_token)) :
                counter_token += 1;
                content_token += x.lower()+","        
        
        insertInDatabaseTokens("M_"+str(i+1),row[0],row[1],row[2],row[3],content_token,counter_token)
    
    print("Token(s) created successfully..!!")
    print("Token(s) stored in local storage / cache created.")


#function to tokeinize the content of new email and retunr body tokens
def tokenizeNewEmail(body) :
    tokenizer = RegexpTokenizer(r'\w+')
    tokenizer1 = RegexpTokenizer(r'\d+')
    body_list = tokenizer.tokenize(body)
    body_list1 = tokenizer1.tokenize(body)
    
    #remove numbers from token list created
    for j in range(len(body_list1)):
        item1 = body_list1[j]
        if item1 in body_list:
            body_list.remove(item1)
            
    #data structures to store tokens for content of new email coming
    body_token = {}
    body_list.sort()
    
    #code to remove punctuation marks and garbage keywords from body tokens
    for x in body_list:
        count_body = 0
        for y in garbage:
            if (x.lower() == y.lower()) :
                count_body += 1
        
        if ((count_body == 0) and (x.lower() not in body_token)) :
            body_token[x.lower()] = 0
    print("\nBody - Token : ",body_token)
    return body_token;


#function to count occurance of each token in mail list, seperated by category - spam or non-spam
def countOccuranceOfTokenInMialList(body_token) :
    for x in body_token:
        sql1 = "SELECT count(*) from tokens where category='I' and content like '%"+x+"%'"
        mycursor.execute(sql1)
        numOfNonSpamEmail = mycursor.fetchall()
        sql2 = "SELECT count(*) from tokens where category='S' and content like '%"+x+"%'"
        mycursor.execute(sql2)
        numOfSpamEmail = mycursor.fetchall()
        insertInDatabaseStatistics(x,numOfSpamEmail,numOfNonSpamEmail)
    print("\nToken count successful..!!")


#function to find probability of a word in spam mails
def calculateProbabilityOfWordInSpam(word,numwordspam,numwordtotal):
    alpha = 1
    n_wi_spam = executeInDatabaseAndReturnSingleOutput("select num_SPAM from statistics where token='"+word+"'")
    output = (n_wi_spam + alpha) / (numwordspam + numwordtotal)
    return output


#function to find probability of a word in non-spam mails
def calculateProbabilityOfWordInNonSpam(word,numwordnonspam,numwordtotal):
    alpha = 1
    n_wi_nonspam = executeInDatabaseAndReturnSingleOutput("select num_NONSPAM from statistics where token='"+word+"'")
    output = (n_wi_nonspam + alpha) / (numwordnonspam + numwordtotal)
    return output
    

if __name__ == "__main__":
    #creating garbage dictionary
    garbage = ["all" , "another" , "any" , "anybody" , "anyone" , "anything" , "as" , "aught" , "both" , "each" , "eachother" , "either" , "enough" , "everybody" , "everyone" , "everything" , "few" , "he" , "her" , "hers" , "herself" , "him" , "himself" , "his" , "I" , "idem" , "it" , "its" , "itself" , "many" , "me" , "mine" , "most" , "my" , "myself" , "naught" , "neither" , "noone" , "nobody" , "none" , "nothing" , "nought" , "one" , "oneanother" , "other" , "others" , "ought" , "our" , "ours" , "ourself" , "ourselves" , "several" , "she" , "some" , "somebody" , "someone" , "something" , "somewhat" , "such" , "suchlike" , "that" , "thee" , "their" , "theirs" , "theirself" , "theirselves" , "them" , "themself" , "themselves" , "there" , "these" , "they" , "thine" , "this" , "those" , "thou" , "thy" , "thyself" , "us" , "we" , "what" , "whatever" , "whatnot" , "whatsoever" , "whence" , "where" , "whereby" , "wherefrom" , "wherein" , "whereinto" , "whereof" , "whereon" , "wherever" , "wheresoever" , "whereto" , "whereunto" , "wherewith" , "wherewithal" , "whether" , "which" , "whichever" , "whichsoever" , "who" , "whoever" , "whom" , "whomever" , "whomso" , "whomsoever" , "whose" , "whosever" , "whosesoever" , "whoso" , "whosoever" , "ye" , "yon" , "yonder" , "you" , "your" , "yours" , "yourself" , "yourselves" , "only" , "now" , "when" , "is" , "i" , "are" , "have" , "am" , "has" , "get" , "give" , "new" , "old" , "had" , "been" , "more" , "and" , "or" , "not" , "how" , "why" , "can" , "could" , "a" , "an" , "the" , "might" , "will" , "would" , "should" , "it" , "was" , "were" , "here" , "using" , "jan" , "feb" , "mar" , "apr" , "may" , "jun" , "jul" , "aug" , "sept" , "oct" , "nov" , "dec" , "january" , "february" , "march" , "april" , "june" , "july" , "august" , "september" , "october" , "november" , "december" , "for" , "hi" , "hello" , "while" , "if" , "in" , "age" , "up" , "down" , "right" , "left" , "too" , "with" , "did" , "do"]
    
    readDataAndLoad(garbage)
    
    #subject,body,sender of new email
    subject = "New Job - C++ Developer,CPP Programmer,Software Engineer,Software Programmer | More jobs matching your Search Alert - Developer Jobs Searched June 5 and or not has have been"
    body = "9 Jobs matching your search alert Developer Jobs Searched June 5, C++ Developer (Immediate Joiners only), HR Remedy India and or not has have been"
    sender =  "jobs@naukri.com"
    
    #tokenize new email and store tokens in variable
    body_token = tokenizeNewEmail(body)
    
    #count occurance of each token in token list
    countOccuranceOfTokenInMialList(body_token)
    
    #count total nonspam mails
    numOfNonSpamMails = executeInDatabaseAndReturnSingleOutput("SELECT count(*) from tokens where category='I'")
    print("Number of Non-spam mails : ",numOfNonSpamMails);
    
    #count total spam mails
    numOfSpamMails = executeInDatabaseAndReturnSingleOutput("SELECT count(*) from tokens where category='S'")
    print("Number of Non-spam mails : ",numOfSpamMails);
    
    #count total words in spam email
    totalWordsInSpam = executeInDatabaseAndReturnSingleOutput("SELECT sum(num_tokens) from tokens where category='S'")
    print("Number of words in Spam email - ",totalWordsInSpam)
    
    #count total words in non spam email
    totalWordsInNonSpam = executeInDatabaseAndReturnSingleOutput("SELECT sum(num_tokens) from tokens where category='I'")
    print("Number of words in Non-Spam email - ",totalWordsInNonSpam)
    
    #total words in mail list
    totalWordsInMailList = totalWordsInSpam + totalWordsInNonSpam
    
    #calculating P(spam|w1,w2,w3,.....,wn)
    probspam = numOfSpamMails / (numOfNonSpamMails + numOfSpamMails)
    print("Probability of spam messages : ", probspam)
    for x in body_token:
        prob_wi_spam = calculateProbabilityOfWordInSpam(x,totalWordsInSpam,totalWordsInMailList)
        probspam *= float(prob_wi_spam)
    #probspam = round(probspam, 3)
    print("P(spam|wi) = ",probspam)
    
    #calculating P(spam|w1,w2,w3,.....,wn)
    probnonspam = numOfNonSpamMails / (numOfNonSpamMails + numOfSpamMails)
    print("Probability of non-spam messages : ", probnonspam)
    for x in body_token:
        prob_wi_nonspam = calculateProbabilityOfWordInNonSpam(x,totalWordsInNonSpam,totalWordsInMailList)
        probnonspam *= float(prob_wi_nonspam)
    #probnonspam = round(probnonspam, 3)
    print("P(Non-spam|wi) = ",probnonspam)
    