'''
URL encode or decode stdin to stdout
'''

import sys
import logging
import argparse
import urllib


def doEncode(instr, full_url=False):
  print "encode"
  res = {}
  if not full_url:
    res = urllib.quote(instr)
  else:
    raise NotImplementedError("url parsing for encode not implemented")
    pass
  return res


def doDecode(instr, full_url=False):
  print "decode"
  res = {}
  if not full_url:
    res = urllib.unquote(instr)
  else:
    raise NotImplementedError("url parsing for decode not implemented")
    pass
  return res


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='URL encode or decode provided stdin text')
  parser.add_argument('-l', '--log_level',
                      action='count',
                      default=0,
                      help='Set logging level, multiples for more detailed.')
  parser.add_argument('-u', '--url',
                      default=False,
                      action='store_true',
                      help='Parse the input as a URL and encode / decode the parts that need it.')
  parser.add_argument('-f', '--format',
                      default='text',
                      help='Output format (text, json)')
  parser.add_argument('-d', '--decode',
                      default=False,
                      action='store_true',
                      help="URL decode, otherwise encode")
  args = parser.parse_args()
  # Setup logging verbosity
  levels = [logging.WARNING, logging.INFO, logging.DEBUG]
  level = levels[min(len(levels) - 1, args.log_level)]
  logging.basicConfig(level=level,
                      format="%(asctime)s %(levelname)s %(message)s")
  instr = sys.stdin.read()
  res = {}
  if args.decode:
    res = doDecode(instr, args.url)
  else:
    res = doEncode(instr, args.url)
  if args.format == 'json':
    import json
    print json.dumps(res, encoding='utf-8')
    sys.exit(0)
  print res.decode('utf-8')
  sys.exit(0)