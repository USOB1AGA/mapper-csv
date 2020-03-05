import os
import sys
import argparse
import json
import re
from datetime import datetime
import time

#=========================
class csv_functions():

    #----------------------------------------
    def __init__(self):
        self.initialized = True
        self.statPack = {}

        self.variantFile = __file__.replace('.py', '.json')
        if not os.path.exists(self.variantFile):
            print('')
            print('File %s is missing!' % self.variantFile)
            print('')
            self.initialized = False
            return

        try: self.variantJson = json.load(open(self.variantFile,'r', encoding='latin-1'))
        except json.decoder.JSONDecodeError as err:
            print('')
            print('JSON error %s in %s' % (err, self.variantFile))
            print('')
            self.initialized = False
            return

        #--ensure these lists exist
        if 'GARBAGE_VALUES' not in self.variantJson:
            self.variantJson['GARBAGE_VALUES'] = []
        if 'ORGANIZATION_TOKENS' not in self.variantJson:
            self.variantJson['ORGANIZATION_TOKENS'] = []
        if 'PERSON_TOKENS' not in self.variantJson:
            self.variantJson['PERSON_TOKENS'] = []
        if 'SENZING_ATTRIBUTES' not in self.variantJson:
            self.variantJson['SENZING_ATTRIBUTES'] = []

        #--turn lists into dictionaries for speed
        self.variantData = {}
        for variantList in self.variantJson:
            if type(self.variantJson[variantList]) == list:
                self.variantData[variantList] = dict(zip([i.upper() for i in self.variantJson[variantList]], [''] * len(self.variantJson[variantList])))
            else:
                self.variantData[variantList] = self.variantJson[variantList]

        #--supported date formats
        self.dateFormats = []
        self.dateFormats.append("%Y-%m-%d")
        self.dateFormats.append("%m/%d/%Y")
        self.dateFormats.append("%d/%m/%Y")
        self.dateFormats.append("%d-%b-%Y")
        self.dateFormats.append("%Y")
        self.dateFormats.append("%Y-%M")
        self.dateFormats.append("%m-%Y")
        self.dateFormats.append("%m/%Y")
        self.dateFormats.append("%b-%Y")
        self.dateFormats.append("%b/%Y")
        self.dateFormats.append("%m-%d")
        self.dateFormats.append("%m/%d")
        self.dateFormats.append("%b-%d")
        self.dateFormats.append("%b/%d")
        self.dateFormats.append("%d-%m")
        self.dateFormats.append("%d/%m")
        self.dateFormats.append("%d-%b")
        self.dateFormats.append("%d/%b")

        #--set iso country code size 
        self.isoCountrySize = 'ISO3'
    
    #----------------------------------------
    def format_date(self, dateString, outputFormat = None):
        for dateFormat in self.dateFormats:
            try: dateValue = datetime.strptime(dateString, dateFormat)
            except: pass
            else: 
                if not outputFormat:
                    if len(dateString) == 4:
                        outputFormat = '%Y'
                    elif len(dateString) in (5,6):
                        outputFormat = '%m-%d'
                    elif len(dateString) in (7,8):
                        outputFormat = '%Y-%m'
                    else:
                        outputFormat = '%Y-%m-%d'
                return datetime.strftime(dateValue, outputFormat)
        return None

    #-----------------------------------
    def clean_value(self, valueString):
        #--remove extra spaces
        returnValue = ' '.join(str(valueString).strip().split())
        if returnValue.upper() in self.variantData['GARBAGE_VALUES']:
            returnValue = ''
        return returnValue

    #-----------------------------------
    def is_senzing_attribute(self, attrName):
        attrName = attrName.upper()
        if attrName in self.variantData['SENZING_ATTRIBUTES']:
            return True
        elif '_' in attrName:
            baseName = attrName[attrName.find('_') + 1:]
            if baseName in self.variantData['SENZING_ATTRIBUTES']:
                return True
            else:
                baseName = attrName[0:attrName.rfind('_')]
                if baseName in self.variantData['SENZING_ATTRIBUTES']:
                    return True
        return False

    #-----------------------------------
    def get_senzing_attribute(self, attrName):
        attrName = attrName.upper()
        if attrName in self.variantData['SENZING_ATTRIBUTES']:
            return self.variantData['SENZING_ATTRIBUTES'][attrName]
        return {}

    #-----------------------------------
    def is_organization_name(self, nameString):
        if nameString:
            for token in nameString.replace('.',' ').replace(',',' ').split():
                if token.upper() in self.variantData['ORGANIZATION_TOKENS']:
                    return True
        return False

    #-----------------------------------
    def is_person_name(self, nameString):
        if nameString:
            for token in nameString.replace('.',' ').replace(',',' ').split():
                if token.upper() in self.variantData['PERSON_TOKENS']:
                    return True
        return False

