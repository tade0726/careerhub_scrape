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

        yield Request(url=login_link, callback=self.get_jobs,  meta={"type": response.meta.get("type")})

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
