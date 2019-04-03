import csv 
from urllib.request import urlopen 
from bs4 import BeautifulSoup
import re

startYear = 2011
endYear = 2015

def monthToNum(month):
	if month == "JANUARY":
		return 1
	if month == "FEBRUARY":
		return 2
	if month == "MARCH":
		return 3
	if month == "APRIL":
		return 4
	if month == "MAY":
		return 5
	if month == "JUNE":
		return 6
	if month == "JULY":
		return 7
	if month == "AUGUST":
		return 8
	if month == "SEPTEMBER":
		return 9
	if month == "OCTOBER":
		return 10
	if month == "NOVEMBER":
		return 11
	if month == "DECEMBER":
		return 12
	return month

def cellsToArray7(cells, monthCell, dayCell):
	csvRow = []

	if len(cells) is 7:
		monthCell = monthToNum(cells[0].get_text().replace('\n',""))
		dayCell = cells[1].get_text()
		csvRow.append(year)
	if len(cells) is 6:
		dayCell = cells[0].get_text()
		csvRow.append(year)
		csvRow.append(monthCell)
	if len(cells) is 5:
		csvRow.append(year)
		csvRow.append(monthCell)
		csvRow.append(dayCell)

	for cell in cells:
		formattedRow = monthToNum(cell.get_text().replace('\n',""))
		csvRow.append(formattedRow)

	return {"csvRow": csvRow, "monthCell": monthCell, "dayCell": dayCell}

def cellsToArray8(cells, monthCell, dayCell):
	csvRow = []

	if len(cells) is 9:
		monthCell = monthToNum(cells[0].get_text().replace('\n',""))
		dayCell = cells[1].get_text()
		csvRow.append(year)
		csvRow.append(monthCell)
		csvRow.append(dayCell)
		csvRow.append(cells[3].get_text())
		csvRow.append(cells[4].get_text())
		csvRow.append(cells[5].get_text())
		csvRow.append(cells[6].get_text()+", "+cells[7].get_text())
	if len(cells) is 8:
		dayCell = cells[0].get_text()
		csvRow.append(year)
		csvRow.append(monthCell)
		csvRow.append(dayCell)
		csvRow.append(cells[2].get_text())
		csvRow.append(cells[3].get_text())
		csvRow.append(cells[4].get_text())
		csvRow.append(cells[5].get_text()+", "+cells[6].get_text())
	if len(cells) is 7:
		csvRow.append(year)
		csvRow.append(monthCell)
		csvRow.append(dayCell)
		csvRow.append(cells[1].get_text())
		csvRow.append(cells[2].get_text())
		csvRow.append(cells[3].get_text())
		csvRow.append(cells[4].get_text()+", "+cells[5].get_text())
	if len(cells) is 6:
		csvRow.append(year)
		csvRow.append(monthCell)
		csvRow.append(dayCell)
		csvRow.append(cells[0].get_text())
		csvRow.append(cells[1].get_text())
		csvRow.append(cells[2].get_text())
		csvRow.append(cells[3].get_text()+", "+cells[4].get_text())

	return {"csvRow": csvRow, "monthCell": monthCell, "dayCell": dayCell}

years = list(range(startYear,endYear+1))

csvFile = open("./film2.csv", 'wt') 
writer = csv.writer(csvFile)

for year in years:
	print("Starting year "+str(year)+"...")
	html = urlopen("https://en.wikipedia.org/wiki/"+str(year)+"_in_film") 
	bsObj = BeautifulSoup(html, "html.parser") 
	#The main comparison table is currently the first table on the page 
	tables = []
	table = bsObj.find("span",{"id":re.compile("[0-9][0-9][0-9][0-9]_films")}).parent.findNext("table",{"class":"wikitable"})
	while table is not None:
		tables.append(table)
		table = table.findNext("table",{"class":"wikitable"})

	allrows =[]
	for table in tables:
		rows = table.findAll("tr")
		for row in rows:
			allrows.append(row)

	monthCell = ""
	dayCell = ""
	for row in allrows:
		cells = row.findAll(['td', 'th'])
		
		csvRow = []
		if year == 2012:
			returnedTuple = cellsToArray8(cells, monthCell, dayCell)
			csvRow = returnedTuple["csvRow"]
			monthCell = returnedTuple["monthCell"]
			dayCell = returnedTuple["dayCell"]
		else:
			returnedTuple = cellsToArray7(cells, monthCell, dayCell)
			csvRow = returnedTuple["csvRow"]
			monthCell = returnedTuple["monthCell"]
			dayCell = returnedTuple["dayCell"]

		if len(csvRow) >= 2:
			if csvRow[2] == 'Opening':
				if year is years[0] and row is allrows[0]:
					csvRow[0]=""
					try:
						writer.writerow(csvRow) 
					except: 
						csvFile.close()
			else:
				try:
					writer.writerow(csvRow)
				except:
					csvFile.close()	
print("Done.")
csvFile.close()