#----------------------------------------
if __name__ == "__main__":
    appPath = os.path.dirname(os.path.abspath(sys.argv[0]))


    #--test the instance
    csvFunctions = csv_functions()
    if not csvFunctions.initialized:
        sys.exit(1)

    #--see if they entered arguments
    argStr = ' '.join(sys.argv[1:])
    if len(sys.argv) == 1 or 'help' in argStr.lower() or '-h' in argStr.lower():
        print()
        print('possible commands ...')
        print('\tdisplay lists')
        print('\tadd <token> to <list>')
        #print('\tdelete token from list')
        print('\tadd file asdf.txt to list')
        print()
        sys.exit(0)

    if argStr.lower() == 'display lists':
        print()
        for key in csvFunctions.variantJson.keys():
            print (key)
        print()
        sys.exit(0)

    if sys.argv[1].lower() == 'add' and len(sys.argv) >= 5: 
        variantTokens = []
        fileName = ''
        targetList = ''
        priorToken = ''
        for token in sys.argv[2:]:
            if priorToken == 'file':
                fileName = token
            elif priorToken == 'to':
                targetList = token
            elif token.lower() not in ('file', 'to'):
                variantTokens.append(token)
            priorToken = token.lower()

        variant = ' '.join(variantTokens).upper()
        targetList = targetList.upper()
        errorText = ''

        if targetList not in csvFunctions.variantJson:
            print()
            ok = input('%s is not a current list, create it? (Y/n) ' % targetList)
            if ok.upper().startswith('Y'):
                csvFunctions.variantJson[targetList] = []
            else:
                errorText = 'aborted!'
        elif fileName and variant:
            #print ('fileName = %s' % fileName)
            #print ('variant = %s' % variant)
            errorText = 'command not recognized'
        elif fileName and not os.path.exists(fileName):
            errorText = '%s not found' % fileName

        if errorText:
            print()
            print(errorText)
            print()
            sys.exit(1)
        else:

            print()
            addCnt = 0
            skipCnt = 0
            if fileName:
                variantList = [line. rstrip('\n') for line in open(fileName)]
            else:
                variantList = [variant]
            for variant in variantList:
                variant = variant.upper()
                if variant in csvFunctions.variantJson[targetList]:
                    print('exists: %s' % variant)
                    skipCnt += 1
                else:
                    csvFunctions.variantJson[targetList].append(variant)
                    print('added: %s' % variant)
                    addCnt += 1
            print()
            if addCnt > 0:
                print()
                ok = input('ok to save? (Y/n) ')
                if ok.upper().startswith('Y'):

                    #--ensures lists are sorted
                    for variantList in csvFunctions.variantJson:
                        if type(csvFunctions.variantJson[variantList]) == list:
                            csvFunctions.variantJson[variantList] = sorted(csvFunctions.variantJson[variantList])
                    #--write to file
                    with open(csvFunctions.variantFile, 'w') as f:
                        json.dump(csvFunctions.variantJson, f, indent=4, sort_keys = True)
                    print()
                    print('saved!')
                    print()

            sys.exit(0)


    print()
    print('command not recognized')
    print()
    sys.exit(1)
