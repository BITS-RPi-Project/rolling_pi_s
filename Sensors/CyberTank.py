
import RPi.GPIO as GPIO
import sqlite3
import datetime
import time

#initialise GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(20,GPIO.OUT)  #Trigger for Level Tx
GPIO.setup(21,GPIO.IN)   #Echo for Level Tx

GPIO.setup(9, GPIO.OUT)  #Level 0-20%
GPIO.setup(10, GPIO.OUT) #Level 20-40%
GPIO.setup(17, GPIO.OUT) #Level 40-60%
GPIO.setup(27, GPIO.OUT) #Level 60-80%
GPIO.setup(22, GPIO.OUT) #Level 80-100%

GPIO.setup(19, GPIO.OUT) #Running Indication
GPIO.setup(26, GPIO.OUT) #Heartbeat
GPIO.setup(13, GPIO.OUT) #Fault Light

#sensorVariable
sensorID = 1

#Change variance we want to record
changeVar = 1

#Frequency to update
secToUpdate = 10

cntr = 0

#connect to our DB
connection = sqlite3.connect('/home/pi/CyberTank/CyberTankDB')
cursor = connection.cursor()

print("CyberTank Running")
GPIO.output(9,True)
time.sleep(0.15)
GPIO.output(10,True)
time.sleep(0.15)
GPIO.output(17,True)
time.sleep(0.15)
GPIO.output(27,True)
time.sleep(0.15)
GPIO.output(22,True)
time.sleep(0.15)

GPIO.output(19,True) #Running Indication


#update DB with new level
def updateDB():
    Lvl_TRIGGER = 20    #Level Tx Trigger
    Lvl_ECHO    = 21    #Level Tx Echo
    #get previous level
    cursor.execute("SELECT level FROM tankLevel WHERE no = (SELECT MAX(no)  FROM tankLevel )")
    value  = cursor.fetchall()
    previousLevel = float(value[0][0])
    
    #setting variables
    i=0              
    Total=0
    
    GPIO.output(19,False) #Running Indication
    
    # will take i number of readings and average on the fly
    while i<5:
   # Set trigger to False (Low)
        GPIO.output(Lvl_TRIGGER, False)
        GPIO.output(26,True) #Heartbeat
    # Allow module to settle
        time.sleep(0.15)
        GPIO.output(26,False) #Heartbeat
        time.sleep(0.15)
    # Send 10us pulse to trigger
        GPIO.output(Lvl_TRIGGER, True)
    # Wait 10us
        time.sleep(0.00001)
        GPIO.output(Lvl_TRIGGER, False)
        
        WDT = 0    #watchdog timer
        stop = 0   #declaring stop
        
        while GPIO.input(Lvl_ECHO)==0:
          start = time.time()
          WDT += 1      #counting up watch dog timer
          if WDT ==1000:  #if count is high due to Lvl_ECHO not turning on, break
              print("Sensor Reading Fault")
              break
       
        while GPIO.input(Lvl_ECHO)==1:
          stop = time.time()
  
    # Calculate pulse length
        elapsed = stop-start
        
    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (m/s)
        speedSound = 331.12
        distance = elapsed * speedSound

    # That was the distance there and back so halve the value
        distance = distance / 2 
    #Tank Height in Meters
        TH = 2.15
    #Probe Height above water 100% level in m
        PH = 0.203
 

        TankLvlM = TH-(distance - PH) #calculating tank level in metres
       
        TnkLvl = round((TankLvlM/TH * 100),1) #calculating tank level in percent      
        
        #fault code to drive fault LED
        if WDT>999 or TnkLvl>105 or TnkLvl<0:
            GPIO.output(13,True)
            Fault = 1
        else:
            GPIO.output(13,False)
            Fault = 0
            
        if TnkLvl > 105:           #sets a max value of 105%
            TnkLvl = 105
        if TnkLvl < 0:             #sets a min value of 0%
           TnkLvl = 0
        
        #does a comparison of current level to previous level
        LvlCmp = round ((TnkLvl - previousLevel),1) 
        #this is so if a value is returned that is too great a change it limits that change
        #prevents excessive writing to database
        #if comparison is greater than 2, limit tank level to previous level
        if LvlCmp > 2:
            print("Reading " + str(i)+":"+"High Error: " + str(TnkLvl)) #print output for monitoring
            TnkLvl = previousLevel 
         
        #if comparison is less than 2, limit tank level to previous level  
        if LvlCmp < -2:
            print("Reading " + str(i)+":"+"Low Error: " + str(TnkLvl)) #print output for monitoring
            TnkLvl = previousLevel
            
       
        Total = round((Total + TnkLvl),1) #running total of tank level
        AvgLvl = round((Total/(i+1)),1)   #on the fly averaging of tank level
        currentLevel = round(TnkLvl,1) #rounding to 1 decimal place
        if i==4:
            
            print (":Total="+str(Total)+":AvgLvl="+str(AvgLvl)) #print output for monitoring
           
        i+=1    #increment i
        
    if Fault == 0:
        GPIO.output(19,True) #Running Indication   
    var = round((AvgLvl - previousLevel),3)
    print ("Previous Level: " + str(previousLevel) + " : Variance:" + str(var))
        
    if (var > changeVar or var < (changeVar * -1)):
        cursor.execute("INSERT INTO tankLevel(sensorID,level, datetime) values ("+str(sensorID)+ "," + str(AvgLvl) + ", datetime('now','localtime'))")
        connection.commit()
        #only print when writing to DB
        DateStamp = datetime.datetime.now()
        print(DateStamp) #print output for monitoring
        print('Recording New Level: ' + str(AvgLvl) + '%') #print output for monitoring
        
    print("") #just to add space between readings
    
    
def updateLights():
     #get current level 
    cursor.execute("SELECT level FROM tankLevel WHERE no = (SELECT MAX(no)  FROM tankLevel )")
    value  = cursor.fetchall()
    level = int(value[0][0])
                                                                                                                                        
    #turn lights on according to level
    if level >= 80:
        GPIO.output(10,True)
        GPIO.output(17,True)
        GPIO.output(27,True)
        GPIO.output(22,True)
        GPIO.output(9,True)

    elif level >= 60:
        GPIO.output(10,True)
        GPIO.output(17,True)
        GPIO.output(27,True)
        GPIO.output(22,False)
        GPIO.output(9,True)


    elif level >= 40:
        GPIO.output(10,True)
        GPIO.output(17,True)
        GPIO.output(27,False)
        GPIO.output(22,False)
        GPIO.output(9,True)

    elif level >= 20:
        GPIO.output(10,True)
        GPIO.output(17,False)
        GPIO.output(27,False)
        GPIO.output(22,False)
        GPIO.output(9,True)
        
    elif level >= 10:
        GPIO.output(10,False)
        GPIO.output(17,False)
        GPIO.output(27,False)
        GPIO.output(22,False)
        GPIO.output(9,True)

    else:
        GPIO.output(10,False)
        GPIO.output(17,False)
        GPIO.output(27,False)
        GPIO.output(22,False)
        
        #loop for flashinglight
        for x in range(secToUpdate):
            GPIO.output(9,False)
            time.sleep(0.5)
            GPIO.output(9,True)
            time.sleep(0.5)         
                    
        #we dont want to wait another period so we will call the funtions here
        updateDB()
        updateLights()
 
while True:
    
    cntr += 1
    print (str(cntr))
    
    updateDB()
    updateLights()
    time.sleep(secToUpdate)
    