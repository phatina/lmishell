# Copyright (C) 2015 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import logging
import sys


# Logging levels
LOG_DEFAULT, \
LOG_VERBOSE, \
LOG_MORE_VERBOSE, \
LOG_QUIET = range(4)


class Logger(logging.Logger):
    '''
    LMIShell's logger with queueing capability.
    '''
    def __init__(self, name, level=logging.NOTSET):
        # Due to Python2.6 compatibility, we call superclass c-tor in this way.
        logging.Logger.__init__(self, name, level)
        self.queue = []

    def _log(self, level, msg, args, exc_info=None, extra=None):
        if logging._srcfile:
            try:
                fn, lno, func = self.findCaller()
            except ValueError:
                fn, lno, func = '(unknown file)', 0, '(unknown function)'
        else:
            fn, lno, func = '(unknown file)', 0, '(unknown function)'
        if exc_info:
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()

        record = self.makeRecord(
            self.name, level, fn, lno, msg, args, exc_info, func, extra)
        if self.isEnabledFor(level):
            self.handle(record)
        else:
            self.queue.append(record)

    def setLevel(self, level):
        '''
        Sets a logging level of this handler. If there are any log records
        stored in internal queue, they are also handled.

        :param int level: logging level
        '''
        logging.Logger.setLevel(self, level)
        self.processQueue()

    def setVerbose(self):
        '''
        Sets logging to 'Verbose' level.
        '''
        self.setLevel(logging.INFO)

    def setMoreVerbose(self):
        '''
        Sets logging to 'More Verbose' level.
        '''
        self.setLevel(logging.DEBUG)

    def setQuiet(self):
        '''
        Sets logging to 'Quiet' level. In other words, it drops all the logging
        handlers.
        '''
        handlers = logger.handlers
        for handler in handlers:
            logger.removeHandler(handler)
        logger.addHandler(logging.NullHandler())

    def processQueue(self):
        '''
        Logs all enabled log records stored in internal queue.
        '''
        # Handle all enabled log records.
        for r in self.queue:
            if not self.isEnabledFor(r.levelno):
                continue
            self.handle(r)

        # Remove all handled records.
        self.queue = filter(
            lambda r: not self.isEnabledFor(r.levelno),
            self.queue)

    def debug(self, msg, *args, **kwargs):
        '''
        Log a message with severity 'DEBUG'.
        '''
        self._log(logging.DEBUG, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        '''
        Log a message with severity 'CRITICAL'.
        '''
        self._log(logging.CRITICAL, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        '''
        Log a message with severity 'ERROR'.
        '''
        self._log(logging.ERROR, msg, args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        '''
        Log a message with severity 'ERROR' also with exception information.
        '''
        kwargs['exc_info'] = 1
        self.error(msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        '''
        Log a message with severity 'INFO'.
        '''
        self._log(logging.INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        '''
        Log a message with severity 'WARNING'.
        '''
        self._log(logging.WARNING, msg, args, **kwargs)


# Setup logging.
logging.setLoggerClass(Logger)
logging.basicConfig(format='%(levelname)s: %(message)s')

# Create a logger instance.
logger = logging.getLogger('lmishell')
