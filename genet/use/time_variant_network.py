import logging
import os
import re

from lxml import etree
import xml.etree.cElementTree as ET


def read_network_change_events_xml(path):
    change_events = {}
    ch_event = {'links': set()}
    for event, elem in ET.iterparse(path):
        tag = re.sub(r'{http://www\.matsim\.org/files/dtd}', '', elem.tag)  # noqa: W605
        if tag == 'link':
            ch_event['links'].add(elem.attrib['refId'])
        elif tag == 'networkChangeEvent':
            change_events[elem.attrib['startTime']] = ch_event
            ch_event = {'links': set()}
        else:
            ch_event[tag] = elem.attrib
    return change_events


def write_network_change_events_xml(change_events, output_dir, fname='networkChangeEvents.xml'):
    fpath = os.path.join(output_dir, fname)
    logging.info('Writing {}'.format(fpath))

    with open(fpath, "wb") as f, etree.xmlfile(f, encoding='utf-8') as xf:
        xf.write_declaration()
        networkChangeEvents_attribs = {
            'xmlns': "http://www.matsim.org/files/dtd",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'xsi:schemaLocation': "http://www.matsim.org/files/dtd "
                                  "http://www.matsim.org/files/dtd/networkChangeEvents.xsd"}
        with xf.element("networkChangeEvents", networkChangeEvents_attribs):
            for event_time, change_event in change_events.items():
                with xf.element("networkChangeEvent", {'startTime': event_time}):
                    for link in change_event['links']:
                        xf.write(etree.Element("link", {'refId': link}))
                    xf.write(etree.Element("flowCapacity", change_event['flowCapacity']))
                    xf.write(etree.Element("freespeed", change_event['freespeed']))
                    xf.write(etree.Element("lanes", change_event['lanes']))
