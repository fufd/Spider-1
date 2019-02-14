# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib import parse
from Spider.items import JobBoleArticleItem
from Spider.utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
      # 解析所有文章页面的详情页的url
      post_nodes = response.css("#archive .floated-thumb .post-thumb a")
      for post_node in post_nodes:
          image_url = post_node.css("img::attr(src)").extract_first("")
          post_url = post_node.css("::attr(href)").extract_first("")
          yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":image_url}, callback=self.parse_detail)
      # 提取下一页的url 交给parse
      next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
      if next_url :
          yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)



    def parse_detail(self, response):
      article_item = JobBoleArticleItem()
      front_image_url = response.meta.get("front_image_url", "")
      title = response.css(".entry-header h1::text").extract()[0]
      praise_nums = response.css(".vote-post-up h10::text").extract()[0]
      fav_nums = response.css(".bookmark-btn::text").extract()[0]
      match_re = re.match(".*?(\d+).*", fav_nums)
      if match_re:
         fav_nums = int(match_re.group(1))
      else:
         fav_nums = 0

      comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
      match_re = re.match(".*?(\d+).*", comment_nums)
      if match_re:
         comment_nums = int(match_re.group(1))
      else:
         comment_nums = 0

      content = response.css("div.entry").extract()[0]

      tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
      tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
      tags = ",".join(tag_list)

      article_item["url_object_id"] = get_md5(response.url)
      article_item["title"] = title
      article_item["url"] = response.url
      article_item["front_image_url"] =[front_image_url]
      article_item["praise_nums"] = praise_nums
      article_item["comment_nums"] = comment_nums
      article_item["fav_nums"] = fav_nums
      article_item["tags"] = tags
      article_item["content"] = content
      yield article_item


