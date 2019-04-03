import mysql.connector                               #mysql connector  to database
import smtplib                                       #simple mail transfer protocol lib
import pandas as pd                                  #pandas for dataframe
from email.mime.multipart import MIMEMultipart       #Multipurpose Internet Mail Extensions
from email.mime.text import MIMEText

mydb = mysql.connector.connect(                      #connection to local database
  host="127.0.0.1",                                  #Host IP
  user="root",                                       #database username
  passwd="pass",                                     #database password
  auth_plugin='mysql_native_password',               #password auth type
  database="flt"                                     #schema name
)

cursor=mydb.cursor()                                 #assigning cursor
cursor.execute ("""select air.tail_number, m.model_number, m.description, comp.company_name, codes.code, codes.country_name, codes.SDF_COC_003, codes.SDF_COC_002
from aircraft air
left join model m on air.mdl_auto_key=m.mdl_auto_key
left join companies comp on air.cmp_owner=comp.cmp_auto_key
left join country_codes codes on comp.coc_auto_key=codes.coc_auto_key""")             #SQL querry to fetch needed data
result=cursor.fetchall()                            #fetching data

#creating two dataframes for two different tables, adding column names
df1=df = pd.DataFrame(result, columns=["Tail Number", "Model Number", "Model Description", "Company Name", "Country Code", "Country", "Europe", "Continental"])

df=df[df['Continental']=="Europe"]    #dataframe for aircrafts from Europe
df1=df1[df1['Continental']!="Europe"] #dataframe for aircrafts not from Europe

#defining  custom format
def highlight(s):
    is_T = pd.Series(data=False, index=s.index)  #creating series as long as dataframe
    is_T['Europe'] = s.loc['Europe'] == 'T'      #checking if Europe column row value is equal to T. Assigning to is_T series
    return ['background-color: 75a1f7' if is_T.any() else 'background-color: #ff6666' for v in is_T]   #if is_T true return light blue, otherwise light red. For every value in is_T

table_eu=df.style.apply(highlight, axis=1).hide_index().hide_columns(['Europe','Continental']).render()  #assigning style (coloring) to table_eu. hiding indexes and two columns. Rendering html

table_non_eu=df1.style.hide_index().hide_columns(['Europe','Continental']).render()                      #assigning style to table_eu. hiding indexes and two columns. Rendering html

#writing html message
html = """
<html><body><p>Hello, .</p>
<p>Aircrafts which belong to European companies [light-blue]:</p>

{table1}

<p>Aircrafts from outside Europe:</p>

{table2}

<p>Regards,</p>
<p>Ernestas</p>
</body></html>
"""

html = html.format(table1=table_eu, table2=table_non_eu)  #assigning values to table1 and table2

#smtp settings
me = 'mail@gmail.com'           #sender
password = 'pass'            #sender's password
server = 'smtp.gmail.com:587'       #smtp server for gmail tls
you = 'meee@gmail.lt' #receiver

#creating message
message = MIMEMultipart(
    "related", None,[ MIMEText(html,'html')])
message['Subject'] = "Aircraft data"
message['From'] = me
message['To'] = you


server = smtplib.SMTP(server)
server.ehlo()                      #open transmission
server.starttls()                  #using tsl protocol
server.login(me, password)         #loging as sender
server.sendmail(me, you, message.as_string()) #sending mail
server.quit()
