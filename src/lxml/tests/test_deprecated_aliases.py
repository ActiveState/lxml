# -*- coding: utf-8 -*-
"""
Tests for the deprecated methods that lxml 5.0 removed and this fork keeps
for code written against lxml 4.x: XPath.evaluate(), parser.setElementClassLookup()
and XSLT.apply().  Each must behave like the supported call it aliases.
"""
from __future__ import absolute_import

import unittest

from lxml import etree

from .common_imports import HelperTestCase


class DeprecatedAliasesTestCase(HelperTestCase):
    def setUp(self):
        super(DeprecatedAliasesTestCase, self).setUp()
        self.root = etree.fromstring(
            b'<r xmlns:n="urn:n"><a>1</a><n:b>2</n:b><a>3</a></r>')

    def test_etxpath_evaluate(self):
        path = etree.ETXPath("{urn:n}b")
        self.assertEqual([e.text for e in path.evaluate(self.root)],
                         [e.text for e in path(self.root)])
        self.assertEqual(["2"], [e.text for e in path.evaluate(self.root)])

    def test_xpath_evaluate_variables(self):
        path = etree.XPath("count(a[. = $v])")
        self.assertEqual(1.0, path.evaluate(self.root, v="3"))
        self.assertEqual(path(self.root, v="3"), path.evaluate(self.root, v="3"))

    def test_xpath_element_evaluator_evaluate(self):
        evaluator = etree.XPathEvaluator(self.root)
        self.assertEqual(2.0, evaluator.evaluate("count(a)"))
        self.assertEqual(evaluator("count(a)"), evaluator.evaluate("count(a)"))

    def test_xpath_document_evaluator_evaluate(self):
        evaluator = etree.XPathEvaluator(etree.ElementTree(self.root))
        self.assertEqual(2.0, evaluator.evaluate("count(//a)"))

    def test_parser_set_element_class_lookup(self):
        class Custom(etree.ElementBase):
            pass
        for parser in (etree.XMLParser(), etree.HTMLParser()):
            parser.setElementClassLookup(
                etree.ElementDefaultClassLookup(element=Custom))
            self.assertTrue(isinstance(etree.fromstring("<x/>", parser), Custom))
            parser.setElementClassLookup()
            self.assertFalse(isinstance(etree.fromstring("<x/>", parser), Custom))

    def test_xslt_apply(self):
        style = etree.XSLT(etree.fromstring(
            b'<xsl:stylesheet version="1.0" '
            b'xmlns:xsl="http://www.w3.org/1999/XSL/Transform">'
            b'<xsl:param name="p" select="0"/>'
            b'<xsl:template match="/"><out>'
            b'<xsl:value-of select="count(//a) + $p"/></out></xsl:template>'
            b'</xsl:stylesheet>'))
        self.assertEqual(str(style(self.root)), str(style.apply(self.root)))
        self.assertEqual("12", style.apply(self.root, p="10").getroot().text)
        self.assertTrue(style.apply(self.root, profile_run=True).xslt_profile
                        is not None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([unittest.defaultTestLoader.loadTestsFromTestCase(
        DeprecatedAliasesTestCase)])
    return suite


if __name__ == '__main__':
    print('to test use test.py %s' % __file__)
