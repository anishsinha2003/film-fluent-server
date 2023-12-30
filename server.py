from flask_cors import CORS
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests


app = Flask("__name__")
CORS(app)

#routes
@app.route("/get/titles", methods=['POST'])
def receive_data():
    # movie/tv show name gotten from the frontend
    query = request.get_json()

    # make url for the given query
    queryUrl = f"https://www.imdb.com/find/?q={query}&ref_=nv_sr_sm"
    # mimicking user agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {"user-agent": USER_AGENT}
    pageToScrape = requests.get(queryUrl, headers=headers)
    soup = BeautifulSoup(pageToScrape.text, "html.parser")
    listOfTitesDict = []

    titlesDiv = soup.find("section", attrs={"data-testid" : "find-results-section-title"})
    if (titlesDiv):

        titleNames = titlesDiv.findAll("a", attrs={"class": "ipc-metadata-list-summary-item__t"})
        tags = titlesDiv.findAll("ul", attrs={"class": "ipc-inline-list ipc-inline-list--show-dividers ipc-inline-list--no-wrap ipc-inline-list--inline ipc-metadata-list-summary-item__tl base"})
        actors = titlesDiv.findAll("ul", attrs={"class": "ipc-inline-list ipc-inline-list--show-dividers ipc-inline-list--no-wrap ipc-inline-list--inline ipc-metadata-list-summary-item__stl base"})
        imgs = titlesDiv.findAll("img", attrs={"class": "ipc-image"})

        for i in range(0, len(titleNames)):
            # try blocks for attributes that dont exist
            try:
                 title = titleNames[i].text
            except:
                title = "none"

            try:
                tag = tags[i].text
            except:
                tag = "none"

            try:
                actorsList = actors[i].text.split(", ")
            except:
                actorsList = []

            try:
                # image = imgs[i].get("src")
                href = titleNames[i].get("href")
                titleId = href.split("/")[2]
                image = getImageSrc(titleId, headers)
            except:
                image = "none"
            try:
                href = titleNames[i].get("href")
                titleId = href.split("/")[2]
                urlForThatTitle = f"https://www.imdb.com/title/{titleId}/reviews"
            except:
                urlForThatTitle = "none"

            newTitleInfo = {}
            newTitleInfo["title"] = title
            newTitleInfo["tag"] = tag
            newTitleInfo["actorsList"] = actorsList
            newTitleInfo["image"] = image
            newTitleInfo["urlForThatTitle"] = urlForThatTitle

            listOfTitesDict.append(newTitleInfo)
    return jsonify({'titles': listOfTitesDict})


@app.route("/get/reviews", methods=['POST'])
def get_reviews():
    hrefUrl = request.get_json()
    # mimicking user agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {"user-agent": USER_AGENT}
    pageToScrape = requests.get(hrefUrl, headers=headers)
    soup = BeautifulSoup(pageToScrape.text, "html.parser")

    listOfReviews = []

    listDiv = soup.find("div", attrs={"class" : "lister-list"})
    if (listDiv):
        allReviews = listDiv.findAll("div", attrs={"class": "review-container"})
        for i in range(0, len(allReviews)):
            rating = allReviews[i].find("div", attrs={"class": "ipl-ratings-bar"})
            if rating:
                rating = rating.text.strip()
                parts = rating.split("/")
                rating = int(parts[0])
            else:
                rating = "None"

            name_date = allReviews[i].find("div", attrs={"class": "display-name-date"})
            if name_date:
                name_date = name_date.text.lstrip()
            else:
                name_date = "None"

            content = allReviews[i].find("div", attrs={"class": "text show-more__control"})
            if content:
                content = content.text
            else:
                content = "None"

            newReviewInfo = {}

            newReviewInfo["rating"] = rating
            newReviewInfo["name_date"] = name_date
            newReviewInfo["content"] = content

            listOfReviews.append(newReviewInfo)
    return jsonify({'reviews': listOfReviews})

def getImageSrc(filmId, headers):
    imageScrape = requests.get(f"https://www.imdb.com/title/{filmId}/", headers=headers)
    soup = BeautifulSoup(imageScrape.text, "html.parser")
    imageDiv = soup.find("a", attrs={"class" : "ipc-lockup-overlay ipc-focusable"})
    if (imageDiv):
        imageHref = imageDiv.get('href')
        imageScrape2 = requests.get(f"https://www.imdb.com{imageHref}", headers=headers)
        soup = BeautifulSoup(imageScrape2.text, "html.parser")
        imageDiv = soup.find("img", attrs={"class" : "sc-7c0a9e7c-0 eWmrns"})
        imageSrc = imageDiv.get("src")
        return imageSrc
    return "None"


if __name__ == "__main__":
    app.run(debug=True)