# pylint: disable-msg=C0121,C0322,C0323,C0103,W0622,R0904,W0141,W0142,W0621,E0501
#
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
 


""" A test case that is REALLY required to be refactored. """ 
 

import unittest
import sys
import getopt
import traceback
import codecs
from os.path import basename

from webdav import WebdavClient


HELP_TEXT = '''
Test WebDAV unicode features with WebDAV client.
\nUsage:\tUnicodeTest.py [-h] [url [user password]]
\t-h[elp] : Show this text.
'''

url= "http://bsasdf01.as.bs.dlr.de/taminowebdavserver/datafinder/test/SISTEC/rbetz/unittest/"
user= "tamino user"
password= "tamino"

        
class UnicodeTestCase(unittest.TestCase):
    connection = None
    
    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        print "init URL=", url
        self.resource = WebdavClient.CollectionStorer(url, UnicodeTestCase.connection)
        if not UnicodeTestCase.connection:
            UnicodeTestCase.connection= self.resource.connection
        if user:
            print "User", user, "Password:", password
            self.resource.connection.addBasicAuthorization(user, password)
        davOpt = self.resource.davOptions()
        if davOpt.find("slide") < 0:    # is this a Tamino server ?
            self.resource.connection.TAMINO_URL_ENCODE_BUG= 0
            
    def setUp(self):
        pass



    # The two main test methods
    
    def setAndCheckProperty(self, name, value):
        try:
            self.resource.writeProperties({ ('none:', name) : value})
            returned= self.resource.readProperty('none:', name).textof()
            print "Property value:", repr(returned)
            if type(value) != type(u""):
                value= unicode(value, 'latin-1')
            self.failUnlessEqual(returned, value, "Wrong value %s" % repr(returned))
        except WebdavClient.WebdavError, e:
            print e
            self.fail(str(e))

            
    def createAndCheckResource(self, name):
        try:
            try:
                result= self.resource.listResources()
                print "Resources found:", result.keys()
                self.failUnless(_findin(name, result.keys()), "No resource %s found." % repr(name))
            finally:
                self.resource.deleteResource(name)    # clean up server data
        except WebdavClient.WebdavError, e:
            print e
            traceback.print_tb(sys.exc_info()[2])
            self.fail(str(e))
            
    def copyAndCheckResource(self, targetName):
        try:
            name= "UnicodeTest_ö.txt"
            child= self.resource.addResource(name, "Binary Content", None)
            targetUrl= self.resource.url + targetName
            targetPath= targetUrl[len(str(self.resource.connection)):]
            print "Target path:", repr(targetPath)
            try:
                child.copy(targetUrl)
            except:
                self.resource.deleteResource(name)    # clean up server data
                raise
            try:
                result= self.resource.listResources()
                print "Resources found:", result.keys()
                self.failUnless(_findin(targetPath, result.keys()), "No resource %s found." % repr(name))
            finally:
                self.resource.deleteResource(name)    # clean up server data
                self.resource.deleteResource(basename(targetUrl))    # clean up server data
        except WebdavClient.WebdavError, e:
            print e
            traceback.print_tb(sys.exc_info()[2])
            self.fail(str(e))
            
    def moveAndCheckResource(self, targetName):
        try:
            name= "UnicodeTest.txt"
            child= self.resource.addResource(name, "Binary Content", None)
            targetUrl= self.resource.url + targetName
            targetPath= targetUrl[len(str(self.resource.connection)):]
            print "Target path:", repr(targetPath)
            try:
                child.move(targetUrl)
            except:
                self.resource.deleteResource(name)    # clean up server data
                raise
            try:
                result= self.resource.listResources()
                print "Resources found:", result.keys()
                self.failUnless(_findin(targetPath, result.keys()), "No resource %s found." % repr(name))
            finally:
                self.resource.deleteResource(basename(targetUrl))    # clean up server data
        except WebdavClient.WebdavError, e:
            print e
            traceback.print_tb(sys.exc_info()[2])
            self.fail(str(e))
            

    # Test special resource names
    
    def testCreateWithLatin(self):
        print "\nTest CreateWithLatin"
        self.createAndCheckResource("Größte")
 
    def testCreateWithUtf(self):
        print "\nTest CreateWithUtf"
        self.createAndCheckResource(u"Größte")

    def testCreateWithSeparator(self):
        print "\nTest CreateWithSeparator"
        self.createAndCheckResource("!~one_two-three.four five:six$seven")

    def testCopyWithUtf(self):
        print "\nTest CopyWithUtf"
        self.copyAndCheckResource(u"Größte")

    def testCopyWithLatin(self):
        print "\nTest CopyWithLatin"
        self.copyAndCheckResource("Größte")
 
    def testCopyWithSeparator(self):
        print "\nTest CopyWithSeparator"
        self.copyAndCheckResource("!~one_two-three.four five:six$seven")

    def testMoveWithUtf(self):
        print "\nTest MoveWithUtf"
        self.moveAndCheckResource(u"Größte")

    def testMoveWithLatin(self):
        print "\nTest MoveWithLatin"
        self.moveAndCheckResource("Größte")
 

    # Test illegal resource names
    
    def testCreateWithPercent(self):
        print "\nTest CreateWithPercent"
        self.failUnlessRaises(ValueError, self.resource.addResource, 
            "one_two-three.four five:six%seven", "Binary Content")

    def testCreateWithQuestion(self):
        print "\nTest CreateWithQuestion"
        self.failUnlessRaises(ValueError, self.resource.addResource, 
            "one_two-three.four five:six?seven", "Binary Content")

    def testCreateWithHash(self):
        print "\nTest CreateWithHash"
        self.failUnlessRaises(ValueError, self.resource.addResource, 
            "one_two-three.four five:six#seven", "Binary Content")


    # Test special property names
    
    def testPropertyLatinName(self):
        print "\nTest PropertyLatinName"
        self.setAndCheckProperty("Größe", "leer")

    def testPropertyUtfName(self):
        print "\nTest PropertyUtfName"
        self.setAndCheckProperty(u"Größe", "leer")

    def testPropertySeparatedName(self):
        print "\nTest PropertySeparatedName"
        self.setAndCheckProperty("one_two-three.four", "leer")

    # Test illegal property names
    
    def testPropertyNameWithColon(self):
        print "\nTest PropertyNameWithColon"
        self.failUnlessRaises(ValueError, self.resource.writeProperties, 
            { ('none:', "one_two-three:four") : "value"} )
      

    # Test special property values
    
    def testPropertyLatinValue(self):
        print "\nTest PropertyLatinValue"
        self.setAndCheckProperty("property", "Größe")

    def testPropertyBracedValue(self):
        print "\nTest PropertyBracedValue"
        self.setAndCheckProperty("property", "<> . & # ;")

    def testPropertyUtfValue(self):
        print "\nTest PropertyUtfValue"
        self.setAndCheckProperty("property", u"Größe")

    
    # Test unicode resource values

    def testResourceValueUtf(self):
        print "\nTest ResourceValueUtf"
        name= 'resource.dat'
        utf_reader= codecs.lookup('utf-8')[2]
        latin_writer= codecs.lookup('latin-1')[3]
        try:
            child= self.resource.addResource(name, u"Größe")
            try:
                file= child.downloadContent()
                text= utf_reader(file).read()
                print >>latin_writer(sys.stdout), "Text:", text
                self.failUnlessEqual(text, u"Größe", "Wrong value %s" % repr(text))               
            finally:
                self.resource.deleteResource(name)    # clean up server data
        except WebdavClient.WebdavError, e:
            print e
            traceback.print_tb(sys.exc_info()[2])
            self.fail(str(e))
        

class UnicodeResourceSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, \
            map(UnicodeTestCase, ("testCreateWithLatin", "testCreateWithUtf", "testCreateWithSeparator",
                "testCreateWithPercent", "testCreateWithQuestion", "testCreateWithHash",
                "testResourceValueUtf", "testCopyWithUtf", "testCopyWithLatin", "testCopyWithSeparator")))

class UnicodePropertySuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, \
            map(UnicodeTestCase, ("testPropertyLatinName", "testPropertyUtfName", "testPropertySeparatedName",
                "testPropertyNameWithColon", "testPropertyLatinValue", "testPropertyBracedValue",)))

class UnicodeTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, (UnicodeResourceSuite(), UnicodePropertySuite()))

        
def _findin(name, vector):
    if  type(name) != type(u'1'):
        name= unicode(name, 'latin-1')
    return filter(lambda n: n.endswith(name), vector)


if  __name__ == '__main__':
    try:
        options, params= getopt.getopt(sys.argv[1:], "hp:")
    except getopt.GetoptError, e:
        print e
        sys.exit(1)	
    print options, params
    if len(params) > 0:
        url= params[0]
    if len(params) > 2:
        user= params[1]
        password= params[2]
    print url, user, password
    unittest.TextTestRunner().run(UnicodeTestSuite())
