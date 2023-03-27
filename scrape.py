import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.message import EmailMessage

# URL endpoint for the POST request
login_url = 'https://cpr.repairq.io/site/login#'

def createSessionOne():

    data = {
        'UserLoginForm[username]': 'samuel.day',
        'UserLoginForm[password]': '4478',
        'UserLoginForm[currentLocation]': '958'
    }

    session_sam = requests.Session()
    session_sam.post(login_url, data=data)

    return session_sam

def createSessionTwo():

    data = {
        'UserLoginForm[username]': 'tshaikh',
        'UserLoginForm[password]': '5727galleria',
        'UserLoginForm[currentLocation]': '873'
    }

    session_taha = requests.Session()
    session_taha.post(login_url, data=data)

    return session_taha

def getCurrentDate():

    # Get current date as datetime object
    now = datetime.now()

    # Format datetime object as string in desired format
    date_str = now.strftime('%m/%d/%Y')

    return date_str

def getLastTableRow(table_rows):
    # Get last cell (td) in each table row
    last_cells = []
    for row in table_rows:
        cells = row.find_all('td')
        if len(cells) > 0:
            last_cell = cells[-1]
            last_cells.append(last_cell.text.strip())
    return last_cells

def getSummaryTableCell(table_rows):
    if len(table_rows) > 0:
        if len(table_rows[-2]) > 2:
            cells = table_rows[-2].find_all('td')
            if len(cells) > 2:
                return(cells[3].text.strip())
            else:
                return '$0'
        else:
            return "$0"

def getCashFlowToday(session, location_ID, location_STR):

    date = getCurrentDate()

    url = 'https://cpr.repairq.io/report/cashFlowSummary'

    data = {
        'filter[transactionDateStart_local]': date,
        'filter[transactionDateStart]': date,
        'filter[transactionDateEnd_local]': date,
        'filter[transactionDateEnd]': date,
        'filter[location][]': location_ID,
        'multiselect': location_ID,
        'yt0': 'Apply Filters'
    }

    response = session.post(url, data=data)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all table rows (tr) on webpage
    table_rows = soup.find_all('tr')

    last_cells = getLastTableRow(table_rows)

    # Print last item in array (total cashflow)
    revenue = last_cells.pop()

    if '$' not in revenue:
        revenue = "$0"

    return revenue

def getTicketCreatedToday(session, location_ID, location_STR):

    date = getCurrentDate()

    url = 'https://cpr.repairq.io/report/revenueDetail'

    data = {
        'filter[ticketDateStart_local]': date,
        'filter[ticketDateStart]': date,
        'filter[ticketDateEnd_local]': date,
        'filter[ticketDateEnd]': date,
        'filter[dateType]': 'created',
        'filter[location][]': location_ID,
        'multiselect': location_ID,
        'filter[closed_only]': 'all',
        'yt0': 'Apply Filters'
    }

    response = session.post(url, data=data)

    soup = BeautifulSoup(response.content, 'html.parser')

    h6_tags = soup.find_all('h6')

    amt = '$0'

    if len(h6_tags) > 5:
        amt = h6_tags[6].text.strip()

    return amt

def getPartsUsedToday(session, location_ID, location_STR):

    date = getCurrentDate()

    url = 'https://cpr.repairq.io/report/inventoryUsageSummary'

    data = {
        'filter[inventory_date_from_local]': date,
        'filter[inventory_date_from]': date,
        'filter[inventory_date_to_local]': date,
        'filter[inventory_date_to]': date,
        'filter[location][]': location_ID,
        'multiselect': location_ID,
        'yt0': 'Apply Filters'
    }

    response = session.post(url, data=data)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all table rows (tr) on webpage
    table_rows = soup.find_all('tr')

    used_parts = getSummaryTableCell(table_rows)

    return used_parts

def calculateProfitabilityFor(cashflow, used_parts):

    cashflow = float(cashflow[1:])
    used_parts = float(used_parts[1:])

    return '%.2f' % (cashflow - used_parts)

def getReportForStore(session, store_ID, store_STR):

    cashflow = getCashFlowToday(session, store_ID, store_STR)
    used_parts = getPartsUsedToday(session, store_ID, store_STR)
    ticket_created = getTicketCreatedToday(session, store_ID, store_STR)
    profitability = calculateProfitabilityFor(cashflow, used_parts)

    return [store_STR, cashflow, used_parts, ticket_created, profitability]

def generateTableForReport():

    data = [['Location', 'Cashflow', 'Parts Used', 'Ticket Created', 'Gross Profit']]
    data.append(getReportForStore(session_sam, 958, "CPR Atascocita"))
    data.append(getReportForStore(session_sam, 975, "CPR Liberty"))
    data.append(getReportForStore(session_taha, 873, "CPR Galleria"))
    data.append(getReportForStore(session_taha, 984, "CPR Richmond"))

    table_html = "<table style='text-align:center;'>"
    table_html += "<tr><th colspan='5'><h4 style='text-align:center;'>Daily Report for {}</h4></th></tr>".format(getCurrentDate())
    for row in data:
        table_html += "<tr>"
        for cell in row:
            table_html += "<td style='border: 1px solid black; padding: 5px;'>{}</td>".format(cell)
        table_html += "</tr>"
    table_html += "</table>"

    return table_html

def sendEmail(table, email):

    # set up email message
    msg = EmailMessage()
    msg['Subject'] = 'Daily Report'
    msg['From'] = 'samuel.day@cpr-stores.com'
    msg['To'] = email

    # add HTML content
    html = """
    <html>
    <head>
    	<title>Centered Table</title>
    </head>
    <body style="text-align:center;">
    	""" +  table + """
    </body>
    </html>
    """
    msg.set_content(html, subtype='html')

    # set up SMTP server and login
    with smtplib.SMTP('webmail.cellphonerepair.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.login('samuel.day@cpr-stores.com', 'Sad77889900!')

        # send email
        server.send_message(msg)


session_sam = createSessionOne()
session_taha = createSessionTwo()

table = generateTableForReport()

emails = ['samuel.day@cpr-stores.com', 'stephen.day@cpr-stores.com']

for email in emails:
    sendEmail(table, email)
