#!/usr/bin/python
import os
import json
import math
import time

from tests import BaseUnitTestHelper
from uut.ingestion.elastic import ElasticIngestion
from uut.ingestion.exceptions import (ElasticIngestionDataValidationInvalidDataStructureElement,
                               ElasticIngestionDataValidationNoTimeElement,
                               ElasticIngestionDataValidationNoGameTimeElement)


class BaseElasticIngestionUnitTest(BaseUnitTestHelper):
    scenario = 'TEST'
    customer = 'unittest'

    def setUp(self):
        self.report_files = []

    def tearDown(self):
        if len(self.report_files):
            for rfile in self.report_files:
                rfile.close()

    @property
    def base_fixture_path(self):
        return os.path.join(self.base_path,
            'uut', 'fixtures', 'sample_reports')
    
    def get_sample_report(self, report_filename):
        report_file = open(os.path.join(self.base_fixture_path, report_filename), 'r')
        self.report_files.append(report_file)
        return report_file

    def get_elastic_instance(self, report_name):
        stats_list = json.load(self.get_sample_report(report_name))
        # get an instance of the elastic ingestion and attach a json object
        inst = ElasticIngestion(scenario=BaseElasticIngestionUnitTest.scenario,
                                customer=BaseElasticIngestionUnitTest.customer)
        inst.data = stats_list
        inst.validate_data()
        return inst


class TestElasticIngestion(BaseElasticIngestionUnitTest):
    def test_batch_elk_data(self):
        batch_size = 100
        inst = self.get_elastic_instance('sample_AEB_10_0_CCRS_Collision.json')

        expected_buckets = math.ceil(len(inst.data) / batch_size)
        batches = inst.batch_elk_data(batch_size=batch_size)

        print('\n Testing batching routine')
        self.assertEqual(len(batches), expected_buckets)
        self.assertEqual(len(batches[0]), batch_size)

    def test_build_elk_request(self):
        inst = self.get_elastic_instance('sample_AEB_10_0_CCRS_Collision.json')
        # get the batches and run one through the elk_request build
        batches = inst.batch_elk_data(batch_size=100)
        base_time = time.time()
        request = inst.build_elk_request(base_time, batches[0], 0)

        self.assertEqual(request.tell(), 0)  # file pointer should be at 0

        # now we are gonna read the file and extract the json objects
        file_contents = []
        last_line = None
        for line in request.readlines():
            line = line.decode()
            if line != '\n':
                file_contents.append(json.loads(line))
            last_line = line  # cache the last line in the file

        # kibana expects a new line at the end of the file
        print('\n Testing the ELK BULK POST body routine')
        self.assertTrue(last_line == '\n')

        # when inserting to elk each record must be prepended with an object that designates the index
        self.assertTrue('create' in file_contents[0])
        self.assertTrue('report' in file_contents[0]['create']['_index'])
        self.assertTrue('_doc' in file_contents[0]['create']['_type'])

        # check to ensure the first item in the request matches the first item in the batch
        self.assertEqual(file_contents[1]['result'], batches[0][0])
        self.assertEqual(file_contents[1]['step'], 0)
        self.assertEqual(file_contents[-1]['step'], len(batches[0]) - 1)
        self.assertEqual(file_contents[1]['fps_timestamp'], base_time*1000)
        self.assertEqual(file_contents[-1]['fps_timestamp'],
            (base_time + ((inst.fps / 60) * (len(batches[0])-1)))*1000)

    def test_validate_data_invalid_data_structure(self):
        bad_data_structure = [[{'key':'value'}]]
        print('\n Testing the data validation structure error')
        with self.assertRaises(ElasticIngestionDataValidationInvalidDataStructureElement):
            inst = ElasticIngestion()
            inst.data = bad_data_structure
            inst.validate_data()

    def test_validate_data_no_time(self):
        bad_data_structure = [{'key':'value'}]
        print('\n Testing the data validation with no time error')
        with self.assertRaises(ElasticIngestionDataValidationNoTimeElement):
            inst = ElasticIngestion()
            inst.data = bad_data_structure
            inst.validate_data()

    def test_validate_data_no_game_time(self):
        bad_data_structure = [{'time':12341234}]
        print('\n Testing the data validation no game time error')
        with self.assertRaises(ElasticIngestionDataValidationNoGameTimeElement):
            inst = ElasticIngestion()
            inst.data = bad_data_structure
            inst.validate_data()
