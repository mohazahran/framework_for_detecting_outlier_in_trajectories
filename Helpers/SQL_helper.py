'''
Created on Aug 21, 2016

@author: Mohamed Zahran
'''
import MySQLdb
import os, sys

CAT_PATH = 'D:\Career\Work\Purdue\PhD_courses\Summer2016_sem3\Data\pins.csv_TRANSLATION.txt'

def initializeConnection():
    db = MySQLdb.connect(host="127.0.0.1", # your host, usually localhost                     
                         user="root", # your username
                          passwd="admin", # your password
                          use_unicode=True,
                          charset="utf8",
                          db="pinterest") # name of the data base
    return db

def getEnglishWords(db, englishIds):
    eWords = []
    for eId in  englishIds:
        cur = db.cursor()
        cur.execute("SELECT * FROM englishwords e where EnWID="+str(eId))
        for row in cur.fetchall() :
            eWords.append(row[1])
            break
    return eWords



def insertCateogry(cur, theId, cat):
    #INSERT INTO Customers (CustomerName, City, Country) VALUES ('Cardinal', 'Stavanger', 'Norway');
    sql1 = 'INSERT INTO categories (catId, category) VALUES '+'('+'\''+str(theId)+'\''+','+'\''+cat+'\''+')'
    cur.execute(sql1)
    

def addCategory(cur, theId, link, cat):        
    #UPDATE table_name SET column1=value1,column2=value2,... WHERE some_column=some_value;
    sql2 = 'UPDATE pins SET catId='+'\''+str(theId)+'\''+' WHERE website='+'\''+link+'\''
    cur.execute(sql2)


def prepRepinData(cur):
    wr = open ('D:\Career\Work\Purdue\PhD_courses\Summer2016_sem3\Data\sqlData_repins','w')
    sql = 'SELECT p.pinId, rep.`userId1` AS user1Follower, p.website, p.catId, c.category \
           FROM pins p, `categories` c, `repins` rep \
           WHERE p.`catId` = c.`catId` AND p.`pinId` = rep.`pinId` AND rep.`userId2` = p.`userId` AND c.`catId` <> -1 AND c.`catId` <> 3 \
           ORDER BY user1Follower ASC'
           
    #sql = 'SELECT `categories`.`catId`, `categories`.`category` FROM `categories`'
    res = cur.execute(sql)
    print(res)
    for row in cur.fetchall():
        for col in row:
            wr.write(str(col) + '\t')
        wr.write('\n')
    wr.close()


def main():
    db = initializeConnection()
    cur = db.cursor()
    prepRepinData(cur)
#     r = open(CAT_PATH,'r')    
#     catCount = 0
#     catDic = {}
#     for line in r:
#         parts = line.strip().split('\t')
#         parts[1] = parts[1].lower()
#         if(parts[1] not in catDic):          
#             catCount += 1
#             catDic[parts[1]] = catCount
#             insertCateogry(cur, catCount, parts[1])
#             
#         addCategory(cur, catDic[parts[1]], parts[0], parts[1])        
#         print(catCount, catDic[parts[1]], line)            
#         db.commit()
#    r.close()
    db.close()
    

main()
print('DONE!')