import RPi.GPIO as GPIO    
import time      
from time import sleep
import mfrc522
import socket
from mfrc522 import SimpleMFRC522
from queue import PriorityQueue

GPIO.setwarnings(False)


HOST='192.168.2.2'
PORT=9090
socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST,PORT))

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

p.start(99.93) #99.93 49.965
pb.start(95) #95 47.5

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
   p.ChangeDutyCycle(99.93)
   pb.ChangeDutyCycle(95)
   time.sleep(1)
   GPIO.output(in1,GPIO.HIGH)
   GPIO.output(in2,GPIO.LOW)
   GPIO.output(in3,GPIO.LOW)
   GPIO.output(in4,GPIO.HIGH)
   while t:
        time.sleep(0.18) # czas obrotu dobrany do wyniku kalibracji kierunku jazdy
        t -= 1
   GPIO.output(in1,GPIO.LOW)
   GPIO.output(in2,GPIO.LOW)
   GPIO.output(in3,GPIO.LOW)
   GPIO.output(in4,GPIO.LOW)
   time.sleep(1)
   # czesc odpowiadajaca za zmiane w tablicy kierunku
   global b
   global kierunek
   b -= 1
   if b<0:
	   b = 3
   kierunek = m_obrot[b]
         
def RotateRight(t):
   p.ChangeDutyCycle(99.93)
   pb.ChangeDutyCycle(95)
   time.sleep(1)
   GPIO.output(in1,GPIO.LOW)
   GPIO.output(in2,GPIO.HIGH)
   GPIO.output(in3,GPIO.HIGH)
   GPIO.output(in4,GPIO.LOW)
   while t:
        time.sleep(0.18) # 0.12675 0.1575 czas obrotu dobrany do wyniku kalibracji kierunku jazdy
        t -= 1
   GPIO.output(in1,GPIO.LOW)
   GPIO.output(in2,GPIO.LOW)
   GPIO.output(in3,GPIO.LOW)
   GPIO.output(in4,GPIO.LOW)
   time.sleep(1)
   # czesc odpowiadajaca za zmiane w tablicy kierunku
   global b 
   
   global kierunek
   b += 1
   if b>3:
	   b = 0
   print(b)
   kierunek = m_obrot[b]
   

m_obrot = ['right','down','left','up'] #tablica obrotu
b = 0
kierunek = m_obrot[b] #domyślny zwrot robota


#zmiana aktualnej strefy po najechaniu na nową kartę

def ZoneCheck(current_zone):
	new_zone = Read()	
	if  new_zone != current_zone:
		print('Change of zone')
		return new_zone

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
    return 404 
    
# funkcja pozwalająca na przejazd pojedyńczą trasą do sąsiadującej strefy
def follow_route(start_zone, target_zone):
	
	target_direction_index = find_target_index(start_zone, target_zone)
	#print(target_direction_index)
	if target_direction_index != 404:
		while b != target_direction_index:
			if b-1==target_direction_index or b-target_direction_index==-3:
			   print(b)	
			   RotateLeft(5)
			else:
			   print(b)
			   RotateRight(5)
			
		p.ChangeDutyCycle(65)
		pb.ChangeDutyCycle(61.75)	
		Forward() 
	else:
		print('Error follow route')
		Stop()
		time.sleep(10)
	

def heuristic(a, b):
    ax, ay = int(a[1:]), int(a[1:])
    bx, by = int(b[1:]), int(b[1:])
    return abs(ax - bx) + abs(ay - by)
    
def astar(start, goal):
    open_set = PriorityQueue()
    open_set.put((0, start))

    came_from = {}
    g_score = {node: float('inf') for node in zone_connections}
    g_score[start] = 0

    while not open_set.empty():
        current_cost, current_node = open_set.get()

        if current_node == goal:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            return path[::-1]

        for index, neighbor in enumerate(zone_connections[current_node]):
            if neighbor:
                tentative_g_score = g_score[current_node] + 1 
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    open_set.put((f_score, neighbor))

    return None  




start_zone = 'S5'
final_zone = 'S5'
    
# program głowny
while True:
	
	
	while start_zone==final_zone:
	   final_zone=f'S{socket.recv(1024).decode("utf8")}'  
	   print(final_zone)

	print(final_zone)
	node_number = 0
	new_zone = 0
	current_zone=''

	path = astar(start_zone, final_zone)
	if path:
	   print(f"Shortest path from {start_zone} to {final_zone}: {path}")
	else:
		
	   print(f"Path from {start_zone} to {final_zone} not found")
       
# Powiększenie tablicy scieżki robota ma na celu upewnienie go o istnieniu punktu docelowego	  
	path.append('Final') 


	while new_zone != final_zone:
		
		new_zone = ZoneCheck(current_zone)
		target_zone = path[node_number]
		if new_zone: 
			print('przybyto do strefy: ', new_zone) 
			Stop()
			time.sleep(2)
			socket.send(new_zone.encode('utf8'))
			print('executing follow_route: ',new_zone,' ',target_zone)
			follow_route(new_zone,target_zone)
				
			current_zone=new_zone
			

			node_number +=1
			
		else:
			print('cosjest')



	print('przybyto na miejsce docelowe')	
	start_zone=final_zone




	

	

		
	
		










    

