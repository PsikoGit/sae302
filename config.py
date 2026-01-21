#!/bin/env python3

class Config:
    SQLALCHEMY_DATABASE_URI = 'mariadb+mariadbconnector://qamu:qamu@localhost/sae302'
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True,'pool_recycle':3600,'pool_size':10}
    SECRET_KEY = '123456789AZERTYazertyLaClefSuperSecreteMagique'
