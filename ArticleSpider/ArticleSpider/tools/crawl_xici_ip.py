# -*- coding:utf-8 -*-
__author__ = 'zhangteng'
import requests
from scrapy.selector import Selector
import  MySQLdb

conn = MySQLdb.connect(host="localhost",user="root",password = "zhangteng",db = "article_spider",charset="utf8")
cursor = conn.cursor()

def crawl_ips():
    #攫取西刺的免费ip代理
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
    }
    for i in range(1879):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i),headers=headers)

        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
                print(speed)
            all_texts = tr.css("td::text").extract()

            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]

            ip_list.append((ip,port,speed,proxy_type))

        for ip_info in ip_list:
            cursor.execute(
                "insert article_spider.proxy_ip(ip, port, speed, proxy_type) values ('{0}','{1}',{2},'{3}')".format(ip_info[0],ip_info[1],ip_info[2],ip_info[3])
            )
            conn.commit()

class GetIP(object):
    #从数据库中删除无效的ip

    def delete_ip(self, ip):
        delete_sql = """
            delete from article_spider.proxy_ip where ip = '{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port, proxy_type):
        #判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try :
            proxy_dict = {
                proxy_type:proxy_url,
            }
            response = requests.get(http_url,proxies = proxy_dict)
        except Exception as e :
            print('invalid ip and port')
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code <300 :
                print ("effective ip")
                return True
            else:
                print('invalid ip and ip')
                return False

    def get_random_ip(self):
        #从数据库中随机获取一个ip
        sql = """select ip, port, proxy_type from article_spider.proxy_ip 
              ORDER BY RAND() 
              LIMIT 1 
              """
        result = cursor.execute(sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            proxy_type = ip_info[2]

            judge_re = self.judge_ip(ip,port, proxy_type)
            if judge_re:
                return "{0}://{1}:{2}".format(proxy_type,ip,port)
            else:
                return self.get_random_ip()
#crawl_ips()
if __name__ == "__main__":
    get_ip = GetIP()
    print(get_ip.get_random_ip())
