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


import sys
import urllib
from os.path import basename

from webdav.Constants import *
from webdav.WebdavClient import ResourceStorer, CollectionStorer
from webdav.acp.Acl import ACL

from davlib import XML_DOC_HEADER
import qp_xml


PRINCIPALS_BASE= '/taminowebdavserver/administration/security/userdb/users/'
PRINCIPALS_ALL= '/taminowebdavserver/administration/security/userdb/'

class ChangeAcl(object):
    def __init__(self, switch=TAG_GRANT, *names):
        self.names= map(lambda n: urllib.quote_plus(n), names)
        self.aceText= {}
        for name in self.names:
            self.aceText[name]= '<D:%s>\n' % TAG_ACE + \
                                '<D:%s><D:%s>%s</D:%s></D:%s>\n' % (TAG_PRINCIPAL, TAG_HREF, PRINCIPALS_BASE + name, TAG_HREF, TAG_PRINCIPAL) + \
                                '<D:%s><D:%s><D:%s /></D:%s></D:%s>\n' % (switch, TAG_PRIVILEGE, TAG_ALL, TAG_PRIVILEGE, switch) + \
                                '</D:%s>\n' % TAG_ACE;
    def toXML(self):
        return '<D:%s xmlns:D="DAV:">' % TAG_ACL + \
            reduce(lambda l,r: l+r+'\n', self.aceText.values()) + \
            '</D:%s>' % TAG_ACL

class GrantAcl(ChangeAcl):
    def __init__(self, *names):
        ChangeAcl.__init__(self, TAG_GRANT, *names)

    def toXML(self):
        return '<D:%s xmlns:D="DAV:">' % TAG_ACL + \
            reduce(lambda l,r: l+r+'\n', self.aceText.values()) + \
            '<D:%s>\n' % TAG_ACE + \
            '<D:%s><D:%s>%s</D:%s></D:%s>\n' % (TAG_PRINCIPAL, TAG_HREF, PRINCIPALS_ALL, TAG_HREF, TAG_PRINCIPAL) + \
            '<D:%s><D:%s><D:%s /></D:%s></D:%s>\n' % (TAG_DENY, TAG_PRIVILEGE, TAG_WRITE, TAG_PRIVILEGE, TAG_DENY) + \
            '</D:%s>\n' % TAG_ACE + \
            '</D:%s>' % TAG_ACL
        
class DenyAcl(ChangeAcl):
    def __init__(self, *names):
        ChangeAcl.__init__(self, TAG_DENY, *names)
        
        
class Buri(object):
    connection= None
    
    def __init__(self):
        self.storers= []
        self.url= "http://buri.sistec.kp.dlr.de/taminowebdavserver/datafinder/"
        user= "tamino user"
        password= "tamino"
        if  len(sys.argv) > 1:
            self.url= sys.argv[1]
        print "init ", self.url
        self.resource= CollectionStorer(self.url, Buri.connection)
        if not Buri.connection:
            Buri.connection= self.resource.connection
        if  len(sys.argv) > 3:
            user= sys.argv[2]
            password= sys.argv[3]
        if  user:
            self.resource.connection.addBasicAuthorization(user, password)

    def getMembers(self):
        print "Get members"
        items= self.resource.findProperties((NS_DAV, PROP_RESOURCE_TYPE))
        for item in items.keys():
            self.storers.append(ResourceStorer(item, Buri.connection))
            print "Path ", item
            
    def getAcls(self):
        print "Get ACLs"
        for item in self.storers:
            if item.path.endswith("tmp2"):
                aclElem= item.readProperty(NS_DAV, 'acl')
                acl= ACL(aclElem)
                print "ACL for", item.path,
                qp_xml.dump(sys.stdout, aclElem)
                break
        
    def addAdmin(self):
        print "Add Admin"
        for item in self.storers:
            newAcl= GrantAcl('admin')
            print "set ACL of", item.path, "to", newAcl.toXML()
            item.setAcl(newAcl)
        
    def denyGuy(self):
        print "Deny Guy"
        for item in self.storers:
            if item.path.endswith("public"):
                newAcl= DenyAcl('gkloss')
                print "deny ACL of", item.path, "to", newAcl.toXML()
                item.setAcl(newAcl)
        
    def removeAll(self):
        print "Add Admin"
        for item in self.storers:
            newAcl= DenyAcl('')
            print "set ACL of", item.path, "to", newAcl.toXML()
            item.setAcl(newAcl)
        
    def addUser(self, username, collection):
        print "Add User", username, "to", collection
        for item in self.storers:
            if  item.path.find(collection) >= 0:
                newAcl= GrantAcl(username)
                print "set ACL of", item.path, "to", newAcl.toXML()
                item.setAcl(newAcl)
        
    def removeUser(self, username, collections):
        print "Deny user", username, "from", collections
        for item in self.storers:
            print "Dir:", basename(item.path)
            if  basename(item.path) in collections:
                newAcl= DenyAcl(username)
                print "deny ACL of", item.path, "to", newAcl.toXML()
                item.setAcl(newAcl)
        
           
if  __name__ == '__main__':
    buri= Buri()
    buri.getMembers()
    buri.getAcls()
    #buri.removeUser('Thijs Metsch', 'tmp')
    #buri.addAdmin()    
    buri.removeUser('Uwe Tapper', ('rbetz', 'mwag', 'gkloss'))
    buri.removeUser('Matthias Wagner', ('rbetz', 'gkloss', 'utap'))
    buri.removeUser('Roland Betz', ('gkloss', 'mwag', 'utap'))
    buri.removeUser('Guy Kloss', ('rbetz', 'mwag', 'utap'))
