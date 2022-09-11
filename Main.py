import os
from os.path import exists
import re
import requests

# Must install requests module, python -m pip install requests
# Defining the variables.
fullpath = r'C:\xampp\htdocs\kentucky\resources\views\base'
downloadFolderCss = r'C:\xampp\htdocs\kentucky\public\css'
downloadFolderJs = r'C:\xampp\htdocs\kentucky\public\js'
cssTag = """<link rel="stylesheet" href="{{ asset('css/<file>') }}" >""" #MustBeCssTag Ex: <link rel="stylesheet href="<file>" />
jsTag = """<script type="text/javascript" src="{{ asset('js/<file>') }}"></script>""" #MustBeJsTag Ex: <script src="<file>"></script>

fileFlag = False
filesToWork = []

# Validations
if fullpath == '': 
    print("You must specify a file path or folder path")
    quit()
if downloadFolderCss == '' and downloadFolderJs == '' : 
    print('At least one folder Css or JS must be specified')
    quit()

cssTag = cssTag if cssTag != '' else """"<link rel="stylesheet" href="<file>" >"""
jsTag = jsTag  if jsTag != '' else """<script type="text/javascript" src="<file>"></script>"""

# Prepare to validate folders and file existence
paths = [fullpath, downloadFolderCss, downloadFolderJs]
index = 0

for path in paths:
    if path != '':
        validate = os.path.isdir(path)
        if not validate :
            if index != 0:
                print(path + ' directory not exists')
                quit()
            else:
                validate = exists(path)
                if validate:
                    fileFlag = True
                else:
                    print(path + ' file not exists')
                    quit()            
    index += 1

if fileFlag:
    filesToWork.append(paths[0])
else:
    for path, subdirs, files in os.walk(paths[0]):
        for name in files:
            filesToWork.append(os.path.join(path, name))

if len(filesToWork) > 0:
    for filePath in filesToWork:
        urlsToBeReplaced = []
        print('Working on file: '+filePath)
        file = open(filePath, 'r')
        countLine = 0
    
        lines = file.readlines()

        for line in lines:
            # Regex pattern for search url https://stackoverflow.com/questions/6038061/regular-expression-to-find-urls-within-a-string
            urls = re.findall('(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])', line)
            if not len(urls) == 0:
                for url in urls:
                    formated_url = url[0] + '://'+ url[1] + url[2]
                    print('Working on url: '+formated_url)
                    firstPosition = line.find(formated_url)
                    lastPosition = firstPosition + len(formated_url)

                    if firstPosition != -1:
                        urlValidated = line[firstPosition : lastPosition]
                        fileType = urlValidated.split(".").pop()
                        fileName = urlValidated.split("/").pop()

                        flagToDownload = False
                        folderToDownload = ''

                        if fileType == 'css':
                            if downloadFolderCss != '':
                                folderToDownload = downloadFolderCss
                                flagToDownload = True
                                replacePath = cssTag
                        elif fileType == 'js':
                            if downloadFolderJs != '':
                                folderToDownload = downloadFolderJs
                                flagToDownload = True
                                replacePath = jsTag
                        else:
                            print('Not CSS or JS')

                        if flagToDownload:
                            downloadedFilePath = folderToDownload+os.sep+fileName
                            if not os.path.exists(downloadedFilePath):
                                print('Downloading: '+formated_url)
                                response = requests.get(urlValidated)
                                downloadStatus = response.status_code
                                if downloadStatus == 200:
                                    open(downloadedFilePath, "wb").write(response.content)
                                    
                                    termToBeReplaced = replacePath.find('<file>')
                                    
                                    if termToBeReplaced == -1:
                                        replacePath = replacePath + os.sep + '<file>'

                                    replacePath = replacePath.replace('<file>',fileName)

                                    urlObject = {
                                        'urlInFile' : urlValidated,
                                        'newUrlInFile' :  replacePath,
                                        'line' : countLine
                                    }

                                    urlsToBeReplaced.append(urlObject)
                                else:
                                    print('File cannot be downloaded from web')
                            else:
                                print('Cannot download because file already exists')
                    else:
                        print("Url doesn't be correctly formated")
        
            countLine += 1

        if len(urlsToBeReplaced) > 0:
            print('Rewriting file: ' + filePath)

            with open(filePath, 'r', encoding='utf-8') as file:
                data = file.readlines()
                for urlData in urlsToBeReplaced:
                    data[urlData['line']] = urlData['newUrlInFile'] + '\n'
            
            with open(filePath, 'w', encoding='utf-8') as file:
                file.writelines(data)
        else:
            print('No lines will be rewritten')
else:
    print('No files to work')


