# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from tools.crawl_xici_ip import GetIP
from fake_useragent import UserAgent


class ArticlespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

#随机生成UserAgent
class RandomUserAgentMiddlware( object):
    def __init__(self,crawler):
        super(RandomUserAgentMiddlware,self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE","random")
        pass

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler)

    def process_request(self,request,spider):
        def get_ua():
            return getattr(self.ua,self.ua_type)

        request.headers.setdefault("User-Agent",get_ua())
        pass
        #ip代理
        # request.meta['proxy'] = "http://222.85.50.108:808"

#随机获取ip
class RandomProxyMiddleware(object):
    def process_request(self, request,spider):
        request.meta['proxy'] = GetIP.get_random_ip()
        pass

#通过chrom请求动态网页
class JSPageMiddleware(object):
    def process_request(self, request, spider):
        spider.brower.get(request.url)
        if spider.name == "jd":
            import time
            time.sleep(2)
        return HtmlResponse(url = spider.brower.current_url, body = spider.brower.page_source, encoding="utf-8",request=request)