import csv
import re
import os

from smartva.loggers import status_logger, warning_logger
from smartva.utils import status_notifier
from vaprep_data import (
    ADDITIONAL_HEADERS,
    SHORT_FORM_ADDITIONAL_HEADERS_DATA,
    BINARY_CONVERSION_MAP,
    AGE_HEADERS,
    ADULT_RASH_HEADER,
    ADULT_RASH_CONVERSION_HEADERS,
    ADULT_RASH_EVERYWHERE_LIST,
    ADULT_RASH_EVERYWHERE_VALUE,
    CHILD_WEIGHT_CONVERSION_DATA,
    FREE_TEXT_HEADERS,
    WORD_SUBS
)

ADULT = 'adult'
CHILD = 'child'
NEONATE = 'neonate'

PREPPED_FILENAME_TEMPLATE = '{:s}-prepped.csv'


def int_value(x):
    try:
        return int(x)
    except ValueError:
        return 0


class VaPrep(object):
    """
    This file cleans up input and converts from ODK collected data to VA variables.
    """

    def __init__(self, input_file, output_dir, short_form):
        self.input_file_path = input_file
        self.output_dir = output_dir
        self.short_form = short_form
        self.want_abort = False

        self._matrix_data = {
            ADULT: [],
            CHILD: [],
            NEONATE: []
        }

    @staticmethod
    def additional_headers_and_values(headers):
        additional_headers = ADDITIONAL_HEADERS
        additional_values = [0] * len(ADDITIONAL_HEADERS)
        for k, v in SHORT_FORM_ADDITIONAL_HEADERS_DATA:
            if k not in headers:
                additional_headers.append(k)
                additional_values.append(v)

        return additional_headers, additional_values

    def run(self):
        status_notifier.update({'progress': (1,)})

        status_logger.debug('Initial data prep')

        with open(self.input_file_path, 'rU') as f:
            reader = csv.reader(f)

            # Read headers and check for free text columns
            headers = next(reader)

            # Extend the headers with additional headers and read the remaining data into the matrix
            additional_headers, additional_values = self.additional_headers_and_values(headers)
            headers.extend(additional_headers)

            for row in reader:
                new_row = row + additional_values

                # Fill in blank values for age.
                # TODO: Eliminate this step in favor more robust future cell processing.
                for header in AGE_HEADERS.values():
                    new_row[headers.index(header)] = int_value(new_row[headers.index(header)])

                for header in BINARY_CONVERSION_MAP:
                    mapping = BINARY_CONVERSION_MAP[header]
                    try:
                        index = headers.index(header)
                    except ValueError:
                        # Header does not exist. Log a warning.
                        warning_logger.debug('Skipping missing header "{}".'.format(header))
                    else:
                        for value in new_row[index].split(' '):
                            try:
                                if int(value) in mapping:
                                    new_row[headers.index(mapping[int(value)])] |= 1
                            except ValueError:
                                # No values to process or not an integer value (invalid).
                                pass

                # set adultrash variables based on multiple choice question
                index = headers.index(ADULT_RASH_HEADER)
                try:
                    rash_values = list(map(int, new_row[index].split(' ')))
                except ValueError:
                    # No rash data. Skip.
                    pass
                else:
                    if set(ADULT_RASH_EVERYWHERE_LIST).issubset(set(rash_values)):
                        # if 1, 2, and 3 are selected, then change the value to 4 (all)
                        rash_values = [ADULT_RASH_EVERYWHERE_VALUE]
                    # set adultrash to the other selected values
                    for rash_index in range(min(len(rash_values), len(ADULT_RASH_CONVERSION_HEADERS))):
                        new_row[headers.index(ADULT_RASH_CONVERSION_HEADERS[rash_index])] = rash_values[rash_index]

                # Convert weights from kg to g
                for header in CHILD_WEIGHT_CONVERSION_DATA:
                    mapping = CHILD_WEIGHT_CONVERSION_DATA[header]
                    try:
                        units = int(new_row[headers.index(header)])
                    except ValueError:
                        # No weight data. Skip.
                        pass
                    else:
                        if units == 2:
                            weight = float(new_row[headers.index(mapping[units])]) * 1000
                            new_row[headers.index(header)] = 1
                            new_row[headers.index(mapping[1])] = weight

                # this just does a substitution of words in the above list (mostly misspellings, etc..)
                for question in FREE_TEXT_HEADERS:
                    try:
                        index = headers.index(question)
                    except ValueError:
                        warning_logger.debug('Free text column "{}" does not exist.'.format(question))
                    else:
                        # check to see if any of the keys exist in the freetext (keys can be multiple words like 'dog bite')
                        new_answer_array = []
                        for word in re.sub('[^a-z ]', '', new_row[index].lower()).split(' '):
                            if word in WORD_SUBS:
                                new_answer_array.append(WORD_SUBS[word])
                            elif word:
                                new_answer_array.append(word)

                        new_row[index] = ' '.join(new_answer_array)

                self.save_row(headers, new_row)

        self.write_data(headers, self._matrix_data, self.output_dir)

        return 1

    @staticmethod
    def get_age_data(headers, row):
        """
        Return age data in years, months, days, and module type.

        :param headers:
        :param row:
        :return: Age data in years, months, days, and module type.
        """
        age_data = {}
        for age, header in AGE_HEADERS.items():
            age_data[age] = int(row[headers.index(header)])

        return age_data

    @staticmethod
    def get_matrix(matrix_data, years=0, months=0, days=0, module=0):
        """
        Returns the appropriate age range matrix for extending.

        Adult = 12 years or older
        Child = 29 days to 12 years
        Neonate = 28 days or younger
        Module is used if age data are not used.

        :param matrix_data: Dictionary of age range matricies.
        :param years: Age in years
        :param months: Age in months
        :param days: Age in days
        :param module: Module, if specified
        :return: Specific age range matrix.
        :rtype : list
        """
        if years >= 12 or (not years and not months and not days and module == 3):
            return matrix_data[ADULT]
        if years or months or days >= 29 or (not years and not months and not days and module == 2):
            return matrix_data[CHILD]
        return matrix_data[NEONATE]

    def save_row(self, headers, row):
        """
        Save row of data in appropriate age matrix.

        :param headers:
        :param row:
        """
        self.get_matrix(self._matrix_data, **self.get_age_data(headers, row)).extend([row])

    @staticmethod
    def write_data(headers, matrix_data, output_dir):
        """
        Write intermediate prepped csv files.

        :param headers:
        """
        status_logger.debug('Writing adult, child, neonate prepped.csv files')

        for age, matrix in matrix_data.items():
            with open(os.path.join(output_dir, PREPPED_FILENAME_TEMPLATE.format(age)), 'wb', buffering=0) as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(matrix)

    def abort(self):
        self.want_abort = True
