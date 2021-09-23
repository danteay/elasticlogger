"""Test logger integration."""

import logging

from expects import equal, expect
from mamba import before, context, description, it
from testfixtures import LogCapture

from elasticlogger import Logger
from elasticlogger.hooks import HookContext

with description('Instance creation of Logger.') as self:
    with before.all:
        self.logger = Logger(name='test', level=logging.DEBUG)

    with before.each:
        self.logger.set_level(logging.DEBUG)
        self.logger.context.clear()
        self.logger.clear_hooks()

    with context('Check properties:'):
        with it('validates name'):
            assert self.logger.name == 'test'

        with it('changes logger level'):
            self.logger.set_level(logging.INFO)

            assert logging.INFO == self.logger.level

        with it('checks base logging.Logger instance'):
            assert self.logger.logger.name == 'test'

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
                self.logger.err('some').error('test message')

            name, level, message, error = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('ERROR'))
            expect(message).to(equal('test message'))
            expect(error).to(equal('some'))

        with it('prints critical logs'):
            with LogCapture(attributes=('name', 'levelname', 'message', 'error')) as capture:
                self.logger.err('some').critical('test message')

            name, level, message, error = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('CRITICAL'))
            expect(message).to(equal('test message'))
            expect(error).to(equal('some'))

        with it('prints logs and add extra param'):
            with LogCapture(attributes=('name', 'levelname', 'message', 'extra')) as capture:
                self.logger.field('extra', 'value').info('test message')

            name, level, message, extra = capture.actual()[0]
            expect(name).to(equal('test'))
            expect(level).to(equal('INFO'))
            expect(message).to(equal('test message'))
            expect(extra).to(equal('value'))

        with it('prints logs and add extra params as dict'):
            with LogCapture(attributes=('name', 'levelname', 'message', 'extra', 'extra2')) as capture:
                self.logger.fields({'extra': 'value', 'extra2': 'value2'}).info('test message')

            expected = ('test', 'INFO', 'test message', 'value', 'value2')
            expect(capture.actual()[0]).to(equal(expected))

    with context('Test global context:'):
        with it('prints logs with global context variables'):
            self.logger.context.field('ctx', 'valctx')

            with LogCapture(attributes=('name', 'levelname', 'message', 'ctx')) as capture:
                self.logger.info('test message')

            expected = ('test', 'INFO', 'test message', 'valctx')
            expect(capture.actual()[0]).to(equal(expected))

        with it('prints logs by adding many context variables at once'):
            self.logger.context.fields({'ctx': 'ctx1', 'ctx2': 'ctx2'})

            with LogCapture(attributes=('name', 'levelname', 'message', 'ctx', 'ctx2')) as capture:
                self.logger.info('test message')

            expected = ('test', 'INFO', 'test message', 'ctx1', 'ctx2')
            expect(capture.actual()[0]).to(equal(expected))

        with it('clear global context'):
            self.logger.context.fields({'ctx': 'ctx1', 'ctx2': 'ctx2'})

            with LogCapture(attributes=('name', 'levelname', 'message', 'ctx', 'ctx2')) as capture:
                self.logger.context.clear()
                self.logger.info('test message')

            expected = ('test', 'INFO', 'test message', None, None)
            expect(capture.actual()[0]).to(equal(expected))

        with it('raises error for non string key'):
            try:
                self.logger.context.field(12, 12)
            except Exception as error:
                expect(error.args[0]).to(equal("Invalid context value key, expected 'str' got 'int'"))

    with context('Test Logger Hooks:'):
        with it('adds new hook and modify extra value'):

            def hook(hoot_context: HookContext):
                """test hook"""
                hoot_context.extra_data['extra'] = 2

            self.logger.add_hook(hook)

            with LogCapture(attributes=('extra', )) as capture:
                self.logger.field('extra', 1).info('message')
                extra = capture.actual()[0]

            expect(extra).to(equal(2))

        with it('Hook execution fail'):

            def hook_error(_: HookContext):
                """test hook error"""
                raise Exception('hook error')

            self.logger.add_hook(hook_error)

            with LogCapture(attributes=('error', )) as capture:
                self.logger.field('extra', 1).info('message')
                error = capture.actual()[0]

            expect(error).to(equal('hook error'))
