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


BASE_URL= "http://jotuns:8080/rbetz/test"

class LongPropTest(unittest.TestCase):
    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self.url= BASE_URL
        if  len(sys.argv) > 1:
            self.url= sys.argv[1]
        print "init ", self.url
        self.resource= WebdavClient.CollectionStorer(self.url)
    
    def setUp(self):
        pass
        
               
    def testAddProperty(self):
        print "\nTest AddProperty"
        value= 'a'*5000
        self.resource.writeProperties({('TENT:', 'long') : value})
        try: 
            #properties= self.resource.readProperties(('TENT:', 'long'))
            #self.assertEqual(len(properties), 1, "Returned %d properties." % len(properties))
            #gotValue= properties.get(('TENT:', 'long'))
            gotValue= self.resource.readProperty('TENT:', 'long')
            self.assertEqual(str(gotValue), value, "Wrong property value: %s/%s" % (
                                                        type(gotValue), gotValue))
        finally: pass
            #self.resource.deleteProperties(None, ('TENT:', 'long'))  # clean up meta data
    
    
if  __name__ == '__main__':
    unittest.main()
