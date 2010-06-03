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
# limitations under the License.
 
 
import unittest
import sys

from webdav import WebdavClient


URL= "http://buri/taminowebdavserver/datafinder/"
USER= "tamino user"


class AutentificationTestCase(unittest.TestCase):
    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        if  len(sys.argv) > 1:
            self.url= URL
            self.username= USER
            self.password= sys.argv[1]
            print "Password ", self.password
        else:
            print "Usage %s password" % sys.argv[0]
            sys.exit(1)
        self.resource= None
    
    def setUp(self):
        self.resource= WebdavClient.CollectionStorer(self.url)
        self.resource.connection.addBasicAuthorization(self.username, self.password)
                        
    def testListResources(self):
        print "\nTest listResources"
        result= self.resource.listResources()
        print "Resources: ", result.keys()
        print "Live properties: ", result.values()[0]
        if len(result) == 0:
            self.fail("Collection contains %d items." % len(result))
        self.failUnless(result.keys()[0].find('Hallo.txt'), "No resource Hello.txt found.")
    
    def runTest(self):
        self.testListResources();
        
if  __name__ == '__main__':
    unittest.TextTestRunner().run(AutentificationTestCase())
