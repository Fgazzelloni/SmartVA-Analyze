import csv
import pytest

from smartva.adult_symptom_prep import AdultSymptomPrep
from smartva.data.adult_symptom_data import DEFAULT_AGE

headers = ['sid']
headers.extend(['a4_06']) # alcohol amount
headers.extend(['a2_63_1'])
headers.extend(['g5_04a'])
data = [
    {'sid': 'lower_belly_pain', 'a2_63_1': '2'},
    {'sid': 'heavy_alcohol', 'a4_06': '3'},
    {'sid': 'age_group', 'g5_04a': 0},
]

expected_results = [
    {'sid': 'lower_belly_pain',  's82991' : '1'},
    {'sid': 'heavy_alcohol', 's150992': '1'},
    {'sid': 'age_group', 'real_age': str(DEFAULT_AGE)},
]


@pytest.fixture
def input_file(tmpdir):
    f_path = tmpdir.mkdir('intermediate-files').join('adult-logic-rules.csv')
    with f_path.open('wb') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(data)
    return f_path


@pytest.fixture
def output_file(tmpdir):
    f_path = tmpdir.join('intermediate-files', 'adult-symptom.csv')
    return f_path


@pytest.fixture
def prep(tmpdir):
    return AdultSymptomPrep(tmpdir.strpath, True)


class TestAdultSymptomPrep(object):
    def test_input_data(self, prep, input_file, output_file):
        print(input_file)
        prep.run()
        assert output_file.check()
        with output_file.open('rb') as f:
            r = csv.DictReader(f)
            matrix = [row for row in r]

        self.validate_matrix(iter(matrix), iter(expected_results))

    def validate_matrix(self, t_matrix, v_matrix):
        for t in t_matrix:
            v = v_matrix.next()
            for var in v:
                assert t[var] == v[var], "SID: '{}' does not produce expected result".format(t['sid'])
