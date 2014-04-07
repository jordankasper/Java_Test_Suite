import logging
import newrelic.agenttest.testenv
import os
import tarfile
import tempfile
import urllib.request
import subprocess

def run(test_env):
    for app_class in sorted(test_env.config.keys()):
        for app in [app for app in test_env.config[app_class]
                    if app.get('archive')]:
            logging.info('checking {}'.format(app['path']))
            if not (os.path.exists(app['path']) and app_is_up_to_date(app)):
                logging.info("downloading {} for {}".format(_remote_app_path(app), app['path']))
                archive = download_app(app)
                if archive == None:
                    logging.info("ignoring {} because {} does not exist on server".format(app['path'], _remote_app_path(app)))
                else :
                    expand_app_archive(app, archive)

def _local_md5sum_path(app):
    return os.path.join(os.path.dirname(app['path']), app['archive'] + '.md5')

def _remote_app_path(app):
    return "http://{}/{}".format(app['archive_repo'], app['archive'])

def _remote_app_md5sum_path(app):
    return _remote_app_path(app) + '.md5'

def app_is_up_to_date(app):
    remote_checksum = None;
    try:
        remote_checksum = urllib.request.urlopen(
            _remote_app_md5sum_path(app)).read().decode().strip()
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise e
        return False

    try:
        local_checksum = ''
        with open(_local_md5sum_path(app), 'r') as f:
            local_checksum = f.read().strip()

        if local_checksum == remote_checksum:
            logging.debug('{} checksums match'.format(app['path']))
            return True
        else:
            logging.info(
                '{} checksums do not match: {} vs {}'.format(
                    app['path'],
                    local_checksum,
                    remote_checksum))
            return False
    except Exception as e:
        logging.debug(e)
        return False

def download_app(app):
    try:
        return urllib.request.urlopen(_remote_app_path(app))
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise e
        return None

def expand_app_archive(app, archive):
    tf = tempfile.NamedTemporaryFile()
    logging.info("saving {} to {}".format(_remote_app_path(app), tf.name))
    tf.write(archive.read())
    archive = tarfile.open(fileobj=tf,debug=0)

    pardir = os.path.dirname(app['path'])

    if not os.path.exists(pardir):
        os.mkdir(pardir)

    logging.info("extracting {} to {}".format(tf.name, pardir))

    # TODO: Determine why this silently fails for all archives
    #archive.extractall(path=pardir)

    subprocess.call(["tar", "xzf", tf.name, "-C", pardir]);

    tf.close()

    logging.info("getting md5 checksum from {}".format(_remote_app_md5sum_path(app)))

    checksum = urllib.request.urlopen(
        _remote_app_md5sum_path(app)).read()

    logging.info("writing md5 file {}".format(_local_md5sum_path(app)))

    with open(_local_md5sum_path(app), 'w+') as f:
        f.write(checksum.decode())

if __name__ == '__main__':
    logging.getLogger().setLevel(os.environ.get('TEST_LOG_LEVEL', 'INFO'))
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s')
    test_conf = os.environ.get('TEST_CONFIG', '/Users/roger/Documents/workspace_git/agent_integration_tests/conf/java_config.yml')
    test_local_conf = os.environ.get('TEST_LOCAL_CONFIG', '/Users/roger/Documents/workspace_git/agent_integration_tests/conf/java_local_config.yml')

    run(
        newrelic.agenttest.testenv.TestEnv(
            test_conf,
            test_local_conf,
            None))
#    run(
#        newrelic.agenttest.testenv.TestEnv(
#            os.environ['TEST_CONFIG'],
#            os.environ['TEST_LOCAL_CONFIG']))
