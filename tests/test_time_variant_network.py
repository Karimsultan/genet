import os

import lxml
import pytest
from genet.use import time_variant_network
from lxml.etree import Element
from tests.fixtures import *

# paths in use assume we're in the repo's root, so make sure we always are
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(root_dir)


@pytest.fixture
def network_change_events_schema():
    xsd_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "test_data", "dtd", "matsim", "networkChangeEvents.xsd"))

    xml_schema_doc = lxml.etree.parse(xsd_path)
    yield lxml.etree.XMLSchema(xml_schema_doc)


@pytest.fixture
def network_change_events_example_path():
    sample_xml_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   "test_data/network_change_events/networkChangeEvents.xml"))
    yield sample_xml_path


@pytest.fixture
def network_change_events_dict():
    return {'06:00:00': {'links': {'3', '1', '2'}, 'freespeed': {'type': 'absolute', 'value': '1.0'},
                         'lanes': {'type': 'absolute', 'value': '2.0'},
                         'flowCapacity': {'type': 'scaleFactor', 'value': '2'}},
            '9:00:00': {'links': {'3', '1', '2'}, 'lanes': {'type': 'absolute', 'value': '1.0'},
                        'freespeed': {'type': 'absolute', 'value': '10.0'},
                        'flowCapacity': {'type': 'scaleFactor', 'value': '0.5'}}}


def test_reading_xml(network_change_events_example_path, network_change_events_dict):
    ch_events = time_variant_network.read_network_change_events_xml(network_change_events_example_path)
    assert_semantically_equal(ch_events, network_change_events_dict)


def test_writes_well_formed_and_valid_network_change_events_xml_file(tmpdir, network_change_events_schema, network_change_events_dict):
    fname = 'net_change_evs.xml'
    expected_xml = os.path.join(tmpdir, fname)
    time_variant_network.write_network_change_events_xml(network_change_events_dict, tmpdir, fname=fname)

    xml_obj = lxml.etree.parse(expected_xml)
    assert network_change_events_schema.assertValid(
        xml_obj), f'Doc generated at {expected_xml} is not valid against ' \
                  f'XSD due to {network_change_events_schema.error_log.filter_from_errors()}'


def test_saving_network_change_events_to_xml_produces_xml_file(network_change_events_dict, tmpdir):
    # the content of the file is tested elsewhere
    fname = 'net_change_evs.xml'
    expected_xml = os.path.join(tmpdir, fname)
    assert not os.path.exists(expected_xml)

    time_variant_network.write_network_change_events_xml(network_change_events_dict, tmpdir, fname=fname)
    assert os.path.exists(expected_xml)



def test_saving_network_change_events_to_xml_produces_correct_xml_content(network_change_events_dict, tmpdir):
    fname = 'net_change_evs.xml'
    expected_xml = os.path.join(tmpdir, fname)

    time_variant_network.write_network_change_events_xml(network_change_events_dict, tmpdir, fname=fname)
    events_from_file = time_variant_network.read_network_change_events_xml(expected_xml)

    assert_semantically_equal(events_from_file, network_change_events_dict)

