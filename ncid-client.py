#!/usr/bin/python -u
# -*- coding: utf-8 -*-

'''simple tcp client'''

# apt-get install python-configobj
from configobj import ConfigObj

# apt-get install python-twisted
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

from datetime import datetime

# it may block, but twisted logging MAY block too
import logging
from logging.handlers import TimedRotatingFileHandler

CONFIG = ConfigObj('./ncid-client.cfg')
LOGFILE = CONFIG.get('logfile', '/var/log/ncid/incoming.log')
SERVER_IP = CONFIG.get('server_ip', '192.168.2.1')
SERVER_PORT = int(CONFIG.get('server_port', 3333))

logger = logging.getLogger('NCID')
logger.setLevel(logging.DEBUG)
logger.name = 'NCID'
handler = TimedRotatingFileHandler(LOGFILE, when='midnight')
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s,%(name)s] %(message)s'))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class NcidClient(LineReceiver):
	def lineReceived(self, line):
		if line.startswith('CIDLOG:'):
			data = line.split('*')
			date, time, phonenr = data[2], data[4], data[8]
			tstamp_log = datetime.strptime('%s %s' % (date, time), '%d%m%Y %H%M').strftime('%Y-%m-%d %H:%M')
			logger.info('%s: %s' % (str(tstamp_log), phonenr))
		else:
			logger.debug(line)

class NcidClientFactory(ClientFactory):
	protocol = NcidClient

	def clientConnectionFailed(self, connector, reason):
		logger.debug('connection failed: %s' % reason.getErrorMessage())
		reactor.stop()

	def clientConnectionFailed(self, connector, reason):
		logger.debug('connection lost: %s' % reason.getErrorMessage())
		reactor.stop()

def main():
	logger.info('initializing...')
	factory = NcidClientFactory()
	reactor.connectTCP(SERVER_IP, SERVER_PORT, factory)
	logger.info('started!')
	reactor.run()
	logger.info('stopped!')

if __name__ == '__main__':
	main()

