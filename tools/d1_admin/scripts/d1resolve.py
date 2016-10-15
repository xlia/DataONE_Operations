'''
Resolve an identifier.
'''

import logging
import argparse
import d1_admin_tools.d1_config
import pprint
from d1_client import cnclient_2_0


def resolve(client, pid):
  ''' Resolve the provided identifier in the specified environment

  :param client: An instance of CoordinatingNodeClient
  :param pid: Identifier to resolve
  :return: Dictionary mimicking an objectLocationList with addition of error entry
  '''
  response = {'error':None,
              'xml': None,
              }
  try:
    obj_locs = client.resolve(pid)
    response['xml'] = client.last_response_body #dom.toprettyxml(indent="  ")
    response['identifier'] = unicode(obj_locs.identifier.value())
    response['objectLocation'] = []
    for loc in obj_locs.objectLocation:
      oloc = {'url': unicode(loc.url),
              'nodeIdentifier': unicode(loc.nodeIdentifier.value()),
              'baseURL': unicode(loc.baseURL),
              'version': map(unicode, loc.version),
              'preference': unicode(loc.preference) }
      response['objectLocation'].append(oloc)
  except Exception as e:
    logging.info(e)
    response['error'] = unicode(e)
  return response


def doResolve(pid, environments, configuration):
  ''' Resolve the provided identifier in the list of provided environments.

  :param pid: Identifier to resolve
  :param environments:  Names of one or more environments to examine
  :param configuration: instance of D1Configuration providing lists of environments
  :return: List of dictionaries containing results of the resolve operation in each environment
  '''
  if len(environments) > 1:
    logging.warn('Checking all environments...')
  results = []
  client = None
  for env in environments:
    if client is None:
      client = cnclient_2_0.CoordinatingNodeClient_2_0(configuration.envPrimaryBaseURL(env),
                                                       api_major=2,
                                                       capture_response_body=True)
    else:
      client.set_base_url(configuration.envPrimaryBaseURL(env))
    logging.info("Resolving %s in %s", pid, env)
    res = resolve(client, pid)
    results.append({'environment': env,
                    'resolve': resolve(client, pid)})
  return results


def main():
  parser = argparse.ArgumentParser(description='Resolve identifier in a DataONE environment.')
  parser.add_argument('-l', '--log_level',
                      action='count',
                      default=0,
                      help='Set logging level, multiples for more detailed.')
  parser.add_argument('-e', '--environment',
                      default=None,
                      help="Name of environment to examine (default = all")
  parser.add_argument('-c', '--config',
                      default=d1_admin_tools.d1_config.CONFIG_FILE,
                      help='Name of configuration file (default = {0}'.format(d1_admin_tools.d1_config.CONFIG_FILE))
  parser.add_argument('-f', '--format',
                      default='json',
                      help='Output format (text, json, yaml)')
  parser.add_argument('-u', '--urls_only',
                      action='store_true',
                      help='Only present URLs from which object can be retrieved')
  parser.add_argument('pid',
                      help="Identifier to evaluate")
  args = parser.parse_args()
  # Setup logging verbosity
  levels = [logging.WARNING, logging.INFO, logging.DEBUG]
  level = levels[min(len(levels) - 1, args.log_level)]
  logging.basicConfig(level=level,
                      format="%(asctime)s %(levelname)s %(message)s")
  config = d1_admin_tools.d1_config.D1Configuration()
  config.load()
  PP = pprint.PrettyPrinter(indent=2)
  environments = []
  if args.environment is None or args.environment == "all":
    environments = config.environments()
  else:
    environments = [ args.environment, ]
  results = doResolve(args.pid, environments, config)
  format = args.format.lower()
  if format not in ['text', 'json', 'yaml']:
    format = 'text'
  if args.urls_only:
    summary = []
    for result in results:
      if result['resolve']['error'] is None:
        for loc in result['resolve']['objectLocation']:
          summary.append(loc['url'])
    results = summary
    if format == 'text':
      results = "\n".join(summary)
      print results
      return
  if args.format == 'yaml':
    import yaml
    print(yaml.safe_dump(results, encoding=d1_admin_tools.d1_config.ENCODING))
  elif args.format == 'json':
    import json
    for result in results:
      try:
        result['resolve'].pop('xml', None)
      except:
        pass
    print(json.dumps(results, indent=2, encoding=d1_admin_tools.d1_config.ENCODING))
  elif args.format == 'xml':
    import xml.dom.minidom
    for result in results:
      dom = xml.dom.minidom.parseString(result['resolve']['xml'])
      print dom.toprettyxml(indent="  ")
  else:
    PP.pprint(results)


if __name__ == "__main__":
  main()