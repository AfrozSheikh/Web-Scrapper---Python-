from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo

logging.basicConfig(filename="scrapper.log", level=logging.INFO)
client =pymongo.MongoClient("mongodb+srv://sa8329925:9766432374Afroz@webscrapping.k0j9t.mongodb.net/?retryWrites=true&w=majority&appName=WebScrapping")
app = Flask(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            
            # Updated to match the class name from the standalone script
            bigboxes = flipkart_html.findAll("div", {"class": "cPHDOP col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]

        
            
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            
            # Updated to match the class name from the standalone script
            commentboxes = prod_html.find_all("div", {"class": "RcXBOT"})
            productName = box.find("div", {"class": "KzDlHZ"}).text 

            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = 'Unkown'
                    logging.info("name not found")

                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = 'No Rating'
                    logging.info("rating not found")

                try:
                    commentHead = commentbox.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                    logging.info("commentHead not found")

                try:
                    custComment = commentbox.find("div", {"class": "ZmyHeo"}).div.div.text
                except:
                    custComment = 'No Comment'
                    logging.info("custComment not found")

                mydict = {"Product": productName, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            
            logging.info("log my final result {}".format(reviews))
            db = client['review-scrap']
            review_col = db['review_scrap_data']
            review_col.insert_many(reviews)
            return render_template('result.html', reviews=reviews)

        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0")







