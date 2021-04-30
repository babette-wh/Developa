# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 01:29:10 2021

@author: Malin Spørck
"""

import bz2
import sqlite3
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def print_explanation():
    print(
''' 
------------------------------------------------------------------------
This application opens file1 with Traffic Data arranged in the following sequence:
Time, Duration, SrcDevice, DstDevice, Protocol, SrcPort, DstPort, SrcPackets, DstPackets, SrcBytes, DstBytes
        
It connects to an sqlite database, inserts data from the traffic data file into the database in the table "Network_Traffic"
        
The application also runs queries in the database to analyze trafficdata and change status in entries of traffic that looks suspicious, based on conditions set in the database table "Criteria"
        
Menu:
            
    1: Read data from file and store data in database
        - Input parameter: number of lines to read from file (100000 elements is recomended)
    2: Run Check For Suspicious Traffic 
    3: Create report over suspicious data and store to Report_dd.month-yyyy_hh.mm.pdf 
    4: Create charts over suspicious data and store them as .png images 
    0: Exit
------------------------------------------------------------------------
''')
    
"""
Checks for suspicious traffic based on criterias described in Criteria SQL table
ToDo: Must create checkers so that we do not register duplicates in the database, before calling Readfile
"""
def RunCheckForSuspiciousTraffic():
    print("\nRuning check(s) for suspicious traffic...")
    try:
        cursor = conn.cursor()      
        criterias = []
        for row in cursor.execute('SELECT SQL from Criteria'):
            """Stripping down sql string for unwanted characters"""
            SQL_Criteria = str(row).replace('("',"").replace(')",',"")
            criterias.append(SQL_Criteria)
        
        for elements in criterias:
            print("sql " + elements)            
            cursor.execute(elements)  
        conn.commit()                    
            
    except Exception as err:
        print ('Query Failed: %s\nError: %s' % ("SQL", str(err)))
   
    finally:
        cursor.close()
        """ print ('Closing the connection')"""
 
"""
NewItem(Time, Duration, SrcDevice, DstDevice, Protocol, SrcPort, DstPort, SrcPackets, DstPackets, SrcBytes, DstBytes):
This function is used to store data from the input file to SQLITE database. 
""" 
def NewItem(Time, Duration, SrcDevice, DstDevice, Protocol, SrcPort, DstPort, SrcPackets, DstPackets, SrcBytes, DstBytes):
    try:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Network_Traffic (Time, Duration, SrcDevice, DstDevice, Protocol, SrcPort, DstPort, SrcPackets, DstPackets, SrcBytes, DstBytes) 
                  VALUES (?,?,?,?,?,?,?,?,?,?,?) ;''',(Time, Duration, SrcDevice, DstDevice, Protocol, SrcPort, DstPort, SrcPackets, DstPackets, SrcBytes, DstBytes))        
    except Exception as err:
        print ('Query Failed: %s\nError: %s' % ("SQL", str(err)))
    else:
        NewId = cursor.execute('SELECT last_insert_rowid();').fetchone()[0]
        """print('New record inserted with id ' + str(NewId))"""
    finally:
        cursor.close()
        """ print ('Closing the connection')"""
"""
ReadFile(filename, numb_lines):
Used to create reade .bz2 file and store items in SQLITE database, by callling the function 
NwewItem(,,,) with the parameters from the input file
When the file has been read  and the data has been added to the database, 
the function exits after committing the changes to the database 

Code created with inspiration from
Anon., 2021. Reading first lines of bz2 files in python - Stack Overflow. [online] Available at:
<https://stackoverflow.com/questions/37172679/reading-first-lines-of-bz2-files-in-python> 
[Accessed 30 April 2021].

