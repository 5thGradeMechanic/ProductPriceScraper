from replit import db
import requests, schedule, time, os, smtplib
from bs4 import BeautifulSoup
from replit import db
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
'''
keys = db.keys()
for key in keys:
  print("DELETED: ", keys)
  del db[key]
'''


#Function to add a product to be tracked
def addProduct():
  #Bottle Opener: https://ridge.com/products/stonewashed-titanium-bottle-opener
  #Fancy Pen: https://ridge.com/products/bolt-action-pen-matte-black-titanium
  #Travel Kit: https://ridge.com/products/frequent-flyer-kit-alpine-navy

  link = input("Link: ")
  desiredPrice = float(input("Desired Price: "))
  print()

  #Build the database, based on the time scraped (the key).
  db[time.time()] = {
    "name": None,
    "link": link,
    "price": None,
    "desiredPrice": desiredPrice
  }
  print("Product Added! \n")


def email(name, desiredPrice, price, link):
  password = os.environ['mailPassword']
  username = os.environ['mailUsername']
  host = "smtp.gmail.com"
  port = 587
  s = smtplib.SMTP(host=host, port=port)
  s.starttls()
  s.login(username, password)

  msg = MIMEMultipart()
  msg["To"] = username
  msg["From"] = username
  msg["Subject"] = f"""{name} fell below your target price!"""
  text = f"""<p><a href='{link}'>This item</a> is now {price} which is below your purchase level of {desiredPrice}</p>"""
  msg.attach(MIMEText(text, 'html'))
  s.send_message(msg)
  del msg


#Function to update the DB with scraped information
def updateProductDB():
  keys = db.keys()
  #print(keys)

  for key in keys:
    #print(f"""{key}: {db[key]}\n""")
    productName = db[key]["name"]
    url = db[key]["link"]
    price = db[key]["price"]
    desiredPrice = db[key]["desiredPrice"]
    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    #Add the name and price from the scrape to the DB
    productName = soup.find(
      "h1",
      {"class": "theridge-pdp__product-title"})['data-product-title'].strip()
    db[key]["name"] = productName  #assigns value to the DB
    productPrice = soup.find("span", {"class": "money igPrice"}).text.strip()
    formattedPrice = float(productPrice[1:].replace(",", ""))
    db[key]["price"] = formattedPrice  #assigns value to the DB

    #Print the stored variables out
    print("Stored Values:")
    print("Product Name:", productName)
    print("Price is:", formattedPrice)
    print("URL:", url)
    print("Desired Price:", desiredPrice)
    print()

    #Check if the price has changed from what has already been stored.
    if formattedPrice != price:
      db[key]["price"] = formattedPrice
      print("Price has changed! \n")

      #If the price has changed, check if it is below the desired price.
      if formattedPrice <= desiredPrice:
        print(
          f"The {productName} is now {price}, which is below your threshold of ${desiredPrice}. Email is beint sent."
        )
        print("---------- \n")
        email(
          productName, desiredPrice, price, url
        )  #If < target price, then send an email to yourself with a link and a reminder
        print("Email sent! \n")

      else:
        print(
          f"The {productName} is still more than your desired of price ${desiredPrice}.\n"
        )

    else:
      print(f"The price for {productName} has not changed.\n")


#addProduct()
#updateProductDB()

schedule.every(1).minutes.do(updateProductDB)
updateProductDB()

while True:
  schedule.run_pending()
  time.sleep(1)

#Potential Improvements
#Could add color to each output