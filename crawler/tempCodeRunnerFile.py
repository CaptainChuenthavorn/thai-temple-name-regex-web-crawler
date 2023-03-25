import crawler
import sys
import json

URL = 'https://th.wikipedia.org/wiki/%E0%B8%AB%E0%B8%A1%E0%B8%A7%E0%B8%94%E0%B8%AB%E0%B8%A1%E0%B8%B9%E0%B9%88:%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%8A%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%A7%E0%B8%B1%E0%B8%94%E0%B9%84%E0%B8%97%E0%B8%A2'
HOST = 'https://th.wikipedia.org'

filename="province_name.json"
file = open(filename, encoding="utf8")
# province_name is used for translating province name from thai to eng
province_name = json.load(file)

if __name__ == "__main__":

    # no args
    province_thai = ["กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี"]

    # args
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        if (args[0] == "-p" or args[0] == "-province") and len(args) > 1:
            province_thai = [province_name["to_thai"][province]
                            for province in args[1:]]

    crawler = crawler.Crawler(HOST, URL, province_thai, crawler.HTMLParser())

    # crawler export the temple names to csv file
    crawler.run()
