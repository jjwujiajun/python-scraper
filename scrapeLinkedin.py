import pymysql
from urllib.request import Request, urlopen 
from bs4 import BeautifulSoup
import re
from datetime import datetime

### MySQL functions ###
def createProfile(webAddr, firstName, lastName=""):
	cur.execute("SELECT * FROM profile WHERE webAddr=\"%s\"" % (webAddr))
	result = cur.fetchone()
	if result is None:
		cur.execute("INSERT INTO profile (webAddr, firstName, lastName) VALUES (\"%s\",\"%s\",\"%s\")" % (webAddr, firstName, lastName))
		cur.connection.commit()
		cur.execute("SELECT * FROM profile WHERE firstName=\"%s\" AND lastName=\"%s\"" % (firstName,lastName))
		result = cur.fetchone()
	return result[0]

def createEducation(college, course=""):
	cur.execute("SELECT * FROM education WHERE college=\"%s\" AND course=\"%s\"" % (college, course))
	result = cur.fetchone()
	if result is None:
		cur.execute("INSERT INTO education (college, course) VALUES (\"%s\",\"%s\")" % (college, course))
		cur.connection.commit()
		cur.execute("SELECT * FROM education WHERE college=\"%s\" AND course=\"%s\"" % (college, course))
		result = cur.fetchone()
	return result[0]

def createJob(title, company, sector="", location=""): 
	cur.execute("SELECT * FROM job WHERE title=\"%s\" AND company=\"%s\"" % (title, company))
	result = cur.fetchone()
	if result is None:
		cur.execute("INSERT INTO job (title, company, sector, location) VALUES (\"%s\",\"%s\",\"%s\",\"%s\")" % (title, company, sector, location))
		cur.connection.commit()
		cur.execute("SELECT * FROM job WHERE title=\"%s\" AND company=\"%s\"" % (title, company))
		result = cur.fetchone()
	return result[0]

