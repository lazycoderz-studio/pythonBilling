from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import pymysql

window = Tk()
window.geometry("900x600")
window.title("Billing")

#===========field listner ==========================
def quantityFieldListener(a,b,c):
    global quantityVar
    global costVar
    global itemRate
    quantity = quantityVar.get()
    if quantity != "":
        try:
            quantity=float(quantity)
            cost = quantity*itemRate
            quantityVar.set("%.2f"%quantity)
            costVar.set("%.2f"%cost)
        except ValueError:
            quantity=quantity[:-1]
            quantityVar.set(quantity)
    else:
        quantity=0
        quantityVar.set("%.2f"%quantity)
def costFieldListener(a,b,c):
    global quantityVar
    global costVar
    global itemRate
    cost = costVar.get()
    if cost !="":
        try:
            cost = float(cost)
            quantity=cost/itemRate
            quantityVar.set("%.2f"%quantity)
            costVar.set("%.2f"%cost)
        except ValueError:
            cost=cost[:-1]
            costVar.set(cost)
    else:
        cost=0
        costVar.set(cost)

#============= global variable for  entries===========
#========login variable========
usernameVar = StringVar()
passwordVar = StringVar()

#============main window variable=======
options=[]
rateDict={}
itemVariable=StringVar()
quantityVar = StringVar()
quantityVar.trace('w',quantityFieldListener)
itemRate=2
rateVar = StringVar()
rateVar.set("%.2f"%itemRate)
costVar=StringVar()
costVar.trace('w', costFieldListener)
#========mainTreeView======================
billsTV = ttk.Treeview(height=15, columns=('Rate','Quantity','Cost'))

#==========update tree View
updateTV = ttk.Treeview(height=15, columns=('Name','Rate','type','Store_Type'))

#============= add item Variables==========
storeOptions=['Frozen','Fresh']
addItemNameVar=StringVar()
addItemRateVar=StringVar()
addItemTypeVar=StringVar()
addstoredVar=StringVar()
addstoredVar.set(storeOptions[0])

itemLists= list()
totalCost=0.0
totalCostVar=StringVar()
totalCostVar.set("Total Cost = {}".format(totalCost))

updateItemId=""

#=============funtion to generate bill=====================
def generate_bill():
    global itemVariable
    global quantityVar
    global itemRate
    global costVar
    global itemLists
    global totalCost
    global totalCostVar
    itemName = itemVariable.get()
    quantity=quantityVar.get()
    cost = costVar.get()
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor()
    
    query="insert into bill (name,quantity, rate, cost) values('{}','{}','{}','{}')".format(itemName,quantity,itemRate,cost)
    cursor.execute(query)
    conn.commit()
    conn.close()
    listDict = {"name":itemName, "rate":itemRate,"quantity":quantity, "cost":cost}
    itemLists.append(listDict)
    totalCost+=float(cost)
    quantityVar.set("0")
    costVar.set("0")
    updateListView()
    totalCostVar.set("Total Cost = {}".format(totalCost))
def OnDoubleClick(event):
    global addItemNameVar
    global addItemRateVar
    global addItemTypeVar
    global addstoredVar
    global updateItemId
    item = updateTV.selection()
    updateItemId= updateTV.item(item,"text")
    item_detail= updateTV.item(item,"values")
    item_index=storeOptions.index(item_detail[3])
    addItemTypeVar.set(item_detail[2])
    addItemRateVar.set(item_detail[1])
    addItemNameVar.set(item_detail[0])
    addstoredVar.set(storeOptions[item_index])
    
    

def updateListView():
    records = billsTV.get_children()

    for element in records:
        billsTV.delete(element)

    for row in itemLists:
        billsTV.insert('', 'end',text=row['name'],values=(row["rate"],row["quantity"],row["cost"]))

def getItemLists():
    records=updateTV.get_children()

    for element in records:
        updateTV.delete(element)
    
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query="select * from itemlist"
    cursor.execute(query)
    data = cursor.fetchall()
    for row in data:
        updateTV.insert('','end',text=row['nameid'],values=(row['name'],row['rate'],row['type'],row['storetype']))
    updateTV.bind("<Double-1>",OnDoubleClick)

    conn.close()
        
    
