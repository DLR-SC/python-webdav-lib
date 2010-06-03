# Copyright 2008 German Aerospace Center (DLR)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.""" Setup script for the DataFinder project. """


""" Setup script to deply the WebDAV client library. """


import shutil
import os
from ConfigParser import ConfigParser
from distutils.core import setup


__version__ = "$LastChangedRevision$"


_configParser = ConfigParser()
_configParser.read("setup.cfg")


_globalConfigurationCategory = "global"
_listSeparator = ";"

_name = _configParser.get(_globalConfigurationCategory, "name")
_version = _configParser.get(_globalConfigurationCategory, "version")
_description = _configParser.get(_globalConfigurationCategory, "description")
_longDescription = _configParser.get(_globalConfigurationCategory, "longDescription")
_author = _configParser.get(_globalConfigurationCategory, "author")
_authorEmail = _configParser.get(_globalConfigurationCategory, "authorEmail")
_maintainer = _configParser.get(_globalConfigurationCategory, "maintainer")
_maintainerEmail = _configParser.get("global", "maintainerEmail")
_url = _configParser.get(_globalConfigurationCategory, "url")

if os.path.exists("./lib"):
    shutil.copy("./lib/qp_xml.py", "./src")
    shutil.copy("./lib/davlib.py", "./src")

setup(name=_name,
      version=_version,
      description = _description,
      long_description = _longDescription,
      author = _author,
      author_email = _authorEmail,
      maintainer = _maintainer,
      maintainer_email = _maintainerEmail,
      url = _url,
      py_modules = ["qp_xml", "davlib"],
      package_dir={"":"src"},
      packages = ["webdav", "webdav.acp"])