def assignEducationToProfile(education_ID, profile_ID, startDate, endDate):
	cur.execute("SELECT * FROM profile_education WHERE (profile_ID=%i AND education_ID=%i) OR (education_ID=%i AND profile_ID=%i)" % (profile_ID, education_ID, education_ID, profile_ID))
	result = cur.fetchone()
	if result is None:
		if endDate == "NULL":
			query = "INSERT INTO profile_education (profile_ID, education_ID, startDate) VALUES (%i, %i, \"%s\")" % (profile_ID, education_ID, startDate.strftime("%Y-%m-%d"))
		else:
			query = "INSERT INTO profile_education (profile_ID, education_ID, startDate, endDate) VALUES (%i, %i, \"%s\", \"%s\")" % (profile_ID, education_ID, startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"))

		cur.execute(query)
		cur.connection.commit()

def assignJobToProfile(job_ID, profile_ID, startDate, endDate):
	# For date format: https://dev.mysql.com/doc/refman/5.5/en/date-and-time-literals.html

	cur.execute("SELECT * FROM profile_job WHERE (profile_ID=%i AND job_ID=%i) OR (job_ID=%i AND profile_ID=%i)" % (profile_ID, job_ID, job_ID, profile_ID))
	result = cur.fetchone()

	if result is None:
		if endDate == 'NULL':
			query = "INSERT INTO profile_job (profile_ID, job_ID, startDate) VALUES (%i, %i, \"%s\");" % (profile_ID, job_ID, startDate.strftime("%Y-%m-%d"))
		else:
			query = "INSERT INTO profile_job (profile_ID, job_ID, startDate, endDate) VALUES (%i, %i, \"%s\"), \"%s\")" % (profile_ID, job_ID, startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"))

		cur.execute(query)
		cur.connection.commit()

def createConnection(profile_ID1, profile_ID2):
	cur.execute("SELECT * FROM connection WHERE (profile_ID1=\"%i\" AND profile_ID2=\"%i\") OR (profile_ID1=\"%i\" AND profile_ID2=\"%i\")" % (profile_ID1, profile_ID2, profile_ID2, profile_ID1))
	result = cur.fetchone()
	if result is None:
		cur.execute("INSERT INTO connection (profile_ID1, profile_ID2) VALUES (\"%i\",\"%i\")" % (profile_ID1, profile_ID2))
		cur.connection.commit()

### helper functions ###
def _decodeDateString(dateString):
	date=""
	try:
		date = datetime.strptime(dateString, '%B %Y')
	except ValueError:
		date = datetime.strptime(dateString, '%Y')
	return date

# TODO: if only year, like 2004 - 2008, end date should be 081231. not 080101	
def convertStringToDates(dateString):
	if dateString is None:
		return {"startDate": "NULL", "endDate": "NULL"}
	else:
		dateStrings = dateString.split("–")
		startDate = _decodeDateString(dateStrings[0].lstrip().rstrip())
		endDate = "NULL"
		if "Present" not in dateStrings[1]:
			endDate = _decodeDateString(dateStrings[1].lstrip().rstrip())
		
		return {"startDate": startDate, "endDate": endDate}

### procedurial functions ###
def scrapeProfilePage(profileObj):

	#profile
	nameObj = profileObj.find("h1", {"id": "name"})
	profile_ID = createProfile(url, nameObj.get_text().lstrip())

	#job
	jobObj = profileObj.find("section", {"id": "experience"})
	if jobObj is not None:
		# items to scrape from each work section
		# TODO: get industry
		jobObj = jobObj.find("li")
		jobTitleObj = jobObj.find("h4", {"class": "item-title"})
		jobCompanyObj = jobObj.find("h5", {"class": "item-subtitle"})
		jobLocationObj = jobObj.find("span", {"class": "location"})
		jobDateObj = jobObj.find("span", {"class": "date-range"})
		jobDates = convertStringToDates(jobDateObj.get_text())

		# scrape descriptor from main section or from company's page.
		# 1. scape from main section
		jobDescriptor = profileObj.find("div", {"class": "profile-overview-content"}).findAll("dd", {"class": "descriptor"})[1]

		if jobDescriptor is None:
			jobDescriptor = ""
		
		job_ID = createJob(jobTitleObj.get_text().lstrip(), jobCompanyObj.get_text().lstrip(), jobDescriptor.get_text().lstrip())
		assignJobToProfile(job_ID, profile_ID, jobDates['startDate'], jobDates['endDate'])


	#education
	eduObj = profileObj.find("section", {"id": "education"})
	if eduObj is not None:
		eduObj = eduObj.find("li")
		eduUniObj = eduObj.find("h4", {"class": "item-title"})
		eduQualificationObj = eduObj.find("h5", {"class": "item-subtitle"})
		eduDateObj = eduObj.find("span", {"class": "date-range"})
		eduDates = convertStringToDates(eduDateObj.get_text())

		education_ID = createEducation(eduUniObj.get_text().lstrip(), eduQualificationObj.get_text().lstrip())
		assignEducationToProfile(education_ID, profile_ID, eduDates['startDate'], eduDates['endDate'])


conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd='84823284', db='mysql', charset='utf8')
cur = conn.cursor()
cur.execute("USE linkedIn")

name = "steveleonardsingapore"

try:
	url = "https://www.linkedin.com/in/" + name

	# Scrape from website
	# linkedInProfileReq = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5);'})
	# profile_HTML = urlopen(linkedInProfileReq).read()

	# Save to sample
	# with open('sampleLinkedInData.txt', 'w') as sampleFile:
	# 	linkedInProfileReq = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5);'})
	# 	profile_HTML = urlopen(linkedInProfileReq).read()
	# 	sampleFile.write(str(profile_HTML))		

	# Scrape from sample
	with open('sampleLinkedInData '+name+'.txt', 'r') as sampleFile:
		profile_HTML = str.encode(sampleFile.read())

	profileObj = BeautifulSoup(profile_HTML, "html.parser") 

	scrapeProfilePage(profileObj)

finally:
	cur.close()
	conn.close()