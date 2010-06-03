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


""" Refactor or remove this. """


import unittest
import sys
from os.path import basename
import getopt
from time import strftime
import qp_xml

from webdav.Constants import NS_DAV, TAG_ACL, PROP_CONTENT_LENGTH, DATE_FORMAT_HTTP, \
                             PROP_CREATION_DATE, DATE_FORMAT_HTTP, PROP_LAST_MODIFIED, \
                             PROP_CONTENT_TYPE
from webdav import Condition
from webdav.Condition import NotTerm, ExistsTerm
from webdav import WebdavClient
from webdav.acp.Acl import ACL


_helpText = '''
Test WebDAV extension features with WebDAV client.
\nUsage:\tExtensionTestCase.py [-hp] [url [user password]]
\t-h[elp] : Show this text.
\t-p[art] dasl|acl|deltav|all : default: dasl.
'''

url = "http://bsasdf01.as.bs.dlr.de/taminowebdavserver/datafinder/test/SISTEC/PictureDemo/"
user = "tamino user"
password = "tamino"

def printresult(resources):
    urls = resources.keys()
    names = map(lambda url: (basename(url), str(resources[url].popitem()[1])), urls)
    print "%d results: " % len(urls), names, "\n\n"

        
class ExtensionTestCase(unittest.TestCase):
    connection = None
    
    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        print "init URL=", url
        self.resource = WebdavClient.CollectionStorer(url, ExtensionTestCase.connection)
        if not ExtensionTestCase.connection:
            ExtensionTestCase.connection = self.resource.connection
        if  user:
            print "User", user, "Password:", password
            self.resource.connection.addBasicAuthorization(user, password)
            
    def setUp(self):
        pass
        
    def testSearchNumber(self):
        print "Test SearchNumber: lenght=312"
        condition = Condition.IsEqualTerm(PROP_CONTENT_LENGTH, 312)
        result = self.resource.search(condition, ('DAV:', PROP_CONTENT_LENGTH) )
        printresult(result)        
        self.failUnlessEqual(len(result), 5, "Five resources do match but %d found." % len(result))
        
    def testSearchString(self):
        print "Test SearchString: type is jpeg"
        condition = Condition.MatchesTerm(PROP_CONTENT_TYPE, 'image/pjpeg')
        result = self.resource.search(condition, ('DAV:', PROP_CONTENT_TYPE) )
        printresult(result)
        self.failUnlessEqual(len(result), 54, "54 resources do match but %d found." % len(result))
        
    def testSearchStringCaseless(self):
        print "Test SearchString: type is jpeg"
        condition = Condition.MatchesTerm(PROP_CONTENT_TYPE, 'image/PJPEG', "case-less")
        result = self.resource.search(condition, ('DAV:', PROP_CONTENT_TYPE) )
        printresult(result)
        self.failUnlessEqual(len(result), 54, "54 resources do match but %d found." % len(result))
        
    def testSearchStringPart(self):
        print "Test SearchStringPart: type contains jpeg"
        condition = Condition.ContainsTerm(PROP_CONTENT_TYPE, 'pjpeg')
        result = self.resource.search(condition, ('DAV:', PROP_CONTENT_TYPE) )
        printresult(result)
        self.failUnlessEqual(len(result), 54, "54 resources do match but %d found." % len(result))
        
    def testSearchContent(self):
        print "Test SearchContent: content contains word 'picture'"
        condition = Condition.ContentContainsTerm('picture')
        result = self.resource.search(condition, ('DAV:', PROP_CONTENT_LENGTH) )
        printresult(result)
        self.failUnlessEqual(len(result), 64, "64 resources do match but %d found." % len(result))
        
    def testSearchDate(self):
        print "Test SearchDate: items created before first item"
        childs = self.resource.listResources()
        firstItem = childs.popitem()[1]
        firstDate = firstItem.getCreationDate()
        print "%s created on %s." % (firstItem.getDisplayName(),
                strftime(DATE_FORMAT_HTTP, firstDate))
        condition = Condition.BeforeTerm(PROP_CREATION_DATE, firstDate)
        result = self.resource.search(condition, ('DAV:', PROP_CREATION_DATE) )
        printresult(result)
        self.failUnlessEqual(len(result), 3, "Three resources do match but %d found." % len(result))
        
    def testSearchDate2(self):
        print "Test SearchDate2: modified before first item"
        childs = self.resource.listResources()
        firstItem = childs.popitem()[1]
        firstDate = firstItem.getLastModified()
        print "%s created on %s." % (firstItem.getDisplayName(), 
                strftime(DATE_FORMAT_HTTP, firstDate))
        condition = Condition.BeforeTerm(PROP_LAST_MODIFIED, firstDate)
        result = self.resource.search(condition, ('DAV:', PROP_LAST_MODIFIED) )
        printresult(result)
        self.failUnlessEqual(len(result), 3, "Three resources do match but %d found." % len(result))
        
    def testSearchDefined(self):
        print "Test Search for a defined property"
        condition = ExistsTerm(('DF:', 'feature'))
        result = self.resource.search(condition, ('DAV:', PROP_CONTENT_LENGTH) )
        printresult(result)
        self.failUnlessEqual(len(result), 3, "Three resources do match but %d found." % len(result))

    def testSearchNotDefined(self):
        print "Test Search for a undefined property"
        condition = NotTerm(ExistsTerm(('DF:', 'feature')))
        result = self.resource.search(condition, ('DAV:', PROP_CONTENT_LENGTH) )
        #result = self.resource.deepFindProperties(('DF:', 'feature'), ('DAV:', PROP_CONTENT_LENGTH) )
        printresult(result)
        self.failUnlessEqual(len(result), 148, "148 resources do match but %d found." % len(result))


    # ACL related tests

    def testSetAcl(self):
        """
        Allow write access to a newly created collection only for the current user:
        Use this ACL (order of ACEs is important)
        ACL = ACE(currentUser, grant, all), ACE(users, deny, write)
        """
        print "Change ACl of 'new' resource"
        child = self.resource.addResource("new", "Binary Content", None)
        try:
            # replace space with plus
            aclText = '''<D:acl xmlns:D="DAV:">
             <D:ace><D:principal>
             <D:href>/taminowebdavserver/administration/security/userdb/users/%s</D:href></D:principal>
             <D:grant><D:privilege><D:all/></D:privilege></D:grant></D:ace>
             <D:ace><D:principal>
             <D:href>/taminowebdavserver/administration/security/users/localhost/userdb</D:href></D:principal>
             <D:deny><D:privilege><D:write/></D:privilege></D:deny></D:ace></D:acl>''' % user.replace(' ','+')
            class DummyAcl:
                def toXML(self):
                    return aclText
            acl = DummyAcl()

            print "Setting ACL to", aclText
            child.setAcl(acl)    
            value = child.readProperty(NS_DAV, TAG_ACL)
            print "ACL returned:"
            qp_xml.dump(sys.stdout, value)
            #self.assertEqual(acl.toXML(), str(value), "Wrong ACL returned: %s" % str(value))
        finally:
            #self.resource.deleteResource("new")    # clean up server data
            pass
        
    def testGetPrivileges(self):
        print "Test read current user's privileges on", self.resource.path
        privileges = self.resource.getCurrentUserPrivileges()
        print len(privileges), "privileges: ", privileges, "\n"
            
    def testGetAcl(self):
        print "Test read ACL of ", self.resource.path
        value = self.resource.readProperty(NS_DAV, TAG_ACL)
        print "ACL property:", qp_xml.dump(sys.stdout, value),"\n"
        acl = ACL(value)
        print "ACL: ", acl.toXML(), "\n"

    
    # Delta-V related tests
        
    def testVersionOn(self):
        print "Test activation of version control."
        try:
            self.resource.deleteResource("new")    # clean up server data
        except Exception, error:
            print "Warning:", error
            
        child = self.resource.addResource("new", "Binary Content", None)
        child.activateVersionControl()
    
    def updateAutoVersion(self):
        print "Test adding a new version"
        storer = WebdavClient.ResourceStorer(url + '/new', ExtensionTestCase.connection)
        # lock resource
        lockToken = storer.lock(user)
        try:
            # PUT request/ update data
            storer.uploadContent("New binary content", lockToken)
            storer.writeProperties({('TENT:', 'features') : "X4711"}, lockToken)
        finally:    # unlock
            storer.unlock(lockToken)
        # view versions
        result = storer.listAllVersions()
        print "Existing versions of 'new':"
        for item in result:
            print "\t", item
        self.failUnless(len(result)==2, "Two versions expected insted of %d." % len(result))

    def testUncheckout(self):
        print "Test undoing an checkout operation"        
        storer = self.resource.addResource("new2", "Binary Content", None)
        lockToken = None
        try:
            storer.activateVersionControl()
            lockToken = storer.lock(user)
            storer.writeProperties({('TENT:', 'features') : "X4711"}, lockToken)
            storer.uncheckout(lockToken)
            storer.unlock(lockToken)
            lockToken = None
            result = storer.listAllVersions()
            print "Existing versions of 'new2':", result
            self.failUnless(len(result)==1, "Two versions expected insted of %d." % len(result))            
            self.failUnlessRaises(WebdavClient.WebdavError, self.resource.readProperties, ('TENT:', 'features'))
        finally:
            storer.delete(lockToken)    # clean up server data
           
    def updateVersion(self):
        print "Creating second versions with"
        storer = WebdavClient.ResourceStorer(url + '/new', ExtensionTestCase.connection)
        # checkout resource
        storer.checkout()
        # PUT request/ update data
        storer.uploadContent("New binary content")
        # unlock
        storer.checkin()
        # view versions
        result = storer.listAllVersions()
        printresult(result)


class DaslTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, \
            map(ExtensionTestCase, ("testSearchNumber", "testSearchString", "testSearchStringCaseless", "testSearchStringPart", 
                                    "testSearchContent", "testSearchDate", "testSearchDate2", "testSearchDefined", "testSearchNotDefined")))
    
class AclTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, \
            map(ExtensionTestCase, ("testGetPrivileges", "testGetAcl", 'testSetAcl')))
    
class DeltavTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, \
            map(ExtensionTestCase, ('testVersionOn','updateAutoVersion', 'testUncheckout')))
    
    
if  __name__ == '__main__':
    part = 'dasl'
    try:
        options, params = getopt.getopt(sys.argv[1:], "hp:")
    except getopt.GetoptError, e:
        print e
        sys.exit(1)	
    print options, params
    if len(params) > 0:
        url = params[0]
    if len(params) > 2:
        user = params[1]
        password = params[2]
        
    for opt in options:
        s = opt[0]
        if s == '-h':
            print _helpText
            sys.exit(0)
        elif s == '-p':
            part = opt[1]
     
    print part, url, user, password       
    if 'all' == part or 'dasl' == part:
        unittest.TextTestRunner().run(DaslTestSuite())
    if 'all' == part or 'acl' == part:
        unittest.TextTestRunner().run(AclTestSuite())
    if 'all' == part or 'deltav' == part:
        unittest.TextTestRunner().run(DeltavTestSuite())
