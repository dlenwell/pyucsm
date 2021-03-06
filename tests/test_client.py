#!/usr/bin/python

# Copyright (c) 2011 Grid Dynamics Consulting Services, Inc, All Rights Reserved
#  http://www.griddynamics.com
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  @Project:     pyucsm
#  @Description: Python binding for CISCO UCS XML API

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                 os.path.pardir)))

import unittest
import pyucsm
import httplib
from xml.dom import minidom

import reference_system as testucsmparams

_host = testucsmparams.HOST
_login = testucsmparams.LOGIN
_password = testucsmparams.PASSWORD

import logging
logging.basicConfig()
pyucsm.set_debug(True)

TEST_ORG = 'org-root/org-pyucsmtest'

class MyBaseTest(unittest.TestCase):
    def assertXmlEquals(self, str1, str2):
        return ''.join(str1.split()) == ''.join(str2.split())

class TestUcsmConnection(MyBaseTest):
    """Need have some working UCSM system to run this tests.
    """

    def test_constructor_nossl(self):
        item = pyucsm.UcsmConnection(_host)
        self.assertEqual(item.__dict__['_create_connection']().__class__, httplib.HTTPConnection)
        
    def test_constructor_ssl(self):
        item = pyucsm.UcsmConnection(_host, secure=True)
        self.assertEqual(item.__dict__['_create_connection']().__class__, httplib.HTTPSConnection)

    def test_connection_ok_nossl(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
        finally:
            c.logout()
            
    def test_connection_ok_ssl(self):
        c = pyucsm.UcsmConnection(_host, secure=True)
        try:
            c.login(_login, _password)
        finally:
            c.logout()

    def test_connection_refresh(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
            c.refresh()
        finally:
            c.logout()
        
    def test_connection_wrong_password(self):
        c = pyucsm.UcsmConnection(_host)
        if not testucsmparams.SIMULATOR:
            with self.assertRaises(pyucsm.UcsmResponseError):
                c.login(_login, 'this is wrong password')
                c.logout()
            with self.assertRaises(pyucsm.UcsmError):
                c.login(_login, 'this is wrong password')
                c.logout()


    def test_connection_404(self):
        c = pyucsm.UcsmConnection('example.com', 80)
        with self.assertRaises(pyucsm.UcsmFatalError):
            c.login(_login, 'this is wrong password')
            c.logout()
        with self.assertRaises(pyucsm.UcsmError):
            c.login(_login, 'this is wrong password')
            c.logout()

    def test_property_filter(self):
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr')>5, pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr')>=5, pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr')<5, pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr')<=5, pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr')==5, pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr')!=5, pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr').wildcard_match('*'), pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr').any_bit(['one','two']), pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr').any_bit('one,two'), pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr').all_bit(['one','two']), pyucsm.UcsmPropertyFilter)
        self.assertIsInstance(pyucsm.UcsmAttribute('cls','attr').all_bit('one,two'), pyucsm.UcsmPropertyFilter)

    def test_compose_filter(self):
        self.assertIsInstance((pyucsm.UcsmAttribute('cls','attr')>5) & (pyucsm.UcsmAttribute('cls','attr')>5),
                              pyucsm.UcsmComposeFilter)
        self.assertIsInstance((pyucsm.UcsmAttribute('cls','attr')>5) | (pyucsm.UcsmAttribute('cls','attr')>5),
                              pyucsm.UcsmComposeFilter)
        self.assertIsInstance(~((pyucsm.UcsmAttribute('cls','attr')>5) & (pyucsm.UcsmAttribute('cls','attr')>5)),
                              pyucsm.UcsmComposeFilter)
        self.assertIsInstance(~((pyucsm.UcsmAttribute('cls','attr')>5) | (pyucsm.UcsmAttribute('cls','attr')>5)),
                              pyucsm.UcsmComposeFilter)

        expr = (pyucsm.UcsmAttribute('cls','attr')>5) & (pyucsm.UcsmAttribute('cls','attr')>5) & \
               (pyucsm.UcsmAttribute('cls','attr')>5)
        self.assertIsInstance(expr, pyucsm.UcsmComposeFilter)
        self.assertEqual(len(expr.arguments), 3)

        expr = (pyucsm.UcsmAttribute('cls','attr')>5) | (pyucsm.UcsmAttribute('cls','attr')>5) | \
               (pyucsm.UcsmAttribute('cls','attr')>5)
        self.assertIsInstance(expr, pyucsm.UcsmComposeFilter)
        self.assertEqual(len(expr.arguments), 3)

        expr = (pyucsm.UcsmAttribute('cls','attr')>5) | (pyucsm.UcsmAttribute('cls','attr')>5) & \
               (pyucsm.UcsmAttribute('cls','attr')>5)
        self.assertIsInstance(expr, pyucsm.UcsmComposeFilter)
        self.assertNotEqual(len(expr.arguments), 3)

        expr = (pyucsm.UcsmAttribute('cls','attr')>5) & (pyucsm.UcsmAttribute('cls','attr')>5) | \
               (pyucsm.UcsmAttribute('cls','attr')>5)
        self.assertIsInstance(expr, pyucsm.UcsmComposeFilter)
        self.assertNotEqual(len(expr.arguments), 3)

    def test_xml_filter(self):
        expr = (pyucsm.UcsmAttribute('cls','attr')>5) | (pyucsm.UcsmAttribute('cls','attr')>5) & \
               (pyucsm.UcsmAttribute('cls','attr')>5)
        self.assertIsInstance(expr, pyucsm.UcsmComposeFilter)
        self.assertXmlEquals(expr.xml(),
                             '<or>'
                               '<gt class="cls" property="attr" value="5"/>'
                               '<and>'
                                 '<gt class="cls" property="attr" value="5"/>'
                                 '<gt class="cls" property="attr" value="5"/>'
                               '</and>'
                             '</or>')

    def test_simple_query_construct(self):
        conn = pyucsm.UcsmConnection('host', 80)
        self.assertXmlEquals('<firsttest />',
                                conn._instantiate_query('firsttest'))
        self.assertXmlEquals('<secondtest one="1" two="zwei" />',
                                conn._instantiate_query('secondtest', one=1, two="zwei"))

    def test_child_query_construct(self):
        conn = pyucsm.UcsmConnection('host', 80)
        self.assertXmlEquals('<secondtest one="1" two="zwei" />',
                                conn._instantiate_query('secondtest', one=1, two="zwei"))
        wish = """<getSmth cookie="123456"><inFilter><gt class="blade" prop="cores" value="2" /></inFilter></getSmth>"""
        self.assertXmlEquals(wish,
                             conn._instantiate_query('getSmth',
                                                             child_data_= (pyucsm.UcsmAttribute('blade','cores')>2).xml(),
                                                             cookie='123456'))

    def test_resolve_children(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
            res = c.resolve_children('aaaUser', 'sys/user-ext')
            self.assertIsInstance(res, list)
            if len(res):
                self.assertIsInstance(res[0], pyucsm.UcsmObject)
        finally:
            c.logout()

    def test_resolve_class(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
            res = c.resolve_class('pkiEp')
            self.assertIsInstance(res, list)
            self.assertIsInstance(res[0], pyucsm.UcsmObject)
            res = c.resolve_class('pkiEp', filter=(pyucsm.UcsmAttribute('pkiEp', 'intId')<0))
            self.assertIsInstance(res, list)
            self.assertEquals(0, len(res))
        finally:
            c.logout()

    def test_resolve_classes(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
            res = c.resolve_classes(['computeItem', 'equipmentChassis'])
            self.assertIsInstance(res, list)
            self.assertGreater(len(res), 0)
            self.assertIsInstance(res[0], pyucsm.UcsmObject)
        finally:
            c.logout()

    def test_resolve_dn(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
            res = c.resolve_dn('sys')
            self.assertIsInstance(res, pyucsm.UcsmObject)
            res = c.resolve_dn('qewr')
            self.assertIsNone(res)
        finally:
            c.logout()

    def test_resolve_dns(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
            res,unres = c.resolve_dns(['sys', 'mac', 'ololo'])
            self.assertIsInstance(res, list)
            self.assertIsInstance(unres, list)
            self.assertEquals(len(res), 2)
            self.assertEquals(len(unres), 1)
        finally:
            c.logout()

    def test_resolve_parent(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
            res = c.resolve_parent('sys/user-ext')
            self.assertIsInstance(res, pyucsm.UcsmObject)
            self.assertEquals(res.dn, 'sys')
            res = c.resolve_parent('sys/this/is/bullshit')
            self.assertIsNone(res)
        finally:
            c.logout()

    def test_find_dns_by_class_id(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
            res = c.find_dns_by_class_id('macpoolUniverse')
            self.assertIsInstance(res, list)
            self.assertEquals(len(res), 1)
            self.assertEquals(res[0], 'mac')
            with self.assertRaises(pyucsm.UcsmFatalError):
                res = c.find_dns_by_class_id('notrealclass')
        finally:
            c.logout()

    def test_conf_mo(self):
        import random
        if testucsmparams.SIMULATOR:
            c = pyucsm.UcsmConnection(_host)
            try:
                c.login(_login, _password)
                src = pyucsm.UcsmObject()
                src.ucs_class = 'aaaLdapEp'
                src.attributes['timeout'] = random.randint(0, 10)
                res = c.conf_mo(src, dn='sys/ldap-ext')
                self.assertEquals(int(res.attributes['timeout']), src.attributes['timeout'])
            finally:
                c.logout()

    def test_conf_mos(self):
        import random
        if testucsmparams.SIMULATOR:
            c = pyucsm.UcsmConnection(_host)
            try:
                c.login(_login, _password)
                src = pyucsm.UcsmObject()
                src.ucs_class = 'aaaLdapEp'
                src.attributes['timeout'] = random.randint(0, 60)
                res = c.conf_mos({'sys/ldap-ext':src})
                import sys
                print >> sys.stderr, res, src
                self.assertEquals(int(res['sys/ldap-ext'].attributes['timeout']), src.attributes['timeout'])
            finally:
                c.logout()

    def test_conf_mo_group(self):
        import random
        if testucsmparams.SIMULATOR:
            c = pyucsm.UcsmConnection(_host)
            try:
                c.login(_login, _password)
                src = pyucsm.UcsmObject()
                src.ucs_class = 'aaaLdapEp'
                src.attributes['timeout'] = random.randint(0, 60)
                dns = ['sys']
                res = c.conf_mo_group(dns, src)
                self.assertEquals(int(res[0].attributes['timeout']), src.attributes['timeout'])
            finally:
                c.logout()

    def test_estimate_impact(self):
        import random
        if testucsmparams.SIMULATOR:
            c = pyucsm.UcsmConnection(_host)
            try:
                c.login(_login, _password)
                with self.assertRaises(pyucsm.UcsmResponseError):
                    admin_user = pyucsm.UcsmObject()
                    admin_user.ucs_class = 'aaaUser'
                    admin_user.attributes['status'] = 'deleted'
                    admin_user.attributes['dn'] = 'sys/user-ext/user-admin'
                    ack,old_ack,aff,old_aff = c.estimate_impact({'sys/user-ext/user-admin':admin_user})
                newuser = pyucsm.UcsmObject()
                newuser.ucs_class = 'aaaUser'
                newuser.attributes['status'] = 'created'
                newuser.attributes['dn'] = 'sys/user-ext/user-testuser'
                ack,old_ack,aff,old_aff = c.estimate_impact({'sys/user-ext/user-testuser':newuser})
                self.assertEquals(ack, [])
                self.assertEquals(old_ack, [])
                self.assertEquals(aff, [])
                self.assertEquals(old_aff, [])
            finally:
                c.logout()

    def test_scope(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)
            res = c.scope('computeBlade', 'sys', recursive=True)
            self.assertNotEquals(len(res), 0)
            self.assertEquals(len(res[0].children), 0)
            #res = c.scope('computeBlade', 'sys', recursive=False)
            #self.assertEquals(len(res), 0) # TODO: why without recursive it behaves recursive?
            res = c.scope('computeBlade', 'sys', recursive=True, hierarchy=True)
            self.assertNotEquals(len(res[0].children), 0)
        finally:
            c.logout()

    def test_config_mo_wrappers(self):
        c = pyucsm.UcsmConnection(_host)
        if testucsmparams.SIMULATOR:
            try:
                c.login(_login, _password)

                find_ = c.resolve_dn('org-root/org-Test1')
                if find_:
                    c.delete_object(find_)

                obj1 = pyucsm.UcsmObject('orgOrg')
                obj1.name = 'Test1'
                obj1.rn = 'wrongrn'
                t1 = c.create_object(obj1, root='org-root', rn='org-Test1')
                self.assertIsNotNone(obj1)

                obj2 = pyucsm.UcsmObject('orgOrg')
                obj2.name = 'Test2'
                obj2.rn = 'org-Test2'
                t2 = c.create_object(obj2, root='org-root/org-Test1')
                self.assertIsNotNone(obj2)

                obj3 = pyucsm.UcsmObject('orgOrg')
                obj3.name = 'Test3'
                t3 = c.create_object(obj3, dn='org-root/org-Test1/org-Test2/org-Test3')
                self.assertIsNotNone(obj3)

                obj4 = pyucsm.UcsmObject('orgOrg')
                obj4.name = 'Test4'
                obj4.dn = 'org-root/org-Test1/org-Test2/org-Test3/org-Test4'
                t4 = c.create_object(obj4)
                self.assertIsNotNone(obj4)

                test_const = 'Lorum ipsum!'
                obj1.descr = test_const
                obj1_changed = c.update_object(obj1)
                self.assertEquals(test_const, obj1_changed.descr)

                c.delete_object(c.resolve_dn('org-root/org-Test1'))

                find_2 = c.resolve_dn('org-root/org-Test1')
                self.assertIsNone(find_2)
            finally:
                c.logout()

    def test_resolve_elements(self):
        c = pyucsm.UcsmConnection(_host)
        try:
            c.login(_login, _password)

            found = c.resolve_elements('org-root', 'lsbootPolicy')
            self.assertTrue(bool(sum(o.ucs_class == 'lsbootPolicy' for o in found.values())))
        finally:
            c.logout()

    def test_clone_profile(self):
        def parametrized_test(c, src, name, target='org-root'):
            try:
                created = None
                if target:
                    created = c.clone_profile(src, name, target)
                else:
                    created = c.clone_profile(src, name)
                    target = 'org-root'
                self.assertIsInstance(created, pyucsm.UcsmObject)
                self.assertEqual(created.ucs_class, 'lsServer')
                self.assertEqual(created.name, name)
                self.assertEqual(os.path.dirname(created.dn), target)
            finally:
                if created:
                    c.delete_object(created)

        c = pyucsm.UcsmConnection(_host, 80)
        try:
            test_org = None
            c.login(_login, _password)
            test_org = pyucsm.UcsmObject('orgOrg')
            test_org.dn = TEST_ORG
            test_org = c.create_object(test_org)

            tests = [
                ('org-root/ls-11', 'mycoolprof'),
                ('org-root/ls-11', 'mycoolprof', TEST_ORG)
            ]
            for test in tests:
                parametrized_test(c, *test)
        finally:
            try:
                c.delete_object(test_org)
            finally:
                c.logout()

    def test_instantiate_template(self):
        def parametrized_test(c, src, name, target='org-root'):
            try:
                created = None
                if target:
                    created = c.instantiate_template(src, name, target)
                else:
                    created = c.instantiate_template(src, name)
                    target = 'org-root'
                self.assertIsInstance(created, pyucsm.UcsmObject)
                self.assertEqual(created.ucs_class, 'lsServer')
                self.assertEqual(created.name, name)
                self.assertEqual(os.path.dirname(created.dn), target)
            finally:
                if created:
                    c.delete_object(created)

        c = pyucsm.UcsmConnection(_host)
        try:
            test_org = None
            c.login(_login, _password)
            test_org = pyucsm.UcsmObject('orgOrg')
            test_org.dn = TEST_ORG
            test_org = c.create_object(test_org)

            tests = [
                ('org-root/ls-11', 'mycoolprof'),
                ('org-root/ls-11', 'mycoolprof', TEST_ORG)
            ]
            for test in tests:
                parametrized_test(c, *test)
        finally:
            try:
                c.delete_object(test_org)
            finally:
                c.logout()

    def test_instantiate_n_template(self):
        def parametrized_test(c, src, target='org-root', prefix='', number=1):
            try:
                created = c.instantiate_n_template(src, target_org_dn=target,
                                                   prefix=prefix,
                                                   number=number)
                self.assertIsInstance(created, list)
                self.assertEqual(len(created), number)
                for obj in created:
                    self.assertIsInstance(obj, pyucsm.UcsmObject)
                    self.assertEqual(obj.ucs_class, 'lsServer')
                    self.assertEqual(os.path.dirname(obj.dn), target)
                    if prefix:
                        self.assertTrue(obj.name.startswith(prefix))
            finally:
                if created:
                    for obj in created:
                        c.delete_object(obj)

        c = pyucsm.UcsmConnection(_host)
        try:
            test_org = None
            c.login(_login, _password)
            test_org = pyucsm.UcsmObject('orgOrg')
            test_org.dn = TEST_ORG
            test_org = c.create_object(test_org)

            tests = [
                (('org-root/ls-11',), {}),
                (('org-root/ls-11',), {'prefix': 'ololo'}),
                (('org-root/ls-11',), {'number': 2}),
                (('org-root/ls-11',), {'target': TEST_ORG})
            ]
            for args, kwargs in tests:
                parametrized_test(c, *args, **kwargs)
        finally:
            try:
                c.delete_object(test_org)
            finally:
                c.logout()

    def test_instantiate_n_template_named(self):
        def parametrized_test(c, src, names, target='org-root', prefix=''):
            try:
                created = None
                created = c.instantiate_n_template_named(src, names,
                                                         target_org_dn=target)
                self.assertIsInstance(created, list)
                self.assertEqual(len(created), len(names))
                self.assertEqual(
                    set(names),
                    set(o.name for o in created)
                )

                for obj in created:
                    self.assertIsInstance(obj, pyucsm.UcsmObject)
                    self.assertEqual(obj.ucs_class, 'lsServer')
                    self.assertEqual(os.path.dirname(obj.dn), target)
                    if prefix:
                        self.assertTrue(obj.name.startswith(prefix))
            finally:
                if created:
                    for obj in created:
                        c.delete_object(obj)

        c = pyucsm.UcsmConnection(_host)
        try:
            test_org = None
            c.login(_login, _password)
            test_org = pyucsm.UcsmObject('orgOrg')
            test_org.dn = TEST_ORG
            test_org = c.create_object(test_org)

            tests = [
                (('org-root/ls-11', ['test']), {}),
                (('org-root/ls-11', ['test1', 'test2']), {}),
                (('org-root/ls-11', ['test']), {'target': TEST_ORG})
            ]
            for args, kwargs in tests:
                parametrized_test(c, *args, **kwargs)
        finally:
            try:
                c.delete_object(test_org)
            finally:
                c.logout()


class TestUcsmObject(MyBaseTest):

    def test_ucsm_object_parsing(self):
        xml_str = """<computeBlade adminPower="policy" adminState="in-service" assignedToDn="org-root/ls-11"
        association="associated" availability="unavailable" availableMemory="8192" chassisId="1"
        checkPoint="discovered" connPath="A,B" connStatus="A" descr="" discovery="complete" dn="sys/chassis-1/blade-1"
        fltAggr="0" fsmDescr="" fsmFlags="" fsmPrev="TurnupSuccess" fsmProgr="100" fsmRmtInvErrCode="none"
        fsmRmtInvErrDescr="" fsmRmtInvRslt="" fsmStageDescr="" fsmStamp="2011-06-29T12:35:04.205" fsmStatus="nop"
        fsmTry="0" intId="28925" lc="undiscovered" lcTs="1970-01-01T01:00:00.000" lowVoltageMemory="not-applicable"
        managingInst="A" memorySpeed="not-applicable" model="N20-B6620-1" name="" numOfAdaptors="1" numOfCores="10"
        numOfCoresEnabled="10" numOfCpus="2" numOfEthHostIfs="3" numOfFcHostIfs="0" numOfThreads="14"
        operPower="on" operQualifier="" operState="ok" operability="operable"
        originalUuid="1b4e28ba-2fa1-11d2-0101-b9a761bde3fb" presence="equipped" revision="0" serial="577"
        serverId="1/1" slotId="1" totalMemory="8192" usrLbl="" uuid="1b4e28ba-2fa1-11d2-0101-b9a761bde3fb"
        vendor="Cisco Systems Inc"/>"""
        doc = minidom.parseString(xml_str)
        elem = doc.childNodes[0]
        obj = pyucsm.UcsmObject(elem)
        self.assertEquals('policy', obj.attributes['adminPower'])
        self.assertEquals('policy', obj.adminPower)
        self.assertEquals('sys/chassis-1/blade-1', obj.dn)
        self.assertEquals('computeBlade', obj.ucs_class)
        obj.attributes['this_is_shurely_not_in_dict'] = 42
        self.assertEquals(42, obj.this_is_shurely_not_in_dict)
        obj.this_is_also_not_in_dict = 84
        self.assertEquals(84, obj.this_is_also_not_in_dict)
        copy = obj.copy()
        self.assertEquals(len(obj.attributes), len(copy.attributes))
        self.assertEquals(len(obj.children), len(obj.children))
        obj.ucs_class += 'appended'
        self.assertNotEquals(obj.ucs_class, copy.ucs_class)

    def test_ucsm_object_hierarchy(self):
        obj = pyucsm.UcsmObject('parentClass')
        obj.children.append(pyucsm.UcsmObject('childClass1'))
        obj.children.append(pyucsm.UcsmObject('childClass2'))
        self.assertEquals(1, len(obj.find_children('childClass1')))
        self.assertEquals(1, len(obj.find_children('childClass2')))

    def test_compare(self):
        obj1 = pyucsm.UcsmObject('testObject')
        obj1.dn = TEST_ORG
        obj2 = pyucsm.UcsmObject('testObject')
        obj2.dn = TEST_ORG
        obj3 = pyucsm.UcsmObject('testObject')
        obj3.dn = 'org-root/org-test2'
        obj4 = pyucsm.UcsmObject('testObject1')
        obj4.dn = TEST_ORG
        self.assertEqual(obj1, obj2)
        self.assertNotEqual(obj1, obj3)
        self.assertNotEqual(obj1, obj4)

    def test_recursive_compare(self):
        an_obja = pyucsm.UcsmObject('testObject')
        an_objb = pyucsm.UcsmObject('testObject')

        obj1 = pyucsm.UcsmObject('testObject')
        obj1.dn = TEST_ORG
        obj2 = pyucsm.UcsmObject('testObject')
        obj2.dn = TEST_ORG
        obj3 = pyucsm.UcsmObject('testObject')
        obj3.dn = 'org-root/org-test2'
        obj4 = pyucsm.UcsmObject('testObject1')
        obj4.dn = TEST_ORG

        for child in (obj2, obj3, obj4):
            obja = an_obja.copy()
            objb = an_objb.copy()
            obja.children.append(obj1)
            objb.children.append(child.copy())
            self.assertEquals( obja == objb, obj1 == child )

    def test_copy(self):
        obja = pyucsm.UcsmObject('testObject')
        obja.dn = TEST_ORG
        objc = pyucsm.UcsmObject('testObject')
        objc.dn = TEST_ORG
        obja.children.append(objc)
        objb = obja.copy()
        self.assertIsNot(obja, objb)
        self.assertEqual(obja, objb)


if __name__ == '__main__':
    unittest.main()
