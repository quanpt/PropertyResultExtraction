import urllib.request
import time, base64, subprocess
import csv
from lxml import etree


# download the url
def url_retrieve(url, file_name):
    urllib.request.urlretrieve(url, file_name)




# extract data from domain page to csv
def write_domain_csv(file_name, distanceDict):
    suburb_expr = '//div[@class="suburb-listings" and descendant::h6[@class="suburb-listings__heading"]]'
    suburb_text_expr = './/h6[@class="suburb-listings__heading"]'
    property_link_expr = './/a[@class="auction-details"]'
    address_expr = './/span[@class="auction-details__address"]'
    bedroom_expr = './/span[@class="auction-details__bedroom"]'
    property_type_expr = './/span[@class="auction-details__property-type"]'
    price_expr = './/span[@class="auction-details__price"]'
    href_expr = './@href'
    print_format = '"{}"\t"{}"\t{}\t"{}"\t{}\t"{}"\t{}\n'

    html_parser = etree.HTMLParser(encoding='utf-8', recover=True,
                                   strip_cdata=True)
    document = etree.parse(file_name, html_parser)
    with open('domain_{}.csv'.format(time.strftime("%Y_%m_%d")), 'w') as output:
        output.write(print_format.format('Suburb', 'Address', 'Bedroom', 'Type', 'Price', 'Link', 'Distance'))
        for e in document.xpath(suburb_expr):
            suburb_name = e.xpath(suburb_text_expr)[0].text
            for property_link in e.xpath(property_link_expr):
                price_text = property_link.xpath(price_expr)[0].text
                try:
                    price = float(price_text[1:-1]) * (1000 if price_text[-1] == 'm' else 1)
                except ValueError:
                    price = price_text
                output.write(print_format.format(suburb_name,
                                                 property_link.xpath(address_expr)[0].text,
                                                 property_link.xpath(bedroom_expr)[0].text,
                                                 property_link.xpath(property_type_expr)[0].text,
                                                 price,
                                                 property_link.xpath(href_expr)[0],
                                                 distanceDict.get(suburb_name.upper(), 'unknown')))


def img2room(href):
    if href.find('convert/LQ') > 0:
        return 0
    if href.find('convert/MQ') > 0:
        return 1
    if href.find('convert/Mg') > 0:
        return 2
    if href.find('convert/Mw') > 0:
        return 3
    if href.find('convert/NA') > 0:
        return 4
    if href.find('convert/NQ') > 0:
        return 5
    if href.find('convert/Ng') > 0:
        return 6
    return 7


def getXpath(element, xpath, default):
    res = element.xpath(xpath)
    return res[0] if len(res) > 0 else default


# extract data from realestate page to csv
def write_realestate_csv(file_name, distanceDict):
    suburb_expr = '//div[@class="rui-table-responsive suburb" and descendant::div[@class="col-suburb-name"]]'
    suburb_text_expr = './/div[@class="col-suburb-name"]'
    property_link_expr = './/tbody/tr'
    address_expr = '(.//a[@class="col-address"]/text() | .//div[@class="col-address"]/text())'
    bedroom_expr = './/div[contains(@class,"col-num-beds")]/text()'
    property_type_expr = './/div[@class="col-property-type"]/text()'
    price_expr = './/div[@class="col-property-price"]/text()'
    href_expr = './/a[@class="col-address"]/@href'
    print_format = '"{}"\t"{}"\t{}\t"{}"\t{}\t"{}"\t{}\n'

    html_parser = etree.HTMLParser(encoding='utf-8', recover=True,
                                   strip_cdata=True)
    document = etree.parse(file_name, html_parser)
    with open('realestate_{}.csv'.format(time.strftime("%Y_%m_%d")), 'w') as output:
        output.write(print_format.format('Suburb', 'Address', 'Bedroom', 'Type', 'Price', 'Link', 'Distance'))
        for e in document.xpath(suburb_expr):
            suburb_name = e.xpath(suburb_text_expr)[0].text
            for property_link in e.xpath(property_link_expr):
                bedroom = getXpath(property_link, bedroom_expr, 0.5)
                price_text = property_link.xpath(price_expr)[0]
                price = price_text[1:].replace(',','')
                href = property_link.xpath(href_expr)
                href = ('https://www.realestate.com.au' + href[0]) if len(href) > 0 else ''
                output.write(print_format.format(suburb_name,
                                                 property_link.xpath(address_expr)[0],
                                                 bedroom,
                                                 property_link.xpath(property_type_expr)[0],
                                                 price, href, distanceDict.get(suburb_name.upper(), 'un_known')))


# fully extract domain result page
def extract_domain_csv(distanceDict):
    url = 'https://www.domain.com.au/auction-results/sydney/'
    file_name = 'domain.html'
    url_retrieve(url, file_name)
    write_domain_csv(file_name, distanceDict)


# fully extract realestate result page
def extract_realestate_csv(distanceDict):
    url = 'https://www.realestate.com.au/auction-results/nsw'
    file_name = 'realestate.html'
    url_retrieve(url, file_name)
    write_realestate_csv(file_name, distanceDict)


def import_distance(filename):
    distance = {}
    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            distance[row[0].upper()] = row[2]
    return distance

# run both domain and realestate extraction
if __name__ == '__main__':
    distance = import_distance('distance.csv')
    extract_domain_csv(distance)
    extract_realestate_csv(distance)