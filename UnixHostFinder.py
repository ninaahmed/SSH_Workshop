from bs4 import BeautifulSoup
import urllib.request
from subprocess import call
import sys
import ssl

# Check that username was included in command line
if(len(sys.argv) < 2):
	print(f"Usage: python3 {sys.argv[0]} <CS username>")
	sys.exit(1)

# Use the username from the command line argument
username = str(sys.argv[1])

# URL for UTCS site with list of all Unix hosts available
url = 'https://apps.cs.utexas.edu/unixlabstatus/'

try:
	# Create an SSL context to connect to UTCS's site
	context = ssl._create_unverified_context()
	# Read in website as a string
	site = urllib.request.urlopen(url, context=context).read()
except:
	print("Could not connect to UTCS Unix hosts site")
	sys.exit(1)

#Create Web Scraper instance
soup = BeautifulSoup(site, 'html.parser')

#Create a list of all the hosts on the site
hosts = []

# Loop through all hosts on website
for host in soup.find_all('tr'):
	#Get the text for this item
	text = host.get_text()	
	#Split up text into an array of lines
	lines = text.splitlines();	

	# Valid hosts take up 6 lines
	if len(lines) == 6:
		#Get the name of the host 
		name = lines[1] 	
		# Can be either 'up' or 'down'
		status = lines[2]	
		# Make sure this isn't the table header and that the host is 'up'
		if name != 'Host' and status == 'up':	
			load = float(lines[5])
			users = int(float(lines[4]))
			hosts.append((name, users, load))

# See if we updated the default value and found a host
if len(hosts) > 0:	
	hosts.sort(key=lambda tup: (tup[1], tup[2]))
	#print('Best Host Found = ' + currMinHost)
	#print('Num Users = ' + str(currMinUsers))
	
	# Alternative implementation: Opens a new 'Terminal' window with ssh command
	#appscript.app('Terminal').do_script('ssh slaberge@' + currMinHost + '.cs.utexas.edu')

	NUM_ATTEMPTS = 10
	for i in range(0, min(len(hosts), NUM_ATTEMPTS)):
		hostname = hosts[i][0]
		try:
			call(['ssh', username + '@' + hostname + '.cs.utexas.edu'])
			sys.exit(0)
		except Exception as e:
			print(e)
			print(f"Connection to {hostname} failed.")
			print(f"Trying {hosts[i+1]} instead")
	sys.exit(-1)	
	# Run ssh command in this terminal window
	'''
	try:
		call(['ssh', username + '@' + currMinHost + '.cs.utexas.edu'])
		sys.exit(0);
	except:
		for i in range(2, 5):
			try:
				print(f"Connection failed. Retrying, attempt {i}")
				call(['ssh', username + '@' + currMinHost + '.cs.utexas.edu'])
				sys.exit(0);
			except:
				pass
	try:
		call(['ssh', username + '@aida.cs.utexas.edu'])
		sys.exit(0);
	except:
		print("All attempts failed, exiting.")
		sys.exit(-1);
	'''
else:
	print('No suitable host could be found.')
