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
""" Tests for the LDAPDelegate class

$Id: test_LDAPDelegate.py 1695 2009-02-08 08:21:58Z jens $
"""

import unittest


class TestSimple(unittest.TestCase):

    def _getTargetClass(self):
        from Products.LDAPUserFolder.LDAPDelegate import LDAPDelegate

        return LDAPDelegate

    def _makeOne(self, *args, **kw):
        klass = self._getTargetClass()

        return klass(*args, **kw)

    def test_clean_dn(self):
        # http://www.dataflake.org/tracker/issue_00623
        delegate = self._makeOne()
        dn = 'cn="Joe Miller, Sr.", ou="odds+sods <1>", dc="host;new"'
        dn_clean = 'cn=Joe Miller\\, Sr.,ou=odds\\+sods \\<1\\>,dc=host\\;new'
        self.assertEquals(delegate._clean_dn(dn), dn_clean)
        
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSimple))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