def print_bill():
    global itemLists
    global totalCost

    billString = ""
    billString+="=====================Receipt==========================\n\n"
    billString+="======================================================\n"
    billString+="{:<20}{:<10}{:<15}{:<10}\ns".format("Name", "Rate", "Quantity", "Cost")
    billString+="======================================================\n"
    
   

    
    for item in itemLists:
        billString+="{:<20}{:<10}{:<15}{:<10}\n".format(item["name"],item["rate"],item["quantity"],item["cost"])

    billString+="======================================================\n"
    billString+="{:<20}{:<10}{:<15}{:<10}\n".format("Total Cost"," "," ",totalCost)

    billFile = filedialog.asksaveasfile(mode='w',defaultextension=".txt")
    if billFile is None:
        messagebox.showerror("Invalid file Name", "Please enter valid name")
    else:
        billFile.write(billString)
        billFile.close()
        
    print(billString)
    

    itemLists =[]
    totalCost=0.0
    updateListView()
    totalCostVar.set("Total Cost = {}".format(totalCost)) 
    
    
#===============function to logOut===================
def LogOut():
    remove_all_widgets()
    loginWindow()

def moveToUpdate():
    remove_all_widgets()
    updateItemWindow()

#===============function to move to veiw bills window========
def movetoBills():
    remove_all_widgets()
    viewAllBills()
    
#=========funtion to read data from list of item
def readAllData():
    global options
    global rateDict
    global itemVariable
    global itemRate
    global rateVar
    options=[]
    rateDict={}
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = "select * from itemlist"
    cursor.execute(query)
    data = cursor.fetchall()
    count=0
    for row in data:
        count+=1
        options.append(row['nameid'])
        rateDict[row['nameid']]=row['rate']
        itemVariable.set(options[0])
        itemRate=int(rateDict[options[0]])
    conn.close()
    rateVar.set("%.2f"%itemRate)
    if count ==0:
        remove_all_widgets()
        itemAddWindow()
    else:
        remove_all_widgets()
        mainwindow()
    
def optionMenuListener(event):
    global itemVariable
    global rateDict
    global itemRate
    item = itemVariable.get()
    itemRate= int(rateDict[item])
    rateVar.set("%.2f"%itemRate)
#==========function to remove all widget
def remove_all_widgets():
    global window
    for widget in window.winfo_children():
        widget.grid_remove()

#=================update bill data===========
def updateBillsData():
    records = billsTV.get_children()

    for element in records:
        
        billsTV.delete(element)

        
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = "select * from bill"
    cursor.execute(query)
    data = cursor.fetchall()
    
    for row in data:
        billsTV.insert('', 'end',text=row['name'],values=(row["rate"],row["quantity"],row["cost"]))
    conn.close()
        
#============== admin login function=======

def adminLogin():
    global usernameVar
    global passwordVar

    username = usernameVar.get()
    password = passwordVar.get()

    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor()

    query = "select * from users where username='{}' and password='{}'".format(username, password)
    cursor.execute(query)
    data = cursor.fetchall()
    admin = False
    for row in data:
        admin = True
    conn.close()
    if admin:
        readAllData()
    else:
        messagebox.showerror("Invalid user", "Credentials enters are invalid")

def addItemListener():
    remove_all_widgets()
    itemAddWindow()


def addItem():
    global addItemNameVar
    global addItemRateVar
    global addItemTypeVar
    global addstoredVar
    name = addItemNameVar.get()
    rate = addItemRateVar.get()
    Type = addItemTypeVar.get()
    storeType= addstoredVar.get()
    nameId=name.replace(" ","_")
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor()
    query = "insert into itemlist (name,nameid,rate,type,storetype) value('{}','{}','{}','{}','{}')".format(name, nameId, rate,Type,storeType)
    cursor.execute(query)
    conn.commit()
    conn.close()
    addItemNameVar.set("")
    addItemRateVar.set("")
    addItemTypeVar.set("")
def updateItem():
    global addItemNameVar
    global addItemRateVar
    global addItemTypeVar
    global addstoredVar
    global updateItemId

    name = addItemNameVar.get()
    rate = addItemRateVar.get()
    Type = addItemTypeVar.get()
    storeType= addstoredVar.get()
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor()
    query = "update  itemlist set name='{}',rate='{}',type='{}',storetype='{}' where nameid='{}'".format(name,rate,Type,storeType,updateItemId)
    cursor.execute(query)
    conn.commit()
    conn.close()

    addItemNameVar.set("")
    addItemRateVar.set("")
    addItemTypeVar.set("")
    getItemLists()
    
