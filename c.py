import csv
from datetime import datetime
import glob
import sys

sys.setdefaultencoding('UTF-8')     # still heb strings log lft->rgt reversed(?)

proc_name = 'ArbSumLetters'
now = datetime.now()
cur_yymmdd = now.strftime('%y%m%d')

FilePath_ArbSum = 'arb/'
FilePath_Ezr = 'ezr/'
FullFilePath_layoutHtml = FilePath_Ezr + 'layout.html'

FullFilePath_ArbSumWildCard = FilePath_ArbSum + 'ccc-d' + cur_yymmdd + '?'
OutFileNameTemplate = FilePath_ArbSum + 'ArbSumLetter-d' + cur_yymmdd
i = 1

log_file_name = proc_name + '.log'
with open(log_file_name, 'a+') as flog:
    flog.write('\n\n_______________________________________________________________________________\n')
    flog.write('%s %s %s' % ('Program started at: ', now.strftime("%Y-%m-%d %H:%M:%S"), '\n'))

try:
    with open(FullFilePath_layoutHtml, mode='r') as LayoutHtmlFile:
        LayoutHtmlRead = LayoutHtmlFile.read()
except Exception as e:
    flog.write('%s %s', 'ERROR open_HTML_layout..: ', e)
    sys.exit()


try:
    for file in glob.glob(FullFilePath_ArbSumWildCard + '*'):
        with open(file, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for d_csv_row in csv_reader:
                d_csv_row_fix = {'@' + k: v for k, v in d_csv_row.items()}

                LayoutHtmlReplace = LayoutHtmlRead
                for k, v in d_csv_row_fix.iteritems():
                    LayoutHtmlReplace = LayoutHtmlReplace.replace(k, v)

                OutFileName = OutFileNameTemplate + '__' + str(i) + '.html'
                with open(OutFileName, 'w') as f:
                    f.write(LayoutHtmlReplace)
                i += 1
except Exception as e:
    with open(log_file_name, 'a+') as flog:
        flog.write('%s %s' % ('ERROR main process..: ', e))
    sys.exit()


with open(log_file_name, 'a+') as flog:
    flog.write('%s %s' % ('END=OK main process..: ', now.strftime("%Y-%m-%d %H:%M:%S")))
