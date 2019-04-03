import csv 
from urllib.request import Request, urlopen 
from bs4 import BeautifulSoup
import time

def scrapeLink(url):
	print("Searching for company...", end=" ")

	url = url.encode('ascii',errors='ignore')
	url = url.decode('ascii',errors='ignore')

	req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5);'})
	searchPage = urlopen(req).read()
	searchObj = BeautifulSoup(searchPage, "html.parser") 

	#div = searchObj.findAll("div",{"class":"company_browse"})
	table = searchObj.findAll("tbody")[0]
	data = table.findAll("td")

	# if result is not found
	if len(data) == 0:
		print("No result.")
		return {"name":" ", "url": " "}
	else:
		return {"name": data[0].get_text(), "url": "http://www.hoovers.com" + data[0].a['href']}


csvSource = open('/Users/Jiajun/Desktop/csvSource.csv', 'r')
reader = csv.reader(csvSource)
companyList = list(reader)
csvSource.close()

csvOutput = open('/Users/Jiajun/Desktop/csvOutput.csv', 'wt')
writer = csv.writer(csvOutput)

num = 1

for companylink in companyList[481:600]:
	# stall scraping for awhile
	time.sleep(6)

	print(num)
	
	#scrape
	com = scrapeLink(companylink[6])
	row = [com['name'], com['url']]

	# write data to file
	csvOutput = open('/Users/Jiajun/Desktop/csvOutput.csv', 'a')
	writer = csv.writer(csvOutput)
	try:
		writer.writerow(row)
	finally:
		csvOutput.close()

	num += 1



# #The main comparison table is currently the first table on the page 
# table = bsObj.findAll("table",{"class":"wikitable"})[0] 
# rows = table.findAll("tr")

# csvFile = open("../files/editors.csv", 'wt') 
# writer = csv.writer(csvFile)

# try:
# 	for row in rows: 
# 		csvRow = [] 
# 		for cell in row.findAll(['td', 'th']): 
# 			csvRow.append(cell.get_text()) 
# 			writer.writerow(csvRow) 
# 		finally: csvFile.close()
