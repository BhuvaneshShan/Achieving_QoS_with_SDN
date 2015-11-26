from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

PORT_NUMBER = 8080
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET request
	def do_GET(self):
		self.send_header('Content-type','text/html')
		self.end_headers()
		x = reserve_queue()
		if x:
			self.send_response(200)
			self.wfile.write("OK")
		else:
			self.send_response(400)
			self.wfile.write("Unable to Reserve")
		return

#initialize matrices
reservematrix = [[ "Free" for x in range(3)] for x in range(2)] 
matrix = [[ 0 for x in range(3)] for x in range(2)] 


def _reserve_queue():
clientbandwidth = math.ceil(clientbandwidth)
availmatrix = [[ 0 for x in range(3)] for x in range(2)] 
if s1 to s2:
	availmatrix = matrix
else:
	#s2 to s1
	#switching rows in the matrix
	for i in range(0,3):
		availmatrix[0][i] = matrix[1][i]
		availmatrix[1][i] = matrix[0][i]

if clientbandwidth <=1:
	#checking first row
	if availmatrix[0][0] >= 1:
		availmatrix[0][0] -= 1
		reserveavailmatrix[0][0]= "Reserved"
		#need to enqueue on queue 1
	elif availmatrix[0][1] >=1:
		availmatrix[0][1] -= 1
		reserveavailmatrix[0][1]= "Partially Reserved"
		#need to enqueue on queue 2
	elif availmatrix[0][2] >=1:
		availmatrix[0][2] -= 1
		reserveavailmatrix[0][2]= "Partially Reserved"
		#need to enqueue on queue 3
	else:
		#cannot accomodate
		return 0
	#checking second row
	if availmatrix[1][0] >=1:
		availmatrix[1][0] -= 1
		reserveavailmatrix[1][0]= "Reserved"
		#need to enqueue on queue 1
	elif availmatrix[1][1] >=1:
		availmatrix[1][1] -= 1
		reserveavailmatrix[1][1]= "Partially Reserved"
		#need to enqueue on queue 2
	elif availmatrix[1][2] >= 1:
		availmatrix[1][2] -=1
		reserveavailmatrix[1][2]= "Partially Reserved"
		#need to enqueue on queue 3
	else:
		#cannot accomodate
		return 0
elif clientbandwidth <=5:
	#checking first row
	if availmatrix[0][1] >= clientbandwidth:
		availmatrix[0][1] -= clientbandwidth
		reserveavailmatrix[0][1]= "Partially Reserved"
		#need to enqueue on queue 2
	elif availmatrix[0][2] >= clientbandwidth:
		availmatrix[0][2] -= clientbandwidth
		reserveavailmatrix[0][2]= "Partially Reserved"
		#need to enqueue on queue 3
	else:
		#cannot accomodate
		return 0
	#checking second row
	if availmatrix[1][1] >= clientbandwidth:
		availmatrix[1][1] -= clientbandwidth
		reserveavailmatrix[1][1]= "Partially Reserved"
		#need to enqueue on queue 2
	elif availmatrix[1][2] >= clientbandwidth:
		availmatrix[1][2] -= clientbandwidth
		reserveavailmatrix[1][2]= "Partially Reserved"
		#need to enqueue on queue 3
	else:
		#cannot accomodate
		return 0
elif clientbandwidth <=10:
	#checking first row
	if availmatrix[0][2] >= clientbandwidth:
		availmatrix[0][2] -= clientbandwidth
		reserveavailmatrix[0][2]= "Partially Reserved"
		#need to enqueue on queue 3
	else:
		#cannot accomodate
		return 0
	#checking second row
	if availmatrix[1][2] >= clientbandwidth:
		availmatrix[1][2] -= clientbandwidth
		reserveavailmatrix[1][2]= "Partially Reserved"
		#need to enqueue on queue 3
	else:
		#cannot accomodate
		return 0
else:
	#cannot accomodate
	return 0
#enabling reservation only for some duration
Timer(timeofreservation, _reset_matrix, recurring=True)

def _reset_matrix():
	#free up state of reservation
	reservematrix = [[ "Free" for x in range(3)] for x in range(2)] 
	#free up available bandwidth	
	for i in range(0,2):
		for j in range(0,3):
			if j == 0:
				matrix[i][j] = 1
			elif j == 1:
				matrix[i][j] = 5
			else:
				matrix[i][j] = 10








