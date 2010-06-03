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
 

""" Has to be refactored. """


import unittest
import sys
import filecmp  # cmp
import os       # remove
import getopt

from webdav.WebdavResponse import PropertyResponse
from webdav import WebdavClient


HELP_TEXT= '''
Test WebDAV extension features with WebDAV client.
\nUsage:\ClientTestCase.py [-vm] [url [user password]]
\t-h[elp] : Show this text.
\t-v[erbose] : Show debug information
\t-m[ethods] test1,test2,... : colon separated list of test methods, default: all.
'''

url= "http://jotuns:8080/rbetz/test/"
user= ""
password= ""


class ClientTestCase(unittest.TestCase):
    connection= None
    
    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self.url= url
        print "init ", self.url
        self.resource= WebdavClient.CollectionStorer(self.url, ClientTestCase.connection)
        if not ClientTestCase.connection:
            ClientTestCase.connection= self.resource.connection
        if  len(user) > 0:
            self.resource.connection.addBasicAuthorization(user, password)
            
    def setUp(self):
        pass
        
    def testValidate(self):
        print "\nTest validate"
        self.resource.validate()        
        
    def testReadAll(self):
        print "\nTest readAll"
        result= self.resource.readAllProperties()
        print "All properties of test/:\n", str(result)
        self.failUnless(isinstance(result, PropertyResponse),
                        'Wrong result class ' + str(type(result)))
        self.failUnless(result.has_key(('DAV:', 'resourcetype')), "Has no resource type")
        resourceType= result[('DAV:', 'resourcetype')]
        self.failUnless(resourceType.find('collection', 'DAV:'), "is not collection")
                
    def testListResources(self):
        print "\nTest listResources"
        result= self.resource.listResources()
        print "Resources: ", result.keys()
        print "Live properties: ", result.values()[0]
        if len(result) == 0:
            self.fail("Collection contains %d items." % len(result))
        self.failUnless(result.keys()[0].find('Hallo.txt') >= 0, "No resource 'Hallo.txt' found.")
        
    def testMissingProperty(self):
        print "\nTest MissingProperty"
        try: 
            self.resource.readProperty('TENT:', 'does_not_exist')
            self.fail("No exception has been raise.")
        except WebdavClient.WebdavError, e:
            print "Expected Error: ", e
            self.failUnlessEqual(e.code, 404, "Wrong eror code.")
            
        
        
    def testCreateCollection(self):
        print "\nTest CreateCollection"
        child= self.resource.addCollection("new");
        try:
            #map= self.resource.readAllProperties()
            result= self.resource.findProperties(('DAV:', 'getcontentlength'))
            print "Path:", child.path
            ## some servers do not append a trailing slash to collection paths
            self.failUnless(result.has_key(child.path) or result.has_key(child.path[0:-1]), \
                "No new collection " + child.path)
        finally:
            self.resource.deleteResource("new")     # clean up server data
        
        
    def testAddProperty(self):
        print "\nTest AddProperty"
        self.resource.writeProperties({('TENT:', 'features') : "X4711"})
        try: 
            value= self.resource.readProperty('TENT:', 'features')
            self.assertEqual(str(value), "X4711", "Wrong property value: %s/%s" % (type(value), value))
        finally:
            self.resource.deleteProperties(None, ('TENT:', 'features'))  # clean up meta data

    def testCreateResource(self):
        print "\nTest CreateResource"
        child= self.resource.addResource("new", "Binary Content", {('TENT:', 'feature') : "X4711"});

        try:
            value= child.readProperty('TENT:', 'feature')
            self.assertEqual(str(value), "X4711", "Wrong property value " + str(value))

            file= child.downloadContent()
            text= file.read()
            self.assertEqual(text, "Binary Content", "Wrong content " + text)
        finally:
            self.resource.deleteResource("new")    # clean up server data
        
    def testUploadResource(self):
        print "\nTest UploadResource"
        # Create File
        dataFile= open('testFile.txt', 'w')
        dataFile.write("abc"*1000)
        dataFile.close()
        dataFile= open('testFile.txt')
        # Create empty resource
        child= self.resource.addResource("new");
        try:
            try:
                child.uploadFile(dataFile)
                dataFile.close()
                child.downloadFile('resultFile.txt')
                self.failUnless(filecmp.cmp('testFile.txt', 'resultFile.txt'), "Download data differs")
            except Exception, e:
                print e
                raise e
        finally:
            self.resource.deleteResource("new")    # clean up server data
            os.remove('testFile.txt')
            os.remove('resultFile.txt')
        
    def testLock(self):
        print "\nTest Lock"
        child= self.resource.addResource("new", "Binary Content");
        token= child.lock("thisUser")
        print "Token ", token
        self.failUnless(token, "No lock token returned")
        try:
            activeLock= child.readStandardProperties().getLockDiscovery()
            print "Active lock", activeLock
            self.failUnlessEqual(activeLock[1], "thisUser", "Wrong lock owner %s" % activeLock[1])
            self.failUnlessRaises(WebdavClient.WebdavError, child.writeProperties,
                                                            {('TENT:', 'features') : "X4711"} )
            child.writeProperties({('TENT:', 'features') : "X4711"}, token)
            child.uploadContent("New binary Content", token)
        finally:
            child.unlock(token)
            child.delete()    # clean up server data
            #self.resource.deleteResource("new")    # clean up server data

    
    def testLockAll(self):
        print "\nTest LockAll"
        token= self.resource.lockAll("thisUser")
        self.failUnless(token, "No lock token returned")
        try:
            child= self.resource.addCollection("new", token);
            self.assertRaises(WebdavClient.WebdavError, child.writeProperties, {('TENT:', 'features') : "X4711"})
            child.writeProperties({('TENT:', 'features') : "X4711"}, lockToken= token)
            self.resource.deleteResource("new", token)     # clean up server data
        finally:
            self.resource.unlock(token) 

    
    def testNamespace(self):
        print "\nTest Namespace"
        self.resource.writeProperties({('TENT:', 'features') : "X4711", ('DATA:', 'features') : "X4712"})
        properties= self.resource.readProperties(('TENT:', 'features'), ('DATA:', 'features'))
        self.assertEqual(len(properties), 2, "Returned %d properties." % len(properties))
        value= str(properties.get(('TENT:', 'features')))
        self.assertEqual(value, "X4711", "Wrong property value " + value)
        value= str(properties.get(('DATA:', 'features')))
        self.assertEqual(value, "X4712", "Wrong property value " + value)
        # clean up meta data
        self.resource.deleteProperties(None, ('TENT:', 'features'), ('DATA:', 'features'))
    
    def testRelation(self):
        print "\nTest Relation"
        #link= Element(NS_DAV, 'link')
        #link.add(Element(NS_DAV, 'src', self.resource.url))
        #link.add(Element(NS_DAV, 'dst', str(self.resource.connection)))
        #print "Set link: ", ; qp_xml.dump(sys.stdout, link)
        #self.resource.writeProperties({('TENT:', 'base') : link})
        #value= self.resource.readProperty('TENT:', 'base')
        #self.failUnless(value, "No property value")
        
        #link= value.find('link', 'DAV:')
        #self.failUnless(link, "No link element")
        #source= link.find('src', 'DAV:')
        #self.failUnless(source, "No source element")
        #destination= link.find('dst', 'DAV:')
        #self.failUnless(destination, "No destination element")
        #print "Link: ", destination.textof()
        #self.assertEqual(destination.textof(), str(self.resource.connection), "Wrong link %s" % destination)
        #self.resource.deleteProperties(None, ('TENT:', 'base'))     # clean up meta data
    
    def testCopy(self):
        print "\nTest Copy operation"
        child= self.resource.addResource("new", "Binary Content", {('TENT:', 'feature') : "X4711"});
        newPath= child.path + "_copy"
        try:
            child.copy(child.url + "_copy")
        except:
            self.resource.deleteResource("new")    # clean up server data
            raise
        try:
            child.path= newPath     # trick: modify child to point to resource's copy !
            value= child.readProperty('TENT:', 'feature')
            self.assertEqual(str(value), "X4711", "Wrong property value " + str(value))
            file= child.downloadContent()
            text= file.read()
            self.assertEqual(text, "Binary Content", "Wrong content " + text)
        finally:
            self.resource.deleteResource("new")    # clean up server data
            self.resource.deleteResource("new_copy")    # clean up server data

    def testMove(self):
        print "\nTest Move operation"
        child= self.resource.addResource("new", "Binary Content", {('TENT:', 'feature') : "X4711"});
        newPath= child.path + "_renamed"
        try:
            child.move(child.url + "_renamed")
        except:
            self.resource.deleteResource("new")    # clean up server data
            raise
        try:
            child.path= newPath     # trick: modify child to point to resource's copy !            
            value= child.readProperty('TENT:', 'feature')
            self.assertEqual(str(value), "X4711", "Wrong property value " + str(value))
            file= child.downloadContent()
            text= file.read()
            self.assertEqual(text, "Binary Content", "Wrong content " + text)
        finally:
            self.resource.deleteResource("new_renamed")    # clean up server data

    def testOptions(self):
        print "\nTest options"
        optionMap= self.resource.options()
        print "All options", optionMap.keys()
        print "Dav option value:   ", optionMap.get('dav')
        print "Dasl option value:  ", optionMap.get('dasl')
        print "Server option value:", optionMap.get('server')
        

class ClientTestSuite(unittest.TestSuite):
    def __init__(self, methods):
        unittest.TestSuite.__init__(self, map(ClientTestCase, methods))
            
    
if  __name__ == '__main__':
    methodNames= ("testReadAll", "testListResources", "testMissingProperty", "testCreateCollection", 
                "testAddProperty", "testNamespace", "testRelation", "testCreateResource", "testLock",
                "testValidate", "testOptions", "testUploadResource", "testCopy", "testMove"
                )                
    try:
        options, params= getopt.getopt(sys.argv[1:], "hvm:")
    except getopt.GetoptError, e:
        print e
        sys.exit(1)
    if len(params) > 0:
        url= params[0]
    if len(params) > 2:
        user= params[1]
        password= params[2]
    for opt in options:
        s= opt[0]
        if s == '-h':
            print HELP_TEXT
            sys.exit(0)
        elif s == '-m':
            methodNames= opt[1].split(',')
    suite= ClientTestSuite(methodNames)
    unittest.TextTestRunner().run(suite)
