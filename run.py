#!/usr/bin/env python3

import sys
import argparse
import yaml
import ntpath
from atlassian import Bitbucket


def create_parser():
    parser = argparse.ArgumentParser(
        prog=None,
        usage=None,
        description=None,
        epilog=None,
        parents=[],
        prefix_chars='-',
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler='error',
        add_help=True,
        allow_abbrev=True
    )

    parser.add_argument(
        '-b', '--bitbucket',
        type=str,
        default='http://nuc.local:8083',
        help='Bitbucket URL'
    )

    parser.add_argument(
        '-u', '--user',
        type=str,
        default='admin',
        help='Butbucket admin user'
    )

    parser.add_argument(
        '-p', '--passwd',
        type=str,
        default='admin123',
        help='Bitbucket admin password'
    )

    parser.add_argument(
        '-f', '--file',
        type=str,
        default='project1_meta.yaml',
        help='project model yaml'
    )

    return parser


def yaml_read(path):
    """
    Простая функция чтения yaml файла
    :param path: path to yaml file
    :return: project map dictionary
    """
    with open(path, 'r') as project_model:
        try:
            model = yaml.safe_load(project_model)
        except yaml.YAMLError as exc:
            print(exc)

        return model


def main():
    parser = create_parser()
    parser_namespace = parser.parse_args(sys.argv[1:])
    bitbucket_url = parser_namespace.bitbucket
    bitbucket_user = parser_namespace.user
    bitbucket_pass = parser_namespace.passwd
    project_model_path = parser_namespace.file

    project_key = ntpath.basename(project_model_path).replace('_meta.yaml', '')

    project_map = yaml_read(project_model_path)

    if project_map['READY']:
        project_map = yaml_read(project_model_path)
        if project_map['RESOURCES'] and project_map['RESOURCES']['bitbucket']:

            project_model_bitbucket = project_map['RESOURCES']['bitbucket']
            project_name = project_model_bitbucket['name']
            project_description = project_model_bitbucket['description']

            bitbucket = Bitbucket(
                url=bitbucket_url,
                username=bitbucket_user,
                password=bitbucket_pass)

            bb_projects = bitbucket.project_list(limit=9999)

            if next((i for i in bb_projects if i['key'] == project_key.upper()), None):
                print(f'INFO: BitBucket project {project_key} already exists')
            else:
                bitbucket.create_project(project_key, project_name, description=project_description)
                print(f'INFO: BitBucket project {project_key} created')

            for group in project_model_bitbucket['privileges']:

                if 'delete' in project_model_bitbucket['privileges'][group]:
                    bitbucket.project_grant_group_permissions(project_key, f'rb-{project_key}-{group}', 'PROJECT_ADMIN')
                    print(f'INFO: rb-{project_key}-{group} PROJECT_ADMIN granted')

                elif 'write' in project_model_bitbucket['privileges'][group]:
                    bitbucket.project_grant_group_permissions(project_key, f'rb-{project_key}-{group}', 'PROJECT_WRITE')
                    print(f'INFO: rb-{project_key}-{group} PROJECT_WRITE granted')

                elif 'read' in project_model_bitbucket['privileges'][group]:
                    bitbucket.project_grant_group_permissions(project_key, f'rb-{project_key}-{group}', 'PROJECT_READ')
                    print(f'INFO: rb-{project_key}-{group} PROJECT_READ granted')

    else:
        print('MAP NOT READY')


if __name__ == '__main__':
    main()