def loginWindow():
    titleLabel = Label(window,text="P&E Billing System",font="Arial 40",fg="green")
    titleLabel.grid(row=0,column=0,columnspan=4, padx=(40,0),pady=(10,0))

    loginLabel = Label(window,text="Admin Login",font="Arial 30")
    loginLabel.grid(row=1, column=2,padx=(50,0),columnspan=2, pady=10)

    usernameLabel = Label(window, text="Username")
    usernameLabel.grid(row=2, column=2,padx=20,pady=5)

    passwordLabel = Label(window, text="Password")
    passwordLabel.grid(row=3, column=2,padx=20,pady=5)

    usernameEntry= Entry(window, textvariable=usernameVar)
    usernameEntry.grid(row=2, column=3,padx=20,pady=5)

    passwordEntry = Entry (window, textvariable=passwordVar,show="*")
    passwordEntry.grid(row=3,column=3,padx=20,pady=5)

    loginButton=Button(window, text="Login",width=20, height=2, command=lambda:adminLogin())
    loginButton.grid(row=4, column=2, columnspan=2)

def mainwindow():
    
    titleLabel = Label(window,text="P&E Billing System",font="Arial 30",fg="green")
    titleLabel.grid(row=0,column=1,columnspan=3,pady=(10,0))

    addNewItem = Button(window, text="Add Item", width=15, height=2, command=lambda: addItemListener())
    addNewItem.grid(row=1, column=0, padx=(10,0),pady=(10,0))
    updateItem = Button(window, text="Update Item", width=15, height=2,command=lambda: moveToUpdate())
    updateItem.grid(row=1, column=1, padx=(10,0), pady=(10,0))

    showallEntry= Button(window, text="Show Bills", width=15, height=2,command=lambda:movetoBills())
    showallEntry.grid(row=1, column=2, padx=(10,0), pady=(10,0))

    logoutBtn = Button(window, text = "Logout",width=15, height=2,command=lambda:LogOut())
    logoutBtn.grid(row=1, column=4,pady=(10,0))

    itemLabel = Label(window, text="Select Item")
    itemLabel.grid(row=2, column=0, padx=(5,0),pady=(10,0))

    itemDropDown=OptionMenu(window,itemVariable,*options,command=optionMenuListener)
    itemDropDown.grid(row=2, column=1,padx=(10,0), pady=(10,0))

    rateLabel= Label(window, text="Rate")
    rateLabel.grid(row=2, column=2, padx=(10,0), pady=(10,0))

    rateValue = Label(window, textvariable=rateVar)
    rateValue.grid(row=2, column=3, padx=(10,0), pady=(10,0))

    quantityLabel = Label(window, text="Quantity")
    quantityLabel.grid(row=3, column=0,padx=(5,0),pady=(10,0))
    quantityEntry=Entry(window, textvariable=quantityVar)
    quantityEntry.grid(row=3, column=1,padx=(5,0),pady=(10,0))

    costLabel= Label(window, text="Cost")
    costLabel.grid(row=3, column=2, padx=(10,0), pady=(10,0))

    costEntry=Entry(window, textvariable=costVar)
    costEntry.grid(row=3, column=3, padx=(10,0), pady=(10,0))

    buttonBill = Button(window, text="Add to List", width =15,command=lambda:generate_bill())
    buttonBill.grid(row=3, column=4,padx=(5,0),pady=(10,0))

    billLabel=Label(window, text="Bills", font="Arial 25")
    billLabel.grid(row=4, column=2)

    billsTV.grid(row=5, column=0, columnspan=5)

    scrollBar = Scrollbar(window, orient="vertical",command=billsTV.yview)
    scrollBar.grid(row=5, column=4, sticky="NSE")

    billsTV.configure(yscrollcommand=scrollBar.set)

    billsTV.heading('#0',text="Item Name")
    billsTV.heading('#1',text="Rate")
    billsTV.heading('#2',text="Quantity")
    billsTV.heading('#3',text="Cost")

    totalCostLabel = Label(window, textvariable=totalCostVar)
    totalCostLabel.grid(row=6,column=1)
    generateBill = Button(window, text="Generate Bills",width=15, command = lambda:print_bill())
    generateBill.grid(row=6,column=4)

    updateListView()
    
                 

