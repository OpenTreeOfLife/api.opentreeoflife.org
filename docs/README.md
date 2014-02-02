# Open Tree API Documentation

This file documents the design of the Open Tree API, including requirements defined by
the [Open Tree of Life](http://opentreeoflife.org) community and software team
and the reasons for various "details of implementation".

## OToL API Version 1 Methods

All API calls are specific to the API version, which is a part
of the URL. This allows for new versions of the API to come out
which are not backward-compatible, while allowing old clients
to continue working with older API versions.


NOTE: The dev.opentreeoflife.org hostname is a development URL and subject to change.

### Getting a Github Oauth token

Any API methods that allow writing (or changing the state of
the repo) require an authentication token. The examples below
assume a Github Oauth token is stored in the environment
variable

    $GITHUB_OAUTH_TOKEN

To get a Github OAuth token, you can use ```curl``` as well:

    curl -u USERNAME -X POST https://api.github.com/authorizations \
        --data '{"scopes":["public_repo"],"note":"description"}'

where USERNAME is your Github login/username. The above will
return JSON containing a "token" key, which is your new OAuth
token.

To put it into an environment variable:

    export GITHUB_OAUTH_TOKEN=codecafe

In the Open Tree curation webapp, we obtain this when a user logs into the
site via Github. Github returns a persistent token that streamlines
authentication in the future. (Basically, the user shouldn't need to login
again unless they revoke access to the curation app on Github.)

Here are other tips on managing auth tokens programmatically:

http://developer.github.com/v3/oauth/#get-or-create-an-authorization-for-a-specific-app

### Fetch a study

To get the entire NexSON of study N :

    curl http://dev.opentreeoflife.org/api/v1/study/N.json

If the study does not exist, this API call will return a 404 error code.

### Updating a study

If you want to update study 10 with a file called
10-modified.json, the following command will accomplish that:

    curl -X PUT http://localhost:8080/api/v1/study/10.json?auth_token=$GITHUB_OAUTH_TOKEN \
    --data-urlencode nexson@10-modified.json

For large studies, it's faster to skip the URL-encoding and pass the NexSON data as binary:

    curl -X PUT 'http://localhost:8080/api/v1/study/10?auth_token=26b5a59d2cbc921bdfe04ec0e9f6cc05c879a761' \
    --data-binary @10-modified.json --compressed


Either form of this command will create a commit with the updated JSON on a branch of the form

    USERNAME_study_ID

where USERNAME is the authenticated users Github login and ID
is the study ID number.

On success, it will return a JSON response similar to this:

    {
     "branch_name": "leto_study_13",
     "sha": "e13343535837229ced29d44bdafad2465e1d13d8",
     "description": "Updated study #13",
     "error": 0
     }

```branch_name``` is the WIP branch that was created, ```sha```
is the latest commit on that branch, ```description``` is a
textual description of what happened and ```error``` is set to
0.

On failure, ```error``` will be set to 1 and ```description``` will provide details on why the request failed.

Any PUT request attempting to update a study with invalid JSON
will be denied and an HTTP error code 400 will be returned.

[Here](https://github.com/OpenTreeOfLife/phylesystem/compare/leto_study_9?expand=1)
is an example commit created by the OpenTree API.

### Creating a new study

To create a new study from a file in the current directory called ```study.json```:

    curl -X POST "http://dev.opentreeoflife.org/api/v1/study/?auth_token=$GITHUB_OAUTH_TOKEN" --data-urlencode nexson@study.json

### Syncing a WIP branch with Github

This API method will sync the local Git repo on the server with it's remote (usually Github).

    curl -X POST http://dev.opentreeoflife.org/api/pull/v1/master?auth_token=$GITHUB_OAUTH_TOKEN

On success, it will return JSON similar to this:

    {
        "branch_name": "master",
        "sha": "9ed1ab2d118c911467c28cbdaa7cb3091243154d",
        "description": "Updated branch master",
        "error": 0
    }

If there is an error in syncing the local git repository with the remote, an HTTP 409 (conflict) error code will be returned with a JSON response of the form:

    {
        "error": 1,
        "description": "Could not pull! Details: ..."
    }

where the description will usually contain the full error reported by Git.

### Merge a study in a WIP branch

To merge branch X into branch Y:

    curl -X POST http://dev.opentreeoflife.org/api/merge/v1/X/Y?auth_token=$GITHUB_OAUTH_TOKEN

The default value for Y is the "master" branch, which is what most merges will want to do.

The following two commands are equivalent.

    curl -X POST http://dev.opentreeoflife.org/api/merge/v1/leto_study_1003?auth_token=$GITHUB_OAUTH_TOKEN

    curl -X POST http://dev.opentreeoflife.org/api/merge/v1/leto_study_1003/master?auth_token=$GITHUB_OAUTH_TOKEN

If the request is successful, a JSON response similar to this will be returned:

        {
            "error": 0,
            "branch_name": "master",
            "description": "Merged branch leto_study_12",
            "sha":  "dcab222749c9185797645378d0bda08d598f81e7"
        }

        If there is an error, an HTTP 400 error will be returned with a JSON response similar
        to this:

        {
            "error": 1,
            "description": "Could not push foo branch"
        }

### Using different author information

By default, the API uses the name and email associated with the Github Oauth token to assign provenance to API calls. To over-ride that you can provide ```author_name``` and ```author_email``` arguments:

    curl -X PUT 'http://dev.opentreeoflife.org/api/v1/study/13.json?auth_token=$GITHUB_OAUTH_TOKEN&author_name=joe&author_email=joe@joe.com' --data-urlencode nexson@1003.json

## Not Yet Implemented Methods

The following methods have not been implemented yet.

### Listing available studies

    # By convention, this might be the default view for a "collection" URL:
    curl https://dev.opentreeoflife.org/api/v1/studies

### Searching, filtering, sorting, paginating studies

    # Add searching, sorting, pagination, filters on the query string
    curl https://dev.opentreeoflife.org/api/v1/studies?q=mammal&sort=status,-date&page=3&filter=state-draft

### Listing your own studies (as a curator), sorted by status

This is the default __dashboard__ view for a logged-in curator. Of course it's
just a special case of the filtered list above.

    # the curator's "dashboard" is just a preset filter
    curl https://dev.opentreeoflife.org/api/v1/studies?q=jimallman&sort=-status,-date&page=1&filter=state-draft

This and other "canned" views might have friendlier URLs:

    curl https://dev.opentreeoflife.org/api/v1/studies/dashboard

    curl https://dev.opentreeoflife.org/api/v1/studies/draft

    curl https://dev.opentreeoflife.org/api/v1/studies/published

    curl https://dev.opentreeoflife.org/api/v1/studies/latest

### Fetching a work-in-progress (WIP) study

    curl http://dev.opentreeoflife.org/api/v1/study/N.json?branch=user_study_N

This will return the latest state of N.json on the ```user_study_N``` branch or a 404 if that branch does not exist.

### Incorporating "namespaced" study identifiers from different sources

We need to avoid collisions between studies created in phylografter, the
Open Tree web curation tool, and other tools. Rather than keeping a global
counter or using GUIDs, we're planning to use a prefix for tool or system
that contributes Nexson studies to the repository.

The prefixes currently planned include:
    'ot' for the [Open Tree curation tool](https://dev.opentreeoflife.org/curator/study) 
    'pg' for [phylografter](http://reelab.net/phylografter/)


These "namespaces" will appear in different forms, depending on context: 

- as CURIEs in NexSON or NeXML

    ```
    'nexml': { "@id": "ot:123", ... }

    <nexml id="pg:987" ... >
    ```

- as folders in the datastore (filesystem or git repo)

    ```
    ot/123.json
    pg/987.json
    ```

- as subpaths in RESTful URLs

    ```
    http://dev.opentreeoflife.org/api/v1/study/ot/123/tree
    http://dev.opentreeoflife.org/api/v1/study/pg/987/tree
    ```
    
- as elements of WIP branch names (in a branching repo)

    ```
    jimallman_study_ot_123
    leto_study_pg_987
    ```


### Creating, fetching, updating subresources (not yet implemented)

We should be able to extend the RESTful style used for studies to manage
"subresources" (trees, nodes, OTUs?) within a study.  Where possible, this
would provide a uniform set of CRUD (create, retrieve, update,
delete) operations using URLs like:

    http://dev.opentreeoflife.org/api/v1/study/ot/123/tree
    http://dev.opentreeoflife.org/api/v1/study/ot/123/tree/5
    http://dev.opentreeoflife.org/api/v1/study/ot/123/tree/5/node/789
    http://dev.opentreeoflife.org/api/v1/study/ot/123/otu/456

Apart from normal elements in NexSON, we might also consider using this
convention for supporting files and annotations:

    http://dev.opentreeoflife.org/api/v1/study/ot/123/file/3
    http://dev.opentreeoflife.org/api/v1/study/ot/123/file/alignment_data.xsl
    http://dev.opentreeoflife.org/api/v1/study/ot/123/annotation/456

Ideally, it would be good to also allow fetching (and more?) of sets of
related objects:

- contiguous ranges of objects
- non-contiguous "sets" of objects
- arbitrary sets of mixed types?

Here are some possible examples:

    http://dev.opentreeoflife.org/api/v1/study/ot/123/tree/1...4
    http://dev.opentreeoflife.org/api/v1/study/ot/123/tree/1,5,8

The last case (arbitrary setes of mixed types) might include the cluster of
elements needed for a complex annotation. This would probably be handled
best in a more general diff/patch solution, probably in RPC style rather
than REST. Or as a choreographed series of RESTful operations on the
individual elements, as shown above.


## Authors

Jonathan "Duke" Leto

Jim Allman