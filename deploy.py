#!/usr/bin/env python3
# vim: set et nonumber:
#
# Originally from
#  - berkeley-dsep-infra/datahub
#  - berkeley-dsep-infra/data8xhub
#

import argparse
import logging
import os
import subprocess
import sys
import yaml

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def tag_fragment_file(tag):
    tag_fragment = yaml.dump({'singleuser': {'image': {'tag': tag}}})
    filename = '/tmp/tag-{}.yaml'.format(tag)
    with open(filename, 'w') as f:
        f.write(tag_fragment)
    return filename

def git(*args, **kwargs):
    return subprocess.check_output(['git'] + list(args))

def helm(*args, **kwargs):
    arg0 = 'helm'
    logging.info("Executing " + arg0 + " " + ' '.join(args))
    return subprocess.check_call([arg0] + list(args), **kwargs)

def kubectl(*args, **kwargs):
    arg0 = 'kubectl'
    logging.info("Executing " + arg0 + " " + ' '.join(args))
    return subprocess.check_call([arg0] + list(args), **kwargs)

def last_git_modified(path, n=1):
    return git(
        'log',
        '-n', str(n),
        '--pretty=format:%h',
        path
    ).decode('utf-8').split('\n')[-1]

def build_user_image(image_name, commit_range=None, push=False):
    if commit_range:
        image_touched = git('diff', '--name-only', commit_range,
            'user-image').decode('utf-8').strip() != ''
        if not image_touched:
            print("user-image not touched, not building")
            return

    # Pull last available version of image to maximize cache use
    try_count = 0
    while try_count < 50:
        last_image_tag = last_git_modified('user-image', try_count + 1)
        last_image_spec = image_name + ':' + last_image_tag
        try:
            subprocess.check_call([
                'docker', 'pull', last_image_spec
            ])
            break
        except subprocess.CalledProcessError:
            try_count += 1
            pass

    tag = last_git_modified('user-image')
    image_spec = image_name + ':' + tag

    subprocess.check_call([
        'docker', 'build', '--cache-from', last_image_spec, '-t', image_spec, 'user-image'
    ])
    if push:
        print('pushing {}'.format(image_spec))
        subprocess.check_call([
            'docker', 'push', image_spec
        ])
    print('build completed for image', image_spec)

def deploy(release):
    # Set up helm!
    helm('version')
    # workaround https://github.com/kubernetes/helm/issues/3392
    #helm('init', '--service-account', 'tiller', '--force-upgrade')
    helm('init', '--service-account', 'tiller', '--upgrade')
    kubectl('rollout', 'status', '--watch', 'deployment/tiller-deploy',
        '--namespace=kube-system')
    helm('repo', 'add', 'jupyterhub',
        'https://jupyterhub.github.io/helm-chart/')
    helm('repo', 'update')

    singleuser_tag = last_git_modified('user-image')

    # We can't use --set because helm converts numeric values to float64
    # https://github.com/kubernetes/helm/issues/1707
    tagfilename = tag_fragment_file(singleuser_tag)

    with open('hub/config.yaml') as f:
        config = yaml.safe_load(f)

    helm('upgrade', '--install', '--wait',
        release, 'jupyterhub/jupyterhub',
        '--namespace', release,
        '--version', config['version'],
        '-f', 'hub/config.yaml',
        '-f', os.path.join('hub', 'secrets', release + '.yaml'),
        '-f', tagfilename,
        '--timeout', '3600'
        #'--set', 'singleuser.image.tag={}'.format(singleuser_tag)
    )


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--user-image-spec',
        default='berkeleydsep/singleuser-data100'
    )
    subparsers = argparser.add_subparsers(dest='action')

    build_parser = subparsers.add_parser('build',
        description='Build and push images')
    build_parser.add_argument('--commit-range',
        help='Range of commits to consider when building images')
    build_parser.add_argument('--push', action='store_true')

    deploy_parser = subparsers.add_parser('deploy',
        description='Deploy with helm')
    deploy_parser.add_argument('release', default='prod')


    args = argparser.parse_args()

    if args.action == 'build':
        build_user_image(args.user_image_spec, args.commit_range, args.push)
    else:
        deploy(args.release)

main()
