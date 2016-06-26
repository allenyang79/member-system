#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse


'''
def run(test_set, debug, coverage_modules, skip_env_run=False, verbose=False):
    if not skip_env_run:
        env_run = os.path.abspath('./scripts/env_run.sh')
        cmd = env_run + ' nosetests'
    else:
        cmd = 'nosetests'
    if debug:
        cmd += ' --nocapture --nologcapture'
    if coverage_modules:
        cmd += ' --with-coverage'
        if coverage_modules == 'all':
            cmd += ' --cover-package=%s' % (','.join(ALL_COVERAGE_MODULES))
        else:
            cmd += ' --cover-package=%s' % (coverage_modules)
    if verbose:
        cmd += ' -v'
    cmd += ' ' + test_set
    print(cmd)
    os.system(cmd)
'''

def run(args):
    if os.path.dirname(os.path.relpath(__file__)) != 'scripts':
        print "please run this script on working dir."
        return
    #env_run = os.path.abspath('./scripts/env_run.sh')
    root_dir = './' #os.path.join(os.path.dirname(__file__),'..')
    #venv = './venv/bin/activate' #os.path.join(os.path.dirname(__file__),'../venv/bin/activate')
    # --with-coverage --cover-inclusive --cover-package=app
    if args.s:
        s = '--nocapture --nologcapture'
    else:
        s = ''
    if args.v:
        v = '--verbose'
    else:
        v = ''
    if args.c:
        c = '--with-coverage --cover-inclusive'
        if args.cp:
            c = '{} --cover-package={}'.format(args.cp)

        else:
            c = '{} --cover-package=app'.format(c)
    else:
        c = '--with-coverage --cover-inclusive'
        if args.cp:
            c = '{} --cover-package={}'.format(args.cp)
        else:
            c = '{} --cover-package=app'.format(c)

    if args.target:
        target = args.target
    else:
        target = 'tests'
    cmd = 'PYTHONPATH={root_dir}  nosetests {s} {v} {c} {target}'.format(
        root_dir = root_dir,
        s = s,
        v = v,
        c = c,
        target = target
    )
    print cmd
    os.system(cmd)


def parse_args():
    parser = argparse.ArgumentParser(description='How to run a test?')
    parser.add_argument('-s', default=True, action='store_false', help='Don\'t capture stdout (any stdout output will be printed immediately).')
    parser.add_argument('-v', default=True, action='store_false', help='Be more verbose. [NOSE_VERBOSE]')
    parser.add_argument('-c', type=str, help='Enable plugin Coverage:  Activate a coverage report using Ned Batchelder\'s coverage module.')
    parser.add_argument('-cp', type=str, help='--cover-package=PACKAGE')
    parser.add_argument('-t', '--target', type=str, help='target')


    #Restrict coverage output to selected packages [NOSE_COVER_PACKAGE]')
    #  --with-coverage       Enable plugin Coverage:  Activate a coverage report
    #                    using Ned Batchelder's coverage module.
    #                    [NOSE_WITH_COVERAGE]
    #parser.add_argument('-t', '--test_set', type=str, help='test set', default='tests')
    #parser.add_argument('-d', '--debug', help='debug mode', default=False, action='store_true')

    #parser.add_argument('-e', '--skip_env_run', default=False, action='store_true', help='skip init venv')
    #parser.add_argument('-v', '--verbose', default=False, action='store_true', help='be more verbose')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    run(args)
    #run(args.test_set, args.debug, args.coverage_modules, args.skip_env_run, args.verbose)