def itemAddWindow():
    backButton = Button(window, text="Back" , command=lambda:readAllData())
    backButton.grid(row=0, column=1)
    titleLabel = Label(window,text="P&E Billing System", width=40,font="Arial 30",fg="green")
    titleLabel.grid(row=0,column=2,columnspan=4,pady=(10,0))

    itemNameLabel= Label(window, text="Name")
    itemNameLabel.grid(row=1, column=1, pady=(10,0))

    itemNameEntry= Entry(window, textvariable=addItemNameVar)
    itemNameEntry.grid(row=1, column=2, pady=(10,0))

    itemRateLabel= Label(window, text="Rate")
    itemRateLabel.grid(row=1, column=3, pady=(10,0))
    
    itemRateEntry= Entry(window, textvariable=addItemRateVar)
    itemRateEntry.grid(row=1, column=4, pady=(10,0))
    

    itemtypeLabel= Label(window, text="Type")
    itemtypeLabel.grid(row=2, column=1, pady=(10,0))
    itemTypeEntry= Entry(window, textvariable=addItemTypeVar)
    itemTypeEntry.grid(row=2, column=2, pady=(10,0))

    storeTypeLabel= Label(window, text="Stored Type")
    storeTypeLabel.grid(row=2, column=3, pady=(10,0))
    storeEntry= OptionMenu(window, addstoredVar,*storeOptions)
    storeEntry.grid(row=2, column=4, pady=(10,0))

    AddItemButton = Button(window, text="Add Item", width=20, height=2, command=lambda:addItem())
    AddItemButton.grid(row=3, column=3,pady=(10,0))

    
def updateItemWindow():
    backButton = Button(window, text="Back" , command=lambda:readAllData())
    backButton.grid(row=0, column=1)
    titleLabel = Label(window,text="P&E Billing System", width=40,font="Arial 30",fg="green")
    titleLabel.grid(row=0,column=2,columnspan=4,pady=(10,0))

    itemNameLabel= Label(window, text="Name")
    itemNameLabel.grid(row=1, column=1, pady=(10,0))

    itemNameEntry= Entry(window, textvariable=addItemNameVar)
    itemNameEntry.grid(row=1, column=2, pady=(10,0))

    itemRateLabel= Label(window, text="Rate")
    itemRateLabel.grid(row=1, column=3, pady=(10,0))
    
    itemRateEntry= Entry(window, textvariable=addItemRateVar)
    itemRateEntry.grid(row=1, column=4, pady=(10,0))
    

    itemtypeLabel= Label(window, text="Type")
    itemtypeLabel.grid(row=2, column=1, pady=(10,0))
    itemTypeEntry= Entry(window, textvariable=addItemTypeVar)
    itemTypeEntry.grid(row=2, column=2, pady=(10,0))

    storeTypeLabel= Label(window, text="Stored Type")
    storeTypeLabel.grid(row=2, column=3, pady=(10,0))
    storeEntry= OptionMenu(window, addstoredVar,*storeOptions)
    storeEntry.grid(row=2, column=4, pady=(10,0))

    AddItemButton = Button(window, text="Update Item", width=20, height=2, command=lambda:updateItem())
    AddItemButton.grid(row=3, column=3,pady=(10,0))

    updateTV.grid(row=4,column=0, columnspan=5)
    scrollBar = Scrollbar(window, orient="vertical",command=billsTV.yview)
    scrollBar.grid(row=4, column=4, sticky="NSE")

    updateTV.configure(yscrollcommand=scrollBar.set)

    updateTV.heading('#0',text="Item ID")
    updateTV.column('#0', minwidth=0, width=150)
    updateTV.heading('#1',text="Item Name")
    updateTV.column('#1', minwidth=0, width=170)
    updateTV.heading('#2',text="Rate")
    updateTV.column('#2', minwidth=0, width=150)
    updateTV.heading('#3',text="Type")
    updateTV.column('#3', minwidth=0, width=150)
    updateTV.heading('#4',text="Store Type")
    updateTV.column('#4', minwidth=0, width=150)
    getItemLists()
    
def viewAllBills():
    backButton = Button(window, text="Back" , command=lambda:readAllData())
    backButton.grid(row=0, column=1)
    titleLabel = Label(window,text="P&E Billing System", width=40,font="Arial 30",fg="green")
    titleLabel.grid(row=0,column=2,columnspan=4,pady=(10,0))
    billsTV.grid(row=1, column=0, columnspan=5)

    scrollBar = Scrollbar(window, orient="vertical",command=billsTV.yview)
    scrollBar.grid(row=1, column=4, sticky="NSE")

    billsTV.configure(yscrollcommand=scrollBar.set)

    billsTV.heading('#0',text="Item Name")
    billsTV.heading('#1',text="Rate")
    billsTV.heading('#2',text="Quantity")
    billsTV.heading('#3',text="Cost")

    updateBillsData()


loginWindow()
window.mainloop()
