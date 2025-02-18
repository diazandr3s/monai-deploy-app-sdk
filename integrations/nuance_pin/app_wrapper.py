"""
Copyright (c) 2021 Nuance Communications, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This module exists to isolate logging configuration in a separate name space
This allows these values to be updated completely independent of any other
values in this package

This is an example AI Service.

It meets all of the necessary requirements, but performs trivial actions.
"""

# Copyright 2022 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from importlib import import_module
from typing import List

import pydicom
from ai_service import AiJobProcessor, AiService, Series
from result import ResultStatus


class MONAIAppWrapper(AiJobProcessor):

    partner_name = os.environ["AI_PARTNER_NAME"]
    service_name = os.environ["AI_SVC_NAME"]
    service_version = os.environ["AI_SVC_VERSION"]

    monai_app_module = os.environ["MONAI_APP_CLASSPATH"]

    def filter_image(self, image: pydicom.Dataset) -> bool:
        return True

    def select_series(self, image_series_list: List[Series]) -> List[Series]:
        return image_series_list

    @classmethod
    def initialize_class(cls):
        cls.model_path = os.getenv("AI_MODEL_PATH", "/app/model/model.ts")
        if not os.path.exists(cls.model_path):
            raise FileNotFoundError(f"Could not find model file in path `{cls.model_path}`")
        cls.logger.info(f"Model path: {cls.model_path}")

        monai_app_class_module = cls.monai_app_module.rsplit(".", 1)[0]
        monai_app_class_name = cls.monai_app_module.rsplit(".", 1)[1]
        if not cls.monai_app_module:
            raise ValueError(
                "MONAI App to be run has not been specificed in `MONAI_APP_CLASSPATH` environment variable"
            )

        monai_app_class = getattr(import_module(monai_app_class_module), monai_app_class_name)
        if monai_app_class is None:
            raise ModuleNotFoundError(f"The class `{cls.monai_app_module}` was not found")

    def process_study(self):
        self.logger.info("Starting Processing")
        self.logger.info(f"{len(self.ai_job.prior_studies)} images in prior studies")

        if not hasattr(MONAIAppWrapper, "input_path") or self.input_path is None:
            self.input_path = self.ai_job.image_folder
            self.logger.info(f"Input path: {self.input_path}")

        if not hasattr(MONAIAppWrapper, "output_path") or self.output_path is None:
            self.output_path = self.ai_job.output_folder
            self.logger.info(f"Output path: {self.output_path}")

        # create the inference app instance to run on this subprocess
        self.logger.info("Running MONAI App")

        if not hasattr(MONAIAppWrapper, "monai_app_instance") or self.monai_app_instance is None:
            monai_app_class_module = self.monai_app_module.rsplit(".", 1)[0]
            monai_app_class_name = self.monai_app_module.rsplit(".", 1)[1]
            monai_app_class = getattr(import_module(monai_app_class_module), monai_app_class_name)
            self.monai_app_instance = monai_app_class(
                do_run=False, upload_document=self.upload_document, upload_gsps=self.upload_gsps_dicom
            )

        self.logger.info(f"MONAI App Info: {self.monai_app_instance.get_package_info()}")
        self.logger.info(f"MONAI working directory: {self.ai_job.folder}")

        self.monai_app_instance.run(
            log_level=self.logger.level,
            input=self.input_path,
            output=self.output_path,
            model=self.model_path,
            workdir=self.ai_job.folder,
        )

        self.logger.info("MONAI App complete")

        self.set_transaction_status(reason=ResultStatus.ANALYSIS_COMPLETE)


if __name__ == "__main__":
    AiService(MONAIAppWrapper).start()
