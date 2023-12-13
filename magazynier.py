import RPi.GPIO as GPIO    
import time      
from time import sleep
import mfrc522
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)

in1 = 18
in2 = 16
en = 11
in3 = 36
in4 = 38
enb = 40

reader = SimpleMFRC522()


GPIO.setmode(GPIO.BOARD)

GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)

GPIO.setup(in3,GPIO.OUT)
GPIO.setup(in4,GPIO.OUT)
GPIO.setup(enb,GPIO.OUT)

GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)

GPIO.output(in3,GPIO.LOW)
GPIO.output(in4,GPIO.LOW)

p=GPIO.PWM(en,1000)
pb=GPIO.PWM(enb,1000)

p.start(99.93)
pb.start(95)

def Forward():
   GPIO.output(in1,GPIO.HIGH)
   GPIO.output(in2,GPIO.LOW)
   GPIO.output(in3,GPIO.HIGH)
   GPIO.output(in4,GPIO.LOW)
   
def ForwardTimed(t):
   GPIO.output(in1,GPIO.HIGH)
   GPIO.output(in2,GPIO.LOW)
   GPIO.output(in3,GPIO.HIGH)
   GPIO.output(in4,GPIO.LOW)
   while t:
         time.sleep(1)
         t -= 1
   if t==0:
         GPIO.output(in1,GPIO.LOW)
         GPIO.output(in2,GPIO.LOW)
         GPIO.output(in3,GPIO.LOW)
         GPIO.output(in4,GPIO.LOW)
   
def Stop():
   GPIO.output(in1,GPIO.LOW)
   GPIO.output(in2,GPIO.LOW)
   GPIO.output(in3,GPIO.LOW)
   GPIO.output(in4,GPIO.LOW)
    
def Read():
	try:
		id, text = reader.read()
		if text.strip():
			return text.strip()
		else:
			return False
	except:
		print('wait')
		
def RotateLeft(t):
   GPIO.output(in1,GPIO.HIGH)
   GPIO.output(in2,GPIO.LOW)
   GPIO.output(in3,GPIO.LOW)
   GPIO.output(in4,GPIO.HIGH)
   while t:
        time.sleep(0.12675) # czas obrotu dobrany do wyniku kalibracji kierunku jazdy
        t -= 1
   GPIO.output(in1,GPIO.LOW)
   GPIO.output(in2,GPIO.LOW)
   GPIO.output(in3,GPIO.LOW)
   GPIO.output(in4,GPIO.LOW)
   # czesc odpowiadajaca za zmiane w tablicy kierunku
   global b
   global kierunek
   b -= 1
   if b<0:
	   b = 3
   kierunek = m_obrot[b]
         
def RotateRight(t):
   GPIO.output(in1,GPIO.LOW)
   GPIO.output(in2,GPIO.HIGH)
   GPIO.output(in3,GPIO.HIGH)
   GPIO.output(in4,GPIO.LOW)
   while t:
        time.sleep(0.12675) # czas obrotu dobrany do wyniku kalibracji kierunku jazdy
        t -= 1
   GPIO.output(in1,GPIO.LOW)
   GPIO.output(in2,GPIO.LOW)
   GPIO.output(in3,GPIO.LOW)
   GPIO.output(in4,GPIO.LOW)
   # czesc odpowiadajaca za zmiane w tablicy kierunku
   global b 
   global kierunek
   b += 1
   if b>3:
	   b = 0
   kierunek = m_obrot[b]
   
def align(target): # funkcja ustawiająca robota w danym kierunku
	global kierunek
	#print(kierunek)
	while target != kierunek:
		RotateRight(5)
		#print(kierunek)
		

   

# test funkcji ruchowych
"""
Forward()
time.sleep(3)		
RotateLeft(5)
RotateRight(5)
GPIO.cleanup()
"""

# empiryczny test kalibracji kierunku jazdy
"""
p.ChangeDutyCycle(99.93)
pb.ChangeDutyCycle(95)
ForwardTimed(2)
#RotateRight(5)
#RotateLeft(5)
"""

