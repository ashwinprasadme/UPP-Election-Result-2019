import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import csv
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style

# print(writer.dumps())

def readStateInfo(filepath):
    _info = []
    with open(filepath, 'r') as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            # print(dict(row))
            _info.append(row)
    csvFile.close()
    return _info


def getResultConstituency(constituency, party, state="S16", candidate=None):
    # http://eciresults.nic.in/ConstituencywiseS1610.htm?ac=10
    resultUrl = "http://eciresults.nic.in/Constituencywise{0}{1}.htm?ac={1}"
    # print(resultUrl.format(state, constituency))
    response = requests.get(resultUrl.format(state, constituency))

    # print(response)
    soup = BeautifulSoup(response.text, "html.parser")
    votes_table = soup.find('table', {"style": "margin: auto; width: 100%; font-family: Verdana; border: solid 1px black;font-weight:lighter"})

    _resultDict = None

    for tr in votes_table:
        # print(tr)
        if tr != "":
            try:
                _votes = None
                tds = tr.find_all('td')
                if candidate is None:
                    if tds[1].text == party:
                        # print("Candidate: {0} Party: {1}  Votes: {2}".format(tds[0].text, tds[1].text, tds[2].text))
                        _resultDict = {"candidate": tds[0].text, "party": tds[1].text, "votes": int(tds[2].text)}
                        break
                else:
                    if tds[0].text == candidate:
                        # print("Candidate: {0} Party: {1}  Votes: {2}".format(tds[0].text, tds[1].text, tds[2].text))
                        _resultDict = {"candidate": tds[0].text, "party": tds[1].text, "votes": int(tds[2].text)}
                        break
            except Exception as ae:
                _resultDict = None
                pass

    if _resultDict is None:
        return False
    else:
        return _resultDict


STATE = "mizoram"
PARTY = "Indian National Congress"

_constituencies = readStateInfo("states/{0}.csv".format(STATE))

_totalVotes = 0
_totalConstituencyCollected = 0
_resultList = []

for _constituency in _constituencies:
    _result = getResultConstituency(constituency=_constituency["constituencyNumber"], party=PARTY)
    if _result:
        _totalConstituencyCollected += 1
        _totalVotes =  _totalVotes + _result["votes"]
        _resultList.append([_constituency["constituencyName"], _result["candidate"], _result["votes"]])
        print("Constituency: {0} \t Candidate: {1} \t Votes: {2} \n".format(_constituency["constituencyName"], _result["candidate"], _result["votes"]))
        

print("\n\n TOTAL VOTES - {0:,} \n Collected from {1}/{2} Constituencies".format(_totalVotes, _totalConstituencyCollected, len(_constituencies)))

_resultList.sort(key = lambda x: x[2], reverse=True) 

writer = MarkdownTableWriter()
writer.headers = ["Constituency", "Candidate", "Votes"]
writer.value_matrix = _resultList

writer.styles = [
    Style(align="center"),
    Style(align="center"),
    Style(font_weight="bold", align="right", thousand_separator=","),
]

writer.write_table()

file = open("index.md","w") 
 
file.write("# Election Result UPP 2019 - Test \n") 
file.write("# TOTAL VOTES - {0:,} \n## (Collected from {1}/{2} Constituencies) \n # Results by Constituency \n\n\n".format(_totalVotes, _totalConstituencyCollected, len(_constituencies))) 

file.write(writer.dumps()) 
 
file.close() 