.. python-xbee documentation master file, created by
   sphinx-quickstart on Sat Jul 24 22:28:51 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-xbee's documentation!
=======================================

.. module:: xbee

Introduction
------------

The purpose of XBee is to allow one easy access to
the advanced features of an Xbee device from a 
Python application. It provides a semi-complete
implementation of the XBee binary API protocol
and allows a developer to send and receive the
information they desire without dealing with the
raw communication details.

Usage
-----

.. warning::
   
   In order to use an XBee device with this library, API mode
   must be enabled. For instructions about how to do this, see
   the documentation for your XBee device.



API
----

.. autoclass:: xbee.base.XBeeBase
   :members:

.. autoclass:: xbee.XBee
   :members:

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

