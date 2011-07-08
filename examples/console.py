import sys
import csv
import os.path
import logging
import optparse

logger = logging.getLogger('wikidump')

sys.path.append('../src/')
from wikidump.utils import load_dumps, find_dumps
from wikidump.model import Dump

def main():
  logging.basicConfig(level=logging.DEBUG)
  if len(sys.argv) < 2:
    logger.error("Must specify a command! Try 'help'")
    sys.exit(-1)

  command = sys.argv[1]

  if command == 'help':
    # Display a help message
    logger.info("The following commands are supported:")
    logger.info("    index             : builds indexes - warning: can take many hours")
    logger.info("    stats             : print statistics in a tab-delimited CSV format")
    logger.info("    categories [lang] : list categories for 'lang', and the number of documents in each")

  elif command == 'list':
    # List available dumps
    dumps = find_dumps()
    # TODO: Print if an index exists
    for key in sorted(dumps):
      print "  %-20s%s" % (key, dumps[key])
    
  elif command == 'index':
    # Build indices
    load_dumps(build_index=True)

  elif command == 'stats':
    root_logger = logging.getLogger()
    root_logger.level = logging.ERROR
    # Display statistics
    paths = find_dumps()
    sizes = dict((k, len(Dump(p))) for k, p in paths.iteritems())

    fields = ['lang', 'filename', 'pages', 'categories']
    outfile = csv.DictWriter(sys.stdout, fields)
    for p in sorted(sizes, key=sizes.get, reverse=True):
      dump = Dump(paths[p])
      d = dict\
            ( lang=p
            , filename=os.path.basename(paths[p])
            , pages=sizes[p]
            , categories=len(dump.categories)
            )
      outfile.writerow(d)

  elif command == 'categories':
    # Dump category distribution
    parser = optparse.OptionParser()
    parser.add_option("-l", "--language", dest="lang", help="Relevant language prefix")
    options, args = parser.parse_args(sys.argv[2:])

    dump = load_dumps([options.lang], build_index=True)[options.lang]
    cats = dump.categories

    for c in sorted(cats, key=lambda x:len(cats[x]), reverse=True):
      print "%-4d %s" % (len(cats[c]), c)

  else:
    logging.error("Unknown command: %s", command)
    logging.info("Try the 'help' command.")

main()
