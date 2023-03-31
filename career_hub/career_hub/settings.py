# Scrapy settings for career_hub project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os

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
