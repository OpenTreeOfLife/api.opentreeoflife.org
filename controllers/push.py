import api_utils
import traceback
import datetime
import codecs
import json
import os

def check_not_read_only():
    if api_utils.READ_ONLY_MODE:
        raise HTTP(403, json.dumps({"error": 1, "description": "phylesystem-api running in read-only mode"}))
    return True

@request.restful()
def v1():
    """The OpenTree API v1: Merge Controller

    This controller can be used to merge changes from master into
    a WIP. After this succeeds, subsequent GETs and POSTs to the document
    should be able to merge to master.
    """
    response.view = 'generic.json'

    def PUT(resource_id=None, jsoncallback=None, callback=None, _=None, doc_type='nexson', **kwargs):
        """OpenTree API methods relating to updating branches

        'doc_type' should be 'nexson' (default), 'collection', or 'favorites'

        curl -X POST http://localhost:8000/api/push/v1?resource_id=9
        curl -X POST http://localhost:8000/api/push/v1?resource_id=TestUserB/my-favorite-trees&doc_type=collection
        """
        if not check_not_read_only():
            raise HTTP(500, "should raise from check_not_read_only")
        _LOG = api_utils.get_logger(request, 'ot_api.push.v1.PUT')
        fail_file = api_utils.get_failed_push_filepath(request, doc_type=doc_type)
        # _LOG.debug(">> fail_file for type '{t}': {f}".format(t=doc_type, f=fail_file))
        # support JSONP request from another domain
        if jsoncallback or callback:
            response.view = 'generic.jsonp'

        if doc_type.lower() == 'nexson':
            phylesystem = api_utils.get_phylesystem(request)
            try:
                phylesystem.push_study_to_remote('GitHubRemote', resource_id)
            except:
                m = traceback.format_exc()
                _LOG.warn('Push of study {s} failed. Details: {m}'.format(s=resource_id, m=m))
                if os.path.exists(fail_file):
                    _LOG.warn('push failure file "{f}" already exists. This event not logged there'.format(f=fail_file))
                else:
                    timestamp = datetime.datetime.utcnow().isoformat()
                    try:
                        ga = phylesystem.create_git_action(resource_id)
                    except:
                        m = 'Could not create an adaptor for git actions on study ID "{}". ' \
                            'If you are confident that this is a valid study ID, please report this as a bug.'
                        m = m.format(resource_id)
                        raise HTTP(400, json.dumps({'error': 1, 'description': m}))
                    master_sha = ga.get_master_sha()
                    obj = {'date': timestamp,
                           'study': resource_id,
                           'commit': master_sha,
                           'stacktrace': m}
                    api_utils.atomic_write_json_if_not_found(obj, fail_file, request)
                    _LOG.warn('push failure file "{f}" created.'.format(f=fail_file))
                raise HTTP(409, json.dumps({
                    "error": 1,
                    "description": "Could not push! Details: {m}".format(m=m)
                }))

        elif doc_type.lower() == 'collection':
            docstore = api_utils.get_tree_collection_store(request)
            try:
                docstore.push_doc_to_remote('GitHubRemote', resource_id)
            except:
                m = traceback.format_exc()
                _LOG.warn('Push of collection {s} failed. Details: {m}'.format(s=resource_id, m=m))
                if os.path.exists(fail_file):
                    _LOG.warn('push failure file "{f}" already exists. This event not logged there'.format(f=fail_file))
                else:
                    timestamp = datetime.datetime.utcnow().isoformat()
                    try:
                        ga = docstore.create_git_action(resource_id)
                    except:
                        m = 'Could not create an adaptor for git actions on collection ID "{}". ' \
                            'If you are confident that this is a valid collection ID, please report this as a bug.'
                        m = m.format(resource_id)
                        raise HTTP(400, json.dumps({'error': 1, 'description': m}))
                    master_sha = ga.get_master_sha()
                    obj = {'date': timestamp,
                           'collection': resource_id,
                           'commit': master_sha,
                           'stacktrace': m}
                    api_utils.atomic_write_json_if_not_found(obj, fail_file, request)
                    _LOG.warn('push failure file "{f}" created.'.format(f=fail_file))
                raise HTTP(409, json.dumps({
                    "error": 1,
                    "description": "Could not push! Details: {m}".format(m=m)
                }))

        elif doc_type.lower() == 'amendment':
            docstore = api_utils.get_taxonomic_amendment_store(request)
            try:
                docstore.push_doc_to_remote('GitHubRemote', resource_id)
            except:
                m = traceback.format_exc()
                _LOG.warn('Push of amendment {s} failed. Details: {m}'.format(s=resource_id, m=m))
                if os.path.exists(fail_file):
                    _LOG.warn('push failure file "{f}" already exists. This event not logged there'.format(f=fail_file))
                else:
                    timestamp = datetime.datetime.utcnow().isoformat()
                    try:
                        ga = docstore.create_git_action(resource_id)
                    except:
                        m = 'Could not create an adaptor for git actions on amendment ID "{}". ' \
                            'If you are confident that this is a valid amendment ID, please report this as a bug.'
                        m = m.format(resource_id)
                        raise HTTP(400, json.dumps({'error': 1, 'description': m}))
                    master_sha = ga.get_master_sha()
                    obj = {'date': timestamp,
                           'amendment': resource_id,
                           'commit': master_sha,
                           'stacktrace': m}
                    api_utils.atomic_write_json_if_not_found(obj, fail_file, request)
                    _LOG.warn('push failure file "{f}" created.'.format(f=fail_file))
                raise HTTP(409, json.dumps({
                    "error": 1,
                    "description": "Could not push! Details: {m}".format(m=m)
                }))

        elif doc_type.lower() == 'favorites':
            raise NotImplementedError('TODO: add push behavior for favorites!') 

        else:
            raise ValueError("Can't push unknown doc_type '{}'".format(doc_type)) 

        if os.path.exists(fail_file):
            # log any old fail_file, and remove it because the pushes are working
            with codecs.open(fail_file, 'rU', encoding='utf-8') as inpf:
                prev_fail = json.load(inpf)
            os.unlink(fail_file)
            fail_log_file = codecs.open(fail_file + '.log', mode='a', encoding='utf-8')
            json.dump(prev_fail, fail_log_file, indent=2, encoding='utf-8')
            fail_log_file.close()

        return {'error': 0,
                'description': 'Push succeeded'}
    return locals()