Obtaining the bz2 file we used as dataset
Anon., 2021. Unified Host and Network Data Set - Cyber Security Research. [online] Available at:
<https://csr.lanl.gov/data/2017/> 
[Accessed 30 April 2021].
""" 
def ReadFile(filename, numb_lines):   
    print("Reading file...") 
    source_file = bz2.open(filename, "r")
    count = 0
    
    for line in source_file:
        
        if(count < int(numb_lines)):
            x = str(line).replace("b'","")
            y = str(x).replace("\\n","")
            yy = str(y).replace("Port","")
            zz = str(yy).replace("'","")
            z = str(zz).split(",")           
            NewItem(z[0], z[1], z[2], z[3], z[4], z[5], z[6], z[7], z[8], z[9], z[10])
        else: 
            break
        count += 1
        read_count = int(numb_lines)/10
        if(count%read_count == 1 and count > 1):
            print(str(int(count/read_count)*10) + "%")
            
    conn.commit()
    print("Data stored in database")
"""
CreateReport(sql):
Used to create report and store result in .pdf file (Report_dd.month-yyyy_hh.mm.pdf )
Code created with inspiration from
Anon., 2021. How do I plot only a table in Matplotlib? - Stack Overflow. [online] Available at: 
<https://stackoverflow.com/questions/32137396/how-do-i-plot-only-a-table-in-matplotlib> 
[Accessed 30 April 2021].
"""    
def CreateReport(sql):        
    print("Creating report...")
    cursor.execute(sql)
    rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns = ("ID", "Time", "Duration", "SrcDevice", "DstDevice", "Protocol", "SrcPort", "DstPort", "SrcPackets", "DstPackets", "SrcBytes", "DstBytes", "Status"))
        
    fig, ax =plt.subplots(figsize=(12,5))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')

    x = datetime.datetime.now()

    pp = PdfPages("Report_" + str(x.strftime("%d.%B-%Y_%H.%M")) + ".pdf")
    pp.savefig(fig, bbox_inches='tight')
    pp.close()
    
    print("Report created " + " Report_" + str(x.strftime("%d.%B-%Y_%H.%M")) + ".pdf")

"""
CreateChart(sql, filename, X, Y):
Used to create charts and store result to .png files
Code created with inspiration from
Anon., 2021. Pandas Dataframe: Plot Examples with Matplotlib and Pyplot. [online] Available at: 
<http://queirozf.com/entries/pandas-dataframe-plot-examples-with-matplotlib-pyplot> 
[Accessed 30 April 2021].
"""
def CreateChart(sql, filename, X, Y):
    print("Creating chart " + X + "...")    
    cursor.execute(sql)
    rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns = ("ID", "Time", "Duration", "SrcDevice", "DstDevice", "Protocol", "SrcPort", "DstPort", "SrcPackets", "DstPackets", "SrcBytes", "DstBytes", "Status", Y))
    
    ax = plt.gca()
    df.plot(kind='bar',x=X,y=Y, figsize=(15, 15))
    plt.xlabel(X)   
  
    plt.savefig(filename)   
    
    print("Chart created " + filename + "\n")  

"""Connection to database"""
conn = sqlite3.connect('NetworkAnalyzerDatabase.db')
cursor = conn.cursor()

"""
Printing menu
"""
running = True
while (running):
    print_explanation()
    option = input("Enter choice: ")
   
    if option.isdigit():
        if(int(option)==1):
            numb_lines = input("Number of lines to read from file: ")
            ReadFile("Traffic_Data.crdownload", numb_lines)
        elif(int(option)==2):            
            RunCheckForSuspiciousTraffic()
            
        elif(int(option)==3):
            sql = "select * from Network_Traffic where Status = 'Suspicious' limit 100"
            CreateReport(sql)
        elif(int(option)==4):  
            """Number of attempted tries to communicate on the different commonly abused ports"""
            sql = "select *, count(DstPort) from Network_Traffic where Status = 'Suspicious' group by dstport order by dstport"
            CreateChart(sql, "chart1.png", "DstPort", "Number_of_communications")
            
            """Number of attemted tries to communicate on the different commonly abused ports ordered by which computter the attemts is on. limited to the 10 computers with the most attempts"""
            sql = "select *, count(DstPort) from Network_Traffic where Status = 'Suspicious' group by dstdevice order by count(DstPort) desc limit 20"
            CreateChart(sql, "chart2.png", "DstDevice", "Number_of_communications")
            
            """Number of attemted tries to communicate on the different commonly abused ports ordered by which computter that attemted the communication. limited to the 10 computers with the most attempts"""
            sql = "select *, count(DstPort) from Network_Traffic where Status = 'Suspicious' group by srcdevice order by count(DstPort) desc limit 20"
            CreateChart(sql, "chart3.png", "SrcDevice", "Number_of_communications")                
        elif(int(option)==0):
            running = False       
cursor.close()