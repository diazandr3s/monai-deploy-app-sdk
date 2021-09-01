# Copyright 2020 - 2021 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .domain import Domain


class DICOMStudy(Domain):
    """This class represents a DICOM Study.

    It contains a collection of DICOM Studies.
    """

    def __init__(self, study_instance_uid):
        super().__init__(None)
        self._study_instance_uid = study_instance_uid
        self._series_dict = {}

    def get_study_instance_uid(self):
        return self._study_instance_uid

    def add_series(self, series):
        self._series_dict[series.get_series_instance_uid()] = series

    def get_all_series(self):
        return list(self._series_dict.values())

    @property
    def study_id(self):
        return self.__study_id

    @study_id.setter
    def study_id(self, val):
        self.__study_id = val

    @property
    def study_date(self):
        return self.__study_date

    @study_date.setter
    def study_date(self, val):
        self.__study_date = val

    @property
    def study_time(self):
        return self.__study_time

    @study_time.setter
    def study_time(self, val):
        self.__study_time = val

    @property
    def study_description(self):
        return self.__study_description

    @study_description.setter
    def study_description(self, val):
        self.__study_description = val

    @property
    def accession_number(self):
        return self.__accession_number

    @accession_number.setter
    def accession_number(self, val):
        self.__accession_number = val

    def __str__(self):
        result = "---------------" + "\n"

        study_instance_uid_attr = "Study Instance UID: " + self._study_instance_uid + "\n"
        result += study_instance_uid_attr

        study_id_attr = "Study ID: " + self.study_id + "\n"
        result += study_id_attr

        study_date_attr = "Study Date: " + self.study_date + "\n"
        result += study_date_attr

        study_time_attr = "Study Time: " + self.study_time + "\n"
        result += study_time_attr

        study_desc_attr = "Study Description: " + self.study_description + "\n"
        result += study_desc_attr

        accession_num_attr = "Accession Number: " + self.accession_number + "\n"
        result += accession_num_attr

        result += "---------------" + "\n"

        return result
