import requests
import re
import utils
import json
filename="province_name.json"
file = open(filename, encoding="utf8")
# province_name is used for translating province name from thai to eng
province_name = json.load(file)

class HTMLParser:
    """The HTMLParser class is a class that can be used to extract information from HTML strings.
    """

    def __init__(self):
        pass

    def get_anchor(self, html: str):
        """
        Returns a list of all anchor tags in the input HTML.

        Args:
        html (str): The input HTML string.

        Returns:
        list: A list of anchor tags in the input HTML.

        Example usage:
        html : '<html><body><a href="<https://www.example.com>">Link</a></body></html>'
        returns : ['<a href="<https://www.example.com>">']
        """
        return re.findall(r'<a\s+[^>]*>', html)

    def get_href(self, html: str):
        """
        Returns a list of all href attributes in anchor tags in the input HTML.

        Args:
        html (str): The input HTML string.

        Returns:
        list: A list of href attributes in anchor tags in the input HTML.

        Example usage:
        html : '<html><body><a href="https://www.example.com">Link</a></body></html>'
        returns : ['https://www.example.com']
        """
        return re.findall(r'(?<=href=").*?(?=")', html)

    def get_title(self, html: str):
        """
        Returns a list of all title attributes in anchor tags in the input HTML.

        Args:
        html (str): The input HTML string.

        Returns:
        list: A list of title attributes in anchor tags in the input HTML.

        Example usage:
        html : '<html><body><a href="https://www.example.com" title="Example Website">Link</a></body></html>'
        returns : ['Example Website']
        """
        return re.findall(r'(?<=title=").*?(?=")', html)


class Crawler:
    """This class is responsible for crawling a website that contains information about temples in Thailand. 
    It has methods for extracting information from the HTML of the website and exporting the data to CSV files.

    ### Attributes

    - `HOST`: The base URL of the website being crawled.
    - `root_url`: The URL of the root page of the website being crawled.
    - `provinces`: A list of the provinces to be crawled (Thai).
    - `parser`: An instance of the `HTMLParser` class, used for parsing the HTML of the website.
    - `result`: A list to store the collected data from crawling the website.    

    """

    def __init__(self, HOST: str, root_url: str, provinces: list, parser: HTMLParser):
        """The constructor method instantiates the Crawler class with the specified parameters.
        ### Parameters:
        - `HOST` : str - The base URL of the website being crawled.
        - `root_url` : str - The URL of the root page of the website being crawled.
        - `provinces` : list - A list of the provinces to be crawled (Thai).
        - `parser` : HTMLParser - An instance of the `HTMLParser` class, used for parsing the HTML of the website.
        """
        self.HOST = HOST
        self.parser = parser
        self.root_url = root_url
        self.provinces = provinces
        self.result = list()

    # extract provinces and href from the anchors in root html
    def extract_provinces(self, html: str):
        """This method extracts the provinces and their corresponding URLs from the HTML strings.

        **Parameters:**

        - `html` : str - The HTML strings.

        **Returns:**

        - `temples` : list - A list of dictionaries containing the title and href of the anchor tags in the HTML.

        """

        anchors = self.parser.get_anchor(html)
        # print("--ANCHORS--")
        # print(anchors)
        f = open("anchors.txt", "w", encoding="utf-8")
        f.write("Found "+str(len(anchors))+" <a>\n")
        for item in anchors:
            f.write(str(item)+"\n")
        f.close()
        # print("--End ANCHORS--")
        temples = []
        # print("--title--")
        for anchor in anchors:
            title = self.parser.get_title(anchor)
            href = self.parser.get_href(anchor)
            if len(title) != 0:
                if re.match("รายชื่อวัดใน", title[0]):
                    temples.append({"title": title[0], "href": href[0]})
                    f = open("href.txt", "a", encoding="utf-8")
                    # for item in href:
                    f.write(str(href[0])+"\n")
                    f.close()   
                    f = open("title.txt", "a", encoding="utf-8")
                    # for item in href:
                    f.write(str(title[0])+"\n")
                    f.close()

            # print("--End title--")
        return temples

    def extract_temple_name(self, html):
        """This method extracts the names of the temples from the HTML of a province page.

        **Parameters:**

        - `html` : str - The HTML of a province page.

        **Returns:**

        - `temple_names` : list - A list of the names of the temples.

        """
        temple_name_pattern = r'(?<=title=")วัด.*?(?="|\s\()'
        temple_names = re.findall(temple_name_pattern, html)

        # Remove last 2 items : "วัดไทย"
        temple_names = temple_names[:len(temple_names)-2]

        return temple_names

    def run(self):
        """This method runs the crawler by crawling each desired province, 
        extracting the names of the temples in each province, and exporting the collected data to a CSV file.

        **Returns:**

        - `None`
        """        
        print("Start running crawler")
        # Clear the list of previously collected data
        self.result = []

        # Get the HTML of the root page
        root_html = requests.get(self.root_url).text
        # print(root_html)
        # Extract the provinces and their corresponding URLs from the HTML of the root page
        provinces_href = self.extract_provinces(root_html)
        # print("--provinces_href--")
        # print(provinces_href)

        province_url_to_visit = []

        # Get links for each desired province
        for province in self.provinces:
            for ph in provinces_href:
                match = re.search(province, ph['title'])
                if match:
                    province_url_to_visit.append(
                        {'province': province, 'url': self.HOST+ph['href']})
        print("province_url_to_visit :",province_url_to_visit)

        # Crawl each province and extract the names of the temples in each province
        for province_url in province_url_to_visit:
            url = province_url['url']
            print('Crawling: ' + province_url['province'])
            html = requests.get(url).text
            temple_name_in_this_province = self.extract_temple_name(html)
            
            # Export the collected data to a CSV file
            thai_province_name = province_url['province']
            eng_province_name = province_name['to_eng'][thai_province_name]
            utils.export_csv(temple_name_in_this_province, header=None,
                            filename='../' + eng_province_name+'.csv')
