# Project Name

## Project file structure
```
/
    environment.yml
    Dockerfile
    docker-compose.yml
demo/
    code/
    context_data/
        jobs/
        data/
career_hub/
    main.py
    career_hub/
        __init__.py
        middlewares.py
        settings.py
        items.py
        pipelines.py
        spiders/
            __init__.py
            careerhub_spider.py
.vscode/
```

## Code

## environment.yml
```python
name: web_spider
channels:
  - defaults
dependencies:
  - python=3.9
  - anaconda::anaconda
  - pymongo
```
## Dockerfile
```python
FROM continuumio/anaconda3:latest
COPY environment.yml .
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y make

RUN conda update -n base -c defaults conda
RUN conda env create -f environment.yml
RUN echo "conda activate web_spider" >> ~/.bashrc

ENV PATH /opt/conda/envs/web_spider/bin:$PATH

WORKDIR /app
EXPOSE 8888
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]

```
## docker-compose.yml
```python
version: '3'

services:
  scrapy:
    build: .
    volumes:
      - .:/app
    environment:
      - MONGO_HOST=mongo
    depends_on:
      - mongo
    ports:
      - "8888:8888"

  mongo:
    image: mongo:latest
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - ./mongodb-data:/data/db
```
## career_hub/main.py
```python
from scrapy import cmdline

cmdline.execute("scrapy crawl career".split())

```
## career_hub/career_hub/__init__.py
```python

```
## career_hub/career_hub/middlewares.py
```python
# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class CareerHubSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class CareerHubDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

```
## career_hub/career_hub/settings.py
```python
# Scrapy settings for career_hub project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os

def load_env():
    # get the absolute path of the code file
    code_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(os.path.dirname(os.path.dirname(code_dir)), '.secrets')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                # parse the key-value pairs in the .env file
                key, value = [x.strip() for x in line.strip().split('=')]
                os.environ[key] = value
load_env()

# Access the SECRET_KEY environment variable
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

BOT_NAME = "career_hub"

SPIDER_MODULES = ["career_hub.spiders"]
NEWSPIDER_MODULE = "career_hub.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'career_hub (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Download delay
DOWNLOAD_DELAY = 0

# Turn off fitering
DUPEFILTER_CLASS = "scrapy.dupefilters.BaseDupeFilter"

# SETTING for mongodb
MONGO_DATABASE = "career_hub"
MONGO_URI = "mongodb://localhost:27017/"

ITEM_PIPELINES = {
    "career_hub.pipelines.ItemPipeline": 700,
}

```
## career_hub/career_hub/items.py
```python
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class BaseItem(Item):
    _id = Field()
    crawled_timestamp = Field()


class CareerHubItem(BaseItem):
    # just need one field, cause the structure of the item is dynamic
    item = Field()

```
## career_hub/career_hub/pipelines.py
```python
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pymongo
from datetime import datetime
from career_hub.items import CareerHubItem


class CareerHubPipeline:
    def process_item(self, item, spider):
        return item


class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        raise NotImplementedError


class ItemPipeline(MongoPipeline):
    def process_item(self, item, spider):
        if isinstance(item, CareerHubItem):
            item["item"]["crawled_timestamp"] = datetime.now()
            collection_name = "_".join(["web", spider.name])
            self.db[collection_name].insert_one(item["item"])
        return item

```
## career_hub/career_hub/spiders/__init__.py
```python
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

```
## career_hub/career_hub/spiders/careerhub_spider.py
```python
import scrapy
from scrapy.http import FormRequest, Request
from bs4 import BeautifulSoup
from career_hub.items import CareerHubItem
from itemadapter import ItemAdapter
from career_hub.settings import USERNAME, PASSWORD


import hashlib


def url_to_key(url: str) -> str:
    hash_object = hashlib.md5(url.encode())
    return hash_object.hexdigest()

class CareerSpider(scrapy.Spider):
    """
    describle the spider:

    - login to the career hub
    - get the ticket from the login link
    - get the detail link of each job
    - parse job detail, and save to moongdb
    """

    name = "career"
    start_urls = ["https://login.adelaide.edu.au/cas/login"]

    target_urls = {
        "gp": "https://careerhub.adelaide.edu.au/students/jobs/TypeOfWork/896/graduate-employment",
        "intern": "https://careerhub.adelaide.edu.au/students/jobs/TypeOfWork/899/internship-placement-vacation-",
    }

    base_url = "https://careerhub.adelaide.edu.au"

    username = USERNAME
    password = PASSWORD

    def parse(self, response):
        # Extract the CSRF token from the login page using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        login_data = {
            "username": self.username,
            "password": self.password,
            "lt": "",
            "execution": "e1s1",
            "_eventId": "submit",
            "submit": "Login",
        }

        login_data["lt"] = soup.select_one('[name="lt"]')["value"]

        # Submit a POST request to the login form with your credentials
        yield FormRequest.from_response(
            response, formdata=login_data, callback=self.after_login
        )

    def after_login(self, response):
        # Check if the login was successful
        if "Log Out" in response.text:
            self.logger.info("Login successful!")
            for t, url in self.target_urls.items():
                yield Request(url=url, callback=self.get_ticket, meta={"type": t})
        else:
            self.logger.error("Login failed.")

    def get_ticket(self, response):
        # get ticket embeding in the login link
        soup = BeautifulSoup(response.text, "html.parser")
        login_link = soup.find("a", class_="btn btn-primary btn-lg")["href"]

        yield Request(url=login_link, callback=self.get_jobs)

    def get_jobs(self, response):
        # Parse the job list
        soup = BeautifulSoup(response.text, "html.parser")

        job_list = soup.find_all("div", class_="list-group-item")

        for job in job_list:
            title = (
                job.find("h4")
                .text.strip()
                .replace("\n", "")
                .replace("\r", "")
                .replace("\s", "")
            )
            title = " ".join(title.split())
            detail_link = job.find("a")["href"]
            # yield {"title": title, "detail_link": detail_link}
            yield Request(
                url=self.base_url + detail_link,
                callback=self.parse_detail,
                meta={"type": response.meta.get("type")},
            )

        if not response.meta.get("page"):
            page = soup.find_all("span", class_="pull-right")
            page = page[0].text
            page = page.split(" ")
            total_page = page[-1]
            for i in range(2, int(total_page) + 1):
                yield Request(
                    response.url + f"?page={i}",
                    callback=self.get_jobs,
                    meta={"page": i, "type": response.meta.get("type")},
                )

    def parse_detail(self, respone):
        soup = BeautifulSoup(respone.text, "html.parser")

        # each info, creare a none proof
        company_name = (
            soup.find("div", class_="under-nav")
            .find("div", class_="container")
            .find("h4")
            .find("span")
        )
        company_name = (
            company_name.text.strip().replace("\n", "").replace("\r", "")
            if company_name
            else None
        )

        # each info, creare a none proof
        company_link = (
            soup.find("div", class_="under-nav")
            .find("div", class_="container")
            .find("h4")
            .find("a")
        )
        company_link = company_link["href"] if company_link else None

        # each info, creare a none proof
        job_details = soup.find("div", class_="job-details")
        job_details = (
            job_details.text.strip().replace("\n", "").replace("\r", "")
            if job_details
            else None
        )

        eles = soup.find("div", class_="under-nav")

        # each info, creare a none proof
        job_title = eles.find("h3")
        job_title = (
            job_title.text.strip().replace("\n", "").replace("\r", "")
            if job_title
            else None
        )

        # each info, creare a none proof
        job_locations = [
            x.parent.text.strip().replace("\n", "").replace("\r", "")
            for x in eles.find_all("span", class_="glyphicon glyphicon-map-marker")
            if x
        ]

        try:
            application_procedures = None
            app_link = soup.find("p", class_="job-detail-website").find("a")["href"]
        except AttributeError:
            application_procedures = (
                [
                    x
                    for x in soup.find_all("div")
                    if x.text.strip().lower() == "applications"
                ][0]
                .find_next_sibling("div")
                .text.strip()
                .replace("\n", "")
                .replace("\r", "")
            )
            app_link = None

        # deadline
        application_deadline = [x for x in soup.find_all("div", class_="panel-heading")]

        application_deadline = (
            [
                x
                for x in application_deadline
                if x.text.strip().lower() == "applications"
            ]
            if application_deadline
            else None
        )
        application_deadline = (
            (application_deadline[0].find_next_siblings("div", class_="panel-body"))
            if application_deadline
            else None
        )

        application_deadline = (
            application_deadline[0].find("strong") if application_deadline else None
        )

        application_deadline = (
            application_deadline.text.strip().replace("\n", "").replace("\r", "")
            if application_deadline
            else None
        )

        # getting the other information

        other_info = soup.find_all("div", class_="panel-heading")
        other_info = [
            x for x in other_info if x.text.strip().lower() == "other information"
        ]
        other_info = other_info[0] if other_info else None
        other_info = other_info.find_next_siblings("div")[0] if other_info else None

        other_info_titles = other_info.find_all("strong") if other_info else None
        other_info_values = other_info.find_all("p") if other_info else None

        other_info_titles = (
            [x.text.strip().replace(" ", "-") for x in other_info_titles]
            if other_info_titles
            else None
        )
        other_info_values = (
            [x.text.strip() for x in other_info_values] if other_info_titles else None
        )

        posted_date = other_info.find("small") if other_info else None
        posted_date = posted_date.text.strip() if posted_date else None

        item = {}
        item["title"] = job_title
        item["company_name"] = company_name
        item["company_link"] = self.base_url + company_link if company_link else None
        item["locations"] = job_locations
        item["detail"] = job_details
        item["application_procedures"] = application_procedures
        item["application_link"] = self.base_url + app_link if app_link else None
        item["application_deadline"] = application_deadline
        item["_id"] = url_to_key(respone.url)
        item["job_type"] = respone.meta.get("type")

        if other_info_titles and other_info_values:
            other_info_dict = dict(zip(other_info_titles, other_info_values))
            item["other_info"] = other_info_dict

        item["posted_date"] = posted_date
        item["url"] = respone.url

        # remove none
        item = {k: v for k, v in item.items() if v}

        if item.get("application_link"):
            yield Request(
                url=self.base_url + app_link,
                meta={"item": item},
                callback=self.get_redirect_url,
            )
        else:
            hub_item = CareerHubItem()
            hub_item["item"] = item
            yield hub_item

    def get_redirect_url(self, response):
        # get the redirect url

        item = response.meta.get("item")
        item["application_link"] = response.url

        hub_item = CareerHubItem()
        hub_item["item"] = item
        yield hub_item

```