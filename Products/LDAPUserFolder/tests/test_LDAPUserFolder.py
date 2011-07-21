##############################################################################
#
# Copyright (c) 2000-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" LDAPUserFolder class tests

$Id: test_LDAPUserFolder.py 2053 2011-01-10 11:54:37Z jens $
"""

# General Python imports
import copy
import ldap
import os.path
import unittest

# Zope imports
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from App.Common import package_home

# LDAPUserFolder package imports
from Products.LDAPUserFolder import manage_addLDAPUserFolder

# Tests imports
from dataflake.ldapconnection.tests import fakeldap
from Products.LDAPUserFolder.tests.base.dummy import LDAPDummyUser
from Products.LDAPUserFolder.tests.base.testcase import LDAPTest
from Products.LDAPUserFolder.tests.config import defaults
from Products.LDAPUserFolder.tests.config import alternates
from Products.LDAPUserFolder.tests.config import user
from Products.LDAPUserFolder.tests.config import user2
from Products.LDAPUserFolder.tests.config import manager_user
dg = defaults.get
ag = alternates.get
ug = user.get
u2g = user2.get

class TestLDAPUserFolder(LDAPTest):

    def testLUFInstantiation(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        self.failUnless(acl.isPrincipiaFolderish)
        ae(self.folder.__allow_groups__, self.folder.acl_users)
        ae(acl.getProperty('title'), dg('title'))
        ae(acl.getProperty('_login_attr'), dg('login_attr'))
        ae(acl.getProperty('_uid_attr'), dg('uid_attr'))
        ae(acl.getProperty('users_base'), dg('users_base'))
        ae(acl.getProperty('users_scope'), dg('users_scope'))
        ae(acl.getProperty('_roles'), [dg('roles')])
        ae(acl.getProperty('groups_base'), dg('groups_base'))
        ae(acl.getProperty('groups_scope'), dg('groups_scope'))
        ae(acl.getProperty('_binduid'), dg('binduid'))
        ae(acl.getProperty('_bindpwd'), dg('bindpwd'))
        ae(acl.getProperty('_binduid_usage'), dg('binduid_usage'))
        ae(acl.getProperty('_rdnattr'), dg('rdn_attr'))
        ae(acl.getProperty('_local_groups'), not not dg('local_groups'))
        ae(acl.getProperty('_implicit_mapping'), not not dg('implicit_mapping'))
        ae(acl.getProperty('_pwd_encryption'), dg('encryption'))
        ae(acl.getProperty('_extra_user_filter'), dg('extra_user_filter'))
        ae(acl.getProperty('read_only'), not not dg('read_only'))
        ae(len(acl._cache('anonymous').getCache()), 0)
        ae(len(acl._cache('authenticated').getCache()), 0)
        ae(len(acl._cache('negative').getCache()), 0)
        ae(len(acl.getSchemaConfig().keys()), 2)
        ae(len(acl.getSchemaDict()), 2)
        ae(len(acl._groups_store), 0)
        ae(len(acl.getProperty('additional_groups')), 0)
        ae(len(acl.getGroupMappings()), 0)
        ae(len(acl.getServers()), 1)

    def testAlternateLUFInstantiation(self):
        ae = self.assertEqual
        self.folder._delObject('acl_users')
        manage_addLDAPUserFolder(self.folder)
        acl = self.folder.acl_users
        host, port = ag('server').split(':')
        acl.manage_addServer(host, port=port)
        acl.manage_edit( title = ag('title')
                       , login_attr = ag('login_attr')
                       , uid_attr = ag('uid_attr')
                       , users_base = ag('users_base')
                       , users_scope = ag('users_scope')
                       , roles= ag('roles')
                       , groups_base = ag('groups_base')
                       , groups_scope = ag('groups_scope')
                       , binduid = ag('binduid')
                       , bindpwd = ag('bindpwd')
                       , binduid_usage = ag('binduid_usage')
                       , rdn_attr = ag('rdn_attr')
                       , local_groups = ag('local_groups')
                       , implicit_mapping = ag('implicit_mapping')
                       , encryption = ag('encryption')
                       , read_only = ag('read_only')
                       , extra_user_filter = ag('extra_user_filter')
                       )
        acl = self.folder.acl_users
        ae(acl.getProperty('title'), ag('title'))
        ae(acl.getProperty('_login_attr'), ag('login_attr'))
        ae(acl.getProperty('_uid_attr'), ag('uid_attr'))
        ae(acl.getProperty('users_base'), ag('users_base'))
        ae(acl.getProperty('users_scope'), ag('users_scope'))
        ae(acl.getProperty('_roles'), [x.strip() for x in ag('roles').split(',')])
        ae(acl.getProperty('groups_base'), ag('groups_base'))
        ae(acl.getProperty('groups_scope'), ag('groups_scope'))
        ae(acl.getProperty('_binduid'), ag('binduid'))
        ae(acl.getProperty('_bindpwd'), ag('bindpwd'))
        ae(acl.getProperty('_binduid_usage'), ag('binduid_usage'))
        ae(acl.getProperty('_rdnattr'), ag('rdn_attr'))
        ae(acl.getProperty('_local_groups'), not not ag('local_groups'))
        ae(acl.getProperty('_implicit_mapping'), not not ag('implicit_mapping'))
        ae(acl.getProperty('_pwd_encryption'), ag('encryption'))
        ae(acl.getProperty('_extra_user_filter'), ag('extra_user_filter'))
        ae(acl.getProperty('read_only'), not not ag('read_only'))


    def testLDAPDelegateInstantiation(self):
        ld = self.folder.acl_users._delegate
        ae = self.assertEqual
        ae(len(ld.getServers()), 1)
        ae(ld.login_attr, dg('login_attr'))
        ae(ld.rdn_attr, dg('rdn_attr'))
        ae(ld.bind_dn, dg('binduid'))
        ae(ld.bind_pwd, dg('bindpwd'))
        ae(ld.binduid_usage, dg('binduid_usage'))
        ae(ld.u_base, dg('users_base'))
        ae(ld.u_classes, ['top', 'person'])
        ae(ld.read_only, not not dg('read_only'))

    def testLUFEdit(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        acl.manage_edit( title = ag('title')
                       , login_attr = ag('login_attr')
                       , uid_attr = ag('uid_attr')
                       , users_base = ag('users_base')
                       , users_scope = ag('users_scope')
                       , roles = ag('roles')
                       , groups_base = ag('groups_base')
                       , groups_scope = ag('groups_scope')
                       , binduid = ag('binduid')
                       , bindpwd = ag('bindpwd')
                       , binduid_usage = ag('binduid_usage')
                       , rdn_attr = ag('rdn_attr')
                       , obj_classes = ag('obj_classes')
                       , local_groups = ag('local_groups')
                       , implicit_mapping = ag('implicit_mapping')
                       , encryption = ag('encryption')
                       , read_only = ag('read_only')
                       )
        ae(acl.getProperty('title'), ag('title'))
        ae(acl.getProperty('_login_attr'), ag('login_attr'))
        ae(acl.getProperty('_uid_attr'), ag('uid_attr'))
        ae(acl.getProperty('users_base'), ag('users_base'))
        ae(acl.getProperty('users_scope'), ag('users_scope'))
        ae(', '.join(acl.getProperty('_roles')), ag('roles'))
        ae(acl.getProperty('groups_base'), ag('groups_base'))
        ae(acl.getProperty('groups_scope'), ag('groups_scope'))
        ae(acl.getProperty('_binduid'), ag('binduid'))
        ae(acl.getProperty('_bindpwd'), ag('bindpwd'))
        ae(acl.getProperty('_binduid_usage'), ag('binduid_usage'))
        ae(acl.getProperty('_rdnattr'), ag('rdn_attr'))
        ae(', '.join(acl.getProperty('_user_objclasses')), ag('obj_classes'))
        ae(acl.getProperty('_local_groups'), not not ag('local_groups'))
        ae(acl.getProperty('_implicit_mapping'), not not ag('implicit_mapping'))
        ae(acl.getProperty('_pwd_encryption'), ag('encryption'))
        ae(acl.getProperty('read_only'), not not ag('read_only'))

    def testServerManagement(self):
        acl = self.folder.acl_users
        self.assertEqual(len(acl.getServers()), 1)
        acl.manage_addServer('ldap.some.com', port=636, use_ssl=1)
        self.assertEqual(len(acl.getServers()), 2)
        acl.manage_addServer('ldap.some.com', port='636', use_ssl=1)
        self.assertEqual(len(acl.getServers()), 2)
        acl.manage_addServer('localhost')
        self.assertEqual(len(acl.getServers()), 2)
        acl.manage_deleteServers([1])
        self.assertEqual(len(acl.getServers()), 1)
        acl.manage_deleteServers()
        self.assertEqual(len(acl.getServers()), 1)

        acl.manage_addServer('ldap.some.com', port=636, use_ssl=1)
        svr = [x for x in acl.getServers() if x['host'] == 'ldap.some.com'][0]
        self.assertEquals(svr['conn_timeout'], 5)
        self.assertEquals(svr['op_timeout'], -1)
        acl.manage_addServer( 'ldap.some.com'
                            , port=636
                            , use_ssl=1
                            , op_timeout=10
                            , conn_timeout=15
                            )
        svr = [x for x in acl.getServers() if x['host'] == 'ldap.some.com'][0]
        self.assertEquals(svr['conn_timeout'], 15)
        self.assertEquals(svr['op_timeout'], 10)

    def testImplicitMapping(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        ae(len(acl.getGroupMappings()), 0)
        have_roles = ['ldap_group', 'some_group']
        ae(acl._mapRoles(have_roles), [])
        gp = acl.getProperty
        ae(gp('_implicit_mapping'), 0)
        acl.manage_edit( title = gp('title')
                       , login_attr = gp('login_attr')
                       , uid_attr = gp('uid_attr')
                       , users_base = gp('users_base')
                       , users_scope = gp('users_scope')
                       , roles = gp('roles')
                       , groups_base = gp('groups_base')
                       , groups_scope = gp('groups_scope')
                       , binduid = gp('binduid')
                       , bindpwd = gp('bindpwd')
                       , binduid_usage = gp('binduid_usage')
                       , rdn_attr = gp('rdn_attr')
                       , obj_classes = gp('obj_classes')
                       , local_groups = gp('local_groups')
                       , implicit_mapping = 1
                       , encryption = gp('encryption')
                       , read_only = gp('read_only')
                       )
        ae(gp('_implicit_mapping'), 1)
        mapped_roles = acl._mapRoles(have_roles)
        ae(len(mapped_roles), 2)
        for role in have_roles:
            self.assert_(role in mapped_roles)
        acl.manage_edit( title = gp('title')
                       , login_attr = gp('login_attr')
                       , uid_attr = gp('uid_attr')
                       , users_base = gp('users_base')
                       , users_scope = gp('users_scope')
                       , roles = gp('roles')
                       , groups_base = gp('groups_base')
                       , groups_scope = gp('groups_scope')
                       , binduid = gp('binduid')
                       , bindpwd = gp('bindpwd')
                       , binduid_usage = gp('binduid_usage')
                       , rdn_attr = gp('rdn_attr')
                       , obj_classes = gp('obj_classes')
                       , local_groups = gp('local_groups')
                       , implicit_mapping = 0
                       , encryption = gp('encryption')
                       , read_only = gp('read_only')
                       )
        ae(gp('_implicit_mapping'), 0)

    def testGroupMapping(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        ae(len(acl.getGroupMappings()), 0)
        have_roles = ['ldap_group', 'some_group']
        ae(acl._mapRoles(have_roles), [])
        acl.manage_addGroupMapping('ldap_group', 'Manager')
        ae(len(acl.getGroupMappings()), 1)
        roles = acl._mapRoles(have_roles)
        ae(len(roles), 1)
        self.assert_('Manager' in roles)
        acl.manage_deleteGroupMappings('unknown')
        ae(len(acl.getGroupMappings()), 1)
        acl.manage_deleteGroupMappings(['ldap_group'])
        ae(len(acl.getGroupMappings()), 0)
        ae(acl._mapRoles(have_roles), [])

    def testLDAPSchema(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        ae(len(acl.getLDAPSchema()), 2)
        ae(len(acl.getSchemaDict()), 2)
        acl.manage_addLDAPSchemaItem( 'mail'
                                    , 'Email'
                                    , ''
                                    , 'public'
                                    )
        ae(len(acl.getLDAPSchema()), 3)
        ae(len(acl.getSchemaDict()), 3)
        cur_schema = acl.getSchemaConfig()
        self.assert_('mail' in cur_schema.keys())
        acl.manage_addLDAPSchemaItem( 'cn'
                                    , 'exists'
                                    , ''
                                    , 'exists'
                                    )
        ae(len(acl.getLDAPSchema()), 3)
        ae(len(acl.getSchemaDict()), 3)
        acl.manage_deleteLDAPSchemaItems(['cn', 'unknown', 'mail'])
        ae(len(acl.getLDAPSchema()), 1)
        ae(len(acl.getSchemaDict()), 1)
        cur_schema = acl.getSchemaConfig()
        self.assert_('mail' not in cur_schema.keys())
        self.assert_('cn' not in cur_schema.keys())

    def testSchemaMappedAttrs(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        ae(len(acl.getMappedUserAttrs()), 0)
        acl.manage_addLDAPSchemaItem( 'mail'
                                    , 'Email'
                                    , ''
                                    , 'public'
                                    )
        ae(len(acl.getMappedUserAttrs()), 1)
        ae(acl.getMappedUserAttrs(), (('mail', 'public'),))
        acl.manage_deleteLDAPSchemaItems(['mail'])
        ae(len(acl.getMappedUserAttrs()), 0)

    def testSchemaMultivaluedAttrs(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        ae(len(acl.getMultivaluedUserAttrs()), 0)
        acl.manage_addLDAPSchemaItem( 'mail'
                                    , 'Email'
                                    , 'yes'
                                    , 'public'
                                    )
        ae(len(acl.getMultivaluedUserAttrs()), 1)
        ae(acl.getMultivaluedUserAttrs(), ('mail',))

    def testAddUser(self):
        acl = self.folder.acl_users
        ae=self.assertEqual
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
            acl.manage_addGroupMapping(role, role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(msg.split(' ')[0] == 'ALREADY_EXISTS')
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        for role in ug('user_roles'):
            self.assert_(role in user_ob.getRoles())
        for role in acl.getProperty('_roles'):
            self.assert_(role in user_ob.getRoles())
        ae(user_ob.getProperty('cn'), ug('cn'))
        ae(user_ob.getProperty('sn'), ug('sn'))
        ae(user_ob.getId(), ug(acl.getProperty('_uid_attr')))
        ae(user_ob.getUserName(), ug(acl.getProperty('_login_attr')))

    def testAddUserReadOnly(self):
        acl = self.folder.acl_users
        acl.read_only = 1
        acl._delegate.read_only = 1
        ae=self.assertEqual
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(msg)
        user_ob = acl.getUser(ug('cn'))
        ae(user_ob, None)

    def testGetUser(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_ob = acl.getUserByDN(user_ob.getUserDN())
        self.assertNotEqual(user_ob, None)
        user_ob = acl.getUserById(ug(acl.getProperty('_uid_attr')))
        self.assertNotEqual(user_ob, None)
        self.assertEqual(len(acl.getUserNames()), 1)

    def testGetUserWrongObjectclasses(self):
        acl = self.folder.acl_users

        for role in u2g('user_roles'):
            acl.manage_addGroup(role)

        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assert_(not msg)

        # Adding a new user will always add it with the object classes set
        # on the Configure tab. Need to do some more or less nasty munging
        # to put the undesirable object classes on this user!
        acl.manage_addLDAPSchemaItem( 'objectClass'
                                    , multivalued='1'
                                    )
        user_ob = acl.getUser(u2g(acl.getProperty('_login_attr')))
        ob_class_string = ';'.join(u2g('objectClasses'))
        acl.manage_editUser( user_ob.getUserDN()
                           , REQUEST=None
                           , kwargs={ 'objectClass' : ob_class_string }
                           )

        user_ob = acl.getUser(u2g(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob, None)

        user_ob = acl.getUserById(u2g(acl.getProperty('_uid_attr')))
        self.assertEqual(user_ob, None)

        results = acl.findUser('cn', u2g('cn'))
        self.assertEqual(len(results), 0)

    def testFindUser(self):
        # test finding a user with specific or wildcard match on one attribute
        acl = self.folder.acl_users

        for role in u2g('user_roles'):
            acl.manage_addGroup(role)

        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assert_(not msg)

        key = acl.getProperty('_login_attr')
        user_cn = u2g(key)
        crippled_cn = user_cn[:-1]

        # Search on a bogus attribute, must return error result
        result = acl.findUser('foobarkey', 'baz')
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get('sn'), 'Error')

        # Search on valid attribute with invalid term, must return empty result
        result = acl.findUser(key, 'invalid_cn')
        self.assertEquals(len(result), 0)

        # We can also try this through the extra user filter
        acl._extra_user_filter = "(%s=%s)" % (key, "invalid_cn")
        result = acl.findUser(key, user_cn)
        self.assertEquals(len(result), 0)
        acl._extra_user_filter = ''

        # Search with wildcard - both user_cn and crippled_cn must return
        # the data for user2.
        result = acl.findUser(key, user_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.findUser(key, crippled_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        # Repeat the previous two searches by asking for the friendly name
        # assigned to the cn ("Canonical Name")
        result = acl.findUser('Canonical Name', user_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.findUser('Canonical Name', crippled_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        # Test the mapped public name by putting one into the schema
        # by force, then asking for it
        acl._ldapschema['cn']['public_name'] = 'Comic Name'
        result = acl.findUser('Comic Name', user_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.findUser('Comic Name', crippled_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        # Now we ask for exact matches. Only user_cn returns results.
        result = acl.findUser(key, user_cn, exact_match=True)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.findUser(key, crippled_cn, exact_match=True)
        self.assertEquals(len(result), 0)


    def testSearchGroups(self):
        # test finding a group with specific or wildcard match on
        # multiple attributes
        acl = self.folder.acl_users

        # let's create some users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assert_(not msg)
        # and put them in groups that match the uniqueMember shortcut in fakeldap
        ldapconn = acl._delegate.connect()
        group_cn = 'group1'
        crippled_cn = group_cn[:-1]
        group_description = 'a description'
        ldapconn.add_s("cn=" + group_cn + "," + dg('groups_base'),
                       dict(objectClass=['groupOfUniqueNames', 'top'],
                            uniqueMember=['cn=test2,' + dg('users_base')],
                            description=[group_description],
                            mail=['group1@example.com'],
                            ).items())

        # now let's check these groups work
        u = acl.getUser('test2')
        self.failIf('Manager' in u.getRoles())
        acl.manage_addGroupMapping(group_cn, 'Manager')
        u = acl.getUser('test2')
        self.failIf('Manager' not in u.getRoles())

        # ok, so now we can try group searches by attributes
        # Search on a bogus attribute, must return error result
        result = acl.searchGroups(foobarkey='baz')
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get('cn'), 'n/a')

        # Search on valid attribute with invalid term, must return empty result
        result = acl.searchGroups(cn='invalid_cn', description=group_description)
        self.assertEquals(len(result), 0, result)

        # Search with wildcard - both user_cn and crippled_cn must return
        # the data for user2.
        result = acl.searchGroups(cn=group_cn, description=group_description)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get('cn'), group_cn)

        result = acl.searchGroups(cn=crippled_cn, description=group_description)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get('cn'), group_cn)

        # Now we ask for exact matches. Only group_cn returns results.
        result = acl.searchGroups( cn=group_cn
                                 , description=group_description
                                 , exact_match=True
                                 )
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get('cn'), group_cn)

        result = acl.searchGroups( cn=crippled_cn
                                 , description=group_description
                                 , exact_match=True
                                 )
        self.assertEquals(len(result), 0)

    def testSearchUsers(self):
        # test finding a user with specific or wildcard match on
        # multiple attributes
        acl = self.folder.acl_users

        for role in u2g('user_roles'):
            acl.manage_addGroup(role)

        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assert_(not msg)

        key = acl.getProperty('_login_attr')
        user_cn = u2g(key)
        crippled_cn = user_cn[:-1]
        user_sn = u2g('sn')
        crippled_sn = user_sn[:-1]

        # Search on a bogus attribute, must return error result
        result = acl.searchUsers(foobarkey='baz')
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get('sn'), 'Error')

        # Search on valid attribute with invalid term, must return empty result
        result = acl.searchUsers(cn='invalid_cn', sn=user_sn)
        self.assertEquals(len(result), 0)

        # Search with wildcard - both user_cn and crippled_cn must return
        # the data for user2.
        result = acl.searchUsers(cn=user_cn, sn=user_sn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.searchUsers(cn=crippled_cn, sn=crippled_sn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        # Now we ask for exact matches. Only user_cn returns results.
        result = acl.searchUsers(cn=user_cn, sn=user_sn, exact_match=True)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.searchUsers( cn=crippled_cn
                                , sn=crippled_sn
                                , exact_match=True
                                )
        self.assertEquals(len(result), 0)

        # Weird edge case: Someone put "dn" into the LDAP Schema tab and
        # searched for that
        acl.manage_addLDAPSchemaItem('dn', 'DN')
        user2_dn = 'cn=%s,%s' % (user_cn, acl.users_base)
        result = acl.searchUsers(dn=user2_dn, exact_match=True)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)


    def testGetUserNames(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        expected = [`x` for x in range(100)]
        expected.sort()
        for name in expected:
            u = user.copy()
            u['cn'] = name
            u['sn'] = name
            msg = acl.manage_addUser(REQUEST=None, kwargs=u)
            self.assert_(not msg)
        userlist = acl.getUserNames()
        self.assertEqual(userlist, tuple(expected))

    def testUserIds(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        expected = [`x` for x in range(100)]
        expected.sort()
        for name in expected:
            u = user.copy()
            u['cn'] = name
            u['sn'] = name
            msg = acl.manage_addUser(REQUEST=None, kwargs=u)
            self.assert_(not msg)
        userlist = acl.getUserIds()
        self.assertEqual(userlist, tuple(expected))

    def testUserIdsAndNames(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        expected = [(`x`, `x`) for x in range(100)]
        expected.sort()
        for name in expected:
            u = user.copy()
            u['cn'] = name[0]
            u['sn'] = name[1]
            msg = acl.manage_addUser(REQUEST=None, kwargs=u)
            self.assert_(not msg)
        userlist = acl.getUserIdsAndNames()
        self.assertEqual(userlist, tuple(expected))

    def testAuthenticateUser(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.authenticate( ug(acl.getProperty('_login_attr'))
                                  , ug('user_pw')
                                  , {}
                                  )
        self.assertNotEqual(user_ob, None)
        user_ob = acl.authenticate( ug(acl.getProperty('_login_attr'))
                                  , ''
                                  , {}
                                  )
        self.assertEqual(user_ob, None)
        user_ob = acl.authenticate( ug(acl.getProperty('_login_attr'))
                                  , 'falsepassword'
                                  , {}
                                  )
        self.assertEqual(user_ob, None)

    def testAuthenticateUserWithCache(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)

        user_ob = acl.authenticate( ug(acl.getProperty('_login_attr'))
                        , 'falsepassword'
                        , {}
                        )

        # make sure the user could not connect
        self.assertEqual(user_ob, None)

        # now let's try again with the right password
        user_ob = acl.authenticate( ug(acl.getProperty('_login_attr'))
                        , ug('user_pw')
                        , {}
                        )
    
        # now we should be OK
        self.assertNotEqual(user_ob, None)

    def testDeleteUser(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assert_(not msg)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertNotEqual(mgr_ob, None)
        newSecurityManager({}, mgr_ob)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        acl.manage_deleteUsers([user_dn])
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob, None)
        self.assertEqual(acl.getGroups(dn=user_dn), [])
        noSecurityManager()

    def testDeleteUserReadOnly(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        acl.read_only = 1
        acl._delegate.read_only = 1
        acl.manage_deleteUsers([user_dn])
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assertNotEqual(acl.getGroups(dn=user_dn), [])

    def testEditUser(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        msg = acl.manage_editUser(user_dn, kwargs={'sn' : 'New'})
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob.getProperty('sn'), 'New')

    def testEditUserMultivalueHandling(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        msg = acl.manage_editUser(user_dn, kwargs={'sn' : 'New; Lastname'})
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob.getProperty('sn'), 'New; Lastname')

    def testEditUserReadOnly(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        acl.read_only = 1
        acl._delegate.read_only = 1
        msg = acl.manage_editUser(user_dn, kwargs={'sn' : 'New'})
        self.assert_(msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob.getProperty('sn'), ug('sn'))

    def testEditUserPassword(self):
        conn = fakeldap.FakeLDAPConnection()
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        res = conn.search_s(user_ob.getUserDN(), scope=ldap.SCOPE_BASE)
        old_pw = res[0][1]['userPassword'][0]
        acl.manage_editUserPassword(user_dn, 'newpass')
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        res = conn.search_s(user_ob.getUserDN(), scope=ldap.SCOPE_BASE)
        new_pw = res[0][1]['userPassword'][0]
        self.assertNotEqual(old_pw, new_pw)

    def testEditUserPasswordReadOnly(self):
        conn = fakeldap.FakeLDAPConnection()
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        res = conn.search_s(user_ob.getUserDN(), scope=ldap.SCOPE_BASE)
        old_pw = res[0][1]['userPassword'][0]
        acl.read_only = 1
        acl._delegate.read_only = 1
        acl.manage_editUserPassword(user_dn, 'newpass')
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        res = conn.search_s(user_ob.getUserDN(), scope=ldap.SCOPE_BASE)
        new_pw = res[0][1]['userPassword'][0]
        self.assertEqual(old_pw, new_pw)

    def testEditUserRoles(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
            acl.manage_addGroupMapping(role, role)
        new_role = 'Privileged'
        acl.manage_addGroup(new_role)
        acl.manage_addGroupMapping(new_role, new_role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assert_(new_role not in user_ob.getRoles())
        user_dn = user_ob.getUserDN()
        acl.manage_editUserRoles(user_dn, ['Manager', new_role])
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assert_(new_role in user_ob.getRoles())

    def testEditUserRolesReadOnly(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        new_role = 'Privileged'
        acl.manage_addGroup(new_role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assert_(new_role not in user_ob.getRoles())
        user_dn = user_ob.getUserDN()
        acl._delegate.read_only = 1
        acl.manage_editUserPassword(user_dn, 'newpass')
        acl.manage_editUserRoles(user_dn, ['Manager', new_role])
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assert_(new_role not in user_ob.getRoles())

    def testUserMappedAttrs(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        ae(len(acl.getMappedUserAttrs()), 0)
        acl.manage_addLDAPSchemaItem( 'mail'
                                    , 'Email'
                                    , ''
                                    , 'email'
                                    )
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertEqual(ug('mail'), user_ob.getProperty('mail'))
        self.assertEqual(ug('mail'), user_ob.getProperty('email'))


    def testModRDN(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
            acl.manage_addGroupMapping(role, role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assert_(not msg)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertNotEqual(mgr_ob, None)
        newSecurityManager({}, mgr_ob)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        msg = acl.manage_editUser(user_dn, kwargs={'cn' : 'new'})
        user_ob = acl.getUser('new')
        ae(user_ob.getProperty('cn'), 'new')
        ae(user_ob.getId(), 'new')
        new_dn = 'cn=new,%s' % acl.getProperty('users_base')
        ae(user_ob.getUserDN(), new_dn)
        for role in ug('user_roles'):
            self.assert_(role in user_ob.getRoles())
        for role in acl.getProperty('_roles'):
            self.assert_(role in user_ob.getRoles())
        noSecurityManager()

    def testSetUserProperty(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assert_(not msg)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertNotEqual(mgr_ob, None)
        self.assertEqual( mgr_ob.getProperty('sn')
                        , manager_user.get('sn')
                        )
        acl.manage_setUserProperty( mgr_ob.getUserDN()
                                  , 'sn'
                                  , 'NewLastName'
                                  )
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual( mgr_ob.getProperty('sn')
                        , 'NewLastName'
                        )

    def testSetUserPropertyMultivalueHandling(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assert_(not msg)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertNotEqual(mgr_ob, None)
        self.assertEqual( mgr_ob.getProperty('sn')
                        , manager_user.get('sn')
                        )
        acl.manage_setUserProperty( mgr_ob.getUserDN()
                                  , 'sn'
                                  , 'NewLastName; Secondlastname'
                                  )
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual( mgr_ob.getProperty('sn')
                       , 'NewLastName; Secondlastname'
                       )

    def testSetUserPropertyBinaryHandling(self):
        # Make sure binary attributes are never converted
        test_home = package_home(globals())
        image_path = os.path.join(test_home, 'test.jpg')
        image_file = open(image_path, 'rb')
        image_contents = image_file.read()
        image_file.close()
        acl = self.folder.acl_users
        acl.manage_addLDAPSchemaItem('jpegPhoto', binary=True)
        acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), '')
        acl.manage_setUserProperty( mgr_ob.getUserDN()
                                  , 'jpegPhoto'
                                  , image_contents
                                  )
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), image_contents)

    def testManageEditUserBinaryHandling(self):
        # Make sure binary attributes are never converted
        test_home = package_home(globals())
        image_path = os.path.join(test_home, 'test.jpg')
        image_file = open(image_path, 'rb')
        image_contents = image_file.read()
        image_file.close()
        acl = self.folder.acl_users
        acl.manage_addLDAPSchemaItem('jpegPhoto', binary=True)
        acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), '')
        acl.manage_editUser( mgr_ob.getUserDN()
                           , kwargs={'jpegPhoto':image_contents}
                           )
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), image_contents)

    def testManageAddUserBinaryHandling(self):
        # Make sure binary attributes are never converted
        test_home = package_home(globals())
        image_path = os.path.join(test_home, 'test.jpg')
        image_file = open(image_path, 'rb')
        image_contents = image_file.read()
        image_file.close()
        acl = self.folder.acl_users
        acl.manage_addLDAPSchemaItem('jpegPhoto', binary=True)
        kw_args = copy.deepcopy(manager_user)
        kw_args['jpegPhoto'] = image_contents
        acl.manage_addUser(REQUEST=None, kwargs=kw_args)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), image_contents)

    def testGetAttributesOfAllObjects(self):
        # Test the resilience of the getAttributesOfAllUsers method
        # Even if problems are encountered, the resultset should have
        # keys for each attribute asked for.
        acl = self.folder.acl_users

        # I'm adding a user to prevent a log message from the LDAPUserFolder
        # about not finding any users under Zope 2.8.x
        acl.manage_addUser(REQUEST=None, kwargs=manager_user)

        search_string = '(objectClass=*)'
        attributes = ['foobar', 'baz']
        res = acl.getAttributesOfAllObjects( acl.getProperty('users_base')
                                           , acl.getProperty('users_scope')
                                           , search_string
                                           , attributes
                                           )

        for attr in attributes:
            self.failUnless(res.has_key(attr))

    def testGroupLifecycle_nonutf8(self):
        # http://www.dataflake.org/tracker/issue_00527
        # Make sure groups with non-UTF8/non-ASCII characters can be
        # added and deleted.
        groupid = 'gr\xc3\xbcppe' # Latin-1 Umlaut-U
        acl = self.folder.acl_users

        # Add the group with the odd character in it
        acl.manage_addGroup(groupid)
        all_groups = acl.getGroups()

        # Only one group record should exist, the one we just entered
        self.failUnless(len(all_groups) == 1)
        self.failUnless(all_groups[0][0] == groupid)

        # Now delete the group. The DN we get back from getGroups will have been
        # recoded into whatever is set in utils.py (normally latin-1). Due to
        # a lack of encoding into UTF-8 in the deletion code, the deletion
        # would fail silently and the group would still exist.
        group_dn = all_groups[0][1]
        acl.manage_deleteGroups(dns=[group_dn])
        self.failUnless(len(acl.getGroups()) == 0)

    def testNegativeCaching(self):
        ae = self.assertEqual
        acl = self.folder.acl_users

        ae(len(acl._cache('negative').getCache()), 0)
        ae(acl.getUser('missing'), None)
        ae(len(acl._cache('negative').getCache()), 1)
        acl.manage_addUser(REQUEST=None, kwargs=user)
        ae(len(acl._cache('negative').getCache()), 0)


    def testNegativeCachePoisoning(self):
        # Test against cache poisoning
        # https://bugs.launchpad.net/bugs/695821
        # The requested attribute value is part of the cache key now
        ae = self.assertEqual
        acl = self.folder.acl_users

        # Prep: Make sure the login and UID attributes are different
        old_login_attr = acl._login_attr
        old_uid_attr = acl._uid_attr
        acl._login_attr = 'cn'
        acl._uid_attr = 'uid'

        # Lookup by the login attrbute
        ignored = acl.getUser('missing2')
        ignored = acl.getUser('missing2')
        ae(len(acl._cache('negative').getCache()), 1)

        # Lookup by the UID
        ignored = acl.getUserById('missing2')
        ignored = acl.getUserById('missing2')
        ae(len(acl._cache('negative').getCache()), 2)

        # Lookup by arbitrary attribute
        ignored = acl.getUserByAttr('sn', 'missing2', cache=True)
        ignored = acl.getUserByAttr('sn', 'missing2', cache=True)
        ae(len(acl._cache('negative').getCache()), 3)

        # _expireUser only removes entries for the login and UID
        acl._expireUser('missing2')
        ae(len(acl._cache('negative').getCache()), 1)

        # Cleanup
        acl._login_attr = old_login_attr
        acl._uid_attr = old_uid_attr


    def testGroupsWithCharactersNeedingEscaping(self):
        # http://www.dataflake.org/tracker/issue_00507
        # Make sure groups with hash characters can be
        # added, deleted and used
        groupid = '"#APPLIKATIONEN LAUFWERK(a)#"'
        acl = self.folder.acl_users

        # Add the group with the odd character in it
        acl.manage_addGroup(groupid)
        all_groups = acl.getGroups()

        # Only one group record should exist, the one we just entered
        self.failUnless(len(all_groups) == 1)
        self.failUnless(all_groups[0][0] == groupid)

        # Now delete the group.
        group_dn = all_groups[0][1]
        # XXX Shortcoming in fakeldap: DNs are not "unescaped", meaning escaping
        # done during insertion will be retained in the real record, unlike
        # a real LDAP server which will store and return unescaped DNs.
        # That means we cannot use the returned DN, we must construct it anew.
        group_dn = 'cn=%s,%s' % (groupid, acl.groups_base)
        acl.manage_deleteGroups(dns=[group_dn])
        self.failUnless(len(acl.getGroups()) == 0)

    def testGetUserFilterString(self):
        acl = self.folder.acl_users
        filt_string = acl._getUserFilterString()
        for ob_class in acl.getProperty('_user_objclasses'):
            self.failUnless('(objectclass=%s)' % ob_class.lower() 
                                 in filt_string.lower())
        self.failUnless('(%s=*)' % dg('uid_attr') in filt_string.lower())

        filters = ['(uid=test)', '(cn=test)']
        filt_string = acl._getUserFilterString(filters=filters)
        for ob_class in acl.getProperty('_user_objclasses'):
            self.failUnless('(objectclass=%s)' % ob_class.lower() 
                                 in filt_string.lower())
        for filt in filters:
            self.failUnless(filt in filt_string)
        self.failIf('(%s=*)' % dg('uid_attr') in filt_string.lower())

        # Set up some different values
        acl.manage_edit( title = ag('title')
                       , login_attr = ag('login_attr')
                       , uid_attr = ag('uid_attr')
                       , users_base = ag('users_base')
                       , users_scope = ag('users_scope')
                       , roles= ag('roles')
                       , groups_base = ag('groups_base')
                       , groups_scope = ag('groups_scope')
                       , binduid = ag('binduid')
                       , bindpwd = ag('bindpwd')
                       , binduid_usage = ag('binduid_usage')
                       , rdn_attr = ag('rdn_attr')
                       , local_groups = ag('local_groups')
                       , implicit_mapping = ag('implicit_mapping')
                       , encryption = ag('encryption')
                       , read_only = ag('read_only')
                       , obj_classes = ag('obj_classes')
                       , extra_user_filter = ag('extra_user_filter')
                       )

        filt_string = acl._getUserFilterString()
        for ob_class in acl.getProperty('_user_objclasses'):
            self.failUnless('(objectclass=%s)' % ob_class.lower() 
                                 in filt_string.lower())
        self.failUnless(ag('extra_user_filter') in filt_string)
        self.failUnless('(%s=*)' % ag('uid_attr') in filt_string)

        filters = ['(uid=test)', '(cn=test)']
        filt_string = acl._getUserFilterString(filters=filters)
        for ob_class in acl.getProperty('_user_objclasses'):
            self.failUnless('(objectclass=%s)' % ob_class.lower() 
                                 in filt_string.lower())
        for filt in filters:
            self.failUnless(filt in filt_string)
        self.failIf('(%s=*)' % ag('uid_attr') in filt_string)


    def test_expireUser(self):
        # http://www.dataflake.org/tracker/issue_00617 etc.
        try:
            from hashlib import sha1 as sha_new
        except ImportError:
            from sha import new as sha_new

        acl = self.folder.acl_users
    
        # Retrieving an invalid user should return None
        nonexisting = acl.getUserById('invalid')
        self.failUnless(nonexisting is None)
    
        # The retrieval above will add the invalid user to the negative cache
        negative_cache_key = '%s:%s:%s' % ( acl._uid_attr
                                          , 'invalid'
                                          , sha_new('').hexdigest()
                                          )
        self.failIf(acl._cache('negative').get(negative_cache_key) is None)
    
        # Expiring the user must remove it from the negative cache
        acl._expireUser('invalid')
        self.failUnless(acl._cache('negative').get(negative_cache_key) is None)

        # User IDs that come in as unicode should not break anything.
        # https://bugs.launchpad.net/bugs/700071
        acl._expireUser(u'invalid')

    def test_manage_reinit(self):
        # part of http://www.dataflake.org/tracker/issue_00629
        acl = self.folder.acl_users
        old_hash = acl._hash

        # Fill some caches
        acl._misc_cache().set('foo', 'bar')
        self.assertEquals(acl._misc_cache().get('foo'), 'bar')
        dummy = LDAPDummyUser('user1', 'pass')
        acl._cache('authenticated').set('user1', dummy)
        self.assertEquals(acl._cache('authenticated').get('user1'), dummy)
        acl._cache('anonymous').set('user1', dummy)
        self.assertEquals(acl._cache('anonymous').get('user1'), dummy)
        acl._cache('negative').set('user1', dummy)
        self.assertEquals(acl._cache('negative').get('user1'), dummy)

        acl.manage_reinit()
        self.failIf(acl._misc_cache().get('foo'))
        self.failIf(acl._cache('authenticated').get('user1'))
        self.failIf(acl._cache('anonymous').get('user1'))
        self.failIf(acl._cache('negative').get('user1'))
        self.failIf(acl._hash == old_hash)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLDAPUserFolder))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