m_obrot = ['right','down','left','up'] #tablica obrotu
b = 0
kierunek = m_obrot[b] #domyślny zwrot robota

# test tablicy obrotu
"""
print(kierunek)
RotateRight(5)
print(kierunek)
time.sleep(2)
RotateRight(5)
print(kierunek)
time.sleep(2)
RotateRight(5)
print(kierunek)
"""


current_zone = Read()
LastZone=''
#OnCard = False
#Sprawdzanie czy robot jest aktualnie na karcie, nie działa bo reader.read() czeka na input
"""
def CardCheck():
	try:
		if Read():
			OnCard = True
			print(OnCard)
		else:
			OnCard = False
			print(OnCard)
	except:
		print('ERROR')
	time.sleep(0.01)
"""	
#zmiana aktualnej strefy po najechaniu na nową kartę

def ZoneCheck(current_zone):
	new_zone = Read()	
	if  new_zone != current_zone:
		print('Change of zone')
		return new_zone

#test działania ustalonej wcześniej sciezki	
"""	
while True:
	
	new_zone = ZoneCheck(current_zone)

	if new_zone:
		
		if new_zone =='S20':
			Forward()
		
		elif new_zone == 'S19':
			RotateRight(5)
			Forward()
		
		elif new_zone == 'S18':
			RotateLeft(5)
			Forward()
		elif new_zone == 'S1':
			GPIO.cleanup()
			
		current_zone=new_zone
		time.sleep(1)
		
	else:
		Forward()
"""
# tablica zawierająca wszystkie połączenia 
# indeks oznacza kierunek do docelowej strefy
# 0-prawo 1-dol 2-lewo 3-gora
zone_connections = { 
    'S1': ['S2','S5','',''],        
    'S2': ['S3','S6','S1',''], 
    'S3': ['S4','S7','S2',''], 
    'S4': ['','S8','S3',''], 
    'S5': ['S6','S9','','S1'], 
    'S6': ['S7','S10','S5','S2'], 
    'S7': ['S8','S11','S6','S3'], 
    'S8': ['','S12','S7','S4'], 
    'S9': ['S10','S13','','S5'], 
    'S10': ['S11','S14','S9','S6'], 
    'S11': ['S12','S15','S10','S7'], 
    'S12': ['','S16','S11','S8'], 
    'S13': ['S14','S17','','S9'], 
    'S14': ['S15','S18','S13','S10'], 
    'S15': ['S16','S19','S14','S11'], 
    'S16': ['','S20','S15','S12'], 
    'S17': ['S18','','','S13'], 
    'S18': ['S19','','S17','S14'], 
    'S19': ['S20','','S18','S15'], 
    'S20': ['','','S19','S16'] 
}

# funkcja wyszukująca w jakim kierunku nalezy jechac 
# aby dostac sie z obszaru start do target
def find_target_index(start_zone, target_zone): 
    if start_zone in zone_connections:
        connections = zone_connections[start_zone]
        if target_zone in connections:
            index = connections.index(target_zone)
            return index
    return None 
    
#print(find_target_index('S16','S12'))



# funkcja pozwalająca na przejazd pojedyńczą trasą do sąsiadującej strefy
def follow_route(start_zone, target_zone):
	
	target_direction_index = find_target_index(start_zone, target_zone)
	if target_direction_index:
		while b != target_direction_index:
			RotateRight(5)
		ForwardTimed(1) # do zmiany?
	else:
		print('Error')
	
#follow_route('S10','S6')

# program głowny, teraz trzeba zrobić zeby target zone było sąsiadujące, 
# i aktualizowało się w miarę pokonywania trasy
while new_zone != final_zone:
	
	new_zone = ZoneCheck(current_zone)

	if new_zone:
		
		follow_route(new_zone,target_zone)
			
		current_zone=new_zone
		time.sleep(1)
		
	else:
		Forward()

	
	





	

	

		
	
		










    

