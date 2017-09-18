# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst,MapCompose
from w3lib.html import remove_tags


class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class JDIndexItem(scrapy.Item):
    index_name = scrapy.Field()
    url = scrapy.Field()
    pro_name = scrapy.Field()
    pro_url = scrapy.Field()
    def get_insert_sql(self):
        insert_sql="""
        insert into jd_index(url,name,pro_url,pro_name)VALUES (%s,%s,%s,%s)
        """
        params=(
            self["url"],self["index_name"],self["pro_url"],self["pro_name"]
        )
        return insert_sql,params

class JDDetailItem(scrapy.Item):
    uid = scrapy.Field()      #种类的name
    url = scrapy.Field()          #价格
    price = scrapy.Field()            #评论面页的url
    jdname = scrapy.Field()     #主标题
    jdcommit = scrapy.Field()     #副标题
    jdtype = scrapy.Field()#店铺
    shopname = scrapy.Field()
    sort_name = scrapy.Field()  #店铺支持
    def get_insert_sql(self):
        insert_sql="""
        insert into jd_detile(uid,url,price,jdname,jdcommit,jdtype,shopname,sort_name)VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        params=(
            self["uid"],self["url"],self["price"],self["jdname"],self["jdcommit"],self["jdtype"],self["shopname"],self["sort_name"]
        )
        return insert_sql,params

class JDCommentItem(scrapy.Item):
    uid = scrapy.Field()
    shopParams = scrapy.Field()
    buy_sourse = scrapy.Field()
    user_comment = scrapy.Field()
    good_sourse = scrapy.Field()
    user_comment_Detail = scrapy.Field()
    def get_insert_sql(self):
        insert_sql="""
        insert into jd_comment(uid,shopParams,buy_sourse,user_comment,good_sourse,user_comment_Detail)VALUES (%s,%s,%s,%s,%s,%s)
        """
        params=(
            self["uid"],self["shopParams"],self["buy_sourse"],self["user_comment"],
            self["good_sourse"],self["user_comment_Detail"]
        )
        return insert_sql,params
