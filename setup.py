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


""" Setup script to deploy the WebDAV client library. """


from ConfigParser import ConfigParser
from distutils import core
import os
import shutil
import subprocess
import sys


__version__ = "$LastChangedRevision$"


class _BaseCommandRunner(core.Command):
    """ Base class for encapsulating command line commands. """
    
    def run(self):
        self._create_build_dir()
        command = self._create_command()
        self._run_command(command)
        self._perform_post_actions()
    
    @staticmethod
    def _create_build_dir():
        if not os.path.exists("build"):
            os.mkdir("build")

    def _create_command(self):
        pass
    
    def _run_command(self, command):
        if self.verbose:
            print(command)
        subprocess.call(command, shell=True)
    
    def _perform_post_actions(self):
        pass


class pylint(_BaseCommandRunner):
    """ Runs the pylint command. """

    description = "Runs the pylint command."
    user_options = [
        ("command=", None, "Path and name of the command line tool."),
        ("out=", None, "Specifies the output type (html, parseable). Default: html")]

    def initialize_options(self):
        self.command = "pylint"
        if sys.platform == "win32":
            self.command += ".bat"
        self.out = "html"
        self.output_file_path = "build/pylint.html"

    def finalize_options(self):
        self.verbose = self.distribution.verbose
        if self.out == "parseable":
            self.output_file_path = "build/pylint.txt"

    def _create_command(self):
        testScripts = list()
        for fileName in os.listdir("tests"):
            if fileName.endswith(".py"):
                testScripts.append(os.path.join("tests", fileName))
        return (
            "%s --rcfile=dev/pylintrc --output-format=%s src/webdav %s > %s"
            % (self.command, self.out, " ".join(testScripts), self.output_file_path))

    def _perform_post_actions(self):
        if self.out == "parseable" and sys.platform == "win32":
            try:
                file_object = open(self.output_file_path, "rb")
                content = file_object.read().replace("\\", "/")
            finally:
                file_object.close()
            try:
                file_object = open(self.output_file_path, "wb")
                file_object.write(content)
            finally:
                file_object.close()


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
_licenseFileName = _configParser.get(_globalConfigurationCategory, "license_file_name")
_changesFileName = _configParser.get(_globalConfigurationCategory, "changes_file_name")


def _createManifestTemplate(licenseFileName, changesFileName):
    """ Handles the creation of the manifest template file. """
    
    manifestTemplateFileName = "MANIFEST.in"
    if not os.path.exists(manifestTemplateFileName):
        try:
            fileHandle = open(manifestTemplateFileName, "wb")
            fileHandle.write("include %s\n" % licenseFileName)
            fileHandle.write("include %s" % changesFileName)
            fileHandle.close()
        except IOError:
            print("Cannot create manifest template file.")
            sys.exit(-1)


def _set_pythonpath():
    python_path = [os.path.realpath(path) for path in ["src"]]
    python_path = os.pathsep.join(python_path) + os.pathsep + os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = python_path


def performSetup():
    """ Main method of the setup script. """
    
    if os.path.exists("./lib"):
        shutil.copy("./lib/qp_xml.py", "./src")
        shutil.copy("./lib/davlib.py", "./src")
        shutil.copy("./lib/uuid_.py", "./src")
    
    _set_pythonpath()
    _createManifestTemplate(_licenseFileName, _changesFileName)
    
    core.setup(name=_name,
        version=_version,
        description = _description,
        long_description = _longDescription,
        author = _author,
        author_email = _authorEmail,
        maintainer = _maintainer,
        maintainer_email = _maintainerEmail,
        url = _url,
        py_modules = ["qp_xml", "davlib", "uuid_"],
        package_dir={"":"src"},
        packages = ["webdav", "webdav.acp"],
        cmdclass={"pylint": pylint})


performSetup()
