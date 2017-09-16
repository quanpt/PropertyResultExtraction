import urllib.request
import time, base64, subprocess
from lxml import etree


# download the url
def url_retrieve(url, file_name):
    urllib.request.urlretrieve(url, file_name)


# extract data from domain page to csv
def write_domain_csv(file_name):
    suburb_expr = '//div[@class="suburb-listings" and descendant::h6[@class="suburb-listings__heading"]]'
    suburb_text_expr = './/h6[@class="suburb-listings__heading"]'
    property_link_expr = './/a[@class="auction-details"]'
    address_expr = './/span[@class="auction-details__address"]'
    bedroom_expr = './/span[@class="auction-details__bedroom"]'
    property_type_expr = './/span[@class="auction-details__property-type"]'
    price_expr = './/span[@class="auction-details__price"]'
    href_expr = './@href'
    print_format = '"{}"\t"{}"\t{}\t"{}"\t{}\t"{}"\n'

    html_parser = etree.HTMLParser(encoding='utf-8', recover=True,
                                   strip_cdata=True)
    document = etree.parse(file_name, html_parser)
    with open('domain_{}.csv'.format(time.strftime("%Y_%m_%d")), 'w') as output:
        output.write(print_format.format('Suburb', 'Address', 'Bedroom', 'Type', 'Price', 'Link'))
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
                                                 property_link.xpath(href_expr)[0]))


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


# extract data from realestate page to csv
def write_realestate_csv(file_name):
    suburb_expr = '//div[@class="rui-table-responsive suburb" and descendant::div[@class="col-suburb-name"]]'
    suburb_text_expr = './/div[@class="col-suburb-name"]'
    property_link_expr = './/tbody/tr'
    address_expr = '(.//a[@class="col-address"]/text() | .//div[@class="col-address"]/text())'
    bedroom_expr = './/div[@class="col-num-beds noscrape"]/img/@src'
    property_type_expr = './/div[@class="col-property-type"]/text()'
    price_expr = './/div[@class="col-property-price noscrape"]/img/@src'
    href_expr = './/a[@class="col-address"]/@href'
    print_format = '"{}","{}",{},"{}",{},"{}"\n'

    html_parser = etree.HTMLParser(encoding='utf-8', recover=True,
                                   strip_cdata=True)
    document = etree.parse(file_name, html_parser)
    with open('realestate_{}.csv'.format(time.strftime("%Y_%m_%d")), 'w') as output:
        output.write(print_format.format('Suburb', 'Address', 'Bedroom', 'Type', 'Price', 'Link'))
        for e in document.xpath(suburb_expr):
            suburb_name = e.xpath(suburb_text_expr)[0].text
            for property_link in e.xpath(property_link_expr):
                bedroom = img2room(property_link.xpath(bedroom_expr)[0])
                price_text = property_link.xpath(price_expr)[0]
                with open('tmp.png', 'wb') as f:
                    f.write(base64.b64decode(price_text[22:]))
                subprocess.run('/usr/bin/tesseract tmp.png tmp'.split(' '))
                with open('tmp.txt') as f:
                    price_text = f.readline()
                price = price_text[1:-1].replace(',','')[:-3]
                href = property_link.xpath(href_expr)
                href = ('https://www.realestate.com.au' + href[0]) if len(href) > 0 else ''
                output.write(print_format.format(suburb_name,
                                                 property_link.xpath(address_expr)[0],
                                                 bedroom,
                                                 property_link.xpath(property_type_expr)[0],
                                                 price, href))


# fully extract domain result page
def extract_domain_csv():
    url = 'https://www.domain.com.au/auction-results/sydney/'
    file_name = 'domain.html'
    url_retrieve(url, file_name)
    write_domain_csv(file_name)


# fully extract realestate result page
def extract_realestate_csv():
    url = 'https://www.realestate.com.au/auction-results/nsw'
    file_name = 'realestate.html'
    url_retrieve(url, file_name)
    write_realestate_csv(file_name)


# run both domain and realestate extraction
if __name__ == '__main__':
    extract_domain_csv()
    extract_realestate_csv()