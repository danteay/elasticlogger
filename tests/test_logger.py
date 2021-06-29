"""Test logger integration."""

import json
import logging
from logging import LogRecord

from expects import expect, equal
from mamba import before, context, description, it
from testfixtures import LogCapture

from elasticlogger import Logger


with description('Instance creation of Logger.') as self:
    with before.all:
        self.logger = Logger(name='test', level=logging.DEBUG)

    with before.each:
        self.logger.set_level(logging.DEBUG)
        self.logger.context.clear()

    with context('Check properties:'):
        with it('validates name'):
            assert self.logger.name == 'test'

        with it('changes logger level'):
            self.logger.set_level(logging.INFO)

            assert logging.INFO == self.logger.level

    with context('Executes log methods'):
        with it('prints debug logs'):
            with LogCapture() as capture:
                self.logger.debug('test message')

            name, level, message = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('DEBUG'))
            expect(message).to(equal('test message'))

        with it('prints info logs'):
            with LogCapture() as capture:
                self.logger.info('test message')

            name, level, message = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('INFO'))
            expect(message).to(equal('test message'))

        with it('prints warning logs'):
            with LogCapture() as capture:
                self.logger.warning('test message')

            name, level, message = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('WARNING'))
            expect(message).to(equal('test message'))

        with it('prints info logs with error message'):
            with LogCapture(attributes=('name', 'levelname', 'message', 'error')) as capture:
                self.logger.err('some').info('test message')

            name, level, message, error = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('INFO'))
            expect(message).to(equal('test message'))
            expect(error).to(equal('some'))

        with it('prints error logs'):
            with LogCapture(attributes=('name', 'levelname', 'message', 'error')) as capture:
                self.logger.error(message='test message', error='some')

            name, level, message, error = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('ERROR'))
            expect(message).to(equal('test message'))
            expect(error).to(equal('some'))

        with it('prints critical logs'):
            with LogCapture(attributes=('name', 'levelname', 'message', 'error')) as capture:
                self.logger.critical(message='test message', error='some')

            name, level, message, error = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('CRITICAL'))
            expect(message).to(equal('test message'))
            expect(error).to(equal('some'))

        with it('prints logs and add extra param'):
            with LogCapture(attributes=('name', 'levelname', 'message', 'extra')) as capture:
                self.logger.field('extra', 'value').info(message='test message')

            name, level, message, extra = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('INFO'))
            expect(message).to(equal('test message'))
            expect(extra).to(equal('value'))

        with it('prints logs and add extra params as dict'):
            with LogCapture(attributes=('name', 'levelname', 'message', 'extra', 'extra2')) as capture:
                self.logger.fields({'extra': 'value', 'extra2': 'value2'}).info(message='test message')

            expected = ('test', 'INFO', 'test message', 'value', 'value2')
            expect(capture.actual()[0]).to(equal(expected))

    with context('Test global context:'):
        with it('prints logs with global context variables'):
            self.logger.context.field('ctx', 'valctx')

            with LogCapture(attributes=('name', 'levelname', 'message', 'ctx')) as capture:
                self.logger.info(message='test message')

            expected = ('test', 'INFO', 'test message', 'valctx')
            expect(capture.actual()[0]).to(equal(expected))

        with it('prints logs by adding many context variables at once'):
            self.logger.context.fields({'ctx': 'ctx1', 'ctx2': 'ctx2'})

            with LogCapture(attributes=('name', 'levelname', 'message', 'ctx', 'ctx2')) as capture:
                self.logger.info(message='test message')

            expected = ('test', 'INFO', 'test message', 'ctx1', 'ctx2')
            expect(capture.actual()[0]).to(equal(expected))

        with it('clear global context'):
            self.logger.context.fields({'ctx': 'ctx1', 'ctx2': 'ctx2'})

            with LogCapture(attributes=('name', 'levelname', 'message', 'ctx', 'ctx2')) as capture:
                self.logger.context.clear()
                self.logger.info(message='test message')

            expected = ('test', 'INFO', 'test message', None, None)
            expect(capture.actual()[0]).to(equal(expected))

        with it('raises error for non string key'):
            try:
                self.logger.context.field(12, 12)
            except Exception as error:
                expect(error.args[0]).to(equal("Invalid context value key, expected 'str' got 'int'"))
