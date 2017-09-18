# -*- coding:utf-8 -*-
__author__ = 'zhangteng'
from scrapy_redis.spiders import RedisSpider
from selenium.webdriver.common.action_chains import ActionChains
from scrapy.http import Request
from urllib import parse
import uuid
import os
from items import JDIndexItem, ArticleItemLoader, JDDetailItem, JDCommentItem
from selenium import webdriver
from scrapy import signals
from scrapy.selector import Selector
from scrapy.xlib.pydispatch import dispatcher
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

class MySpider(RedisSpider):
    name = 'jd'
    redis_key = "jobbole:start_urls"
    def __init__(self):
        self.firefox_profile=FirefoxProfile()
        self.firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
        self.brower = webdriver.Firefox(firefox_profile=self.firefox_profile,executable_path=os.path.join(os.path.abspath(os.path.dirname(__file__)),"Selenium\geckodriver.exe"))
        super(MySpider, self).__init__()
        #信号  当关闭时关闭浏览器
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        print('spider closed')
        self.brower.quit()

    def parse(self, response):
        self.brower.get(response.url)
        self.brower.execute_script("window.scrollTo(0,250)")
        for i in range(1,16):
                selector=self.brower.find_element_by_xpath("html/body/div[5]/div[1]/div[1]/div/ul/li[{0}]".format(i))
                ActionChains(self.brower).move_to_element(selector).perform()
        """
        1、获取当前页面
        2、获取到下一页的Url 并交给scrapy下载 下载完成后交给Parse
        """
        selectorRepnse=Selector(text=self.brower.page_source)
        #self.brower.quit()
        items_pop = selectorRepnse.css(".cate_detail_item")
        for items in items_pop:
            #主分类
            pro = items.css(".cate_detail_tit_lk")
            pro_name = pro.css("::text").extract_first("")
            pro_url = parse.urljoin(response.url, pro.css("::attr(href)").extract_first(""))
            links = items.css(".cate_detail_con_lk")
            for link in links:
                #次级分类
                name = link.css("::text").extract_first("")
                url = parse.urljoin(response.url,link.css("::attr(href)").extract_first(""))
                #填充Item
                item_loader = ArticleItemLoader(item=JDIndexItem(), response=response)
                item_loader.add_value("index_name",str(name))
                item_loader.add_value("url",str(url))
                item_loader.add_value("pro_name",str(pro_name))
                item_loader.add_value("pro_url",str(pro_url))
                article_item = item_loader.load_item()
                yield article_item
                yield Request(url= url, meta={"name": name}, callback=self.parse_detail, dont_filter=True)

            # for link in links:
            #     url = parse.urljoin(response.url,link.css("::attr(href)").extract_first(""))
            #     #把详细页交给 parse_detail 解析
            #     yield Request(url=parse.urljoin(response.url, url), meta={"name": name},callback=self.parse_detail)


    def parse_detail(self, response):
        self.brower.get(response.url)
        self.brower.execute_script("window.scrollTo(0,document.body.scrollHeight-1000)")
        import time
        time.sleep(2)
        selecter=Selector(text=self.brower.page_source)
        #解析详细 页
        sort_name = response.meta.get("name", "")
        # 通过Itemloder加载item
        detail_items = selecter.css(".gl-i-wrap.j-sku-item")
        for detail_item in detail_items:
           uid = uuid.uuid4()
           item_loder=ArticleItemLoader(item=JDDetailItem(),response=response)
           url=parse.urljoin(response.url,detail_item.css("div.gl-i-wrap.j-sku-item div.p-img a::attr(href)").extract_first())
           price=detail_item.css("div.p-price strong i::text").extract_first("")
           name=detail_item.css("div.p-name em::text").extract_first("")
           commit=detail_item.css("div.p-commit span.buy-score em::text").extract_first("暂无推荐指数")
           type=detail_item.css("div.p-icons.J-pro-icons i::text").extract_first("")
           shopname=detail_item.css("div.p-shop span a::text").extract_first("")
           item_loder.add_value("uid",uid)
           item_loder.add_value("url",url)
           item_loder.add_value("price",price)
           item_loder.add_value("jdname",name)
           item_loder.add_value("jdcommit",commit)
           item_loder.add_value("jdtype",type)
           item_loder.add_value("shopname",shopname)
           item_loder.add_value("sort_name",sort_name)
           yield item_loder.load_item()
           yield Request(url=url, meta={"detail_url":url,"uid":uid}, callback=self.parse_comment, dont_filter=True)
        next_url= parse.urljoin(response.url, response.css(".pn-next::attr(href)").extract_first(""))
        if next_url != "":
            yield Request(url=next_url, callback=self.parse_detail, meta={"name": sort_name}, dont_filter=True)

    def parse_comment(self, response):
        #上个商品的url
        detail_url = response.meta.get("detail_url", "")
        #上个商品的外键
        uid = response.meta.get("uid", "")
        self.brower.get(detail_url)
        self.brower.execute_script("window.scrollTo(0,1000)")
        self.brower.find_element_by_css_selector("li[data-anchor=\"#comment\"]").click()
        import time
        time.sleep(2)
        select=Selector(text=self.brower.page_source)
        #商品简介
        shopItems=select.css("ul.parameter2.p-parameter-list li")
        shopMes=""
        for shopItem in shopItems:
            text=shopItem.css("::text").extract_first()
            shopMes+=text+";"
        buySourse=select.xpath(".//*[@id='buy-rate']/a/text()").extract_first("无购买指数")
        #累计所占比例
        items=""
        buyItems=select.css("ul.filter-list li a")
        for index in range(len(buyItems)):
            items+=buyItems[index].css("::text").extract_first()
            items+=buyItems[index].css("em::text").extract_first()+";"
        #商品分数
        goodtext=select.css("div.comment-percent strong.percent-tit::text").extract_first("未获取到!")
        source=select.xpath(".//*[@id='comment']/div[2]/div[1]/div[1]/div/text()").extract_first("100")+"%"
        #商品评价分数
        shopSourse=goodtext+":"+source
        shopMessage=select.css("div.tag-list span")
        # 商品评价具体参数
        ShopParameter=""
        if shopMessage:
            for shopmess in shopMessage:
                ShopParameter+=shopmess.css("::text").extract_first()+";"
        else:
           ShopParameter = "暂无评论记录"
        #添加数据
        items_loder=ArticleItemLoader(item=JDCommentItem(),response=response)
        items_loder.add_value("uid",uid)
        items_loder.add_value("shopParams",shopMes)
        items_loder.add_value("buy_sourse",buySourse)
        items_loder.add_value("user_comment",items)
        items_loder.add_value("good_sourse",shopSourse)
        items_loder.add_value("user_comment_Detail",ShopParameter)
        yield items_loder.load_item()

