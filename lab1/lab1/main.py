import os
from scrapy import cmdline
from lxml import etree

def posts_analysis():
    url_list = []
    pages_count = 0
    root = etree.parse("res/posts.xml")
    for page in root.iterfind(".//item"):
        pages_count += 1
        for child in page:
            if child.tag == "url":
                url_list.append(child.text)
                break

    if pages_count != 0:
        for _idx, _child in enumerate(url_list):
            print('{1}'.format(
                _idx,
                _child
            ))
    else:
        print("XML tree is empty")

posts_analysis()

def products_to_xhtml():
    dom = etree.parse("res/products.xml")
    xslt = etree.parse("script/products.xsl")
    transform = etree.XSLT(xslt)
    result = transform(dom)
    result.write_output("res/products.html")

products_to_xhtml()